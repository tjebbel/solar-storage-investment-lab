"""Verdieping 23 november 2026: vijf kruisanalyses op bestaande tabellen, alleen Engels.
Voor de geplande onderzoeken 37 (PPA als de capture rate daalt) en 38 (flexibiliteit) en versie 2 van 27 en 30.

Geen nieuwe bronnen: alles komt uit tableau/data_en. Draai dit na omzet_risico, ppa_waardeketen, fonds_simulator en voorspelmodel.
Tabellen (tableau/data en tableau/data_en):
  t77_ppa_vs_2030        dashboard 37: PPA-prijs per land (t76) tegen de zon-opbrengst 2025 en de stresstest 2030 (t70) en de LCOE.
                         Een PPA loopt tien jaar; 2030 is een eerlijker ijkpunt dan alleen 2025. Stresstest, geen prognose.
  t78_solar_battery_hedge dashboard 38: per zone de verandering 2023-2025 van de capture-prijs zon en de batterij-omzet (t1), en
                         hoeveel MW batterij per MW zon het verlies van zon dekt (aanname: VOLLASTUREN vollasturen zon).
  t79_battery_drivers    dashboard 38: batterij-omzet per zone en jaar tegen dagspreiding, negatieve uren en avond/middag-verhouding
                         (t1, t54), met de voorspelling uit de dagspreiding alleen en het residu.
  t80_forecast_value     dashboard 30 v2: wat het voorspelmodel (t73) oplevert in euro per MW, naast de verbetering van de fout.
  t81_impact_frontier    dashboard 27 v2: bouwstenen van de fondssimulator (t65): rendement tegen vermeden CO2, met Pareto-vlag.
  t82_cost_of_capital    dashboard 15: kapitaalkosten zon per land (data/extern/kapitaalkosten_landen.csv, IEA) en wat dezelfde
                         zonnecentrale daardoor meer kost dan bij Europese financiering (zelfde rekenregel als impact_zuiden:
                         85% van de LCOE is kapitaal, looptijd 25 jaar). Jaren verschillen per land (2021 of 2024): kolom Year.
  t83_public_finance     dashboards 15 en 33: internationale publieke financiering per land, techniekgroep en jaar
                         (IRENA Renewable Energy Statistics 2026, PUBFIN; miljoen USD van 2023). Ontvangende landen.
  t84_public_solar_vs_capital  per land uit t82: publieke financiering voor zon-PV 2015-2024 naast de kapitaalkosten.
  t85_wacc_by_country    dashboard 33: kapitaalkosten en financieringsaandeel in de LCOE per land en techniek (IRENA Renewable
                         Power Generation Costs in 2024, figuur S.7; 64 landen voor zon), met Moody's-rating.
  t86_irena_solar_lcoe   dashboard 32: LCOE zon op utiliteitsschaal per regio en vier grote markten, 2015 en 2024 (IRENA tabel 3.3).
  t87_iea_wacc_survey    dashboards 15 en 33: IEA Cost of Capital Observatory, alle projecttypen, landen en jaren (2019-2024).
Beperkingen: t70 kent twee LCOE-waarden (Spanje, Nederland) voor alle landen; KYOS ligt ongeveer 25% onder LevelTen;
VOLLASTUREN is een vaste aanname voor alle zones; correlaties zijn geen oorzaak.
Gebruik:  PYTHONPATH=src python3 -m eti.verdieping
"""
from pathlib import Path

import numpy as np
import pandas as pd

D = Path("tableau/data_en")
UIT = [Path("tableau/data"), Path("tableau/data_en")]
VOLLASTUREN = 1000          # vollasturen zon per jaar, vaste aanname voor de hedge-verhouding
CO2 = "CO2 per M EUR per year, marginal fossil response"
KAPITAALDEEL, LOOPTIJD = 0.85, 25   # zoals in impact_zuiden


