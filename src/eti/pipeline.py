"""End-to-end run: data -> warehouse -> analysis -> results (CSV, Markdown, charts)."""
import csv
import json
import os
from collections import defaultdict

from . import battery, data, esg, finance, live, market, regions, warehouse
from .config import Assumptions


def _by_day(rows, idx):
    days = defaultdict(list)
    for r in rows:
        days[r[0][:10]].append(r[idx])
    return [v for v in days.values() if len(v) == 24 and None not in v]


def analyse(db, a=Assumptions()):
    rows = warehouse.hourly(db)
    prices = [r[1] for r in rows]
    solar_nat = [r[2] for r in rows]
    factors = [r[3] for r in rows]
    # 1. market
    cr = market.capture_rate(prices, solar_nat)
    pairs = [(s, p) for s, p in zip(solar_nat, prices) if p is not None]
    slope, intercept, r2 = market.ols([s for s, _ in pairs], [p for _, p in pairs])
    by_month = defaultdict(lambda: [0.0, 0.0, 0.0, 0])
    for (ts, p, s, _f) in rows:
        if p is not None:
            m = by_month[int(ts[5:7])]
            m[0] += p * s; m[1] += s; m[2] += p; m[3] += 1
    monthly_cr = {k: (v[0] / v[1]) / (v[2] / v[3]) for k, v in sorted(by_month.items()) if v[1] and v[3] and v[2]}
    # 2. solar project
    scale = a.solar_mw * a.solar_full_load_hours / sum(solar_nat)
    park = [s * scale for s in solar_nat]
    solar_rev = sum(p * g for p, g in zip(prices, park) if p is not None)
    solar_capex = a.solar_mw * a.solar_capex_per_mw
    solar_opex = a.solar_mw * a.solar_opex_per_mw
    solar_cf = finance.project_cashflows(solar_capex, solar_rev, solar_opex, a.solar_life, a.solar_degradation)
    solar_irr = finance.irr_safe(solar_cf)
    solar_lcoe = finance.lcoe(solar_capex, solar_opex, a.solar_mw * a.solar_full_load_hours,
                              a.discount_rate, a.solar_life, a.solar_degradation)
    debt = finance.max_debt(solar_cf[1:16], a.dscr_target, a.debt_rate)
    # 3. battery
    daily_prices = _by_day(rows, 1)
    bat_rev, schedule = battery.yearly_arbitrage(daily_prices, a.battery_mw, a.battery_hours, a.battery_efficiency)
    bat_rev *= 365 / len(daily_prices)                       # scale for skipped days
    bat_capex = a.battery_mw * a.battery_hours * a.battery_capex_per_mwh
    bat_opex = bat_capex * a.battery_opex_share
    bat_cf = finance.project_cashflows(bat_capex, bat_rev, bat_opex, a.battery_life, a.battery_degradation)
    try:
        bat_irr = finance.irr_safe(bat_cf)
    except ValueError:
        bat_irr = None
    bat_rev_naive = battery.naive_forecast_arbitrage(daily_prices, a.battery_mw, a.battery_hours,
                                                     a.battery_efficiency) * 365 / len(daily_prices)
    solar_irr_tax = finance.irr_safe(regions.after_tax_cashflows(solar_capex, solar_rev, solar_opex, a.solar_life,
                                                            a.solar_degradation, a.tax_rate))
    uplift = finance.required_uplift(bat_capex, bat_rev, bat_opex, a.battery_life,
                                     a.battery_degradation, a.hurdle_irr)
    # 4. portfolio (battery cash flows stop after its life)
    port_cf = [s + (bat_cf[t] if t < len(bat_cf) else 0) for t, s in enumerate(solar_cf)]
    port_irr = finance.irr_safe(port_cf)
    sim_solar = finance.monte_carlo_irr(solar_capex, solar_rev, solar_opex, a.solar_life,
                                        a.revenue_sd_solar, a.simulations, 1, a.solar_degradation)
    def _irr(capex=solar_capex, rev=solar_rev, opex=solar_opex, life=a.solar_life, deg=a.solar_degradation):
        return finance.irr_safe(finance.project_cashflows(capex, rev, opex, life, deg))
    sensitivity = {
        "Capex ±20%": (_irr(capex=solar_capex * 1.2), _irr(capex=solar_capex * 0.8)),
        "Revenue ±20% (price / capture)": (_irr(rev=solar_rev * 0.8), _irr(rev=solar_rev * 1.2)),
        "Opex ±20%": (_irr(opex=solar_opex * 1.2), _irr(opex=solar_opex * 0.8)),
        "Degradation 1.0% / 0%": (_irr(deg=0.01), _irr(deg=0.0)),
        "Life 20 / 30 years": (_irr(life=20), _irr(life=30)),
    }
    # 5. impact
    solar_hourly_t, solar_avg_t = esg.avoided_solar_tonnes(park, factors)
    daily_factors = _by_day(rows, 3)
    common = min(len(daily_factors), len(schedule))
    bat_t = esg.battery_shift_tonnes(daily_factors[:common], schedule[:common],
                                     a.battery_mw, a.battery_hours, a.battery_efficiency)
    return {
        "market": {"capture_rate_solar": cr, "negative_hours": market.negative_hours(prices),
                   "slope_eur_per_gwh_solar": slope * 1000, "r2": r2, "monthly_capture_rate": monthly_cr},
        "solar": {"capex": solar_capex, "revenue_y1": solar_rev, "irr": solar_irr, "irr_after_tax": solar_irr_tax,
                  "lcoe": solar_lcoe, "capture_price": solar_rev / (a.solar_mw * a.solar_full_load_hours),
                  "npv": finance.npv(a.discount_rate, solar_cf), "max_debt": debt, "gearing": debt / solar_capex,
                  "irr_p10": finance.percentile(sim_solar, 10), "irr_p50": finance.percentile(sim_solar, 50),
                  "irr_p90": finance.percentile(sim_solar, 90),
                  "p_below_hurdle": (sum(x < a.hurdle_irr for x in sim_solar) + (a.simulations - len(sim_solar))) / a.simulations if sim_solar else 1.0},
        "battery": {"capex": bat_capex, "revenue_y1": bat_rev, "revenue_y1_naive": bat_rev_naive, "irr": bat_irr,
                    "npv": finance.npv(a.discount_rate, bat_cf),
                    "uplift_needed_per_mw": uplift / a.battery_mw},
        "portfolio": {"irr": port_irr, "npv": finance.npv(a.discount_rate, port_cf)},
        "impact": {"solar_avoided_t_hourly": solar_hourly_t, "solar_avoided_t_yearly_avg": solar_avg_t,
                   "battery_shift_t": bat_t,
                   "t_per_meur_solar": solar_hourly_t / (solar_capex / 1e6)},
        "sensitivity_solar_irr": sensitivity,
        "irr_simulations_solar": sim_solar,
        "battery_schedule_example": None,
        "assumptions": a.__dict__,
    }


