"""Onbalansregel die alleen het vorige kwartier kent.

Vraag: hoeveel van de waarde van onbalans vangt een batterij die realtime reageert, zonder kennis vooraf?
Bij elk kwartier gebruikt de regel alleen prijzen die dan al bekend zijn (het vorige kwartier of eerder) en
drempels uit de zeven dagen ervoor. Laden rekent af tegen de prijs voor een tekort, ontladen tegen de prijs
voor een overschot, zodat kwartieren met twee prijzen (regeltoestand 2) vanzelf meetellen.

Schrijft powerbi/data/fact_onbalans_regel.csv en reports/onbalansregel.json.
Gebruik:  PYTHONPATH=src python3 -m eti.onbalansregel
"""
import json
import os
import sys

import numpy as np
import pandas as pd

OUT = "powerbi/data"
EFF = 0.88            # rondrit-rendement, verrekend bij ontladen (gelijk aan de dagmarktberekening)
STAP = 0.25           # MWh per kwartier bij 1 MW
NIVEAUS = 8           # laadstappen van een batterij van 2 uur
VENSTER = 7 * 96      # zeven dagen aan kwartieren voor de drempels
KWANTIELEN = ((0.10, 0.90), (0.25, 0.75), (0.33, 0.67))
MARGES = (0, 10, 20, 30, 40, 50, 75, 100)
CAPEX = (300_000, 250_000, 200_000)


def lees(data=OUT):
    """Kwartierprijzen (tekort = prijs bij laden, overschot = prijs bij ontladen) met de dagmarktprijs van dat uur."""
    ob = pd.read_csv(os.path.join(data, "fact_onbalans_nl.csv"), parse_dates=["timestamp_utc"]).set_index("timestamp_utc").sort_index()
    ob = ob.rename(columns={"prijs_tekort_eur_mwh": "tekort", "prijs_overschot_eur_mwh": "overschot"})[["tekort", "overschot"]]
    ob = ob[~ob.index.duplicated()].asfreq("15min")
    da = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), usecols=["timestamp_utc", "prijs_eur_mwh"],
                     parse_dates=["timestamp_utc"]).drop_duplicates("timestamp_utc").set_index("timestamp_utc").prijs_eur_mwh
    ob["dagmarkt"] = da.reindex(ob.index.floor("h")).values
    return ob


def signalen_kwantiel(df, laag=0.25, hoog=0.75, vertraging=1, venster=VENSTER, eff=EFF):
    """Ontladen als de laatst bekende overschotprijs in het bovenste deel van de afgelopen week zat, laden als de
    laatst bekende tekortprijs in het onderste deel zat. Alles is `vertraging` kwartieren oud of ouder."""
    verkoop, koop = df.overschot.shift(vertraging), df.tekort.shift(vertraging)
    boven = verkoop.rolling(venster, min_periods=96).quantile(hoog)
    onder = koop.rolling(venster, min_periods=96).quantile(laag)
    zinvol = boven * eff > onder                       # alleen handelen als de drempels samen winst toelaten
    return ((koop <= onder) & zinvol).values, ((verkoop >= boven) & zinvol).values


def signalen_dagmarkt(df, marge, vertraging=1):
    """Ontladen als de laatst bekende overschotprijs boven de dagmarktprijs van dit uur plus de marge lag, laden als
    de laatst bekende tekortprijs eronder lag. De dagmarktprijs is de dag ervoor al bekend."""
    verkoop, koop = df.overschot.shift(vertraging), df.tekort.shift(vertraging)
    return (koop <= df.dagmarkt - marge).values, (verkoop >= df.dagmarkt + marge).values


def simuleer(koop, verkoop, laad, ontlaad, dagen, max_cycli=1.0, eff=EFF):
    """Loopt de kwartieren af. Per kwartier hooguit een stap laden of ontladen; per dag hooguit `max_cycli` volledige
    ontladingen (None = onbeperkt). Geeft de kasstroom per kwartier (EUR per MW) en de ontladen stappen."""
    n = len(koop)
    kas, stappen = np.zeros(n), np.zeros(n, dtype=int)
    limiet = None if max_cycli is None else int(round(max_cycli * NIVEAUS))
    soc, vandaag, gebruikt = 0, None, 0
    for t in range(n):
        if dagen[t] != vandaag:
            vandaag, gebruikt = dagen[t], 0
        if ontlaad[t] and soc > 0 and (limiet is None or gebruikt < limiet) and verkoop[t] == verkoop[t]:
            soc -= 1; gebruikt += 1; stappen[t] = 1
            kas[t] = STAP * eff * verkoop[t]
        elif laad[t] and soc < NIVEAUS and koop[t] == koop[t]:
            soc += 1
            kas[t] = -STAP * koop[t]
    return kas, stappen


