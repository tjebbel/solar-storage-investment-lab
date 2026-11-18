"""Grote nachtrun: extra open data en analyses. Elke stap is onafhankelijk; een fout wordt gelogd en overgeslagen.
Run: PYTHONPATH=src python3 -m eti.nacht2 [stap ...]
Stappen: meer_landen, kwartier, vermogen, grensstromen, weer, prijsmodel, australie, onzekerheid"""
import csv, json, os, sys, time, traceback, urllib.parse
from collections import defaultdict
from datetime import datetime, timezone
from . import battery, extra, live, nacht, bootstrap

OUT = "powerbi/data"
RAW = "data/raw"
EXTRA_COUNTRIES = [("IT-North", "it", "Italie (Noord)"), ("PL", "pl", "Polen"),
                   ("NO2", "no", "Noorwegen (Zuid)"), ("SE3", "se", "Zweden (Midden)")]
EXTRA_COUNTRIES += [("AT", "at", "Oostenrijk"), ("CH", "ch", "Zwitserland"), ("CZ", "cz", "Tsjechie"),
                    ("HU", "hu", "Hongarije"), ("PT", "pt", "Portugal"), ("GR", "gr", "Griekenland"),
                    ("FI", "fi", "Finland"), ("EE", "ee", "Estland"), ("RO", "ro", "Roemenie"), ("SI", "si", "Slovenie")]
ALL_COUNTRIES = extra.COUNTRIES + EXTRA_COUNTRIES
log = extra.log


