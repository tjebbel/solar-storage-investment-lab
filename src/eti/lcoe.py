"""Kostprijs van zon per land, twee methoden. Gebruikt door mck_kostencurve (t13) en verdieping (t92).

Eigen model:  LCOE = (CAPEX x CRF(WACC, 25 jaar) + OPEX) / opbrengst. Dezelfde installatie in elk land (PBL: 449 EUR/kW,
              15,7 EUR/kW/jaar); opbrengst = mediaan 2023-2025 van opwek / gemiddeld vermogen (Ember); WACC per land uit IRENA
              (data/extern/irena_wacc_2024.csv), waar die ontbreekt de mediaan van de overige landen. Ondergrens.
IRENA:        gewogen gemiddelde van projecten opgeleverd in 2024 voor zeven landen (data/extern/irena_solar_country_2024.csv),
              anders het Europese gemiddelde (data/extern/irena_solar_lcoe_2024.csv). USD naar EUR met 1,0824 (gemiddelde 2024).
"""
import numpy as np
import pandas as pd

EMBER = "data/ember_global/release_generation_yearly_global.csv"
IRENA_LAND = {"FRA": "France", "DEU": "Germany", "GRC": "Greece", "ITA": "Italy", "NLD": "Netherlands", "POL": "Poland", "ESP": "Spain"}
CAPEX, OPEX, LOOPTIJD, USD_PER_EUR = 449.0, 15.7, 25, 1.0824


def crf(w, n=LOOPTIJD):
    return w / (1 - (1 + w) ** -n)


def zon_ember(ember=EMBER):
    """Opwek (TWh) en vermogen (GW) van zon per land en jaar."""
    e = pd.read_csv(ember, low_memory=False)
    e = e[(e["Electricity source"] == "Solar") & (e["Area type"] == "Country or economy")]
    return tuple(e.pivot(index="ISO 3 code", columns="Year", values=k) for k in ("Generation (TWh)", "Capacity (GW)"))


def per_land(codes, ember=EMBER):
    g, c = zon_ember(ember)
    y = pd.DataFrame({j: g[j] / ((c[j] + c[j - 1]) / 2) * 1000 for j in (2023, 2024, 2025)})
    t = pd.DataFrame({"Landcode": list(codes)})
    t["Opbrengst kWh per kW"] = t["Landcode"].map(y.median(axis=1))
    spreiding = t["Landcode"].map((y.max(axis=1) - y.min(axis=1)) / y.median(axis=1))
    t["Opbrengst betrouwbaar"] = (t["Landcode"].map(c[2025]) >= 1) & (spreiding <= 0.25)
    w = pd.read_csv("data/extern/irena_wacc_2024.csv")
    w = w[w["Technology"] == "Solar PV"].set_index("ISO3")["WACC %"]
    t["WACC %"] = t["Landcode"].map(w)
    t["WACC-bron"] = np.where(t["WACC %"].notna(), "IRENA 2024, land", "mediaan van de overige landen")
    t["WACC %"] = t["WACC %"].fillna(t["WACC %"].median())
    t["LCOE eigen model"] = (CAPEX * crf(t["WACC %"] / 100) + OPEX) / t["Opbrengst kWh per kW"] * 1000
    i = pd.read_csv("data/extern/irena_solar_country_2024.csv")
    i = i[i["Year"] == 2024].set_index("Country")["LCOE USD/MWh"]
    europa = pd.read_csv("data/extern/irena_solar_lcoe_2024.csv").set_index("Region or country").at["Europe", "Average 2024"]
    t["LCOE IRENA"] = t["Landcode"].map(IRENA_LAND).map(i).fillna(europa) / USD_PER_EUR
    t["IRENA-basis"] = np.where(t["Landcode"].isin(IRENA_LAND), "IRENA 2024, land", "IRENA 2024, Europees gemiddelde")
    return t.set_index("Landcode")
