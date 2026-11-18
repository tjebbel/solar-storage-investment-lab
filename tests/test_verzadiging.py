"""Dagtabel voor Texas en Californie en de verzadigingscurve per GW."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
import numpy as np
import pandas as pd

from eti import vs_dag

try:
    import scipy  # noqa: F401
    from eti import verzadiging_gw as vz
except ImportError:
    vz = None


class TestDagtabel(unittest.TestCase):
    def test_per_uur_middelt_kwartieren_en_slaat_rommel_over(self):
        uit = vs_dag.per_uur([("2025-01-01 00:00", "10"), ("2025-01-01 00:15", 20.0), ("2025-01-01 01:00", None), ("2025-01-01 02:00", "x")])
        self.assertEqual(uit, {"2025-01-01 00:00": 15.0})

    def test_dagmaten(self):
        P = [10.0] * 10 + [0.0, -5.0] + [10.0] * 6 + [60.0, 40.0] + [10.0] * 4               # dal om 10 en 11 uur, piek om 18 en 19 uur
        mix = [{"SUN": 100.0 if 8 <= u <= 15 else 0.0, "NG": 400.0, "BAT": 50.0 if u == 18 else (-30.0 if u == 11 else 0.0)} for u in range(24)]
        m = dict(zip(vs_dag.KOP[2:], vs_dag.dagmaten(P, mix)))
        self.assertAlmostEqual(m["gem_prijs_eur"], sum(P) / 24)
        self.assertAlmostEqual(m["spreiding_2u"], 50.0 - (-2.5))
        self.assertAlmostEqual(m["piekpremie"] + m["daldiepte"], m["spreiding_2u"])
        self.assertEqual((m["uur_piek"], m["uur_dal"], m["negatieve_uren"]), (18, 11, 1))
        self.assertAlmostEqual(m["batterij_achteraf_per_mw"], (50.0 * 0.88 - (-2.5)) * 2)
        self.assertEqual((m["zon_mwh"], m["zon_piek_mw"], m["bat_ontladen_max_mw"], m["bat_laden_max_mw"], m["opwek_uren"]), (800.0, 100.0, 50.0, 30.0, 24))
        self.assertAlmostEqual(m["bat_aandeel_piekuur"], 50.0 / 450.0)                       # laden telt niet mee als opwek

    def test_dag_zonder_opwek_en_onvolledige_dag(self):
        P = list(range(24))
        leeg = dict(zip(vs_dag.KOP[2:], vs_dag.dagmaten([float(p) for p in P], [{}] * 24)))
        self.assertEqual(leeg["opwek_uren"], 0)
        self.assertIsNone(leeg["zon_mwh"])
        half = dict(zip(vs_dag.KOP[2:], vs_dag.dagmaten([float(p) for p in P], [{"NG": 100.0}] * 12 + [{}] * 12)))
        self.assertEqual(half["opwek_uren"], 12)


@unittest.skipIf(vz is None, "scipy niet geinstalleerd")
class TestVerzadiging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(7)
        dagen = pd.date_range("2021-01-01", "2025-12-31")
        delen = []
        for markt, helling in zip(vz.KORT, (-0.10, -0.06)):
            vloot = np.linspace(0.2, 12.0, len(dagen))
            zon, gas, last = rng.uniform(0.02, 0.3, len(dagen)), rng.uniform(2, 6, len(dagen)), rng.uniform(0.8, 1.2, len(dagen))
            seizoen = 0.3 * np.sin(2 * np.pi * dagen.dayofyear / 365)
            omzet = np.exp(4.0 + helling * vloot + 0.2 * np.log(zon) + 0.3 * np.log(gas) + 1.5 * np.log(last) + seizoen + rng.normal(0, 0.4, len(dagen)))
            delen.append(pd.DataFrame({"markt": markt, "datum": dagen, "vloot_gw": vloot, "vloot_mw": vloot * 1000, "batterij_achteraf_per_mw": omzet,
                                       "batterij_plan_per_mw": omzet * 0.9, "ln_zon": np.log(zon), "ln_gas": np.log(gas), "ln_last": np.log(last), "schok": False}))
        cls.d = pd.concat(delen, ignore_index=True)
        cls.d["jaar"], cls.d["maand"] = cls.d.datum.dt.year, cls.d.datum.dt.month

    def test_helling_per_gw_wordt_teruggevonden(self):
        for markt, echt in zip(vz.KORT, (-0.10, -0.06)):
            m = vz.schat(self.d, markt)
            i = m["namen"].index("vloot_gw")
            self.assertAlmostEqual(m["b"][i], echt, delta=0.015)
            self.assertLess(m["p"][i], 0.001)

    def test_curve_gaat_door_het_anker_en_daalt(self):
        basis = {markt: vz.schat(self.d, markt) for markt in vz.KORT}
        krv, punten = vz.curve(self.d, basis)
        for markt in vz.KORT:
            c = krv[krv.markt == markt].sort_values("vloot_gw")
            self.assertEqual(int(c.anker.sum()), 1)
            self.assertTrue((c.omzet_per_mw_jaar.diff().dropna() < 0).all())
            self.assertTrue(((c.laag <= c.omzet_per_mw_jaar + 1e-6) & (c.omzet_per_mw_jaar <= c.hoog + 1e-6)).all())
            self.assertTrue(c[c.vloot_gw > c[c.anker].vloot_gw.iloc[0]].buiten_waarneming.all())
        self.assertGreater(len(punten), 20)

    def test_onvolledige_dagen_tellen_niet_mee(self):
        pad = os.path.join(ROOT, "powerbi/data/fact_vs_dag.csv")
        if not (os.path.exists(pad) and os.path.exists(os.path.join(ROOT, "powerbi/data/fact_gas_henryhub.csv"))):
            self.skipTest("fact_vs_dag of fact_gas_henryhub ontbreekt: eerst eti.vs_dag draaien")
        d = vz.laad(os.path.join(ROOT, "powerbi/data"))
        self.assertTrue(d[d.opwek_uren < 24].opwek_mwh.isna().all())
        self.assertGreater(d.vloot_gw.max(), 5)


if __name__ == "__main__":
    unittest.main()
