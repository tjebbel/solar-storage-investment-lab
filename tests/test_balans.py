import unittest

import pandas as pd

from eti import balans

XML = """<?xml version="1.0" encoding="utf-8"?>
<Balancing_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:balancingdocument:4:1">
  <TimeSeries><businessType>A95</businessType><flowDirection.direction>A01</flowDirection.direction><curveType>A03</curveType>
    <Period><timeInterval><start>2026-09-01T00:00Z</start><end>2026-09-01T06:00Z</end></timeInterval><resolution>PT15M</resolution>
      <Point><position>1</position><activation_Price.amount>18.5</activation_Price.amount></Point>
      <Point><position>9</position><activation_Price.amount>13</activation_Price.amount></Point>
    </Period></TimeSeries>
  <TimeSeries><businessType>A96</businessType><flowDirection.direction>A02</flowDirection.direction>
    <Period><timeInterval><start>2026-09-01T00:00Z</start><end>2026-09-01T01:00Z</end></timeInterval><resolution>PT15M</resolution>
      <Point><position>2</position><activation_Price.amount>-40</activation_Price.amount></Point>
    </Period></TimeSeries>
</Balancing_MarketDocument>"""


class BalansTest(unittest.TestCase):
    def test_punt_geldt_tot_het_volgende_punt_of_het_einde(self):
        reeksen = balans.lees_reeksen(XML)
        soort, richting, fcr = reeksen[0]
        self.assertEqual((soort, richting, len(fcr)), ("A95", "A01", 24))       # zes uur aan kwartieren
        self.assertEqual([p for _, p in fcr[:8]], [18.5] * 8)                    # eerste blok van twee uur
        self.assertEqual({p for _, p in fcr[8:]}, {13.0})
        self.assertEqual(fcr[8][0].strftime("%H:%M"), "02:00")
        _, _, afrr = reeksen[1]
        self.assertEqual(len(afrr), 3)                                           # vanaf het tweede kwartier tot het einde
        self.assertEqual(afrr[0][0].strftime("%H:%M"), "00:15")

    def test_jaartabel(self):
        tijd = pd.date_range("2025-01-01", periods=8, freq="15min")
        fcr = pd.Series([10.0] * 8, index=tijd)
        op = pd.Series([0, 100, 0, 200, 0, 0, 0, 0], index=tijd, dtype=float)
        af = pd.Series([0, 0, -20, 0, 0, 0, 0, 0], index=tijd, dtype=float)
        rij = balans.jaartabel(fcr, op, af).iloc[0]
        self.assertAlmostEqual(rij.fcr_omzet_per_mw_bij_volledige_inzet, 10.0 * 8760)
        self.assertAlmostEqual(rij.afrr_op_aandeel_kwartieren, 0.25)
        self.assertAlmostEqual(rij.afrr_op_prijs_gemiddeld, 150.0)
        self.assertAlmostEqual(rij.afrr_af_prijs_gemiddeld, -20.0)


if __name__ == "__main__":
    unittest.main()
