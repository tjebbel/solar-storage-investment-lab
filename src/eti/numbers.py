"""Single source of truth: every figure used in memo, reference work, study doc and dashboard.
Run: PYTHONPATH=src python -m eti.numbers  -> reports/numbers.json"""
import json, os, tempfile
from collections import defaultdict
from dataclasses import replace
from . import battery, data, finance, lenses, pipeline, regions, scenarios, warehouse
from .config import Assumptions


def build(a=Assumptions()):
    db = warehouse.connect(os.path.join(tempfile.mkdtemp(), "n.db"))
    warehouse.load(db, data.synthetic_year())
    res = pipeline.analyse(db, a)
    rows = warehouse.hourly(db)
    P = [r[1] for r in rows]; S = [r[2] for r in rows]
    mwh = a.solar_mw * a.solar_full_load_hours
    park = [s * mwh / sum(S) for s in S]
    s, b = res["solar"], res["battery"]
    capex, rev, opex = s["capex"], s["revenue_y1"], a.solar_mw * a.solar_opex_per_mw
    L, d, cr, T = a.solar_life, a.solar_degradation, res["market"]["capture_rate_solar"], a.tax_rate
    tax_irr = lambda cf: finance.irr([cf[0]] + [c - max(0, c - capex / L) * T for c in cf[1:]])
    n = {"assumptions": a.__dict__, "market": res["market"], "solar": s, "battery": b,
         "portfolio": res["portfolio"], "impact": res["impact"], "sensitivity": res.get("sensitivity_solar_irr")}
    # upside: higher yield (950 h measured-type yield)
    up = replace(a, solar_full_load_hours=950.0)
    r_up = pipeline.analyse(db, up)["solar"]
    n["upside_950h"] = {"irr": r_up["irr"], "irr_after_tax": r_up["irr_after_tax"], "lcoe": r_up["lcoe"]}
    # break-evens and curves (pre-tax project IRR vs 8% hurdle; after-tax vs 6%)
    n["breakeven_capture_8"] = scenarios.breakeven_capture(capex, rev, opex, L, d, cr, 0.08, 0.2, 2.0)
    n["capture_curve"] = scenarios.solar_irr_vs_capture(capex, rev, opex, L, d, cr, [0.6, 0.7, 0.8, 0.9, 1.0, 1.1])
    n["erosion"] = {e: {"irr": finance.irr(scenarios.eroding_cashflows(capex, rev, opex, L, d, e)),
                        "irr_after_tax": tax_irr(scenarios.eroding_cashflows(capex, rev, opex, L, d, e))}
                    for e in (0.0, 0.01, 0.02, 0.03)}
    c = scenarios.curtailment(P, park)
    n["curtailment"] = {**c, "irr": finance.irr(finance.project_cashflows(capex, c["revenue_curtailed"], opex, L, d))}
    cf = finance.project_cashflows(capex, rev, opex, L, d)
    n["leverage"] = {g: scenarios.equity_irr(cf, g * capex, a.debt_rate, 15) for g in (0.5, 0.6, 0.7)}
    n["ppa_price"] = {t: scenarios.ppa_price_for_irr(capex, mwh, opex, L, d, t) for t in (0.06, 0.07, 0.08)}
    bo = b["capex"] * a.battery_opex_share
    n["battery_uplift_curve"] = scenarios.battery_irr_vs_uplift(b["capex"], b["revenue_y1"], bo, a.battery_life,
                                                                a.battery_degradation, [0, 2e5, 4e5, 6e5, 8e5])
    n["battery_naive_irr"] = scenarios.battery_irr_vs_uplift(b["capex"], b["revenue_y1_naive"], bo, a.battery_life,
                                                             a.battery_degradation, [0])[0]
    n["tariff"] = scenarios.tariff_effect(b["revenue_y1"], 7300, [0, 5, 10, 15, 20])
    sc = {"Basis": {}, "Orderly": {"revenue_shift": -0.10}, "Fysiek": {"revenue_shift": -0.03, "extra_degradation": 0.003},
          "Disorderly": {"revenue_shift": -0.15, "capex_shift": 0.10}}
    n["climate_scen"] = {k: lenses.scenario_npv(capex, rev, opex, L, d, a.discount_rate, **v) for k, v in sc.items()}
    carbon = {}
    for dc in (0, 50, 100):
        q = lenses.carbon_passthrough(P, 100, 0.37, dc)
        sr = lenses.solar_revenue(q, park)
        carbon[dc] = {"solar_irr": finance.irr(finance.project_cashflows(capex, sr, opex, L, d))}
    n["carbon"] = carbon
    n["worlds"] = {}
    for name, w in lenses.WORLDS.items():
        out = {}
        for cfg, tc in (("standalone", 2 * 10 * 7300), ("hybride", 0)):
            out[cfg] = lenses.world_result(P, park, capex, opex, L, d, b["revenue_y1"],
                                           b["capex"] * (0.95 if tc == 0 else 1), bo, a.battery_life,
                                           a.battery_degradation, w, tariff_cost=tc)
        si = out["hybride"]["solar_irr"]
        out["fund"] = lenses.fund_cashflows(100, 4, si, 6, 0.02, 0.2, 0.08, 10) if si and si > -0.5 else None
        n["worlds"][name] = out
    f = lenses.fund_cashflows(100, 4, s["irr"], 6, 0.02, 0.2, 0.08, 10)
    n["fund_base"] = {k: f[k] for k in ("net_irr", "tvpi", "trough", "j_curve")}
    n["regions"] = {}
    for r in regions.REGIONS:
        n["regions"][r] = {y: regions.vision(r, y) for y in (2025, 2030, 2050)}
        R = regions.REGIONS[r]
        for y in (2025, 2030, 2050):
            v = n["regions"][r][y]
            g = R["grid"] * regions.YEARS[y]["grid"]
            lg = regions.lifetime_grid(g, y) if y < 2050 else g
            v["t_per_meur_year_life"] = lg * R["flh"] / 1000 / (v["capex"] / 1e6)
        n["regions"][r]["inputs"] = R
    ri = regions.REGIONS["India (RvdW)"]
    n["india_blended"] = {lab: regions.lcoe(ri["capex"], ri["capex"] * 0.03, ri["flh"], w, 25)
                          for lab, w in (("markt", 0.12), ("first_loss", regions.blended_wacc(0.12, 0.2, 0.02)), ("garantie", 0.07))}
    db.close()
    return n


if __name__ == "__main__":
    n = build()
    os.makedirs("reports", exist_ok=True)
    json.dump(n, open("reports/numbers.json", "w"), indent=1, default=float)
    print("reports/numbers.json written")
