"""Dashboard 5, in de traditie van McKinsey: kostencurve voor CO2-reductie met extra zonnestroom per Europees land.

Per land, jaar 2025:
  capture-prijs zon  = gemiddelde prijs x capture rate (t1, gemiddeld over de zones van het land)       [EUR/MWh]
  LCOE               = IRENA 2024: per land voor zeven landen, anders het Europese gemiddelde (eti.lcoe)   [EUR/MWh]
                       ernaast als bandbreedte: "LCOE eigen model" (ondergrens) en "LCOE oude aanname" (Nederland 67,39 in het
                       noorden, Spanje 51,09 in het zuiden; de waarde tot 24 november 2026)
  kosten per ton     = (LCOE - capture-prijs) / emissiefactor   (emissiefactor in t CO2 per MWh)
                       twee varianten: gemiddelde factor van de stroommix (Ember) en een marginale factor van 0,40 (gas)
  potentieel         = (zonopwek-doel 2030 - zonopwek 2025) x emissiefactor  [Mt CO2 per jaar], doel uit Ember. Heeft een land
                       alleen een vermogensdoel (GW; Duitsland 215, Bulgarije, Servie), dan doel x opbrengst 2025 (TWh per GW).
                       Kolom Doelbron zegt welke van de twee. Het zijn doelen, geen prognoses.
Negatieve kosten: extra zon is al winstgevend tegen de marktprijs. Een MACC is een momentopname; zie Kesicki en Ekins (2012).
Schrijft tableau/data/t13_kostencurve.csv (gesorteerd, met cumulatief potentieel voor de balkbreedte).
Gebruik:  PYTHONPATH=src python3 -m eti.mck_kostencurve
"""
import os

import numpy as np
import pandas as pd

from eti.lcoe import per_land

ZUID = {"ESP", "PRT", "ITA", "GRC", "BGR", "ROU", "HRV", "SRB", "SVN"}
LCOE = {"noord": 67.39, "zuid": 51.09}
MARGINAAL = 0.40


def bouw(t1="tableau/data/t1_zonejaar.csv", ember="data/ember_global/release_generation_yearly_global.csv",
         doelen="powerbi/data/fact_ember_doelen.csv", jaar=2025):
    t = pd.read_csv(t1)
    t = t[t["Jaar"] == jaar].assign(cp=lambda d: d["Gemiddelde prijs"] * d["Capture rate zon"])
    l = t.groupby("Landcode").agg(Land=("Zonenaam", "first"), capture_prijs=("cp", "mean")).reset_index()
    l["Land"] = l["Land"].str.replace(r" \(.*\)$", "", regex=True)
    e = pd.read_csv(ember, low_memory=False)
    e = e[(e["Year"] == jaar) & (e["Area type"] == "Country or economy")]
    ci = e[e["Electricity source"] == "Total generation"].set_index("ISO 3 code")["Emissions intensity (gCO2e/kWh)"]
    zon = e[e["Electricity source"] == "Solar"].set_index("ISO 3 code")["Generation (TWh)"]
    kap = e[e["Electricity source"] == "Solar"].set_index("ISO 3 code")["Capacity (GW)"]
    d = pd.read_csv(doelen)
    d = d[(d["TARGET_YEAR"] == 2030) & (d["FUEL_CATEGORY"] == "Solar")].sort_values("COLLECTION_YEAR")
    doel, doel_gw = (d[d["METRIC"] == m].groupby("COUNTRY_CODE")["VALUE"].last() for m in ("generation_twh", "capacity_total_gw"))
    k = per_land(l["Landcode"], ember)
    l["LCOE"] = l["Landcode"].map(k["LCOE IRENA"])
    l["LCOE-bron"] = l["Landcode"].map(k["IRENA-basis"])
    l["LCOE eigen model"] = l["Landcode"].map(k["LCOE eigen model"])
    l["LCOE oude aanname"] = np.where(l["Landcode"].isin(ZUID), LCOE["zuid"], LCOE["noord"])
    l["Emissiefactor gemiddeld t/MWh"] = l["Landcode"].map(ci) / 1000
    l["Zon TWh 2025"] = l["Landcode"].map(zon)
    l["Zon doel TWh 2030"] = l["Landcode"].map(doel)
    uit_gw = l["Landcode"].map(doel_gw) * l["Zon TWh 2025"] / l["Landcode"].map(kap)
    l["Doelbron"] = np.where(l["Zon doel TWh 2030"].notna(), "opwekdoel (Ember)",
                             np.where(uit_gw.notna(), "vermogensdoel x opbrengst 2025", "geen doel"))
    l["Zon doel TWh 2030"] = l["Zon doel TWh 2030"].fillna(uit_gw)
    l["Extra zon TWh"] = (l["Zon doel TWh 2030"] - l["Zon TWh 2025"]).clip(lower=0)
    l["Marge EUR/MWh"] = l["capture_prijs"] - l["LCOE"]
    l["Kosten per ton (gemiddelde factor)"] = (l["LCOE"] - l["capture_prijs"]) / l["Emissiefactor gemiddeld t/MWh"]
    l["Kosten per ton (marginale factor)"] = (l["LCOE"] - l["capture_prijs"]) / MARGINAAL
    for v in ("eigen model", "oude aanname"):
        l[f"Kosten per ton, {v} (marginale factor)"] = (l[f"LCOE {v}"] - l["capture_prijs"]) / MARGINAAL
    l["Potentieel Mt (gemiddelde factor)"] = l["Extra zon TWh"] * l["Emissiefactor gemiddeld t/MWh"]
    l["Potentieel Mt (marginale factor)"] = l["Extra zon TWh"] * MARGINAAL
    l = l.rename(columns={"capture_prijs": "Capture-prijs zon EUR/MWh"})
    l = l.dropna(subset=["Emissiefactor gemiddeld t/MWh"]).sort_values("Kosten per ton (marginale factor)")
    for v in ("gemiddelde", "marginale"):
        s = l.sort_values(f"Kosten per ton ({v} factor)")
        l.loc[s.index, f"Cumulatief Mt ({v} factor)"] = s[f"Potentieel Mt ({v} factor)"].fillna(0).cumsum()
    return l


def main():
    l = bouw()
    l.to_csv("tableau/data/t13_kostencurve.csv", index=False)
    k = ["Landcode", "Capture-prijs zon EUR/MWh", "LCOE", "Emissiefactor gemiddeld t/MWh", "Kosten per ton (gemiddelde factor)",
         "Kosten per ton (marginale factor)", "Extra zon TWh", "Potentieel Mt (marginale factor)"]
    tekst = l[k].round(2).to_string(index=False)
    neg = l[l["Kosten per ton (marginale factor)"] < 0]
    tekst += (f"\n\nLanden waar extra zon al geld oplevert (capture-prijs boven LCOE): {', '.join(neg['Landcode'])}"
              f"\nPotentieel 2025-2030 met doelen bekend: {l['Potentieel Mt (marginale factor)'].sum():.1f} Mt per jaar (marginaal), "
              f"{l['Potentieel Mt (gemiddelde factor)'].sum():.1f} Mt (gemiddeld); landen zonder doel: "
              f"{', '.join(l[l['Zon doel TWh 2030'].isna()]['Landcode'])}")
    print(tekst)
    open("resultaten/kostencurve.txt", "w", encoding="utf-8").write(tekst + "\n")


if __name__ == "__main__":
    main()
