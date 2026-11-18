"""Maakt de DAX-maten toetsbaar zonder Power BI te hebben gedraaid.

Schrijft drie dingen:
- powerbi/data/dim_datum.csv: de datumtabel waar het model om vroeg (een rij per dag, met week, kwartaal en feestdag).
- powerbi/maten_analyse.dax: de maten plus een toetsvraag. Plak het geheel in de DAX-queryweergave van Power BI of Fabric
  en druk op Uitvoeren; 'Model bijwerken' zet de maten daarna in het model.
- powerbi/maten_verwacht.csv: wat die toetsvraag hoort terug te geven, hier in Python uitgerekend op dezelfde tabel.
Zo is de toets in Power BI een vergelijking van twee tabellen in plaats van een oordeel op het oog.

De maten gebruiken alleen kolommen van fact_land_maand, dus er is geen relatie of berekende kolom voor nodig.
Gebruik:  PYTHONPATH=src python3 -m eti.powerbi_toets
          PYTHONPATH=src python3 -m eti.powerbi_toets vergelijk export.csv   (uitkomst uit Power BI naast de verwachting)
"""
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

DATA, MAP = "powerbi/data", "powerbi"
LCOE = 67.39                                                  # euro per MWh, Nederland 2025 (fact_regio_jaar)
KRAP = 5.0
LAND, JAAR = "Nederland", 2026
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"]
DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]

DAX = '''// Maten voor de signalering, met een toetsvraag. Niet in Power BI uitgevoerd: vergelijk de uitkomst met maten_verwacht.csv.
// Plakken in: Power BI Desktop of Fabric > DAX-queryweergave > Uitvoeren. 'Model bijwerken met wijzigingen' voegt de maten toe.
DEFINE
    MEASURE fact_land_maand[Gem prijs] = AVERAGE ( fact_land_maand[gem_prijs] )
    MEASURE fact_land_maand[Capture rate zon] = AVERAGE ( fact_land_maand[capture_zon] )
    MEASURE fact_land_maand[Capture-prijs zon] = [Gem prijs] * [Capture rate zon]
    MEASURE fact_land_maand[LCOE] = {lcoe}      // Nederland 2025; vervang door een parameter of door fact_regio_jaar[lcoe_eur_mwh]
    MEASURE fact_land_maand[Marge zon] = [Capture-prijs zon] - [LCOE]
    MEASURE fact_land_maand[Status zon] =
        SWITCH ( TRUE (), ISBLANK ( [Marge zon] ), BLANK (), [Marge zon] < 0, "Kosten niet gedekt", [Marge zon] < {krap}, "Krap", "Gedekt" )
    MEASURE fact_land_maand[Prijs z-score] =
        // de gekozen maand tegenover de twaalf maanden ervoor, voor hetzelfde land
        VAR p = MAXX ( fact_land_maand, fact_land_maand[jaar] * 12 + fact_land_maand[maand] )
        VAR venster =
            FILTER (
                ALL ( fact_land_maand[jaar], fact_land_maand[maand] ),
                fact_land_maand[jaar] * 12 + fact_land_maand[maand] >= p - 12
                    && fact_land_maand[jaar] * 12 + fact_land_maand[maand] < p
            )
        VAR gem = CALCULATE ( AVERAGE ( fact_land_maand[gem_prijs] ), venster )
        VAR sd = CALCULATE ( STDEV.S ( fact_land_maand[gem_prijs] ), venster )
        RETURN DIVIDE ( [Gem prijs] - gem, sd )
    MEASURE fact_land_maand[Prijs signaal] =
        SWITCH ( TRUE (), ISBLANK ( [Prijs z-score] ), BLANK (), ABS ( [Prijs z-score] ) >= 3, "Schok", ABS ( [Prijs z-score] ) >= 2, "Let op", "Gewoon" )
    MEASURE fact_nl_uur_alle_jaren[Dagen sinds laatste meting] =
        DATEDIFF ( MAX ( fact_nl_uur_alle_jaren[timestamp_utc] ), UTCNOW (), DAY )

// Toetsvraag: {land}, {jaar}, per maand. Hoort gelijk te zijn aan maten_verwacht.csv (afronding op twee decimalen).
EVALUATE
SUMMARIZECOLUMNS (
    fact_land_maand[land],
    fact_land_maand[jaar],
    fact_land_maand[maand],
    TREATAS ( {{ "{land}" }}, fact_land_maand[land] ),
    TREATAS ( {{ {jaar} }}, fact_land_maand[jaar] ),
    "Gem prijs", ROUND ( [Gem prijs], 2 ),
    "Capture-prijs zon", ROUND ( [Capture-prijs zon], 2 ),
    "Marge zon", ROUND ( [Marge zon], 2 ),
    "Status zon", [Status zon],
    "Prijs z-score", ROUND ( [Prijs z-score], 2 ),
    "Prijs signaal", [Prijs signaal]
)
ORDER BY fact_land_maand[maand]
'''


