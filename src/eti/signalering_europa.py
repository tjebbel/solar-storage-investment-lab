"""Uitbreiding van het tweede dashboard 'Signalering Nederland': dezelfde rekenregels voor alle 37 zones en alle jaren.

Rekenregels (gelijk aan powerbi/maten_analyse.dax en de Tableau-velden in de bouwgids, stap 10):
  capture-prijs zon = gemiddelde prijs x capture rate zon
  marge zon         = capture-prijs zon - LCOE;  status: < 0 'Kosten niet gedekt', < 5 'Krap', anders 'Gedekt'
  prijs z-score     = (prijs - gemiddelde van de 12 maanden ervoor) / standaardafwijking (steekproef) van die 12 maanden
  prijs signaal     = |z| >= 3 'Schok', >= 2 'Let op', anders 'Gewoon'
Controle: voor Nederland 2026 moet dit exact powerbi/maten_verwacht.csv geven (66 waarden).

Schrijft naar tableau/data:
  t9_signalering_zones.csv   zone x maand: prijs, capture-prijs zon, z-score, signaal (heatmap: welke zones schokken wanneer)
  t10_dekking_nl.csv         Nederland, jaar x LCOE-scenario x status: aantal maanden (hoe vaak verdient zon zijn kostprijs terug);
                             drie scenario's: studiemodel 2025 en 2030 (PBL-referentieproject) en IRENA 2024 (gemeten projecten)
Gebruik:  PYTHONPATH=src python3 -m eti.signalering_europa
"""
import os

import numpy as np
import pandas as pd

T2 = "tableau/data/t2_land_maand.csv"
VERWACHT = "powerbi/maten_verwacht.csv"
UIT = "tableau/data"
LCOE = {"LCOE 2025 (67,39)": 67.39, "LCOE 2030 (50,54)": 50.54}     # Nederland, powerbi/data/fact_regio_jaar.csv


def status(marge):
    return np.select([marge.isna(), marge < 0, marge < 5], [None, "Kosten niet gedekt", "Krap"], "Gedekt")


def signaal(z):
    return np.select([z.isna(), z.abs() >= 3, z.abs() >= 2], [None, "Schok", "Let op"], "Gewoon")


def bereken(t2, lcoe=67.39):
    d = t2.copy()
    d["Maand"] = pd.to_datetime(d["Maand"])
    d = d.sort_values(["Zonenaam", "Maand"])
    d["Capture-prijs zon"] = d["Gemiddelde prijs"] * d["Capture rate zon"]
    d["Marge zon"] = d["Capture-prijs zon"] - lcoe
    d["Status zon"] = status(d["Marge zon"])
    p = d.groupby("Zonenaam")["Gemiddelde prijs"]
    gem = p.transform(lambda s: s.shift(1).rolling(12, min_periods=2).mean())
    sd = p.transform(lambda s: s.shift(1).rolling(12, min_periods=2).std(ddof=1))
    d["Prijs z-score"] = (d["Gemiddelde prijs"] - gem) / sd.replace(0, np.nan)
    d["Prijs signaal"] = signaal(d["Prijs z-score"])
    return d


def controle(d, verwacht=VERWACHT):
    """Vergelijk Nederland 2026 met de verwachte DAX-uitkomst; geeft (goed, totaal)."""
    if not os.path.exists(verwacht):
        return None
    v = pd.read_csv(verwacht)
    nl = d[(d["Zonenaam"] == "Nederland") & (d["Jaar"] == 2026)].set_index("Maandnummer")
    goed = totaal = 0
    for _, r in v.iterrows():
        x = nl.loc[r["maand"]]
        for kol in ["Gem prijs", "Capture-prijs zon", "Marge zon", "Prijs z-score"]:
            bron = "Gemiddelde prijs" if kol == "Gem prijs" else kol
            totaal += 1
            goed += abs(round(x[bron], 2) - r[kol]) <= 0.011
        for kol in ["Status zon", "Prijs signaal"]:
            totaal += 1
            goed += x[kol] == r[kol]
    return goed, totaal


def scenarios():
    """De twee waarden van het studiemodel plus de IRENA-kostprijs van 2024 (gemeten projecten), zelfde bron als dashboard 5."""
    from eti.lcoe import per_land
    irena = per_land(["NLD"]).at["NLD", "LCOE IRENA"]
    return {**LCOE, f"LCOE 2024 IRENA ({irena:.2f})".replace(".", ","): irena}


def dekking_nl(t2):
    rijen = []
    for naam, l in scenarios().items():
        d = bereken(t2[t2["Zonenaam"] == "Nederland"], l)
        for (jaar, st), n in d.groupby(["Jaar", "Status zon"]).size().items():
            rijen.append({"Jaar": jaar, "Scenario": naam, "Status zon": st, "Maanden": n})
    return pd.DataFrame(rijen).sort_values(["Scenario", "Jaar", "Status zon"])


def main(t2_pad=T2, uit=UIT):
    t2 = pd.read_csv(t2_pad)
    d = bereken(t2)
    c = controle(d)
    if c:
        print(f"Controle Nederland 2026 tegen maten_verwacht.csv: {c[0]} van {c[1]} waarden kloppen")
    kol = ["Zonenaam", "Zone", "Landcode", "Jaar", "Maandnummer", "Maand", "Gemiddelde prijs", "Capture-prijs zon",
           "Prijs z-score", "Prijs signaal"]
    zones = d[d["Jaar"] >= 2020][kol]
    zones.to_csv(os.path.join(uit, "t9_signalering_zones.csv"), index=False)
    dk = dekking_nl(t2)
    dk.to_csv(os.path.join(uit, "t10_dekking_nl.csv"), index=False)
    s = zones.dropna(subset=["Prijs signaal"])
    per_jaar = s.assign(schok=s["Prijs signaal"].ne("Gewoon")).groupby("Jaar")["schok"].mean().mul(100).round(1)
    print("Aandeel zone-maanden met 'Let op' of 'Schok' per jaar (%):", per_jaar.to_dict())
    print(dk.pivot_table(index="Jaar", columns=["Scenario", "Status zon"], values="Maanden", fill_value=0).to_string())
    print(f"Geschreven: {uit}/t9 ({len(zones)} rijen), t10 ({len(dk)} rijen)")


if __name__ == "__main__":
    main()
