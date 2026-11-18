"""Onzekerheid per land: block-bootstrap van dagen (10.000 trekkingen per land-jaar).
Geeft P10/P50/P90 van capture rate zon en realistische batterij-omzet (2 uur, per MW).
Run: PYTHONPATH=src python3 -m eti.bootstrap [trekkingen]  -> powerbi/data/fact_onzekerheid_land.csv"""
import csv, random, sys
from collections import defaultdict
from . import battery, live
from .extra import COUNTRIES, YEARS, OUT, log


def daily_stats(rows):
    d = defaultdict(list)
    for t, p, g in rows:
        d[t.date()].append((p, g.get("solar", 0.0)))
    days = sorted(k for k, v in d.items() if len(v) == 24 and all(p is not None for p, _ in v))
    out, prev = [], None
    for k in days:
        P = [p for p, _ in d[k]]; S = [s for _, s in d[k]]
        bat = 0.0
        if prev is not None:
            _, pair = battery.best_daily_spread(prev, 2, 0.88)
            if pair:
                i, j = pair
                bat = max(sum(P[j:j + 2]) * 0.88 - sum(P[i:i + 2]), 0.0)
        out.append((sum(p * s for p, s in zip(P, S)), sum(S), sum(P), bat))
        prev = P
    return out


def pct(v, q):
    v = sorted(v); k = (len(v) - 1) * q
    return v[int(k)] + (v[min(int(k) + 1, len(v) - 1)] - v[int(k)]) * (k - int(k))


def run(n=10000, block=7, seed=42):
    rnd = random.Random(seed); res = []
    for bzn, cc, naam in COUNTRIES:
        for y in YEARS:
            try:
                ds = daily_stats(live.fetch_energy_charts(y, bzn=bzn, country=cc))
                if len(ds) < 200:
                    continue
                cr, bat = [], []
                for _ in range(n):
                    rev = vol = ps = b = 0.0; cnt = 0
                    while cnt < 365:
                        s = rnd.randrange(len(ds) - block)
                        for x in ds[s:s + block]:
                            rev += x[0]; vol += x[1]; ps += x[2]; b += x[3]; cnt += 1
                    if vol > 0:
                        cr.append((rev / vol) / (ps / (24 * cnt)))
                    bat.append(b * 365 / cnt)
                res.append([naam, y, n] + [pct(cr, q) for q in (.1, .5, .9)] + [pct(bat, q) for q in (.1, .5, .9)])
                log(f"  {naam} {y}: capture P10-P90 {res[-1][3]:.2f}-{res[-1][5]:.2f}")
            except Exception as e:
                log(f"  {naam} {y} OVERGESLAGEN: {e}")
    with open(f"{OUT}/fact_onzekerheid_land.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["land", "jaar", "trekkingen", "capture_p10", "capture_p50", "capture_p90",
                    "batterij_p10", "batterij_p50", "batterij_p90"]); w.writerows(res)
    log(f"  -> fact_onzekerheid_land.csv: {len(res)} rijen")


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
