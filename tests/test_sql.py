"""Tests voor de SQL-loper: stappen lezen, volgorde bepalen, opdrachten splitsen en parameters binden."""
import sqlite3
import unittest

from eti import sql_run

VOORBEELD = """-- kop van het bestand
-- STAP: b | hangt af van: a, raw_x | soort: tabel
DROP TABLE IF EXISTS b;
CREATE TABLE b AS SELECT naam || '; ' || naam AS dubbel FROM a;   -- puntkomma in een tekstwaarde
-- STAP: a | hangt af van: raw_x | soort: tabel
DROP TABLE IF EXISTS a;
CREATE TABLE a AS SELECT naam FROM raw_x WHERE jaar >= {{jaar}};
-- STAP: vraag | hangt af van: b | soort: query
SELECT COUNT(*) AS n FROM b WHERE ({{filter}} = '' OR dubbel LIKE {{filter}} || '%');
"""


class Lezen(unittest.TestCase):
    def test_stappen_en_afhankelijkheden(self):
        s = sql_run.stappen(VOORBEELD)
        self.assertEqual([x["naam"] for x in s], ["b", "a", "vraag"])
        self.assertEqual(s[0]["afhankelijk"], ["a", "raw_x"])
        self.assertEqual(s[2]["soort"], "query")

    def test_volgorde_zet_bron_voor_afnemer(self):
        namen = [x["naam"] for x in sql_run.volgorde(sql_run.stappen(VOORBEELD))]
        self.assertEqual(namen, ["a", "b", "vraag"])

    def test_kring_geeft_fout(self):
        kring = [{"naam": "p", "afhankelijk": ["q"]}, {"naam": "q", "afhankelijk": ["p"]}]
        with self.assertRaises(ValueError):
            sql_run.volgorde(kring)

    def test_opdrachten_splitsen(self):
        o = sql_run.opdrachten(sql_run.stappen(VOORBEELD)[0]["sql"])
        self.assertEqual(len(o), 2)
        self.assertIn("'; '", o[1])                       # de puntkomma in de tekstwaarde blijft staan
        self.assertNotIn("--", o[1])

    def test_kolomnaam(self):
        self.assertEqual(sql_run.kolomnaam("Share of generation (%)"), "share_of_generation")
        self.assertEqual(sql_run.kolomnaam("ISO 3 code"), "iso_3_code")


class Uitvoeren(unittest.TestCase):
    def test_parameters_en_leeg_filter(self):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE raw_x (naam TEXT, jaar INTEGER)")
        con.executemany("INSERT INTO raw_x VALUES (?, ?)", [("nl", 2024), ("es", 2025), ("no", 2019)])
        uit = {}
        for stap in sql_run.volgorde(sql_run.stappen(VOORBEELD)):
            uit[stap["naam"]] = sql_run.voer_uit(con, stap, {"jaar": 2024, "filter": ""})
        self.assertEqual(uit["a"][1], 2)                    # twee rijen vanaf 2024
        self.assertEqual(int(uit["vraag"][0].n.iloc[0]), 2)    # leeg filter: alles
        stap = sql_run.stappen(VOORBEELD)[2]
        self.assertEqual(int(sql_run.voer_uit(con, stap, {"filter": "es"})[0].n.iloc[0]), 1)
        kwaad = sql_run.voer_uit(con, stap, {"filter": "x'; DROP TABLE b; --"})[0]      # gebonden waarde: geen injectie
        self.assertEqual(int(kwaad.n.iloc[0]), 0)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM b").fetchone()[0], 2)


if __name__ == "__main__":
    unittest.main()
