"""Wereldwijde uitbreiding. Run: PYTHONPATH=src python3 -m eti.wereld [stap ...]
Zonder sleutel: meer_zones, tasmanie, nasa, worldbank, owid_co2, uk, japan, vs (pakket gridstatus), vs_eia.
Nieuw op 17 november: eia_opwek (EIA_API_KEY) en balans_probe (ENTSOE_TOKEN), beide voor de nachtrun.
Met gratis sleutel (omgevingsvariabele): ember (EMBER_API_KEY), eia_gas (EIA_API_KEY),
onbalans (ENTSOE_TOKEN). Zonder sleutel wordt zo'n stap netjes overgeslagen."""
import csv, io, json, os, sys, time, traceback, urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from . import battery, extra, live, nacht, nacht2

OUT, RAW = nacht2.OUT, nacht2.RAW
log, _w, _cached = extra.log, nacht2._w, nacht2._cached
UA = {"User-Agent": "Mozilla/5.0 (solar-storage-investment-lab, research)"}


def _get(url, path, binary=False, headers=None, data=None):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, "rb" if binary else "r", encoding=None if binary else "utf-8").read()
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=120) as r:
                data_in = r.read()
            if not data_in:
                raise ValueError("leeg antwoord")
            data_out = data_in
            open(path, "wb").write(data_out); time.sleep(1)
            return data_out if binary else data_out.decode("utf-8", "replace")
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** (attempt + 1))


# 1. Alle overige Europese biedzones in Energy-Charts
MEER_ZONES = [("LT", "lt", "Litouwen"), ("LV", "lv", "Letland"), ("HR", "hr", "Kroatie"), ("BG", "bg", "Bulgarije"),
              ("SK", "sk", "Slowakije"), ("RS", "rs", "Servie"), ("DK2", "dk", "Denemarken (Oost)"),
              ("NO1", "no", "Noorwegen (Oslo)"), ("NO3", "no", "Noorwegen (Midden)"), ("NO4", "no", "Noorwegen (Noord)"),
              ("NO5", "no", "Noorwegen (West)"), ("SE1", "se", "Zweden (Noord)"), ("SE2", "se", "Zweden (Noord-Midden)"),
              ("SE4", "se", "Zweden (Zuid)"), ("IT-South", "it", "Italie (Zuid)"), ("IT-Centre-North", "it", "Italie (Midden-Noord)"),
              ("IT-Sicily", "it", "Italie (Sicilie)")]
def meer_zones():
    nacht2.ALL_COUNTRIES[:] = nacht2.ALL_COUNTRIES + MEER_ZONES
    nacht2.meer_landen()


# 2. Tasmanie erbij in Australie
def tasmanie():
    nacht2.AEMO_REGIOS.append(("TAS1", "Australie (Tasmanie)", -42.88, 147.33))
    nacht2.australie()


# 3. NASA POWER: dagelijkse instraling en wind wereldwijd (geen sleutel)
LOCATIES = [("Nederland", 52.1, 5.2), ("Duitsland", 51.0, 10.0), ("Spanje", 40.0, -3.7), ("Italie", 41.9, 12.5),
            ("Polen", 52.2, 21.0), ("Zweden", 59.3, 18.1), ("VK", 52.5, -1.5), ("Texas", 31.0, -100.0),
            ("Californie", 35.4, -119.0), ("Chili (Atacama)", -23.6, -70.4), ("Brazilie", -15.8, -47.9),
            ("India (Rajasthan)", 27.0, 73.0), ("China (Qinghai)", 36.6, 101.8), ("Japan", 35.7, 139.7),
            ("Australie (Zuid)", -34.9, 138.6), ("Zuid-Afrika", -29.0, 24.0), ("Marokko", 31.0, -7.0),
            ("Egypte (Benban)", 24.5, 32.7), ("Saoedi-Arabie", 24.7, 46.7), ("Kenia", -1.3, 36.8),
            ("Nigeria", 9.1, 7.4), ("Indonesie", -6.2, 106.8), ("Vietnam", 11.0, 107.0), ("Mexico", 25.0, -103.0)]
def parse_nasa(d):
    p = d["properties"]["parameter"]
    return [(k, p["ALLSKY_SFC_SW_DWN"][k], p.get("WS50M", {}).get(k)) for k in sorted(p["ALLSKY_SFC_SW_DWN"])]
