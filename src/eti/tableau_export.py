"""Maakt de databestanden voor het Tableau-dashboard 'Zon en opslag in Europa: eerste bevindingen'.

Tableau leest csv's prima, maar het sterschema in powerbi/data is gemaakt voor Power BI-relaties en DAX. Voor Tableau zijn
vijf platte tabellen handiger: elke tabel hoort bij een of twee werkbladen, met Nederlandse kolomnamen, een echte datum
waar een tijdas nodig is, en de lange vorm waar een gestapelde staaf nodig is. Zo is er in Tableau geen koppeling nodig.

Schrijft naar tableau/data:
  t1_zonejaar.csv          zone x jaar: prijs, capture rate, negatieve uren, dagspreiding, batterij-omzet, segment, grensgeval
  t2_land_maand.csv        zone x maand: voor de signalering (de Tableau-versie van de DAX-maten)
  t3_batterij.csv          hoogste bouwkosten per kWh voor 8% en 5% per scenario
  t4_schokjaar.csv         opbouw van de prijsstijging 2026 tegen 2025 per zone (lange vorm)
  t5_bronnen.csv           verschil Energy-Charts tegen Ember per jaar, met en zonder dekkingsgaten (lange vorm)
Alle getallen met een punt als decimaalteken (zie de bouwgids: landinstelling van de gegevensbron op Engels).
Gebruik:  PYTHONPATH=src python3 -m eti.tableau_export
"""
import os
import sqlite3

import pandas as pd

from . import sql_run

DATA = "powerbi/data"
UIT = "tableau/data"


def mart_zonejaar(data=DATA):
    con = sqlite3.connect(":memory:")
    sql_run.laad(con, data)
    for stap in sql_run.volgorde(sql_run.stappen(open(os.path.join(sql_run.SQLMAP, "03_pijplijn.sql"), encoding="utf-8").read())):
        if stap["soort"] == "tabel":
            sql_run.voer_uit(con, stap, sql_run.PARAMETERS)
    z = pd.read_sql("SELECT biedzone, land, regio, iso3, jaar, heel_jaar, gem_prijs, capture_zon, negatieve_uren, dagspreiding, "
                    "batterij_per_mw, segment FROM mart_zonejaar", con)
    con.close()
    return z


def t1(data=DATA):
    z = mart_zonejaar(data)
    g = pd.read_csv(os.path.join(data, "fact_segment_zone_SG.csv"))[["biedzone", "jaar", "aandeel_gelijk", "grensgeval"]]
    z = z.merge(g, on=["biedzone", "jaar"], how="left")
    z["grensgeval"] = z.grensgeval.map({True: "grensgeval", False: "stevig"})
    return z.rename(columns={"biedzone": "Zone", "land": "Zonenaam", "regio": "Regio", "iso3": "Landcode", "jaar": "Jaar",
                             "heel_jaar": "Heel jaar", "gem_prijs": "Gemiddelde prijs", "capture_zon": "Capture rate zon",
                             "negatieve_uren": "Negatieve uren", "dagspreiding": "Dagspreiding", "batterij_per_mw": "Batterij-omzet per MW",
                             "segment": "Segment", "aandeel_gelijk": "Segment stabiel (aandeel)", "grensgeval": "Segment zekerheid"})


def t2(data=DATA):
    m = pd.read_csv(os.path.join(data, "fact_land_maand.csv"))
    sleutel = pd.read_csv(os.path.join(data, "fact_land_jaar.csv"))[["land", "biedzone", "iso3"]].drop_duplicates("land")
    m = m.merge(sleutel, on="land", how="left")
    m["Maand"] = pd.to_datetime(dict(year=m.jaar, month=m.maand, day=1)).dt.strftime("%Y-%m-%d")
    return m.rename(columns={"land": "Zonenaam", "biedzone": "Zone", "iso3": "Landcode", "jaar": "Jaar", "maand": "Maandnummer",
                             "gem_prijs": "Gemiddelde prijs", "capture_zon": "Capture rate zon", "capture_wind": "Capture rate wind",
                             "negatieve_uren": "Negatieve uren", "dagspreiding": "Dagspreiding"})


def t3(data=DATA):
    b = pd.read_csv(os.path.join(data, "fact_batterij_breakeven_BI.csv"))
    b["Scenario"] = b.netkosten.str.replace("geen netkosten", "dagmarkt, geen netkosten").str.replace(
        "tijdsafhankelijk transportrecht", "tijdsafhankelijk transportrecht", regex=False)
    b.loc[~b.netkosten.str.startswith("stapeling"), "Scenario"] = "dagmarkt, " + b.netkosten + ", " + b.cycli_per_dag.map(lambda c: f"{c:g} cyclus per dag".replace(".", ","))
    b.loc[b.netkosten.str.startswith("stapeling"), "Scenario"] = b.netkosten
    lang = b.melt(id_vars=["Scenario", "cycli_per_dag", "levensduur_jaar", "omzet_per_mw"],
                  value_vars=["max_capex_per_kwh_voor_8pct", "max_capex_per_kwh_voor_5pct"], var_name="Doelrendement", value_name="Hoogste bouwkosten per kWh")
    lang["Doelrendement"] = lang.Doelrendement.map({"max_capex_per_kwh_voor_8pct": "8%", "max_capex_per_kwh_voor_5pct": "5%"})
    lang["Bouwkosten nu per kWh"] = 280.0
    return lang.rename(columns={"cycli_per_dag": "Cycli per dag", "levensduur_jaar": "Levensduur (jaar)", "omzet_per_mw": "Omzet per MW"})


def t4(data=DATA):
    s = pd.read_csv(os.path.join(data, "fact_schokjaar_zone_SJ.csv"))
    s = s[s.maanden == s.maanden.max()]
    lang = s.melt(id_vars=["biedzone", "prijsstijging"], value_vars=["door_gas", "door_zon", "door_wind", "rest"], var_name="Oorzaak", value_name="Euro per MWh")
    lang["Oorzaak"] = lang.Oorzaak.map({"door_gas": "Gas", "door_zon": "Zon", "door_wind": "Wind", "rest": "Niet verklaard"})
    return lang.rename(columns={"biedzone": "Zone", "prijsstijging": "Prijsstijging totaal"})


def t5(data=DATA):
    j = pd.read_csv(os.path.join(data, "fact_bronnen_jaar_RC.csv"))
    lang = j.melt(id_vars=["jaar"], value_vars=["verschil_alle_pct", "verschil_zonder_gat_pct"], var_name="Vergelijking", value_name="Verschil (%)")
    lang["Vergelijking"] = lang.Vergelijking.map({"verschil_alle_pct": "alle landen", "verschil_zonder_gat_pct": "zonder dekkingsgaten"})
    return lang.rename(columns={"jaar": "Jaar"})


def main(data=DATA, uit=UIT):
    os.makedirs(uit, exist_ok=True)
    tabellen = {"t1_zonejaar": t1(data), "t2_land_maand": t2(data), "t3_batterij": t3(data), "t4_schokjaar": t4(data), "t5_bronnen": t5(data)}
    for naam, t in tabellen.items():
        t.to_csv(os.path.join(uit, f"{naam}.csv"), index=False, float_format="%.6g")
        print(f"{naam}.csv: {len(t)} rijen, kolommen: {', '.join(t.columns)}")
    return tabellen


if __name__ == "__main__":
    main()
