"""Tests voor de automatische rapporten: randgevallen in dag- en weekrapport, het sjabloon en het versturen."""
import unittest
from datetime import date
from unittest import mock

import numpy as np
import pandas as pd

try:
    from eti import rapport_auto as ra            # heeft matplotlib en seaborn nodig (voor de grafieken van het maandrapport)
except ImportError:
    ra = None
ZONDER = "matplotlib of seaborn ontbreekt"


def dagen(n=40, einde="2026-04-12", gat=None):
    idx = pd.date_range(end=einde, periods=n, freq="D")
    d = pd.DataFrame({"uren": 24, "prijs": np.linspace(80, 119, n), "dagspreiding": 100.0, "negatieve_uren": 2, "batterij_per_mw": 200.0, "volledig": True}, index=idx)
    if gat:
        d.loc[pd.Timestamp(gat), ["uren", "volledig"]] = [20, False]
    return d


@unittest.skipIf(ra is None, ZONDER)
class Kalender(unittest.TestCase):
    def test_pasen_en_feestdagen(self):
        self.assertEqual(ra.pasen(2025), date(2025, 4, 20))
        self.assertEqual(ra.pasen(2026), date(2026, 4, 5))
        f = ra.feestdagen(2026)
        for dag in (date(2026, 1, 1), date(2026, 4, 6), date(2026, 4, 27), date(2026, 5, 14), date(2026, 5, 25), date(2026, 12, 26)):
            self.assertIn(dag, f)
        self.assertIn(date(2025, 4, 26), ra.feestdagen(2025))            # 27 april 2025 is een zondag: Koningsdag schuift


@unittest.skipIf(ra is None, ZONDER)
class Dag(unittest.TestCase):
    def test_gewone_dag_vergelijkt_met_week_eerder(self):
        tekst, t = ra.dagrapport(dagen())
        self.assertEqual(t, pd.Timestamp("2026-04-12"))
        self.assertIn("Dezelfde weekdag een week eerder", tekst)
        self.assertIn("Vergelijking over 7 volledige dagen.", tekst)

    def test_feestdag_vergelijkt_met_zondag(self):
        tekst, t = ra.dagrapport(dagen(), "2026-04-06")                  # tweede paasdag, een maandag
        self.assertIn("(feestdag)", tekst)
        self.assertIn("De laatste zondag (feestdag)", tekst)

    def test_onvolledige_dag_telt_niet_mee(self):
        tekst, t = ra.dagrapport(dagen(gat="2026-04-12"))
        self.assertEqual(t, pd.Timestamp("2026-04-11"))                  # de laatste volledige dag
        tekst, _ = ra.dagrapport(dagen(gat="2026-04-09"))
        self.assertIn("ontbreken uren op 1 dag", tekst)
        self.assertIn("Vergelijking over 6 volledige dagen.", tekst)

    def test_geen_data_geeft_een_melding(self):
        leeg = dagen().assign(volledig=False)
        tekst, t = ra.dagrapport(leeg)
        self.assertIsNone(t)
        self.assertIn("Geen volledige dag", tekst)


@unittest.skipIf(ra is None, ZONDER)
class Week(unittest.TestCase):
    def test_alleen_hele_weken(self):
        tekst, w = ra.weekrapport(dagen(n=40, einde="2026-04-15"))        # eindigt op een woensdag
        self.assertEqual(w.end_time.date(), date(2026, 4, 12))           # de lopende week doet niet mee
        self.assertIn("Weekrapport week 15 van 2026", tekst)
        self.assertIn("n.b.", tekst)                                      # geen zelfde week vorig jaar in dit voorbeeld

    def test_week_met_gat_wordt_overgeslagen(self):
        _, w = ra.weekrapport(dagen(n=40, einde="2026-04-12", gat="2026-04-08"))
        self.assertEqual(w.end_time.date(), date(2026, 4, 5))


@unittest.skipIf(ra is None, ZONDER)
class Sjabloon(unittest.TestCase):
    def test_stoplicht_en_verschil(self):
        self.assertEqual(ra.stoplicht(6, lambda x: x >= 5, lambda x: x >= 0), ra.GROEN)
        self.assertEqual(ra.stoplicht(2, lambda x: x >= 5, lambda x: x >= 0), ra.GEEL)
        self.assertEqual(ra.stoplicht(-1, lambda x: x >= 5, lambda x: x >= 0), ra.ROOD)
        self.assertEqual(ra.stoplicht(float("nan"), lambda x: True, lambda x: True), "n.b.")
        self.assertEqual(ra.verschil(110, 100), "+10%")
        self.assertEqual(ra.verschil(5, 0), "n.b.")

    def test_vul_meldt_ontbrekende_velden(self):
        with self.assertLogs("rapport_auto", level="WARNING") as logs:
            tekst = ra.vul("Prijs {{prijs}}, norm {{norm}}", {"prijs": "172"})
        self.assertEqual(tekst, "Prijs 172, norm n.b.")
        self.assertIn("norm", logs.output[0])


@unittest.skipIf(ra is None, ZONDER)
class Versturen(unittest.TestCase):
    def test_zonder_instellingen_gebeurt_er_niets(self):
        self.assertFalse(ra.verstuur("onderwerp", "tekst", mail={"host": "", "van": "", "aan": [], "poort": 587, "gebruiker": "", "wachtwoord": ""}))

    def test_met_instellingen_gaat_het_bericht_weg(self):
        mail = {"host": "smtp.voorbeeld.test", "poort": 587, "gebruiker": "u", "wachtwoord": "w", "van": "a@voorbeeld.test", "aan": ["b@voorbeeld.test"]}
        with mock.patch("eti.rapport_auto.smtplib.SMTP") as smtp:
            self.assertTrue(ra.verstuur("Dagrapport", "inhoud", mail=mail))
        server = smtp.return_value.__enter__.return_value
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("u", "w")
        self.assertEqual(server.send_message.call_args[0][0]["Subject"], "Dagrapport")


if __name__ == "__main__":
    unittest.main()
