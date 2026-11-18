"""Zonprofiel: de klok van de instraling, de capture rate en het afschakelen bij negatieve prijzen."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import numpy as np
import pandas as pd

from eti import nacht2, zonprofiel as zp

DATA = os.path.join(ROOT, "powerbi/data")


class TestKlok(unittest.TestCase):
    def test_straling_naar_het_begin_van_het_uur(self):
        rijen = [("2025-06-01 12:00", 800.0, 5.0, 20.0, 10), ("2025-01-01 00:00", 0.0, 5.0, 2.0, 90)]
        self.assertEqual(nacht2.straling_per_beginuur(rijen), {"2025-06-01 11:00": 800.0, "2024-12-31 23:00": 0.0})

    def test_uitgelijnd_profiel_geeft_de_echte_capture_rate(self):
        """Zon met een piek om 12 uur, prijs laag rond de middag. De straling komt een uur te laat gestempeld binnen."""
        uur = np.arange(24)
        zon = np.clip(np.cos((uur - 12) / 6 * np.pi / 2), 0, None)                 # opwek in het uur dat op `uur` begint
        prijs = [100 - 60 * z for z in zon]
        echt = nacht2.proxy_capture(prijs, list(zon))
        rijen = [(f"2025-06-01 {u + 1:02d}:00" if u < 23 else "2025-06-02 00:00", float(z), 0, 0, 0) for u, z in zip(uur, zon)]      # eindstempel
        sleutels = [f"2025-06-01 {u:02d}:00" for u in uur]
        uitgelijnd = nacht2.straling_per_beginuur(rijen)
        verschoven = {t: r for t, r, *_ in rijen}
        self.assertAlmostEqual(nacht2.proxy_capture(prijs, [uitgelijnd.get(k) for k in sleutels]), echt)
        self.assertNotAlmostEqual(nacht2.proxy_capture(prijs, [verschoven.get(k) for k in sleutels]), echt, places=3)


class TestAfschakelen(unittest.TestCase):
    def reeks(self, factor):
        rng = np.random.default_rng(11)
        n = 2000
        instraling = rng.uniform(300, 900, n)
        prijs = rng.normal(20, 40, n)
        zon = instraling * 0.5 * np.where(prijs < 0, factor, 1.0)
        return pd.DataFrame({"instraling": instraling, "prijs_eur_mwh": prijs, "solar_mw": zon, "maand": 6})

    def test_parken_die_doordraaien_en_parken_die_afschakelen(self):
        self.assertAlmostEqual(zp.afschakelen(self.reeks(1.0))[1], 1.0, places=6)
        uren, verhouding = zp.afschakelen(self.reeks(0.5))
        self.assertGreater(uren, 100)
        self.assertTrue(0.5 < verhouding < 0.65)               # de noemer bevat ook de afgeschakelde uren, dus iets boven 0,5

    def test_te_weinig_negatieve_uren_geeft_geen_oordeel(self):
        t = self.reeks(1.0)
        t["prijs_eur_mwh"] = t.prijs_eur_mwh.abs()
        self.assertTrue(np.isnan(zp.afschakelen(t)[1]))

    def test_capture_weegt_naar_opwek(self):
        prijs, zon = pd.Series([10.0, 30.0]), pd.Series([3.0, 1.0])
        self.assertAlmostEqual(zp.capture(prijs, zon), (10 * 3 + 30 * 1) / 4 / 20)


@unittest.skipUnless(all(os.path.exists(os.path.join(DATA, f)) for f in ("fact_nl_uur_alle_jaren.csv", "fact_weer_uur.csv", "fact_ember_opwek_jaar.csv")), "brontabellen ontbreken")
class TestOpDeData(unittest.TestCase):
    def test_vorm_klopt_niveau_niet(self):
        t = zp.toets(DATA).set_index("jaar")
        vol = t[t.uren >= 8700]
        self.assertTrue((vol.dekking < 0.1).all())                                  # de reeks telt maar een paar procent van Nederland
        self.assertTrue((vol.correlatie_uur > vol.correlatie_uur_stempel).all())    # uitgelijnd past in elk jaar beter
        self.assertTrue((vol.correlatie_dag > 0.8).all())
        self.assertLess(vol.loc[2020:2022, "verschil_capture"].abs().max(), 0.03)   # voor het afschakelen begon: bijna gelijk


if __name__ == "__main__":
    unittest.main()
