"""Market analytics: capture rate, cannibalisation, negative prices."""


def capture_rate(prices, generation):
    pairs = [(p, g) for p, g in zip(prices, generation) if p is not None]
    revenue = sum(p * g for p, g in pairs)
    volume = sum(g for _, g in pairs)
    mean_price = sum(p for p, _ in pairs) / len(pairs)
    return (revenue / volume) / mean_price


def negative_hours(prices):
    return sum(1 for p in prices if p is not None and p < 0)


def ols(x, y):
    """Simple least squares: slope, intercept, R²."""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_res = sum((b - (intercept + slope * a)) ** 2 for a, b in zip(x, y))
    ss_tot = sum((b - my) ** 2 for b in y)
    return slope, intercept, 1 - ss_res / ss_tot
