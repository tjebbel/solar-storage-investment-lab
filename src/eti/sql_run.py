"""Draait de SQL-bestanden in sql/ op een SQLite-database die uit de csv's in powerbi/data wordt gevuld.

Elke stap in een bestand begint met "-- STAP: naam | hangt af van: a, b | soort: tabel of query". Het script zet de
stappen in de goede volgorde, vult {{parameters}} veilig in (als gebonden waarden, niet als tekst), meet de tijd en
schrijft een verslag. Een stap van soort 'tabel' bouwt tabellen; een stap van soort 'query' geeft rijen terug.

Gebruik:  PYTHONPATH=src python3 -m eti.sql_run                 (alles, verslag in reports/analyse/sql_uitvoer.txt)
          PYTHONPATH=src python3 -m eti.sql_run maand=2025-06 jaar=2024 regio=Iberie
"""
import os
import re
import sqlite3
import sys
import time

import pandas as pd

DATA, SQLMAP, DB, VERSLAG = "powerbi/data", "sql", "data/analyse.db", "reports/analyse/sql_uitvoer.txt"
BRONNEN = {"raw_land_jaar": "fact_land_jaar", "raw_flex_land": "fact_flex_land", "raw_land_maand": "fact_land_maand", "raw_nl_uur": "fact_nl_uur_alle_jaren",
           "raw_ember_opwek_jaar": "fact_ember_opwek_jaar", "raw_dim_land": "dim_land"}
VOLGORDE = ["03_pijplijn.sql", "01_analyse.sql", "02_optimalisatie.sql", "04_dashboard.sql", "05_reconciliatie.sql"]   # de pijplijn bouwt wat de rest leest
PARAMETERS = {"maand": "2025-06", "jaar": 2025, "jaar_van": 2019, "jaar_tot": 2025, "regio": "", "segment": "", "zone": "", "niveau": "regio", "tolerantie_pp": 0.5, "tolerantie_rel": 0.10}


def kolomnaam(naam):
    """'Share of generation (%)' -> 'share_of_generation': namen die zonder aanhalingstekens in SQL passen."""
    return re.sub(r"\W+", "_", str(naam)).strip("_").lower()


def laad(con, data=DATA):
    """Zet de csv's als raw_-tabellen in de database, plus de koppeltabel biedzone -> regio."""
    from . import da
    for tabel, bestand in BRONNEN.items():
        df = pd.read_csv(os.path.join(data, bestand + ".csv"), low_memory=False)
        df.columns = [kolomnaam(c) for c in df.columns]
        df.to_sql(tabel, con, if_exists="replace", index=False)
    pd.DataFrame(sorted(da.REGIO.items()), columns=["biedzone", "regio"]).to_sql("raw_dim_zone", con, if_exists="replace", index=False)


def stappen(tekst):
    """Splitst een bestand in stappen. Geeft een lijst dicts: naam, afhankelijk (lijst), soort, sql."""
    uit = []
    for blok in re.split(r"(?m)^-- STAP:", tekst)[1:]:
        kop, _, sql = blok.partition("\n")
        delen = [d.strip() for d in kop.split("|")]
        info = {"naam": delen[0], "afhankelijk": [], "soort": "query"}
        for d in delen[1:]:
            sleutel, _, waarde = d.partition(":")
            if sleutel.strip() == "hangt af van":
                info["afhankelijk"] = [x.strip() for x in waarde.split(",") if x.strip()]
            elif sleutel.strip() == "soort":
                info["soort"] = waarde.strip()
        info["sql"] = sql.strip()
        uit.append(info)
    return uit


def volgorde(lijst):
    """Topologische volgorde: een stap komt na alles waar ze van afhangt. Bronnen buiten de lijst (raw_*) tellen niet mee."""
    namen, klaar, uit = {s["naam"] for s in lijst}, set(), []
    wacht = list(lijst)
    while wacht:
        nu = [s for s in wacht if all(a in klaar or a not in namen for a in s["afhankelijk"])]
        if not nu:
            raise ValueError("kringverwijzing tussen stappen: " + ", ".join(s["naam"] for s in wacht))
        for s in nu:
            uit.append(s)
            klaar.add(s["naam"])
            wacht.remove(s)
    return uit


