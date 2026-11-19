import unittest
from pathlib import Path
from eti import dashboard1_revisie as r


@unittest.skipUnless(Path("tableau/data/t1_zonejaar.csv").exists(), "t1 ontbreekt")
class TestRevisie(unittest.TestCase):
    def test_kpi_vijf_per_jaar_en_pijl(self):
        k = r.kpi()
        self.assertTrue((k.groupby("Jaar").size() == 5).all())
        self.assertTrue(k[k.Verschil > 0].Pijl.eq("▲").all())

    def test_rangorde_top_en_bodem(self):
        j = r.rangorde(); j = j[j.Jaar == 2025]
        self.assertGreaterEqual((j.Groep == "Top 5").sum(), 4)
        self.assertGreaterEqual((j.Groep == "Bodem 5").sum(), 4)
        self.assertEqual((j.Zone == "NL").sum(), 1)

    def test_alle_scenarios_leesbaar(self):
        b = r.batterij()
        self.assertFalse(b["Scenario leesbaar"].eq(b["Scenario"]).any())

    def test_top_tien_plus_overige(self):
        self.assertEqual(r.schok_top().Zone.nunique(), 11)


if __name__ == "__main__":
    unittest.main()
