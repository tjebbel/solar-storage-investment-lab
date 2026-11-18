"""Test voor het notebook-sjabloon: de zes delen staan erin en het bestand is geldig notebook-JSON."""
import unittest

from eti import maak_notebook


class Sjabloon(unittest.TestCase):
    def test_zes_delen_en_geldige_cellen(self):
        nb = maak_notebook.notebook()
        koppen = [regel.strip() for cel in nb["cells"] if cel["cell_type"] == "markdown" for regel in cel["source"] if regel.startswith("## ")]
        self.assertEqual([k.split(". ", 1)[1] for k in koppen], ["Instellen", "Overzicht van de data", "Opschonen", "Verkennen", "Kernanalyse", "Bevindingen en aanbevelingen"])
        self.assertEqual((nb["nbformat"], nb["nbformat_minor"]), (4, 5))
        self.assertEqual(len({cel["id"] for cel in nb["cells"]}), len(nb["cells"]))
        for cel in nb["cells"]:
            if cel["cell_type"] == "code":
                compile("".join(cel["source"]), cel["id"], "exec")            # elke codecel is geldige Python
                self.assertEqual(cel["outputs"], [])


if __name__ == "__main__":
    unittest.main()
