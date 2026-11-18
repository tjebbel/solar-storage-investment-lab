"""Dekking van de opwekreeks: een reeks die maar een deel van het jaar beslaat geeft geen bruikbare capture rate."""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import pandas as pd

from eti import herstel


def schrijf_maand(map_, zone, jaar, maand, zon):
    soorten = [{"name": "Wind onshore", "data": [10.0, 12.0]}]
    if zon is not None:
        soorten.append({"name": "Solar", "data": zon})
    with open(os.path.join(map_, f"power_{zone}_{jaar}_{maand:02d}.json"), "w", encoding="utf-8") as fh:
        json.dump({"unix_seconds": [0, 3600], "production_types": soorten}, fh)


class TestDekking(unittest.TestCase):
    def setUp(self):
        self.map = tempfile.TemporaryDirectory()
        for maand in range(1, 13):
            schrijf_maand(self.map.name, "XX", 2021, maand, [0.0, 5.0] if maand == 12 else None)      # reeks begint in december
            schrijf_maand(self.map.name, "YY", 2021, maand, [None, 0.0] if maand == 1 else [0.0, 3.0])  # januari zonder zon
        self.tabel = os.path.join(self.map.name, "fact_land_jaar.csv")
        pd.DataFrame({"land": ["Xland", "Yland", "Zland"], "biedzone": ["XX", "YY", "ZZ"], "jaar": [2021, 2021, 2021],
                      "capture_zon": [3.5, 0.9, 0.8], "capture_bron": ["opwek (Energy-Charts)"] * 3}).to_csv(self.tabel, index=False)
        self.oud, herstel.F = herstel.F, self.tabel

    def tearDown(self):
        herstel.F = self.oud
        self.map.cleanup()

    def test_maanddekking(self):
        self.assertAlmostEqual(herstel.maanddekking("XX", 2021, self.map.name), 1 / 12)
        self.assertAlmostEqual(herstel.maanddekking("YY", 2021, self.map.name), 11 / 12)
        self.assertIsNone(herstel.maanddekking("ZZ", 2021, self.map.name))

    def test_afkeuren_bewaart_de_meting(self):
        self.assertEqual(herstel.dekking(cache_dir=self.map.name), 1)
        L = pd.read_csv(self.tabel).set_index("biedzone")
        self.assertTrue(pd.isna(L.loc["XX", "capture_zon"]))
        self.assertAlmostEqual(L.loc["XX", "capture_zon_gemeten"], 3.5)
        self.assertTrue(pd.isna(L.loc["XX", "capture_bron"]))                  # leeg, zodat zon_proxy het gat ziet
        self.assertAlmostEqual(L.loc["YY", "capture_zon"], 0.9)                # elf van de twaalf maanden: blijft staan
        self.assertAlmostEqual(L.loc["ZZ", "capture_zon"], 0.8)                # geen bewaarde bestanden: niet aangeraakt
        self.assertEqual(herstel.dekking(cache_dir=self.map.name), 0)          # tweede keer verandert er niets meer


if __name__ == "__main__":
    unittest.main()
