import unittest

import numpy as np
import pandas as pd

from eti import kernenergie as kern


def maand(kwartier=False):
    stap = 900 if kwartier else 3600
    n = 48 * (4 if kwartier else 1)
    tijd = [1_735_689_600 + i * stap for i in range(n)]                 # 1 januari 2025, 00:00 UTC
    opwek = {"unix_seconds": tijd, "production_types": [
        {"name": "Nuclear", "data": [1000.0] * n}, {"name": "Solar", "data": [500.0] * n},
        {"name": "Load", "data": [9000.0] * n}, {"name": "Hydro pumped storage consumption", "data": [-200.0] * n},
        {"name": "Cross border electricity trading", "data": [300.0] * n}]}
    prijs = {"unix_seconds": tijd, "price": [50.0] * n}
    return opwek, prijs


class KernenergieTest(unittest.TestCase):
    def test_uurreeks_telt_alleen_opwek_en_middelt_kwartieren(self):
        u = kern.uurreeks(*maand(kwartier=True))
        self.assertEqual(len(u), 48)
        self.assertAlmostEqual(u.kern.iloc[0], 1000.0)
        self.assertAlmostEqual(u.totaal.iloc[0], 1500.0)          # kern plus zon; vraag, pompverbruik en handel tellen niet mee

    def test_zone_zonder_kernenergie_geeft_niets(self):
        opwek, prijs = maand()
        opwek["production_types"] = [r for r in opwek["production_types"] if r["name"] != "Nuclear"]
        self.assertIsNone(kern.uurreeks(opwek, prijs))

    def _jaar(self, terugregelen):
        tijd = pd.date_range("2025-01-01", periods=24 * 40, freq="h", tz="UTC")
        prijs = np.where(tijd.hour == 12, -10.0, 60.0)             # elke dag een negatief uur op de middag
        productie = np.where(tijd.hour == 12, 1000.0 * terugregelen, 1000.0)
        return pd.DataFrame({"kern": productie, "totaal": productie * 2, "prijs": prijs}, index=tijd)

    def test_vlak_profiel_vangt_de_gemiddelde_prijs(self):
        k = kern.kengetallen(self._jaar(1.0), top=1000.0, vermogen_mw=1250.0)
        self.assertAlmostEqual(k["capture_kern"], 1.0)
        self.assertAlmostEqual(k["aandeel_in_negatieve_uren"], 1 / 24)
        self.assertAlmostEqual(k["productie_bij_negatieve_prijs"], 1.0)
        self.assertAlmostEqual(k["daguitslag_mediaan"], 0.0)
        self.assertAlmostEqual(k["benutting_tov_vermogen"], 0.8)
        self.assertEqual(k["dagen_met_negatieve_prijs"], 40)

    def test_terugregelen_bij_negatieve_prijs_verhoogt_de_capture_rate(self):
        k = kern.kengetallen(self._jaar(0.5))
        self.assertAlmostEqual(k["productie_bij_negatieve_prijs"], 0.5)
        self.assertAlmostEqual(k["daguitslag_mediaan"], 0.5)
        self.assertGreater(k["capture_kern"], 1.0)
        self.assertLess(k["aandeel_in_negatieve_uren"], 1 / 24)

    def test_te_korte_reeks_geeft_niets(self):
        self.assertIsNone(kern.kengetallen(self._jaar(1.0).iloc[:100]))


if __name__ == "__main__":
    unittest.main()
