"""Tests voor de vervolgonderzoeken van 18 november 2026: bronnen, segmenten, batterij, schokjaar, benchmark en DAX-vergelijking."""
import os
import sqlite3
import tempfile
import unittest

import numpy as np
import pandas as pd

from eti import tableau_export, batterij_irr, bronnen_toets, powerbi_toets, schokjaar, segment_gevoeligheid, sql_benchmark, sql_run


def rec(rijen):
    return pd.DataFrame(rijen, columns=["iso3", "jaar", "a_pct", "b_pct", "zones", "verhouding", "categorie", "zon_twh"])


class Bronnen(unittest.TestCase):
    def setUp(self):
        r = []
        for j in range(2019, 2026):
            r.append(("LAG", j, 7.0, 10.0, 1, 0.7, "structureel lager in A", 5.0))      # A mist 30%, elk jaar
            r.append(("GAT", j, 0.2, 10.0, 1, 0.02, "dekkingsgat in A", 8.0))           # A meet bijna niets
            r.append(("GEL", j, 10.0 + (j % 2), 10.0, 1, 1.0 + 0.1 * (j % 2), "sluit aan", 3.0))
        self.v = rec(r)

    def test_regime_en_ontbrekend_deel(self):
        land = bronnen_toets.per_land(self.v).set_index("iso3")
        self.assertEqual(land.loc["LAG", "regime"], "structureel lager in A")
        self.assertAlmostEqual(land.loc["LAG", "geschat_ontbrekend_aandeel_zon"], 0.3)
        self.assertAlmostEqual(land.loc["LAG", "geschat_ontbrekend_twh"], 1.5)
        self.assertEqual(land.loc["GAT", "regime"], "te weinig bruikbare jaren")

    def test_gat_telt_niet_mee_in_het_verschil(self):
        j = bronnen_toets.per_jaar(self.v).iloc[0]
        self.assertLess(j.verschil_alle_pct, j.verschil_zonder_gat_pct)
        self.assertEqual(j.dekkingsgaten, 1)

    def test_correctie_buiten_steekproef(self):
        t = bronnen_toets.toets_buiten_steekproef(self.v).set_index("groep")
        self.assertAlmostEqual(t.loc["structureel lager in A", "mediane_fout_met_correctie"], 0.0)


class Reconciliatie(unittest.TestCase):
    def test_sql_indeling(self):
        """De nieuwe 05 op een kleine database: gat, aansluiting binnen de relatieve tolerantie, structureel lager."""
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE stg_land_jaar (iso3, jaar, aandeel_zon_energycharts)")
        con.execute("CREATE TABLE stg_mix (iso3, jaar, aandeel_zon_pct)")
        con.execute("CREATE TABLE raw_dim_land (iso3, continent)")
        for iso, a, b in (("GAT", 0.001, 10.0), ("REL", 0.205, 19.0), ("LAG", 0.07, 10.0)):
            con.execute("INSERT INTO raw_dim_land VALUES (?, 'Europe')", (iso,))
            for j in range(2019, 2024):
                con.execute("INSERT INTO stg_land_jaar VALUES (?, ?, ?)", (iso, j, a))
                con.execute("INSERT INTO stg_mix VALUES (?, ?, ?)", (iso, j, b))
        p = dict(sql_run.PARAMETERS)
        for stap in sql_run.volgorde(sql_run.stappen(open(os.path.join("sql", "05_reconciliatie.sql"), encoding="utf-8").read())):
            sql_run.voer_uit(con, stap, p)
        c = dict(con.execute("SELECT iso3, categorie FROM rec_vergelijk WHERE jaar = 2020").fetchall())
        self.assertEqual(c, {"GAT": "dekkingsgat in A", "REL": "sluit aan", "LAG": "structureel lager in A"})


class Segmenten(unittest.TestCase):
    def test_regel_en_volgorde(self):
        z = pd.DataFrame({"capture_zon": [0.55, 0.55, 0.9, 0.7, np.nan], "negatieve_uren": [400, 100, 0, 0, 0], "dagspreiding": [150, 150, 50, 90, 90]})
        s = segment_gevoeligheid.segment(z, segment_gevoeligheid.BASIS)
        self.assertEqual(list(s), ["Zonverzadigd", "Batterijmarkt", "Vlakke prijzen", "Middenveld", "Middenveld"])

    def test_drempel_op_de_grens_wisselt(self):
        z = pd.DataFrame({"biedzone": ["X"], "land": ["X"], "regio": ["R"], "jaar": [2025], "capture_zon": [0.70], "negatieve_uren": [0], "dagspreiding": [121]})
        b = segment_gevoeligheid.segment(z, segment_gevoeligheid.BASIS)
        m = segment_gevoeligheid.monte_carlo(z, b, n=200)
        self.assertTrue(m.grensgeval.iloc[0])


