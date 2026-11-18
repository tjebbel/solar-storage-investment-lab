"""Nachtanalyse: per land en jaar de waarde van flexibiliteit en van zon/wind, uit de lokale cache.
Run: PYTHONPATH=src python3 -m eti.nacht  -> powerbi/data/fact_flex_land.csv, fact_tech_land.csv"""
import csv, os, statistics
from collections import defaultdict
from . import battery, finance, live
from .extra import COUNTRIES, YEARS, OUT, log

DURATIONS = [1, 2, 4]          # uren opslag bij 1 MW
EFF = 0.88
BAT_CAPEX_PER_MWH = 300_000    # EUR per MWh opslag
SOLAR_CAPEX, SOLAR_OPEX, SOLAR_FLH = 449_000, 15_700, 740   # per MW (PBL)
WIND_CAPEX, WIND_OPEX, WIND_FLH = 1_400_000, 40_000, 2_500  # per MW onshore (aanname)


def _days(rows):
    d = defaultdict(list)
    for t, p, _ in rows:
        d[t.date()].append(p)
    return [v for v in d.values() if len(v) == 24 and None not in v]


def _irr(capex, rev, opex, life, degradation=0.005):
    return finance.irr_safe(finance.project_cashflows(capex, rev, opex, life, degradation))


def run():
    flex, tech = [], []
    for bzn, cc, naam in COUNTRIES:
        for y in YEARS:
            try:
                rows = live.fetch_energy_charts(y, bzn=bzn, country=cc)
                days = _days(rows)
                if len(days) < 200:
                    raise ValueError(f"te weinig volle dagen ({len(days)})")
                scale = 365 / len(days)
                for h in DURATIONS:
                    perf, _ = battery.yearly_arbitrage(days, 1, h, EFF)
                    naive = battery.naive_forecast_arbitrage(days, 1, h, EFF)
                    capex = BAT_CAPEX_PER_MWH * h
                    flex.append([naam, y, h, perf * scale, naive * scale, naive / perf if perf else None,
                                 _irr(capex, naive * scale, capex * 0.02, 15, 0.02)])   # batterij: 2% degradatie per jaar, zoals in config
                P = [p for _, p, _ in rows]
                for techn, capex, opex, flh in (("zon", SOLAR_CAPEX, SOLAR_OPEX, SOLAR_FLH),
                                                ("wind", WIND_CAPEX, WIND_OPEX, WIND_FLH)):
                    gen = [g.get("solar" if techn == "zon" else "wind", 0.0) for _, _, g in rows]
                    tot = sum(g for p, g in zip(P, gen) if p is not None)
                    if tot <= 0:
                        continue
                    cp = sum(p * g for p, g in zip(P, gen) if p is not None) / tot
                    neg = sum(g for p, g in zip(P, gen) if p is not None and p < 0) / tot
                    rev = cp * flh
                    tech.append([naam, y, techn, cp, statistics.mean(p for p in P if p is not None), neg,
                                 _irr(capex, rev, opex, 25)])
                log(f"  {naam} {y}: batterij 2u realistisch EUR {flex[-2][4]:,.0f}/MW")
            except Exception as e:
                log(f"  {naam} {y} OVERGESLAGEN: {e}")
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/fact_flex_land.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["land", "jaar", "uren_opslag", "omzet_perfect_per_mw", "omzet_realistisch_per_mw",
                                       "voorspel_ratio", "irr_realistisch"]); w.writerows(flex)
    with open(f"{OUT}/fact_tech_land.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["land", "jaar", "technologie", "capture_price", "gem_prijs",
                                       "aandeel_productie_negatief", "irr_merchant"]); w.writerows(tech)
    log(f"  -> fact_flex_land.csv: {len(flex)} rijen, fact_tech_land.csv: {len(tech)} rijen")


if __name__ == "__main__":
    run()
