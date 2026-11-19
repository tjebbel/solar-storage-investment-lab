import unittest
from pathlib import Path
from eti import cbs_hernieuwbaar as c

@unittest.skipUnless(Path("data/extern/cbs/82610NED.csv").exists(), "CBS-selecties ontbreken")
class TestCBS(unittest.TestCase):
    def test_voorlopig_en_punt(self):
        d = c.lees("82610NED")
        self.assertTrue(d[d.Jaar == 2025]["Voorlopig"].all())
        self.assertTrue(d.filter(like="aantal").iloc[0].isna().all())  # '.' wordt NaN

    def test_zon_vollasturen_plausibel(self):
        s = c.stroom(); z = s[(s.Bron == "Zonnestroom") & (s.Jaar == 2025)]["Vollasturen"].iloc[0]
        self.assertTrue(800 < z < 1100)

    def test_marginale_factor_binnen_band(self):
        k = c.toetsen(c.vermeden(c.stroom()), impact="bestaat_niet.csv")
        ref = k[k.Toets.str.startswith("Marginale")]["Referentie"]
        self.assertTrue(ref.between(0.30, 0.50).all())

if __name__ == "__main__":
    unittest.main()
