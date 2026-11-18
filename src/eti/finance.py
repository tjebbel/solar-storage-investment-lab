"""Investment metrics: NPV, IRR, LCOE, debt sizing, Monte Carlo."""
import random


def npv(rate, cashflows):
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))


def irr(cashflows, low=-0.99, high=1.0, tol=1e-7):
    f_low = npv(low, cashflows)
    if f_low * npv(high, cashflows) > 0:
        raise ValueError("no sign change: IRR not found")
    while high - low > tol:
        mid = (low + high) / 2
        f_mid = npv(mid, cashflows)
        if f_low * f_mid <= 0:
            high = mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


def lcoe(capex, opex, mwh, rate, years, degradation=0.0):
    costs = capex + sum(opex / (1 + rate) ** t for t in range(1, years + 1))
    energy = sum(mwh * (1 - degradation) ** (t - 1) / (1 + rate) ** t for t in range(1, years + 1))
    return costs / energy


def project_cashflows(capex, revenue, opex, years, degradation=0.0):
    return [-capex] + [revenue * (1 - degradation) ** (t - 1) - opex for t in range(1, years + 1)]


def max_debt(cfads, dscr_target, rate):
    """Sculpted debt capacity: present value of CFADS / DSCR at the loan rate."""
    return sum(c / dscr_target / (1 + rate) ** t for t, c in enumerate(cfads, start=1))


def irr_safe(cashflows):
    """IRR, or NaN when the cash flows never pay back (no sign change): a loss-making year, not a crash."""
    try:
        return irr(cashflows)
    except ValueError:
        return float("nan")


def monte_carlo_irr(capex, revenue, opex, years, sd, n=1000, seed=1, degradation=0.0):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        r = rng.gauss(revenue, sd * revenue)
        try:
            v = irr_safe(project_cashflows(capex, r, opex, years, degradation))
            if v == v:
                out.append(v)
        except ValueError:
            continue
    return sorted(out)


def percentile(sorted_values, p):
    if not sorted_values:
        return float("nan")
    k = (len(sorted_values) - 1) * p / 100
    lo = int(k)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (k - lo)


def annuity(rate, years):
    return years if rate == 0 else (1 - (1 + rate) ** -years) / rate


def required_uplift(capex, revenue, opex, years, degradation, target_irr):
    """Extra constant yearly revenue needed to reach target_irr (NPV at target = 0)."""
    base = npv(target_irr, project_cashflows(capex, revenue, opex, years, degradation))
    return max(0.0, -base / annuity(target_irr, years))
