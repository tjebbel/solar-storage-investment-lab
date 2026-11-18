import unittest

from eti import finance, herijk, volledige_case as vc


class VolledigeCaseTest(unittest.TestCase):
    def test_zonder_netkosten_en_daling_gelijk_aan_het_basismodel(self):
        capex = vc.CAPEX_KW * 1000 * herijk.MW
        basis = finance.project_cashflows(capex, 100_000 * herijk.MW, capex * herijk.OPEX_SH, herijk.LIFE, herijk.DEG)
        for a, b in zip(vc.kasstromen(100_000, 0.0), basis):
            self.assertAlmostEqual(a, b)
        self.assertAlmostEqual(vc.irr(100_000, 0.0), herijk.irr(100_000, vc.CAPEX_KW * 1000 / herijk.H))

    def test_netkosten_verlagen_elk_jaar_met_hetzelfde_bedrag(self):
        zonder, met = vc.kasstromen(200_000, 0.0), vc.kasstromen(200_000, 57_000.0)
        self.assertEqual(zonder[0], met[0])
        for a, b in zip(zonder[1:], met[1:]):
            self.assertAlmostEqual(a - b, 57_000.0 * herijk.MW)

    def test_daling_stopt_na_vijf_jaar(self):
        k = vc.kasstromen(100_000, 0.0, daling=0.10)
        kosten = vc.CAPEX_KW * 1000 * herijk.MW * herijk.OPEX_SH
        omzet = [x + kosten for x in k[1:]]
        self.assertAlmostEqual(omzet[1] / omzet[0], 0.90 * (1 - herijk.DEG))
        self.assertAlmostEqual(omzet[7] / omzet[6], 1 - herijk.DEG)          # jaar 8 op jaar 7: alleen nog degradatie

    def test_transportrecht_verlaagt_netkosten_en_omzet(self):
        omzet = vc.met_transportrecht(vc.STAPEL)
        saldo = (omzet - vc.NET_TDTR) - (vc.STAPEL - vc.NET_VAST)
        self.assertAlmostEqual(saldo, sum(vc.TDTR_SALDO) / 2)
        self.assertLess(omzet, vc.STAPEL)

    def test_tabel_ordent_de_gevallen(self):
        t = vc.tabel(87_000.0).set_index(["inkomsten", "netaansluiting"])
        eigen = "Dagmarkt met bijsturen (eigen model)"
        self.assertGreater(t.loc[(eigen, "geen netkosten, zoals in de memo"), "irr"], 0)
        self.assertTrue(t.loc[(eigen, "vast transportrecht"), "irr"] != t.loc[(eigen, "vast transportrecht"), "irr"])   # geen terugverdientijd
        vast = t.loc[("Volledige stapeling (benchmark)", "vast transportrecht"), "irr"]
        recht = t.loc[("Volledige stapeling (benchmark)", "tijdsafhankelijk transportrecht"), "irr"]
        self.assertGreater(recht, vast)


if __name__ == "__main__":
    unittest.main()
