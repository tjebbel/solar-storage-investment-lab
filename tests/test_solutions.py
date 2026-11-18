import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from exercises import solutions as s  # noqa: E402


class TestSolutions(unittest.TestCase):
    def test_units(self):
        self.assertEqual(s.kw_to_kwh(2000, 15), 500)
        self.assertAlmostEqual(s.capacity_factor(20000, 20), 0.1142, places=4)

    def test_merit_order(self):
        plants = [("solar", 3000, 0), ("wind", 4000, 0), ("nuclear", 500, 10), ("gas", 6000, 90), ("coal", 1500, 70)]
        self.assertEqual(s.merit_order_price(plants, 6000), (0, "wind"))
        self.assertEqual(s.merit_order_price(plants, 9000), (70, "coal"))
        self.assertEqual(s.merit_order_price(plants, 12000), (90, "gas"))

    def test_capture_and_ppa(self):
        self.assertAlmostEqual(s.capture_price([100, 20, 100], [0, 10, 0]), 20)
        self.assertEqual(s.ppa_settlement(40, 60, 1000), 20000)
        self.assertEqual(s.ppa_settlement(90, 60, 1000), -30000)

    def test_finance(self):
        self.assertEqual(s.simple_payback(10e6, 1.1e6), 10e6 / 1.1e6)
        self.assertAlmostEqual(s.real_rate(0.07, 0.025), 0.04390, places=5)
        self.assertAlmostEqual(s.irr_of([-100, 110]), 0.10, places=6)

    def test_private_markets(self):
        jc = s.j_curve(100, [0.3, 0.3, 0.2, 0.1, 0.0, 0.0], [0, 0.05, 0.2, 0.5, 0.6, 0.5])
        self.assertEqual(jc, [-30.0, -55.0, -55.0, -15.0, 45.0, 95.0])
        self.assertAlmostEqual(s.tvpi(60, 90, 100), 1.5)
        self.assertEqual(s.fund_of_funds_exposure(8, 25, 0.1), 180)

    def test_cfe_and_datacenter(self):
        cons = [10, 10, 10, 10]; clean = [0, 20, 20, 0]
        self.assertEqual(s.annual_match(cons, clean), 1.0)
        self.assertEqual(s.hourly_match(cons, clean), 0.5)
        self.assertEqual(s.datacenter_energy(100, 1.2), 1_051_200)
        self.assertEqual(s.grid_tariff_effect(60, 10, 300, 20), (360000, 240000))


if __name__ == "__main__":
    unittest.main()
