"""Tests voor de statistische analyse (_SA) en de prognose: rekenfuncties op kleine, bekende voorbeelden."""
import unittest

import numpy as np
import pandas as pd

try:
    import scipy  # noqa: F401
    from eti import prognose, sa
    SCIPY = True
except ImportError:
    SCIPY = False


@unittest.skipUnless(SCIPY, "scipy ontbreekt")
class Hulp(unittest.TestCase):
    def test_holm_is_monotoon_en_begrensd(self):
        p = sa.holm([0.01, 0.04, 0.03, 0.5])
        self.assertAlmostEqual(p[0], 0.04)                 # kleinste p maal vier
        self.assertAlmostEqual(p[2], 0.09)                 # 0,03 maal drie
        self.assertAlmostEqual(p[1], 0.09)                 # 0,04 maal twee = 0,08, maar niet lager dan de vorige
        self.assertEqual(p[3], 0.5)

    def test_wilson_bevat_het_aandeel(self):
        lo, hi = sa.wilson(5, 20)
        self.assertTrue(0 < lo < 0.25 < hi < 1)
        self.assertTrue(np.isnan(sa.wilson(0, 0)[0]))

    def test_een_steekproef_ziet_ligging(self):
        rng = np.random.default_rng(1)
        hoog = sa.een_steekproef("x", rng.normal(0.10, 0.02, 40), 0.05, "h0", "h1")
        laag = sa.een_steekproef("x", rng.normal(0.00, 0.02, 40), 0.05, "h0", "h1")
        self.assertLess(hoog["p"], 0.001)
        self.assertGreater(laag["p"], 0.99)
        self.assertGreater(hoog["effectgrootte"], 0.9)

    def test_gepaard_richting(self):
        voor = np.linspace(0.8, 1.0, 20)
        r = sa.gepaard("x", voor, voor - 0.3 + np.linspace(-0.02, 0.02, 20), "h0", "h1")
        self.assertLess(r["p"], 0.001)
        self.assertAlmostEqual(r["schatting"], -0.3, places=6)


@unittest.skipUnless(SCIPY, "scipy ontbreekt")
class ABTest(unittest.TestCase):
    def test_vergelijk_en_conversie(self):
        rng = np.random.default_rng(2)
        r = sa.vergelijk(rng.normal(100, 20, 500), rng.normal(110, 20, 500), drempel=105)
        self.assertAlmostEqual(r["verschil"], 10, delta=3)
        self.assertLess(r["p"], 0.001)
        self.assertGreater(r["conversie_b"], r["conversie_a"])

    def test_onderscheidend_vermogen(self):
        groot, _ = sa.onderscheidend(1000, 1000, 0.3)
        klein, mde = sa.onderscheidend(50, 50, 0.1)
        self.assertGreater(groot, 0.99)
        self.assertLess(klein, 0.2)
        self.assertAlmostEqual(mde, 0.56, delta=0.01)       # bekende waarde: 2,8 gedeeld door wortel 25

    def test_proef_met_bekend_effect(self):
        dagen = pd.date_range("2023-01-01", periods=800, freq="D")
        rng = np.random.default_rng(3)
        a = rng.normal(150, 60, 800)
        dag = pd.DataFrame({"datum": dagen, "jaar": dagen.year, "a": a, "b": a + 40})
        tabel, _ = sa.ab_test(dag)
        totaal = tabel[tabel.onderdeel == "totaal"].iloc[0]
        self.assertAlmostEqual(totaal.verschil, 40, delta=15)
        gepaard = tabel[tabel.onderdeel.str.startswith("gepaard (")].iloc[0]
        self.assertAlmostEqual(gepaard.verschil, 40, places=6)
        self.assertGreater(tabel[tabel.onderdeel == "verdeling over de groepen"].p.iloc[0], 0.01)