def nasa():
    jaar, rows = defaultdict(lambda: [0.0, 0]), []
    for naam, lat, lon in LOCATIES:
        try:
            d = _cached(f"nasa_{naam.split()[0]}_{lat}_{lon}.json", "https://power.larc.nasa.gov/api/temporal/daily/point",
                        {"parameters": "ALLSKY_SFC_SW_DWN,WS50M", "community": "RE", "latitude": lat, "longitude": lon,
                         "start": "20150101", "end": time.strftime("%Y%m%d"), "format": "JSON"})
            for k, sw, ws in parse_nasa(d):
                if sw is not None and sw >= 0:
                    jaar[(naam, k[:4])][0] += sw; jaar[(naam, k[:4])][1] += 1
            log(f"  NASA {naam} klaar")
        except Exception as e:
            log(f"  NASA {naam} OVERGESLAGEN: {e}")
    for (naam, y), (kwh, n) in sorted(jaar.items()):
        if n >= 330:
            ghi = kwh * 365 / n
            rows.append([naam, int(y), ghi, ghi * 0.80])     # vollasturen ~ GHI x prestatieratio 0,8 (vaste opstelling)
    _w("fact_instraling_wereld.csv", ["locatie", "jaar", "ghi_kwh_m2", "vollasturen_schatting"], rows)


# 4. World Bank: toegang, aandeel hernieuwbaar, BBP, uitstoot (geen sleutel)
WB = {"EG.ELC.ACCS.ZS": "toegang_elektriciteit_pct", "EG.ELC.RNEW.ZS": "hernieuwbaar_in_opwek_pct",
      "EG.FEC.RNEW.ZS": "hernieuwbaar_in_eindverbruik_pct", "NY.GDP.PCAP.CD": "bbp_per_hoofd_usd",
      "SP.POP.TOTL": "bevolking", "EN.GHG.CO2.PC.CE.AR5": "co2_per_hoofd_t", "FR.INR.LEND": "rente_leningen_pct"}
def parse_wb(payload, name):
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        return []
    return [(r["country"]["value"], r["countryiso3code"], int(r["date"]), name, r["value"])
            for r in payload[1] if r.get("value") is not None]
def worldbank():
    rows = []
    for code, name in WB.items():
        try:
            d = _cached(f"wb_{code}.json", f"https://api.worldbank.org/v2/country/all/indicator/{code}",
                        {"format": "json", "per_page": 20000, "date": "2000:2025"})
            rows += parse_wb(d, name); log(f"  World Bank {name} klaar")
        except Exception as e:
            log(f"  World Bank {name} OVERGESLAGEN: {e}")
    _w("fact_worldbank.csv", ["land", "iso3", "jaar", "indicator", "waarde"], rows)


# 5. OWID CO2-dataset
def owid_co2():
    txt = _get("https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv", f"{RAW}/owid-co2-data.csv")
    cols = ["country", "iso_code", "year", "co2", "co2_per_capita", "co2_per_gdp", "share_global_co2",
            "coal_co2", "gas_co2", "oil_co2", "total_ghg", "population", "gdp"]
    rows = [[r.get(c, "") for c in cols] for r in csv.DictReader(io.StringIO(txt))
            if r["year"] and int(r["year"]) >= 2000 and r["iso_code"]]
    _w("fact_owid_co2.csv", cols, rows)


# 6. Verenigd Koninkrijk: Elexon (marktindex day-ahead en onbalansprijs), geen sleutel
def uk():
    from datetime import date, timedelta
    mi = []
    d0, today = date(2019, 1, 1), date.today()
    while d0 < today:
        d1 = min(d0 + timedelta(days=7), today)
        try:
            d = _cached(f"elexon_mi_{d0}.json", "https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index",
                        {"from": f"{d0}T00:00Z", "to": f"{d1}T00:00Z", "dataProviders": "APXMIDP", "format": "json"})
            for r in d.get("data", d if isinstance(d, list) else []):
                if r.get("price") is not None and r.get("volume") and r["startTime"][:10] < str(d1):
                    mi.append([r["startTime"][:16].replace("T", " "), r["price"]])
        except Exception as e:
            log(f"  UK marktindex week {d0} OVERGESLAGEN: {e}")
        if d0.month == 1 and d0.day <= 7:
            log(f"  UK {d0.year} gestart")
        d0 = d1
    _w("fact_uk_prijs.csv", ["timestamp_utc", "prijs_gbp_mwh"], mi)
    _uur_markt("Verenigd Koninkrijk", mi, 1.17, lat=52.5, lon=-1.5)


def _lokale_dag(k, offset):
    """Dag in lokale tijd: zo vallen het middagdal en de avondpiek in dezelfde dag en mist de batterij geen cyclus."""
    if not offset:
        return k[:10]
    from datetime import datetime, timedelta
    return (datetime.strptime(k[:16], "%Y-%m-%d %H:%M") + timedelta(hours=offset)).strftime("%Y-%m-%d")


def weernaam(naam):
    """Naam van het weerbestand per markt. Texas krijgt een eigen bestand: het deelt het voorvoegsel VS met Californie."""
    return "VS_Texas" if "Texas" in naam else naam.split()[0]