def opdrachten(sql):
    """Losse opdrachten zonder commentaar. Een opdracht eindigt met een puntkomma aan het eind van de regel; een
    puntkomma midden in een regel (in een tekstwaarde) splitst niet."""
    kaal = "\n".join(re.sub(r"\s*--.*$", "", r) for r in sql.splitlines())
    return [o.strip() for o in re.split(r";[ \t]*\n", kaal + "\n") if o.strip()]


def voer_uit(con, stap, parameters):
    """Draait een stap. Geeft (rijen als DataFrame of None, aantal rijen, seconden)."""
    start, resultaat, aantal = time.perf_counter(), None, 0
    for opdracht in opdrachten(stap["sql"]):
        gebonden = re.sub(r"\{\{(\w+)\}\}", r":\1", opdracht)                    # {{jaar}} -> :jaar, de waarde gaat apart mee
        nodig = {k: parameters[k] for k in set(re.findall(r":(\w+)", gebonden)) if k in parameters}
        cur = con.execute(gebonden, nodig)
        if cur.description:                                                        # een SELECT geeft kolommen terug
            resultaat = pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description])
            aantal = len(resultaat)
    con.commit()
    if stap["soort"] == "tabel":
        tabel = re.findall(r"CREATE TABLE (\w+)", stap["sql"])
        aantal = con.execute(f"SELECT COUNT(*) FROM {tabel[-1]}").fetchone()[0] if tabel else 0
    return resultaat, aantal, time.perf_counter() - start


def verbind(db):
    """Opent de database als bestand. Laat de map dat niet toe (SQLite moet zijn journaalbestand kunnen verwijderen),
    dan draait alles in het geheugen: zelfde uitkomsten, alleen blijft er geen databasebestand achter."""
    try:
        os.makedirs(os.path.dirname(db) or ".", exist_ok=True)
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE IF NOT EXISTS _schrijfproef (x)")
        con.execute("DROP TABLE _schrijfproef")
        con.commit()
        return con, db
    except (sqlite3.OperationalError, OSError):
        return sqlite3.connect(":memory:"), "geheugen (de map liet geen databasebestand toe)"


def main(*args, data=DATA, db=DB, verslag=VERSLAG):
    parameters = dict(PARAMETERS)
    for a in args:
        k, _, v = a.partition("=")
        parameters[k] = type(PARAMETERS.get(k, ""))(v) if k in PARAMETERS else v
    con, waar = verbind(db)
    laad(con, data)
    regels, tijden = [f"SQLite {sqlite3.sqlite_version}; database: {waar}; parameters: {parameters}", ""], {}
    for bestand in VOLGORDE:
        regels.append(f"== {bestand} ==")
        for stap in volgorde(stappen(open(os.path.join(SQLMAP, bestand), encoding="utf-8").read())):
            resultaat, aantal, sec = voer_uit(con, stap, parameters)
            tijden[stap["naam"]] = sec
            regels.append(f"{stap['naam']:<24} {stap['soort']:<6} {aantal:>7} rijen {sec * 1000:>9.1f} ms" + (f"   <- {', '.join(stap['afhankelijk'])}" if stap["afhankelijk"] else ""))
            if resultaat is not None and len(resultaat):
                regels += ["    " + r for r in resultaat.head(8).to_string(index=False, max_colwidth=60).splitlines()]
        regels.append("")
    if "traag" in tijden and "snel" in tijden:
        regels.append(f"Trage query {tijden['traag'] * 1000:.0f} ms, herschreven {tijden['snel'] * 1000:.1f} ms ({tijden['traag'] / max(tijden['snel'], 1e-6):.0f} keer sneller), "
                      f"voorberekend {tijden['voorberekend'] * 1000:.1f} ms.")
    k = pd.read_sql("SELECT controle, status, aantal, toelichting FROM kwaliteit", con)
    regels += ["", "Kwaliteitscontroles: " + ", ".join(f"{n} {s}" for s, n in k.status.value_counts().items())]
    con.close()
    os.makedirs(os.path.dirname(verslag), exist_ok=True)
    with open(verslag, "w", encoding="utf-8") as fh:
        fh.write("\n".join(regels) + "\n")
    print("\n".join(r for r in regels if not r.startswith("    ")))
    return tijden, k


if __name__ == "__main__":
    main(*sys.argv[1:])
