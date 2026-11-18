"""Sharper investment analysis: break-evens, scenarios and policy sensitivity."""
from . import finance


def _rev_at(revenue, base_capture, capture):
    return revenue * capture / base_capture


def solar_irr_vs_capture(capex, revenue, opex, life, degradation, base_capture, capture_rates):
    out = {}
    for c in capture_rates:
        cfs = finance.project_cashflows(capex, _rev_at(revenue, base_capture, c), opex, life, degradation)
        try:
            out[c] = finance.irr(cfs)
        except ValueError:
            out[c] = None
    return out


def breakeven_capture(capex, revenue, opex, life, degradation, base_capture, hurdle, lo=0.2, hi=1.5):
    """Capture rate at which NPV at the hurdle rate is zero (bisection)."""
    f = lambda c: finance.npv(hurdle, finance.project_cashflows(
        capex, _rev_at(revenue, base_capture, c), opex, life, degradation))
    if f(lo) * f(hi) > 0:
        raise ValueError("break-even outside range")
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def battery_irr_vs_uplift(capex, revenue, opex, life, degradation, uplifts):
    out = {}
    for u in uplifts:
        try:
            out[u] = finance.irr(finance.project_cashflows(capex, revenue + u, opex, life, degradation))
        except ValueError:
            out[u] = None
    return out


def tariff_effect(revenue, throughput_mwh, tariffs):
    """Arbitrage margin when grid tariff (EUR/MWh) is charged on both charge and discharge."""
    return {t: revenue - 2 * t * throughput_mwh for t in tariffs}


def curtailment(prices, generation):
    """Revenue and lost volume when the park switches off in negative-price hours."""
    full = sum(p * g for p, g in zip(prices, generation) if p is not None)
    curt = sum(p * g for p, g in zip(prices, generation) if p is not None and p > 0)
    lost = sum(g for p, g in zip(prices, generation) if p is not None and p <= 0)
    return {"revenue_full": full, "revenue_curtailed": curt, "lost_mwh": lost,
            "lost_share": lost / sum(generation)}


def eroding_cashflows(capex, revenue, opex, life, degradation, erosion):
    """Revenue falls by `erosion` per year on top of degradation (capture-rate decline)."""
    return [-capex] + [revenue * ((1 - degradation) * (1 - erosion)) ** (t - 1) - opex
                       for t in range(1, life + 1)]


def equity_irr(cashflows, debt, rate, tenor):
    """Equity IRR with an annuity loan of `debt` over `tenor` years."""
    pay = debt / finance.annuity(rate, tenor)
    eq = [cashflows[0] + debt] + [c - (pay if t <= tenor else 0)
                                  for t, c in enumerate(cashflows[1:], start=1)]
    min_dscr = min(cashflows[t] / pay for t in range(1, tenor + 1))
    return finance.irr(eq), min_dscr


def ppa_price_for_irr(capex, mwh, opex, life, degradation, target):
    """Fixed pay-as-produced PPA price (EUR/MWh) that gives exactly `target` IRR."""
    pv_e = sum(mwh * (1 - degradation) ** (t - 1) / (1 + target) ** t for t in range(1, life + 1))
    return (capex + opex * finance.annuity(target, life)) / pv_e
