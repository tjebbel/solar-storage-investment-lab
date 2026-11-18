"""Run with: python -m unittest discover -s tests   (or: pytest)"""
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from eti import battery, data, esg, finance, market, warehouse, pipeline  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "data", "sample", "dayahead_sample.xml")


class TestData(unittest.TestCase):
    def test_synthetic_year_length(self):
        self.assertEqual(len(data.synthetic_year(2024)), 8784)   # leap year
        self.assertEqual(len(data.synthetic_year(2025)), 8760)

    def test_parse_entsoe_xml(self):
        pts = data.parse_entsoe_xml(open(SAMPLE, encoding="utf-8").read())
        self.assertEqual(len(pts), 4)
        self.assertEqual(pts[1][0].strftime("%H:%M"), "22:15")
        self.assertAlmostEqual(pts[3][1], -1.2)


class TestWarehouse(unittest.TestCase):
    def test_load_is_idempotent(self):
        db = warehouse.connect(":memory:")
        rows = data.synthetic_year(2024)[:48]
        self.assertEqual(warehouse.load(db, rows), 48)
        self.assertEqual(warehouse.load(db, rows), 48)
        n = db.execute("SELECT COUNT(*) FROM fact_generation").fetchone()[0]
        self.assertEqual(n, 48 * 4)
        db.close()

    def test_foreign_key_enforced(self):
        db = warehouse.connect(":memory:")
        with self.assertRaises(Exception):
            db.execute("INSERT INTO fact_generation VALUES ('2024-01-01T00:00Z', 'nuclear', 1.0)")
        db.close()


class TestMarket(unittest.TestCase):
    def test_capture_rate_flat_profile_is_one(self):
        self.assertAlmostEqual(market.capture_rate([10, 20, 30], [1, 1, 1]), 1.0)

    def test_capture_rate_skips_missing(self):
        self.assertAlmostEqual(market.capture_rate([10, None, 30], [1, 5, 1]), 1.0)

    def test_ols_exact(self):
        s, i, r2 = market.ols([0, 1, 2], [1, 3, 5])
        self.assertAlmostEqual(s, 2); self.assertAlmostEqual(i, 1); self.assertAlmostEqual(r2, 1)


class TestBattery(unittest.TestCase):
    def brute(self, prices, h, eff):
        blocks = [sum(prices[i:i + h]) / h for i in range(len(prices) - h + 1)]
        return max([0.0] + [(blocks[j] * eff - blocks[i]) * h
                            for i in range(len(blocks)) for j in range(i + h, len(blocks))])

    def test_linear_equals_brute_force(self):
        rng = random.Random(3)
        for _ in range(200):
            p = [rng.uniform(-20, 150) for _ in range(24)]
            self.assertAlmostEqual(battery.best_daily_spread(p, 2, 0.88)[0], self.brute(p, 2, 0.88))

    def test_example_day(self):
        gain, pair = battery.best_daily_spread([80, 70, 40, 10, -5, 20, 90, 150], 2, 0.88)
        self.assertAlmostEqual(gain, 206.2)
        self.assertEqual(pair, (3, 6))


class TestFinance(unittest.TestCase):
    def test_irr_npv(self):
        cf = [-1000, 300, 300, 300, 300, 300]
        self.assertAlmostEqual(finance.npv(0, cf), 500)
        self.assertAlmostEqual(finance.npv(finance.irr(cf), cf), 0, places=3)

    def test_irr_no_sign_change(self):
        with self.assertRaises(ValueError):
            finance.irr([100, 10, 10])          # never negative: no IRR

    def test_required_uplift_reaches_target(self):
        x = finance.required_uplift(1000, 50, 10, 10, 0.0, 0.08)
        cf = finance.project_cashflows(1000, 50, 10, 10)
        cf = [cf[0]] + [c + x for c in cf[1:]]
        self.assertAlmostEqual(finance.irr(cf), 0.08, places=5)

    def test_percentiles_ordered(self):
        sim = finance.monte_carlo_irr(10e6, 1.4e6, 3e5, 20, 0.15, n=300)
        self.assertLess(finance.percentile(sim, 10), finance.percentile(sim, 90))


class TestESG(unittest.TestCase):
    def test_hourly_vs_average(self):
        hourly, avg = esg.avoided_solar_tonnes([0, 10, 0], [500, 100, 500])
        self.assertAlmostEqual(hourly, 1.0)          # 10 MWh * 100 kg
        self.assertAlmostEqual(avg, 3.6666666, places=4)

    def test_battery_shift(self):
        t = esg.battery_shift_tonnes([[100, 100, 500, 500]], [(0, 2)], mw=1, hours=2, efficiency=1.0)
        self.assertAlmostEqual(t, 0.8)


class TestEndToEnd(unittest.TestCase):
    def test_pipeline_runs_and_writes_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            res = pipeline.run(os.path.join(d, "t.db"), os.path.join(d, "out"))
            self.assertTrue(os.path.exists(os.path.join(d, "out", "results.md")))
            self.assertTrue(os.path.exists(os.path.join(d, "out", "monthly_capture_rate.csv")))
            self.assertAlmostEqual(res["market"]["capture_rate_solar"], 0.789, places=3)
            self.assertEqual(res["market"]["negative_hours"], 156)
            self.assertLess(res["impact"]["solar_avoided_t_hourly"], res["impact"]["solar_avoided_t_yearly_avg"])


