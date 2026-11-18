"""Tests voor de data-analyse (_DA): alleen de rekenfuncties, zonder de grote tabellen."""
import unittest

import numpy as np
import pandas as pd

from eti import da

try:
    import sklearn  # noqa: F401
    SKLEARN = True
except ImportError:
    SKLEARN = False


class Verdeling(unittest.TestCase):
    def test_normaal_en_scheef(self):
        rng = np.random.default_rng(1)
        self.assertEqual(da.verdeling(pd.Series(rng.normal(size=2000))), "ongeveer normaal")
        self.assertIn("scheef naar rechts", da.verdeling(pd.Series(rng.exponential(size=2000))))

    def test_constant_en_tweetoppig(self):
        self.assertEqual(da.verdeling(pd.Series([3.0] * 20)), "constant of te weinig waarden")
        rng = np.random.default_rng(2)
        twee = pd.Series(np.concatenate([rng.normal(-4, 1, 500), rng.normal(4, 1, 500)]))
        self.assertEqual(da.verdeling(twee), "mogelijk tweetoppig")


class Verbanden(unittest.TestCase):
    def test_rang_is_spearman(self):
        a = pd.Series([1, 2, 3, 4, 5.0])
        self.assertAlmostEqual(da.rang(a, a ** 3), 1.0)
        self.assertAlmostEqual(da.rang(a, -a), -1.0)

    def test_vif_ziet_dubbelganger(self):
        rng = np.random.default_rng(3)
        x = rng.normal(size=300)
        df = pd.DataFrame({"a": x, "b": x + rng.normal(scale=0.05, size=300), "c": rng.normal(size=300)})
        v = da.vif(df)
        self.assertGreater(v["a"], 10)
        self.assertLess(v["c"], 1.5)

    def test_eta2(self):
        groep = pd.Series(["x"] * 50 + ["y"] * 50)
        self.assertAlmostEqual(da.eta2(groep, pd.Series([0.0] * 50 + [1.0] * 50)), 1.0)
        rng = np.random.default_rng(4)
        self.assertLess(da.eta2(groep, pd.Series(rng.normal(size=100))), 0.1)


class Segmenten(unittest.TestCase):
    def rij(self, capture, negatief, spreiding):
        return pd.Series({"capture_zon": capture, "negatieve_uren": negatief, "dagspreiding": spreiding})

    def test_regels_in_volgorde(self):
        self.assertEqual(da.regelsegment(self.rij(0.55, 400, 150)), "Zonverzadigd")      # verzadiging gaat voor
        self.assertEqual(da.regelsegment(self.rij(0.62, 400, 150)), "Batterijmarkt")
        self.assertEqual(da.regelsegment(self.rij(0.70, 200, 40)), "Vlakke prijzen")
        self.assertEqual(da.regelsegment(self.rij(0.85, 50, 80)), "Zon houdt waarde")
        self.assertEqual(da.regelsegment(self.rij(0.65, 250, 100)), "Middenveld")

    def test_clusternamen_zijn_uniek(self):
        centra = pd.DataFrame({"capture_zon": [0.72, 0.62, 0.83, 0.55], "dagspreiding": [47, 150, 76, 105],
                               "negatieve_uren": [260, 230, 0, 440]})
        namen = da.clusternamen(centra)
        self.assertEqual(len(set(namen)), 4)
        self.assertEqual(namen[0], "Waterkracht dempt de dag")
        self.assertEqual(namen[3], "Zonverzadigd met veel negatieve uren")

    @unittest.skipUnless(SKLEARN, "scikit-learn ontbreekt")
    def test_clusters_vindt_twee_groepen(self):
        rng = np.random.default_rng(5)
        rijen = []
        for i in range(30):
            laag = i < 12
            rijen.append({"biedzone": f"Z{i}", "jaar": 2025, **{k: rng.normal(0 if laag else 8, 1) for k in da.CLUSTERKOLOMMEN}})
        lab, tabel, centra, _ = da.clusters(pd.DataFrame(rijen), herhalingen=5)
        self.assertEqual(int(tabel[tabel.gekozen].k.iloc[0]), 2)
        self.assertEqual(sorted(lab.value_counts().tolist()), [12, 18])


class Uitschieters(unittest.TestCase):
    def test_rekenfout_wordt_leeg_en_gemeld(self):
        n = 40
        p = pd.DataFrame({"biedzone": [f"Z{i}" for i in range(n)], "land": "x", "jaar": 2021, "deeljaar": False,
                          "capture_uit_opwek": True, "capture_bron": "opwek", "capture_zon": [0.8] * (n - 1) + [3.5],
                          "gem_prijs": 80.0, "negatieve_uren": 10.0})
        lijst, effect, uit = da.uitschieters(p)
        fout = lijst[lijst.kolom == "capture_zon"]
        self.assertEqual(len(fout), 1)
        self.assertEqual(fout.categorie.iloc[0], "invoer- of rekenfout")
        self.assertTrue(np.isnan(uit.capture_zon.iloc[-1]))
        self.assertEqual(len(da.schoon(uit)), n)


if __name__ == "__main__":
    unittest.main()