def _kernmaten(keys, P, rad, dag_offset):
    """Uren, gemiddelde prijs, capture zon (instraling als profiel), negatieve uren en de batterij van 2 uur."""
    days = defaultdict(list)
    for k, p in zip(keys, P):
        days[_lokale_dag(k, dag_offset)].append(p)
    full = [v for v in days.values() if len(v) == 24]
    bat = battery.naive_forecast_arbitrage(full, 1, 2, 0.88) * 365 / len(full) if len(full) > 30 else None
    return [len(P), sum(P) / len(P), nacht2.proxy_capture(P, [rad.get(k) for k in keys]), sum(1 for p in P if p < 0), bat]


KOP_MARKT = ["markt", "jaar", "uren", "gem_prijs_eur", "capture_zon_instraling", "negatieve_uren",
             "batterij_2u_realistisch_eur_per_mw"]


def _vervang(bestand, naam, rows):
    """Schrijft de rijen van een markt in een tabel en laat de andere markten staan."""
    f = os.path.join(OUT, bestand)
    old = [r for r in csv.reader(open(f))][1:] if os.path.exists(f) else []
    _w(bestand, KOP_MARKT, [r for r in old if r[0] != naam] + rows)


def _uur_markt(naam, pts, fx, lat, lon, dag_offset=0, halfjaar_tot=None):
    """Zelfde kernmaten voor een markt buiten Energy-Charts: capture zon (instraling als profiel), negatieve uren, batterij.
    Met halfjaar_tot (bijvoorbeeld "06-24") komt er een tweede tabel bij met alleen de lokale dagen van 1 januari tot en
    met die datum: zo zijn jaren te vergelijken met een jaar waarvan de data halverwege ophouden."""
    uur = defaultdict(list)
    for t, p in pts:
        uur[t[:13] + ":00"].append(float(p))
    rows, half = [], []
    for y in sorted({k[:4] for k in uur}):
        try:
            keys = sorted(k for k in uur if k.startswith(y))
            P = [sum(uur[k]) / len(uur[k]) * fx for k in keys]
            end = min(f"{y}-12-31", time.strftime("%Y-%m-%d"))
            wd = _cached(f"weer_{weernaam(naam)}_{y}.json", "https://archive-api.open-meteo.com/v1/archive",
                         {"latitude": lat, "longitude": lon, "start_date": f"{y}-01-01", "end_date": end,
                          "hourly": "shortwave_radiation,wind_speed_100m,temperature_2m,cloud_cover", "timezone": "UTC"})
            rad = nacht2.straling_per_beginuur(nacht2.parse_openmeteo(wd))
            rows.append([naam, int(y)] + _kernmaten(keys, P, rad, dag_offset))
            if halfjaar_tot:
                deel = [(k, p) for k, p in zip(keys, P) if f"{y}-01-01" <= _lokale_dag(k, dag_offset) <= f"{y}-{halfjaar_tot}"]
                if len(deel) > 30 * 24:
                    half.append([naam, int(y)] + _kernmaten([k for k, _ in deel], [p for _, p in deel], rad, dag_offset))
        except Exception as e:
            log(f"  {naam} {y} OVERGESLAGEN: {e}")
    _vervang("fact_wereld_markten.csv", naam, rows)
    if halfjaar_tot:
        _vervang("fact_vs_halfjaar.csv", naam, half)


# 7. Japan: JEPX spotprijzen (CSV per fiscaal jaar), systeemprijs per halfuur
def parse_jepx(text):
    pts = []
    for r in csv.reader(text.splitlines()):
        try:
            d = r[0].replace("/", "-"); slot = int(r[1]); price = float(r[5])     # kolom 6 = systeemprijs (JPY/kWh)
        except (ValueError, IndexError):
            continue
        h, mnt = divmod((slot - 1) * 30, 60)
        from datetime import datetime, timedelta
        t = datetime.strptime(f"{d} {h:02d}:{mnt:02d}", "%Y-%m-%d %H:%M") - timedelta(hours=9)   # JST -> UTC
        pts.append((t.strftime("%Y-%m-%d %H:%M"), price * 1000))                              # JPY/kWh -> JPY/MWh
    return pts
