"""Tests voor de ML-pijplijn en het losse analysescript: kenmerken zonder lek, tijdsplitsing en invoercontrole."""
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

try:
    import sklearn  # noqa: F401
    from eti import analyse_script, ml_pijplijn as ml
    SKLEARN = True
except ImportError:
    SKLEARN = False


def paneel(zones=12, jaren=range(2019, 2027)):
    rng = np.random.default_rng(1)
    rijen = []
    for z in range(zones):
        niveau = rng.uniform(0.5, 2.0)
        for j in jaren:
            rijen.append({"biedzone": f"Z{z}", "land": f"Z{z}", "regio": "A" if z % 2 else "B", "jaar": j, "deeljaar": j == 2026,
                          "batterij_per_mw": 40_000 * niveau * (1 + 0.1 * (j - 2019)) * rng.uniform(0.9, 1.1), "dagspreiding": 100 * niveau, "gem_prijs": 80.0 + j - 2019,
                          "capture_zon": 0.9 - 0.04 * (j - 2019), "negatieve_uren": 50.0 * (j - 2018), "voorspel_ratio": 0.75, "aandeel_zon_pct": 5.0 + z,
                          "aandeel_wind_pct": 10.0, "aandeel_kern_pct": 0.0, "aandeel_gas_pct": 20.0, "aandeel_waterkracht_pct": 5.0, "vraag_twh": 50.0 + z})
    return pd.DataFrame(rijen)


@unittest.skipUnless(SKLEARN, "scikit-learn ontbreekt")
class Kenmerken(unittest.TestCase):
    def test_doel_is_de_verhouding_van_volgend_jaar(self):
        k = ml.kenmerken(paneel())
        z = k[k.biedzone == "Z3"].set_index("jaar")
        self.assertAlmostEqual(z.loc[2022, ml.DOEL], z.loc[2023, "verhouding"])           # geen lek: het doel komt uit t+1
        self.assertAlmostEqual(z.loc[2022, ml.VERANDERING], z.loc[2023, "verhouding"] - z.loc[2022, "verhouding"])
        self.assertTrue(np.isnan(z.loc[2026, ml.DOEL]))                                    # laatste jaar: nog geen doel
        self.assertNotIn(2019, z.index)                                                    # eerste jaar valt weg: geen groei bekend
        self.assertAlmostEqual(k[k.jaar == 2023].verhouding.median(), 1.0)

    def test_splitsing_op_tijd(self):
        tr, te, vooruit, nieuw = ml.splits(ml.kenmerken(paneel()))
        self.assertEqual(sorted(tr.doeljaar.unique()), [2021, 2022, 2023, 2024])
        self.assertEqual(list(te.doeljaar.unique()), [2025])                               # laatste hele jaar apart
        self.assertEqual(list(vooruit.doeljaar.unique()), [2026])                          # onvolledig jaar: alleen een blik vooruit
        self.assertEqual(list(nieuw.jaar.unique()), [2026])
        self.assertLess(tr.jaar.max(), te.jaar.min() + 1)

    def test_pijplijn_leert_en_voorspelt(self):
        from sklearn.linear_model import Ridge
        k = ml.kenmerken(paneel())
        tr, te, _, _ = ml.splits(k)
        model = ml.pijplijn(Ridge(alpha=1.0)).fit(tr[ml.GETALLEN + ml.CATEGORIE], tr[ml.VERANDERING])
        fout = ml.maten(te[ml.DOEL], te.verhouding + model.predict(te[ml.GETALLEN + ml.CATEGORIE]))
        self.assertLess(fout["rmse"], 0.3)
        self.assertEqual(ml.maten([1, 2, 3], [1, 2, 3]), {"rmse": 0.0, "mae": 0.0, "r2": 1.0})

    def test_voorspel_weigert_onvolledige_invoer(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            json.dump({"kenmerken": ["verhouding", "regio"]}, open(os.path.join(d, ml.META), "w"))
            with self.assertRaises(ValueError):
                ml.voorspel(pd.DataFrame({"verhouding": [1.0]}), d)


@unittest.skipUnless(SKLEARN, "scikit-learn ontbreekt")
class Script(unittest.TestCase):
    def test_ontbrekende_kolom_stopt_met_een_duidelijke_fout(self):
        with tempfile.TemporaryDirectory() as d:
            pd.DataFrame({"land": ["x"], "jaar": [2025]}).to_csv(os.path.join(d, "fact_land_jaar.csv"), index=False)
            with self.assertRaises(analyse_script.DataFout) as fout:
                analyse_script.laad(d)
            self.assertIn("kolommen ontbreken", str(fout.exception))
            self.assertEqual(analyse_script.main(d, os.path.join(d, "uit")), 1)

    def test_getalnotatie(self):
        self.assertEqual(analyse_script.nl(7192.4, 0), "7.192")
        self.assertEqual(analyse_script.nl(-0.4), "-0,40")


if __name__ == "__main__":
    unittest.main()


class ScriptAlsProgramma(unittest.TestCase):
    """Het script hoort te werken zoals het in de kop staat: `python3 src/eti/analyse_script.py`. Dan staat src/eti vooraan
    in het zoekpad en mag eti/numbers.py de standaardmodule numbers niet verdringen (numpy heeft die nodig)."""

    def test_start_als_los_script(self):
        import subprocess
        import sys
        hoofdmap = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if not os.path.exists(os.path.join(hoofdmap, "powerbi/data/fact_land_jaar.csv")):
            self.skipTest("brontabellen ontbreken")
        try:
            import scipy, seaborn, sklearn  # noqa: F401
        except ImportError:
            self.skipTest("scipy, seaborn of scikit-learn ontbreekt")
        with tempfile.TemporaryDirectory() as uit:
            klaar = subprocess.run([sys.executable, os.path.join("src", "eti", "analyse_script.py"), os.path.join("powerbi", "data"), uit], cwd=hoofdmap, capture_output=True, text=True, timeout=300)
            self.assertEqual(klaar.returncode, 0, klaar.stderr[-600:])
            self.assertNotIn("attempted relative import", klaar.stderr)
            self.assertTrue(any(f.endswith(".png") for f in os.listdir(uit)))
