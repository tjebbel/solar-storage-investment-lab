"""Battery arbitrage: one cycle per day, perfect foresight (an upper bound)."""


def best_daily_spread(prices, hours, efficiency):
    """Best (discharge*eff - charge) block profit per MW in one day, O(n). Returns (gain, (i, j))."""
    blocks = [sum(prices[i:i + hours]) / hours for i in range(len(prices) - hours + 1)]
    best, best_pair = 0.0, None
    cheapest, cheapest_i = float("inf"), None
    for j in range(hours, len(blocks)):
        if blocks[j - hours] < cheapest:
            cheapest, cheapest_i = blocks[j - hours], j - hours
        gain = (blocks[j] * efficiency - cheapest) * hours
        if gain > best:
            best, best_pair = gain, (cheapest_i, j)
    return best, best_pair


def yearly_arbitrage(daily_prices, mw, hours, efficiency):
    """Sum over days. daily_prices: list of per-day price lists without None."""
    total, schedule = 0.0, []
    for day in daily_prices:
        gain, pair = best_daily_spread(day, hours, efficiency)
        total += gain * mw
        schedule.append(pair)
    return total, schedule


def naive_forecast_arbitrage(daily_prices, mw, hours, efficiency):
    """Realistic bound: plan today's cycle on yesterday's prices, settle at today's prices."""
    total = 0.0
    for prev, day in zip(daily_prices, daily_prices[1:]):
        _, pair = best_daily_spread(prev, hours, efficiency)
        if pair is None:
            continue
        i, j = pair
        gain = (sum(day[j:j + hours]) * efficiency - sum(day[i:i + hours]))
        total += max(gain, 0.0) * mw          # operator skips a cycle that would lose money (intraday check)
    return total * len(daily_prices) / max(1, len(daily_prices) - 1)


def naive_forecast_daily(daily_prices, hours, efficiency):
    """Per-day gain per MW of the plan-on-yesterday strategy (losing cycles skipped): the terms of naive_forecast_arbitrage."""
    out = []
    for prev, day in zip(daily_prices, daily_prices[1:]):
        _, pair = best_daily_spread(prev, hours, efficiency)
        if pair is None:
            out.append(0.0)
            continue
        i, j = pair
        out.append(max(sum(day[j:j + hours]) * efficiency - sum(day[i:i + hours]), 0.0))
    return out
