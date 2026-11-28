"""Aanvulling met open Ember-data: landen buiten de 37 biedzones, opwek per bron wereldwijd, en wind naast zon.

  t104_europe_price_countries.csv   uurprijzen per land (Ember, uit ENTSO-E): prijs, negatieve uren, dagspreiding en middagindex
                                    per jaar, met het aandeel zon en wind uit de jaardata. Bevat ook Ierland, het Verenigd
                                    Koninkrijk, Montenegro, Noord-Macedonie, Albanie, Kosovo en Moldavie.
  t105_world_generation.csv         opwek, aandeel en vermogen per land, bron en jaar (2015-2025), alle werelddelen.
  t106_wind_vs_solar.csv            capture rate van zon en wind per jaar: mediaan van de 37 zones en Nederland (uit t2).

De bronbestanden staan in data/raw/ember (niet op GitHub, CC BY 4.0, ember-energy.org). Ontbreken ze, dan blijven de
bestaande tabellen staan.  Gebruik:  PYTHONPATH=src python3 -m eti.ember_extra
"""
from pathlib import Path
import zipfile
import pandas as pd

RAW, D = Path("data/raw/ember"), Path("tableau/data")
IN_ZONES = {"AUT", "BEL", "BGR", "CHE", "CZE", "DEU", "DNK", "EST", "ESP", "FIN", "FRA", "GRC", "HRV", "HUN", "ITA", "LTU", "LVA",
            "NLD", "NOR", "POL", "PRT", "ROU", "SRB", "SWE", "SVN", "SVK"}
BRONNEN = ["Solar", "Wind", "Hydro", "Nuclear", "Gas", "Coal", "Bioenergy", "Other fossil", "Other renewables"]


def prijzen():
    z = zipfile.ZipFile(RAW / "european_wholesale_electricity_price_data_hourly.zip")
    rijen = []
    for naam in z.namelist():
        if naam == "all_countries.csv":
            continue
        d = pd.read_csv(z.open(naam))
        t = pd.to_datetime(d["Datetime (Local)"]); d = d.assign(Year=t.dt.year, Hour=t.dt.hour, Day=t.dt.date)
        d = d[d.Year >= 2019].rename(columns={"Price (EUR/MWhe)": "P"})
        for jaar, g in d.groupby("Year"):
            dag = g.groupby("Day")["P"]; gem = g["P"].mean()
            mid, avond = g[g.Hour.between(11, 15)]["P"].mean(), g[g.Hour.between(18, 21)]["P"].mean()
            rijen.append({"Country": g["Country"].iloc[0], "ISO3": g["ISO3 Code"].iloc[0], "Year": jaar, "Hours": len(g),
                          "Partial year": len(g) < 8700, "Average price EUR/MWh": round(gem, 2),
                          "Negative hours": int((g["P"] < 0).sum()), "Negative hours %": round(100 * (g["P"] < 0).mean(), 2),
                          "Daily spread EUR/MWh": round((dag.max() - dag.min()).mean(), 2),
                          "Midday index 11-15h": round(mid / gem, 4) if gem else None,
                          "Evening to midday ratio": round(avond / mid, 3) if mid and mid > 0 else None})
    p = pd.DataFrame(rijen)
    j = pd.read_csv(RAW / "release_generation_yearly_global.csv", low_memory=False)
    j = j[j["Electricity source"].isin(["Solar", "Wind"])].pivot_table(index=["ISO 3 code", "Year"], columns="Electricity source",
                                                                       values="Share of generation (%)").reset_index()
    j.columns = ["ISO3", "Year", "Solar share %", "Wind share %"]
    p = p.merge(j, on=["ISO3", "Year"], how="left")
    p["Coverage"] = p["ISO3"].map(lambda c: "in the 37 zones" if c in IN_ZONES else "new country")
    return p.sort_values(["Country", "Year"])


def wereld():
    j = pd.read_csv(RAW / "release_generation_yearly_global.csv", low_memory=False)
    j = j[(j["Area type"] == "Country or economy") & (j.Year >= 2015) & j["Electricity source"].isin(BRONNEN + ["Total generation"])]
    j = j[["Area", "ISO 3 code", "Year", "Continent", "Ember region", "Electricity source", "Generation (TWh)", "Share of generation (%)",
           "Capacity (GW)", "Emissions intensity (gCO2e/kWh)"]]
    j = j.rename(columns={"Area": "Country", "ISO 3 code": "ISO3", "Electricity source": "Source", "Generation (TWh)": "Generation TWh",
                          "Share of generation (%)": "Share of generation %", "Capacity (GW)": "Capacity GW",
                          "Emissions intensity (gCO2e/kWh)": "Emissions intensity gCO2 per kWh"})
    for k in ("Country", "Continent", "Ember region"):
        j[k] = j[k].astype(str).str.replace(",", "", regex=False)       # geen komma's in waarden (Tableau)
    return j.dropna(subset=["Generation TWh"]).round(3)


def wind_zon():
    t = pd.read_csv(D / "t2_land_maand.csv")
    m = t.groupby("Jaar")[["Capture rate zon", "Capture rate wind"]].median()
    nl = t[t.Zone == "NL"].groupby("Jaar")[["Capture rate zon", "Capture rate wind"]].median()
    uit = []
    for naam, d in (("Median of 37 zones", m), ("Netherlands", nl)):
        for bron, kolom in (("Solar", "Capture rate zon"), ("Wind", "Capture rate wind")):
            uit.append(pd.DataFrame({"Year": d.index, "Area": naam, "Source": bron, "Capture rate": d[kolom].round(3).values}))
    return pd.concat(uit, ignore_index=True)


def main():
    uit = {"t106_wind_vs_solar": wind_zon()}
    if (RAW / "european_wholesale_electricity_price_data_hourly.zip").exists() and (RAW / "release_generation_yearly_global.csv").exists():
        uit["t104_europe_price_countries"] = prijzen(); uit["t105_world_generation"] = wereld()
    else:
        print("data/raw/ember ontbreekt: t104 en t105 blijven zoals ze zijn")
    for naam, d in uit.items():
        for map_ in (D, Path("tableau/data_en")):                     # kolommen zijn al Engels
            d.to_csv(map_ / f"{naam}.csv", index=False)
        print(f"{naam}: {len(d)} rijen")


if __name__ == "__main__":
    main()
