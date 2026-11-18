"""Vervolgonderzoek 2: hoe gevoelig is de indeling in segmenten voor de gekozen drempels?

De segmentregel (sql/03_pijplijn.sql, mart_zonejaar) gebruikt vijf drempels die gekozen zijn, niet afgeleid:
    capture rate zon < 0,60 en negatieve uren >= 300  -> Zonverzadigd   (de volgorde telt: dit gaat voor)
    dagspreiding >= 120 euro per MWh                   -> Batterijmarkt
    dagspreiding < 60 euro per MWh                     -> Vlakke prijzen
    capture rate zon >= 0,75                           -> Zon houdt waarde
    anders                                             -> Middenveld
Aanpak: (1) elke drempel apart 10% en 20% omhoog en omlaag; (2) alle vijf tegelijk willekeurig binnen plus of min 20%
(2.000 trekkingen). Per zone-jaar: in welk deel van de varianten blijft het segment gelijk? Een zone-jaar dat in minder
dan 80% van de trekkingen zijn segment houdt, heet 'grensgeval'. Grensgevallen horen in een rapport met een voorbehoud.

Schrijft powerbi/data/fact_segment_drempel_SG.csv (per drempel), fact_segment_zone_SG.csv (per zone-jaar).
Gebruik:  PYTHONPATH=src python3 -m eti.segment_gevoeligheid
"""
import os
import sqlite3

import numpy as np
import pandas as pd

from . import sql_run

DATA = "powerbi/data"
BASIS = {"capture_laag": 0.60, "negatief_uren": 300, "spreiding_hoog": 120, "spreiding_laag": 60, "capture_hoog": 0.75}
NAMEN = {"capture_laag": "capture rate onder (zonverzadigd)", "negatief_uren": "negatieve uren vanaf (zonverzadigd)",
         "spreiding_hoog": "dagspreiding vanaf (batterijmarkt)", "spreiding_laag": "dagspreiding onder (vlakke prijzen)",
         "capture_hoog": "capture rate vanaf (zon houdt waarde)"}
STABIEL, TREKKINGEN = 0.8, 2000


def zonejaren(data=DATA):
    con = sqlite3.connect(":memory:")
    sql_run.laad(con, data)
    for stap in sql_run.volgorde(sql_run.stappen(open(os.path.join(sql_run.SQLMAP, "03_pijplijn.sql"), encoding="utf-8").read())):
        if stap["soort"] == "tabel":
            sql_run.voer_uit(con, stap, sql_run.PARAMETERS)
    z = pd.read_sql("SELECT biedzone, land, regio, jaar, capture_zon, negatieve_uren, dagspreiding, segment FROM mart_zonejaar", con)
    con.close()
    return z


def segment(z, d):
    """Zelfde regel als in SQL, vectorieel. Een lege capture rate vergelijkt nergens mee (zoals NULL in SQL)."""
    c, n, s = z.capture_zon, z.negatieve_uren, z.dagspreiding
    return np.select([(c < d["capture_laag"]) & (n >= d["negatief_uren"]), s >= d["spreiding_hoog"], s < d["spreiding_laag"], c >= d["capture_hoog"]],
                     ["Zonverzadigd", "Batterijmarkt", "Vlakke prijzen", "Zon houdt waarde"], "Middenveld")


def per_drempel(z, basis):
    rijen = []
    for k in BASIS:
        for f in (0.8, 0.9, 1.1, 1.2):
            d = dict(BASIS, **{k: BASIS[k] * f})
            nieuw = segment(z, d)
            wissel = nieuw != basis
            rijen.append({"drempel": k, "omschrijving": NAMEN[k], "basis": BASIS[k], "factor": f, "waarde": BASIS[k] * f,
                          "zonejaren": len(z), "wisselen": int(wissel.sum()), "aandeel_wisselen": float(wissel.mean()),
                          "wisselen_2025": int(wissel[z.jaar == 2025].sum())})
    return pd.DataFrame(rijen)


def monte_carlo(z, basis, n=TREKKINGEN, seed=18):
    rng = np.random.default_rng(seed)
    gelijk = np.zeros(len(z))
    for _ in range(n):
        d = {k: v * rng.uniform(0.8, 1.2) for k, v in BASIS.items()}
        gelijk += segment(z, d) == basis
    uit = z[["biedzone", "land", "regio", "jaar", "capture_zon", "negatieve_uren", "dagspreiding"]].copy()
    uit["segment"] = basis
    uit["aandeel_gelijk"] = gelijk / n
    uit["grensgeval"] = uit.aandeel_gelijk < STABIEL
    return uit


def main(data=DATA, uit=DATA):
    z = zonejaren(data)
    basis = segment(z, BASIS)
    assert (basis == z.segment.values).all(), "de Python-regel wijkt af van de SQL-regel"
    d, m = per_drempel(z, basis), monte_carlo(z, basis)
    d.to_csv(os.path.join(uit, "fact_segment_drempel_SG.csv"), index=False)
    m.to_csv(os.path.join(uit, "fact_segment_zone_SG.csv"), index=False)
    pd.set_option("display.width", 200)
    print(d.round(3).to_string(index=False))
    print("\nGrensgevallen per jaar:", m.groupby("jaar").grensgeval.sum().to_dict())
    print("Aandeel grensgevallen per segment:", m.groupby("segment").grensgeval.mean().round(2).to_dict())
    print(m[(m.jaar == 2025) & m.grensgeval].sort_values("aandeel_gelijk").round(3).to_string(index=False))
    return d, m


if __name__ == "__main__":
    main()