def japan():
    pts = []
    for fy in range(2019, 2027):
        try:
            ref = {"Referer": "https://www.jepx.jp/electricpower/market-data/spot/", "X-Requested-With": "XMLHttpRequest"}
            try:
                raw = _get(f"https://www.jepx.jp/js/csv_read.php?dir=spot_summary&file=spot_summary_{fy}.csv",
                           f"{RAW}/jepx_{fy}.csv", binary=True, headers=ref)
            except Exception:
                raw = _get("https://www.jepx.jp/_download.php", f"{RAW}/jepx_{fy}.csv", binary=True,
                           headers={**ref, "Content-Type": "application/x-www-form-urlencoded"},
                           data=f"dir=spot_summary&file=spot_summary_{fy}.csv".encode())
            txt = raw.decode("shift_jis", "replace")
            pts += parse_jepx(txt); log(f"  Japan FY{fy} klaar")
        except Exception as e:
            log(f"  Japan FY{fy} OVERGESLAGEN: {e}")
    _uur_markt("Japan (systeemprijs)", pts, 0.0060, lat=35.7, lon=139.7, dag_offset=9)


# 8. VS: Californie via het pakket gridstatus (OASIS) en het EIA-archief; Texas via het EIA-archief
def _caiso_maand(g, y, m, loc):
    path = f"{RAW}/CAISO_{y}_{m:02d}.csv"
    if os.path.exists(path) and os.path.getsize(path) > 50:
        return path
    start = f"{y}-{m:02d}-01"; end = min(f"{y + (m == 12)}-{(m % 12) + 1:02d}-01", time.strftime("%Y-%m-%d"))
    for poging in range(3):
        try:
            df = g.get_lmp(date=start, end=end, market="DAY_AHEAD_HOURLY", locations=[loc])
            if len(df):
                df[["Interval Start", "LMP"]].to_csv(path, index=False); return path
        except Exception as e:
            fout = e
        time.sleep(20 * (poging + 1))
    return None


def vs():
    try:
        import gridstatus
    except ImportError:
        raise RuntimeError("pakket gridstatus ontbreekt: pip install gridstatus")
    from datetime import datetime, timezone
    def lees(path, pts):
        for r in csv.DictReader(open(path)):
            t = datetime.fromisoformat(r["Interval Start"]).astimezone(timezone.utc)
            pts.append((t.strftime("%Y-%m-%d %H:%M"), r["LMP"]))
    # Californie: OASIS levert per aanvraag hooguit een maand en bewaart ruim drie jaar
    pts, g = [], gridstatus.CAISO()
    for y in range(2023, 2027):
        n = 0
        for m in range(1, 13):
            if f"{y}-{m:02d}-01" >= time.strftime("%Y-%m-%d"):
                break
            p = _caiso_maand(g, y, m, "TH_SP15_GEN-APND")
            if p:
                lees(p, pts); n += 1
        log(f"  VS Californie {y}: {n} maanden")
    log("  VS: maandbestanden bijgewerkt; de stap vs_eia rekent Californie en Texas uit")


EIA_CSV = "https://www.eia.gov/electricity/wholesalemarkets/csv/"


def parse_eia_lmp(text, kolom):
    """EIA-archief met uurprijzen per hub of zone -> [(begin van het uur 'YYYY-MM-DD HH:MM' in UTC, prijs in USD per MWh)].
    De eerste kolom is het einde van het uur in UTC; lege cellen vallen weg."""
    from datetime import datetime, timedelta
    regels = text.splitlines()
    kop = next(i for i, r in enumerate(regels) if r.startswith("UTC Timestamp"))
    if kolom not in next(csv.reader([regels[kop]])):
        raise KeyError(kolom)
    pts = []
    for r in csv.DictReader(regels[kop:]):
        try:
            p = float(r[kolom])
            t = datetime.strptime(r["UTC Timestamp (Interval Ending)"][:16], "%Y-%m-%d %H:%M") - timedelta(hours=1)
        except (ValueError, TypeError):
            continue
        pts.append((t.strftime("%Y-%m-%d %H:%M"), p))
    return pts


def voeg_samen(eia, oasis, grens="2025-01-01"):
    """Het EIA-archief tot de grens; OASIS voor de uren die het archief mist en voor alles vanaf de grens."""
    uur = {t[:13] + ":00": float(p) for t, p in oasis}
    uur.update({t[:13] + ":00": float(p) for t, p in eia if t < grens})
    return sorted(uur.items())


def _oasis_punten():
    """Uurprijzen SP15 uit de maandbestanden die de stap vs heeft opgehaald (tijd in UTC)."""
    from datetime import datetime, timezone
    pts = []
    for y in range(2023, 2027):
        for m in range(1, 13):
            path = f"{RAW}/CAISO_{y}_{m:02d}.csv"
            if os.path.exists(path) and os.path.getsize(path) > 50:
                for r in csv.DictReader(open(path)):
                    t = datetime.fromisoformat(r["Interval Start"]).astimezone(timezone.utc)
                    pts.append((t.strftime("%Y-%m-%d %H:%M"), r["LMP"]))
    return pts


