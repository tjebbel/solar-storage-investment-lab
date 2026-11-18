import unittest

import numpy as np
import pandas as pd

from eti import onbalansregel as ob


def kwartieren(n, start="2025-03-03 00:00"):
    return pd.date_range(start, periods=n, freq="15min", tz="UTC")


class OnbalansregelTest(unittest.TestCase):
    def test_signaal_kent_alleen_het_verleden(self):
        rng = np.random.default_rng(1)
        df = pd.DataFrame({"tekort": rng.normal(60, 40, 400), "overschot": rng.normal(50, 40, 400)}, index=kwartieren(400))
        laad, ontlaad = ob.signalen_kwantiel(df, vertraging=1, venster=96)
        later = df.copy()
        later.iloc[300:] = 9999.0                      # de toekomst vanaf kwartier 300 verandert
        laad2, ontlaad2 = ob.signalen_kwantiel(later, vertraging=1, venster=96)
        self.assertTrue((laad[:301] == laad2[:301]).all())      # kwartier 300 kijkt naar 299 en eerder
        self.assertTrue((ontlaad[:301] == ontlaad2[:301]).all())
        self.assertFalse(laad[:96].any() or ontlaad[:96].any())  # zonder een dag aan historie geen signaal

    def test_cycluslimiet_en_lading(self):
        n = 64
        koop, verkoop = np.full(n, 10.0), np.full(n, 100.0)
        laad = np.array([True] * 16 + [False] * 16 + [True] * 16 + [False] * 16)
        ontlaad = ~laad
        dagen = np.zeros(n, dtype=int)
        kas, stappen = ob.simuleer(koop, verkoop, laad, ontlaad, dagen, max_cycli=1.0)
        self.assertEqual(stappen.sum(), ob.NIVEAUS)                              # een volle ontlading, niet meer
        kas2, stappen2 = ob.simuleer(koop, verkoop, laad, ontlaad, dagen, max_cycli=2.0)
        self.assertEqual(stappen2.sum(), 2 * ob.NIVEAUS)
        self.assertAlmostEqual(kas2.sum(), 2 * (8 * 0.25 * 0.88 * 100 - 8 * 0.25 * 10))

    def test_lege_batterij_ontlaadt_niet(self):
        n = 20
        kas, stappen = ob.simuleer(np.full(n, 10.0), np.full(n, 100.0), np.zeros(n, bool), np.ones(n, bool), np.zeros(n, int))
        self.assertEqual(stappen.sum(), 0)
        self.assertEqual(kas.sum(), 0.0)

    def test_perfect_is_bovengrens(self):
        prijs = np.array([10.0] * 8 + [50.0] * 80 + [100.0] * 8)
        self.assertAlmostEqual(ob.perfect_dag(prijs, prijs, max_cycli=1.0), 8 * 0.25 * 0.88 * 100 - 8 * 0.25 * 10)
        rng = np.random.default_rng(2)
        koop, verkoop = rng.normal(70, 50, 96), rng.normal(50, 50, 96)
        laad, ontlaad = rng.random(96) < 0.3, rng.random(96) < 0.3
        kas, _ = ob.simuleer(koop, verkoop, laad, ontlaad, np.zeros(96, int), max_cycli=1.0)
        self.assertLessEqual(kas.sum(), ob.perfect_dag(koop, verkoop, max_cycli=1.0) + 1e-9)

    def _dag(self):
        df = pd.DataFrame({"tekort": 80.0, "overschot": 40.0, "dagmarkt": np.repeat(np.arange(24, dtype=float) * 5, 4)},
                          index=kwartieren(96))
        schema = np.zeros(96, dtype=int)
        schema[8:16], schema[72:80] = -1, 1             # laden in uur 2 en 3, ontladen in uur 18 en 19
        return df, schema

    def test_zonder_signaal_volgt_de_batterij_het_dagmarktplan(self):
        df, schema = self._dag()
        niets = np.zeros(96, dtype=bool)
        kas_da, kas_ob, stappen = ob.simuleer_gecombineerd(df, schema, niets, niets)
        verwacht = 0.25 * 0.88 * df.dagmarkt.values[72:80].sum() - 0.25 * df.dagmarkt.values[8:16].sum()
        self.assertAlmostEqual(kas_da.sum(), verwacht)
        self.assertEqual(kas_ob.sum(), 0.0)
        self.assertEqual(stappen.sum(), 8)

    def test_afwijking_rekent_af_tegen_de_onbalansprijs(self):
        df, _ = self._dag()
        laad, ontlaad = np.zeros(96, dtype=bool), np.zeros(96, dtype=bool)
        laad[0:8], ontlaad[20:28] = True, True
        kas_da, kas_ob, stappen = ob.simuleer_gecombineerd(df, np.zeros(96, dtype=int), laad, ontlaad)
        self.assertEqual(kas_da.sum(), 0.0)
        self.assertAlmostEqual(kas_ob[0:8].sum(), -8 * 0.25 * 80.0)             # laden kost de tekortprijs
        self.assertAlmostEqual(kas_ob[20:28].sum(), 8 * 0.25 * 0.88 * 40.0)     # ontladen levert de overschotprijs op
        self.assertEqual(stappen.sum(), 8)

    def test_voorwaarts_kiest_de_beste_van_het_jaar_ervoor(self):
        uitkomst = {"a": {2023: {"omzet_per_mw": 10.0}, 2024: {"omzet_per_mw": 5.0}},
                    "b": {2023: {"omzet_per_mw": 20.0}, 2024: {"omzet_per_mw": 1.0}}}
        self.assertEqual(ob.voorwaarts(uitkomst, [2023, 2024, 2025], "a"), {2023: "a", 2024: "b", 2025: "a"})

    def test_jaarcijfers(self):
        dagen = pd.date_range("2025-01-01", periods=4, freq="D").date
        dag = pd.DataFrame({"kas": [100.0, -20.0, 60.0, 60.0], "stappen": [8, 0, 4, 4], "geldig": 96}, index=dagen)
        j = ob.jaarcijfers(dag, 2025)
        self.assertAlmostEqual(j["omzet_per_mw"], 50.0 * 365)
        self.assertAlmostEqual(j["cycli_per_dag"], 0.5)
        self.assertAlmostEqual(j["aandeel_dagen_met_verlies"], 0.25)
        self.assertIsNone(ob.jaarcijfers(dag, 2024))


if __name__ == "__main__":
    unittest.main()
