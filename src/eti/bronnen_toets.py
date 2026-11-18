"""Vervolgonderzoek 1: zon achter de meter, of verklaart iets anders het verschil tussen de twee zonbronnen?

Vraag. Het zonaandeel volgens Energy-Charts (A, gemeten per biedzone) ligt gemiddeld 6 tot 12% onder dat van Ember (B)
in 2019 tot en met 2025. Ember schat zon achter de meter mee. Verklaart die kleinschalige zon het verschil?

Aanpak, in drie stappen:
1. Dekkingsgaten scheiden van methodeverschillen. Een land-jaar waarin A minder dan een kwart van B telt, meet de bron
   van A (bijna) geen zon. Dat is ontbrekende data, geen definitie. Zonder die rijen: hoe groot is het verschil nog?
2. Per land de verhouding A/B over de jaren. Is ze stabiel en lager dan 1, dan telt A structureel een deel niet mee;
   het ontbrekende deel (1 - verhouding) is dan de schatting van de kleinschalige zon die A mist.
3. Toets buiten de steekproef: de verhouding per land uit 2019-2022 als correctiefactor op 2023-2025. Als het verschil
   door een vaste definitie komt (zoals zon achter de meter), dan sluit de gecorrigeerde A beter aan op B.

Eén ijkpunt van buiten: Duitsland had eind 2024 ongeveer 100 GW zon, waarvan 38 GW op woningdaken en 29 GW op
bedrijfsdaken (BSW-Solar). Toch is A/B voor Duitsland ongeveer 1. De Duitse netbeheerders schatten zon achter de meter
dus mee. 'Zon achter de meter ontbreekt in A' geldt per land, niet in het algemeen.

Schrijft powerbi/data/fact_bronnen_land_RC.csv, fact_bronnen_jaar_RC.csv en fact_bronnen_toets_RC.csv.
Gebruik:  PYTHONPATH=src python3 -m eti.bronnen_toets
"""
import os
import sqlite3

import numpy as np
import pandas as pd

from . import sql_run

DATA = "powerbi/data"
GAT = 0.25                    # A onder een kwart van B: dekkingsgat
STABIEL = 0.8                 # minstens 80% van de jaren aan dezelfde kant
IJK, TOETS = range(2019, 2023), range(2023, 2026)


def vergelijking(data=DATA, tolerantie_pp=0.5, tolerantie_rel=0.10):
    """Bouwt in het geheugen de pijplijn en de aansluiting (03 en 05) en geeft rec_vergelijk plus Ember-zon in TWh."""
    con = sqlite3.connect(":memory:")
    sql_run.laad(con, data)
    p = dict(sql_run.PARAMETERS, tolerantie_pp=tolerantie_pp, tolerantie_rel=tolerantie_rel)
    for bestand in ("03_pijplijn.sql", "05_reconciliatie.sql"):
        for stap in sql_run.volgorde(sql_run.stappen(open(os.path.join(sql_run.SQLMAP, bestand), encoding="utf-8").read())):
            if stap["soort"] == "tabel":
                sql_run.voer_uit(con, stap, p)
    v = pd.read_sql("SELECT * FROM rec_vergelijk", con)
    twh = pd.read_sql("SELECT UPPER(iso_3_code) AS iso3, year AS jaar, generation_twh AS zon_twh FROM raw_ember_opwek_jaar "
                      "WHERE electricity_source = 'Solar'", con)
    con.close()
    return v.merge(twh, on=["iso3", "jaar"], how="left")


