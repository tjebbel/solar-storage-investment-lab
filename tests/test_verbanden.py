import unittest

import pandas as pd

from eti import verbanden


class VerbandenTest(unittest.TestCase):
    def test_spearman_volgt_de_rangorde(self):
        self.assertAlmostEqual(verbanden.spearman([1, 2, 3, 4], [10, 20, 400, 8000]), 1.0)
        self.assertAlmostEqual(verbanden.spearman([1, 2, 3, 4], [9, 7, 5, 1]), -1.0)

    def test_ols_vindt_helling_en_r2(self):
        x = [0.0, 1.0, 2.0, 3.0, 4.0]
        b, se, r2 = verbanden.ols([1 + 2 * v for v in x], [x])
        self.assertAlmostEqual(b[0], 1.0)
        self.assertAlmostEqual(b[1], 2.0)
        self.assertAlmostEqual(r2, 1.0)

    def test_jaareffect_verklaart_gemeenschappelijke_daling(self):
        # twee landen, zelfde daling per jaar, verschillend zonaandeel: het jaar verklaart alles, het aandeel voegt niets toe
        p = pd.DataFrame({"iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"], "jaar": [2023, 2024, 2025] * 2,
                          "capture": [0.9, 0.7, 0.6, 0.9, 0.7, 0.6], "aandeel_pct": [5.0, 6.0, 9.0, 12.0, 15.0, 16.0]})
        uit = verbanden.paneel(p).set_index("specificatie")
        self.assertAlmostEqual(uit.loc["jaareffecten", "r2"], 1.0)
        self.assertLess(uit.loc["eigen zonaandeel", "r2"], 0.5)


if __name__ == "__main__":
    unittest.main()
