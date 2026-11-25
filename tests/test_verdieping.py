"""Toetsen voor de kruisanalyses (t77-t81): rekenregels en samenhang met de brontabellen."""
import unittest
from pathlib import Path

import pandas as pd

D = Path("tableau/data_en")


@unittest.skipUnless((D / "t77_ppa_vs_2030.csv").exists(), "draai eerst eti.verdieping")
class Verdieping(unittest.TestCase):
    def test_ppa_verschil(self):
        t = pd.read_csv(D / "t77_ppa_vs_2030.csv")
        self.assertTrue(((t["PPA price EUR/MWh"] - t["Solar revenue 2030 EUR/MWh"] - t["PPA minus 2030 revenue"]).abs() < 1e-3).all())
        self.assertFalse(t.Market.duplicated().any())

    def test_ppa_prijs_gelijk_aan_bron(self):
        t = pd.read_csv(D / "t77_ppa_vs_2030.csv").set_index("Market")["PPA price EUR/MWh"]
        b = pd.read_csv(D / "t76_ppa_countries.csv").set_index("Market")["Price EUR/MWh"]
        self.assertTrue(((t - b.reindex(t.index)).abs() < 1e-3).all())

    def test_hedge_alleen_bij_verlies_en_winst(self):
        t = pd.read_csv(D / "t78_solar_battery_hedge.csv")
        h = t.dropna(subset=["Battery MW per solar MW to offset"])
        self.assertTrue((h["Solar capture price change"] < 0).all() and (h["Battery revenue per MW change"] > 0).all())
        self.assertTrue((h["Battery MW per solar MW to offset"] > 0).all())

    def test_voorspelwaarde(self):
        t = pd.read_csv(D / "t80_forecast_value.csv")
        self.assertTrue(((t["Battery model EUR/MW"] - t["Battery yesterday EUR/MW"] - t["Revenue gain EUR per MW"]).abs() < 1).all())

    def test_pareto(self):
        t = pd.read_csv(D / "t81_impact_frontier.csv")
        co2 = "CO2 per M EUR per year, marginal fossil response"
        s = t[t["Has marginal factor"]]
        for _, r in s[s["On the frontier"]].iterrows():
            beter = (s["IRR P50"] > r["IRR P50"]) & (s[co2] > r[co2])
            self.assertFalse(beter.any())
        self.assertFalse(t.loc[~t["Has marginal factor"], "On the frontier"].any())

    def test_kapitaalkosten(self):
        t = pd.read_csv(D / "t82_cost_of_capital.csv").set_index("Country")
        self.assertAlmostEqual(t.at["Europe", "LCOE vs European financing"], 1.0, places=6)
        self.assertTrue((t["LCOE vs European financing"] >= 1).all())
        self.assertTrue(t.WACC.between(0.02, 0.2).all())


class OpenbareBronnen(unittest.TestCase):
    def test_openbare_bronnen(self):
        t = pd.read_csv("data/extern/terugleververgoeding_2027.csv")
        self.assertTrue(((t["Feed-in payment ct/kWh"] - t["Feed-in cost ct/kWh"] - t["Net ct/kWh"]).abs() < 0.01).all())
        w = pd.read_csv("data/extern/wachtrij_netbeheer.csv")
        self.assertEqual(len(w), 24)
        self.assertTrue(w.groupby("Date").size().eq(4).all())
        e = pd.read_csv("data/extern/energiearmoede.csv")
        self.assertEqual(e["Year"].tolist(), list(range(2019, 2026)))
        j = pd.read_csv("data/extern/irena_jobs_2025.csv")
        self.assertLess(j[j["Dimension"] == "Technology"]["Jobs million"].sum(), j[j["Dimension"] == "Total"]["Jobs million"].iloc[0])

class KostprijsPerLand(unittest.TestCase):
    def test_lcoe_per_land(self):
        t = pd.read_csv(D / "t92_solar_lcoe_country.csv")
        self.assertEqual(len(t), 26)
        self.assertTrue(t["LCOE own model EUR/MWh"].between(20, 100).all())
        self.assertEqual((t["IRENA basis"] == "IRENA 2024 country data").sum(), 7)
        nl = t.set_index("Country").loc["Netherlands"]
        self.assertLess(abs(nl["LCOE own model EUR/MWh"] - nl["LCOE IRENA EUR/MWh"]), 5)


if __name__ == "__main__":
    unittest.main()
