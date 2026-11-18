"""Export a Power BI-ready star schema (CSV) from the warehouse and numbers.json.
Run: PYTHONPATH=src python -m eti.powerbi  -> powerbi/data/*.csv"""
import csv, json, os, tempfile
from . import data, warehouse, numbers


def _w(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def export(out="powerbi/data"):
    os.makedirs(out, exist_ok=True)
    n = numbers.build()
    db = warehouse.connect(os.path.join(tempfile.mkdtemp(), "p.db")); warehouse.load(db, data.synthetic_year())
    rows = warehouse.hourly(db); db.close()
    _w(f"{out}/fact_markt_uur.csv", ["timestamp_utc", "datum", "maand", "uur", "prijs_eur_mwh", "zon_nl_mw", "netfactor_kg_mwh"],
       [(t, t[:10], int(t[5:7]), int(t[11:13]), p, s, g) for t, p, s, g in rows if p is not None])
    _w(f"{out}/dim_regio.csv", ["regio", "wacc", "vollasturen", "capex_eur_kw", "netintensiteit_g_kwh", "fx_kosten"],
       [(r, v["inputs"]["wacc"], v["inputs"]["flh"], v["inputs"]["capex"] / 1000, v["inputs"]["grid"], v["inputs"]["fx_cost"])
        for r, v in n["regions"].items()])
    _w(f"{out}/fact_regio_jaar.csv", ["regio", "jaar", "lcoe_eur_mwh", "wacc", "financieringsaandeel", "t_co2_per_meur_jaar"],
       [(r, int(y), round(v[y]["lcoe"], 2), round(v[y]["wacc"], 4), round(v[y]["fin_share"], 4), round(v[y]["t_per_meur_year_life"], 1))
        for r, v in n["regions"].items() for y in (2025, 2030, 2050)])
    _w(f"{out}/fact_capture_curve.csv", ["capture_rate", "irr"], [(float(k), v) for k, v in n["capture_curve"].items()])
    _w(f"{out}/fact_erosie.csv", ["erosie", "irr", "irr_na_belasting"],
       [(float(k), v["irr"], v["irr_after_tax"]) for k, v in n["erosion"].items()])
    _w(f"{out}/fact_wereldbeeld.csv", ["wereldbeeld", "irr_zon", "irr_batterij_standalone", "irr_batterij_hybride", "netto_irr_belegger"],
       [(w, o["hybride"]["solar_irr"], o["standalone"]["battery_irr"], o["hybride"]["battery_irr"],
         o["fund"]["net_irr"] if o["fund"] else None) for w, o in n["worlds"].items()])
    _w(f"{out}/fact_jcurve.csv", ["jaar", "cumulatief_lp"], list(enumerate(n["fund_base"]["j_curve"])))
    _w(f"{out}/fact_klimaatscenario.csv", ["scenario", "npv_eur", "irr"], [(k, v[0], v[1]) for k, v in n["climate_scen"].items()])
    s, b = n["solar"], n["battery"]
    kpi = [("Zon", "IRR voor belasting", s["irr"]), ("Zon", "IRR na belasting", s["irr_after_tax"]),
           ("Zon", "LCOE", s["lcoe"]), ("Zon", "Capture price", s["capture_price"]),
           ("Zon", "Capture rate", n["market"]["capture_rate_solar"]), ("Zon", "Kans onder hurdle", s["p_below_hurdle"]),
           ("Zon", "IRR P10", s["irr_p10"]), ("Zon", "IRR P90", s["irr_p90"]),
           ("Zon", "Break-even capture rate (8%)", n["breakeven_capture_8"]),
           ("Batterij", "Omzet perfecte voorkennis", b["revenue_y1"]), ("Batterij", "Omzet naieve voorspelling", b["revenue_y1_naive"]),
           ("Batterij", "IRR", b["irr"]), ("Portefeuille", "IRR", n["portfolio"]["irr"]),
           ("Impact", "Vermeden t CO2 (uurfactor)", n["impact"]["solar_avoided_t_hourly"]),
           ("Impact", "Vermeden t CO2 (jaargemiddelde)", n["impact"]["solar_avoided_t_yearly_avg"])]
    _w(f"{out}/fact_kpi.csv", ["project", "kpi", "waarde"], kpi)
    json.dump(n, open("reports/numbers.json", "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    print(export())
