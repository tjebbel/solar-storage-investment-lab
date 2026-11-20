"""Dashboard 6 (winstpool langs de waardeketen) en dashboard 17 (PPA of merchant), alleen Engels.

Bronnen (handmatig verzameld uit openbare jaarcijfers en persberichten, met URL per rij):
  data/extern/waardeketen_2025.csv   omzet en nettowinst 2025 van tien fabrikanten in de zonneketen
  data/extern/ppa_prijzen.csv        LevelTen P25 (zon, Europa en per land) en Pexapark EURO Composite (alle technieken)
Tabellen (tableau/data en tableau/data_en, Engelse kolommen):
  t60_value_chain        bedrijf, schakel, omzet (mld USD), nettomarge, brutomarge
  t61_ppa_prices         PPA-prijsreeksen, met index t.o.v. Q3 2024
  t62_ppa_vs_merchant    land: PPA-prijs P25 (Q4 2025) tegen de capture-prijs zon 2025 uit ons eigen model (t1)
Wisselkoers: 6,85 CNY per USD (gemiddelde 2025, zoals in de omrekeningen van pv magazine in de bronnen).
Gebruik:  PYTHONPATH=src python3 -m eti.ppa_waardeketen
"""
from pathlib import Path
import pandas as pd

EXT, D = Path("data/extern"), Path("tableau/data")
UIT = [Path("tableau/data"), Path("tableau/data_en")]
CNY_PER_USD = 6.85
VOLGORDE = {"Polysilicon (granular)": 1, "Polysilicon and cells": 1, "Wafers": 2, "Wafers and modules": 3, "Modules": 4,
            "Modules (thin film)": 5, "Inverters and storage": 6, "Microinverters and batteries": 6}
ZONES = {"Germany": ["DE-LU"], "Spain": ["ES"], "Italy": ["IT-North", "IT-Centre-North", "IT-South", "IT-Sicily"]}


def waardeketen():
    w = pd.read_csv(EXT / "waardeketen_2025.csv")
    f = w.Currency.map({"CNY": 1 / CNY_PER_USD, "USD": 1.0})
    w["Revenue USD bn"] = w["Revenue bn"] * f
    w["Net income USD bn"] = w["Net income bn"] * f
    w["Net margin %"] = 100 * w["Net income bn"] / w["Revenue bn"]
    w["Chain order"] = w.Segment.map(VOLGORDE)
    w["Group"] = w.Home.map(lambda h: "China" if h == "China" else "Outside China")
    w["Profitable"] = w["Net margin %"] > 0
    return w.sort_values(["Chain order", "Net margin %"])


def ppa():
    p = pd.read_csv(EXT / "ppa_prijzen.csv")
    basis = p[(p.Source == "LevelTen") & (p.Index == "P25 continental index") & (p.Period == "Q3 2024")]["Price EUR/MWh"].iloc[0]
    p["Index vs Q3 2024"] = (p["Price EUR/MWh"] / basis).where(p.Index == "P25 continental index")
    return p


def ppa_tegen_merchant(jaar=2025):
    t1 = pd.read_csv(D / "t1_zonejaar.csv")
    t1 = t1[t1.Jaar == jaar]
    p = ppa(); p = p[(p.Index == "P25 country") & (p.Period == "Q4 2025")].set_index("Market")["Price EUR/MWh"]
    rij = []
    for land, zones in ZONES.items():
        z = t1[t1.Zone.isin(zones)]
        if z.empty or land not in p:
            continue
        capture = (z["Gemiddelde prijs"] * z["Capture rate zon"]).mean()
        rij.append({"Country": land, "Year": jaar, "PPA P25 Q4 2025 EUR/MWh": p[land], "Solar capture price EUR/MWh": capture,
                    "Average price EUR/MWh": z["Gemiddelde prijs"].mean(), "Solar capture rate": z["Capture rate zon"].mean(),
                    "PPA minus capture price": p[land] - capture,
                    "Reading": "PPA pays more than the market" if p[land] > capture else "market paid more than the PPA"})
    return pd.DataFrame(rij)


def main():
    uit = {"t60_value_chain": waardeketen(), "t61_ppa_prices": ppa(), "t62_ppa_vs_merchant": ppa_tegen_merchant()}
    for t, d in uit.items():
        for u in UIT:
            d.to_csv(u / f"{t}.csv", index=False, float_format="%.6g")
        print(f"{t}: {len(d)} rijen")
    return uit


if __name__ == "__main__":
    main()
