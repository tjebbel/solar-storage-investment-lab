"""Tests voor het datawoordenboek: het schema wordt gebouwd en de controle vindt wat ze moet vinden."""
import os
import tempfile
import unittest

import pandas as pd

from eti import woordenboek as wb


class Valideer(unittest.TestCase):
    SCHEMA = {"properties": {"jaar": {"type": "number"}, "capture_zon": {"type": ["number", "null"], "minimum": 0, "maximum": 2},
                             "technologie": {"type": "string", "enum": ["zon", "wind"]}}, "required": ["jaar", "technologie"]}

    def test_goede_tabel_geeft_niets(self):
        df = pd.DataFrame({"jaar": [2024, 2025], "capture_zon": [0.6, None], "technologie": ["zon", "wind"]})
        self.assertEqual(wb.valideer(df, self.SCHEMA), [])

    def test_vindt_elke_soort_afwijking(self):
        df = pd.DataFrame({"jaar": [2024, None], "capture_zon": [3.5, -0.1], "technologie": ["zon", "kern"], "extra": [1, 2]})
        soorten = {f[0] for f in wb.valideer(df, self.SCHEMA)}
        self.assertEqual(soorten, {"nieuwe kolom", "lege waarden", "onder de ondergrens", "boven de bovengrens", "onbekende waarde"})
        self.assertIn(("kolom ontbreekt", "jaar", "staat wel in het schema"), wb.valideer(df.drop(columns="jaar"), self.SCHEMA))

    def test_verkeerd_type(self):
        df = pd.DataFrame({"jaar": ["twintig"], "capture_zon": [0.5], "technologie": ["zon"]})
        self.assertIn("verkeerd type", {f[0] for f in wb.valideer(df, self.SCHEMA)})


class Bouw(unittest.TestCase):
    def test_schema_uit_een_klein_profiel(self):
        with tempfile.TemporaryDirectory() as d:
            pd.DataFrame([{"dataset": "fact_land_jaar", "kolom": "capture_zon", "rijen": 10, "ontbreekt": 0, "ontbreekt_pct": 0.0, "uniek": 9, "type": "getal",
                           "min": 0.5, "max": 1.1, "mediaan": 0.8},
                          {"dataset": "fact_land_jaar", "kolom": "capture_bron", "rijen": 10, "ontbreekt": 2, "ontbreekt_pct": 20.0, "uniek": 2, "type": "tekst"},
                          {"dataset": "fact_land_jaar", "kolom": "onbekend", "rijen": 10, "ontbreekt": 0, "ontbreekt_pct": 0.0, "uniek": 3, "type": "getal",
                           "min": 1, "max": 3, "mediaan": 2}]).to_csv(os.path.join(d, "fact_profiel_DA.csv"), index=False)
            pd.DataFrame([{"dataset": "fact_land_jaar", "kolom": "capture_bron", "waarde": "opwek", "aantal": 6},
                          {"dataset": "fact_land_jaar", "kolom": "capture_bron", "waarde": "instraling", "aantal": 2}]).to_csv(os.path.join(d, "fact_waarden_DA.csv"), index=False)
            regels, schema, (beschreven, kolommen, tabellen) = wb.bouw(d)
        t = schema["$defs"]["fact_land_jaar"]
        self.assertEqual((beschreven, kolommen, tabellen), (2, 3, 1))
        self.assertEqual(t["properties"]["capture_zon"]["maximum"], 2)
        self.assertEqual(t["properties"]["capture_bron"]["enum"], ["opwek", "instraling", None])
        self.assertEqual(t["required"], ["capture_zon", "onbekend"])
        self.assertTrue(any("nog te beschrijven" in r for r in regels))


if __name__ == "__main__":
    unittest.main()