def _w(name, header, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    log(f"  -> {name}: {len(rows)} rijen")


def _cached(name, url, params):
    path = os.path.join(RAW, name)
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    payload = live.http_get_json(url, params)
    json.dump(payload, open(path, "w", encoding="utf-8"))
    time.sleep(1)
    return payload


def parse_installed(d):
    """Energy-Charts /installed_power -> [(jaar, naam_bron, GW)]."""
    years = d.get("time") or d.get("years") or []
    return [(int(str(y)[:4]), s["name"], v) for s in d.get("production_types", [])
            for y, v in zip(years, s.get("data", [])) if v is not None]


def parse_cbet(d):
    """Energy-Charts /cbet (GW per kwartier) -> {buurland: TWh}; positief = netto import, negatief = netto export."""
    secs = d.get("unix_seconds") or []
    step_h = (secs[1] - secs[0]) / 3600 if len(secs) > 1 else 1
    return {c["name"]: sum(v for v in c.get("data", []) if v is not None) * step_h / 1000 for c in d.get("countries", [])}


def parse_openmeteo(d):
    h = d["hourly"]
    return [(t.replace("T", " "), h["shortwave_radiation"][i], h["wind_speed_100m"][i], h["temperature_2m"][i],
             h.get("cloud_cover", [None] * len(h["time"]))[i]) for i, t in enumerate(h["time"])]


def straling_per_beginuur(rijen):
    """{beginuur: straling}. Open-Meteo stempelt de straling op het eind van het uur: de waarde van 12:00 is het gemiddelde
    van 11:00 tot 12:00. Prijzen en opwek staan op het begin van het uur. Zonder deze stap loopt het zonprofiel een uur
    achter op de prijs en valt de capture rate in markten met veel zon enkele punten te hoog uit."""
    from datetime import timedelta
    return {(datetime.strptime(t, "%Y-%m-%d %H:%M") - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"): r for t, r, *_ in rijen}


def parse_aemo(text, offset_h=10):
    """AEMO PRICE_AND_DEMAND csv (marktijd AEST = UTC+10) -> [(uur 'YYYY-MM-DD HH:00' UTC, gem. prijs)]."""
    from datetime import timedelta
    b = defaultdict(list)
    for r in csv.DictReader(text.splitlines()):
        try:
            t = datetime.strptime(r["SETTLEMENTDATE"], "%Y/%m/%d %H:%M:%S") - timedelta(hours=offset_h, minutes=1)
            b[t.strftime("%Y-%m-%d %H:00")].append(float(r["RRP"]))
        except (KeyError, ValueError):
            continue
    return sorted((k, sum(v) / len(v)) for k, v in b.items())


def lokale_dag(k, offset):
    """Dag in lokale markttijd voor een uur 'YYYY-MM-DD HH:00' in UTC: zo vallen middagdal en avondpiek in dezelfde dag."""
    if not offset:
        return k[:10]
    from datetime import timedelta
    return (datetime.strptime(k[:16], "%Y-%m-%d %H:%M") + timedelta(hours=offset)).strftime("%Y-%m-%d")


def proxy_capture(prices, radiation):
    """Capture rate met instraling als opwekprofiel: voor markten zonder opwekdata per bron.
    Het gemiddelde loopt over alle uren, ook de nachturen zonder zon."""
    allp = [p for p in prices if p is not None]
    pairs = [(p, r or 0.0) for p, r in zip(prices, radiation) if p is not None]
    vol = sum(r for _, r in pairs)
    if not allp or vol == 0:
        return None
    return (sum(p * r for p, r in pairs) / vol) / (sum(allp) / len(allp))


# 1. Kwartierprijzen: wat levert handelen per kwartier extra op voor een batterij?
def kwartier():
    rows = []
    for bzn, cc, naam in ALL_COUNTRIES:
        pts = []
        for y, m in [(2025, 10), (2025, 11), (2025, 12)] + [(2026, k) for k in range(1, 12)]:
            f = os.path.join(RAW, f"price_{bzn}_{y}_{m:02d}.json")
            if os.path.exists(f):
                pts += live.parse_prices(json.load(open(f, encoding="utf-8")))
        qdays, hdays = defaultdict(list), defaultdict(list)
        for t, p in pts:
            if t >= datetime(2025, 10, 1, tzinfo=timezone.utc) and p is not None:
                qdays[t.date()].append(p)
        for d, v in qdays.items():
            if len(v) == 96:
                hdays[d] = [sum(v[i:i + 4]) / 4 for i in range(0, 96, 4)]
        days = sorted(hdays)
        if len(days) < 30:
            log(f"  {naam}: te weinig kwartierdagen ({len(days)})"); continue
        for h in (1, 2):
            hr, _ = battery.yearly_arbitrage([hdays[d] for d in days], 1, h, 0.88)
            qr, _ = battery.yearly_arbitrage([qdays[d] for d in days], 0.25, h * 4, 0.88)  # 1 MW over kwartieren = 0,25 MWh per kwartier
            rows.append([naam, len(days), h, hr * 365 / len(days), qr * 365 / len(days), qr / hr - 1 if hr else None])
        log(f"  {naam}: {len(days)} dagen, kwartier-uplift 2u {rows[-1][5]:.1%}")
    _w("fact_kwartier_batterij.csv", ["land", "dagen", "uren_opslag", "omzet_uur_per_mw", "omzet_kwartier_per_mw", "uplift"], rows)


# 2. Vier extra landen in alle land-tabellen
def meer_landen():
    extra.COUNTRIES[:] = ALL_COUNTRIES
    nacht.COUNTRIES = ALL_COUNTRIES
    extra.countries()
    nacht.run()


# 3. Opgesteld vermogen per land en jaar
def vermogen():
    rows = []
    for _, cc, naam in ALL_COUNTRIES:
        try:
            d = _cached(f"installed_{cc}.json", f"{live.ENERGY_CHARTS}/installed_power",
                        {"country": cc, "time_step": "yearly", "installation_decommission": "false"})
            pts = parse_installed(d)
            rows += [[naam, y, live.map_technology(n) or n, n, v] for y, n, v in pts]
            log(f"  {naam}: vermogen {len(pts)} waarden")
        except Exception as e:
            log(f"  {naam} vermogen OVERGESLAGEN: {e}")
    _w("fact_vermogen_land.csv", ["land", "jaar", "technologie", "naam_bron", "gw"], rows)


# 4. Grensstromen Nederland per maand en buurland
def grensstromen():
    rows = []
    for y in range(2019, 2027):
        for m in range(1, 13):
            start = f"{y}-{m:02d}-01"
            if start >= time.strftime("%Y-%m-%d"):
                break
            end = f"{y + (m == 12)}-{(m % 12) + 1:02d}-01"
            try:
                d = _cached(f"cbet_nl_{y}_{m:02d}.json", f"{live.ENERGY_CHARTS}/cbet", {"country": "nl", "start": start, "end": end})
                rows += [[y, m, c, twh] for c, twh in parse_cbet(d).items()]
            except Exception as e:
                log(f"  grensstromen {y}-{m:02d} OVERGESLAGEN: {e}")
        log(f"  grensstromen {y} klaar")
    _w("fact_grensstromen_nl.csv", ["jaar", "maand", "land", "netto_import_twh"], rows)


# 5. Weer per uur (Open-Meteo, geen sleutel) op vijf locaties
LOCATIES = [("De Bilt", 52.10, 5.18), ("Groningen", 53.22, 6.57), ("Vlissingen", 51.44, 3.60),
            ("Eindhoven", 51.45, 5.38), ("Den Helder", 52.96, 4.76)]
def weer():
    rows = []
    for naam, lat, lon in LOCATIES:
        for y in range(2019, 2027):
            try:
                end = min(f"{y}-12-31", time.strftime("%Y-%m-%d"))
                d = _cached(f"weer_{naam.replace(' ', '_')}_{y}.json", "https://archive-api.open-meteo.com/v1/archive",
                            {"latitude": lat, "longitude": lon, "start_date": f"{y}-01-01", "end_date": end,
                             "hourly": "shortwave_radiation,wind_speed_100m,temperature_2m,cloud_cover", "timezone": "UTC"})
                rows += [[naam] + list(r) for r in parse_openmeteo(d)]
            except Exception as e:
                log(f"  weer {naam} {y} OVERGESLAGEN: {e}")
        log(f"  weer {naam} klaar")
    _w("fact_weer_uur.csv", ["locatie", "timestamp_utc", "straling_w_m2", "wind_100m_kmh", "temp_c", "bewolking_pct"], rows)
    # vollasturen-schatting: straling naar opbrengst met prestatieratio 0,85 (vuistregel)
    jaar = defaultdict(float)
    for r in rows:
        if r[2] is not None:
            jaar[(r[0], r[1][:4])] += r[2] / 1000 * 0.85
    _w("fact_vollasturen_schatting.csv", ["locatie", "jaar", "vollasturen_schatting"], [[k[0], int(k[1]), v] for k, v in sorted(jaar.items())])


# 6. Prijsmodel: hoe goed voorspellen weer, tijd en opwek de prijs? (lineaire regressie, per jaar)
def prijsmodel():
    import numpy as np
    weer_f = os.path.join(OUT, "fact_weer_uur.csv")
    if not os.path.exists(weer_f):
        raise RuntimeError("draai eerst de stap weer")
    w = {}
    for r in csv.DictReader(open(weer_f)):
        if r["locatie"] == "De Bilt":
            w[r["timestamp_utc"]] = r
    rows, coef_rows = [], []
    for y in range(2019, 2027):
        try:
            data = live.fetch_energy_charts(y)
        except Exception as e:
            log(f"  prijsmodel {y} OVERGESLAGEN: {e}"); continue
        X, Y, prev = [], [], {}
        for t, p, g in data:
            k = t.strftime("%Y-%m-%d %H:%M"); r = w.get(k)
            if p is None or r is None or not r["straling_w_m2"] or not r["wind_100m_kmh"]:
                continue
            lag = prev.get(t.hour)
            prev[t.hour] = p
            if lag is None:
                continue
            row = [1.0, float(r["straling_w_m2"]), float(r["wind_100m_kmh"]), float(r["temp_c"] or 0),
                   1.0 if t.weekday() >= 5 else 0.0, lag] + [1.0 if t.hour == h else 0.0 for h in range(1, 24)]
            X.append(row); Y.append(p)
        if len(Y) < 1000:
            continue
        X, Y = np.array(X), np.array(Y)
        n = len(Y); cut = int(n * 0.8)                      # train op de eerste 80%, test op de rest
        beta, *_ = np.linalg.lstsq(X[:cut], Y[:cut], rcond=None)
        pred = X[cut:] @ beta
        mae = float(np.mean(np.abs(pred - Y[cut:])))
        naive = float(np.mean(np.abs(X[cut:, 5] - Y[cut:])))   # 'prijs van gisteren zelfde uur'
        r2 = 1 - float(np.sum((Y[cut:] - pred) ** 2) / np.sum((Y[cut:] - Y[cut:].mean()) ** 2))
        rows.append([y, n, r2, mae, naive, 1 - mae / naive])
        for name, b in zip(["constante", "straling", "wind", "temperatuur", "weekend", "prijs_gisteren"], beta[:6]):
            coef_rows.append([y, name, float(b)])
        log(f"  prijsmodel {y}: R2 {r2:.2f}, MAE {mae:.1f} vs naief {naive:.1f} EUR/MWh")
    _w("fact_prijsmodel.csv", ["jaar", "uren", "r2_test", "mae_model", "mae_naief", "verbetering"], rows)
    _w("fact_prijsmodel_coef.csv", ["jaar", "variabele", "coefficient"], coef_rows)


# 7. Onzekerheid (bootstrap) opnieuw, nu voor tien landen
def onzekerheid():
    bootstrap.COUNTRIES = ALL_COUNTRIES
    bootstrap.run(10000)


# 8. Buiten Europa: Australie (AEMO, zeer veel zon) - prijzen per 5 min, zon via instraling (Open-Meteo)
AEMO_REGIOS = [("SA1", "Australie (Zuid)", -34.93, 138.60), ("VIC1", "Australie (Victoria)", -37.81, 144.96),
               ("QLD1", "Australie (Queensland)", -27.47, 153.03), ("NSW1", "Australie (NSW)", -33.87, 151.21)]
def australie():
    import urllib.request
    rows = []
    for reg, naam, lat, lon in AEMO_REGIOS:
        for y in range(2019, 2027):
            try:
                prices = {}
                for m in range(1, 13):
                    if f"{y}-{m:02d}" >= time.strftime("%Y-%m"):
                        break
                    path = os.path.join(RAW, f"aemo_{reg}_{y}{m:02d}.csv")
                    if not os.path.exists(path):
                        url = f"https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{y}{m:02d}_{reg}.csv"
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
                        with urllib.request.urlopen(req, timeout=90) as r:
                            open(path, "wb").write(r.read())
                        time.sleep(1)
                    prices.update(dict(parse_aemo(open(path, encoding="utf-8").read())))
                end = min(f"{y}-12-31", time.strftime("%Y-%m-%d"))
                wd = _cached(f"weer_{reg}_{y}.json", "https://archive-api.open-meteo.com/v1/archive",
                             {"latitude": lat, "longitude": lon, "start_date": f"{y}-01-01", "end_date": end,
                              "hourly": "shortwave_radiation,wind_speed_100m,temperature_2m,cloud_cover", "timezone": "UTC"})
                rad = straling_per_beginuur(parse_openmeteo(wd))
                keys = [k for k in sorted(prices) if k in rad]
                P = [prices[k] for k in keys]; R = [rad[k] for k in keys]
                days = defaultdict(list)
                for k, p in zip(keys, P):
                    days[lokale_dag(k, 10)].append(p)      # markttijd AEST = UTC+10: een cyclus per lokale dag
                full = [v for v in days.values() if len(v) == 24]
                bat = battery.naive_forecast_arbitrage(full, 1, 2, 0.88) * 365 / max(1, len(full)) if len(full) > 30 else None
                eur = 0.6   # AUD -> EUR (benadering)
                rows.append([naam, y, len(P), sum(P) / len(P) * eur, proxy_capture(P, R), sum(1 for p in P if p < 0),
                             bat * eur if bat else None])
                log(f"  {naam} {y}: capture (instraling) {rows[-1][4]:.2f}, negatieve uren {rows[-1][5]}")
            except Exception as e:
                log(f"  {naam} {y} OVERGESLAGEN: {e}")
    _w("fact_australie.csv", ["regio", "jaar", "uren", "gem_prijs_eur", "capture_zon_instraling", "negatieve_uren",
                             "batterij_2u_realistisch_eur_per_mw"], rows)


def australie_profiel():
    """Dagprofiel per regio en jaar over januari-oktober, dezelfde maanden in elk jaar. Toetst of een lagere batterij-omzet
    in de doorsnee dag zit (mediaan, dal en piek) of in een paar piekdagen. Leest alleen de cache van australie()."""
    import statistics as st
    eur, rows = 0.6, []     # AUD -> EUR (benadering), gelijk aan australie()
    for reg, naam, *_ in AEMO_REGIOS:
        for y in range(2019, 2027):
            prices = {}
            for m in range(1, 11):
                path = os.path.join(RAW, f"aemo_{reg}_{y}{m:02d}.csv")
                if os.path.exists(path):
                    prices.update(dict(parse_aemo(open(path, encoding="utf-8").read())))
            days = defaultdict(list)
            for k in sorted(prices):
                days[lokale_dag(k, 10)].append(prices[k])
            full = [days[d] for d in sorted(days) if len(days[d]) == 24 and d[:4] == str(y)]
            if len(full) < 250:
                log(f"  {naam} {y}: te weinig dagen ({len(full)}), overgeslagen")
                continue
            omzet = [g * eur for g in battery.naive_forecast_daily(full, 2, 0.88)]
            netto = [battery.best_daily_spread(d, 2, 0.88)[0] / 2 * eur for d in full]
            rows.append([naam, y, len(full), st.mean(omzet), st.median(omzet),
                         sum(sorted(omzet)[-10:]) / sum(omzet) if sum(omzet) else None,
                         sum(1 for d in full if max(d) > 1000), st.median(netto),
                         st.median([sum(d[10:15]) / 5 * eur for d in full]), st.median([sum(d[17:21]) / 4 * eur for d in full])])
    _w("fact_australie_dagprofiel.csv",
       ["regio", "jaar", "dagen_jan_okt", "gem_dagomzet_eur_per_mw", "mediaan_dagomzet_eur_per_mw", "aandeel_top10_dagen",
        "dagen_met_uurprijs_boven_1000_aud", "mediaan_netto_spreiding_eur_mwh", "mediaan_middagprijs_eur_mwh",
        "mediaan_avondprijs_eur_mwh"], rows)


STEPS = [meer_landen, kwartier, vermogen, grensstromen, weer, prijsmodel, australie, australie_profiel, onzekerheid]

if __name__ == "__main__":
    only = sys.argv[1:]
    for fn in STEPS:
        if only and fn.__name__ not in only:
            continue
        log(f"== {fn.__name__}  {time.strftime('%H:%M')}")
        try:
            fn()
        except Exception:
            log(traceback.format_exc())
    log(f"== klaar {time.strftime('%H:%M')}")
