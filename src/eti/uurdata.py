"""Uuranalyses voor dashboards 16, 18, 19 en 20 (alleen Engels), uit de lokale cache in data/raw.

Bron: Energy-Charts (Fraunhofer ISE), per zone en maand: price_<zone>_<jaar>_<maand>.json (dagmarktprijs, per uur; vanaf
oktober 2025 per kwartier) en power_<zone>_<jaar>_<maand>.json (opwek per type en verbruik, per kwartier). Alles wordt naar
uurgemiddelden in lokale tijd omgezet en per zone-jaar in data/cache/ bewaard, zodat een tweede run seconden duurt.

Tabellen (kolommen en waarden direct Engels; ze staan in tableau/data en tableau/data_en):
  t53_duck_profile       zone x jaar x uur van de dag: prijs, zonaandeel van het verbruik, restlast       (dashboard 16)
  t54_duck_depth         zone x jaar: middagprijs, avondprijs, dip, negatieve uren                         (dashboard 16)
  t55_battery_arbitrage  zone x jaar: opbrengst 2-uursbatterij, 1 cyclus per dag, perfecte voorkennis      (dashboard 18)
  t56_hirth              zone: helling van de capture rate zon tegen het zonaandeel, uit maanddata (OLS)   (dashboard 19)
  t57_carbon_free        zone x jaar: koolstofvrij aandeel van de opwek, gemiddeld en per uur              (dashboard 20)
  t58_carbon_free_hour   zone x seizoen x uur van de dag: koolstofvrij aandeel                             (dashboard 20)
  t59_coverage           zone x jaar: dekt de Energy-Charts-opwek het land? zon en totaal tegen OWID/Ember   (controle)

Dekking: Energy-Charts mist voor sommige landen een groot deel van de zonne-opwek (Nederland: alleen een fractie van de
daken). Per land-jaar vergelijken we de som van de zones met OWID (Ember). Onder 60% zondekking vallen zone-jaren uit de
zonanalyses (t53 zonaandeel, t56) en uit t57/t58 (koolstofvrij); de prijsanalyses (t54, t55) blijven, want die hebben
alleen de prijs nodig. De vlag staat in elke tabel in de kolom "Solar coverage ok".

Gebruik:  PYTHONPATH=src python3 -m eti.uurdata            (alle zones; eerste keer enkele minuten)
          PYTHONPATH=src python3 -m eti.uurdata NL DE-LU   (alleen deze zones, voor een snelle proef)
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAW, CACHE = Path("data/raw"), Path("data/cache")
UIT = [Path("tableau/data"), Path("tableau/data_en")]
OOST = {"FI", "EE", "LV", "LT", "BG", "RO", "GR"}                     # Oost-Europese tijd
TZ = {"PT": "Europe/Lisbon"} | {z: "Europe/Helsinki" for z in OOST}  # rest: Midden-Europese tijd
KOOLSTOFVRIJ = ("Nuclear", "Hydro Run-of-River", "Hydro water reservoir", "Hydro pumped storage", "Wind onshore", "Wind offshore",
                "Solar", "Geothermal", "Marine", "Other renewables")
FOSSIEL = ("Fossil", "Waste", "Others", "Biomass")                   # biomassa telt niet als koolstofvrij (conservatief)
NIET_OPWEK = ("Load", "Residual load", "Renewable share of load", "Renewable share of generation",
              "Cross border electricity trading", "Hydro pumped storage consumption")
UUR_DAG = range(24)


def zones():
    return sorted({re.match(r"price_(.+)_\d{4}_\d{2}\.json", os.path.basename(p))[1] for p in glob.glob(str(RAW / "price_*_*_*.json"))})


def _reeks(t, w, tz):
    i = pd.to_datetime(np.asarray(t, dtype="int64"), unit="s", utc=True).tz_convert(tz)
    return pd.Series(pd.to_numeric(pd.Series(w), errors="coerce").to_numpy(dtype=float), index=i)


def uren(zone, jaar):
    """Uurtabel voor een zone-jaar: Price en per productietype het gemiddelde MW, in lokale tijd. Leeg als er geen data is."""
    cache = CACHE / f"uur_{zone}_{jaar}.csv.gz"
    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=False)
    tz = TZ.get(zone, "Europe/Amsterdam")
    prijs, opwek = [], []
    for p in sorted(glob.glob(str(RAW / f"price_{zone}_{jaar}_??.json"))):
        d = json.load(open(p))
        if d.get("unix_seconds"):
            prijs.append(_reeks(d["unix_seconds"], d["price"], tz))
    for p in sorted(glob.glob(str(RAW / f"power_{zone}_{jaar}_??.json"))):
        d = json.load(open(p))
        if d.get("unix_seconds"):
            opwek.append(pd.DataFrame({x["name"]: _reeks(d["unix_seconds"], x["data"], tz) for x in d["production_types"]}))
    if not prijs:
        return pd.DataFrame()
    pr = pd.concat(prijs); pr = pr[~pr.index.duplicated()].resample("h").mean()
    df = pd.DataFrame({"Price": pr})
    if opwek:
        ow = pd.concat(opwek); ow = ow[~ow.index.duplicated()].resample("h").mean()
        df = df.join(ow, how="left")
    df = df[df.index.year == jaar]
    df.index = df.index.tz_localize(None)                              # lokale kloktijd
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, compression="gzip")
    return df


def _klaar(df):
    df = df.copy(); df.index = pd.to_datetime(df.index)
    return df


def kolommen(df, start):
    return [c for c in df.columns if c.startswith(start)]


def opwek(df):
    """Totale opwek en koolstofvrije opwek per uur (MW), zonder verbruik, grenshandel en pompverbruik."""
    gen = [c for c in df.columns if c not in NIET_OPWEK and c != "Price"]
    vrij = [c for c in gen if c in KOOLSTOFVRIJ or c.startswith("Solar")]
    totaal = df[gen].clip(lower=0).sum(axis=1, min_count=1)
    return totaal, df[vrij].clip(lower=0).sum(axis=1, min_count=1)


def zon(df):
    c = [c for c in df.columns if c.startswith("Solar")]
    return df[c].sum(axis=1, min_count=1) if c else pd.Series(np.nan, index=df.index)


def profiel(df, zone, jaar):
    df = _klaar(df); z = zon(df); last = df.get("Load")
    p = pd.DataFrame({"Price": df.Price, "Solar MW": z, "Load MW": last, "Residual load MW": df.get("Residual load")})
    p["Hour"] = df.index.hour
    g = p.groupby("Hour").mean()
    g["Solar share of load %"] = 100 * g["Solar MW"] / g["Load MW"]
    g = g.reset_index(); g.insert(0, "Year", jaar); g.insert(0, "Zone", zone)
    return g


def diepte(df, zone, jaar):
    df = _klaar(df); h = df.index.hour
    mid, avond = df.Price[(h >= 11) & (h < 15)].mean(), df.Price[(h >= 18) & (h < 21)].mean()
    return dict(Zone=zone, Year=jaar, **{"Average price": df.Price.mean(), "Midday price 11-15h": mid, "Evening price 18-21h": avond,
                "Midday dip EUR/MWh": df.Price.mean() - mid, "Evening to midday ratio": avond / mid if mid > 0 else np.nan,
                "Negative hours": int((df.Price < 0).sum()), "Hours": int(df.Price.notna().sum())})


def arbitrage(df, zone, jaar, uren_opslag=2, rendement=0.88):
    """Perfecte voorkennis, 1 cyclus per dag: laden in de goedkoopste en ontladen in de duurste uren van de dag (EUR per MW per jaar)."""
    df = _klaar(df); p = df.Price.dropna()
    dag = p.groupby(p.index.date)
    marge = dag.apply(lambda s: s.nlargest(uren_opslag).sum() * rendement - s.nsmallest(uren_opslag).sum() if len(s) >= 20 else np.nan).dropna()
    return dict(Zone=zone, Year=jaar, **{"Revenue per MW": marge.sum(), "Days": len(marge), "Average daily margin EUR/MW": marge.mean(),
                "Days with margin above 100": int((marge > 100).sum()), "Storage hours": uren_opslag, "Round-trip efficiency": rendement})


def maandpunten(df, zone, jaar):
    df = _klaar(df); z = zon(df); totaal, _ = opwek(df)
    m = pd.DataFrame({"p": df.Price, "z": z, "g": totaal}).dropna()
    m = m[m.z >= 0]
    rij = []
    for mnd, s in m.groupby(m.index.month):
        if s.z.sum() <= 0 or len(s) < 500:
            continue
        cr = (s.p * s.z).sum() / s.z.sum() / s.p.mean() if s.p.mean() > 0 else np.nan
        rij.append(dict(Zone=zone, Year=jaar, Month=mnd, **{"Solar share %": 100 * s.z.sum() / s.g.sum(), "Solar capture rate": cr}))
    return rij


def hirth(maand):
    """OLS per zone: capture rate = a + b x zonaandeel (procentpunt), met maandvaste effecten weggelaten (eenvoudig, zie risico's)."""
    rij = []
    for zone, s in maand.dropna().groupby("Zone"):
        if len(s) < 24 or s["Solar share %"].std() == 0:
            continue
        x, y = s["Solar share %"].to_numpy(), s["Solar capture rate"].to_numpy()
        X = np.column_stack([np.ones_like(x), x]); b, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ b; se = np.sqrt(res @ res / (len(x) - 2) / ((x - x.mean()) ** 2).sum())
        r2 = 1 - (res @ res) / ((y - y.mean()) ** 2).sum()
        rij.append(dict(Zone=zone, **{"Slope per percentage point": b[1], "Interval low": b[1] - 1.96 * se, "Interval high": b[1] + 1.96 * se,
                        "Intercept": b[0], "R2": r2, "Months": len(s), "Max solar share %": x.max(),
                        "Capture rate at 10% share": b[0] + 10 * b[1], "Capture rate at 30% share": b[0] + 30 * b[1]}))
    h = pd.DataFrame(rij)
    if not h.empty:   # alleen betrouwbaar met genoeg spreiding in het aandeel en een redelijke fit
        h["Reliable"] = (h["Max solar share %"] >= 10) & (h.R2 >= 0.4) & (h.Months >= 36)
    return h


def koolstofvrij(df, zone, jaar):
    df = _klaar(df); totaal, vrij = opwek(df)
    a = (vrij / totaal).where(totaal > 0).clip(upper=1)
    seizoen = np.where(df.index.month.isin([4, 5, 6, 7, 8, 9]), "Summer (Apr-Sep)", "Winter (Oct-Mar)")
    uur = pd.DataFrame({"a": a, "Season": seizoen, "Hour": df.index.hour}).dropna().groupby(["Season", "Hour"]).a.mean().mul(100)
    uur = uur.rename("Carbon-free share %").reset_index(); uur.insert(0, "Year", jaar); uur.insert(0, "Zone", zone)
    jaarrij = dict(Zone=zone, Year=jaar, **{"Carbon-free share %": 100 * vrij.sum() / totaal.sum() if totaal.sum() > 0 else np.nan,
                   "Hourly matched %": 100 * a.mean(), "Hours above 90% %": 100 * (a >= 0.9).mean(), "Hours below 50% %": 100 * (a < 0.5).mean(),
                   "Hours": int(a.notna().sum())})
    return jaarrij, uur


LAND = {"AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland", "CZ": "Czechia", "DE-LU": "Germany",
        "DK": "Denmark", "EE": "Estonia", "ES": "Spain", "FI": "Finland", "FR": "France", "GR": "Greece", "HR": "Croatia",
        "HU": "Hungary", "IT": "Italy", "LT": "Lithuania", "LV": "Latvia", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
        "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia"}
DREMPEL = 0.6


def land(zone):
    return LAND.get(zone) or LAND.get(zone[:2])


def dekking(totalen):
    """totalen: rijen Zone, Year, Solar TWh, Generation TWh (Energy-Charts). Vergelijkt per land met OWID (Ember)."""
    t = pd.DataFrame(totalen)
    if t.empty:
        return t
    t["Country"] = t.Zone.map(land)
    o = pd.read_csv(RAW / "owid-energy-data.csv", usecols=["country", "year", "solar_electricity", "electricity_generation"])
    o = o.rename(columns={"country": "Country", "year": "Year", "solar_electricity": "OWID solar TWh", "electricity_generation": "OWID generation TWh"})
    laatste = o.dropna(subset=["OWID solar TWh"]).groupby("Country").Year.max()
    t["OWID year"] = [min(j, laatste.get(c, j)) for c, j in zip(t.Country, t.Year)]
    # Voor Italie, Denemarken, Noorwegen en Zweden levert Energy-Charts per zone de landcijfers: dan niet optellen.
    t["_sleutel"] = t["Solar TWh"].round(3).astype(str) + "|" + t["Generation TWh"].round(3).astype(str)
    uniek = t.drop_duplicates(["Country", "Year", "_sleutel"]).groupby(["Country", "Year"])[["Solar TWh", "Generation TWh"]].sum()
    t["Country data per zone"] = t.groupby(["Country", "Year"])["_sleutel"].transform(lambda s: s.nunique() == 1 and len(s) > 1)
    som = uniek.reindex(pd.MultiIndex.from_frame(t[["Country", "Year"]])).reset_index(drop=True)
    t = t.drop(columns="_sleutel")
    t["Country solar TWh (Energy-Charts)"], t["Country generation TWh (Energy-Charts)"] = som["Solar TWh"].to_numpy(), som["Generation TWh"].to_numpy()
    t = t.merge(o, left_on=["Country", "OWID year"], right_on=["Country", "Year"], how="left", suffixes=("", "_o")).drop(columns="Year_o")
    vol = t.Year.map(lambda j: 1.0)                                    # lopend jaar: schalen naar een heel jaar
    vol[t.Year == 2026] = 8760 / 7656
    t["Solar coverage"] = t["Country solar TWh (Energy-Charts)"] * vol / t["OWID solar TWh"]
    t["Generation coverage"] = t["Country generation TWh (Energy-Charts)"] * vol / t["OWID generation TWh"]
    t["Solar coverage ok"] = t["Solar coverage"] >= DREMPEL
    return t


def namen():
    t1 = Path("tableau/data_en/t1_zonejaar.csv")
    return pd.read_csv(t1).drop_duplicates("Zone").set_index("Zone")["Zonenaam"].to_dict() if t1.exists() else {}


def main(lijst=None, jaren=range(2019, 2027)):
    lijst = lijst or zones(); naam = namen()
    prof, diep, arb, mnd, cfe, cfu, tot = [], [], [], [], [], [], []
    for z in lijst:
        for j in jaren:
            df = uren(z, j)
            if df.empty or df.Price.notna().sum() < 24 * 60:
                continue
            arb.append(arbitrage(df, z, j)); diep.append(diepte(df, z, j))
            g, _ = opwek(_klaar(df)); tot.append(dict(Zone=z, Year=j, **{"Solar TWh": zon(_klaar(df)).sum() / 1e6, "Generation TWh": g.sum() / 1e6}))
            if any(c.startswith("Solar") for c in df.columns):
                prof.append(profiel(df, z, j)); mnd += maandpunten(df, z, j)
            if len(df.columns) > 3:
                jr, uu = koolstofvrij(df, z, j); cfe.append(jr); cfu.append(uu)
        print(f"{z}: klaar", flush=True)
    dk = dekking(tot); ok = set(map(tuple, dk.loc[dk["Solar coverage ok"], ["Zone", "Year"]].values)) if not dk.empty else set()
    vlag = lambda d: d.assign(**{"Solar coverage ok": [(z, j) in ok for z, j in zip(d.Zone, d.Year)]}) if not d.empty else d
    prof = [vlag(p) for p in prof]; cfu = [vlag(u) for u in cfu]
    mnd = [m for m in mnd if (m["Zone"], m["Year"]) in ok]
    uit = {"t59_coverage": dk, "t53_duck_profile": pd.concat(prof, ignore_index=True) if prof else pd.DataFrame(),
           "t54_duck_depth": vlag(pd.DataFrame(diep)), "t55_battery_arbitrage": pd.DataFrame(arb),
           "t56_hirth": hirth(pd.DataFrame(mnd)) if mnd else pd.DataFrame(),
           "t56b_hirth_months": pd.DataFrame(mnd),
           "t57_carbon_free": vlag(pd.DataFrame(cfe)), "t58_carbon_free_hour": pd.concat(cfu, ignore_index=True) if cfu else pd.DataFrame()}
    for t, d in uit.items():
        if d.empty:
            continue
        if "Zone" in d.columns:
            d.insert(1, "Zone name", d.Zone.map(naam).fillna(d.Zone))
        for u in UIT:
            u.mkdir(parents=True, exist_ok=True); d.to_csv(u / f"{t}.csv", index=False, float_format="%.6g")
        print(f"{t}: {len(d)} rijen")
    return uit


if __name__ == "__main__":
    main(sys.argv[1:] or None)
