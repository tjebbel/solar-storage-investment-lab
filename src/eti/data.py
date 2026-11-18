"""Data layer: synthetic hourly market data and an ENTSO-E day-ahead XML parser.

The synthetic generator makes the project run offline and in CI. Replace it with real
ENTSO-E data (see `parse_entsoe_xml`) for actual analysis.
"""
import math
import random
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

# name: (renewable, kg CO2 per MWh). ILLUSTRATIVE direct-combustion factors; replace them with
# official values (e.g. co2emissiefactoren.nl). Biomass and waste are simplified: see docs/concepts.md.
TECHNOLOGIES = {
    "solar": (True, 0.0), "wind": (True, 0.0), "hydro": (True, 0.0), "other_renewable": (True, 0.0),
    "nuclear": (False, 0.0), "biomass": (True, 0.0), "waste": (False, 300.0),
    "gas": (False, 370.0), "oil": (False, 650.0), "coal": (False, 850.0),
}


def synthetic_year(year=2024, seed=50):
    """Hourly rows: (ts_utc, price_eur_mwh or None, {technology: MWh})."""
    rng = random.Random(seed)
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    hours = (datetime(year + 1, 1, 1, tzinfo=timezone.utc) - start) // timedelta(hours=1)
    rows = []
    for h in range(hours):
        t = start + timedelta(hours=h)
        season = math.sin(math.pi * (t.timetuple().tm_yday - 80) / 183)
        sun = math.sin(math.pi * (t.hour - 5) / 14) if 5 <= t.hour <= 19 else 0.0
        solar = max(0.0, 9000 * sun * (0.55 + 0.45 * season) * rng.uniform(0.4, 1.0))
        wind = max(0.0, rng.gauss(4500 - 1200 * season, 2200))
        demand = 12500 + 2500 * (1 if 7 <= t.hour <= 21 else 0) - 1500 * season
        residual = max(1500.0, demand - solar - wind)
        coal = min(residual * 0.15, 1500.0)                     # synthetic mix uses 4 technologies
        gas = residual - coal
        price = 25 + residual * 0.009 + rng.gauss(0, 12)
        if solar + wind > demand * 0.85:
            price = -rng.uniform(0, 40)
        if rng.random() < 0.002:
            price = None
        rows.append((t, None if price is None else round(price, 2),
                     {"solar": solar, "wind": wind, "gas": gas, "coal": coal}))
    return rows


def parse_entsoe_xml(text):
    """Day-ahead price document -> [(ts_utc, price)]. Reads the namespace from the file."""
    root = ET.fromstring(text)
    ns_uri = root.tag[1:].split("}")[0] if root.tag.startswith("{") else ""
    ns = {"n": ns_uri}
    p = "n:" if ns_uri else ""
    out = []
    for period in root.iter(f"{{{ns_uri}}}Period" if ns_uri else "Period"):
        start = datetime.strptime(period.find(f"{p}timeInterval/{p}start", ns).text,
                                  "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        minutes = int(period.find(f"{p}resolution", ns).text[2:-1])
        for pt in period.findall(f"{p}Point", ns):
            pos = int(pt.find(f"{p}position", ns).text)
            out.append((start + timedelta(minutes=minutes * (pos - 1)),
                        float(pt.find(f"{p}price.amount", ns).text)))
    return out
