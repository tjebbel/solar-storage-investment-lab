"""Dashboard 5, in de traditie van McKinsey: kostencurve voor CO2-reductie met extra zonnestroom per Europees land.

Per land, jaar 2025:
  capture-prijs zon  = gemiddelde prijs x capture rate (t1, gemiddeld over de zones van het land)       [EUR/MWh]
  LCOE               = Nederland 67,39 (noorden) of Spanje 51,09 (zuiden), fact_regio_jaar              [EUR/MWh]
  kosten per ton     = (LCOE - capture-prijs) / emissiefactor   (emissiefactor in t CO2 per MWh)
                       twee varianten: gemiddelde factor van de stroommix (Ember) en een marginale factor van 0,40 (gas)
  potentieel         = (zonopwek-doel 2030 - zonopwek 2025) x emissiefactor  [Mt CO2 per jaar], doel uit Ember
Negatieve kosten: extra zon is al winstgevend tegen de marktprijs. Een MACC is een momentopname; zie Kesicki en Ekins (2012).
Schrijft tableau/data/t13_kostencurve.csv (gesorteerd, met cumulatief potentieel voor de balkbreedte).
Gebruik:  PYTHONPATH=src python3 -m eti.mck_kostencurve
"""
import os

import numpy as np
import pandas as pd

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
    d = pd.read_csv(doelen)
    d = d[(d["TARGET_YEAR"] == 2030) & (d["FUEL_CATEGORY"] == "Solar") & (d["METRIC"] == "generation_twh")]
    doel = d.sort_values("COLLECTION_YEAR").groupby("COUNTRY_CODE")["VALUE"].last()
    l["LCOE"] = np.where(l["Landcode"].isin(ZUID), LCOE["zuid"], LCOE["noord"])
    l["LCOE-bron"] = np.where(l["Landcode"].isin(ZUID), "Spanje 2025", "Nederland 2025")
    l["Emissiefactor gemiddeld t/MWh"] = l["Landcode"].map(ci) / 1000
    l["Zon TWh 2025"] = l["Landcode"].map(zon)
    l["Zon doel TWh 2030"] = l["Landcode"].map(doel)
    l["Extra zon TWh"] = (l["Zon doel TWh 2030"] - l["Zon TWh 2025"]).clip(lower=0)
    l["Marge EUR/MWh"] = l["capture_prijs"] - l["LCOE"]
    l["Kosten per ton (gemiddelde factor)"] = (l["LCOE"] - l["capture_prijs"]) / l["Emissiefactor gemiddeld t/MWh"]
    l["Kosten per ton (marginale factor)"] = (l["LCOE"] - l["capture_prijs"]) / MARGINAAL
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
