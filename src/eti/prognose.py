"""Prognose (_SA): Nederlandse dagmarkt tot eind 2026 en over 2027, en scenario's tot 2030 met een eindpunt in 2050.

Statistisch deel (maandreeksen sinds 2019): prijs, zonprijs (de prijs die zon ontvangt), negatieve uren, dagspreiding.
Vier modellen worden op het verleden getoetst (steeds vanaf een eerder moment vooruit voorspellen); het model met de
kleinste fout wint. De intervallen zijn de werkelijk gemaakte fouten uit die toets, geen formule.
Scenariodeel (2028 en later): geen statistiek maar benoemde aannames, zie SCENARIOS.

Uitvoer: fact_prognose_SA, fact_prognose_toets_SA, fact_prognose_jaar_SA, fact_decompositie_SA, fact_scenario_SA.
Gebruik:  PYTHONPATH=src python3 -m eti.prognose [datamap] [uitvoermap]
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import optimize

DATA = "powerbi/data"
S = 12                                   # seizoenslengte in maanden
MIN_UREN = 600                           # een maand met minder uren telt als onvolledig
TRANSFORMATIE = {"prijs": "log", "zonprijs": "log", "dagspreiding": "log", "negatieve_uren": "wortel"}
NORMAAL = (2023, 2024, 2025)
# Aannames per scenario (geen voorspelling). prijs: niveau van de jaarprijs vanaf 2028; jaareffect: verandering per jaar
# van de capture rate door alles behalve de zonaandelen (flexibiliteit, opslag, vraagsturing); tempo: uitbouw van zon
# ten opzichte van 2019-2025 (1 = zelfde tempo); batterij: omzet per MW op de dagmarkt in 2030.
SCENARIOS = {
    "basis": {"prijs": "normaal", "jaareffect": 0.0, "tempo": 1.0, "batterij": "normaal",
              "uitleg": "prijs terug naar het gemiddelde van 2023-2025; zon groeit in het tempo van 2019-2025; overige druk op de capture rate blijft gelijk; batterij-omzet op het gemiddelde van 2023-2025"},
    "flexibiliteit haalt zon in": {"prijs": "normaal", "jaareffect": 0.01, "tempo": 0.5, "batterij": "half",
                                   "uitleg": "gunstig voor zon, ongunstig voor opslag: uitbouw van zon halveert, opslag en vraagsturing winnen een punt capture rate per jaar terug, batterij-omzet halveert zoals in Californie en Texas"},
    "zon loopt uit op flexibiliteit": {"prijs": "normaal", "jaareffect": -0.03, "tempo": 1.0, "batterij": "2026",
                                       "uitleg": "ongunstig voor zon, gunstig voor opslag: de overige druk op de capture rate loopt door op de helft van het tempo van 2023-2025, batterij-omzet blijft op het niveau van 2026"},
    "gas blijft duur": {"prijs": "2026", "jaareffect": 0.0, "tempo": 1.0, "batterij": "2026",
                        "uitleg": "als basis, met de jaarprijs en de batterij-omzet op het niveau van 2026"},
    "gas wordt goedkoop": {"prijs": "laag", "jaareffect": 0.0, "tempo": 1.0, "batterij": "met de prijs mee",
                           "uitleg": "als basis, met de jaarprijs op het laagste jaar sinds 2023 en de batterij-omzet evenredig lager"},
}


# ------------------------------------------------------------------------------------------------------- reeksen
def maandreeksen(data=DATA):
    """Maandcijfers uit de uurtabel. Geeft (tabel per maand, gewicht van elke kalendermaand in de zonopwek)."""
    u = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), parse_dates=["timestamp_utc"]).dropna(subset=["prijs_eur_mwh"])
    u = u.set_index("timestamp_utc").sort_index()
    dag = u.prijs_eur_mwh.resample("D").agg(lambda s: s.max() - s.min() if len(s) >= 20 else np.nan)
    m = pd.DataFrame({"prijs": u.prijs_eur_mwh.resample("MS").mean(),
                      "zonprijs": (u.prijs_eur_mwh * u.solar_mw).resample("MS").sum() / u.solar_mw.resample("MS").sum(),
                      "negatieve_uren": (u.prijs_eur_mwh < 0).resample("MS").sum().astype(float),
                      "dagspreiding": dag.resample("MS").mean(), "uren": u.prijs_eur_mwh.resample("MS").count(),
                      "zon_mwh": u.solar_mw.resample("MS").sum()})
    m["volledig"] = m.uren >= MIN_UREN
    recent = m[m.index.year.isin(NORMAAL)]
    gewicht = recent.groupby(recent.index.month).zon_mwh.sum() / recent.zon_mwh.sum()
    return m, gewicht


def heen(y, soort):
    return np.log(y) if soort == "log" else np.sqrt(y) if soort == "wortel" else np.asarray(y, float)


def terug(z, soort):
    return np.exp(z) if soort == "log" else np.maximum(z, 0) ** 2 if soort == "wortel" else z


# ------------------------------------------------------------------------------------------------------ modellen
def seizoensnaief(y, h):
    """Zelfde maand een jaar eerder."""
    return np.array([y[len(y) - S + (i % S)] for i in range(h)])


def holt_winters(y, h):
    """Exponentiele demping met niveau, gedempte trend en maandpatroon; parameters op de kleinste eenstapsfout."""
    def loop(par, vooruit=0):
        a, b, g, phi = par
        niveau, trend = y[:S].mean(), (y[S:2 * S].mean() - y[:S].mean()) / S
        seizoen, fout = list(y[:S] - niveau), []
        for t in range(len(y)):
            fout.append(y[t] - (niveau + phi * trend + seizoen[t % S]))
            nieuw = a * (y[t] - seizoen[t % S]) + (1 - a) * (niveau + phi * trend)
            trend = b * (nieuw - niveau) + (1 - b) * phi * trend
            seizoen[t % S] = g * (y[t] - nieuw) + (1 - g) * seizoen[t % S]
            niveau = nieuw
        pad = [niveau + trend * sum(phi ** k for k in range(1, i + 2)) + seizoen[(len(y) + i) % S] for i in range(vooruit)]
        return np.array(fout), np.array(pad)
    best = optimize.minimize(lambda p: (loop(p)[0][S:] ** 2).sum(), x0=[0.4, 0.05, 0.1, 0.9], method="L-BFGS-B",
                             bounds=[(0.01, 0.99), (0.0, 0.5), (0.0, 0.99), (0.5, 0.98)])
    return loop(best.x, h)[1]


def terugkeer(y, h, venster=36):
    """Terugkeer naar het gemiddelde: maandpatroon plus een afwijking die elke maand met een vaste factor slinkt.
    Het niveau is de mediaan van de laatste `venster` maanden, zodat een oude schok het doel niet verschuift."""
    maand = np.arange(len(y)) % S
    glad = pd.Series(y).rolling(S, center=True).mean().rolling(2).mean().shift(-1).values     # gecentreerd jaargemiddelde
    afwijking = y - glad
    patroon = np.array([np.nanmedian(afwijking[maand == k]) for k in range(S)])                # mediaan: een schokjaar telt niet door
    patroon -= patroon.mean()
    kaal = y - patroon[maand]
    niveau = np.median(kaal[-venster:])
    u = kaal - niveau
    phi = float(np.clip((u[1:] @ u[:-1]) / (u[:-1] @ u[:-1]), 0.0, 0.98))
    return np.array([niveau + patroon[(len(y) + i) % S] + phi ** (i + 1) * u[-1] for i in range(h)])


def gemiddeld(y, h):
    """Gemiddelde van Holt-Winters en terugkeer: twee zwakke voorspellers middelen is vaak beter dan een van beide."""
    return (holt_winters(y, h) + terugkeer(y, h)) / 2


MODELLEN = {"seizoensnaief": seizoensnaief, "Holt-Winters gedempt": holt_winters, "terugkeer naar het gemiddelde": terugkeer,
            "gemiddelde van twee": gemiddeld}


# ------------------------------------------------------------------------------------------------------ toetsing
def terugtoets(y, soort, h=13, start=48):
    """Voorspel vanaf elk eerder moment h maanden vooruit. Geeft per model een matrix (momenten x horizon) met de
    voorspelling, en de werkelijkheid in dezelfde vorm (oorspronkelijke eenheid)."""
    z = heen(y, soort)
    momenten = range(start, len(y) - h + 1)
    echt = np.array([y[t:t + h] for t in momenten])
    return {naam: np.array([terug(f(z[:t], h), soort) for t in momenten]) for naam, f in MODELLEN.items()}, echt


def fouten(voorspeld, echt):
    e = voorspeld - echt
    return {"rmse": float(np.sqrt((e ** 2).mean())), "mae": float(np.abs(e).mean()),
            "mape": float(np.abs(e[echt != 0] / echt[echt != 0]).mean())}


def kies(y, soort):
    """Toets alle modellen (horizon 1 tot 12 maanden) en kies het model met de kleinste fout (RMSE)."""
    vs, echt = terugtoets(y, soort)
    tabel = {naam: fouten(v[:, :12], echt[:, :12]) for naam, v in vs.items()}
    z = heen(y, soort)
    for naam, f in MODELLEN.items():                                # apart: de laatste twaalf maanden als controlejaar
        tabel[naam].update({"controle_" + k: v for k, v in fouten(terug(f(z[:-12], 12), soort), y[-12:]).items()})
    beste = min(tabel, key=lambda n: tabel[n]["rmse"])
    return beste, tabel, vs[beste], echt


def interval(fout_rel, niveaus=(0.80, 0.95)):
    """Grenzen uit de werkelijk gemaakte relatieve fouten (voorspeld / echt): echt = voorspeld / verhouding.
    Sleutel 0.5 geeft de factor voor de middelste uitkomst: het model gecorrigeerd voor zijn gemiddelde misser."""
    uit = {0.5: 1 / np.median(fout_rel)}
    for n in niveaus:
        lo, hi = np.quantile(fout_rel, [(1 - n) / 2, 1 - (1 - n) / 2])
        uit[n] = (1 / hi, 1 / lo)
    return uit


# ------------------------------------------------------------------------------------------------------ prognose
def decompositie(y, index):
    """Klassieke ontleding: trend (gecentreerd 12-maandsgemiddelde), maandpatroon en rest."""
    s = pd.Series(y, index=index)
    trend = s.rolling(S, center=True).mean().rolling(2).mean().shift(-1)
    patroon = (s - trend).groupby(index.month).transform("mean")
    patroon -= patroon.mean()
    return pd.DataFrame({"waarde": s, "trend": trend, "seizoen": patroon, "rest": s - trend - patroon})


def prognose(data=DATA, horizon=14):
    m, gewicht = maandreeksen(data)
    vol = m[m.volledig]
    deel = m[~m.volledig & (m.index > vol.index.max())]             # de lopende maand
    maanden = pd.date_range(vol.index.max() + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    rijen, toets, jaar, ontleed, paden, toetsdata = [], [], [], [], {}, {}
    for reeks, soort in TRANSFORMATIE.items():
        y = vol[reeks].values.astype(float)
        if soort == "log" and (y <= 0).any():
            soort = "geen"
        beste, tabel, vs, echt = kies(y, soort)
        for naam, f in tabel.items():
            toets.append({"reeks": reeks, "model": naam, "gekozen": naam == beste, **f})
        pad = terug(MODELLEN[beste](heen(y, soort), horizon), soort)
        if len(deel):                                               # lopende maand: wat al gemeten is telt mee
            aandeel = float(deel.uren.iloc[0]) / (deel.index[0].days_in_month * 24)
            gezien = float(deel[reeks].iloc[0])
            if reeks == "negatieve_uren":                           # aantal tot nu toe plus de verwachting voor de rest van de maand
                nu_maand = gezien + pad[0] * (1 - aandeel)
            else:                                                   # rest van de maand: halverwege tussen de meting en het model
                nu_maand = aandeel * gezien + (1 - aandeel) * (gezien + pad[0]) / 2
            verder = terug(MODELLEN[beste](heen(np.append(y, max(nu_maand, 1e-6) if soort == "log" else nu_maand), soort), horizon - 1), soort)
            pad = np.append(nu_maand, verder)
        paden[reeks] = pd.Series(pad, index=maanden)
        toetsdata[reeks] = (vs, echt)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(echt > 0, vs / echt, np.nan)
        absoluut = vs - echt
        for i, (t, w) in enumerate(zip(maanden, pad)):
            k = min(i, vs.shape[1] - 1)
            if reeks == "negatieve_uren":                           # aantallen: fout in uren, niet als verhouding
                q = {n: (max(w - np.quantile(absoluut[:, k], 1 - (1 - n) / 2), 0), max(w - np.quantile(absoluut[:, k], (1 - n) / 2), 0)) for n in (0.80, 0.95)}
                midden = max(w - np.median(absoluut[:, k]), 0)
            else:
                f = interval(rel[:, k][~np.isnan(rel[:, k])])
                q, midden = {n: (w * f[n][0], w * f[n][1]) for n in (0.80, 0.95)}, w * f[0.5]
            rijen.append({"reeks": reeks, "periode": t.strftime("%Y-%m"), "soort": "prognose", "waarde": w, "midden_na_correctie": midden, "laag80": q[0.80][0],
                          "hoog80": q[0.80][1], "laag95": q[0.95][0], "hoog95": q[0.95][1], "model": beste})
        for t, w in vol[reeks].tail(36).items():
            rijen.append({"reeks": reeks, "periode": t.strftime("%Y-%m"), "soort": "waarneming", "waarde": w})
        d = decompositie(y, vol.index).reset_index().rename(columns={"timestamp_utc": "periode"})
        d["periode"], d["reeks"] = d.periode.dt.strftime("%Y-%m"), reeks
        ontleed.append(d)
        som = reeks == "negatieve_uren"                             # jaarcijfers: som voor aantallen, anders urengewogen gemiddelde
        v12, e12 = vs[:, 1:13], echt[:, 1:13]                       # venster van 12 maanden dat een maand na het moment begint
        agg_v, agg_e = (v12.sum(1), e12.sum(1)) if som else (v12.mean(1), e12.mean(1))
        nu = vol[vol.index.year == maanden[0].year]
        dit = pd.concat([nu[reeks], paden[reeks][paden[reeks].index.year == maanden[0].year]])
        uren = np.array([t.days_in_month * 24 for t in dit.index])
        waarde = dit.sum() if som else float((dit.values * uren).sum() / uren.sum())
        jaar.append({"reeks": reeks, "jaar": maanden[0].year, "soort": "waarneming plus prognose voor de resterende maanden", "waarde": waarde,
                     "maanden_prognose": int((dit.index >= maanden[0]).sum())})
        volgend = paden[reeks][paden[reeks].index.year == maanden[0].year + 1]
        w = volgend.sum() if som else volgend.mean()
        if som:
            q = {n: (max(w - np.quantile(agg_v - agg_e, 1 - (1 - n) / 2), 0), max(w - np.quantile(agg_v - agg_e, (1 - n) / 2), 0)) for n in (0.80, 0.95)}
            midden = max(w - np.median(agg_v - agg_e), 0)
        else:
            f = interval(agg_v / agg_e)
            q, midden = {n: (w * f[n][0], w * f[n][1]) for n in (0.80, 0.95)}, w * f[0.5]
        jaar.append({"reeks": reeks, "jaar": maanden[0].year + 1, "soort": "prognose", "waarde": w, "midden_na_correctie": midden, "laag80": q[0.80][0], "hoog80": q[0.80][1],
                     "laag95": q[0.95][0], "hoog95": q[0.95][1], "maanden_prognose": 12, "model": beste})
    for j in (maanden[0].year, maanden[0].year + 1):                # capture rate: zonprijs gewogen naar zonopwek, gedeeld door de jaarprijs
        z = pd.concat([vol.zonprijs, paden["zonprijs"]]); z = z[z.index.year == j]
        p = pd.concat([vol.prijs, paden["prijs"]]); p = p[p.index.year == j]
        g = gewicht.reindex(z.index.month).values
        rij = {"reeks": "capture_rate_zon", "jaar": j, "soort": "afgeleid uit prijs en zonprijs", "waarde": float((z.values * g).sum() / g.sum() / p.mean())}
        if j > maanden[0].year:                                     # interval uit dezelfde toets, voor het venster van 12 maanden
            (vz, ez), (vp, ep) = toetsdata["zonprijs"], toetsdata["prijs"]
            verhouding = []
            for i in range(len(vz)):
                gw = gewicht.reindex(vol.index[48 + i + 1:48 + i + 13].month).values
                verhouding.append(((vz[i, 1:13] * gw).sum() / gw.sum() / vp[i, 1:13].mean()) / ((ez[i, 1:13] * gw).sum() / gw.sum() / ep[i, 1:13].mean()))
            f = interval(np.array(verhouding))
            rij["midden_na_correctie"] = rij["waarde"] * f[0.5]
            for n in (0.80, 0.95):
                rij[f"laag{int(n * 100)}"], rij[f"hoog{int(n * 100)}"] = rij["waarde"] * f[n][0], rij["waarde"] * f[n][1]
        jaar.append(rij)
    return pd.DataFrame(rijen), pd.DataFrame(toets), pd.DataFrame(jaar), pd.concat(ontleed, ignore_index=True), m


# ----------------------------------------------------------------------------------------------------- scenario's
def scenarios(data=DATA, jaartabel=None):
    """Jaarpaden 2027 tot 2030 en de eindpunten 2040 en 2050 onder drie sets aannames (zie SCENARIOS)."""
    from . import sa
    d = sa.regressiedata(data)
    reg, _, _ = sa.regressie(data)
    coef = reg[reg.onderdeel == "coefficient"].set_index("term").coef
    nl = d[d.biedzone == "NL"].sort_values("jaar")
    tempo_eigen = (nl.aandeel_zon_pct.iloc[-1] - nl.aandeel_zon_pct.iloc[0]) / (nl.jaar.iloc[-1] - nl.jaar.iloc[0])
    tempo_buur = (nl.buur_zon_pct.iloc[-1] - nl.buur_zon_pct.iloc[0]) / (nl.jaar.iloc[-1] - nl.jaar.iloc[0])
    lj = pd.read_csv(os.path.join(data, "fact_land_jaar.csv")).query("biedzone == 'NL'").set_index("jaar")
    fl = pd.read_csv(os.path.join(data, "fact_flex_land.csv")).query("uren_opslag == 2 and land == 'Nederland'").set_index("jaar")
    lcoe = pd.read_csv(os.path.join(data, "fact_regio_jaar.csv")).query("regio == 'Nederland'").set_index("jaar").lcoe_eur_mwh
    normaal_prijs = float(lj.loc[list(NORMAAL), "gem_prijs"].mean())
    normaal_bat = float(fl.loc[list(NORMAAL), "omzet_realistisch_per_mw"].mean())
    j2026 = None if jaartabel is None else jaartabel[(jaartabel.reeks == "prijs") & (jaartabel.jaar == 2026)].waarde
    prijs = {"normaal": normaal_prijs, "2026": float(j2026.iloc[0]) if j2026 is not None and len(j2026) else float(lj.loc[lj.index.max(), "gem_prijs"]),
             "laag": float(lj.loc[[j for j in lj.index if j >= 2023], "gem_prijs"].min())}
    batterij = {"normaal": normaal_bat, "2026": float(fl.loc[fl.index.max(), "omzet_realistisch_per_mw"]), "half": normaal_bat / 2,
                "met de prijs mee": normaal_bat * prijs["laag"] / normaal_prijs}
    start_jaar, start_capture = int(nl.jaar.iloc[-1]), float(nl.capture_zon.iloc[-1])
    p2027 = None if jaartabel is None else float(jaartabel[(jaartabel.reeks == "prijs") & (jaartabel.jaar == 2027)].waarde.iloc[0])
    rijen = []
    for naam, a in SCENARIOS.items():
        doel, bat2030 = prijs[a["prijs"]], batterij[a["batterij"]]
        for j in (2027, 2028, 2029, 2030, 2040, 2050):
            n = min(j, 2030) - start_jaar                           # na 2030 geen verdere aanname: de capture rate blijft op het niveau van 2030
            capture = start_capture + n * a["tempo"] * (coef["aandeel_zon_pct"] * tempo_eigen + coef["buur_zon_pct"] * tempo_buur) + n * a["jaareffect"]
            capture = float(np.clip(capture, 0.25, 1.0))
            # prijs: 2027 volgt de statistische prognose, 2028 ligt halverwege, vanaf 2029 geldt het niveau van het scenario
            p = doel if (p2027 is None or j >= 2029) else p2027 if j == 2027 else (p2027 + doel) / 2
            kosten = float(np.interp(j, lcoe.index, lcoe.values))
            bat = normaal_bat + (bat2030 - normaal_bat) * min(j - start_jaar, 5) / 5
            rijen.append({"scenario": naam, "jaar": j, "prijs_eur_mwh": p, "capture_rate_zon": capture, "capture_prijs": p * capture,
                          "lcoe_eur_mwh": kosten, "vereiste_capture_rate": kosten / p, "marge_eur_mwh": p * capture - kosten,
                          "batterij_dagmarkt_per_mw": bat, "aannames": a["uitleg"]})
    par = {"tempo_eigen_zon_pp_per_jaar": tempo_eigen, "tempo_buren_zon_pp_per_jaar": tempo_buur, "coef_eigen": coef["aandeel_zon_pct"],
           "coef_buren": coef["buur_zon_pct"], "capture_startjaar": start_capture, "startjaar": start_jaar}
    return pd.DataFrame(rijen), par


def main(data=DATA, uit=None):
    uit = uit or data
    schrijf = lambda df, naam: (df.to_csv(os.path.join(uit, naam), index=False), print(f"  -> {naam}: {len(df)} rijen"))
    maand, toets, jaar, ontleed, _ = prognose(data)
    schrijf(maand, "fact_prognose_SA.csv"); schrijf(toets, "fact_prognose_toets_SA.csv"); schrijf(jaar, "fact_prognose_jaar_SA.csv")
    schrijf(ontleed, "fact_decompositie_SA.csv")
    sc, par = scenarios(data, jaar)
    schrijf(sc, "fact_scenario_SA.csv")
    print("  aannames scenario's:", {k: round(float(v), 4) for k, v in par.items()})


if __name__ == "__main__":
    main(*sys.argv[1:3])
