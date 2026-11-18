"""Herstelt de onbetrouwbare kolommen in fact_land_jaar.
- aandeel_zon / aandeel_wind: vervangen door Ember (landniveau); de Energy-Charts-waarde blijft in *_energycharts.
- capture_zon ontbreekt (geen zonnedata in de bron): aangevuld met instraling als profiel (Open-Meteo), kolom capture_bron.
- capture_zon uit een opwekreeks die maar een deel van het jaar beslaat: afgekeurd (kolom zon_dekking), de gemeten waarde
  blijft staan in capture_zon_gemeten en zon_proxy vult het gat daarna met instraling.
Run: PYTHONPATH=src python3 -m eti.herstel [ember_aandeel] [dekking] [zon_proxy]"""
import csv, glob, json, os, sys, time
import pandas as pd
from . import live, nacht2
from .extra import log

OUT, EMBER = "powerbi/data", "data/ember_global/release_generation_yearly_global.csv"
ISO = {"Belgie": "BEL", "Bulgarije": "BGR", "Denemarken": "DNK", "Duitsland": "DEU", "Estland": "EST", "Finland": "FIN",
       "Frankrijk": "FRA", "Griekenland": "GRC", "Hongarije": "HUN", "Italie": "ITA", "Kroatie": "HRV", "Letland": "LVA",
       "Litouwen": "LTU", "Nederland": "NLD", "Noorwegen": "NOR", "Oostenrijk": "AUT", "Polen": "POL", "Portugal": "PRT",
       "Roemenie": "ROU", "Servie": "SRB", "Slovenie": "SVN", "Slowakije": "SVK", "Spanje": "ESP", "Tsjechie": "CZE",
       "Zweden": "SWE", "Zwitserland": "CHE"}
COORD = {"NL": (52.1, 5.2), "DE-LU": (51.0, 10.0), "BE": (50.6, 4.6), "FR": (46.6, 2.4), "ES": (40.0, -3.7), "DK1": (56.0, 9.0),
         "DK2": (55.6, 12.0), "IT-North": (45.5, 9.5), "IT-Centre-North": (43.5, 11.5), "IT-South": (40.8, 15.5),
         "IT-Sicily": (37.5, 14.0), "PL": (52.0, 19.0), "NO1": (60.0, 10.8), "NO2": (58.5, 7.5), "NO3": (63.4, 10.4),
         "NO4": (68.5, 17.0), "NO5": (60.4, 5.3), "SE1": (66.5, 20.0), "SE2": (63.0, 16.5), "SE3": (59.3, 16.0),
         "SE4": (56.0, 14.0), "AT": (47.6, 14.1), "CH": (46.8, 8.2), "CZ": (49.8, 15.5), "HU": (47.2, 19.5),
         "PT": (39.5, -8.0), "GR": (39.0, 22.5), "FI": (62.0, 26.0), "EE": (58.7, 25.5), "RO": (45.9, 25.0),
         "SI": (46.1, 14.8), "LT": (55.2, 23.9), "LV": (56.9, 24.6), "HR": (45.3, 16.0), "BG": (42.7, 25.3),
         "SK": (48.7, 19.5), "RS": (44.0, 20.9)}
F = os.path.join(OUT, "fact_land_jaar.csv")


def ember_aandeel():
    L = pd.read_csv(F)
    e = pd.read_csv(EMBER, low_memory=False, usecols=["ISO 3 code", "Year", "Electricity source", "Share of generation (%)"])
    L["iso3"] = L["land"].str.split(" ").str[0].map(ISO)
    for bron, kol in (("Solar", "aandeel_zon"), ("Wind", "aandeel_wind")):
        if kol + "_energycharts" not in L:
            L[kol + "_energycharts"] = L[kol]
        s = e[e["Electricity source"] == bron].rename(columns={"ISO 3 code": "iso3", "Year": "jaar", "Share of generation (%)": "_v"})
        L = L.drop(columns=[c for c in ("_v",) if c in L]).merge(s[["iso3", "jaar", "_v"]], on=["iso3", "jaar"], how="left")
        L[kol] = L["_v"] / 100          # Ember; leeg als Ember het jaar nog niet heeft (bv. lopend jaar)
        L = L.drop(columns="_v")
    L.to_csv(F, index=False)
    nl = L[(L.land == "Nederland") & (L.jaar == 2025)].iloc[0]
    log(f"  aandelen vervangen door Ember: NL 2025 zon {nl.aandeel_zon:.1%} (was {nl.aandeel_zon_energycharts:.1%})")


DREMPEL_DEKKING = 0.75


def maanddekking(bzn, jaar, cache_dir="data/raw"):
    """Aandeel van de maanden waarin de bron zonne-opwek boven nul geeft. Leest alleen de bewaarde bestanden; None als die er niet zijn."""
    maanden = met_zon = 0
    for pad in sorted(glob.glob(os.path.join(cache_dir, f"power_{bzn}_{jaar}_??.json"))):
        with open(pad, encoding="utf-8") as fh:
            soorten = json.load(fh).get("production_types", [])
        maanden += 1
        met_zon += any(v for t in soorten if t.get("name") == "Solar" for v in t.get("data", []) if v and v > 0)
    return met_zon / maanden if maanden else None


