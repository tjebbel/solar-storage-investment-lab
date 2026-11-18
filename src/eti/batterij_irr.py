"""Vervolgonderzoek 4: hoe gevoelig is het rendement van een batterij voor de bouwkosten per kWh en de cyclusgrens?

Dit is de vraag van een investeringscomite: bij welke prijs per kWh haalt het project 8%, en wat kost het als de
garantie het aantal cycli beperkt?

Model (1 MW, 2 uur, 2 MWh):
- Bouwkosten per kWh: 150 tot 400 euro (de volledige case rekent met 560 euro per kW = 280 euro per kWh, TenneT).
- Cycli per dag: 1, 1,5 of 2. Meer cycli leveren meer op de dagmarkt op, maar slijten de batterij sneller.
  Levensduur = het kleinste van 15 jaar en 6.000 volle cycli (een gangbare garantie voor LFP-cellen) gedeeld door de
  cycli per jaar. Slijtage per jaar 2%, onderhoud 2% van de bouwkosten (als eti.herijk).
- Opbrengst bij 1 cyclus: het eigen model 'dagmarkt met bijsturen' (eti.volledige_case, 87.194 euro per MW per jaar).
  De meeropbrengst van een tweede (halve) cyclus komt uit een optimalisatie met volledige kennis vooraf op de
  Nederlandse uurprijzen van 2025 en 2026: de verhouding opbrengst(c cycli)/opbrengst(1 cyclus). Die verhouding is een
  bovengrens voor de meeropbrengst.
- Netkosten: geen, of het tijdsafhankelijke transportrecht (57.000 euro per MW per jaar), zoals in de volledige case.
- Ter vergelijking de volledige stapeling uit de volledige case (Modo Energy), met 1 cyclus per dag en dezelfde
  kosten. Die opbrengst daalt als de vloot groeit; hier vast gehouden, dus een bovengrens.

Schrijft powerbi/data/fact_batterij_irr_grid_BI.csv en fact_batterij_breakeven_BI.csv.
Gebruik:  PYTHONPATH=src python3 -m eti.batterij_irr
"""
import os

import numpy as np
import pandas as pd

from . import finance

DATA = "powerbi/data"
EFF, OPEX, DEG, LEVEN_JAREN, CYCLI_GARANTIE = 0.88, 0.02, 0.02, 15, 6000
OMZET_1_CYCLUS = 87_193.5
CAPEX_KWH = (150, 200, 250, 280, 300, 350, 400)
CYCLI = (1.0, 1.5, 2.0)
NETKOSTEN = {"geen netkosten": 0.0, "tijdsafhankelijk transportrecht": 57_000.0}
DOEL = 0.08
# Volledige stapeling (dagmarkt, FCR, aFRR), bronwaarden uit eti.volledige_case (Modo Energy, 2 uur, 2026):
STAPELING = (("stapeling, vast transportrecht", 305_000.0, 150_000.0), ("stapeling, tijdsafhankelijk transportrecht", 242_500.0, 57_000.0),
             ("stapeling zonder capaciteitsvergoedingen, tijdsafhankelijk", 126_600.0, 57_000.0))


def dag_optimum(p, max_ontladen, cap=2, eff=EFF):
    """Beste dagwinst per MW met volledige kennis: laden en ontladen 1 MWh per uur, opslag 0..cap MWh, begin en eind leeg,
    hooguit max_ontladen MWh ontladen op een dag. Dynamisch programmeren over (uur, lading, al ontladen)."""
    max_o = int(round(max_ontladen))
    neg = -1e18
    w = np.full((cap + 1, max_o + 1), neg)
    w[0, 0] = 0.0
    for prijs in p:
        n = np.full_like(w, neg)
        for s in range(cap + 1):
            for o in range(max_o + 1):
                if w[s, o] == neg:
                    continue
                n[s, o] = max(n[s, o], w[s, o])                                     # niets doen
                if s < cap:
                    n[s + 1, o] = max(n[s + 1, o], w[s, o] - prijs)                 # 1 MWh laden
                if s > 0 and o < max_o:
                    n[s - 1, o + 1] = max(n[s - 1, o + 1], w[s, o] + prijs * eff)   # 1 MWh ontladen
        w = n
    return max(0.0, w[0].max())