def ppa_vs_2030():
    p = pd.read_csv(D / "t76_ppa_countries.csv")
    r = pd.read_csv(D / "t70_revenue_at_risk.csv")
    t = p.merge(r, left_on="Market", right_on="Country")
    t["PPA source"] = np.where(t.Source.str.startswith("LevelTen"), "LevelTen P25 offer", "KYOS estimate")
    uit = t[["Market", "PPA source", "Price EUR/MWh", "Solar revenue 2025 EUR/MWh", "Solar revenue 2030 EUR/MWh", "LCOE EUR/MWh"]].copy()
    uit = uit.rename(columns={"Price EUR/MWh": "PPA price EUR/MWh"})
    uit["PPA minus 2025 revenue"] = uit["PPA price EUR/MWh"] - uit["Solar revenue 2025 EUR/MWh"]
    uit["PPA minus 2030 revenue"] = uit["PPA price EUR/MWh"] - uit["Solar revenue 2030 EUR/MWh"]
    uit["PPA minus LCOE"] = uit["PPA price EUR/MWh"] - uit["LCOE EUR/MWh"]
    uit["Reading"] = np.select(
        [(uit["PPA minus 2025 revenue"] > 0) & (uit["PPA minus 2030 revenue"] > 0),
         (uit["PPA minus 2025 revenue"] <= 0) & (uit["PPA minus 2030 revenue"] > 0),
         (uit["PPA minus 2025 revenue"] <= 0) & (uit["PPA minus 2030 revenue"] <= 0)],
        ["PPA above market in 2025 and 2030", "market paid more in 2025, PPA protects by 2030", "market above PPA in both years"],
        "PPA above market in 2025 only")
    uit["2030 is extrapolated"] = (~t["Within observed range"].astype(bool)) | t["Hits floor 0.2"].astype(bool)
    return uit.sort_values("PPA minus 2030 revenue", ascending=False)


def hedge():
    z = pd.read_csv(D / "t1_zonejaar.csv")
    z["cap"] = z["Gemiddelde prijs"] * z["Capture rate zon"]
    k = {"cap": "Solar capture price", "Batterij-omzet per MW": "Battery revenue per MW", "Capture rate zon": "Solar capture rate"}
    a, b = z[z.Jaar == 2023].set_index("Zone"), z[z.Jaar == 2025].set_index("Zone")
    t = pd.DataFrame({"Zone name": b.Zonenaam, "Region": b.Regio})
    for kol, naam in k.items():
        t[f"{naam} 2023"], t[f"{naam} 2025"] = a[kol], b[kol]
        t[f"{naam} change"] = b[kol] - a[kol]
    t["Solar revenue change EUR per MW"] = t["Solar capture price change"] * VOLLASTUREN
    t["Battery MW per solar MW to offset"] = np.where(
        (t["Solar revenue change EUR per MW"] < 0) & (t["Battery revenue per MW change"] > 0),
        -t["Solar revenue change EUR per MW"] / t["Battery revenue per MW change"], np.nan)
    t["Reading"] = np.select(
        [(t["Solar capture price change"] < 0) & (t["Battery revenue per MW change"] > 0),
         (t["Solar capture price change"] < 0) & (t["Battery revenue per MW change"] <= 0),
         (t["Solar capture price change"] >= 0) & (t["Battery revenue per MW change"] > 0)],
        ["hedge: solar down, battery up", "both down", "both up"], "solar up, battery down")
    vol = z[z["Heel jaar"].astype(str).str.lower().isin(["true", "1", "ja", "yes"]) & (z.Jaar <= 2025)]
    t["Correlation capture rate vs battery revenue 2019-2025"] = vol.groupby("Zone").apply(
        lambda g: g["Capture rate zon"].corr(g["Batterij-omzet per MW"]))
    t["Full-load hours assumed"] = VOLLASTUREN
    return t.dropna(subset=["Solar capture price change"]).reset_index().sort_values("Battery revenue per MW change", ascending=False)


