"""Dashboard 29 "Realistic battery" en 30 "Forecasting showcase": wat kost het om de prijzen van morgen niet te kennen?

Uit de uurcache van eti.uurdata (Energy-Charts, 37 zones). Batterij zoals t55: 2 uur, 1 cyclus per dag, 88% rendement.
  Perfecte voorkennis  laden in de 2 goedkoopste en ontladen in de 2 duurste uren van de dag zelf (bovengrens, = t55).
  Naief: gisteren      kies de uren die gisteren het goedkoopst en duurst waren; verdien de prijzen van vandaag.
  Naief: vorige week   idem met dezelfde dag een week eerder.
  Vast schema          altijd laden 11-13 uur en ontladen 18-20 uur (de duck curve als vuistregel).
De verhouding tot perfecte voorkennis is de "forecast capture": hoeveel van het plafond een strategie zonder voorspelling haalt.
Lees het als een vloer en een plafond: een echte handelaar biedt in op de day-ahead-veiling met een voorspelling en stuurt daarna
bij op de intradaymarkt; die zit ertussen. Dashboard 1 (realistisch model, NL 61k) en "gisteren" (NL 59k) liggen dicht bij elkaar.
Dezelfde naieve voorspellingen geven een basislijn voor dashboard 30: gemiddelde absolute fout (MAE) van de dagprijs per uur.
Een eigen model (dashboard 30) moet die basislijn verslaan om iets te betekenen.
Tabellen (Engels): t71_battery_strategies (zone x jaar), t72_forecast_baseline (zone x jaar: MAE gisteren / vorige week).
Gebruik: PYTHONPATH=src python3 -m eti.batterij_realistisch
"""
from pathlib import Path

import numpy as np
import pandas as pd

from eti import uurdata as u

UIT = [Path("tableau/data"), Path("tableau/data_en")]
REND, H = 0.88, 2


def dagmatrix(p):
    """Uurprijzen -> DataFrame dag x uur (0-23); dagen met ontbrekende uren vallen weg."""
    m = pd.DataFrame({"p": p.to_numpy(), "d": p.index.date, "h": p.index.hour}).pivot_table(index="d", columns="h", values="p")
    return m.dropna()


def opbrengst(m, kies):
    """kies: dag x uur met de prijzen waarop de keuze wordt gebaseerd (zelfde dagen als m); verdient met de prijzen in m."""
    k = kies.reindex(m.index).to_numpy(); v = m.to_numpy()
    ok = ~np.isnan(k).any(axis=1)
    k, v = k[ok], v[ok]
    o = np.argsort(k, axis=1, kind="stable")
    laag, hoog = o[:, :H], o[:, -H:]
    rij = np.arange(len(v))[:, None]
    return float((v[rij, hoog].sum(axis=1) * REND - v[rij, laag].sum(axis=1)).sum())


def zonejaar(zone, jaar):
    df = u.uren(zone, jaar)
    if df.empty:
        return None
    p = df.Price.copy(); p.index = pd.to_datetime(p.index)
    m = dagmatrix(p)
    if len(m) < 200:
        return None
    gisteren, week = m.shift(1).dropna(), m.shift(7).dropna()
    m1 = m.loc[gisteren.index]
    vast = pd.DataFrame(0.0, index=m.index, columns=m.columns)
    vast[[11, 12]] = -1; vast[[18, 19]] = 1
    perfect = opbrengst(m1, m1)
    r = {"Zone": zone, "Year": jaar, "Days": len(m1),
         "Perfect foresight EUR/MW": perfect,
         "Yesterday's prices EUR/MW": opbrengst(m1, gisteren),
         "Last week's prices EUR/MW": opbrengst(m1, week),
         "Fixed schedule EUR/MW": opbrengst(m1, vast.loc[m1.index]),
         "MAE yesterday EUR/MWh": float((m1 - gisteren).abs().mean().mean()),
         "MAE last week EUR/MWh": float((m.loc[week.index] - week).abs().mean().mean()),
         "Average price EUR/MWh": float(m.values.mean())}
    for k in ("Yesterday's prices", "Last week's prices", "Fixed schedule"):
        r[f"{k} vs perfect"] = r[f"{k} EUR/MW"] / perfect if perfect > 0 else np.nan
    return r


def main(lijst=None, jaren=range(2019, 2027)):
    naam = u.namen()
    rij = [r for z in (lijst or u.zones()) for j in jaren if (r := zonejaar(z, j))]
    t = pd.DataFrame(rij); t.insert(1, "Zone name", t.Zone.map(lambda z: naam.get(z, z)))
    t71 = t.drop(columns=["MAE yesterday EUR/MWh", "MAE last week EUR/MWh"])
    t72 = t[["Zone", "Zone name", "Year", "Days", "Average price EUR/MWh", "MAE yesterday EUR/MWh", "MAE last week EUR/MWh"]].copy()
    t72["MAE yesterday % of price"] = 100 * t72["MAE yesterday EUR/MWh"] / t72["Average price EUR/MWh"]
    for d in UIT:
        t71.round(4).to_csv(d / "t71_battery_strategies.csv", index=False)
        t72.round(4).to_csv(d / "t72_forecast_baseline.csv", index=False)
    return t71, t72


if __name__ == "__main__":
    a, b = main()
    pd.set_option("display.width", 250)
    x = a[a.Year == 2025]
    print(x[["Zone name", "Perfect foresight EUR/MW", "Yesterday's prices vs perfect", "Last week's prices vs perfect",
             "Fixed schedule vs perfect"]].round(2).sort_values("Perfect foresight EUR/MW", ascending=False).head(12).to_string())
    print(x[["Yesterday's prices vs perfect", "Fixed schedule vs perfect"]].median().round(3))
    print(b[(b.Year == 2025) & b.Zone.isin(["NL", "DE-LU", "FR", "ES"])].round(1).to_string())
