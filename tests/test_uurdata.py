import unittest
import numpy as np
import pandas as pd
from eti import uurdata as u


def _dag(prijzen, dagen=3, zon=None):
    i = pd.date_range("2025-06-01", periods=24 * dagen, freq="h")
    df = pd.DataFrame({"Price": np.tile(prijzen, dagen)}, index=i)
    if zon is not None:
        df["Solar"] = np.tile(zon, dagen); df["Fossil gas"] = 100 - df["Solar"]; df["Load"] = 100.0
    return df


class TestUurdata(unittest.TestCase):
    def test_arbitrage_perfecte_voorkennis(self):
        p = np.full(24, 50.0); p[3] = p[4] = 10.0; p[19] = p[20] = 150.0
        r = u.arbitrage(_dag(p), "XX", 2025)
        self.assertAlmostEqual(r["Average daily margin EUR/MW"], 2 * 150 * 0.88 - 2 * 10)
        self.assertEqual(r["Days"], 3)

    def test_middagdip_en_negatieve_uren(self):
        p = np.full(24, 100.0); p[11:15] = -5.0
        r = u.diepte(_dag(p), "XX", 2025)
        self.assertAlmostEqual(r["Midday price 11-15h"], -5.0)
        self.assertEqual(r["Negative hours"], 12)

    def test_koolstofvrij_aandeel(self):
        zon = np.zeros(24); zon[8:16] = 60.0
        jr, uur = u.koolstofvrij(_dag(np.full(24, 50.0), zon=zon), "XX", 2025)
        self.assertAlmostEqual(jr["Carbon-free share %"], 100 * 8 * 60 / (24 * 100))
        self.assertAlmostEqual(uur.set_index("Hour").loc[12, "Carbon-free share %"], 60.0)

    def test_hirth_vindt_de_helling(self):
        x = np.linspace(1, 30, 40)
        m = pd.DataFrame({"Zone": "XX", "Solar share %": x, "Solar capture rate": 1.05 - 0.015 * x})
        h = u.hirth(m).iloc[0]
        self.assertAlmostEqual(h["Slope per percentage point"], -0.015, places=6)
        self.assertGreater(h.R2, 0.999)

    def test_land_van_zone(self):
        self.assertEqual(u.land("IT-North"), "Italy"); self.assertEqual(u.land("NO3"), "Norway"); self.assertEqual(u.land("DE-LU"), "Germany")


if __name__ == "__main__":
    unittest.main()
