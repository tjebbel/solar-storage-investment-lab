import unittest
from pathlib import Path
from eti import ppa_waardeketen as p


@unittest.skipUnless(Path("tableau/data/t1_zonejaar.csv").exists(), "t1 ontbreekt")
class TestPPAWaardeketen(unittest.TestCase):
    def test_marge_en_omrekening(self):
        w = p.waardeketen().set_index("Company")
        self.assertAlmostEqual(w.loc["LONGi", "Net margin %"], 100 * -6.42 / 70.347, places=6)
        self.assertAlmostEqual(w.loc["LONGi", "Revenue USD bn"], 70.347 / 6.85, places=6)
        self.assertTrue((w.loc[w.Group == "China", "Net margin %"].drop("Sungrow") < 0).all())

    def test_ppa_index_basis(self):
        q = p.ppa().set_index(["Index", "Period"]).loc[("P25 continental index", "Q3 2024"), "Index vs Q3 2024"]
        self.assertAlmostEqual(float(q), 1.0)

    def test_ppa_tegen_markt_teken(self):
        m = p.ppa_tegen_merchant().set_index("Country")
        for land, r in m.iterrows():
            self.assertAlmostEqual(r["PPA minus capture price"], r["PPA P25 Q4 2025 EUR/MWh"] - r["Solar capture price EUR/MWh"])


if __name__ == "__main__":
    unittest.main()
