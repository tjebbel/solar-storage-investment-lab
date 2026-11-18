"""Studie-indeling: Nederland / Europa (alle overige Europese landen) / VS / China / Rest van de wereld (buiten Europa).
Schrijft dim_land, dim_markt en fact_studieregio_jaar. Run: PYTHONPATH=src python3 -m eti.regio_indeling"""
import os, pandas as pd
SRC, OUT = "data/ember_global", "powerbi/data"

def studieregio(iso3, continent):
    if iso3 == "NLD": return "Nederland"
    if iso3 == "USA": return "VS"
    if iso3 == "CHN": return "China"
    if continent == "Europe": return "Europa"
    return "Rest van de wereld"

def main():
    y = pd.read_csv(os.path.join(SRC, "release_generation_yearly_global.csv"), low_memory=False)
    y = y[(y["Area type"] == "Country or economy") & y["ISO 3 code"].notna()]
    dim = y[["ISO 3 code", "Area", "Continent", "Ember region", "EU member", "OECD member", "G20 member"]].drop_duplicates("ISO 3 code")
    dim["studieregio"] = [studieregio(i, c) for i, c in zip(dim["ISO 3 code"], dim["Continent"])]
    dim.columns = ["iso3", "land", "continent", "ember_regio", "eu", "oecd", "g20", "studieregio"]
    dim.to_csv(os.path.join(OUT, "dim_land.csv"), index=False)
    print(dim.studieregio.value_counts().to_string())
    # Markten/biedzones uit de eigen pijplijn: alles Europees behalve onderstaande
    buiten = {"Australie": "Rest van de wereld", "Japan": "Rest van de wereld", "Californie (CAISO)": "VS", "Texas (ERCOT)": "VS"}
    markten = set()
    for f in ("fact_land_jaar.csv", "fact_wereld_markten.csv"):
        p = os.path.join(OUT, f)
        if os.path.exists(p): markten |= set(pd.read_csv(p).iloc[:, 0].unique())
    dm = pd.DataFrame(sorted(markten), columns=["markt"])
    dm["studieregio"] = [("Nederland" if m == "Nederland" else next((v for k, v in buiten.items() if m.startswith(k.split(" ")[0])), "Europa")) for m in dm.markt]
    dm.to_csv(os.path.join(OUT, "dim_markt.csv"), index=False)
    # Aggregaat per studieregio
    s = y[y["Electricity source"].isin(["Solar", "Wind", "Clean", "Fossil", "Total generation"])].merge(dim[["iso3", "studieregio"]], left_on="ISO 3 code", right_on="iso3")
    g = s.pivot_table(index=["studieregio", "Year"], columns="Electricity source", values="Generation (TWh)", aggfunc="sum").reset_index()
    for b in ["Solar", "Wind", "Clean", "Fossil"]:
        g[f"aandeel_{b.lower()}_pct"] = 100 * g[b] / g["Total generation"]
    e = s[s["Electricity source"] == "Total generation"].groupby(["studieregio", "Year"])["Emissions (MtCO2e)"].sum().reset_index()
    g = g.merge(e, on=["studieregio", "Year"]); g["intensiteit_g_kwh"] = 1000 * g["Emissions (MtCO2e)"] / g["Total generation"]
    g.to_csv(os.path.join(OUT, "fact_studieregio_jaar.csv"), index=False)
    print(g[g.Year == 2025][["studieregio", "Total generation", "aandeel_solar_pct", "aandeel_clean_pct", "intensiteit_g_kwh"]].round(1).to_string(index=False))

if __name__ == "__main__":
    main()
