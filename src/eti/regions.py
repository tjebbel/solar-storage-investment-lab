"""Regional comparison and 2030/2050 vision. All inputs illustrative unless sourced in docs."""
from . import finance

# Sources (verified 14-11-2026): grid NL 263 g (Electricity Maps 2024); US 384, China 560, India 708 (Ember 2024);
# US capex $1.69/W_AC and 25% capacity factor (LBNL 2026 ed.); India capex $525/kW (IRENA 2024).
# NL: PBL SCE 2025 (740 h, EUR 449/kWp, O&M 15.7/kWp). Spain: REE 2024 (~27 Mt / ~266 TWh -> ~100 g;
# 44.5 TWh / ~30 GW avg -> ~1,500 h), IEA PVPS 2023 (>20 MW: EUR 0.70/W). China: EPC bids 2024
# CNY 2.06-3.30/W (-> EUR 270-430/kW), hours ~1,050 (Jiangsu) to 1,300: 1,200 used. USD->EUR 0.86, CNY->EUR 0.13.
REGIONS = {
    "Nederland":        dict(wacc=0.050, flh=740,  capex=449_000,   grid=263, tax=0.258, fx_cost=0.000, opex=0.035),
    "Europa (Spanje)":  dict(wacc=0.055, flh=1500, capex=700_000,   grid=100, tax=0.25,  fx_cost=0.000),
    "VS (Texas)":       dict(wacc=0.060, flh=2190, capex=1_450_000, grid=384, tax=0.21,  fx_cost=0.015, opex=0.015),
    "China":            dict(wacc=0.045, flh=1200, capex=350_000,   grid=560, tax=0.25,  fx_cost=-0.005),
    "India (RvdW)":     dict(wacc=0.120, flh=1650, capex=450_000,   grid=708, tax=0.25,  fx_cost=0.045),
}
YEARS = {2025: dict(capex=1.00, grid=1.00, wacc_gap=1.0),
         2030: dict(capex=0.75, grid=0.60, wacc_gap=0.8),
         2050: dict(capex=0.50, grid=0.10, wacc_gap=0.4)}


def after_tax_cashflows(capex, revenue, opex, life, degradation, tax):
    dep = capex / life
    out = [-capex]
    for t in range(1, life + 1):
        ebitda = revenue * (1 - degradation) ** (t - 1) - opex
        out.append(ebitda - max(0.0, ebitda - dep) * tax)
    return out


def lcoe(capex, opex, mwh, rate, life, degradation=0.005):
    return finance.lcoe(capex, opex, mwh, rate, life, degradation)


def finance_share(capex, opex, mwh, rate, life):
    """Share of LCOE caused by the cost of capital (vs. 0% rate)."""
    return 1 - lcoe(capex, opex, mwh, 0.0, life) / lcoe(capex, opex, mwh, rate, life)


def vision(region, year, opex_share=None, life=25, advanced_wacc=0.05):
    r, y = REGIONS[region], YEARS[year]
    if opex_share is None:
        opex_share = r.get("opex", 0.03)
    capex = r["capex"] * y["capex"]
    wacc = advanced_wacc + (r["wacc"] - advanced_wacc) * y["wacc_gap"]
    mwh = r["flh"]
    l = lcoe(capex, capex * opex_share, mwh, wacc, life)
    avoided_t_per_meur = r["grid"] * y["grid"] / 1000 * mwh * life / (capex / 1e6) / 1  # t over life per EUR mln
    return {"capex": capex, "wacc": wacc, "lcoe": l, "fin_share": finance_share(capex, capex * opex_share, mwh, wacc, life),
            "t_per_meur_life": avoided_t_per_meur}


def lifetime_grid(start_g, start_year, life=25, g2050_share=0.10):
    """Average grid factor over the asset life, declining linearly to g2050_share*today by 2050."""
    g0 = start_g
    vals = []
    for y in range(start_year, start_year + life):
        frac = min(1.0, max(0.0, (y - 2025) / 25))
        vals.append(g0 * (1 - frac * (1 - g2050_share)))
    return sum(vals) / len(vals)


def blended_wacc(senior_rate, share_concessional, concessional_rate):
    return share_concessional * concessional_rate + (1 - share_concessional) * senior_rate


def hedged_return(local_irr, fx_cost):
    """Euro return after hedging currency: approx. local IRR minus interest-rate differential."""
    return local_irr - fx_cost