def cyclus_verhouding(data=DATA, jaren=(2025, 2026)):
    u = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), usecols=["timestamp_utc", "jaar", "prijs_eur_mwh"])
    u = u[u.jaar.isin(jaren)].dropna()
    u["dag"] = u.timestamp_utc.str[:10]
    tot = {c: 0.0 for c in CYCLI}
    for _, d in u.groupby("dag"):
        p = d.prijs_eur_mwh.to_numpy()
        for c in CYCLI:
            tot[c] += dag_optimum(p, 2 * c)
    return {c: tot[c] / tot[1.0] for c in CYCLI}


def irr(capex_kwh, cycli, omzet, netkosten):
    capex = capex_kwh * 1000 * 2                                                      # 1 MW, 2 MWh
    leven = int(min(LEVEN_JAREN, CYCLI_GARANTIE / (365 * cycli)))
    kas = [-capex] + [omzet * (1 - DEG) ** (t - 1) - capex * OPEX - netkosten for t in range(1, leven + 1)]
    return finance.irr_safe(kas), leven


def breakeven(cycli, omzet, netkosten, doel=DOEL):
    """Hoogste bouwkosten per kWh waarbij het rendement nog het doel haalt (bisectie)."""
    laag, hoog = 10.0, 2000.0
    for _ in range(60):
        mid = (laag + hoog) / 2
        v, _ = irr(mid, cycli, omzet, netkosten)
        if v is not None and v >= doel:
            laag = mid
        else:
            hoog = mid
    return laag


def main(data=DATA, uit=DATA):
    verh = cyclus_verhouding(data)
    rijen, be = [], []
    for c in CYCLI:
        omzet = OMZET_1_CYCLUS * verh[c]
        for naam, net in NETKOSTEN.items():
            for k in CAPEX_KWH:
                v, leven = irr(k, c, omzet, net)
                rijen.append({"cycli_per_dag": c, "omzet_per_mw": omzet, "meeropbrengst_vs_1_cyclus": verh[c] - 1, "levensduur_jaar": leven,
                              "netkosten": naam, "capex_per_kwh": k, "irr": v})
            be.append({"cycli_per_dag": c, "netkosten": naam, "omzet_per_mw": omzet, "levensduur_jaar": int(min(LEVEN_JAREN, CYCLI_GARANTIE / (365 * c))),
                       "max_capex_per_kwh_voor_8pct": breakeven(c, omzet, net), "max_capex_per_kwh_voor_5pct": breakeven(c, omzet, net, 0.05)})
    for naam, omzet, net in STAPELING:                                              # volledige stapeling: weinig cycli, 1 per dag
        for k in CAPEX_KWH:
            v, leven = irr(k, 1.0, omzet, net)
            rijen.append({"cycli_per_dag": 1.0, "omzet_per_mw": omzet, "meeropbrengst_vs_1_cyclus": 0.0, "levensduur_jaar": leven,
                          "netkosten": naam, "capex_per_kwh": k, "irr": v})
        be.append({"cycli_per_dag": 1.0, "netkosten": naam, "omzet_per_mw": omzet, "levensduur_jaar": LEVEN_JAREN,
                   "max_capex_per_kwh_voor_8pct": breakeven(1.0, omzet, net), "max_capex_per_kwh_voor_5pct": breakeven(1.0, omzet, net, 0.05)})
    g, b = pd.DataFrame(rijen), pd.DataFrame(be)
    g.to_csv(os.path.join(uit, "fact_batterij_irr_grid_BI.csv"), index=False)
    b.to_csv(os.path.join(uit, "fact_batterij_breakeven_BI.csv"), index=False)
    pd.set_option("display.width", 200)
    print("Meeropbrengst per extra cyclus (volledige kennis, NL 2025-2026):", {c: round(v, 3) for c, v in verh.items()})
    print(g.pivot_table(index=["netkosten", "capex_per_kwh"], columns="cycli_per_dag", values="irr").round(3).to_string())
    print(b.round(0).to_string(index=False))
    return g, b


if __name__ == "__main__":
    main()
