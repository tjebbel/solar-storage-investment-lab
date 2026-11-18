"""Tests voor de kwaliteitsbewaking: elke controle op een klein voorbeeld waarvan de uitkomst vaststaat."""
import unittest
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from eti import kwaliteit as kw


def uren(n=2000, einde="2026-11-15 09:00"):
    t = pd.date_range(end=einde, periods=n, freq="h", tz="UTC")
    rng = np.random.default_rng(1)
    return pd.DataFrame({"timestamp_utc": t.strftime("%Y-%m-%d %H:%M:%S"), "prijs_eur_mwh": rng.normal(90, 20, n)})


class Controles(unittest.TestCase):
    def test_versheid_drie_niveaus(self):
        df = uren()
        for dagen, ernst, status in ((1, "info", "geslaagd"), (3, "waarschuwing", "gezakt"), (10, "kritiek", "gezakt")):
            nu = datetime(2026, 11, 15, 9, tzinfo=timezone.utc) + pd.Timedelta(days=dagen)
            b = kw.versheid("t", df, "timestamp_utc", (2, 4), nu)[0]
            self.assertEqual((b["ernst"], b["status"]), (ernst, status))

    def test_volume(self):
        df = uren(1000)
        self.assertEqual(kw.volume("t", df, None)[0]["status"], "geslaagd")
        self.assertEqual(kw.volume("t", df, {"rijen": 1005})[0]["status"], "geslaagd")
        self.assertEqual(kw.volume("t", df, {"rijen": 1200})[0]["ernst"], "kritiek")          # rijen verdwenen
        self.assertEqual(kw.volume("t", df, {"rijen": 500})[0]["ernst"], "waarschuwing")      # verdubbeld
        self.assertEqual(kw.volume("t", df.head(0), {"rijen": 5})[0]["ernst"], "kritiek")

    def test_psi_en_verschuiving(self):
        rng = np.random.default_rng(2)
        self.assertLess(kw.psi(rng.normal(0, 1, 5000), rng.normal(0, 1, 2000)), 0.05)
        self.assertGreater(kw.psi(rng.normal(0, 1, 5000), rng.normal(3, 1, 2000)), 1.0)
        df = uren()
        self.assertEqual(kw.verschuiving("t", df, "timestamp_utc", ["prijs_eur_mwh"])[0]["status"], "geslaagd")
        df.loc[df.index[-700:], "prijs_eur_mwh"] += 150                                        # prijsschok in de laatste maand
        b = kw.verschuiving("t", df, "timestamp_utc", ["prijs_eur_mwh"])[0]
        self.assertEqual((b["ernst"], b["status"]), ("waarschuwing", "gezakt"))                # signaal, geen stop
        self.assertIn("sterke verschuiving", b["toelichting"])

    def test_lege_waarden_sprong(self):
        df = pd.DataFrame({"a": [1, None, None, 4], "b": [1, 2, 3, 4]})
        self.assertEqual(kw.lege_waarden("t", df, {"leeg": {"a": 0.5, "b": 0.0}})[0]["status"], "geslaagd")
        b = kw.lege_waarden("t", df, {"leeg": {"a": 0.1, "b": 0.0}})[0]
        self.assertEqual((b["ernst"], b["status"]), ("waarschuwing", "gezakt"))

    def test_schema_en_bereik(self):
        schema = {"$defs": {"t": {"properties": {"jaar": {"type": "number"}, "capture_zon": {"type": "number", "minimum": 0, "maximum": 2}}, "required": ["jaar"]}}}
        goed = kw.schema_en_bereik("t", pd.DataFrame({"jaar": [2025], "capture_zon": [0.6]}), schema)
        self.assertTrue(all(b["status"] == "geslaagd" for b in goed))
        fout = kw.schema_en_bereik("t", pd.DataFrame({"capture_zon": [3.5], "nieuw": [1]}), schema)
        soorten = {(b["controle"], b["ernst"]) for b in fout if b["status"] == "gezakt"}
        self.assertEqual(soorten, {("schema", "kritiek"), ("schema", "waarschuwing"), ("bereik", "waarschuwing")})
        self.assertEqual(kw.schema_en_bereik("onbekend", pd.DataFrame(), schema)[0]["ernst"], "waarschuwing")

    def test_sleutel_en_verwijzing(self):
        df = pd.DataFrame({"land": ["NL", "NL", None], "jaar": [2025, 2025, 2024]})
        self.assertEqual(kw.sleutel("t", df, ["land", "jaar"])[0]["ernst"], "kritiek")
        self.assertEqual(kw.sleutel("t", df.head(1), ["land", "jaar"])[0]["status"], "geslaagd")
        tabellen = {"kind": pd.DataFrame({"land": ["NL", "XX"]}), "ouder": pd.DataFrame({"land": ["NL", "ES"]})}
        self.assertEqual(kw.verwijzing("kind", "land", "ouder", "land", tabellen)[0]["status"], "gezakt")
        self.assertEqual(kw.verwijzing("ouder", "land", "ouder", "land", tabellen)[0]["status"], "geslaagd")
        self.assertEqual(kw.verwijzing("kind", "land", "weg", "land", tabellen)[0]["status"], "gezakt")

    def test_samenvatting_zet_het_ergste_bovenaan(self):
        b = pd.DataFrame([kw.bevinding("volume", "a", "info", True, "ok"), kw.bevinding("schema", "b", "waarschuwing", False, "nieuwe kolom"),
                          kw.bevinding("versheid", "c", "kritiek", False, "tien dagen oud")])
        tekst, telling = kw.samenvatting(b)
        self.assertEqual(telling, {"kritiek": 1, "waarschuwing": 1})
        self.assertLess(tekst.index("[kritiek]"), tekst.index("[waarschuwing]"))


if __name__ == "__main__":
    unittest.main()
