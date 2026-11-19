import unittest
from pathlib import Path
from eti import kpi_dashboards as k


@unittest.skipUnless(Path("tableau/data/t15_controles.csv").exists() and Path("tableau/data/t45_leercurve.csv").exists(), "tabellen ontbreken")
class TestKPI(unittest.TestCase):
    def test_vier_tegels_per_dashboard(self):
        for f in (k.dashboard2, k.dashboard3, k.dashboard4, k.dashboard7):
            t = f()
            self.assertEqual(len(t), 4)
            self.assertTrue(all(x["Richting"] in ("goed", "slecht", "neutraal") for x in t))
            self.assertTrue(all(x["Tekst"] for x in t))


if __name__ == "__main__":
    unittest.main()