def pasen(jaar):
    a, b, c = jaar % 19, jaar // 100, jaar % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    maand, dag = divmod(h + m - 7 * n + 114, 31)
    return date(jaar, maand, dag + 1)


def feestdagen(jaar):
    p = pasen(jaar)
    koningsdag = date(jaar, 4, 26) if date(jaar, 4, 27).weekday() == 6 else date(jaar, 4, 27)
    return {date(jaar, 1, 1): "Nieuwjaarsdag", p: "Eerste paasdag", p + timedelta(1): "Tweede paasdag", koningsdag: "Koningsdag", date(jaar, 5, 5): "Bevrijdingsdag",
            p + timedelta(39): "Hemelvaartsdag", p + timedelta(49): "Eerste pinksterdag", p + timedelta(50): "Tweede pinksterdag", date(jaar, 12, 25): "Eerste kerstdag",
            date(jaar, 12, 26): "Tweede kerstdag"}


def dim_datum(van=2019, tot=2030):
    """Een rij per dag, aaneengesloten en met hele jaren: dat is wat Power BI van een datumtabel vraagt."""
    d = pd.DataFrame({"datum": pd.date_range(f"{van}-01-01", f"{tot}-12-31", freq="D")})
    vrij = {dag: naam for jaar in range(van, tot + 1) for dag, naam in feestdagen(jaar).items()}
    iso = d.datum.dt.isocalendar()
    d["jaar"], d["kwartaal"], d["maand"], d["dag"] = d.datum.dt.year, d.datum.dt.quarter, d.datum.dt.month, d.datum.dt.day
    d["maandnaam"] = d.maand.map(lambda m: MAANDEN[m - 1])
    d["jaarmaand"] = d.datum.dt.strftime("%Y-%m")
    d["jaarkwartaal"] = d.jaar.astype(str) + " K" + d.kwartaal.astype(str)
    d["isojaar"], d["week"] = iso.year.astype(int), iso.week.astype(int)
    d["weekdag_nr"] = d.datum.dt.weekday + 1
    d["weekdag"] = d.weekdag_nr.map(lambda n: DAGEN[n - 1])
    d["feestdag"] = d.datum.dt.date.map(vrij).fillna("")
    d["werkdag"] = (d.weekdag_nr <= 5) & (d.feestdag == "")
    d["seizoen"] = np.where(d.maand.between(4, 9), "zomerhalfjaar", "winterhalfjaar")
    d["datum"] = d.datum.dt.strftime("%Y-%m-%d")
    return d


def verwacht(data=DATA, land=LAND, jaar=JAAR):
    """De toetsvraag uit het DAX-bestand, in pandas. Zelfde definities, zelfde afronding."""
    m = pd.read_csv(os.path.join(data, "fact_land_maand.csv"))
    m = m[m.land == land].assign(p=lambda t: t.jaar * 12 + t.maand).sort_values("p")
    rijen = []
    for _, r in m[m.jaar == jaar].iterrows():
        venster = m[(m.p >= r.p - 12) & (m.p < r.p)].gem_prijs
        z = (r.gem_prijs - venster.mean()) / venster.std(ddof=1) if len(venster) > 1 and venster.std(ddof=1) > 0 else np.nan
        capture_prijs = r.gem_prijs * r.capture_zon
        marge = capture_prijs - LCOE
        rijen.append({"land": land, "jaar": int(r.jaar), "maand": int(r.maand), "Gem prijs": round(r.gem_prijs, 2), "Capture-prijs zon": round(capture_prijs, 2), "Marge zon": round(marge, 2),
                      "Status zon": "" if marge != marge else "Kosten niet gedekt" if marge < 0 else "Krap" if marge < KRAP else "Gedekt",
                      "Prijs z-score": round(z, 2) if z == z else np.nan, "Prijs signaal": "" if z != z else "Schok" if abs(z) >= 3 else "Let op" if abs(z) >= 2 else "Gewoon"})
    return pd.DataFrame(rijen)


