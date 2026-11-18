import unittest
from eti import wereld


class LokaleDagTest(unittest.TestCase):
    def test_avondpiek_californie_valt_in_dezelfde_lokale_dag(self):
        self.assertEqual(wereld._lokale_dag("2025-06-02 03:00", -8), "2025-06-01")
        self.assertEqual(wereld._lokale_dag("2025-06-01 20:00", -8), "2025-06-01")
        self.assertEqual(wereld._lokale_dag("2025-06-01 20:00", 0), "2025-06-01")

    def test_australie_middagdal_en_avondpiek_in_dezelfde_lokale_dag(self):
        from eti import nacht2
        self.assertEqual(nacht2.lokale_dag("2025-01-01 02:00", 10), "2025-01-01")   # 12:00 AEST, middagdal
        self.assertEqual(nacht2.lokale_dag("2025-01-01 08:00", 10), "2025-01-01")   # 18:00 AEST, avondpiek
        self.assertEqual(nacht2.lokale_dag("2025-01-01 15:00", 10), "2025-01-02")   # 01:00 AEST, volgende dag
        self.assertEqual(nacht2.lokale_dag("2025-01-01 15:00", 0), "2025-01-01")


if __name__ == "__main__":
    unittest.main()
