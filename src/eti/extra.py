"""Extra open datasets for a richer Power BI model. Run: PYTHONPATH=src python3 -m eti.extra
Writes powerbi/data/: fact_land_jaar.csv (capture rates per country/year), fact_land_maand.csv,
fact_nl_uur_alle_jaren.csv (hourly NL prices + generation mix), fact_owid_energie.csv,
fact_nl_jaar.csv (investment results per year). Every step is independent: a failure is logged and skipped."""
import csv, json, os, statistics, sys, traceback, urllib.request
from collections import defaultdict
from . import live, market

OUT = "powerbi/data"
COUNTRIES = [("NL", "nl", "Nederland"), ("DE-LU", "de", "Duitsland"), ("BE", "be", "Belgie"),
             ("FR", "fr", "Frankrijk"), ("ES", "es", "Spanje"), ("DK1", "dk", "Denemarken (West)")]
YEARS = range(2019, 2027)
OWID = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
OWID_COLS = ["country", "iso_code", "year", "solar_share_elec", "wind_share_elec", "renewables_share_elec",
             "fossil_share_elec", "nuclear_share_elec", "carbon_intensity_elec", "solar_electricity",
             "wind_electricity", "electricity_demand", "per_capita_electricity", "greenhouse_gas_emissions"]
OWID_KEEP = {"Netherlands", "Germany", "Belgium", "France", "Spain", "Denmark", "United States", "China",
             "India", "United Kingdom", "Italy", "Poland", "European Union (27)", "World", "Brazil", "Japan"}


def log(msg):
    print(msg, flush=True)


def _w(name, header, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    log(f"  -> {name}: {len(rows)} rijen")


def metrics(rows):
    """rows: [(t, price, {tech: MW})] -> market metrics for one period."""
    P = [p for _, p, _ in rows]
    sol = [g.get("solar", 0.0) for _, _, g in rows]
    wnd = [g.get("wind", 0.0) for _, _, g in rows]
    valid = [p for p in P if p is not None]
    if not valid:
        return None
    days = defaultdict(list)
    for t, p, _ in rows:
        if p is not None:
            days[t.date()].append(p)
    full = [max(v) - min(v) for v in days.values() if len(v) >= 20]
    spread = statistics.mean(full) if full else None
    def cr(gen):
        try:
            return market.capture_rate(P, gen) if sum(gen) > 0 else None
        except ZeroDivisionError:
            return None
    total = [sum(g.values()) for _, _, g in rows]
    return {"gem_prijs": statistics.mean(valid), "mediaan_prijs": statistics.median(valid),
            "capture_zon": cr(sol), "capture_wind": cr(wnd), "negatieve_uren": market.negative_hours(P),
            "uren_boven_200": sum(1 for p in valid if p > 200), "dagspreiding": spread,
            "aandeel_zon": sum(sol) / sum(total) if sum(total) else None,
            "aandeel_wind": sum(wnd) / sum(total) if sum(total) else None, "uren": len(valid)}


def countries():
    jaar, maand = [], []
    for bzn, cc, naam in COUNTRIES:
        for y in YEARS:
            try:
                rows = live.fetch_energy_charts(y, bzn=bzn, country=cc)
                if not rows:
                    raise ValueError("geen data")
                m = metrics(rows)
                jaar.append([naam, bzn, y] + [m[k] for k in m])
                bym = defaultdict(list)
                for r in rows:
                    bym[r[0].month].append(r)
                for mo, rr in sorted(bym.items()):
                    mm = metrics(rr)
                    if mm:
                        maand.append([naam, y, mo, mm["gem_prijs"], mm["capture_zon"], mm["capture_wind"],
                                      mm["negatieve_uren"], mm["dagspreiding"]])
                log(f"  {naam} {y}: capture zon {m['capture_zon'] and round(m['capture_zon'], 3)}, neg {m['negatieve_uren']}")
            except Exception as e:
                log(f"  {naam} {y} OVERGESLAGEN: {e}")
    cols = ["land", "biedzone", "jaar", "gem_prijs", "mediaan_prijs", "capture_zon", "capture_wind", "negatieve_uren",
            "uren_boven_200", "dagspreiding", "aandeel_zon", "aandeel_wind", "uren"]
    _w("fact_land_jaar.csv", cols, jaar)
    _w("fact_land_maand.csv", ["land", "jaar", "maand", "gem_prijs", "capture_zon", "capture_wind",
                               "negatieve_uren", "dagspreiding"], maand)


def nl_hourly():
    techs = ["solar", "wind", "gas", "coal", "nuclear", "biomass", "waste", "other_renewable"]
    out = []
    for y in YEARS:
        try:
            for t, p, g in live.fetch_energy_charts(y):
                out.append([t.strftime("%Y-%m-%d %H:%M"), y, t.month, t.hour, p] + [round(g.get(k, 0.0), 1) for k in techs])
        except Exception as e:
            log(f"  NL uur {y} OVERGESLAGEN: {e}")
    _w("fact_nl_uur_alle_jaren.csv", ["timestamp_utc", "jaar", "maand", "uur", "prijs_eur_mwh"] + [f"{k}_mw" for k in techs], out)


def nl_years():
    rows = []
    for y in YEARS:
        f = f"reports/live_{y}/results.json"
        if not os.path.exists(f):
            continue
        r = json.load(open(f)); m, s, b = r["market"], r["solar"], r["battery"]
        rows.append([y, m["capture_rate_solar"], m["negative_hours"], s["irr"], s.get("irr_after_tax"), s["lcoe"],
                     s.get("capture_price"), b["revenue_y1"], b.get("revenue_y1_naive"), b["irr"],
                     r["impact"]["solar_avoided_t_hourly"], r["impact"]["solar_avoided_t_yearly_avg"]])
    _w("fact_nl_jaar.csv", ["jaar", "capture_rate", "negatieve_uren", "irr_zon", "irr_zon_na_belasting", "lcoe",
                           "capture_price", "batterij_omzet_perfect", "batterij_omzet_realistisch", "irr_batterij",
                           "co2_vermeden_uur", "co2_vermeden_jaargem"], rows)


def owid():
    os.makedirs("data/raw", exist_ok=True)
    path = "data/raw/owid-energy-data.csv"
    if not os.path.exists(path):
        urllib.request.urlretrieve(OWID, path)
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["country"] in OWID_KEEP and r["year"] and int(r["year"]) >= 2000:
                rows.append([r.get(c, "") for c in OWID_COLS])
    _w("fact_owid_energie.csv", OWID_COLS, rows)


STEPS = [("Investeringsresultaten NL per jaar", nl_years), ("NL uurdata alle jaren", nl_hourly),
         ("Our World in Data", owid), ("Landenvergelijking Energy-Charts", countries)]

if __name__ == "__main__":
    only = sys.argv[1:]
    for name, fn in STEPS:
        if only and fn.__name__ not in only:
            continue
        log(f"== {name}")
        try:
            fn()
        except Exception:
            log(traceback.format_exc())
