"""Dashboard 6 (winstpool langs de waardeketen) en dashboard 17 (PPA of merchant), alleen Engels.

Bronnen (handmatig verzameld uit openbare jaarcijfers en persberichten, met URL per rij):
  data/extern/waardeketen_2025.csv   omzet en nettowinst 2025 van tien fabrikanten in de zonneketen
  data/extern/ppa_prijzen.csv        LevelTen P25 (zon, Europa en per land) en Pexapark EURO Composite (alle technieken)
  data/extern/ppa_kyos_2025_06.csv   KYOS (juni 2025): zon-PPA-schatting per zone voor 2026-2035, equivalent van P25 (met 20% risicokorting)
Tabellen (tableau/data en tableau/data_en, Engelse kolommen):
  t60_value_chain        bedrijf, schakel, omzet (mld USD), nettomarge, brutomarge
  t61_ppa_prices         PPA-prijsreeksen, met index t.o.v. Q3 2024
  t62_ppa_vs_merchant    land: PPA-prijs (LevelTen P25 Q4 2025, of KYOS-schatting) tegen de capture-prijs zon 2025 uit ons eigen model (t1);
                         kolom Source zegt welke bron. KYOS ligt ongeveer 25% onder LevelTen waar beide bestaan: indicatief.
  t76_ppa_countries      land: PPA-prijs per land (LevelTen P25 waar beschikbaar, anders KYOS), voor de landenvergelijking
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
ZONES = {"Germany": ["DE-LU"], "Spain": ["ES"], "Italy": ["IT-North", "IT-Centre-North", "IT-South", "IT-Sicily"],
         "France": ["FR"], "Greece": ["GR"]}                                   # LevelTen P25 Q4 2025
ZONES_KYOS = {"Netherlands": ["NL"], "Belgium": ["BE"], "Portugal": ["PT"], "Hungary": ["HU"], "Poland": ["PL"],
              "Romania": ["RO"]}                                                # KYOS-schatting, indicatief
LEVELTEN = "LevelTen P25 offer, Q4 2025"
KYOS = "KYOS estimate, P25 equivalent for 2026-2035 (June 2025 report)"


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


def kyos():
    k = pd.read_csv(EXT / "ppa_kyos_2025_06.csv")
    return k.groupby("Country", sort=False)["Solar P25 equivalent EUR/MWh"].mean()


def ppa_tegen_merchant(jaar=2025):
    t1 = pd.read_csv(D / "t1_zonejaar.csv")
    t1 = t1[t1.Jaar == jaar]
    p = ppa(); p = p[(p.Index == "P25 country") & (p.Period == "Q4 2025")].set_index("Market")["Price EUR/MWh"]
    k = kyos()
    rij = []
    for bron, zonekaart, prijzen in ((LEVELTEN, ZONES, p), (KYOS, ZONES_KYOS, k)):
        for land, zones in zonekaart.items():
            z = t1[t1.Zone.isin(zones)]
            if z.empty or land not in prijzen:
                continue
            capture = (z["Gemiddelde prijs"] * z["Capture rate zon"]).mean()
            rij.append({"Country": land, "Year": jaar, "PPA P25 Q4 2025 EUR/MWh": prijzen[land], "Solar capture price EUR/MWh": capture,
                        "Average price EUR/MWh": z["Gemiddelde prijs"].mean(), "Solar capture rate": z["Capture rate zon"].mean(),
                        "PPA minus capture price": prijzen[land] - capture,
                        "Reading": "PPA pays more than the market" if prijzen[land] > capture else "market paid more than the PPA",
                        "Source": bron})
    return pd.DataFrame(rij)


def ppa_landen():
    """Prijs per land: LevelTen waar beschikbaar, anders de KYOS-schatting (zones gemiddeld)."""
    p = ppa(); p = p[(p.Index == "P25 country") & (p.Period == "Q4 2025")].set_index("Market")["Price EUR/MWh"]
    k = pd.read_csv(EXT / "ppa_kyos_2025_06.csv")
    rij = [{"Market": m, "Price EUR/MWh": v, "Source": LEVELTEN, "Note": ""} for m, v in p.items()]
    for land, g in k.groupby("Country", sort=False):
        if land in p.index:
            continue
        n = len(g)
        rij.append({"Market": land, "Price EUR/MWh": g["Solar P25 equivalent EUR/MWh"].mean(), "Source": KYOS,
                    "Note": f"simple average of {n} zones: {', '.join(g.Zone)}" if n > 1 else ""})
    return pd.DataFrame(rij).sort_values("Price EUR/MWh", ascending=False)


def main():
    uit = {"t60_value_chain": waardeketen(), "t61_ppa_prices": ppa(), "t62_ppa_vs_merchant": ppa_tegen_merchant(),
           "t76_ppa_countries": ppa_landen()}
    for t, d in uit.items():
        for u in UIT:
            d.to_csv(u / f"{t}.csv", index=False, float_format="%.6g")
        print(f"{t}: {len(d)} rijen")
    return uit


if __name__ == "__main__":
    main()
