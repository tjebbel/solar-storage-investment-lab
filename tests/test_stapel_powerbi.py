"""Stapelmodel (FCR naast dagmarkt) en de toetsbestanden voor Power BI."""
import os
import sys
import tempfile
import unittest
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import numpy as np
import pandas as pd

from eti import powerbi_toets as pt, stapel

DATA = os.path.join(ROOT, "powerbi/data")


class TestStapel(unittest.TestCase):
    def setUp(self):
        self.map = tempfile.TemporaryDirectory()
        blokken = pd.date_range("2025-01-31 23:00", periods=6 * 6, freq="4h")                 # zes lokale dagen in de winter (UTC+1)
        prijs = np.tile([10.0, 10, 10, 10, 10, 10, 30, 30, 30, 30, 30, 30], 3)                   # dag 1 goedkoop, dag 2 duur, enzovoort
        pd.DataFrame({"vanaf_utc": blokken.strftime("%Y-%m-%d %H:%M:%S"), "prijs_eur_mw_uur": prijs}).iloc[:-2].to_csv(os.path.join(self.map.name, "fact_fcr_nl.csv"), index=False)
        dagen = pd.date_range("2025-02-01", periods=6).strftime("%Y-%m-%d")
        pd.DataFrame({"datum": dagen, "jaar": 2025, "a": 100.0, "b": [500.0, 300, 500, 300, 500, 300], "variant": "x", "groep": "B", "omzet": 0, "seizoen": "w", "weekdeel": "w"}).to_csv(
            os.path.join(self.map.name, "fact_abtest_dag_SA.csv"), index=False)

    def tearDown(self):
        self.map.cleanup()

    def test_fcr_per_lokale_dag_en_onvolledige_dag_valt_weg(self):
        f = stapel.fcr_per_dag(self.map.name)
        self.assertEqual(list(f.index), ["2025-02-01", "2025-02-02", "2025-02-03", "2025-02-04", "2025-02-05"])      # dag zes mist twee blokken
        self.assertAlmostEqual(f.loc["2025-02-01", "fcr"], 6 * 4 * 10.0)
        self.assertAlmostEqual(f.loc["2025-02-02", "fcr"], 6 * 4 * 30.0)

    def test_wisselen_kijkt_alleen_naar_gisteren(self):
        d = stapel.dagtabel(self.map.name).set_index("datum")
        self.assertEqual(list(d.keuze), ["bijsturen", "bijsturen", "fcr", "bijsturen", "fcr"])       # gisteren fcr 240 < 500, dan 720 > 300, ...
        self.assertAlmostEqual(d.loc["2025-02-03", "wissel"], 240.0)                                 # koos FCR op een goedkope FCR-dag: gisteren is geen garantie
        self.assertTrue((d.achteraf >= d.wissel).all())
        self.assertAlmostEqual(d.loc["2025-02-02", "half"], 0.5 * 720 + 0.5 * 300)

    def test_jaartabel(self):
        j = stapel.jaartabel(stapel.dagtabel(self.map.name)).set_index("sleutel")
        self.assertAlmostEqual(j.loc["dagmarkt", "omzet_per_mw_jaar"], 100.0 * 365)
        self.assertFalse(j.loc["dagmarkt", "haalt_8pct"])
        self.assertTrue(j.loc["bijsturen", "haalt_8pct"])
        self.assertAlmostEqual(j.loc["wissel", "aandeel_dagen_fcr"], 2 / 5)


class TestPowerBI(unittest.TestCase):
    def test_datumtabel_is_aaneengesloten_met_hele_jaren(self):
        d = pt.dim_datum(2024, 2026)
        self.assertEqual(len(d), 366 + 365 + 365)
        self.assertEqual((d.datum.iloc[0], d.datum.iloc[-1]), ("2024-01-01", "2026-12-31"))
        self.assertTrue(d.datum.is_unique)
        rij = d.set_index("datum")
        self.assertEqual(rij.loc["2025-04-26", "feestdag"], "Koningsdag")                     # 27 april 2025 is een zondag
        self.assertEqual(rij.loc["2026-04-27", "feestdag"], "Koningsdag")
        self.assertEqual(rij.loc["2026-04-05", "feestdag"], "Eerste paasdag")
        self.assertEqual((rij.loc["2026-01-01", "isojaar"], rij.loc["2026-01-01", "week"]), (2026, 1))
        self.assertEqual((rij.loc["2024-12-30", "isojaar"], rij.loc["2024-12-30", "week"]), (2025, 1))
        self.assertFalse(rij.loc["2026-12-25", "werkdag"])
        self.assertEqual(pt.pasen(2025), date(2025, 4, 20))

    def test_dax_bestand_noemt_alleen_bestaande_kolommen(self):
        tekst = pt.DAX.format(lcoe=pt.LCOE, krap=pt.KRAP, land=pt.LAND, jaar=pt.JAAR)
        self.assertEqual(tekst.count("("), tekst.count(")"))
        self.assertEqual(tekst.count("{"), tekst.count("}"))
        import re
        maten = set(re.findall(r"MEASURE (fact_\w+)\[([^\]]+)\]", tekst))
        self.assertGreaterEqual(len(maten), 9)
        for tabel, kolom in set(re.findall(r"(fact_\w+)\[(\w+)\]", tekst)) - maten:
            pad = os.path.join(DATA, tabel + ".csv")
            if os.path.exists(pad):
                self.assertIn(kolom, list(pd.read_csv(pad, nrows=0).columns), f"{tabel}[{kolom}]")

    @unittest.skipUnless(os.path.exists(os.path.join(DATA, "fact_land_maand.csv")), "fact_land_maand ontbreekt")
    def test_verwachte_waarden(self):
        v = pt.verwacht(DATA)
        self.assertTrue((v["Marge zon"].round(2) == (v["Capture-prijs zon"] - pt.LCOE).round(2)).all())
        self.assertTrue(((v["Prijs z-score"].abs() >= 3) == (v["Prijs signaal"] == "Schok")).all())
        self.assertEqual(set(v["Status zon"]) - {"Gedekt", "Krap", "Kosten niet gedekt"}, set())


if __name__ == "__main__":
    unittest.main()
