"""De verkenner echt gestart onder Streamlit (zonder browser), met het testgereedschap van Streamlit zelf.
Wordt overgeslagen waar streamlit of plotly ontbreekt; tests/test_verken.py dekt dan de rekenfuncties."""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
try:
    import plotly  # noqa: F401
    from streamlit.testing.v1 import AppTest
except Exception:                                  # ImportError, of een Streamlit zonder testgereedschap
    AppTest = None


@unittest.skipIf(AppTest is None, "streamlit of plotly niet geinstalleerd")
@unittest.skipUnless(os.path.exists(os.path.join(ROOT, "powerbi/data/fact_zonejaar_DA.csv")), "fact_zonejaar_DA ontbreekt: eerst eti.da draaien")
class TestVerkennerOnderStreamlit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oud = os.getcwd()
        os.chdir(ROOT)                             # de app leest powerbi/data vanaf de hoofdmap
        cls.app = AppTest.from_file(os.path.join(ROOT, "src/eti/verken_app.py"), default_timeout=120)
        cls.app.run()

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.oud)

    def fouten(self):
        return [str(getattr(f, "value", f))[:400] for f in self.app.exception]

    def test_1_start_zonder_fout(self):
        self.assertEqual(self.fouten(), [])
        self.assertIn("Waar verdient zon nog", self.app.title[0].value)
        self.assertGreaterEqual(len(self.app.metric), 8)        # vier kerncijfers en vier in de rekenhulp

    def test_2_andere_maat_en_schuif(self):
        self.app.sidebar.selectbox[0].select("dagspreiding")
        self.app.run()
        self.assertEqual(self.fouten(), [])
        schuif = next(s for s in self.app.slider if s.label.startswith("Gemiddelde prijs"))
        schuif.set_value(100)
        self.app.run()
        self.assertEqual(self.fouten(), [])
        capture = next(m for m in self.app.metric if m.label == "Capture-prijs")
        self.assertEqual(capture.value, "52 euro")              # 100 euro maal de standaard capture rate 0,52


if __name__ == "__main__":
    unittest.main()
