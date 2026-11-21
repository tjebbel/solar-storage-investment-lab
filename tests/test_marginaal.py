import unittest

import numpy as np
import pandas as pd

from eti import marginaal as m


class TestMarginaal(unittest.TestCase):
    def test_uitstoot_factoren(self):
        idx = pd.date_range("2025-01-01", periods=3, freq="h")
        df = pd.DataFrame({"Fossil gas": [100.0, 200, 0], "Fossil hard coal": [0.0, 0, 100], "Solar": [50.0, 0, 0]}, index=idx)
        e, fos, totaal = m.uitstoot(df)
        self.assertAlmostEqual(e.iloc[0], 40.4)
        self.assertAlmostEqual(e.iloc[2], 85.1)
        self.assertEqual(list(fos), [100, 200, 100])

    def test_helling_gas(self):
        # alleen gas reageert: de marginale factor moet de gasfactor zijn
        idx = pd.date_range("2025-01-01", periods=24 * 400, freq="h")
        rng = np.random.default_rng(1)
        fos = pd.Series(1000 + rng.normal(0, 100, len(idx)), index=idx)
        e = fos * 0.404
        h = m.hellingen(e, fos)
        self.assertTrue(all(abs(v - 0.404) < 1e-6 for v in h.values() if not np.isnan(v)))

    def test_geen_fossiel(self):
        idx = pd.date_range("2025-01-01", periods=24 * 200, freq="h")
        df = pd.DataFrame({"Nuclear": 100.0, "Solar": 10.0}, index=idx)
        e, fos, _ = m.uitstoot(df)
        self.assertEqual(e.sum(), 0)
        self.assertTrue(all(np.isnan(v) for v in m.hellingen(e, fos).values()))


if __name__ == "__main__":
    unittest.main()
