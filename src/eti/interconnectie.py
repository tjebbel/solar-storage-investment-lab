"""Ember-interconnectiedata (scenario's Reference/Projects/Needs, 2024-2030-2040) naar Power BI.
Bron: bestanden in data/ember/. Run: PYTHONPATH=src python3 -m eti.interconnectie"""
import csv, glob, os
from collections import defaultdict
from .extra import log

SRC, OUT = "data/ember", "powerbi/data"
MAANDEN = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def _read(name):
    return list(csv.DictReader(open(os.path.join(SRC, name), encoding="utf-8")))


def _w(name, header, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    log(f"  -> {name}: {len(rows)} rijen")


def ntc():
    rows = []
    for scen, f in (("Reference", "REF_NTC.csv"), ("Projects", "PROJ_NTC.csv"), ("Needs", "NEEDS_NTC.csv")):
        for r in _read(f):
            rows.append([scen, r["Border"], r["From"], r["To"], int(r["Year"]), float(r["NTC_F"]), float(r["NTC_B"])])
    _w("fact_ntc.csv", ["scenario", "grens", "van", "naar", "jaar", "ntc_heen_mw", "ntc_terug_mw"], rows)
    return rows


def importpotentieel():
    rows = []
    for y in (2030, 2040):
        for r in _read(f"imp_pot_chart_{y}.csv"):
            for scen in ("2024", "Reference", "Projects", "Needs"):
                if r.get(scen):
                    rows.append([r["Country"], y, "Huidig (2024)" if scen == "2024" else scen, float(r[scen])])
    _w("fact_importpotentieel.csv", ["land", "peiljaar", "scenario", "waarde"], rows)


def landprofielen():
    uur, maand = [], []
    for y in (2024, 2030, 2040):
        for r in _read(f"country_hourly_chart_{y}.csv"):
            if r.get("RES-E") not in (None, ""):
                uur.append([r["Country"], y, int(r["Hour"]) - 1, int(r["Hour"]), float(r["RES-E"]), float(r["NET-P"])])
        for r in _read(f"country_monthly_chart_{y}.csv"):
            if r.get("RES-E") not in (None, ""):
                maand.append([r["Country"], y, MAANDEN[r["Month"]], float(r["RES-E"]), float(r["NET-P"])])
    _w("fact_land_profiel_uur.csv", ["land", "jaar", "uur", "uur_bron", "res_e", "net_p"], uur)      # uur 0-23 = het uur dat begint, zoals elders
    _w("fact_land_profiel_maand.csv", ["land", "jaar", "maand", "res_e", "net_p"], maand)
    return uur


def stromen():
    uur, maand = [], []
    for y in (2024, 2030, 2040):
        for r in _read(f"flows_hourly_chart_{y}.csv"):
            uur.append([r["Country From"], r["Country To"], y, int(r["Hour"]) - 1, int(r["Hour"]), float(r["Flow"])])
        for r in _read(f"flows_monthly_chart_{y}.csv"):
            maand.append([r["Country From"], r["Country To"], y, MAANDEN.get(r["Month"], r["Month"]), float(r["Flow"])])
    _w("fact_stromen_uur.csv", ["van", "naar", "jaar", "uur", "uur_bron", "stroom"], uur)
    _w("fact_stromen_maand.csv", ["van", "naar", "jaar", "maand", "stroom"], maand)


def samenvatting_nl(ntc_rows, uur_rows):
    tot = defaultdict(float)
    for scen, _, a, b, y, f, t in ntc_rows:
        if "NL" in (a, b):
            tot[(scen, y)] += f + t
    log("  NL interconnectie (MW, beide richtingen): " + ", ".join(f"{s} {y}: {v:,.0f}" for (s, y), v in sorted(tot.items())))
    for y in (2024, 2030, 2040):
        r = [x for x in uur_rows if x[0] == "Netherlands" and x[1] == y]
        if r:
            mid = max(r, key=lambda x: x[5]); low = min(r, key=lambda x: x[5])          # kolom 5 = net_p, kolom 2 = uur 0-23
            log(f"  NL {y}: netto-positie piek uur {mid[2]} ({mid[5]:+.1f}), dal uur {low[2]} ({low[5]:+.1f})")


if __name__ == "__main__":
    n = ntc(); importpotentieel(); u = landprofielen(); stromen(); samenvatting_nl(n, u)
