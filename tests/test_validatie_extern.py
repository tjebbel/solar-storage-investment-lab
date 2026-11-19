import unittest
from pathlib import Path
import pandas as pd
from eti import validatie_extern as v, netcongestie as nc


class TestOordeel(unittest.TestCase):
    def test_grenzen(self):
        self.assertEqual(v.oordeel("cr_x", 0.52, 0.51), "sluit aan")
        self.assertEqual(v.oordeel("cr_x", 0.55, 0.97), "afwijking open")
        self.assertTrue(v.oordeel("lr", 0.35, 0.26).startswith("verklaarbaar"))

    def test_verschoven_kolom(self):
        d = pd.DataFrame({"wachtrij_invoeding": [34.0, 8.5, 0.0], "unieke_verzoeken_afname": [34.0, 22.0, 0.0]})
        self.assertEqual(list(nc.verschoven_invoeding(d)), [True, False, False])


@unittest.skipUnless(Path("tableau/data/t1_zonejaar.csv").exists(), "tabellen ontbreken")
class TestTabel(unittest.TestCase):
    def test_duitsland_sluit_aan(self):
        t = v.tabel()
        de = t[t.Onderwerp.str.contains("Duitsland")]
        self.assertTrue((de.Oordeel == "sluit aan").all())


if __name__ == "__main__":
    unittest.main()