def _eia_punten():
    """Uurprijzen uit het EIA-archief: (Texas, gemiddelde van de hubs; Californie, SP15), beide in dollar per MWh."""
    tx, ca = [], []
    for y in range(2020, 2026):
        for naam, bestand, kolom, doel in (("Texas", f"ercot_lmp_da_hr_hubs_{y}.csv", "Hub average LMP", tx),
                                           ("Californie", f"caiso_lmp_da_hr_zones_{y}.csv", "SP-15 LMP", ca)):
            try:
                doel += parse_eia_lmp(_get(EIA_CSV + bestand, f"{RAW}/eia_{bestand}"), kolom)
                log(f"  EIA {naam} {y} klaar")
            except Exception as e:
                log(f"  EIA {naam} {y} OVERGESLAGEN: {e}")
    return tx, ca


def parse_gridstatus(payload, kolom="spp"):
    """Antwoord van gridstatus.io -> [(begin van het uur 'YYYY-MM-DD HH:MM' in UTC, prijs in dollar per MWh)]."""
    pts = []
    for r in payload.get("data") or []:
        try:
            pts.append((r["interval_start_utc"][:16].replace("T", " "), float(r[kolom])))
        except (KeyError, TypeError, ValueError):
            continue
    return pts


def _json_met_sleutel(url, path, kop):
    """Haalt json op met de sleutel in de kopregel (dus niet in het adres) en bewaart het antwoord."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return json.load(open(path, encoding="utf-8"))
    for poging in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **kop}), timeout=120) as r:
                d = json.loads(r.read().decode("utf-8"))
            json.dump(d, open(path, "w", encoding="utf-8")); time.sleep(2)
            return d
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or poging == 3:
                raise
        except (urllib.error.URLError, ConnectionError, json.JSONDecodeError):
            if poging == 3:
                raise
        time.sleep(5 * (poging + 1))


def texas_gridstatus():
    """Texas (gemiddelde van de hubs, day-ahead) via gridstatus.io: vult de uren die het EIA-archief mist en alles na
    24 juni 2025. Sleutel: GRIDSTATUS_API_KEY in .env. Geeft een lege lijst zonder sleutel of bij een fout."""
    key = os.environ.get("GRIDSTATUS_API_KEY")
    if not key:
        log("  gridstatus overgeslagen: zet GRIDSTATUS_API_KEY (gratis via gridstatus.io) voor Texas na juni 2025"); return []
    vandaag, pts = time.strftime("%Y-%m-%d"), []
    for y in range(2021, 2027):
        if f"{y}-01-01" >= vandaag:
            break
        pagina, n = 1, 0
        while True:
            stempel = f"_{vandaag.replace('-', '')}" if str(y) == vandaag[:4] else ""        # het lopende jaar elke dag opnieuw
            try:
                d = _json_met_sleutel("https://api.gridstatus.io/v1/datasets/ercot_spp_day_ahead_hourly/query?" + urllib.parse.urlencode(
                    {"start_time": f"{y}-01-01T00:00:00Z", "end_time": f"{y + 1}-01-01T00:00:00Z", "filter_column": "location",
                     "filter_value": "HB_HUBAVG", "page": pagina}), f"{RAW}/gridstatus_ercot_hubavg_{y}_{pagina}{stempel}.json",
                    {"x-api-key": key})
            except Exception as e:
                log(f"  gridstatus Texas {y} pagina {pagina} OVERGESLAGEN: {type(e).__name__}"); break
            deel = parse_gridstatus(d)
            pts += deel; n += len(deel)
            if not deel or not (d.get("meta") or {}).get("hasNextPage"):
                break
            pagina += 1
        log(f"  gridstatus Texas {y}: {n} uren")
    return pts


def vergelijk(a, b):
    """Aantal gedeelde uren en het grootste absolute verschil tussen twee prijsreeksen."""
    x, y = {t[:13]: float(p) for t, p in a}, {t[:13]: float(p) for t, p in b}
    samen = [abs(x[t] - y[t]) for t in x if t in y]
    return len(samen), (max(samen) if samen else None)


def vs_eia():
    """Texas en Californie uit het EIA-archief met uurprijzen (zonder sleutel; ERCOT zelf weigert verzoeken van buiten
    de VS). Het archief loopt van 2020 tot en met 24 juni 2025; met een sleutel van gridstatus.io komen de ontbrekende uren en
    alles daarna erbij. Texas: gemiddelde van de hubs, instraling in het midden van de staat. Californie (SP15): het archief tot en met 2024, OASIS voor de gaten en voor alles vanaf 2025."""
    tx, ca = _eia_punten()
    extra = texas_gridstatus()
    if tx and extra:
        n, grootste = vergelijk(tx, extra)
        log(f"  Texas: EIA en gridstatus delen {n} uren, grootste verschil {grootste} dollar per MWh; EIA telt waar beide bestaan")
    tx = voeg_samen(tx, extra, grens="9999") if tx else tx
    if tx:
        _uur_markt("VS Texas (ERCOT)", tx, 0.86, lat=31.0, lon=-100.0, dag_offset=-6, halfjaar_tot="06-24")
    if ca:
        _uur_markt("VS Californie (CAISO)", voeg_samen(ca, _oasis_punten()), 0.86, lat=35.4, lon=-119.0, dag_offset=-8,
                   halfjaar_tot="06-24")
    else:
        log("  EIA-archief niet bereikbaar: Californie en Texas blijven ongewijzigd")


# 8b. VS: uurlijkse opwek per brandstof (EIA-API). Geeft het echte zonprofiel, kernenergie en het batterijvermogen.
def parse_eia_opwek(payload):
    """EIA v2 electricity/rto/fuel-type-data -> [(begin van het uur 'YYYY-MM-DD HH:00' in UTC, brandstofcode, MWh)].
    EIA stempelt deze uurdata op het eind van het uur (formulier EIA-930: 'hour ending'). De prijzen in dit project staan
    op het begin van het uur, dus hier gaat er een uur af. Zonder die stap loopt de opwek een uur achter op de prijs."""
    from datetime import datetime, timedelta
    rows = []
    for r in (payload.get("response") or {}).get("data") or []:
        try:
            begin = datetime.strptime(r["period"][:13], "%Y-%m-%dT%H") - timedelta(hours=1)
            rows.append((begin.strftime("%Y-%m-%d %H:00"), r["fueltype"], float(r["value"])))
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def opwek_kengetallen(rijen, prijs):
    """rijen: [(uur, brandstof, MWh)], prijs: {uur: prijs} -> per jaar en brandstof [jaar, brandstof, TWh, aandeel in de
    opwek, capture rate, aandeel van de productie in negatieve uren, hoogste uurwaarde in MW, uren met prijs].
    Laden van opslag (negatieve waarden) telt niet mee als opwek. Dubbele uren tellen een keer."""
    uniek = {(u, b): v for u, b, v in rijen}
    per_uur, groep = defaultdict(float), defaultdict(list)
    for (u, b), v in uniek.items():
        v = max(v, 0.0)
        per_uur[u] += v
        groep[(u[:4], b)].append((u, v))
    totaal, prijs_som, prijs_n = defaultdict(float), defaultdict(float), defaultdict(int)
    for u, v in per_uur.items():
        totaal[u[:4]] += v
        if u in prijs:
            prijs_som[u[:4]] += prijs[u]; prijs_n[u[:4]] += 1
    out = []
    for jaar, b in sorted(groep):
        reeks = groep[(jaar, b)]
        gem = prijs_som[jaar] / prijs_n[jaar] if prijs_n[jaar] else None
        som = sum(v for _, v in reeks)
        met = [(prijs[u], v) for u, v in reeks if u in prijs]
        volume = sum(v for _, v in met)
        capture = (sum(p * v for p, v in met) / volume) / gem if volume and gem else None
        negatief = sum(v for p, v in met if p < 0) / volume if volume else None
        out.append([int(jaar), b, som / 1e6, som / totaal[jaar] if totaal[jaar] else None, capture, negatief,
                    max((v for _, v in reeks), default=None), len(met)])
    return out


def eia_opwek():
    """Uurlijkse opwek per brandstof voor Texas (ERCO) en Californie (CISO) vanaf 2020. De ruwe pagina's blijven in
    data/raw staan; de tabel fact_vs_opwek_jaar.csv geeft per markt, jaar en brandstof de kengetallen."""
    key = os.environ.get("EIA_API_KEY")
    if not key:
        log("  EIA-opwek overgeslagen: zet EIA_API_KEY (gratis via eia.gov/opendata)"); return
    from datetime import datetime, timedelta
    tx, ca = _eia_punten()
    tx = voeg_samen(tx, texas_gridstatus(), grens="9999")
    prijzen = {"VS Texas (ERCOT)": {t[:13] + ":00": float(p) for t, p in tx},
               "VS Californie (CAISO)": dict(voeg_samen(ca, _oasis_punten()))}
    uit = []
    for ba, markt in (("ERCO", "VS Texas (ERCOT)"), ("CISO", "VS Californie (CAISO)")):
        rijen = []
        for y in range(2020, 2027):
            for m in range(1, 13):
                if f"{y}-{m:02d}-01" >= time.strftime("%Y-%m-%d"):
                    break
                laatste = datetime(y + (m == 12), (m % 12) + 1, 1) - timedelta(hours=1)
                offset = 0
                while True:
                    try:
                        d = _cached(f"eia_fuel_{ba}_{y}_{m:02d}_{offset}.json", "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/",
                                    {"api_key": key, "frequency": "hourly", "data[0]": "value", "facets[respondent][]": ba,
                                     "start": f"{y}-{m:02d}-01T00", "end": laatste.strftime("%Y-%m-%dT%H"),
                                     "sort[0][column]": "period", "sort[0][direction]": "asc", "offset": offset, "length": 5000})
                    except Exception as e:
                        log(f"  EIA-opwek {ba} {y}-{m:02d} OVERGESLAGEN: {type(e).__name__}"); break
                    deel = parse_eia_opwek(d)
                    rijen += deel
                    if len(deel) < 5000:
                        break
                    offset += 5000
            log(f"  EIA-opwek {ba} {y}: {len(rijen)} rijen tot nu")
        rijen = [r for r in rijen if r[0] >= "2020"]             # het uur dat op 31 december 2019 begint is geen jaar
        uit += [[markt] + r for r in opwek_kengetallen(rijen, prijzen[markt])]
    if uit:
        _w("fact_vs_opwek_jaar.csv", ["markt", "jaar", "brandstof", "twh", "aandeel_opwek", "capture_rate", "aandeel_in_negatieve_uren",
                                      "hoogste_uur_mw", "uren_met_prijs"], uit)


# 8c. Nederland: welke balanceringsreeksen geeft ENTSO-E? Ruwe antwoorden bewaren; de verwerking volgt daarna.
NL_REGELZONE = "10YNL----------L"
BALANS_KANDIDATEN = [
    ("prijs_geactiveerd", {"documentType": "A84"}),
    ("prijs_geactiveerd_afrr", {"documentType": "A84", "businessType": "A96"}),
    ("prijs_geactiveerd_picasso", {"documentType": "A84", "processType": "A67", "businessType": "A96"}),
    ("prijs_reserves_dag", {"documentType": "A89", "type_MarketAgreement.Type": "A01"}),
    ("prijs_reserves_dag_afrr", {"documentType": "A89", "type_MarketAgreement.Type": "A01", "businessType": "A96"}),
    ("reserves_dag", {"documentType": "A81", "type_MarketAgreement.Type": "A01"}),
    ("reserves_dag_afrr", {"documentType": "A81", "type_MarketAgreement.Type": "A01", "businessType": "A96"}),
    ("reserves_dag_fcr", {"documentType": "A81", "type_MarketAgreement.Type": "A01", "businessType": "A95"}),
    ("reserves_afrr_proces", {"documentType": "A81", "type_MarketAgreement.Type": "A01", "businessType": "B95", "processType": "A51"}),
    ("reserves_fcr_proces", {"documentType": "A81", "type_MarketAgreement.Type": "A01", "businessType": "B95", "processType": "A52"}),
    ("geactiveerd_volume", {"documentType": "A83"}),
    ("onbalans_volume", {"documentType": "A86"}),
]


def _haal_ruw(url, path):
    """Haalt een bestand op en bewaart het. Bij een foutcode komt de melding van de bron in pad + '.fout' en is de
    uitkomst None. Het adres zelf (met de sleutel erin) wordt nergens weggeschreven."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, "rb").read()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            data = r.read()
        open(path, "wb").write(data)
        return data
    except urllib.error.HTTPError as e:
        open(path + ".fout", "wb").write(f"HTTP {e.code}\n".encode() + (e.read() or b""))
    except Exception as e:
        open(path + ".fout", "wb").write(type(e).__name__.encode())
    finally:
        time.sleep(1)
    return None


