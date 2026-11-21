import unittest

import pandas as pd

from eti import wereld_duck as wd


class TestWereldDuck(unittest.TestCase):
    def test_index_en_negatief(self):
        idx = pd.date_range("2025-01-01", periods=24 * 365, freq="h")
        p = pd.Series([0.0 if 11 <= t.hour < 15 else 100.0 for t in idx], index=idx)
        p.iloc[12] = -10
        prof, diep = wd.maten("Test", p)
        d = diep[0]
        self.assertLess(d["Midday index 11-15h"], 0.01)
        self.assertIsNone(d["Evening to midday ratio"])
        self.assertEqual(d["Negative hours"], 1)
        self.assertEqual(len(prof), 24)


if __name__ == "__main__":
    unittest.main()