def write_outputs(res, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump({k: v for k, v in res.items() if k != "irr_simulations_solar"}, f, indent=2, default=float)
    with open(os.path.join(out_dir, "monthly_capture_rate.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "capture_rate_solar"])
        for m, v in res["market"]["monthly_capture_rate"].items():
            w.writerow([m, round(v, 4)])
    s, b, p, i, mk = res["solar"], res["battery"], res["portfolio"], res["impact"], res["market"]
    pct = lambda x: "n/a" if x is None else f"{x:.1%}"
    md = f"""# Results: solar + storage investment case (synthetic data)

| Metric | Value |
|---|---|
| Solar capture rate | {mk['capture_rate_solar']:.3f} |
| Negative-price hours | {mk['negative_hours']} |
| Price effect of +1 GWh national solar | € {mk['slope_eur_per_gwh_solar']:.2f}/MWh (R² {mk['r2']:.2f}) |
| Solar IRR (P10 / P50 / P90) | {pct(s['irr'])} ({pct(s['irr_p10'])} / {pct(s['irr_p50'])} / {pct(s['irr_p90'])}) |
| Probability solar IRR below hurdle | {s['p_below_hurdle']:.0%} |
| Solar LCOE | € {s['lcoe']:.2f}/MWh |
| Sculpted debt capacity (gearing) | € {s['max_debt']/1e6:.1f}m ({s['gearing']:.0%}) |
| Battery revenue year 1 (upper bound) | € {b['revenue_y1']/1e6:.2f}m |
| Battery IRR (arbitrage only) | {pct(b['irr'])} |
| Extra revenue needed for hurdle IRR (e.g. ancillary services) | € {b['uplift_needed_per_mw']:,.0f} per MW per year |
| Portfolio IRR (solar + battery) | {pct(p['irr'])} |
| Avoided CO2 solar: hourly / yearly-average factor | {i['solar_avoided_t_hourly']:,.0f} t / {i['solar_avoided_t_yearly_avg']:,.0f} t |
| CO2 shifted by battery | {i['battery_shift_t']:,.0f} t per year |

All inputs are synthetic and assumptions illustrative; see `docs/methodology.md`.
"""
    with open(os.path.join(out_dir, "results.md"), "w") as f:
        f.write(md)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        months = list(mk["monthly_capture_rate"])
        fig, ax = plt.subplots(figsize=(6, 2.6))
        ax.plot(months, list(mk["monthly_capture_rate"].values()), marker="o", color="black")
        ax.axhline(1.0, linestyle="--", color="0.5")
        ax.set_xlabel("month"); ax.set_ylabel("capture rate"); ax.set_title("Solar capture rate by month")
        fig.tight_layout(); fig.savefig(os.path.join(out_dir, "capture_rate.png"), dpi=150)
        plt.close(fig)
    except ImportError:
        pass
    return md


def run(db_path, out_dir, a=Assumptions(), source="synthetic", year=2024, figures=True):
    """source: 'synthetic' (offline, default) or 'live' (Energy-Charts API, needs internet)."""
    db = warehouse.connect(db_path)
    try:
        if db.execute("SELECT COUNT(*) FROM fact_price").fetchone()[0] == 0:
            rows = live.fetch_energy_charts(year) if source == "live" else data.synthetic_year(year)
            warehouse.load(db, rows)
        res = analyse(db, a)
        res["meta"] = {"source": source, "year": year,
                       "attribution": live.ATTRIBUTION if source == "live" else "Synthetic data (eti.data)"}
        write_outputs(res, out_dir)
        if figures:
            from . import figures as fig
            fig.make_all(warehouse.hourly(db), res, os.path.join(out_dir, "figures"))
    finally:
        db.close()
    return res
