"""Tests voor eti.voorspelmodel (dashboard 30): geen lek uit het testjaar, ridge-oplossing klopt, tabellen zijn consistent."""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from eti import voorspelmodel as v


def _uren(n=24 * 400, seed=1):
    r = np.random.default_rng(seed)
    i = pd.date_range("2022-01-01", periods=n, freq="h")
    load = 10000 + 2000 * np.sin(2 * np.pi * i.hour / 24) + r.normal(0, 200, n)
    zon = np.clip(4000 * np.sin(np.pi * (i.hour - 6) / 12), 0, None)
    wind = 3000 + r.normal(0, 800, n)
    prijs = 20 + 0.008 * (load - zon - wind) + r.normal(0, 3, n)
    return pd.DataFrame({"Price": prijs, "Load": load, "Solar": zon, "Wind onshore": wind, "Residual load": load - zon - wind}, index=i)


class TestVoorspelmodel(unittest.TestCase):
    def test_kenmerken_gebruiken_alleen_het_verleden(self):
        df = _uren()
        x = v.kenmerken(df)
        t = x.index[500]
        self.assertAlmostEqual(x.loc[t, "Price yesterday"], df.Price.loc[t - pd.Timedelta(hours=24)])
        self.assertAlmostEqual(x.loc[t, "Price last week"], df.Price.loc[t - pd.Timedelta(hours=168)])
        gisteren = df.Price[df.index.date == (t - pd.Timedelta(days=1)).date()].mean()
        self.assertAlmostEqual(x.loc[t, "Mean yesterday"], gisteren)

    def test_ridge_vindt_lineair_verband(self):
        x = v.kenmerken(_uren())
        tr, te = x.iloc[: 24 * 300], x.iloc[24 * 300:]
        X = v.matrix(tr); mod = v.fit(X, tr["Price"])
        pred = v.predict(mod, v.matrix(te, X.columns))
        mae = np.abs(te["Price"].to_numpy() - pred).mean()
        naief = (te["Price"] - te["Price yesterday"]).abs().mean()
        self.assertLess(mae, naief)
        self.assertLess(mae, 4.0)  # ruis is 3 EUR/MWh

    def test_matrix_zonder_exogeen(self):
        x = v.kenmerken(_uren())
        self.assertNotIn("Wind", v.matrix(x, exo=False).columns)
        self.assertIn("Wind", v.matrix(x).columns)

    def test_tabel_consistent(self):
        p = Path("tableau/data_en/t73_forecast_model.csv")
        if not p.exists():
            self.skipTest("t73 nog niet gemaakt")
        t = pd.read_csv(p)
        self.assertTrue((t["Year"] >= 2023).all())
        self.assertTrue((t["Battery model EUR/MW"] <= t["Battery perfect EUR/MW"] + 1e-6).all())
        self.assertTrue((t["MAE model EUR/MWh"] > 0).all())


if __name__ == "__main__":
    unittest.main()