def heeft_data(data):
    """Een antwoord van ENTSO-E met reeksen erin: een zip, of xml met een TimeSeries (geen foutbericht)."""
    return bool(data) and (data[:2] == b"PK" or (b"TimeSeries" in data and b"Acknowledgement_MarketDocument" not in data[:2000]))


def balans_probe():
    """Vraagt voor Nederland twaalf balanceringsreeksen op (prijzen en volumes van regelvermogen en reserves) voor twee
    proefweken. Reeksen die data geven, worden daarna voor alle maanden vanaf 2023 opgehaald. Alleen ruwe bestanden:
    de verwerking tot tabellen volgt als duidelijk is welke reeksen bestaan."""
    tok = os.environ.get("ENTSOE_TOKEN")
    if not tok:
        log("  Balansprobe overgeslagen: zet ENTSOE_TOKEN (gratis via transparency.entsoe.eu)"); return
    def vraag(extra, start, end, path):
        return _haal_ruw("https://web-api.tp.entsoe.eu/api?" + urllib.parse.urlencode(
            {"securityToken": tok, "controlArea_Domain": NL_REGELZONE, "periodStart": start, "periodEnd": end, **extra}), path)
    goed = []
    for naam, extra in BALANS_KANDIDATEN:
        treffers = 0
        for start, end in (("202406030000", "202406100000"), ("202609070000", "202609140000")):
            data = vraag(extra, start, end, f"{RAW}/balans_probe_{naam}_{start[:8]}.bin")
            treffers += heeft_data(data)
            log(f"  balans {naam} {start[:8]}: {len(data) if data else 0} bytes, {'data' if heeft_data(data) else 'geen data'}")
        if treffers:
            goed.append((naam, extra))
    for naam, extra in goed:
        n = 0
        for y in range(2023, 2027):
            for m in range(1, 13):
                if f"{y}-{m:02d}-01" >= time.strftime("%Y-%m-%d"):
                    break
                data = vraag(extra, f"{y}{m:02d}010000", f"{y + (m == 12)}{(m % 12) + 1:02d}010000", f"{RAW}/balans_{naam}_{y}_{m:02d}.bin")
                n += heeft_data(data)
        log(f"  balans {naam}: {n} maanden met data")
    log(f"  balansprobe klaar: {len(goed)} van de {len(BALANS_KANDIDATEN)} reeksen geven data")


