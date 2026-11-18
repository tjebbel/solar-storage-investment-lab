import unittest

from eti import wereld

EIA = """ERCOT Hourly Day-Ahead Locational Marginal Prices ($/megawatt) for Hubs
Hourly day-ahead locational marginal prices for ERCOT
Source: EIA collected from ERCOT
UTC Timestamp (Interval Ending),Local Timestamp Central Time (Interval Beginning),Local Timestamp Central Time (Interval Ending),Local Date,Hour Number,Bus average LMP,Houston LMP,Hub average LMP
2025-01-01 07:00:00,2025-01-01 00:00:00,2025-01-01 01:00:00,2025-01-01,1,23.0,22.87,23.07
2025-01-01 08:00:00,2025-01-01 01:00:00,2025-01-01 02:00:00,2025-01-01,2,21.11,20.93,
2025-01-01 09:00:00,2025-01-01 02:00:00,2025-01-01 03:00:00,2025-01-01,3,20.0,19.5,-3.5
"""


class VsEiaTest(unittest.TestCase):
    def test_uur_begint_een_uur_voor_het_einde_en_lege_cellen_vallen_weg(self):
        self.assertEqual(wereld.parse_eia_lmp(EIA, "Hub average LMP"), [("2025-01-01 06:00", 23.07), ("2025-01-01 08:00", -3.5)])

    def test_onbekende_kolom_geeft_een_fout(self):
        with self.assertRaises(KeyError):
            wereld.parse_eia_lmp(EIA, "West LMP")

    def test_eia_wint_tot_de_grens_en_oasis_vult_de_rest(self):
        eia = [("2024-12-31 22:00", 10.0), ("2025-01-01 00:00", 11.0)]
        oasis = [("2024-12-31 22:00", 99.0), ("2024-12-31 23:00", 12.0), ("2025-01-01 00:00", 13.0)]
        self.assertEqual(wereld.voeg_samen(eia, oasis, grens="2025-01-01"),
                         [("2024-12-31 22:00", 10.0), ("2024-12-31 23:00", 12.0), ("2025-01-01 00:00", 13.0)])

    def test_weerbestand_per_markt(self):
        self.assertEqual(wereld.weernaam("VS Californie (CAISO)"), "VS")          # bestaande bestanden blijven bruikbaar
        self.assertEqual(wereld.weernaam("VS Texas (ERCOT)"), "VS_Texas")         # Texas deelt de instraling van Californie niet
        self.assertEqual(wereld.weernaam("Japan (systeemprijs)"), "Japan")


if __name__ == "__main__":
    unittest.main()
