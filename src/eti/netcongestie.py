"""Dashboards 8 en 13 (en vervolg 26): netcongestie in Nederland, capaciteitskaart Netbeheer Nederland 2026.

Invoer (data/raw/netcongestie/, niet in git; download via capaciteitskaart.netbeheernederland.nl):
  voedingsgebieden.csv   regionale netbeheerders, per voedingsgebied (MW, ; en decimale komma)
  tennetgebieden.csv     TenneT-congestiegebieden (MW)
  tennetcongestie.csv    status per TenneT-station
  congestie_pc6.csv      status per zescijferige postcode
Statuscodes (aanname, RAGKind van het informatiemodel capaciteitskaart 2.1, oplopend):
  0 = beschikbaar zonder wachtrij, 1 = beperkt beschikbaar, 2 = in onderzoek met wachtrij,
  3 = tekort met wachtrij, -1 = onbekend.  Controleer dit tegen de legenda van de kaart.
Uitvoer (tableau/data):
  t29_congestie_gebied.csv     per voedingsgebied: capaciteit, gevraagd, verhouding, wachtrij, jaartal opgelost
  t30_congestie_rnb.csv        per netbeheerder en provincie: optelling en mediaan jaartal
  t31_congestie_tennet.csv     per TenneT-gebied
  t32_congestie_gemeente.csv   per gemeente: aandeel postcodes per status, afname en opwek
Gebruik:  PYTHONPATH=src python3 -m eti.netcongestie
"""
from pathlib import Path
import numpy as np
import pandas as pd

MAP = Path("data/raw/netcongestie")
UIT = Path("tableau/data")
STATUS = {-1: "Onbekend", 0: "Beschikbaar", 1: "Beperkt", 2: "In onderzoek", 3: "Tekort"}
ONBEPAALD = 2090  # jaartallen als 2099 betekenen 'geen datum'


def lees(naam):
    return pd.read_csv(MAP / naam, sep=";", decimal=",", low_memory=False)


def _jaartal(s):
    s = pd.to_numeric(s, errors="coerce")
    return s.where(s < ONBEPAALD)


REFERENTIE = [  # officiele wachtrijcijfers (Kamerstukken / Landelijk Actieprogramma Netcongestie)
    ("Regionaal, afname", 9.1, "14.044 verzoeken, stand 1 juli 2025", "Antwoord Kamervragen 2 februari 2026 (AH 1011)"),
    ("Regionaal, invoeding", 4.6, "8.539 verzoeken, stand 1 juli 2025", "Antwoord Kamervragen 2 februari 2026 (AH 1011)"),
    ("TenneT, afname", 38.0, "212 aanvragen", "Kamerbrief 8 doorbraken, 4 februari 2026"),
]


def verschoven_invoeding(v):
    """Bronfout: bij een deel van de rijen (vooral Liander) staat in wachtrij_invoeding (MW) het AANTAL afnameverzoeken.
    Herkenbaar doordat beide gelijk zijn en groter dan nul. Die waarden worden leeg gemaakt."""
    return (v["wachtrij_invoeding"] == v["unieke_verzoeken_afname"]) & (v["wachtrij_invoeding"] > 0)


def gebieden(v=None):
    v = lees("voedingsgebieden.csv") if v is None else v.copy()
    if "unieke_verzoeken_afname" in v:
        fout = verschoven_invoeding(v)
        v["invoeding_verschoven"] = fout
        v.loc[fout, "wachtrij_invoeding"] = float("nan")
    kol = ["aanwezige_transportcapaciteit_invoeding", "aanwezige_transportcapaciteit_afname",
           "benodigde_transportcapaciteit_invoeding", "benodigde_transportcapaciteit_afname",
           "wachtrij_invoeding", "wachtrij_afname"]
    leeg = v[kol].fillna(0).eq(0).all(axis=1)
    v = v[~leeg].copy()
    for r in ("invoeding", "afname"):
        a, b = v[f"aanwezige_transportcapaciteit_{r}"], v[f"benodigde_transportcapaciteit_{r}"]
        v[f"verhouding_{r}"] = (b / a.where(a > 0)).round(3)
        v[f"tekort_{r}_mw"] = (b - a).clip(lower=0)
        v[f"jaar_opgelost_{r}"] = _jaartal(v[f"jaartal_opgelost_{r}"])
        v[f"geen_datum_{r}"] = pd.to_numeric(v[f"jaartal_opgelost_{r}"], errors="coerce") >= ONBEPAALD
    hou = ["voedingsgebied_id", "RNB", "provincie"] + kol + [c for c in v.columns if c.startswith(("verhouding_", "tekort_", "jaar_opgelost_", "geen_datum_", "invoeding_verschoven"))]
    return v[hou].rename(columns={"RNB": "netbeheerder"}), int(leeg.sum())


