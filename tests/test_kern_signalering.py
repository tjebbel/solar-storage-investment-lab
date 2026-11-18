"""Tests voor eti.kern_wereld (derde dashboard) en eti.signalering_europa (tweede dashboard)."""
import unittest

import numpy as np
import pandas as pd

from eti import kern_wereld, signalering_europa


class Inhaaljaar(unittest.TestCase):
    def test_blijvend_voorbij(self):
        jaren = range(2015, 2021)
        zon = pd.Series([1, 2, 6, 4, 7, 9], index=jaren)       # 2017 even voorbij, 2018 terug, vanaf 2019 blijvend
        kern = pd.Series([5, 5, 5, 5, 5, 5], index=jaren)
        self.assertEqual(kern_wereld.inhaaljaar(zon, kern), 2019)

    def test_nog_niet_of_geen_kern(self):
        jaren = range(2015, 2018)
        self.assertTrue(np.isnan(kern_wereld.inhaaljaar(pd.Series([1, 2, 3], index=jaren), pd.Series([9, 9, 9], index=jaren))))
        self.assertTrue(np.isnan(kern_wereld.inhaaljaar(pd.Series([1, 2, 3], index=jaren), pd.Series([0, 0, 0], index=jaren))))


class Koers(unittest.TestCase):
    def test_categorieen(self):
        t = pd.DataFrame({"Kern TWh 2010": [100, 290, 50, 50, 10, 80],
                          "Kern TWh 2015": [100, 5, 50, 50, 10, 80],
                          "Kern TWh 2025": [0, 90, 40, 70, 10.5, np.nan]})
        t["Kern verschil 2015-2025 %"] = 100 * (t["Kern TWh 2025"] - t["Kern TWh 2015"]) / t["Kern TWh 2015"]
        self.assertEqual(list(kern_wereld.koers(t)),
                         ["Gestopt", "Herstart", "Afbouw", "Uitbouw", "Stabiel", "Geen gegevens 2025"])


class Signalering(unittest.TestCase):
    def maak(self, prijzen, capture=0.5):
        maanden = pd.date_range("2024-01-01", periods=len(prijzen), freq="MS")
        return pd.DataFrame({"Zonenaam": "Testland", "Zone": "TL", "Landcode": "TST", "Jaar": maanden.year,
                             "Maandnummer": maanden.month, "Maand": maanden.strftime("%Y-%m-%d"),
                             "Gemiddelde prijs": prijzen, "Capture rate zon": capture})

    def test_zscore_alleen_voorgaande_maanden(self):
        prijzen = [50 + (i % 2) for i in range(12)] + [80.0]      # rustig jaar, dan een uitschieter
        d = signalering_europa.bereken(self.maak(prijzen))
        laatste = d.iloc[-1]
        venster = pd.Series(prijzen[:12])
        self.assertAlmostEqual(laatste["Prijs z-score"], (80 - venster.mean()) / venster.std(ddof=1))
        self.assertEqual(laatste["Prijs signaal"], "Schok")

    def test_status_grenzen(self):
        d = signalering_europa.bereken(self.maak([100.0, 140.0, 150.0], capture=0.5), lcoe=70.0)   # marges -20, 0, 5
        self.assertEqual(list(d["Status zon"]), ["Kosten niet gedekt", "Krap", "Gedekt"])


if __name__ == "__main__":
    unittest.main()
