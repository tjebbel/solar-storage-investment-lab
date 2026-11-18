"""Ember-bulkbestanden (data/ember_global/) -> compacte Power BI-tabellen.
Run: PYTHONPATH=src python3 -m eti.ember_global"""
import os, sys
import pandas as pd
SRC = sys.argv[1] if len(sys.argv) > 1 else "data/ember_global"
OUT = sys.argv[2] if len(sys.argv) > 2 else "powerbi/data"
EU = ["NLD","DEU","BEL","FRA","ESP","DNK","GBR","POL","ITA","PRT","AUT","SWE","NOR","FIN","IRL","GRC","HUN","CZE","ROU","CHE"]
KERN = EU + ["USA","CHN","IND","JPN","AUS","BRA","ZAF","KOR","CAN","MEX","TUR","VNM"]
def p(n): return os.path.join(SRC, n)
def w(df, n):
    os.makedirs(OUT, exist_ok=True); df.to_csv(os.path.join(OUT, n), index=False); print(f"  -> {n}: {len(df)} rijen")

# 1 dagprijzen Europa (alle landen) + maand
d = pd.read_csv(p("european_wholesale_electricity_price_data_daily.csv"), parse_dates=["Date"])
d.columns = ["land","iso3","datum","prijs"]; w(d, "fact_ember_prijs_dag.csv")
m = pd.read_csv(p("european_wholesale_electricity_price_data_monthly.csv")); m.columns = ["land","iso3","datum","prijs"]; w(m, "fact_ember_prijs_maand.csv")
# 2 opwek jaarlijks wereld (landen + regio's), kernbronnen
y = pd.read_csv(p("release_generation_yearly_global.csv"), low_memory=False)
bron = ["Solar","Wind","Coal","Gas","Nuclear","Hydro","Bioenergy","Other fossil","Other renewables","Clean","Fossil","Total generation","Demand","Net imports"]
y = y[y["Electricity source"].isin(bron)]
cols = ["Area","ISO 3 code","Year","Area type","Electricity source","Generation (TWh)","Share of generation (%)","Capacity (GW)","Emissions (MtCO2e)","CO2 intensity (gCO2/kWh)"]
y = y[[c for c in cols if c in y.columns]]; w(y, "fact_ember_opwek_jaar.csv")
# intensiteit apart (zit op Total-rijen of eigen bron)
yi = pd.read_csv(p("release_generation_yearly_global.csv"), low_memory=False)
if "Electricity source" in yi:
    ci = yi[yi["Electricity source"].str.contains("CO2 intensity", na=False)][["Area","ISO 3 code","Year","Electricity source"] + [c for c in yi.columns if "Value" in c or "Generation (TWh)" in c][:1]]
# 3 opwek maandelijks: kernlanden zon/wind/totaal
mo = pd.read_csv(p("release_generation_monthly_global.csv"), low_memory=False, usecols=["Area","ISO 3 code","Date","Electricity source","Generation (TWh)","Share of generation (%)"])
mo = mo[mo["ISO 3 code"].isin(KERN) & mo["Electricity source"].isin(["Solar","Wind","Clean","Fossil","Total generation","Coal","Gas"])]
w(mo, "fact_ember_opwek_maand.csv")
# 4 capaciteit zon/wind maandelijks
c = pd.read_csv(p("monthly_capacity_wind_solar_public_release_file.csv"))
c = c[c["Is aggregate area"] == 0][["Year","Month","ISO 3 Code","Area","Continent","Source","Installed Capacity","Capacity additions (month-on-month)"]]
w(c, "fact_ember_capaciteit_maand.csv")
# 5 EV
w(pd.read_csv(p("monthly_ev_fleet_impact.csv")), "fact_ember_ev_vloot.csv")
ev = pd.read_csv(p("monthly_ev_sales.csv"), low_memory=False)
ev = ev[ev["Data frequency"] == "Monthly"][["Area","ISO 3 code","Date","Drivetrain","Registrations","Share of registrations (%)"]]
w(ev, "fact_ember_ev_verkoop.csv")
# 6 elektrificatie (vraag per sector)
e = pd.read_csv(p("public-downloads_energy_outputs_electrification_datatool_public_release_file.csv"))
w(e, "fact_ember_elektrificatie.csv")
# 7 export zonnepanelen (China -> wereld) en cleantech
s = pd.read_csv(p("mart_solar_exports_full_release_monthly.csv"))
s = s[["Area","Date","Region","Commodity type","Amount (USD)","Commodity price","Capacity (MW)"]]; w(s, "fact_ember_zon_import.csv")
ct = pd.read_csv(p("clean_tech_exports_full_release_monthly.csv"))
w(ct[ct["Commodity category"] != "All technologies"] if (ct["Commodity category"] != "All technologies").any() else ct, "fact_ember_cleantech_export.csv")
# 8 subnationaal: China-provincies, VS-staten, India-staten (jaar)
for f, key, n in (("release_chn_subnational_generation_yearly.csv","Province","fact_ember_china_provincie.csv"),
                  ("release_us_subnational_generation_yearly.csv","State","fact_ember_vs_staat.csv")):
    t = pd.read_csv(p(f), low_memory=False)
    t = t[t["Electricity source"].isin(["Solar","Wind","Coal","Gas","Clean","Fossil","Total generation"])][["Area",key,"Year","Electricity source","Generation (TWh)","Share of generation (%)","Emissions (MtCO2e)"]]
    w(t, n)
ind = pd.read_csv(p("india_yearly_full_release_long_format.csv"))
w(ind[["State","State type","Year","Category","Subcategory","Variable","Unit","Value"]], "fact_ember_india_staat.csv")
# 9 doelen
try:
    t = pd.read_excel(p("targets_download.xlsx")); w(t, "fact_ember_doelen.csv")
except Exception as ex: print("  doelen overgeslagen:", ex)
