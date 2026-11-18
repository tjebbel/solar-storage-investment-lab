"""Impact metrics: avoided emissions with an hourly grid factor versus a yearly average."""


def avoided_solar_tonnes(generation, grid_kg_per_mwh):
    """(hourly method, yearly-average method) in tonnes CO2."""
    hourly = sum(g * f for g, f in zip(generation, grid_kg_per_mwh)) / 1000
    avg_factor = sum(grid_kg_per_mwh) / len(grid_kg_per_mwh)
    yearly_avg = sum(generation) * avg_factor / 1000
    return hourly, yearly_avg


def battery_shift_tonnes(daily_factors, schedule, mw, hours, efficiency):
    """Emissions avoided by charging in a cleaner block and discharging in a dirtier one."""
    total = 0.0
    for factors, pair in zip(daily_factors, schedule):
        if pair is None:
            continue
        i, j = pair
        charge = sum(factors[i:i + hours]) / hours
        discharge = sum(factors[j:j + hours]) / hours
        total += mw * hours * (discharge * efficiency - charge) / 1000
    return total
