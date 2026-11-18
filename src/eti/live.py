"""Live data connectors.

* Energy-Charts API (Fraunhofer ISE), no registration: day-ahead prices (/price) and
  public net generation per production type (/public_power). Attribution required:
  "Data: Energy-Charts.info (Fraunhofer ISE)". Price data may carry licence terms of the
  original provider (e.g. EPEX SPOT): fetch at runtime, do not redistribute raw prices.
* ENTSO-E Transparency Platform: needs a personal token in the environment variable
  ENTSOE_TOKEN. Parsing lives in eti.data.parse_entsoe_xml.

HTTP and parsing are separated so that parsing is unit-tested offline with fixtures.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

ENERGY_CHARTS = "https://api.energy-charts.info"
ATTRIBUTION = "Data: Energy-Charts.info (Fraunhofer ISE); prices originate from the day-ahead market (EPEX SPOT)."

# production-type name (lower case, substring match) -> technology in the warehouse
TECH_MAP = [("solar", "solar"), ("wind offshore", "wind"), ("wind onshore", "wind"),
            ("fossil gas", "gas"), ("hard coal", "coal"), ("lignite", "coal"), ("fossil oil", "oil"),
            ("nuclear", "nuclear"), ("biomass", "biomass"), ("waste", "waste"),
            ("hydro run", "hydro"), ("other renewable", "other_renewable")]
EXCLUDE = ("load", "share", "cross border", "consumption", "residual")


def http_get_json(url, params, retries=6, timeout=90):
    """GET with exponential back-off on 429/5xx and on broken connections (IncompleteRead, timeouts).
    Raises on other 4xx client errors."""
    import http.client, socket
    full = url + "?" + urllib.parse.urlencode(params)
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(full, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise
        except (http.client.IncompleteRead, urllib.error.URLError, socket.timeout,
                ConnectionError, json.JSONDecodeError):
            if attempt < retries:
                time.sleep(2 ** attempt)        # 2, 4, 8, 16, 32 s
                continue
            raise


def parse_prices(payload):
    """Energy-Charts /price JSON -> [(datetime_utc, price or None)]."""
    secs, prices = payload.get("unix_seconds") or [], payload.get("price") or []
    if len(secs) != len(prices):
        raise ValueError("unix_seconds and price differ in length")
    return [(datetime.fromtimestamp(s, tz=timezone.utc), p) for s, p in zip(secs, prices)]


def map_technology(name):
    n = name.lower()
    if any(x in n for x in EXCLUDE):
        return None
    for key, tech in TECH_MAP:
        if key in n:
            return tech
    return None


def parse_generation(payload):
    """Energy-Charts /public_power JSON (MW) -> {datetime_utc: {technology: MW}}."""
    secs = payload.get("unix_seconds") or []
    out = defaultdict(lambda: defaultdict(float))
    for series in payload.get("production_types") or []:
        tech = map_technology(series["name"])
        if tech is None:
            continue
        for s, v in zip(secs, series["data"]):
            if v is not None:
                out[datetime.fromtimestamp(s, tz=timezone.utc)][tech] += max(v, 0.0)
    return out


def to_hourly(points):
    """Average sub-hourly values per UTC hour. Average MW over one hour = MWh in that hour.
    Works for 15-minute (since 1 Oct 2025) and hourly data alike. None values are skipped;
    an hour without any value becomes None."""
    buckets = defaultdict(list)
    for t, v in points:
        buckets[t.replace(minute=0, second=0, microsecond=0)].append(v)
    out = []
    for hour in sorted(buckets):
        vals = [v for v in buckets[hour] if v is not None]
        out.append((hour, round(sum(vals) / len(vals), 2) if vals else None))
    return out


def generation_hourly(gen):
    techs = sorted({k for d in gen.values() for k in d})
    hourly = {}
    for tech in techs:
        for hour, v in to_hourly([(t, d.get(tech)) for t, d in gen.items()]):
            hourly.setdefault(hour, {})[tech] = v or 0.0
    return hourly


def combine(prices_hourly, gen_hourly):
    """Rows for warehouse.load: (ts_utc, price, {technology: MWh}). Hours without generation are dropped."""
    return [(t, p, gen_hourly[t]) for t, p in prices_hourly if t in gen_hourly]


def fetch_energy_charts(year, bzn="NL", country="nl", cache_dir="data/raw"):
    """Download one year (month by month, polite and resumable) and cache the raw JSON."""
    os.makedirs(cache_dir, exist_ok=True)
    price_pts, gen = [], {}
    for month in range(1, 13):
        start = f"{year}-{month:02d}-01"
        end = f"{year + (month == 12)}-{(month % 12) + 1:02d}-01"
        today = time.strftime("%Y-%m-%d")
        if start >= today:                         # running year: stop at today
            break
        end = min(end, today)
        for kind, url, params in (("price", f"{ENERGY_CHARTS}/price", {"bzn": bzn, "start": start, "end": end}),
                                  ("power", f"{ENERGY_CHARTS}/public_power", {"country": country, "start": start, "end": end})):
            path = os.path.join(cache_dir, f"{kind}_{bzn}_{year}_{month:02d}.json")
            if os.path.exists(path):
                payload = json.load(open(path, encoding="utf-8"))
            else:
                payload = http_get_json(url, params)
                json.dump(payload, open(path, "w", encoding="utf-8"))
                time.sleep(1)                      # be polite to a free public API
            if kind == "price":
                price_pts += parse_prices(payload)
            else:
                gen.update(parse_generation(payload))
    rows = combine(to_hourly(price_pts), generation_hourly(gen))
    return [r for r in rows if r[0].year == year]   # drop the 23:00 UTC hour of 31 Dec of the previous year
