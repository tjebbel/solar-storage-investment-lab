"""Herijking van het basismodel op echte data, en de batterij op dagmarkt en onbalans.
Run: PYTHONPATH=src python3 -m eti.herijk
Schrijft powerbi/data/fact_batterij_stapeling.csv, fact_batterij_irr.csv, fact_herijking.csv, fact_onbalans_nl.csv
en reports/herijking.json.

Uitgangspunten (herzien 17 november 2026):
- Onbalansprijzen (ENTSO-E A85) hebben curveType A03: een weggelaten positie heeft dezelfde prijs als de vorige.
  Die posities worden opgevuld, zodat elk kwartier op het juiste tijdstip staat.
- Laden (afnemen zonder inkoop) kost de prijs voor een tekort (A05); ontladen levert de prijs voor een overschot (A04) op.
- Een onbalansprijs ken je niet vooraf. Een plan op onbalans telt dus ook de verliesdagen mee.
  Op de dagmarkt kan een verlieslatende cyclus worden voorkomen (loop block order); daar blijft 'overslaan' staan.
- De marktkeuze per dag gebeurt vooraf (7-daags gemiddelde tot en met eergisteren). De keuze achteraf is alleen een bovengrens."""
import glob, io, json, zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd
from . import finance

OUT, RAW = "powerbi/data", "data/raw"
MW, H, EFF, OPEX_SH, DEG, LIFE = 10, 2, 0.88, 0.02, 0.02, 15
CAPEX = (300_000, 250_000, 200_000)
STATS = {"punten": 0, "kwartieren": 0}


def _tag(e):
    return e.tag.split("}")[-1]


def vul_posities(punten, n, curve):
    """{positie: prijs} -> lijst van n prijzen; bij curveType A03 herhaalt een ontbrekende positie de vorige prijs."""
    uit, vorige = [], None
    for k in range(1, n + 1):
        if k in punten:
            vorige = punten[k]
        elif curve != "A03":
            vorige = None
        uit.append(vorige)
    return uit