def afstemming(g, t):
    """Onze totalen tegen de officiele cijfers (controle C20)."""
    ruw_inv = g["wachtrij_invoeding"].sum() / 1000
    eigen = {"Regionaal, afname": g["wachtrij_afname"].sum() / 1000,
             "Regionaal, invoeding": ruw_inv,
             "TenneT, afname": t["wachtrij_afname"].sum() / 1000}
    uitleg = {"Regionaal, afname": "capaciteitskaart 2026 tegen stand juli 2025; rijen zonder cijfers (o.a. Stedin) ontbreken",
              "Regionaal, invoeding": f"na verwijderen van {int(g.get('invoeding_verschoven', pd.Series(dtype=bool)).sum())} rijen met een verschoven kolom (vooral Liander)",
              "TenneT, afname": "vermoedelijk dekking: de capaciteitskaart toont 23 congestiegebieden met 75 verzoeken, de officiele wachtrij telt 212 aanvragen; navragen bij TenneT"}
    r = pd.DataFrame(REFERENTIE, columns=["Wachtrij", "Officieel GW", "Officieel toelichting", "Bron"])
    r["Ons project GW"] = r["Wachtrij"].map(eigen).round(2)
    r["Verschil %"] = (100 * (r["Ons project GW"] / r["Officieel GW"] - 1)).round(0)
    r["Verklaring"] = r["Wachtrij"].map(uitleg)
    r["Status"] = ["Afwijking verklaard" if abs(x) <= 20 else "Afwijking open" for x in r["Verschil %"]]
    return r[["Wachtrij", "Ons project GW", "Officieel GW", "Verschil %", "Status", "Verklaring", "Officieel toelichting", "Bron"]]


def per_rnb(g):
    agg = {"voedingsgebied_id": "count", "aanwezige_transportcapaciteit_afname": "sum", "benodigde_transportcapaciteit_afname": "sum",
           "aanwezige_transportcapaciteit_invoeding": "sum", "benodigde_transportcapaciteit_invoeding": "sum",
           "wachtrij_afname": "sum", "wachtrij_invoeding": "sum", "tekort_afname_mw": "sum", "tekort_invoeding_mw": "sum",
           "jaar_opgelost_afname": "median", "jaar_opgelost_invoeding": "median"}
    r = g.groupby(["netbeheerder", "provincie"]).agg(agg).rename(columns={"voedingsgebied_id": "gebieden"}).reset_index()
    r["aandeel_gebieden_tekort_afname"] = g.groupby(["netbeheerder", "provincie"])["tekort_afname_mw"].apply(lambda s: (s > 0).mean()).values.round(3)
    return r


def tennet(t=None):
    t = lees("tennetgebieden.csv") if t is None else t.copy()
    t = t[t["congestiegebied"].notna()].copy()
    for r in ("afname", "invoeding"):
        a, b = t[f"aanwezige_transportcapaciteit_{r}"], t[f"benodigde_transportcapaciteit_{r}"]
        t[f"verhouding_{r}"] = (b / a.where(a > 0)).round(3)
        t[f"tekort_{r}_mw"] = (b - a).clip(lower=0)
        t[f"jaar_opgelost_{r}"] = _jaartal(t[f"jaartal_opgelost_{r}"])
    hou = ["congestiegebied"] + [c for c in t.columns if c.startswith(("aanwezige_", "benodigde_", "wachtrij_", "verhouding_", "tekort_", "jaar_opgelost_"))]
    return t[hou]


