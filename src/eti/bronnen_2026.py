"""Tabellen t112-t118 uit de uploads van 28 nov 2026. Geen komma's in koppen of waarden."""
import csv, os, glob, sys
import openpyxl, pandas as pd

U = "/mnt/user-data/uploads"
OUT = "/tmp/wk/out"
G = "/tmp/wk/gem"

def schoon(x):
    if x is None: return ""
    return " ".join(str(x).replace(",", "").replace("\xa0", " ").split())

def getal(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def schrijf(naam, kop, rijen):
    pad = os.path.join(OUT, naam)
    with open(pad, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([schoon(k) for k in kop])
        for r in rijen:
            w.writerow([schoon(v) if isinstance(v, str) else ("" if v is None else v) for v in r])
    # controle
    with open(pad, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == 0: n = line.count(",")
            elif line.count(",") != n:
                raise SystemExit(f"{naam}: regel {i+1} heeft afwijkend aantal kolommen")
    print(naam, len(rijen), "rijen")

# ---- t112 IEA World Energy Investment 2026 (wereld en regio's, mld USD) ----
regios = ["World", "Advanced economies", "China", "EMDE", "North America",
          "Central and South America", "Europe", "Africa", "Middle East", "Eurasia", "Asia Pacific"]
kpi = {"__total__": "Total investment", "of which: Clean energy": "Clean energy",
       "Fossil fuels": "Fossil fuels", "Power": "Power", "Renewables": "Renewables",
       "o/w solar": "Solar", "o/w wind": "Wind", "Battery storage": "Battery storage",
       "Nuclear": "Nuclear", "Oil": "Oil", "Gas": "Gas", "Coal": "Coal"}
wb = openpyxl.load_workbook(f"{U}/03a7f2c8-WorldEnergyInvestment2026_DataFile.xlsx", data_only=True, read_only=True)
rijen = []
for reg in regios:
    ws = wb[reg]
    rows = list(ws.iter_rows(values_only=True))
    jaren = None; kol0 = None
    for r in rows:
        if r and "2015" in [str(x) for x in r[:14]]:
            kol0 = [str(x) for x in r[:14]].index("2015")
            jaren = [str(x) for x in r[kol0:kol0 + 12]]
            break
    for r in rows:
        if not r or r[1] is None: continue
        label = str(r[1]).strip()
        if label.startswith("Total Billion USD"): label = "__total__"
        if label in kpi:
            c0 = list(r).index(label) + 1 if False else None
            for j, jaar in enumerate(jaren):
                pos = list(r).index(None) if False else None
                waarde = getal(r[kol0 + j]) if kol0 + j < len(r) else None
                if waarde is None: continue
                rijen.append([reg, kpi[label], jaar, round(waarde, 2)])
schrijf("t112_wei_investment.csv", ["Region", "Category", "Year", "Investment USD billion"], rijen)

# ---- t113 IEA WEO 2026 Annex A (wereld, totale energievoorziening en elektriciteit) ----
w = pd.read_csv(f"{U}/7892c961-WEO2026_AnnexA_Free_Dataset_World.csv")
sel = w[(w.FLOW.isin(["Total energy supply", "Electricity generation", "Electrical capacity",
                       "Total final consumption", "CO2 total"]))]
sel = sel[sel.YEAR.isin([2010, 2024, 2030, 2035, 2040, 2050])]
rijen = [[r.SCENARIO, r.FLOW, r.UNIT, r.REGION, int(r.YEAR), round(float(r.VALUE), 3)] for r in sel.itertuples()]
schrijf("t113_weo_world_scenarios.csv", ["Scenario", "Flow", "Unit", "Region", "Year", "Value"], rijen)

# ---- t114 LBNL utility-scale solar: LCOE (2025 USD per MWh) en installatiekosten (2025 USD per Wac) ----
lb = openpyxl.load_workbook(f"{U}/utility_scale_solar_2026_edition_datafile.xlsx", data_only=True, read_only=True)
rijen = []
for r in lb["LCOE Trend (PV only)"].iter_rows(min_row=29, values_only=True):
    if r and isinstance(r[0], (int, float)) and 2000 < r[0] < 2030 and r[1] is not None:
        rijen.append(["LCOE", int(r[0]), getal(r[1]), getal(r[2]), getal(r[3]), getal(r[4])])
for r in lb["CapEx Trend (PV-only)"].iter_rows(min_row=28, values_only=True):
    if r and isinstance(r[0], (int, float)) and 2000 < r[0] < 2030 and r[1] is not None:
        rijen.append(["Installed cost", int(r[0]), getal(r[1]), getal(r[2]), getal(r[3]), getal(r[4])])
schrijf("t114_lbnl_solar_cost.csv",
        ["Series", "Year", "Projects", "Capacity MW",
         "LCOE without tax credits 2025 USD per MWh (LCOE rijen) or capacity-weighted cost 2025 USD per Wac (cost rijen)",
         "LCOE with tax credits 2025 USD per MWh (LCOE rijen) or median cost 2025 USD per Wac (cost rijen)"], rijen)

# ---- t115 Solargis PV-potentieel per land (2020) ----
s = pd.read_excel(f"{U}/27e61910-solargis_pvpotential_countryranking_2020_data.xlsx",
                  sheet_name="Country indicators", header=1)
s.columns = [schoon(c) for c in s.columns]
kolommen = [c for c in s.columns if c.startswith("Average")]
rijen = []
for r in s.itertuples(index=False):
    d = r._asdict() if hasattr(r, "_asdict") else None
    rijen.append([getattr(r, "_0") if False else None])
rijen = []
for _, r in s.iterrows():
    naam = schoon(r.iloc[1])
    if not naam or naam == "nan": continue
    waarden = [getal(r[c]) for c in kolommen]
    rijen.append([schoon(r.iloc[0]), naam, schoon(r.iloc[3])] + waarden)
schrijf("t115_solargis_pv_potential.csv", ["ISO3", "Country", "World Bank region"] + [schoon(c) for c in kolommen], rijen)

# ---- t116 RISE-scores per land en jaar (2010-2023) ----
rijen = []
for bestand, label in [("98a0d1cd-ee_pillar_website_upload.xlsx", "EE"), ("4c26fe2d-re_pillar_website_upload.xlsx", "RE")]:
    wbx = openpyxl.load_workbook(f"{U}/{bestand}", data_only=True, read_only=True)
    for blad in wbx.sheetnames:
        jaar = blad.split()[-1]
        rows = list(wbx[blad].iter_rows(min_row=3, values_only=True))
        for r in rows:
            if not r or not r[0]: continue
            rijen.append([label, jaar, schoon(r[0]), schoon(r[1]), schoon(r[2]), getal(r[3])])
schrijf("t116_rise_scores.csv", ["Pillar", "Year", "Country", "Income group", "Region", "Overall score"], rijen)

# ---- t117 IEX India dag-vooruit op 28 nov 2026 (per kwartier) ----
rijen = []
for bestand, markt in [("78f33cea-DAM_Market_Snapshot.xlsx", "DAM"), ("f7da1e3f-GDAM_Market_Snapshot.xlsx", "GDAM")]:
    ws = openpyxl.load_workbook(f"{U}/{bestand}", data_only=True, read_only=True)["Sheet1"]
    rows = list(ws.iter_rows(min_row=6, values_only=True))
    if markt == "DAM":
        for r in rows:
            if r and r[0] and r[2] and " - " in str(r[2]): rijen.append([markt, schoon(r[0]), schoon(r[2]), getal(r[3]), getal(r[4]), getal(r[5]), getal(r[7])])
    else:
        for r in rows:
            if r and r[0] and r[2] and " - " in str(r[2]): rijen.append([markt, schoon(r[0]), schoon(r[2]), getal(r[3]), getal(r[4]), getal(r[9]), None])
schrijf("t117_iex_india_dam_28nov2026.csv",
        ["Market", "Date", "Time block", "Purchase bid MW", "Sell bid MW", "Cleared volume MW", "Clearing price Rs per MWh"], rijen)

# ---- t118 GEM zon en wind: capaciteit per land en status (utility-schaal) ----
rijen = []
for bestand, techn in [("Global-Solar-Power-Tracker-February-2026.xlsx", "Solar"), ("Global-Wind-Power-Tracker-February-2026.xlsx", "Wind")]:
    ws = openpyxl.load_workbook(f"{G}/{bestand}", read_only=True, data_only=True)
    blad = "Utility-Scale (1 MW+)" if techn == "Solar" else "Data"
    rows = ws[blad].iter_rows(values_only=True)
    kop = [schoon(c) for c in next(rows)]
    ic, ist, icap = kop.index("Country/Area"), kop.index("Status"), kop.index("Capacity (MW)")
    agg = {}
    for r in rows:
        if not r or not r[ic]: continue
        key = (schoon(r[ic]), schoon(r[ist]))
        c = getal(r[icap]) or 0.0
        n, m = agg.get(key, (0, 0.0))
        agg[key] = (n + 1, m + c)
    for (land, status), (n, mw) in agg.items():
        rijen.append([techn, land, status, n, round(mw, 1)])
schrijf("t118_gem_solar_wind.csv", ["Technology", "Country", "Status", "Projects", "Capacity MW"], rijen)