def onbalans_kwartier():
    """-> DataFrame, index tijdstip (UTC), kolommen tekort (A05) en overschot (A04) in EUR/MWh."""
    q = {"A04": {}, "A05": {}}
    for p in sorted(glob.glob(f"{RAW}/imb_NL_*.xml")):
        raw = open(p, "rb").read()
        docs = [raw]
        if raw[:2] == b"PK":
            z = zipfile.ZipFile(io.BytesIO(raw)); docs = [z.read(n) for n in z.namelist()]
        for d in docs:
            for ts in (e for e in ET.fromstring(d).iter() if _tag(e) == "TimeSeries"):
                curve = next((c.text for c in ts if _tag(c) == "curveType"), "A01")
                for per in (e for e in ts if _tag(e) == "Period"):
                    if next((c.text for c in per if _tag(c) == "resolution"), "") != "PT15M":
                        continue
                    ti = next(c for c in per if _tag(c) == "timeInterval")
                    t0 = datetime.strptime(next(g.text for g in ti if _tag(g) == "start"), "%Y-%m-%dT%H:%MZ")
                    t1 = datetime.strptime(next(g.text for g in ti if _tag(g) == "end"), "%Y-%m-%dT%H:%MZ")
                    pts = defaultdict(dict)
                    for pt in (c for c in per if _tag(c) == "Point"):
                        v = {_tag(g).split(".")[-1]: g.text for g in pt}
                        if "position" in v and "amount" in v:
                            pts[v.get("category", "A04")][int(v["position"])] = float(v["amount"])
                    n = int((t1 - t0).total_seconds() // 900)
                    for cat, punten in pts.items():
                        if cat in q:
                            STATS["punten"] += len(punten); STATS["kwartieren"] += n
                            for k, prijs in enumerate(vul_posities(punten, n, curve)):
                                if prijs is not None:
                                    q[cat][t0 + timedelta(minutes=15 * k)] = prijs
    df = pd.DataFrame({"tekort": pd.Series(q["A05"], dtype=float), "overschot": pd.Series(q["A04"], dtype=float)}).sort_index()
    df.index = pd.to_datetime(df.index)
    df["tekort"] = df["tekort"].fillna(df["overschot"]); df["overschot"] = df["overschot"].fillna(df["tekort"])
    return df


def schrijf_onbalans(df=None):
    df = onbalans_kwartier() if df is None else df
    uit = pd.DataFrame({"timestamp_utc": df.index.strftime("%Y-%m-%d %H:%M"), "jaar": df.index.year, "maand": df.index.month,
                        "prijs_tekort_eur_mwh": df["tekort"].round(2).values, "prijs_overschot_eur_mwh": df["overschot"].round(2).values})
    uit.to_csv(f"{OUT}/fact_onbalans_nl.csv", index=False)
    print(f"  -> fact_onbalans_nl.csv: {len(uit)} rijen")


def dagen_onbalans(df):
    """-> {datum: (koop[24], verkoop[24])} met uurgemiddelden; alleen uren met vier kwartieren en dagen met 24 uur."""
    d = df.dropna()
    u = d.resample("1h").mean()[d.resample("1h")["tekort"].count() == 4]
    return {dag: (g["tekort"].tolist(), g["overschot"].tolist()) for dag, g in u.groupby(u.index.date) if len(g) == 24}


def dagen_dagmarkt():
    u = pd.read_csv(f"{OUT}/fact_nl_uur_alle_jaren.csv", usecols=["timestamp_utc", "prijs_eur_mwh"]).dropna()
    u["t"] = pd.to_datetime(u.timestamp_utc)
    uit = {}
    for dag, g in u.groupby(u.t.dt.date):
        if len(g) == 24:
            p = g.sort_values("t").prijs_eur_mwh.tolist(); uit[dag] = (p, p)
    return uit


def beste_blok(koop, verkoop, h, eff):
    """Beste paar (laadblok i, ontlaadblok j >= i + h) binnen een dag, per MW. -> (winst, (i, j))"""
    n = len(koop)
    cb = [sum(koop[i:i + h]) for i in range(n - h + 1)]; sb = [sum(verkoop[j:j + h]) for j in range(n - h + 1)]
    beste, paar, goedkoop, gi = 0.0, None, float("inf"), None
    for j in range(h, n - h + 1):
        if cb[j - h] < goedkoop:
            goedkoop, gi = cb[j - h], j - h
        g = sb[j] * eff - goedkoop
        if g > beste:
            beste, paar = g, (gi, j)
    return beste, paar


def winst(koop, verkoop, paar, h, eff):
    i, j = paar
    return sum(verkoop[j:j + h]) * eff - sum(koop[i:i + h])


def reeksen(markt, dagmarkt=None):
    """Dagwinst per MW: perfect, plan (op gisteren, verlies telt mee), skip (verliesdag overgeslagen), op_da_plan."""
    rijen = {}
    for d in sorted(markt):
        koop, verkoop = markt[d]
        r = {"perfect": beste_blok(koop, verkoop, H, EFF)[0]}
        g = d - timedelta(days=1)
        if g in markt:
            paar = beste_blok(*markt[g], H, EFF)[1]
            r["plan"] = winst(koop, verkoop, paar, H, EFF) if paar else 0.0
            r["skip"] = max(r["plan"], 0.0)
        if dagmarkt is not None and d in dagmarkt:
            paar = beste_blok(*dagmarkt[d], H, EFF)[1]
            r["op_da_plan"] = winst(koop, verkoop, paar, H, EFF) if paar else 0.0
        rijen[d] = r
    return pd.DataFrame.from_dict(rijen, orient="index").sort_index()


def vooraf(a, b, venster=7):
    """Kies per dag reeks b als die over de zeven dagen tot en met eergisteren gemiddeld meer opleverde dan a."""
    df = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    gem = df.shift(2).rolling(venster, min_periods=4).mean()
    kies_b = gem["b"] > gem["a"]
    return df["b"].where(kies_b, df["a"]), kies_b


def irr(omzet_per_mw, capex_mwh):
    capex = capex_mwh * H * MW
    v = finance.irr_safe(finance.project_cashflows(capex, omzet_per_mw * MW, capex * OPEX_SH, LIFE, DEG))
    return None if v is None or v != v else float(v)


def per_jaar(s, j):
    x = s[[d.year == j for d in s.index]].dropna()
    return (float(x.mean()) * 365, len(x)) if len(x) else (None, 0)


def zon(jaren):
    L = pd.read_csv(f"{OUT}/fact_land_jaar.csv"); nl = L[L.land == "Nederland"].set_index("jaar")
    u = pd.read_csv(f"{OUT}/fact_nl_uur_alle_jaren.csv", usecols=["timestamp_utc", "jaar", "prijs_eur_mwh"]).dropna()
    w = pd.read_csv(f"{OUT}/fact_weer_uur.csv", usecols=["timestamp_utc", "straling_w_m2"])
    w = w.groupby(w.timestamp_utc.str[:16]).straling_w_m2.mean()
    w.index = (pd.to_datetime(w.index) - pd.Timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")      # straling staat op het eind van het uur, de prijs op het begin
    u["r"] = u.timestamp_utc.str[:16].map(w)
    rijen = []
    for j in jaren:
        g = u[(u.jaar == j) & u.r.notna()]; mp = g.prijs_eur_mwh.mean(); prijs = float(nl.loc[j, "gem_prijs"])
        f_prof = (g.prijs_eur_mwh * g.r).sum() / g.r.sum() / mp
        f_afs = (g.prijs_eur_mwh.clip(lower=0) * g.r).sum() / g.r.sum() / mp
        for methode, f in (("Opwekdata Energy-Charts", float(nl.loc[j, "capture_zon"])), ("Instralingsprofiel, niet afschakelen", float(f_prof)),
                           ("Instralingsprofiel, afschakelen bij negatieve prijs", float(f_afs))):
            for flh in (740, 950):
                v = finance.irr_safe(finance.project_cashflows(449_000 * 20, prijs * f * flh * 20, 15_700 * 20, 25, 0.005))
                rijen.append([j, methode, flh, round(f, 4), round(prijs * f, 2), None if v != v else round(float(v), 4)])
    return rijen


def main():
    ibq = onbalans_kwartier(); schrijf_onbalans(ibq)
    da, ib = dagen_dagmarkt(), dagen_onbalans(ibq)
    rda, rib = reeksen(da), reeksen(ib, da)
    v1, k1 = vooraf(rda["skip"], rib["plan"]); v2, k2 = vooraf(rda["skip"], rib["op_da_plan"])
    achteraf = pd.concat([rda["skip"], rib["plan"], rib["op_da_plan"]], axis=1).dropna().max(axis=1)
    reeks = {"Dagmarkt": rda["skip"], "Dagmarkt zonder overslaan": rda["plan"], "Dagmarkt perfect": rda["perfect"],
             "Onbalans op dagmarktplan": rib["op_da_plan"], "Onbalans plan op gisteren": rib["plan"],
             "Onbalans plan op gisteren, verliesdagen overgeslagen (niet uitvoerbaar)": rib["skip"],
             "Gestapeld vooraf, onbalans plan op gisteren": v1, "Gestapeld vooraf, onbalans op dagmarktplan": v2,
             "Gestapeld achteraf (bovengrens)": achteraf, "Onbalans perfect": rib["perfect"]}
    jaren = (2023, 2024, 2025, 2026)
    stap, irrs, uit = [], [], {}
    for j in jaren:
        uit[j] = {}
        for naam, s in reeks.items():
            o, n = per_jaar(s, j)
            uit[j][naam] = {"omzet_per_mw": o, "dagen": n}
            if o is not None:
                stap.append([j, naam, round(o * MW), round(o), irr(o, CAPEX[0])])
                if naam in ("Dagmarkt", "Gestapeld vooraf, onbalans plan op gisteren", "Gestapeld vooraf, onbalans op dagmarktplan", "Onbalans perfect"):
                    irrs += [[j, naam, c, irr(o, c)] for c in CAPEX]
        uit[j]["aandeel_dagen_onbalans_gekozen"] = {"plan op gisteren": float(k1[[d.year == j for d in k1.index]].mean()),
                                                    "op dagmarktplan": float(k2[[d.year == j for d in k2.index]].mean())}
    pd.DataFrame(stap, columns=["jaar", "strategie", "omzet_eur", "omzet_per_mw", "irr"]).to_csv(f"{OUT}/fact_batterij_stapeling.csv", index=False)
    pd.DataFrame(irrs, columns=["jaar", "strategie", "capex_per_mwh", "irr"]).to_csv(f"{OUT}/fact_batterij_irr.csv", index=False)
    z = zon(jaren)
    pd.DataFrame(z, columns=["jaar", "methode", "vollasturen", "capture_rate", "capture_prijs", "irr_voor_belasting"]).to_csv(f"{OUT}/fact_herijking.csv", index=False)
    dq = ibq.dropna(); dubbel = (dq.tekort - dq.overschot).abs() > 0.005
    diag = {"aandeel_posities_opgevuld": 1 - STATS["punten"] / max(1, STATS["kwartieren"]), "kwartieren": int(len(dq)),
            "aandeel_dubbele_prijs_per_jaar": {int(k): float(v) for k, v in dubbel.groupby(dq.index.year).mean().items()},
            "gem_verschil_tekort_min_overschot": float((dq.tekort - dq.overschot).mean()), "volledige_dagen_onbalans": len(ib), "volledige_dagen_dagmarkt": len(da)}
    json.dump({"batterij": uit, "zon": z, "onbalansdata": diag}, open("reports/herijking.json", "w"), indent=1, default=float)
    t = pd.DataFrame({j: {n: (round(v["omzet_per_mw"] / 1000, 1) if isinstance(v, dict) and v.get("omzet_per_mw") is not None else None) for n, v in uit[j].items() if n in reeks} for j in jaren})
    print("Batterij 2 uur, k EUR per MW per jaar:"); print(t.to_string())
    print("aandeel dagen onbalans gekozen:", {j: {k: round(v, 2) for k, v in uit[j]["aandeel_dagen_onbalans_gekozen"].items()} for j in jaren})
    print("IRR:"); print(pd.DataFrame(irrs, columns=["jaar", "strategie", "capex", "irr"]).pivot_table(index=["strategie", "jaar"], columns="capex", values="irr").round(3).to_string())
    print("onbalansdata:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in diag.items()})
    print("Zon:"); print(pd.DataFrame(z, columns=["jaar", "methode", "flh", "f", "prijs", "irr"]).pivot_table(index=["methode", "flh"], columns="jaar", values="irr").round(3).to_string())
    print(pd.DataFrame(z, columns=["jaar", "methode", "flh", "f", "prijs", "irr"]).query("flh==740").pivot_table(index="methode", columns="jaar", values="f").round(3).to_string())


if __name__ == "__main__":
    main()
