import unittest
import pandas as pd
from eti import netcongestie as nc, vs_860m as vs


class TestNetcongestie(unittest.TestCase):
    def _v(self):
        k = dict(voedingsgebied_id=["A", "B", "C"], RNB=["Liander", "Enexis", "Stedin"], provincie=["NH", "NB", "ZH"],
                 aanwezige_transportcapaciteit_invoeding=[10, 50, 0], aanwezige_transportcapaciteit_afname=[20, 40, 0],
                 benodigde_transportcapaciteit_invoeding=[15, 10, 0], benodigde_transportcapaciteit_afname=[30, 20, 0],
                 wachtrij_invoeding=[5, 0, 0], wachtrij_afname=[10, 0, 0],
                 jaartal_opgelost_invoeding=[2029, 2099, None], jaartal_opgelost_afname=[2031, None, None])
        return pd.DataFrame(k)

    def test_lege_rij_weg_en_tekort(self):
        g, leeg = nc.gebieden(self._v())
        self.assertEqual(leeg, 1)
        self.assertEqual(list(g.tekort_afname_mw), [10, 0])
        self.assertAlmostEqual(g.verhouding_afname.iloc[0], 1.5)

    def test_2099_is_geen_datum(self):
        g, _ = nc.gebieden(self._v())
        self.assertTrue(pd.isna(g.jaar_opgelost_invoeding.iloc[1]))
        self.assertTrue(g.geen_datum_invoeding.iloc[1])

    def test_gemeente_aandelen(self):
        p = pd.DataFrame(dict(provincie=["U"] * 4, Gemeentenaam=["X"] * 4, afname=["3", "3", "0", "1"], opwek=["0"] * 4))
        m = nc.gemeenten(p)
        self.assertEqual(m["afname Tekort %"].iloc[0], 50.0)
        self.assertEqual(m["postcodes"].iloc[0], 4)


class TestVS860M(unittest.TestCase):
    def test_groepen(self):
        g = vs.groep(pd.Series(["Batteries", "Solar Photovoltaic", "Onshore Wind Turbine", "Petroleum Liquids"]))
        self.assertEqual(list(g), ["Batterij", "Zon", "Wind", "Overig"])


if __name__ == "__main__":
    unittest.main()
