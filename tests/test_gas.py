"""Gasprijs: omrekening, voorlopige maanden, het maandmodel, de terugtoets en het verversen zonder netwerk."""
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import numpy as np
import pandas as pd

from eti import gas

SNAPSHOT = os.path.join(ROOT, gas.SNAPSHOT)


@unittest.skipUnless(os.path.exists(SNAPSHOT), "momentopname van de gasprijs ontbreekt")
class TestReeks(unittest.TestCase):
    def test_omrekening_en_voorlopige_maanden(self):
        g = gas.maandreeks(SNAPSHOT).set_index("periode")
        self.assertAlmostEqual(g.loc["2022-08", "eu_gas_eur_mwh"], 69.977 / 1.0129 / 0.29307107, places=6)       # de piek van de gascrisis: 236 euro
        self.assertTrue(200 < g.loc["2022-08", "eu_gas_eur_mwh"] < 260)
        self.assertFalse(g.loc["2026-09", "voorlopig"])
        for periode, (waarde, _) in gas.VOORLOPIG.items():
            if g.loc[periode, "voorlopig"]:                    # na verversen staat hier de echte waarde
                self.assertAlmostEqual(g.loc[periode, "eu_gas_eur_mwh"], waarde)
        self.assertTrue(g.index.is_monotonic_increasing and g.index.is_unique)
        self.assertFalse(g.eu_gas_eur_mwh.isna().any())


class TestModel(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(3)
        maanden = pd.period_range("2019-01", "2026-10", freq="M")
        gasprijs = rng.uniform(10, 120, len(maanden))
        seizoen = np.array([8, 6, 2, -2, -6, -8, -8, -6, -2, 2, 6, 8])[maanden.month - 1]
        self.nl = pd.DataFrame({"jaar": maanden.year, "maand": maanden.month, "eu_gas_eur_mwh": gasprijs, "gem_prijs": 20 + 1.8 * gasprijs + seizoen + rng.normal(0, 3, len(maanden))})

    def test_maandmodel_vindt_de_helling(self):
        b, X = gas.maandmodel(self.nl)
        self.assertAlmostEqual(b[1], 1.8, delta=0.05)
        self.assertEqual(X(self.nl).shape, (len(self.nl), 13))

    def test_terugtoets_met_gas_wint_van_vorig_jaar(self):
        t = gas.toets(self.nl)
        self.assertEqual(list(t.jaar), [2022, 2023, 2024, 2025, 2026])
        self.assertLess(np.abs(t.fout_met_gas_pct).mean(), 5)
        self.assertLess(np.abs(t.fout_met_gas_pct).mean(), np.abs(t.fout_vorig_jaar_pct).mean())

    def test_prognose_volgt_het_gaspad(self):
        pr = gas.prognose(self.nl, gas.toets(self.nl)).set_index("scenario")
        duur, goedkoop = pr.loc["gas blijft op het niveau van nu (87)"], pr.loc["gas terug naar begin 2026 (30)"]
        self.assertAlmostEqual(duur.stroom_2027_eur_mwh - goedkoop.stroom_2027_eur_mwh, 57 * pr.euro_stroom_per_euro_gas.iloc[0], places=6)
        self.assertTrue(duur.laag < duur.stroom_2027_eur_mwh < duur.hoog)
        terug = pr[pr.index.str.startswith("gasprijs die past")].iloc[0]
        self.assertAlmostEqual(terug.sokkel_eur_mwh + terug.euro_stroom_per_euro_gas * terug.gas_2027_eur_mwh, gas.DUITS_CAL27[0], places=6)

    def test_r2_binnen_een_zone(self):
        rng = np.random.default_rng(5)
        zone = pd.Series(np.repeat(list("abcde"), 8))
        x = pd.DataFrame({"x": rng.normal(size=40)})
        niveau = zone.map(dict(zip("abcde", (0, 50, 100, 150, 200))))
        self.assertGreater(gas.r2_binnen(niveau + 2 * x.x, x, zone), 0.999)          # het niveau per zone telt niet mee
        self.assertLess(gas.r2_binnen(niveau + pd.Series(rng.normal(size=40)), x, zone), 0.2)


class TestVerversen(unittest.TestCase):
    def test_zonder_netwerk_blijft_de_momentopname_staan(self):
        with tempfile.TemporaryDirectory() as map_:
            pad = os.path.join(map_, "gas.csv")
            with open(pad, "w", encoding="utf-8") as fh:
                fh.write("periode,eu_gas_usd_mmbtu,usd_per_eur,bron\n2026-01,11.987,1.1744,FRED\n")
            with mock.patch("urllib.request.urlopen", side_effect=OSError("geen netwerk")):
                self.assertFalse(gas.ververs(pad))
            self.assertEqual(len(pd.read_csv(pad)), 1)

    def test_met_netwerk_wordt_de_momentopname_bijgewerkt(self):
        antwoorden = iter(["observation_date,PNGASEUUSDM\n2017-12-01,7.0\n2026-09-01,25.494\n2026-10-01,28.98\n", "observation_date,EXUSEU\n2026-09-01,1.1505\n2026-10-01,1.1198\n"])

        class Antwoord(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with tempfile.TemporaryDirectory() as map_:
            pad = os.path.join(map_, "gas.csv")
            with mock.patch("urllib.request.urlopen", side_effect=lambda *a, **k: Antwoord(next(antwoorden).encode())):
                self.assertTrue(gas.ververs(pad))
            g = gas.maandreeks(pad).set_index("periode")
            self.assertNotIn("2017-12", g.index)
            self.assertFalse(g.loc["2026-10", "voorlopig"])                           # de echte waarde vervangt de voorlopige
            self.assertAlmostEqual(g.loc["2026-10", "eu_gas_eur_mwh"], 28.98 / 1.1198 / 0.29307107, places=6)


if __name__ == "__main__":
    unittest.main()
