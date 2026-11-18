import unittest
from eti import herijk


class HerijkTest(unittest.TestCase):
    def test_vul_posities_a03_herhaalt_vorige_prijs(self):
        self.assertEqual(herijk.vul_posities({1: 10.0, 3: 30.0}, 4, "A03"), [10.0, 10.0, 30.0, 30.0])
        self.assertEqual(herijk.vul_posities({1: 10.0, 3: 30.0}, 4, "A01"), [10.0, None, 30.0, None])

    def test_beste_blok_laadt_voor_ontladen(self):
        p = [50, 10, 10, 50, 90, 90, 50]
        g, paar = herijk.beste_blok(p, p, 2, 1.0)
        self.assertEqual(paar, (1, 4)); self.assertEqual(g, 160)

    def test_plan_kan_verlies_geven(self):
        self.assertLess(herijk.winst([90, 90, 10, 10], [90, 90, 10, 10], (0, 2), 2, 1.0), 0)


if __name__ == "__main__":
    unittest.main()