if __name__ == "__main__":
    unittest.main()


class TestScenarios(unittest.TestCase):
    def test_breakeven_gives_hurdle_irr(self):
        from eti import scenarios, finance
        c = scenarios.breakeven_capture(10e6, 1.5e6, 0.3e6, 25, 0.005, 0.79, 0.08)
        irr = finance.irr(finance.project_cashflows(10e6, 1.5e6 * c / 0.79, 0.3e6, 25, 0.005))
        self.assertAlmostEqual(irr, 0.08, places=4)

    def test_irr_increases_with_capture(self):
        from eti import scenarios
        r = scenarios.solar_irr_vs_capture(10e6, 1.5e6, 0.3e6, 25, 0.005, 0.79, [0.6, 0.8, 1.0])
        self.assertTrue(r[0.6] < r[0.8] < r[1.0])

    def test_tariff_effect_linear(self):
        from eti import scenarios
        self.assertEqual(scenarios.tariff_effect(100, 10, [0, 5]), {0: 100, 5: 0})


class TestScenarios2(unittest.TestCase):
    def test_curtailment_never_lowers_revenue(self):
        from eti import scenarios
        r = scenarios.curtailment([-10, 50, None], [5, 5, 5])
        self.assertEqual(r["revenue_curtailed"], 250)
        self.assertGreaterEqual(r["revenue_curtailed"], r["revenue_full"])

    def test_ppa_price_hits_target(self):
        from eti import scenarios, finance
        p = scenarios.ppa_price_for_irr(10e6, 20000, 3e5, 25, 0.005, 0.07)
        cf = finance.project_cashflows(10e6, p * 20000, 3e5, 25, 0.005)
        self.assertAlmostEqual(finance.irr(cf), 0.07, places=5)

    def test_equity_irr_above_project_irr_with_cheap_debt(self):
        from eti import scenarios, finance
        cf = finance.project_cashflows(10e6, 1.5e6, 3e5, 25, 0)
        e, d = scenarios.equity_irr(cf, 6e6, 0.05, 15)
        self.assertGreater(e, finance.irr(cf)); self.assertGreater(d, 1)


class TestLenses(unittest.TestCase):
    def test_passthrough_only_gas_hours(self):
        from eti import lenses
        self.assertEqual(lenses.carbon_passthrough([10, 100, None], 60, 0.4, 50), [10, 120, None])

    def test_fund_net_below_gross(self):
        from eti import lenses
        r = lenses.fund_cashflows(100, 4, 0.11, 6, 0.02, 0.2, 0.08, 10)
        self.assertLess(r["net_irr"], 0.11); self.assertLess(r["trough"], 0); self.assertGreater(r["tvpi"], 1)


class TestWorlds(unittest.TestCase):
    def test_tariff_lowers_battery_irr(self):
        from eti import lenses
        w = lenses.WORLDS["Huidig beleid"]
        a = lenses.world_result([50, 150] * 10, [1, 0] * 10, 100, 1, 10, 0, 30, 100, 2, 10, 0, w)
        b = lenses.world_result([50, 150] * 10, [1, 0] * 10, 100, 1, 10, 0, 30, 100, 2, 10, 0, w, tariff_cost=5)
        self.assertLess(b["battery_irr"], a["battery_irr"])


class TestRegions(unittest.TestCase):
    def test_tax_lowers_cashflows(self):
        from eti import regions, finance
        pre = finance.project_cashflows(100, 15, 3, 20, 0)
        post = regions.after_tax_cashflows(100, 15, 3, 20, 0, 0.25)
        self.assertLess(finance.irr(post), finance.irr(pre))

    def test_higher_wacc_higher_lcoe_and_finance_share(self):
        from eti import regions
        self.assertGreater(regions.lcoe(1e6, 3e4, 1500, 0.12, 25), regions.lcoe(1e6, 3e4, 1500, 0.05, 25))
        self.assertGreater(regions.finance_share(1e6, 3e4, 1500, 0.12, 25), regions.finance_share(1e6, 3e4, 1500, 0.05, 25))


class TestImprovements(unittest.TestCase):
    def test_naive_forecast_below_perfect(self):
        from eti import battery
        days = [[10, 10, 50, 90, 20, 10]] * 3 + [[90, 10, 10, 10, 50, 10]]
        perfect, _ = battery.yearly_arbitrage(days, 1, 1, 0.9)
        naive = battery.naive_forecast_arbitrage(days, 1, 1, 0.9)
        self.assertLessEqual(naive, perfect)

    def test_lifetime_grid_declines(self):
        from eti import regions
        self.assertLess(regions.lifetime_grid(300, 2025), 300)

    def test_blended_wacc(self):
        from eti import regions
        self.assertAlmostEqual(regions.blended_wacc(0.12, 0.2, 0.02), 0.10)