@unittest.skipUnless(SCIPY, "scipy ontbreekt")
class Regressie(unittest.TestCase):
    def test_ols_vindt_coefficienten_terug(self):
        rng = np.random.default_rng(4)
        x1, x2 = rng.normal(size=300), rng.normal(size=300)
        y = 1.0 - 0.5 * x1 + 0.2 * x2 + rng.normal(scale=0.1, size=300)
        m = sa.ols(y, np.column_stack([np.ones(300), x1, x2]), np.repeat(np.arange(30), 10))
        self.assertAlmostEqual(m["b"][1], -0.5, delta=0.03)
        self.assertAlmostEqual(m["b"][2], 0.2, delta=0.03)
        self.assertGreater(m["r2"], 0.9)
        self.assertLess(m["p"][1], 0.001)

    def test_ontwerp_heeft_jaardummys(self):
        d = pd.DataFrame({"jaar": [2019, 2020, 2021], "a": [1.0, 2.0, 3.0]})
        X, namen = sa.ontwerp(d, ["a"])
        self.assertEqual(namen, ["constante", "a", "jaar_2020", "jaar_2021"])
        self.assertEqual(X.shape, (3, 4))


@unittest.skipUnless(SCIPY, "scipy ontbreekt")
class Cohorten(unittest.TestCase):
    def test_kaplan_meier(self):
        tabel, mediaan = sa.kaplan_meier([1, 2, 2, 3, 5, 5], [True, True, True, True, False, False])
        self.assertAlmostEqual(tabel.overleving.iloc[0], 5 / 6)
        self.assertAlmostEqual(tabel.overleving.iloc[1], 0.5)
        self.assertEqual(mediaan, 2.0)
        _, geen = sa.kaplan_meier([3, 4, 5], [False, False, False])
        self.assertTrue(np.isnan(geen))


@unittest.skipUnless(SCIPY, "scipy ontbreekt")
class Prognose(unittest.TestCase):
    def reeks(self, n=96, schok=0.0):
        t = np.arange(n)
        y = 100 + 10 * np.sin(2 * np.pi * t / 12)
        y[-1] += schok
        return y

    def test_seizoensnaief_herhaalt_vorig_jaar(self):
        y = self.reeks()
        np.testing.assert_allclose(prognose.seizoensnaief(y, 12), y[-12:])

    def test_terugkeer_dooft_de_schok(self):
        rng = np.random.default_rng(6)
        ruis = np.zeros(96)
        for t in range(1, 96):                                           # afwijkingen die blijven hangen (factor 0,8 per maand)
            ruis[t] = 0.8 * ruis[t - 1] + rng.normal(0, 3)
        basisreeks = self.reeks() + ruis
        geschokt = basisreeks.copy()
        geschokt[-1] += 80
        pad, basis = prognose.terugkeer(geschokt, 24), prognose.terugkeer(basisreeks, 24)
        self.assertGreater(pad[0] - basis[0], 20)                        # de schok werkt eerst door
        verschil = pad - basis
        self.assertTrue((np.diff(verschil) < 0).all())                    # en dooft daarna elke maand verder uit
        self.assertLess(np.abs(prognose.terugkeer(self.reeks(), 12) - self.reeks()[-12:]).max(), 3)   # zonder ruis: het maandpatroon

    def test_holt_winters_volgt_het_patroon(self):
        y = self.reeks()
        pad = prognose.holt_winters(y, 12)
        self.assertLess(np.abs(pad - y[-12:]).max(), 3)

    def test_interval_en_transformaties(self):
        f = prognose.interval(np.array([0.8, 0.9, 1.0, 1.1, 1.25]))
        self.assertAlmostEqual(f[0.5], 1.0)
        self.assertLess(f[0.80][0], 1.0)
        self.assertGreater(f[0.80][1], 1.0)
        for soort in ("log", "wortel", "geen"):
            np.testing.assert_allclose(prognose.terug(prognose.heen(np.array([4.0, 9.0]), soort), soort), [4.0, 9.0])

    def test_kies_geeft_fouten_per_model(self):
        rng = np.random.default_rng(5)
        y = self.reeks() + rng.normal(0, 2, 96)
        beste, tabel, vs, echt = prognose.kies(y, "log")
        self.assertIn(beste, prognose.MODELLEN)
        self.assertEqual(set(tabel), set(prognose.MODELLEN))
        self.assertEqual(vs.shape, echt.shape)
        self.assertLess(tabel[beste]["mape"], 0.05)


if __name__ == "__main__":
    unittest.main()
