import unittest

from eti import wereld


class NachtrunStappenTest(unittest.TestCase):
    def test_eia_opwek_leest_uur_brandstof_en_waarde(self):
        payload = {"response": {"total": "3", "data": [
            {"period": "2025-01-01T06", "respondent": "ERCO", "fueltype": "NUC", "value": "5100"},
            {"period": "2025-01-01T07", "respondent": "ERCO", "fueltype": "SUN", "value": 250},
            {"period": "2025-01-01T08", "respondent": "ERCO", "fueltype": "SUN", "value": None}]}}
        self.assertEqual(wereld.parse_eia_opwek(payload), [("2025-01-01 05:00", "NUC", 5100.0), ("2025-01-01 06:00", "SUN", 250.0)])
        self.assertEqual(wereld.parse_eia_opwek({}), [])

    def test_kengetallen_per_jaar_en_brandstof(self):
        uren = [f"2025-01-01 {h:02d}:00" for h in range(4)]
        prijs = dict(zip(uren, [40.0, -20.0, 60.0, 120.0]))                 # gemiddeld 50
        rijen = [(u, "NUC", 1000.0) for u in uren] + [(uren[1], "SUN", 3000.0), (uren[2], "SUN", 1000.0)]
        rijen += [(uren[1], "BAT", -500.0), (uren[3], "BAT", 800.0), (uren[3], "BAT", 800.0)]     # laden telt niet, dubbel uur een keer
        k = {(r[0], r[1]): r for r in wereld.opwek_kengetallen(rijen, prijs)}
        nuc, sun, bat = k[(2025, "NUC")], k[(2025, "SUN")], k[(2025, "BAT")]
        self.assertAlmostEqual(nuc[4], 1.0)                                   # vlak profiel vangt de gemiddelde prijs
        self.assertAlmostEqual(nuc[5], 0.25)
        self.assertAlmostEqual(sun[4], ((-20.0 * 3000 + 60.0 * 1000) / 4000) / 50.0)
        self.assertAlmostEqual(sun[5], 0.75)
        self.assertAlmostEqual(bat[2], 800.0 / 1e6)
        self.assertEqual(bat[6], 800.0)                                       # hoogste uurwaarde: maat voor het vermogen
        self.assertAlmostEqual(nuc[3] + sun[3] + bat[3], 1.0)
        self.assertEqual(nuc[7], 4)

    def test_zonder_prijs_geen_capture_rate(self):
        k = wereld.opwek_kengetallen([("2026-01-01 00:00", "NUC", 5.0)], {})
        self.assertEqual(k[0][:2], [2026, "NUC"])
        self.assertIsNone(k[0][4])

    def test_gridstatus_leest_begin_van_het_uur_en_prijs(self):
        payload = {"status_code": 200, "data": [
            {"interval_start_utc": "2025-06-25T05:00:00+00:00", "interval_end_utc": "2025-06-25T06:00:00+00:00", "location": "HB_HUBAVG", "spp": 23.5},
            {"interval_start_utc": "2025-06-25T06:00:00+00:00", "location": "HB_HUBAVG", "spp": None}], "meta": {"hasNextPage": False}}
        self.assertEqual(wereld.parse_gridstatus(payload), [("2025-06-25 05:00", 23.5)])
        self.assertEqual(wereld.parse_gridstatus({}), [])

    def test_aanvullen_laat_het_archief_staan(self):
        eia = [("2025-06-24 04:00", 20.0)]
        extra = [("2025-06-24 04:00", 21.0), ("2025-06-25 05:00", 23.5), ("2023-08-10 12:00", 300.0)]
        samen = dict(wereld.voeg_samen(eia, extra, grens="9999"))
        self.assertEqual(samen["2025-06-24 04:00"], 20.0)          # het archief telt waar beide bestaan
        self.assertEqual(samen["2025-06-25 05:00"], 23.5)          # na het einde van het archief
        self.assertEqual(samen["2023-08-10 12:00"], 300.0)         # een gat in het archief
        self.assertEqual(wereld.vergelijk(eia, extra), (1, 1.0))

    def test_antwoord_met_reeksen_herkennen(self):
        self.assertTrue(wereld.heeft_data(b"PK\x03\x04rest"))
        self.assertTrue(wereld.heeft_data(b"<Balancing_MarketDocument><TimeSeries>x</TimeSeries></Balancing_MarketDocument>"))
        self.assertFalse(wereld.heeft_data(b"<Acknowledgement_MarketDocument><Reason>No matching data</Reason></Acknowledgement_MarketDocument>"))
        self.assertFalse(wereld.heeft_data(None))
        self.assertFalse(wereld.heeft_data(b""))


if __name__ == "__main__":
    unittest.main()
