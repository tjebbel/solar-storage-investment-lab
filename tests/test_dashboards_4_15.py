"""Tests voor de modules achter dashboards 4, 5, 7, 9-11, 13, 14 en 15."""
import unittest

import numpy as np
import pandas as pd

from eti import assurance_overzicht, bcg_portefeuille, impact_zuiden, overheden


class Ervaringscurve(unittest.TestCase):
    def test_bekende_leersnelheid(self):
        gw = np.array([100, 200, 400, 800, 1600, 3200.0])
        prijs = 1.0 * 0.8 ** np.log2(gw / 100)                      # precies 20% goedkoper per verdubbeling
        t = pd.DataFrame({"Jaar": range(2015, 2021), "Prijs USD per W": prijs, "Cumulatief GW": gw, "Volledig jaar": True})
        r = bcg_portefeuille.leersnelheid(t)
        self.assertAlmostEqual(r["leersnelheid"], 0.20, places=6)
        self.assertAlmostEqual(r["r2"], 1.0, places=6)


class Kapitaalkosten(unittest.TestCase):
    def test_zelfde_wacc_verandert_niets_en_lagere_wacc_is_goedkoper(self):
        self.assertAlmostEqual(impact_zuiden.lcoe_bij(50.0, 0.08, 0.08), 50.0)
        self.assertLess(impact_zuiden.lcoe_bij(50.0, 0.12, 0.05), 50.0)


class Gebeurtenisstudie(unittest.TestCase):
    def test_voor_en_na(self):
        maanden = pd.date_range("2024-12-01", "2025-12-01", freq="MS")
        toe = [10.0] * 6 + [50.0] + [2.0] * 6                       # piek in juni 2025 = de gebeurtenismaand
        b = pd.DataFrame({"ISO 3 Code": "CHN", "Bron": "Zon", "Maand": maanden, "Toevoeging GW": toe})
        s = overheden.gebeurtenisstudie(b).set_index("Land").loc["China"]
        self.assertAlmostEqual(s["GW per maand ervoor"], 10.0)
        self.assertAlmostEqual(s["GW per maand erna"], 2.0)
        self.assertEqual(s["Piekmaand"], "2025-06")


class Risicokaart(unittest.TestCase):
    def test_score_en_volgorde(self):
        r = assurance_overzicht.risico()
        self.assertTrue((r["Score"] == r["Kans"] * r["Impact"]).all())
        self.assertTrue(r["Score"].is_monotonic_decreasing)


if __name__ == "__main__":
    unittest.main()
