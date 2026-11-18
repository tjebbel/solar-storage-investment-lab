import json, os, unittest
from eti import nacht2


class TestParsers(unittest.TestCase):
    def test_installed(self):
        d = {"time": [2024, 2025], "production_types": [{"name": "Solar", "data": [20.1, 25.3]}]}
        self.assertEqual(nacht2.parse_installed(d), [(2024, "Solar", 20.1), (2025, "Solar", 25.3)])

    def test_cbet_quarter_hours(self):
        d = {"unix_seconds": [0, 900, 1800, 2700], "countries": [{"name": "Germany", "data": [1.0, 1.0, 1.0, None]}]}
        self.assertAlmostEqual(nacht2.parse_cbet(d)["Germany"], 0.75 / 1000)   # TWh, positief = import

    def test_openmeteo(self):
        d = {"hourly": {"time": ["2025-06-01T12:00"], "shortwave_radiation": [800], "wind_speed_100m": [20],
                        "temperature_2m": [18], "cloud_cover": [10]}}
        self.assertEqual(nacht2.parse_openmeteo(d), [("2025-06-01 12:00", 800, 20, 18, 10)])

    def test_aemo_to_utc_hours(self):
        txt = "REGION,SETTLEMENTDATE,TOTALDEMAND,RRP,PERIODTYPE\nSA1,2025/01/01 10:05:00,1000,50,TRADE\nSA1,2025/01/01 11:00:00,1000,70,TRADE\nSA1,2025/01/01 11:05:00,1000,-10,TRADE\n"
        self.assertEqual(nacht2.parse_aemo(txt), [("2025-01-01 00:00", 60.0), ("2025-01-01 01:00", -10.0)])

    def test_naive_forecast_daily_telt_op_tot_jaaromzet(self):
        from eti import battery
        days = [[10, 5, 30, 40], [12, 4, 20, 50], [50, 40, 5, 10], [8, 6, 35, 45]]
        per_dag = battery.naive_forecast_daily(days, 1, 0.9)
        self.assertEqual(len(per_dag), 3)
        self.assertEqual(per_dag[1], 0.0)        # plan van dag 2 verliest op dag 3 en wordt overgeslagen
        self.assertAlmostEqual(sum(per_dag) * 4 / 3, battery.naive_forecast_arbitrage(days, 1, 1, 0.9))

    def test_proxy_capture(self):
        self.assertAlmostEqual(nacht2.proxy_capture([10, 100], [1, 0]), 10 / 55)
        self.assertIsNone(nacht2.proxy_capture([10], [0]))
