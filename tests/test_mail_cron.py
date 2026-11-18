"""Mail en cron echt getest: een SMTP-server op de eigen machine (socket, geen nabootsing) en de cron-regels in een lege omgeving."""
import base64
import os
import re
import secrets
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

try:
    from eti import rapport_auto as ra
except ImportError as fout:                       # matplotlib of seaborn ontbreekt
    ra, REDEN = None, str(fout)


class _Gesprek(socketserver.StreamRequestHandler):
    """Net genoeg SMTP om smtplib een bericht te laten afleveren: EHLO, AUTH PLAIN, MAIL, RCPT, DATA, QUIT."""

    def handle(self):
        s, in_data, regels = self.server, False, []
        zeg = lambda tekst: self.wfile.write((tekst + "\r\n").encode())
        zeg("220 localhost ESMTP proefserver")
        while True:
            ruw = self.rfile.readline()
            if not ruw:
                break
            if in_data:
                if ruw.rstrip(b"\r\n") == b".":
                    s.berichten.append(b"".join(regels)); regels, in_data = [], False
                    zeg("250 OK bericht aangenomen")
                else:
                    regels.append(ruw)
                continue
            tekst = ruw.decode("utf-8", "replace").strip()
            woord = tekst.upper()
            s.opdrachten.append(woord.split(" ")[0])
            if woord.startswith("EHLO"):
                for regel in ["localhost"] + (["AUTH PLAIN"] if s.met_inlog else []):
                    zeg("250-" + regel)
                zeg("250 8BITMIME")
            elif woord.startswith("AUTH PLAIN"):
                s.inlog.append(base64.b64decode(tekst.split(" ")[2]).split(b"\0")[1:])
                zeg("235 2.7.0 ingelogd")
            elif woord.startswith("MAIL FROM"):
                zeg("250 OK")
            elif woord.startswith("RCPT TO"):
                s.ontvangers.append(tekst); zeg("250 OK")
            elif woord == "DATA":
                in_data = True; zeg("354 einde met een regel met alleen een punt")
            elif woord == "QUIT":
                zeg("221 tot ziens"); break
            else:
                zeg("502 niet ondersteund")


class _Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def proefserver(met_inlog=True):
    server = _Server(("127.0.0.1", 0), _Gesprek)
    server.met_inlog, server.berichten, server.opdrachten, server.inlog, server.ontvangers = met_inlog, [], [], [], []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


@unittest.skipIf(ra is None, "rapport_auto niet te laden")
class TestMailEcht(unittest.TestCase):
    def setUp(self):
        self.server = proefserver()
        self.wachtwoord = secrets.token_urlsafe(12)            # proefwaarde, alleen voor deze test
        self.mail = {"host": "127.0.0.1", "poort": self.server.server_address[1], "gebruiker": "proef", "wachtwoord": self.wachtwoord,
                     "van": "rapport@voorbeeld.test", "aan": ["een@voorbeeld.test", "twee@voorbeeld.test"]}

    def tearDown(self):
        self.server.shutdown(); self.server.server_close()

    def test_bericht_met_bijlage_komt_aan(self):
        with tempfile.TemporaryDirectory() as map_:
            bijlage = os.path.join(map_, "grafiek.png")
            with open(bijlage, "wb") as fh:
                fh.write(b"\x89PNG proef")
            self.assertTrue(ra.verstuur("Dagrapport proef", "Eerste regel.\n.Regel die met een punt begint.", [bijlage], self.mail))
        self.assertEqual(len(self.server.berichten), 1)
        bericht = self.server.berichten[0].decode("utf-8", "replace")
        self.assertIn("Subject: Dagrapport proef", bericht)
        self.assertIn('filename="grafiek.png"', bericht)
        self.assertIn("Regel die met een punt begint", bericht)
        self.assertEqual(len(self.server.ontvangers), 2)
        self.assertEqual(self.server.inlog, [[b"proef", self.wachtwoord.encode()]])
        self.assertEqual(self.server.opdrachten[-1], "QUIT")

    def test_zonder_gebruiker_geen_inlog(self):
        self.assertTrue(ra.verstuur("Zonder inlog", "tekst", (), dict(self.mail, gebruiker="", wachtwoord="")))
        self.assertNotIn("AUTH", self.server.opdrachten)
        self.assertEqual(len(self.server.berichten), 1)

    def test_wachtwoord_gaat_niet_onversleuteld_naar_een_andere_machine(self):
        oud, ra.LOKAAL = ra.LOKAAL, ()                         # doe alsof 127.0.0.1 een server buiten de deur is
        try:
            with self.assertLogs(ra.log, "ERROR"):
                self.assertFalse(ra.verstuur("Mag niet", "tekst", (), self.mail))
        finally:
            ra.LOKAAL = oud
        self.assertNotIn("AUTH", self.server.opdrachten)
        self.assertEqual(self.server.berichten, [])

    def test_server_onbereikbaar_geeft_logregel_geen_crash(self):
        self.server.shutdown(); self.server.server_close()
        with self.assertLogs(ra.log, "ERROR"):
            self.assertFalse(ra.verstuur("Niemand thuis", "tekst", (), self.mail))
        self.server = proefserver()


def cronregels():
    patroon = re.compile(r"^\s*(?:Cron:)?\s*((?:[\d*/,-]+\s+){5})(cd <repo> && .+)$")
    return [(m.group(1).split(), m.group(2)) for m in map(patroon.match, (ra.__doc__ or "").splitlines()) if m]


@unittest.skipIf(ra is None, "rapport_auto niet te laden")
class TestCron(unittest.TestCase):
    GRENZEN = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))

    def test_tijdvelden_zijn_geldig(self):
        regels = cronregels()
        self.assertEqual(len(regels), 3)
        for velden, _ in regels:
            for veld, (laag, hoog) in zip(velden, self.GRENZEN):
                for deel in veld.replace("*/", "").split(","):
                    if deel != "*":
                        for getal in deel.split("-"):
                            self.assertTrue(laag <= int(getal) <= hoog, (veld, velden))

    def test_opdrachten_draaien_in_een_lege_omgeving(self):
        """Cron geeft alleen HOME, SHELL en een kaal PATH mee. De regels moeten daar zonder hulp werken."""
        with tempfile.TemporaryDirectory() as werk:
            os.symlink(os.path.join(ROOT, "powerbi"), os.path.join(werk, "powerbi"))
            os.symlink(os.path.join(ROOT, "src"), os.path.join(werk, "src"))
            os.makedirs(os.path.join(werk, "reports/analyse/sjablonen"))
            shutil.copy(os.path.join(ROOT, ra.SJABLOON), os.path.join(werk, ra.SJABLOON))
            omgeving = ["env", "-i", "HOME=" + os.path.expanduser("~"), "SHELL=/bin/sh", "PATH=/usr/bin:/bin", "MPLCONFIGDIR=" + werk]
            for _, opdracht in cronregels():
                regel = opdracht.replace("<repo>", werk).replace("<python>", sys.executable)
                uit = subprocess.run(omgeving + ["/bin/sh", "-c", regel], capture_output=True, text=True, timeout=600)
                self.assertEqual(uit.returncode, 0, regel + "\n" + uit.stderr[-800:])
            self.assertTrue(os.path.exists(os.path.join(werk, ra.LOGBOEK)))
            rapporten = [f for _, _, fs in os.walk(os.path.join(werk, ra.UIT)) for f in fs if f.endswith(".md")]
            self.assertGreaterEqual(len(rapporten), 2, rapporten)


if __name__ == "__main__":
    unittest.main()