def drivers():
    z = pd.read_csv(D / "t1_zonejaar.csv")
    d = pd.read_csv(D / "t54_duck_depth.csv")
    t = d.merge(z, left_on=["Zone", "Year"], right_on=["Zone", "Jaar"])
    t = t[t.Year <= 2025]                                             # 2026 is een deeljaar
    uit = t[["Zone", "Zone name", "Regio", "Year", "Dagspreiding", "Negatieve uren", "Evening to midday ratio",
             "Midday dip EUR/MWh", "Gemiddelde prijs", "Batterij-omzet per MW"]].rename(columns={
        "Regio": "Region", "Dagspreiding": "Daily spread EUR/MWh", "Negatieve uren": "Negative hours",
        "Gemiddelde prijs": "Average price EUR/MWh", "Batterij-omzet per MW": "Battery revenue per MW"})
    x, y = uit["Daily spread EUR/MWh"], uit["Battery revenue per MW"]
    b, a = np.polyfit(x, y, 1)
    uit["Predicted from daily spread"] = a + b * x
    uit["Residual EUR per MW"] = y - uit["Predicted from daily spread"]
    uit["EUR per MW per EUR/MWh of spread"] = b
    for kol in ("Daily spread EUR/MWh", "Negative hours", "Evening to midday ratio", "Midday dip EUR/MWh", "Average price EUR/MWh"):
        uit[f"R2 {kol.split(' EUR')[0].lower()}"] = uit[kol].corr(y) ** 2
    return uit


def forecast_value():
    f = pd.read_csv(D / "t73_forecast_model.csv")
    f["Share captured gain"] = f["Battery model vs perfect"] - f["Battery yesterday vs perfect"]
    f["Revenue gain EUR per MW"] = f["Battery model EUR/MW"] - f["Battery yesterday EUR/MW"]
    f["Revenue gain %"] = 100 * f["Revenue gain EUR per MW"] / f["Battery yesterday EUR/MW"]
    f["Still left on the table EUR per MW"] = f["Battery perfect EUR/MW"] - f["Battery model EUR/MW"]
    f["Improvement from lags and calendar only %"] = 100 * (1 - f["MAE lags and calendar only EUR/MWh"] / f["MAE yesterday EUR/MWh"])
    return f


def frontier():
    a = pd.read_csv(D / "t65_fund_assets.csv")
    t = a[["Building block", "Technology", "Country", "IRR P10", "IRR P50", "IRR P90", "Share of draws with IRR above 8%",
           "CO2 per M EUR per year, average", "CO2 per M EUR per year, marginal domestic", CO2]].copy()
    t["Has marginal factor"] = t[CO2].notna()
    s = t[t["Has marginal factor"]]
    t["On the frontier"] = [bool(h) and not ((s["IRR P50"] >= i) & (s[CO2] >= c) & ((s["IRR P50"] > i) | (s[CO2] > c))).any()
                            for i, c, h in zip(t["IRR P50"], t[CO2], t["Has marginal factor"])]
    t["Clears 8% at P50"] = t["IRR P50"] >= 0.08
    t["Method spread (fossil response / domestic)"] = t[CO2] / t["CO2 per M EUR per year, marginal domestic"].where(lambda v: v > 0)
    return t.sort_values("IRR P50", ascending=False)


def crf(w, n=LOOPTIJD):
    return w / (1 - (1 + w) ** -n)


def cost_of_capital():
    k = pd.read_csv(Path("data/extern") / "kapitaalkosten_landen.csv")
    basis = k.loc[k.Country == "Europe", "WACC"].iloc[0]
    k["WACC %"] = 100 * k.WACC
    k["LCOE vs European financing"] = (1 - KAPITAALDEEL) + KAPITAALDEEL * crf(k.WACC) / crf(basis)
    k["Extra cost from capital %"] = 100 * (k["LCOE vs European financing"] - 1)
    k["Cheaper at European financing %"] = 100 * (1 - 1 / k["LCOE vs European financing"])
    k["Multiple of European WACC"] = k.WACC / basis
    return k.sort_values("WACC", ascending=False)


