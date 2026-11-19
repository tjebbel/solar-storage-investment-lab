import unittest
from pathlib import Path
import pandas as pd
from eti import dashboard_extra as d

HEEFT = Path("tableau/data/t1_zonejaar.csv").exists() and Path(d.OPWEK).exists()


class TestGebeurtenissen(unittest.TestCase):
    def test_datums_geldig_en_uniek(self):
        g = d.gebeurtenissen()
        self.assertEqual(len(g), len(set(zip(g.Datum, g.Gebeurtenis))))
        self.assertTrue(pd.to_datetime(g.Datum).notna().all())


@unittest.skipUnless(HEEFT, "tabellen ontbreken")
class TestAfgeleid(unittest.TestCase):
    def test_kannibalisatie_helling_negatief(self):
        _, b = d.kannibalisatie()
        self.assertLess(b, 0)

    def test_kern_benutting_hoger_dan_zon(self):
        k = d.kern_zon().dropna(subset=["Benutting zon 2025"])
        k = k[k["Kern TWh 2025"] > 50]
        self.assertTrue((k["Benutting kern 2025"] > k["Benutting zon 2025"]).all())

    def test_leercurve_vier_varianten(self):
        self.assertEqual(len(d.leercurve()), 4)


if __name__ == "__main__":
    unittest.main()
