"""Vervolgonderzoek 6: SQLite en SQL Server eerlijk naast elkaar, op dezelfde machine, met dezelfde query's en data.

Wat 'eerlijk' hier betekent:
- dezelfde machine (de Mac), dezelfde data (de csv's in powerbi/data), dezelfde drie query's uit 02_optimalisatie
  (traag, snel, voorberekend) voor dezelfde maand;
- elke query vijf keer, na een opwarmronde; de mediaan telt, zodat een toevallige uitschieter niet beslist;
- de tijd is de verstreken tijd in de database zelf: voor SQLite gemeten rond de uitvoering, voor SQL Server de
  'elapsed time' van SET STATISTICS TIME. De tijd om de uitkomst naar het scherm te schrijven telt niet mee.
Wat niet gelijk is en in het verslag hoort: SQL Server draait in Docker als linux/amd64 en wordt op een Mac met
Apple-chip nagebootst (Rosetta); SQLite draait direct. SQL Server rekent bovendien parallel.

Gebruik (op de Mac, vanuit de repo):
    PYTHONPATH=src .venv/bin/python -m eti.sql_benchmark sqlite             -> resultaten/benchmark_sqlite.csv
    bash sql/tsql/benchmark_tsql.sh                                         -> resultaten/benchmark_tsql.log
    PYTHONPATH=src .venv/bin/python -m eti.sql_benchmark samen              -> resultaten/benchmark_sql.csv en .md
"""
import os
import re
import sqlite3
import statistics
import sys
import time

import pandas as pd

from . import sql_run

MAAND, HERHALINGEN = "2025-06", 5
UIT = "resultaten"
QUERIES = ("traag", "snel", "voorberekend")


def sqlite_tijden(data=sql_run.DATA, maand=MAAND, n=HERHALINGEN):
    con = sqlite3.connect(":memory:")
    sql_run.laad(con, data)
    p = dict(sql_run.PARAMETERS, maand=maand)
    for stap in sql_run.volgorde(sql_run.stappen(open(os.path.join(sql_run.SQLMAP, "03_pijplijn.sql"), encoding="utf-8").read())):
        if stap["soort"] == "tabel":
            sql_run.voer_uit(con, stap, p)
    stappen = {s["naam"]: s for s in sql_run.stappen(open(os.path.join(sql_run.SQLMAP, "02_optimalisatie.sql"), encoding="utf-8").read())}
    rijen = []
    for naam in QUERIES:
        sql_run.voer_uit(con, stappen[naam], p)                                   # opwarmen
        tijden, aantal = [], None
        for _ in range(n):
            res, aantal, sec = sql_run.voer_uit(con, stappen[naam], p)
            tijden.append(sec * 1000)
        rijen.append({"systeem": f"SQLite {sqlite3.sqlite_version}", "query": naam, "rijen": aantal, "mediaan_ms": statistics.median(tijden),
                      "min_ms": min(tijden), "max_ms": max(tijden), "herhalingen": n})
    con.close()
    return pd.DataFrame(rijen)


def tsql_tijden(log):
    """Leest het logboek van benchmark_tsql.sh: per ronde drie keer 'elapsed time' en het aantal rijen, in de volgorde
    traag, snel, voorberekend. De eerste ronde is de opwarmronde en telt niet mee."""
    tekst = open(log, encoding="utf-8", errors="replace").read()
    rondes = re.split(r"(?m)^== ronde \d+", tekst)[1:]
    per = {q: [] for q in QUERIES}
    aantallen = {}
    for i, r in enumerate(rondes):
        uitvoer = [int(x) for x in re.findall(r"SQL Server Execution Times:\s*CPU time = \d+ ms,\s*elapsed time = (\d+) ms", r)]
        rijen = [int(x) for x in re.findall(r"\((\d+) rows affected\)", r)]
        if len(uitvoer) < 3 or i == 0:
            continue
        for q, t, a in zip(QUERIES, uitvoer[:3], rijen[:3]):
            per[q].append(t)
            aantallen[q] = a
    versie = re.search(r"Microsoft SQL Server (\d{4})", tekst)
    return pd.DataFrame([{"systeem": f"SQL Server {versie.group(1) if versie else ''} (Docker, linux/amd64)".strip(), "query": q, "rijen": aantallen.get(q),
                          "mediaan_ms": statistics.median(v) if v else None, "min_ms": min(v) if v else None, "max_ms": max(v) if v else None,
                          "herhalingen": len(v)} for q, v in per.items()])


def samen(uit=UIT):
    s = pd.read_csv(os.path.join(uit, "benchmark_sqlite.csv"))
    t = tsql_tijden(os.path.join(uit, "benchmark_tsql.log"))
    b = pd.concat([s, t], ignore_index=True)
    for systeem, g in b.groupby("systeem"):
        snel = g.loc[g["query"] == "snel", "mediaan_ms"].iloc[0]
        b.loc[b.systeem == systeem, "keer_trager_dan_snel"] = g.mediaan_ms / max(snel, 0.01)
    b.to_csv(os.path.join(uit, "benchmark_sql.csv"), index=False)
    with open(os.path.join(uit, "benchmark_sql.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# SQLite en SQL Server op dezelfde machine\n\nMaand {MAAND}, mediaan van {HERHALINGEN} rondes na een opwarmronde.\n\n")
        try:
            fh.write(b.round(2).to_markdown(index=False))
        except ImportError:                                                        # tabulate niet geinstalleerd
            fh.write("```\n" + b.round(2).to_string(index=False) + "\n```")
        fh.write("\n")
    print(b.round(2).to_string(index=False))
    return b


def main(*args):
    os.makedirs(UIT, exist_ok=True)
    stap = args[0] if args else "sqlite"
    if stap == "sqlite":
        s = sqlite_tijden()
        s.to_csv(os.path.join(UIT, "benchmark_sqlite.csv"), index=False)
        print(s.round(2).to_string(index=False))
    elif stap == "samen":
        samen()
    else:
        raise SystemExit("gebruik: sqlite | samen")


if __name__ == "__main__":
    main(*sys.argv[1:])