GROEP = {"Solar photovoltaic": "Solar", "Solar thermal energy": "Solar", "Wind energy": "Wind", "Onshore wind energy": "Wind",
         "Offshore wind energy": "Wind", "Renewable hydropower": "Hydropower", "Coal": "Fossil fuels", "Natural gas": "Fossil fuels",
         "Oil": "Fossil fuels", "Other fossil fuels": "Fossil fuels", "Nuclear energy": "Nuclear"}


def public_finance():
    p = pd.read_csv(Path("data/extern") / "irena_pubfin_2026.csv")
    p["Group"] = p.Technology.map(GROEP).fillna("Other renewables and storage")
    p["Unallocated"] = p.Country.str.contains("Residual|Unspecified|unallocated", case=False)
    return p.rename(columns={"Value": "Public finance M USD (2023 prices)"})


def public_solar_vs_capital():
    p = public_finance()
    s = p[(p.Technology == "Solar photovoltaic") & p.Year.between(2015, 2024)]
    tot = s.groupby("Country")["Public finance M USD (2023 prices)"].sum()
    k = cost_of_capital()[["Country", "Group", "WACC %", "Year", "Extra cost from capital %"]].rename(columns={"Year": "WACC year"})
    k["Public solar finance 2015-2024 M USD"] = k.Country.map(tot)
    k["Recipient of international public finance"] = k["Public solar finance 2015-2024 M USD"].notna()
    return k.sort_values("Public solar finance 2015-2024 M USD", ascending=False)


def lcoe_country():
    """Dashboard 32: kostprijs van zon per land op drie grondslagen naast de capture-prijs (zie eti.lcoe en t13)."""
    from eti.lcoe import per_land
    t = pd.read_csv(D / "t13_kostencurve.csv")[["Country code", "Country", "Solar capture price EUR/MWh", "LCOE own model",
                                                 "LCOE", "LCOE source", "LCOE previous assumption"]]
    k = per_land(t["Country code"])
    t["Yield kWh per kW"] = t["Country code"].map(k["Opbrengst kWh per kW"])
    t["Yield reliable"] = t["Country code"].map(k["Opbrengst betrouwbaar"])
    t["WACC %"] = t["Country code"].map(k["WACC %"])
    t["WACC from IRENA country data"] = t["Country code"].map(k["WACC-bron"]) == "IRENA 2024, land"
    t = t.rename(columns={"LCOE own model": "LCOE own model EUR/MWh", "LCOE": "LCOE IRENA EUR/MWh", "LCOE source": "IRENA basis",
                          "LCOE previous assumption": "LCOE previous assumption EUR/MWh"})
    for n in ("own model", "IRENA", "previous assumption"):
        t[f"Margin {n} EUR/MWh"] = t["Solar capture price EUR/MWh"] - t[f"LCOE {n} EUR/MWh"]
    return t.sort_values("LCOE IRENA EUR/MWh")


def uit_extern(naam):
    return pd.read_csv(Path("data/extern") / naam)


def wachtrij_europa():
    """Wachtrij voor een netaansluiting per land, met de verhouding tot de piekvraag (definities verschillen per land)."""
    d = uit_extern("netwachtrij_europa_2026.csv")
    d["Queue as multiple of peak demand"] = (d["Queue GW"] / d["Peak demand 2025 GW"]).round(1)
    return d