def main(data=DATA, map_=MAP):
    d = dim_datum()
    d.to_csv(os.path.join(data, "dim_datum.csv"), index=False)
    with open(os.path.join(map_, "maten_analyse.dax"), "w", encoding="utf-8") as fh:
        fh.write(DAX.format(lcoe=LCOE, krap=KRAP, land=LAND, jaar=JAAR))
    v = verwacht(data)
    v.to_csv(os.path.join(map_, "maten_verwacht.csv"), index=False)
    return d, v


def vergelijk(export, verwacht_pad=os.path.join(MAP, "maten_verwacht.csv"), marge=0.011):
    """Vergelijkt de uitkomst van de toetsvraag in Power BI of Fabric (geexporteerd als csv) met maten_verwacht.csv.
    Kolomnamen als 'fact_land_maand[maand]' of '[Gem prijs]' worden teruggebracht tot 'maand' en 'Gem prijs'.
    Getallen mogen 0,01 verschillen (afronding op twee decimalen); tekstkolommen moeten gelijk zijn.
    Geeft een tabel met per maand en kolom de verwachte en de gemeten waarde en of ze kloppen."""
    import re
    if str(export).lower().endswith((".xlsx", ".xls")):
        e = pd.read_excel(export)
    else:
        e = pd.read_csv(export, sep=None, engine="python")                       # komma, puntkomma of tab (plakken uit Tableau)
    e.columns = [re.sub(r"^.*\[(.*)\]$", r"\1", str(c)).strip() for c in e.columns]
    if "maand" not in e.columns:                                                 # Tableau: 'Month of Maand' met 'January 2026' of 'januari 2026'
        kol = next((c for c in e.columns if "maand" in c.lower() or "month" in c.lower()), e.columns[0])
        nl = {"januari": "January", "februari": "February", "maart": "March", "mei": "May", "juni": "June", "juli": "July",
              "augustus": "August", "oktober": "October"}
        tekst = e[kol].astype(str).str.strip()
        for a, b in nl.items():
            tekst = tekst.str.replace(a, b, case=False, regex=False)
        e["maand"] = pd.to_datetime(tekst, errors="coerce", format="mixed").dt.month
    for k in e.columns:                                                          # getallen met een decimale komma
        if not pd.api.types.is_numeric_dtype(e[k]) and k != "maand":
            omgezet = pd.to_numeric(e[k].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
            if omgezet.notna().all() and e[k].astype(str).str.contains(",").any():
                e[k] = omgezet
    v = pd.read_csv(verwacht_pad)
    m = v.merge(e, on=["maand"], how="left", suffixes=("_verwacht", "_power_bi"))
    rijen = []
    for k in [c for c in v.columns if c not in ("land", "jaar", "maand")]:
        for _, r in m.iterrows():
            a, b = r[f"{k}_verwacht"], r.get(f"{k}_power_bi")
            if isinstance(a, str) or isinstance(b, str):
                ok = str(a) == str(b)
            else:
                ok = (pd.isna(a) and pd.isna(b)) or (pd.notna(a) and pd.notna(b) and abs(float(a) - float(b)) <= marge)
            rijen.append({"maand": r.maand, "maat": k, "verwacht": a, "power_bi": b, "klopt": bool(ok)})
    uit = pd.DataFrame(rijen)
    print(f"{int(uit.klopt.sum())} van {len(uit)} waarden kloppen; maanden in de export: {int(e.maand.nunique()) if 'maand' in e else 0} van {len(v)}")
    if not uit.klopt.all():
        print(uit[~uit.klopt].to_string(index=False))
    return uit


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "vergelijk":
        u = vergelijk(sys.argv[2])
        u.to_csv(os.path.join("resultaten", "dax_vergelijking.csv"), index=False)
        raise SystemExit(0 if u.klopt.all() else 1)
    d, v = main()
    print(f"dim_datum: {len(d)} dagen, {d.datum.iloc[0]} tot en met {d.datum.iloc[-1]}")
    print(v.to_string(index=False))