def perfect_dag(koop, verkoop, max_cycli=1.0, eff=EFF):
    """Bovengrens voor een dag met kennis vooraf, zelfde batterij en zelfde cycluslimiet (dynamisch programma)."""
    limiet = int(round(max_cycli * NIVEAUS))
    waarde = np.full((NIVEAUS + 1, limiet + 1), -np.inf)
    waarde[0, 0] = 0.0
    for k, v in zip(koop, verkoop):
        nieuw = waarde.copy()
        if k == k:
            nieuw[1:, :] = np.maximum(nieuw[1:, :], waarde[:-1, :] - STAP * k)
        if v == v:
            nieuw[:-1, 1:] = np.maximum(nieuw[:-1, 1:], waarde[1:, :-1] + STAP * eff * v)
        waarde = nieuw
    return float(waarde.max())


def dagmarktschema(df, eff=EFF):
    """Dagmarktplan per kwartier: -1 laden, +1 ontladen, 0 niets. Het plan komt uit de prijzen van gisteren en vervalt
    op dagen waarop het tegen de dagmarktprijzen van vandaag verlies geeft (de dag ervoor al bekend)."""
    from . import herijk
    da = herijk.dagen_dagmarkt()
    plan = {}
    for d in sorted(da):
        gisteren = d - pd.Timedelta(days=1).to_pytimedelta()
        if gisteren in da:
            paar = herijk.beste_blok(*da[gisteren], herijk.H, eff)[1]
            if paar and herijk.winst(*da[d], paar, herijk.H, eff) > 0:
                plan[d] = paar
    schema = np.zeros(len(df), dtype=int)
    uren = df.index.hour
    for t, d in enumerate(df.index.date):
        paar = plan.get(d)
        if paar:
            if paar[0] <= uren[t] < paar[0] + herijk.H:
                schema[t] = -1
            elif paar[1] <= uren[t] < paar[1] + herijk.H:
                schema[t] = 1
    return schema


def simuleer_gecombineerd(df, schema, laad, ontlaad, max_cycli=2.0, eff=EFF):
    """Dagmarktplan met bijsturen: de batterij volgt het dagmarktplan, tenzij het onbalanssignaal iets anders zegt.
    De dagmarkt rekent het plan af; elke afwijking van het plan rekent af tegen de onbalansprijs van dat kwartier
    (overschotprijs bij meer leveren, tekortprijs bij minder). Geeft kasstroom dagmarkt, kasstroom onbalans en stappen."""
    koop, verkoop, dagmarkt, dagen = df.tekort.values, df.overschot.values, df.dagmarkt.values, df.index.date
    n = len(df)
    kas_da, kas_ob, stappen = np.zeros(n), np.zeros(n), np.zeros(n, dtype=int)
    limiet = int(round(max_cycli * NIVEAUS))
    rest = np.zeros(n, dtype=int)                      # geplande ontlaadstappen die vandaag nog komen (dit kwartier meegeteld)
    for t in range(n - 1, -1, -1):
        volgende = rest[t + 1] if t + 1 < n and dagen[t + 1] == dagen[t] else 0
        rest[t] = volgende + (1 if schema[t] == 1 else 0)
    soc, vandaag, gebruikt = 0, None, 0
    for t in range(n):
        if dagen[t] != vandaag:
            vandaag, gebruikt = dagen[t], 0
        plan = schema[t] if dagmarkt[t] == dagmarkt[t] else 0
        gepland = -STAP if plan == -1 else (STAP * eff if plan == 1 else 0.0)        # MWh aan het net volgens plan
        kas_da[t] = gepland * dagmarkt[t] if plan else 0.0
        geldig = koop[t] == koop[t] and verkoop[t] == verkoop[t]
        ruimte = gebruikt + rest[t] - (1 if plan == 1 else 0) < limiet                  # cyclus over naast het plan
        if geldig and ontlaad[t] and soc > 0 and gebruikt < limiet and (plan == 1 or ruimte):
            actie = 1
        elif geldig and laad[t] and soc < NIVEAUS:
            actie = -1
        elif plan == 1 and soc > 0 and gebruikt < limiet:
            actie = 1
        elif plan == -1 and soc < NIVEAUS:
            actie = -1
        else:
            actie = 0
        if actie == 1:
            soc -= 1; gebruikt += 1; stappen[t] = 1
        elif actie == -1:
            soc += 1
        werkelijk = -STAP if actie == -1 else (STAP * eff if actie == 1 else 0.0)
        afwijking = werkelijk - gepland
        if afwijking and geldig:
            kas_ob[t] = afwijking * (verkoop[t] if afwijking > 0 else koop[t])
        elif afwijking:                                 # geen onbalansprijs bekend: reken af tegen de dagmarktprijs
            kas_ob[t] = afwijking * (dagmarkt[t] if dagmarkt[t] == dagmarkt[t] else 0.0)
    return kas_da, kas_ob, stappen


