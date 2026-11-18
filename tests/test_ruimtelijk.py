import unittest

import numpy as np
import pandas as pd

from eti import ruimtelijk, verbanden


class RuimtelijkTest(unittest.TestCase):
    def test_gewichten_zijn_symmetrisch_en_tellen_op_tot_een(self):
        ntc = pd.DataFrame({"scenario": "Reference", "jaar": 2024, "van": ["NL", "NL", "NL"], "naar": ["DE", "BE", "NW"],
                            "ntc_heen_mw": [4000.0, 1000.0, 500.0], "ntc_terug_mw": [2000.0, 1000.0, 500.0]})
        g = ruimtelijk.gewichten(ntc).set_index(["iso3", "buur"])
        self.assertAlmostEqual(g.loc[("NLD", "DEU"), "gewicht"], 0.75)      # 3000 van de 4000 MW; het knooppunt NW valt weg
        self.assertAlmostEqual(g.loc[("NLD", "BEL"), "gewicht"], 0.25)
        self.assertAlmostEqual(g.loc[("DEU", "NLD"), "gewicht"], 1.0)

    def test_buuraandeel_is_het_gewogen_gemiddelde_van_de_buren_met_een_cijfer(self):
        gew = pd.DataFrame({"iso3": ["NLD"] * 3, "buur": ["DEU", "BEL", "GBR"], "mw": [3000.0, 1000.0, 1000.0]})
        aandeel = pd.DataFrame({"iso3": ["DEU", "BEL"], "jaar": [2025, 2025], "aandeel_pct": [16.0, 8.0]})
        b = ruimtelijk.buuraandeel(gew, aandeel)
        self.assertAlmostEqual(float(b.buur_pct.iloc[0]), (3000 * 16 + 1000 * 8) / 4000)

    def test_cluster_geeft_dezelfde_coefficienten_als_gewone_kleinste_kwadraten(self):
        rng = np.random.default_rng(3)
        x = rng.normal(size=60)
        groep = np.repeat(np.arange(12), 5)
        y = 1 + 2 * x + rng.normal(size=12)[groep]                 # fout per groep: gewone standaardfout is te klein
        b, se, r2 = ruimtelijk.ols_cluster(y, [x], groep)
        b0, se0, r20 = verbanden.ols(y, [x])
        self.assertTrue(np.allclose(b, b0))
        self.assertAlmostEqual(r2, r20)
        self.assertTrue(np.isfinite(se).all() and (se > 0).all())

    def test_paneel_vindt_het_effect_van_de_buren(self):
        rijen = []
        rng = np.random.default_rng(4)
        for i, land in enumerate(["AAA", "BBB", "CCC", "DDD", "EEE", "FFF"]):
            for jaar in range(2019, 2026):
                eigen, buur = rng.uniform(0, 20), rng.uniform(0, 20)
                rijen.append((land, jaar, 1 - 0.01 * eigen - 0.02 * buur + 0.01 * i, eigen, buur))
        p = pd.DataFrame(rijen, columns=["iso3", "jaar", "capture", "aandeel_pct", "buur_pct"])
        uit = ruimtelijk.paneel(p).set_index("specificatie")
        rij = uit.loc["eigen + buren + land- en jaareffecten"]
        self.assertAlmostEqual(rij.coef_eigen, -0.01)
        self.assertAlmostEqual(rij.coef_buren, -0.02)


if __name__ == "__main__":
    unittest.main()