def grondstoffen():
    """Maandprijzen van zilver, koper en aluminium (Wereldbank Pink Sheet), met een index op januari 2019 = 100."""
    r = pd.read_excel("data/extern/pink_sheet_monthly.xlsx", sheet_name="Monthly Prices", header=None, skiprows=4)
    kop, eenheid = r.iloc[0], r.iloc[1]
    d = r.iloc[2:].rename(columns={0: "Maand"})
    uit = []
    for naam in ("Silver", "Copper", "Aluminum"):
        k = kop[kop == naam].index[0]
        t = pd.DataFrame({"Month": pd.to_datetime(d["Maand"].str.replace("M", "-") + "-01"), "Commodity": naam,
                          "Price USD": pd.to_numeric(d[k], errors="coerce"), "Unit": str(eenheid[k]).strip("()")})
        t = t[t["Month"] >= "2015-01-01"].dropna(subset=["Price USD"])
        basis = t.loc[t["Month"] == "2019-01-01", "Price USD"].iloc[0]
        t["Index (Jan 2019 = 100)"] = (100 * t["Price USD"] / basis).round(1)
        uit.append(t)
    return pd.concat(uit, ignore_index=True)


def huishoudprofiel():
    """Gemiddeld uurprofiel per maand van een huishouden (NEDU E1A 2026): zonder panelen, en met panelen afname en invoeding."""
    d = uit_extern("nedu_profielen_2026_uur.csv")
    t = pd.to_datetime(d["Hour start CET"])
    d = d.assign(Month=t.dt.month, Hour=t.dt.hour)
    g = d.groupby(["Month", "Hour"])[["E1A_AZI_A", "E1A_AMI_A", "E1A_AMI_I"]].sum().reset_index()
    g = g.rename(columns={"E1A_AZI_A": "Offtake without solar (fraction of year)", "E1A_AMI_A": "Offtake with solar (fraction of year)",
                          "E1A_AMI_I": "Feed-in with solar (fraction of year)"})
    return g.round(8)


def main():
    uit = {"t77_ppa_vs_2030": ppa_vs_2030(), "t78_solar_battery_hedge": hedge(), "t79_battery_drivers": drivers(),
           "t80_forecast_value": forecast_value(), "t81_impact_frontier": frontier(), "t82_cost_of_capital": cost_of_capital(),
           "t83_public_finance": public_finance(), "t84_public_solar_vs_capital": public_solar_vs_capital(),
           "t85_wacc_by_country": uit_extern("irena_wacc_2024.csv"), "t86_irena_solar_lcoe": uit_extern("irena_solar_lcoe_2024.csv"),
           "t87_iea_wacc_survey": uit_extern("iea_cost_of_capital_observatory_2025.csv"),
           "t88_energy_poverty": uit_extern("energiearmoede.csv"), "t89_grid_queue": uit_extern("wachtrij_netbeheer.csv"),
           "t90_feed_in_tariffs_2027": uit_extern("terugleververgoeding_2027.csv"),
           "t91_renewable_jobs": uit_extern("irena_jobs_2025.csv"), "t92_solar_lcoe_country": lcoe_country(),
           "t93_irena_solar_country": uit_extern("irena_solar_country_2024.csv"),
           "t94_subsidy_per_tonne": uit_extern("pbl_sde_2026_subsidie_intensiteit.csv"),
           "t95_grid_queue_europe": wachtrij_europa(), "t96_grid_costs": uit_extern("eurostat_netkosten.csv"),
           "t97_energy_poverty_region": uit_extern("cbs_energiearmoede_regio.csv"),
           "t98_storage_experience": uit_extern("opslag_ervaringscurves.csv"),
           "t100_commodity_prices": grondstoffen(), "t101_household_profile": huishoudprofiel(),
           "t102_hydrogen_projects": uit_extern("iea_hydrogen_projects_2026.csv")}
    ngfs = Path("data/extern/ngfs/ngfs_r5_electricity.csv")   # licentie: bron niet in de repo
    if ngfs.exists():
        uit["t99_ngfs_regions"] = pd.read_csv(ngfs)
    for naam, d in uit.items():
        for u in UIT:
            d.to_csv(u / f"{naam}.csv", index=False, float_format="%.6g")
        print(f"{naam}: {len(d)} rijen")
    return uit


if __name__ == "__main__":
    main()