def per_land(v):
    rijen = []
    for iso3, t in v.groupby("iso3"):
        bruik = t[t.categorie != "dekkingsgat in A"]
        r = bruik.verhouding
        lager, hoger = float((r < 1).mean()) if len(r) else np.nan, float((r > 1).mean()) if len(r) else np.nan
        if len(bruik) < 3:
            regime = "te weinig bruikbare jaren"
        elif lager >= STABIEL:
            regime = "structureel lager in A"
        elif hoger >= STABIEL:
            regime = "structureel hoger in A"
        else:
            regime = "wisselend of gelijk"
        laatste = t.sort_values("jaar").iloc[-1]
        ontbreekt = max(0.0, 1 - float(r.median())) if regime == "structureel lager in A" else 0.0
        rijen.append({"iso3": iso3, "jaren": len(t), "dekkingsgat_jaren": int((t.categorie == "dekkingsgat in A").sum()),
                      "bruikbare_jaren": len(bruik), "verhouding_mediaan": float(r.median()) if len(r) else np.nan,
                      "verhouding_min": float(r.min()) if len(r) else np.nan, "verhouding_max": float(r.max()) if len(r) else np.nan,
                      "aandeel_jaren_lager": lager, "regime": regime,
                      "geschat_ontbrekend_aandeel_zon": ontbreekt,
                      "laatste_jaar": int(laatste.jaar), "ember_zon_twh_laatste_jaar": laatste.zon_twh,
                      "geschat_ontbrekend_twh": ontbreekt * laatste.zon_twh if pd.notna(laatste.zon_twh) else np.nan})
    return pd.DataFrame(rijen).sort_values(["regime", "verhouding_mediaan"]).reset_index(drop=True)


def per_jaar(v):
    """Gemiddeld verschil (A-B)/B over landen per jaar: alle land-jaren, en zonder dekkingsgaten."""
    rijen = []
    for jaar, t in v.groupby("jaar"):
        z = t[t.categorie != "dekkingsgat in A"]
        rijen.append({"jaar": jaar, "landen": len(t), "verschil_alle_pct": 100 * (t.a_pct.mean() - t.b_pct.mean()) / t.b_pct.mean(),
                      "landen_zonder_gat": len(z), "verschil_zonder_gat_pct": 100 * (z.a_pct.mean() - z.b_pct.mean()) / z.b_pct.mean(),
                      "mediane_verhouding_zonder_gat": float(z.verhouding.median()),
                      "dekkingsgaten": int((t.categorie == "dekkingsgat in A").sum())})
    return pd.DataFrame(rijen)


def toets_buiten_steekproef(v):
    """Correctiefactor per land uit de ijkjaren, toegepast op de toetsjaren. Fout = |A_gecorrigeerd - B| / B."""
    v = v[v.categorie != "dekkingsgat in A"]
    factor = v[v.jaar.isin(IJK)].groupby("iso3").verhouding.median().rename("factor")
    t = v[v.jaar.isin(TOETS)].merge(factor, on="iso3", how="inner")
    t["a_gecorrigeerd"] = t.a_pct / t.factor
    t["fout_zonder"] = (t.a_pct - t.b_pct).abs() / t.b_pct
    t["fout_met"] = (t.a_gecorrigeerd - t.b_pct).abs() / t.b_pct
    rijen = [{"groep": "alle landen", "land_jaren": len(t), "mediane_fout_zonder_correctie": t.fout_zonder.median(),
              "mediane_fout_met_correctie": t.fout_met.median(), "aandeel_beter": float((t.fout_met < t.fout_zonder).mean())}]
    land = per_land(v.assign(categorie=v.categorie))
    for regime, g in t.merge(land[["iso3", "regime"]], on="iso3").groupby("regime"):
        rijen.append({"groep": regime, "land_jaren": len(g), "mediane_fout_zonder_correctie": g.fout_zonder.median(),
                      "mediane_fout_met_correctie": g.fout_met.median(), "aandeel_beter": float((g.fout_met < g.fout_zonder).mean())})
    return pd.DataFrame(rijen)


def main(data=DATA, uit=DATA):
    v = vergelijking(data)
    land, jaar, toets = per_land(v), per_jaar(v), toets_buiten_steekproef(v)
    land.to_csv(os.path.join(uit, "fact_bronnen_land_RC.csv"), index=False)
    jaar.to_csv(os.path.join(uit, "fact_bronnen_jaar_RC.csv"), index=False)
    toets.to_csv(os.path.join(uit, "fact_bronnen_toets_RC.csv"), index=False)
    pd.set_option("display.width", 200)
    print(jaar.round(2).to_string(index=False)); print(); print(land.round(3).to_string(index=False)); print(); print(toets.round(3).to_string(index=False))
    return land, jaar, toets


if __name__ == "__main__":
    main()