# 9-11. Bronnen met gratis sleutel
def ember():
    key = os.environ.get("EMBER_API_KEY")
    if not key:
        log("  Ember overgeslagen: zet EMBER_API_KEY (gratis via ember-energy.org)"); return
    d = _cached("ember_yearly.json", "https://api.ember-energy.org/v1/electricity-generation/yearly",
                {"api_key": key, "start_date": "2000", "is_aggregate_series": "false"})
    rows = [[r.get("entity"), r.get("entity_code"), r.get("date"), r.get("series"), r.get("generation_twh"),
             r.get("share_of_generation_pct")] for r in d.get("data", [])]
    _w("fact_ember_opwek.csv", ["land", "iso3", "jaar", "bron", "twh", "aandeel_pct"], rows)


def eia_gas():
    key = os.environ.get("EIA_API_KEY")
    if not key:
        log("  EIA overgeslagen: zet EIA_API_KEY (gratis via eia.gov/opendata)"); return
    d = _cached("eia_henryhub.json", "https://api.eia.gov/v2/natural-gas/pri/fut/data/",
                {"api_key": key, "frequency": "daily", "data[0]": "value", "facets[series][]": "RNGWHHD", "start": "2010-01-01", "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 5000})
    rows = [[r["period"], r["value"]] for r in d.get("response", {}).get("data", [])]
    _w("fact_gas_henryhub.csv", ["datum", "usd_mmbtu"], rows)


def onbalans():
    tok = os.environ.get("ENTSOE_TOKEN")
    if not tok:
        log("  Onbalans overgeslagen: zet ENTSOE_TOKEN (gratis via transparency.entsoe.eu)"); return
    import xml.etree.ElementTree as ET
    rows = []
    for y in range(2023, 2027):
        for m in range(1, 13):
            start = f"{y}{m:02d}010000"
            if f"{y}-{m:02d}-01" >= time.strftime("%Y-%m-%d"):
                break
            end = f"{y + (m == 12)}{(m % 12) + 1:02d}010000"
            path = f"{RAW}/imb_NL_{y}_{m:02d}.xml"
            try:
                xml = _get("https://web-api.tp.entsoe.eu/api?" + urllib.parse.urlencode(
                    {"securityToken": tok, "documentType": "A85", "controlArea_Domain": "10YNL----------L",
                     "periodStart": start, "periodEnd": end}), path, binary=True)
                docs = [xml]
                if xml[:2] == b"PK":
                    import zipfile, io
                    z = zipfile.ZipFile(io.BytesIO(xml)); docs = [z.read(n) for n in z.namelist()]
                for el in (e for d in docs for e in ET.fromstring(d).iter()):
                    if el.tag.endswith("Point"):
                        pos = price = None
                        for c in el:
                            if c.tag.endswith("position"): pos = int(c.text)
                            if c.tag.endswith("amount"): price = float(c.text)
                        if price is not None:
                            rows.append([y, m, pos, price])
            except Exception as e:
                log(f"  Onbalans {y}-{m:02d} OVERGESLAGEN: {e}")
    from . import herijk
    herijk.schrijf_onbalans()      # kwartierprijzen op tijdstip; tekort (A05) en overschot (A04) apart; A03-posities opgevuld


STEPS = [meer_zones, tasmanie, nasa, worldbank, owid_co2, uk, japan, vs, vs_eia, eia_opwek, balans_probe, ember, eia_gas, onbalans]

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
    log(f"== wereld klaar {time.strftime('%H:%M')}")
