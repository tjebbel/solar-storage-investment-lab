"""Offline tests for the live connectors, using fixtures shaped like the documented API."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from eti import live  # noqa: E402

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def load(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return json.load(f)


class TestLive(unittest.TestCase):
    def test_parse_prices_and_hourly_average(self):
        pts = live.parse_prices(load("ec_price.json"))
        self.assertEqual(len(pts), 8)                         # 15-minute values
        hourly = live.to_hourly(pts)
        self.assertEqual(len(hourly), 2)
        self.assertAlmostEqual(hourly[0][1], 83.0)            # mean of 80, 82, 84, 86
        self.assertAlmostEqual(hourly[1][1], -10.0)           # None values skipped

    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            live.parse_prices({"unix_seconds": [1, 2], "price": [1.0]})

    def test_technology_mapping(self):
        self.assertEqual(live.map_technology("Wind offshore"), "wind")
        self.assertEqual(live.map_technology("Fossil hard coal"), "coal")
        self.assertIsNone(live.map_technology("Load"))
        self.assertIsNone(live.map_technology("Renewable share of load"))
        self.assertIsNone(live.map_technology("Cross border electricity trading"))

    def test_generation_hourly_mwh(self):
        gen = live.generation_hourly(live.parse_generation(load("ec_power.json")))
        hours = sorted(gen)
        self.assertEqual(len(hours), 2)
        self.assertAlmostEqual(gen[hours[0]]["wind"], 1500.0)  # 1000 + 500 MW for one hour
        self.assertAlmostEqual(gen[hours[1]]["solar"], 500.0)
        self.assertAlmostEqual(gen[hours[1]]["gas"], 2000.0)   # missing value skipped

    def test_combine_rows_for_warehouse(self):
        rows = live.combine(live.to_hourly(live.parse_prices(load("ec_price.json"))),
                            live.generation_hourly(live.parse_generation(load("ec_power.json"))))
        self.assertEqual(len(rows), 2)
        ts, price, mix = rows[1]
        self.assertAlmostEqual(price, -10.0)
        self.assertIn("coal", mix)


if __name__ == "__main__":
    unittest.main()