def dekking(drempel=DREMPEL_DEKKING, cache_dir="data/raw"):
    """Keurt gemeten capture rates af als de opwekreeks maar een deel van het jaar beslaat.

    Voorbeeld: de Zweedse zonreeks begint eind 2021. De capture rate van dat jaar weegt dan alleen de wintermaanden,
    toen de prijs door de gascrisis ver boven het jaargemiddelde lag, en komt uit op 3,5. Dat zegt niets over zon."""
    L = pd.read_csv(F)
    for kolom in ("zon_dekking", "capture_zon_gemeten"):
        if kolom not in L:
            L[kolom] = float("nan")
    L["capture_bron"] = L["capture_bron"].astype(object)
    n = 0
    for i, r in L[L.capture_bron.astype(str).str.startswith("opwek")].iterrows():
        d = maanddekking(r.biedzone, int(r.jaar), cache_dir)
        if d is None:
            continue
        L.loc[i, "zon_dekking"] = round(d, 3)
        if d < drempel:
            L.loc[i, "capture_zon_gemeten"], L.loc[i, "capture_zon"], L.loc[i, "capture_bron"] = r.capture_zon, float("nan"), ""
            n += 1
            log(f"  {r.land} {int(r.jaar)}: opwekreeks dekt {d:.0%} van de maanden, capture {r.capture_zon:.2f} afgekeurd")
    L.to_csv(F, index=False); log(f"  -> {n} gemeten capture rates afgekeurd (dekking onder {drempel:.0%})")
    return n


def zon_proxy():
    """Vult lege capture rates met instraling als profiel. Schrijft na elke gevulde rij, zodat een afgebroken run verder kan."""
    L = pd.read_csv(F)
    if "capture_bron" not in L:
        L["capture_bron"] = L["capture_zon"].notna().map({True: "opwek (Energy-Charts)", False: ""})
    L["capture_bron"] = L["capture_bron"].astype(object)
    n = 0
    for i, r in L[L.capture_zon.isna()].iterrows():
        try:
            lat, lon = COORD[r.biedzone]; y = int(r.jaar)
            end = min(f"{y}-12-31", time.strftime("%Y-%m-%d"))
            if os.environ.get("ETI_OFFLINE") and not os.path.exists(os.path.join(nacht2.RAW, f"weer_{r.biedzone}_{y}.json")):
                log(f"  {r.land} {y}: geen bewaard weer, zonder netwerk overgeslagen"); continue
            wd = nacht2._cached(f"weer_{r.biedzone}_{y}.json", "https://archive-api.open-meteo.com/v1/archive",          # eerst het weer: mislukt dat, dan hoeven de prijzen niet
                                {"latitude": lat, "longitude": lon, "start_date": f"{y}-01-01", "end_date": end,
                                 "hourly": "shortwave_radiation,wind_speed_100m,temperature_2m,cloud_cover", "timezone": "UTC"})
            rad = nacht2.straling_per_beginuur(nacht2.parse_openmeteo(wd))
            rows = live.fetch_energy_charts(y, bzn=r.biedzone, country=next(c for b, c, _ in nacht2.ALL_COUNTRIES + MEER if b == r.biedzone))
            P = [p for _, p, _ in rows]
            cr = nacht2.proxy_capture(P, [rad.get(t.strftime("%Y-%m-%d %H:%M")) for t, _, _ in rows])
            if cr is not None:
                L.loc[i, "capture_zon"] = cr; L.loc[i, "capture_bron"] = "instraling (Open-Meteo, proxy)"; n += 1
                L.to_csv(F, index=False)
                log(f"  {r.land} {y}: capture zon (proxy) {cr:.3f}")
        except Exception as e:
            log(f"  {r.land} {int(r.jaar)} proxy OVERGESLAGEN: {e}")
    L.to_csv(F, index=False); log(f"  -> {n} ontbrekende capture rates aangevuld")

try:
    from .wereld import MEER_ZONES as MEER
except Exception:
    MEER = []
def zon_proxy_opnieuw():
    """Rekent alle capture rates uit instraling opnieuw uit (bijvoorbeeld na een correctie in het profiel) en vult daarna de gaten."""
    L = pd.read_csv(F)
    oud = L.capture_bron.astype(str).str.startswith("instraling")
    L.loc[oud, "capture_zon"] = float("nan")
    L.to_csv(F, index=False); log(f"  {int(oud.sum())} waarden uit instraling leeggemaakt voor herberekening")
    zon_proxy()


STEPS = [ember_aandeel, dekking, zon_proxy]
EXTRA = {"zon_proxy_opnieuw": zon_proxy_opnieuw}
if __name__ == "__main__":
    for fn in STEPS + [EXTRA[n] for n in sys.argv[1:] if n in EXTRA]:
        if sys.argv[1:] and fn.__name__ not in sys.argv[1:]:
            continue
        log(f"== herstel {fn.__name__}"); fn()
