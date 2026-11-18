"""Reference solutions for docs/exercises.md (tested in tests/test_solutions.py)."""
from eti import finance


def kw_to_kwh(kw, minutes):                                     # E01
    return kw * minutes / 60


def capacity_factor(mwh_per_year, mw, hours=8760):              # E02
    return mwh_per_year / (mw * hours)


def merit_order_price(plants, demand_mw):                       # E04
    """plants: [(name, capacity_mw, marginal_cost)]. Cheapest first; the last plant needed sets the price."""
    supplied = 0.0
    for name, cap, cost in sorted(plants, key=lambda p: p[2]):
        supplied += cap
        if supplied >= demand_mw:
            return cost, name
    raise ValueError("demand exceeds capacity")


def capture_price(prices, generation):                          # E05
    return sum(p * g for p, g in zip(prices, generation)) / sum(generation)


def ppa_settlement(market_price, ppa_price, mwh):               # E08
    """Financial (contract-for-difference style) PPA, seen from the producer: positive = buyer pays producer."""
    return (ppa_price - market_price) * mwh


def simple_payback(capex, yearly_cash):                         # E10
    return capex / yearly_cash


def real_rate(nominal, inflation):                              # E12
    return (1 + nominal) / (1 + inflation) - 1


def irr_of(cashflows):                                          # E13
    return finance.irr(cashflows)


def j_curve(commitment, calls, distributions):                  # E16
    """Cumulative net cash flow of a fund investor per year (negative first: the J-curve)."""
    cum, out = 0.0, []
    for c, d in zip(calls, distributions):
        cum += -c * commitment + d * commitment
        out.append(round(cum, 2))
    return out


def tvpi(distributions, nav, paid_in):                          # E17
    return (distributions + nav) / paid_in


def fund_of_funds_exposure(n_funds, companies_per_fund, overlap_share=0.0):   # E18
    return round(n_funds * companies_per_fund * (1 - overlap_share))


def hourly_match(consumption, clean_supply):                    # E21
    """Share of consumption matched by clean supply in the same hour (24/7 CFE score)."""
    matched = sum(min(c, s) for c, s in zip(consumption, clean_supply))
    return matched / sum(consumption)


def annual_match(consumption, clean_supply):                    # E21
    return min(1.0, sum(clean_supply) / sum(consumption))


def datacenter_energy(mw_it, pue, hours=8760):                  # E23
    """Yearly electricity (MWh) for an IT load in MW and a power usage effectiveness."""
    return mw_it * pue * hours


def grid_tariff_effect(spread_eur_mwh, tariff_eur_mwh, cycles, mwh_per_cycle):   # E26
    """Yearly battery margin before and after a per-MWh transport tariff charged on charging and discharging."""
    before = spread_eur_mwh * cycles * mwh_per_cycle
    after = (spread_eur_mwh - 2 * tariff_eur_mwh) * cycles * mwh_per_cycle
    return before, after
