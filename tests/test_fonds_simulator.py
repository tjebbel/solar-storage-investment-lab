import unittest

from eti import fonds_simulator as f


class TestFonds(unittest.TestCase):
    def test_prijs_gelijk_aan_lcoe_geeft_wacc(self):
        # verkoop tegen de LCOE zonder waardedaling: project-IRR = de WACC waarmee de LCOE is berekend
        self.assertAlmostEqual(f.irr_zon(60.0, 60.0, 0.0), f.WACC, places=4)

    def test_waardedaling_verlaagt_irr(self):
        self.assertLess(f.irr_zon(70.0, 60.0, 0.03), f.irr_zon(70.0, 60.0, 0.0))

    def test_batterij_verzadiging(self):
        self.assertLess(f.irr_batterij(80_000, 0.08, 1.0), f.irr_batterij(80_000, 0.0, 1.0))

    def test_fonds_hoog_rendement(self):
        # bij 15% project-IRR moet de netto fonds-IRR bestaan en lager zijn dan het project
        r = f.fonds(0.15)["net_irr"]
        self.assertTrue(0.05 < r < 0.15)

    def test_portefeuilles_tellen_op(self):
        for gew in f.PORTEFEUILLES.values():
            self.assertAlmostEqual(sum(gew.values()), 1.0)


if __name__ == "__main__":
    unittest.main()
