import unittest
from pathlib import Path
from eti import vertaal_en as v


class TestVertaling(unittest.TestCase):
    def test_vaste_en_regelteksten(self):
        self.assertEqual(v.vertaal("Zon houdt waarde"), "Solar holds value")
        self.assertEqual(v.vertaal("Noorwegen (Zuid)"), "Norway (South)")
        self.assertEqual(v.vertaal("6 van 11"), "6 of 11")
        self.assertEqual(v.vertaal("LCOE 2025 (67,39)"), "LCOE 2025 (67.39)")
        self.assertIsNone(v.vertaal("een zin die nog niet vertaald is"))

    @unittest.skipUnless(Path("tableau/data/t15_controles.csv").exists(), "tabellen ontbreken")
    def test_niets_ontbreekt(self):
        self.assertEqual(v.main(), set())
        self.assertEqual(v.veldnamen(), [])
        import pandas as pd
        self.assertIn("Solar holds value", set(pd.read_csv("tableau/data_en/t1_zonejaar.csv")["Segment"]))


    def test_engelse_kolommen_en_tegels(self):
        import pandas as pd
        from pathlib import Path
        u = Path("tableau/data_en")
        if not (u / "t15_controles.csv").exists():
            self.skipTest("data_en ontbreekt")
        self.assertEqual(list(pd.read_csv(u / "t15_controles.csv", nrows=1).columns)[:3], ["Control", "Domain", "Objective"])
        self.assertIn("Zonenaam", pd.read_csv(u / "t2_land_maand.csv", nrows=1).columns)   # dashboard 1-2 houden NL kolommen
        k = pd.read_csv(u / "t50_kpi_dashboards.csv")
        self.assertTrue(set(k.Richting) <= {"good", "bad", "neutral"})


if __name__ == "__main__":
    unittest.main()
