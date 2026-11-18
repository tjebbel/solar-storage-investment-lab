"""Professional lenses: climate-scenario stress (GARP SCR), fund economics (CAIA),
carbon pass-through (AIF / CFA SI). Illustrative, transparent formulas."""
from . import finance, battery


def carbon_passthrough(prices, gas_threshold, intensity, delta_carbon):
    """Add intensity*delta_carbon (EUR/MWh) in hours where gas is assumed marginal (price >= threshold)."""
    return [None if p is None else (p + intensity * delta_carbon if p >= gas_threshold else p)
            for p in prices]


def solar_revenue(prices, gen):
    return sum(p * g for p, g in zip(prices, gen) if p is not None)


def fund_cashflows(commitment, draw_years, project_irr, hold, mgmt_fee, carry, hurdle, life):
    """Simple closed-end fund: equal draws, each tranche grows at project_irr for `hold` years,
    fee on commitment during life, European waterfall (carry above hurdle on whole fund)."""
    draws = commitment / draw_years
    gross_in, gross_out = [0.0] * (life + 1), [0.0] * (life + 1)
    for y in range(draw_years):
        gross_in[y] += draws
        gross_out[min(y + hold, life)] += draws * (1 + project_irr) ** hold
    fees = [commitment * mgmt_fee if y < life else 0.0 for y in range(life + 1)]
    lp = [-(gross_in[y] + fees[y]) + gross_out[y] for y in range(life + 1)]
    paid_in = sum(gross_in) + sum(fees)
    distributions = sum(gross_out)
    pref = sum((gross_in[y] + fees[y]) * (1 + hurdle) ** (life - y) for y in range(life + 1))
    profit = distributions - paid_in
    carry_amt = carry * profit if distributions > pref else 0.0
    lp[life] -= carry_amt
    cum, curve = 0.0, []
    for c in lp:
        cum += c
        curve.append(cum)
    net_irr = finance.irr(lp)
    return {"net_irr": net_irr, "tvpi": (distributions - carry_amt) / paid_in,
            "j_curve": curve, "trough": min(curve), "carry": carry_amt}


def scenario_npv(capex, revenue, opex, life, degradation, rate, revenue_shift=0.0,
                 capex_shift=0.0, extra_degradation=0.0):
    cf = finance.project_cashflows(capex * (1 + capex_shift), revenue * (1 + revenue_shift),
                                   opex, life, degradation + extra_degradation)
    return finance.npv(rate, cf), finance.irr(cf)


WORLDS = {  # illustrative, internally consistent NGFS-style worlds
    "Huidig beleid": dict(carbon=0, erosion=0.010, capex=0.00, spread_growth=0.00),
    "Orderly (Net Zero)": dict(carbon=60, erosion=0.025, capex=0.00, spread_growth=0.03),
    "Disorderly": dict(carbon=100, erosion=0.035, capex=0.10, spread_growth=0.04),
}


def world_result(prices, gen, capex, opex, life, degr, bat_base_rev, bat_capex, bat_opex, bat_life,
                 bat_degr, world, gas_threshold=100, intensity=0.37, tariff_cost=0.0):
    """One consistent world: carbon pass-through + capture erosion + capex shock, solar and battery."""
    q = carbon_passthrough(prices, gas_threshold, intensity, world["carbon"])
    rev = solar_revenue(q, gen)
    cf_s = [-capex * (1 + world["capex"])] + [rev * ((1 - degr) * (1 - world["erosion"])) ** (t - 1) - opex
                                              for t in range(1, life + 1)]
    uplift = 1 + intensity * world["carbon"] / 100 * 0.5          # carbon widens evening spread
    cf_b = [-bat_capex * (1 + world["capex"])] + [
        bat_base_rev * uplift * ((1 - bat_degr) * (1 + world["spread_growth"])) ** (t - 1) - bat_opex - tariff_cost
        for t in range(1, bat_life + 1)]
    def safe(cf):
        try:
            return finance.irr(cf)
        except ValueError:
            return None
    return {"solar_irr": safe(cf_s), "battery_irr": safe(cf_b), "solar_rev_y1": rev}