def per_dag(df, kas, stappen):
    d = pd.DataFrame({"kas": kas, "stappen": stappen, "geldig": df.tekort.notna().values & df.overschot.notna().values}, index=df.index)
    g = d.groupby(d.index.date).agg(kas=("kas", "sum"), stappen=("stappen", "sum"), geldig=("geldig", "sum"))
    return g[g.geldig >= 90]                           # alleen dagen met vrijwel alle kwartieren


def jaarcijfers(dag, jaar):
    x = dag[[d.year == jaar for d in dag.index]]
    if not len(x):
        return None
    return {"omzet_per_mw": float(x.kas.mean() * 365), "cycli_per_dag": float(x.stappen.mean() / NIVEAUS), "dagen": int(len(x)),
            "aandeel_dagen_met_verlies": float((x.kas < 0).mean())}


def voorwaarts(uitkomst, jaren, standaard):
    """Kies voor elk jaar de variant die in het jaar ervoor het meeste opleverde; het eerste jaar krijgt de standaard."""
    keuze = {}
    for j in jaren:
        vorig = {v: r[j - 1]["omzet_per_mw"] for v, r in uitkomst.items() if r.get(j - 1)}
        keuze[j] = max(vorig, key=vorig.get) if vorig else standaard
    return keuze


def main(data=OUT, uit=OUT, rapport="reports/onbalansregel.json"):
    from . import herijk
    df = lees(data)
    dagen = df.index.date
    koop, verkoop = df.tekort.values, df.overschot.values
    jaren = sorted({d.year for d in dagen})
    rijen, dagreeksen = [], {}

    def draai(naam, variant, laad, ontlaad, max_cycli, vertraging):
        kas, stappen = simuleer(koop, verkoop, laad, ontlaad, dagen, max_cycli)
        dag = per_dag(df, kas, stappen)
        dagreeksen[(naam, variant, max_cycli, vertraging)] = dag
        return {j: jaarcijfers(dag, j) for j in jaren}

    # 1. Kwantielregel: drie vaste drempelparen, cycluslimiet 1 en 2 per dag en onbeperkt, informatie 1 en 2 kwartieren oud
    kwantiel = {}
    for laag, hoog in KWANTIELEN:
        for vertraging in (1, 2):
            laad, ontlaad = signalen_kwantiel(df, laag, hoog, vertraging)
            for max_cycli in (1.0, 2.0, None):
                kwantiel[(laag, hoog, max_cycli, vertraging)] = draai("Kwantielregel", f"{int(laag * 100)}/{int(hoog * 100)}", laad, ontlaad, max_cycli, vertraging)
    # 2. Dagmarktregel: marge boven en onder de dagmarktprijs
    dagmarkt = {}
    for marge in MARGES:
        for vertraging in (1, 2):
            laad, ontlaad = signalen_dagmarkt(df, marge, vertraging)
            for max_cycli in (1.0, 2.0, None):
                dagmarkt[(marge, max_cycli, vertraging)] = draai("Dagmarktregel", f"marge {marge}", laad, ontlaad, max_cycli, vertraging)

    # 2b. Dagmarktplan met bijsturen op onbalans: hooguit twee cycli per dag, informatie 0, 1 of 2 kwartieren oud
    #     (0 = de prijs van het lopende kwartier is bekend: een bovengrens voor reageren binnen het kwartier)
    schema = dagmarktschema(df)
    geen = np.zeros(len(df), dtype=bool)
    kd, ko, st = simuleer_gecombineerd(df, schema, geen, geen)
    controle = {j: jaarcijfers(per_dag(df, kd + ko, st), j) for j in jaren}
    gecombineerd, delen_gecombineerd = {}, {}
    for laag, hoog in KWANTIELEN:
        for vertraging in (0, 1, 2):
            laad, ontlaad = signalen_kwantiel(df, laag, hoog, vertraging)
            kd, ko, st = simuleer_gecombineerd(df, schema, laad, ontlaad, 2.0)
            dag = per_dag(df, kd + ko, st)
            dagreeksen[("Dagmarkt met bijsturen", f"{int(laag * 100)}/{int(hoog * 100)}", 2.0, vertraging)] = dag
            gecombineerd[(laag, hoog, 2.0, vertraging)] = {j: jaarcijfers(dag, j) for j in jaren}
            ob_dag = per_dag(df, ko, st)
            delen_gecombineerd[(laag, hoog, vertraging)] = {j: float(ob_dag.kas[[d.year == j for d in ob_dag.index]].mean() * 365) for j in jaren}

    # 3. Bovengrens met kennis vooraf, zelfde cycluslimiet
    perfect = {}
    for max_cycli in (1.0, 2.0):
        waarden = {}
        for d, g in df.groupby(dagen):
            if g.tekort.notna().sum() >= 90:
                waarden[d] = perfect_dag(g.tekort.values, g.overschot.values, max_cycli)
        s = pd.Series(waarden)
        perfect[max_cycli] = {j: float(s[[d.year == j for d in s.index]].mean() * 365) for j in jaren}

    # 4. Dagmarkt als maatstaf, en per dag vooraf kiezen tussen dagmarkt en de regel (zeven dagen tot en met eergisteren)
    rda = herijk.reeksen(herijk.dagen_dagmarkt())
    maatstaf = {j: herijk.per_jaar(rda["skip"], j)[0] for j in jaren}

    def regels(naam, uitkomsten, sleutel_variant, standaard):
        for max_cycli in (1.0, 2.0, None):
            for vertraging in (1, 2):
                deel = {k[0] if naam == "Dagmarktregel" else (k[0], k[1]): r for k, r in uitkomsten.items()
                        if k[-2] == max_cycli and k[-1] == vertraging}
                keuze = voorwaarts(deel, jaren, standaard)
                for variant, r in deel.items():
                    for j in jaren:
                        if r.get(j):
                            rijen.append({"regel": naam, "variant": sleutel_variant(variant), "max_cycli_per_dag": max_cycli or 0,
                                          "vertraging_kwartieren": vertraging, "jaar": j, **r[j],
                                          "vooraf_gekozen": bool(keuze[j] == variant),
                                          "aandeel_van_perfect": (r[j]["omzet_per_mw"] / perfect[max_cycli][j]) if max_cycli in perfect else None,
                                          "dagmarkt_per_mw": maatstaf[j]})

    regels("Kwantielregel", kwantiel, lambda v: f"{int(v[0] * 100)}/{int(v[1] * 100)}", (0.25, 0.75))
    for vertraging in (0, 1, 2):
        deel = {(k[0], k[1]): r for k, r in gecombineerd.items() if k[3] == vertraging}
        keuze = voorwaarts(deel, jaren, (0.25, 0.75))
        for variant, r in deel.items():
            for j in jaren:
                if r.get(j):
                    rijen.append({"regel": "Dagmarkt met bijsturen", "variant": f"{int(variant[0] * 100)}/{int(variant[1] * 100)}",
                                  "max_cycli_per_dag": 2.0, "vertraging_kwartieren": vertraging, "jaar": j, **r[j],
                                  "vooraf_gekozen": bool(keuze[j] == variant), "aandeel_van_perfect": r[j]["omzet_per_mw"] / perfect[2.0][j],
                                  "dagmarkt_per_mw": maatstaf[j], "waarvan_onbalans_per_mw": delen_gecombineerd[(variant[0], variant[1], vertraging)][j]})
    regels("Dagmarktregel", dagmarkt, lambda v: f"marge {v}", 30)
    tabel = pd.DataFrame(rijen)
    os.makedirs(uit, exist_ok=True)
    tabel.to_csv(os.path.join(uit, "fact_onbalans_regel.csv"), index=False)

    # 5. Samenvatting: per jaar de vooraf gekozen variant (cycluslimiet 1, informatie 1 kwartier oud), ook gestapeld met de dagmarkt
    kern = tabel[(tabel.max_cycli_per_dag == 1) & (tabel.vertraging_kwartieren == 1) & tabel.vooraf_gekozen]
    samenvatting = {"dagmarkt": maatstaf, "perfect_kwartier_1_cyclus": perfect[1.0], "perfect_kwartier_2_cycli": perfect[2.0]}
    for naam in ("Kwantielregel", "Dagmarktregel"):
        k = kern[kern.regel == naam].set_index("jaar")
        samenvatting[naam] = {int(j): {"variant": r.variant, "omzet_per_mw": float(r.omzet_per_mw), "cycli_per_dag": float(r.cycli_per_dag)} for j, r in k.iterrows()}
        delen = []
        for j, r in k.iterrows():
            d = dagreeksen[(naam, r.variant, 1.0, 1)].kas
            delen.append(d[[x.year == j for x in d.index]])
        regelreeks = pd.concat(delen).sort_index()
        gestapeld, kies = herijk.vooraf(rda["skip"], regelreeks)
        samenvatting[naam + ", vooraf gekozen tegenover dagmarkt"] = {
            int(j): {"omzet_per_mw": herijk.per_jaar(gestapeld, j)[0], "aandeel_dagen_regel": float(kies[[x.year == j for x in kies.index]].mean()),
                     "irr": {c: herijk.irr(herijk.per_jaar(gestapeld, j)[0], c) for c in CAPEX}} for j in jaren if herijk.per_jaar(gestapeld, j)[0] is not None}
        for j in samenvatting[naam]:
            samenvatting[naam][j]["irr"] = {c: herijk.irr(samenvatting[naam][j]["omzet_per_mw"], c) for c in CAPEX}
    from . import finance
    samenvatting["controle_dagmarktplan_zonder_signaal"] = {j: v["omzet_per_mw"] for j, v in controle.items() if v}
    for vertraging in (0, 1, 2):
        k = tabel[(tabel.regel == "Dagmarkt met bijsturen") & (tabel.vertraging_kwartieren == vertraging) & tabel.vooraf_gekozen].set_index("jaar")
        blok = {}
        for j, r in k.iterrows():
            capex = {c: c * herijk.H * herijk.MW for c in CAPEX}
            blok[int(j)] = {"variant": r.variant, "omzet_per_mw": float(r.omzet_per_mw), "waarvan_onbalans_per_mw": float(r.waarvan_onbalans_per_mw),
                            "cycli_per_dag": float(r.cycli_per_dag), "irr": {c: herijk.irr(r.omzet_per_mw, c) for c in CAPEX},
                            "irr_bij_3pct_degradatie": {c: finance.irr_safe(finance.project_cashflows(capex[c], r.omzet_per_mw * herijk.MW, capex[c] * herijk.OPEX_SH, herijk.LIFE, 0.03)) for c in CAPEX}}
        samenvatting[f"Dagmarkt met bijsturen, vertraging {vertraging}"] = blok
    os.makedirs(os.path.dirname(rapport) or ".", exist_ok=True)
    json.dump(samenvatting, open(rapport, "w"), indent=1, default=float)

    toon = tabel[(tabel.vertraging_kwartieren == 1)].pivot_table(index=["regel", "variant", "max_cycli_per_dag"], columns="jaar", values="omzet_per_mw")
    print((toon / 1000).round(1).to_string())
    print("\ndagmarkt:", {j: round(v / 1000, 1) for j, v in maatstaf.items()})
    print("perfect, 1 cyclus:", {j: round(v / 1000, 1) for j, v in perfect[1.0].items()}, "| 2 cycli:", {j: round(v / 1000, 1) for j, v in perfect[2.0].items()})
    for naam in ("Kwantielregel", "Dagmarktregel"):
        print(naam, "vooraf gekozen:", {j: (v["variant"], round(v["omzet_per_mw"] / 1000, 1), round(v["cycli_per_dag"], 2)) for j, v in samenvatting[naam].items()})
        print("  gestapeld met dagmarkt:", {j: (round(v["omzet_per_mw"] / 1000, 1), round(v["aandeel_dagen_regel"], 2)) for j, v in samenvatting[naam + ", vooraf gekozen tegenover dagmarkt"].items()})
    print("controle dagmarktplan zonder signaal:", {j: round(v / 1000, 1) for j, v in samenvatting["controle_dagmarktplan_zonder_signaal"].items()})
    for vertraging in (0, 1, 2):
        b = samenvatting[f"Dagmarkt met bijsturen, vertraging {vertraging}"]
        print(f"Dagmarkt met bijsturen, vertraging {vertraging}:", {j: (v["variant"], round(v["omzet_per_mw"] / 1000, 1), "waarvan onbalans", round(v["waarvan_onbalans_per_mw"] / 1000, 1), "cycli", round(v["cycli_per_dag"], 2),
              "IRR", {c // 1000: (None if v["irr"][c] is None else round(v["irr"][c] * 100, 1)) for c in CAPEX}) for j, v in b.items()})
    return samenvatting


if __name__ == "__main__":
    main(*sys.argv[1:3])