class Batterij(unittest.TestCase):
    def test_dag_optimum(self):
        p = [10, 10, 100, 100] + [50] * 20
        self.assertAlmostEqual(batterij_irr.dag_optimum(p, 2, eff=1.0), 180.0)                 # 2 MWh laden op 10, ontladen op 100
        self.assertAlmostEqual(batterij_irr.dag_optimum([100, 10] * 12, 2, eff=1.0), 180.0)    # cyclusgrens: 2 MWh ontladen
        self.assertEqual(batterij_irr.dag_optimum([50] * 24, 4), 0.0)

    def test_meer_cycli_kortere_levensduur(self):
        _, l1 = batterij_irr.irr(250, 1.0, 90_000, 0)
        _, l2 = batterij_irr.irr(250, 2.0, 90_000, 0)
        self.assertEqual((l1, l2), (15, 8))

    def test_breakeven_haalt_het_doel(self):
        k = batterij_irr.breakeven(1.0, 90_000, 0)
        self.assertGreaterEqual(batterij_irr.irr(k, 1.0, 90_000, 0)[0], 0.08 - 1e-6)


class Schokjaar(unittest.TestCase):
    def test_splitsing_telt_op(self):
        rij = []
        for j, g in ((2025, 30.0), (2026, 50.0)):
            for m in range(1, 11):
                rij.append({"biedzone": "Z", "jaar": j, "maand": m, "gem_prijs": 2 * g + 5 * (j == 2026), "gas": g, "zon": 10.0, "wind": 20.0})
        z = schokjaar.splits(pd.DataFrame(rij), {"gas": 2.0, "zon": 0.0, "wind": 0.0}).iloc[0]
        self.assertAlmostEqual(z.door_gas, 40.0)
        self.assertAlmostEqual(z.rest, 5.0)
        self.assertAlmostEqual(z.door_gas + z.door_zon + z.door_wind + z.rest, z.prijsstijging)


class Benchmark(unittest.TestCase):
    def test_logboek_lezen_zonder_opwarmronde(self):
        blok = "(30 rows affected)\n SQL Server Execution Times:\n   CPU time = 1 ms,  elapsed time = {t} ms.\n"
        tekst = "Microsoft SQL Server 2022\n" + "".join(f"== ronde {i}\n" + blok.format(t=1000 + i) + blok.format(t=5) + blok.format(t=1) for i in range(3))
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as fh:
            fh.write(tekst)
        t = sql_benchmark.tsql_tijden(fh.name).set_index("query")
        self.assertEqual(t.loc["traag", "herhalingen"], 2)
        self.assertEqual(t.loc["traag", "mediaan_ms"], 1001.5)
        os.unlink(fh.name)


class DaxVergelijking(unittest.TestCase):
    def test_vergelijk_vindt_afwijking(self):
        with tempfile.TemporaryDirectory() as d:
            v = pd.DataFrame({"land": ["NL", "NL"], "jaar": [2026, 2026], "maand": [1, 2], "Gem prijs": [10.0, 20.0], "Status zon": ["Gedekt", "Gedekt"]})
            v.to_csv(os.path.join(d, "v.csv"), index=False)
            pd.DataFrame({"fact_land_maand[maand]": [1, 2], "[Gem prijs]": [10.004, 21.0], "[Status zon]": ["Gedekt", "Gedekt"]}).to_csv(os.path.join(d, "e.csv"), index=False)
            u = powerbi_toets.vergelijk(os.path.join(d, "e.csv"), os.path.join(d, "v.csv"))
            self.assertEqual(int(u.klopt.sum()), 3)


class Tableau(unittest.TestCase):
    def test_bestanden_en_nederland_2025(self):
        with tempfile.TemporaryDirectory() as d:
            tab = tableau_export.main(uit=d)
            self.assertEqual(sorted(os.listdir(d)), [f"{n}.csv" for n in sorted(tab)])
            nl = pd.read_csv(os.path.join(d, "t1_zonejaar.csv")).query("Zone == 'NL' and Jaar == 2025").iloc[0]
            self.assertAlmostEqual(nl["Capture rate zon"], 0.6153, places=3)
            self.assertEqual(nl["Segment zekerheid"], "grensgeval")
            s = pd.read_csv(os.path.join(d, "t4_schokjaar.csv"))
            per_zone = s.groupby("Zone").agg(som=("Euro per MWh", "sum"), totaal=("Prijsstijging totaal", "first"))
            self.assertTrue(np.allclose(per_zone.som, per_zone.totaal, atol=1e-3))


if __name__ == "__main__":
    unittest.main()
