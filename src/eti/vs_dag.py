"""Dagtabel voor Texas en Californie uit de bewaarde uurbestanden (geen netwerk nodig).

Per markt en lokale dag: prijs, dagspreiding, wat een batterij van twee uur verdient (plan op gisteren en achteraf
bezien), hoeveel zon er was en wat de batterijvloot deed. Dit is de grondstof voor de verzadigingscurve per GW
(eti.verzadiging_gw). Prijzen in euro met de vaste koers van het project (0,86).

Schrijft powerbi/data/fact_vs_dag.csv.  Gebruik:  PYTHONPATH=src python3 -m eti.vs_dag
"""
import csv
import glob
import json
import os
from collections import defaultdict

from . import battery, wereld
from .extra import log

RAW, OUT = "data/raw", "powerbi/data"
MARKTEN = (("VS Texas (ERCOT)", "ERCO", -6), ("VS Californie (CAISO)", "CISO", -8))
FX, UREN, RENDEMENT = 0.86, 2, 0.88
KOP = ["markt", "datum", "gem_prijs_eur", "spreiding_2u", "piekpremie", "daldiepte", "uur_piek", "uur_dal", "negatieve_uren",
       "batterij_achteraf_per_mw", "batterij_plan_per_mw", "zon_mwh", "wind_mwh", "opwek_mwh", "zon_piek_mw", "opwek_piek_mw",
       "bat_ontladen_max_mw", "bat_laden_max_mw", "bat_ontladen_mwh", "oth_max_mw", "oth_laden_max_mw", "bat_aandeel_piekuur", "opwek_uren"]


def per_uur(punten):
    """[(tijd, prijs)] -> {uur 'JJJJ-MM-DD UU:00': gemiddelde prijs}; kwartieren en dubbele uren worden gemiddeld."""
    groep = defaultdict(list)
    for t, p in punten:
        try:
            waarde = float(p)
        except (TypeError, ValueError):
            continue
        groep[t[:13] + ":00"].append(waarde)
    return {u: sum(v) / len(v) for u, v in groep.items()}


def prijzen(raw=RAW):
    tx, ca = wereld._eia_punten()
    extra = []
    for pad in sorted(glob.glob(os.path.join(raw, "gridstatus_ercot_hubavg_*.json"))):
        with open(pad, encoding="utf-8") as fh:
            extra += wereld.parse_gridstatus(json.load(fh))
    return {"VS Texas (ERCOT)": per_uur(wereld.voeg_samen(tx, extra, grens="9999")),
            "VS Californie (CAISO)": per_uur(wereld.voeg_samen(ca, wereld._oasis_punten()))}


def opwek(ba, raw=RAW):
    """{uur: {brandstof: MWh}} uit de bewaarde EIA-pagina's; dubbele uren tellen een keer."""
    uit = defaultdict(dict)
    for pad in sorted(glob.glob(os.path.join(raw, f"eia_fuel_{ba}_*.json"))):
        with open(pad, encoding="utf-8") as fh:
            for uur, brandstof, waarde in wereld.parse_eia_opwek(json.load(fh)):
                uit[uur][brandstof] = waarde
    return uit


def dagmaten(P, mix):
    """P: 24 prijzen in euro; mix: 24 dicts {brandstof: MWh} (leeg als de opwek ontbreekt)."""
    gem = sum(P) / 24
    s = sorted(P)
    top, dal = sum(s[-UREN:]) / UREN, sum(s[:UREN]) / UREN
    i_piek, i_dal = max(range(24), key=P.__getitem__), min(range(24), key=P.__getitem__)
    rij = [gem, top - dal, top - gem, gem - dal, i_piek, i_dal, sum(p < 0 for p in P), battery.best_daily_spread(P, UREN, RENDEMENT)[0], None]
    if not any(mix):
        return rij + [None] * 11 + [0]
    pos = [{b: max(v, 0.0) for b, v in m.items()} for m in mix]
    totaal = [sum(m.values()) for m in pos]
    bat, oth = [m.get("BAT") for m in mix], [m.get("OTH") for m in mix]
    heeft_bat = any(v is not None for v in bat)
    b = [v or 0.0 for v in bat]
    o = [v or 0.0 for v in oth]
    aandeel = (max(b[i_piek], 0.0) if heeft_bat else max(o[i_piek], 0.0)) / totaal[i_piek] if totaal[i_piek] else None
    return rij + [sum(m.get("SUN", 0.0) for m in pos), sum(m.get("WND", 0.0) for m in pos), sum(totaal), max(m.get("SUN", 0.0) for m in pos), max(totaal),
                  max(b) if heeft_bat else None, -min(b) if heeft_bat else None, sum(max(v, 0.0) for v in b) if heeft_bat else None,
                  max(o), -min(o), aandeel, sum(1 for m in mix if m)]             # opwek_uren: 24 = de dag is compleet


def tabel(raw=RAW):
    alle = prijzen(raw)
    rijen = []
    for markt, ba, offset in MARKTEN:
        prijs, mix = alle[markt], opwek(ba, raw)
        dagen = defaultdict(list)
        for uur in sorted(prijs):
            dagen[wereld._lokale_dag(uur, offset)].append(uur)
        vol = [(d, u) for d, u in sorted(dagen.items()) if len(u) == 24]
        reeks = [[prijs[k] * FX for k in u] for _, u in vol]
        plan = [None] + battery.naive_forecast_daily(reeks, UREN, RENDEMENT)
        for (dag, uren), P, winst in zip(vol, reeks, plan):
            maten = dagmaten(P, [mix.get(k, {}) for k in uren])
            maten[8] = winst
            rijen.append([markt, dag] + [None if v is None else round(v, 3) for v in maten])
        log(f"  {markt}: {len(vol)} volle dagen, {vol[0][0]} tot en met {vol[-1][0]}")
    return rijen


def main(raw=RAW, uit=OUT):
    rijen = tabel(raw)
    os.makedirs(uit, exist_ok=True)
    with open(os.path.join(uit, "fact_vs_dag.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(KOP); w.writerows(rijen)
    log(f"  -> fact_vs_dag.csv: {len(rijen)} rijen")
    return rijen


if __name__ == "__main__":
    main()
