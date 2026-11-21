import unittest

import numpy as np
import pandas as pd

from eti import batterij_realistisch as b


class TestStrategie(unittest.TestCase):
    def test_perfect_is_bovengrens(self):
        rng = np.random.default_rng(3)
        m = pd.DataFrame(rng.normal(80, 30, (50, 24)), index=pd.date_range("2025-01-01", periods=50).date)
        perfect = b.opbrengst(m, m)
        self.assertGreaterEqual(perfect, b.opbrengst(m, m.shift(1).dropna()))

    def test_twee_uur(self):
        m = pd.DataFrame([[10.0] * 22 + [100.0, 100.0]], index=pd.date_range("2025-01-01", periods=1).date)
        self.assertAlmostEqual(b.opbrengst(m, m), 200 * b.REND - 20)


if __name__ == "__main__":
    unittest.main()