def gemeenten(p=None):
    p = pd.read_csv(MAP / "congestie_pc6.csv", sep=";", dtype=str) if p is None else p.copy()
    out = []
    for r in ("afname", "opwek"):
        s = pd.to_numeric(p[r], errors="coerce").map(STATUS)
        tab = pd.crosstab([p["provincie"], p["Gemeentenaam"]], s, normalize="index").mul(100).round(1)
        tab.columns = [f"{r} {c} %" for c in tab.columns]
        out.append(tab)
    n = p.groupby(["provincie", "Gemeentenaam"]).size().rename("postcodes")
    return pd.concat([n] + out, axis=1).reset_index().rename(columns={"Gemeentenaam": "gemeente"})


def controle(g, t, m):
    fout = []
    if (g.filter(like="tekort_") < 0).any().any(): fout.append("negatief tekort")
    if g["jaar_opgelost_afname"].dropna().lt(2026).any(): fout.append("jaartal voor 2026")
    som = m.filter(like="afname ").sum(axis=1)
    if not np.allclose(som, 100, atol=0.5): fout.append("aandelen gemeente tellen niet op tot 100")
    return fout


def main():
    UIT.mkdir(parents=True, exist_ok=True)
    g, leeg = gebieden(); r = per_rnb(g); t = tennet()
    heeft_pc6 = (MAP / "congestie_pc6.csv").exists()
    m = gemeenten() if heeft_pc6 else pd.read_csv(UIT / "t32_congestie_gemeente.csv")
    g.to_csv(UIT / "t29_congestie_gebied.csv", index=False); r.to_csv(UIT / "t30_congestie_rnb.csv", index=False)
    t.to_csv(UIT / "t31_congestie_tennet.csv", index=False)
    af = afstemming(g, t); af.to_csv(UIT / "t51_congestie_afstemming.csv", index=False)
    if heeft_pc6:
        m.to_csv(UIT / "t32_congestie_gemeente.csv", index=False)
        pc = pd.read_csv(MAP / "congestie_pc6.csv", sep=";", dtype=str, usecols=["afname", "opwek"])
    else:  # zonder ruwe postcodebestand: aandelen uit de bewaarde t32 (gewogen naar postcodes)
        w = m["postcodes"]; pc = None
    regels = [f"Netcongestie 2026: {len(g)} voedingsgebieden met cijfers ({leeg} rijen zonder cijfers weggelaten), {len(t)} TenneT-gebieden, {int(m.postcodes.sum())} postcodes.",
              (f"Postcodes met status Tekort: afname {100*(pc.afname=='3').mean():.1f}%, opwek {100*(pc.opwek=='3').mean():.1f}%." if pc is not None else
               f"Postcodes met status Tekort (uit t32): afname {(m['afname Tekort %']*w).sum()/w.sum():.1f}%, opwek {(m['opwek Tekort %']*w).sum()/w.sum():.1f}%."),
              f"Voedingsgebieden met gevraagd > aanwezig: afname {int((g.tekort_afname_mw>0).sum())}, invoeding {int((g.tekort_invoeding_mw>0).sum())}.",
              f"Mediaan jaartal opgelost: afname {g.jaar_opgelost_afname.median():.0f}, invoeding {g.jaar_opgelost_invoeding.median():.0f}; zonder datum (2099): afname {int(g.geen_datum_afname.sum())}, invoeding {int(g.geen_datum_invoeding.sum())}.",
              "Wachtrij per netbeheerder (MW afname / invoeding):"]
    w = g.groupby("netbeheerder")[["wachtrij_afname", "wachtrij_invoeding"]].sum(min_count=1).round(0)
    regels += [f"  {i}: {a:.0f} / {b:.0f}" for i, (a, b) in w.iterrows()]
    regels.append("TenneT, grootste gevraagd/aanwezig afname: " + "; ".join(f"{x.congestiegebied} {x.verhouding_afname:.2f} (opgelost {x.jaar_opgelost_afname:.0f})" for x in t.dropna(subset=["verhouding_afname"]).nlargest(5, "verhouding_afname").itertuples()))
    regels.append("Afstemming met officiele cijfers (GW): " + "; ".join(f"{x.Wachtrij} {x['Ons project GW']} tegen {x['Officieel GW']} ({x['Verschil %']:+.0f}%)" for _, x in af.iterrows()))
    fout = controle(g, t, m); regels.append("Controle: " + ("geslaagd" if not fout else ", ".join(fout)))
    Path("resultaten").mkdir(exist_ok=True); Path("resultaten/netcongestie.txt").write_text("\n".join(regels) + "\n")
    print("\n".join(regels))


if __name__ == "__main__":
    main()
