"""Dashboard 30 "Forecasting showcase": een eigen day-ahead-prijsmodel dat de naieve basislijn (prijzen van gisteren) moet verslaan.

Model: ridge-regressie per zone (numpy, geen extra pakketten), uur voor uur voor de volgende dag.
Kenmerken (alles wat een handelaar de dag ervoor kan weten of laten voorspellen):
  prijs zelfde uur gisteren en vorige week, daggemiddelde en spreiding van gisteren,
  uur, weekdag en maand (dummies), restlast, belasting, wind en zon van de dag zelf.
Restlast, belasting, wind en zon zijn hier de gerealiseerde waarden als vervanging van de day-ahead-voorspellingen die een handelaar
heeft (TSO-prognoses). Dat maakt het model iets te optimistisch: lees de fout als een ondergrens voor dit modeltype (model card).
Daarom staat er een tweede model naast zonder die vier kenmerken ("lags and calendar only"): dat gebruikt alleen wat zeker bekend is.
Backtest: uitbreidend venster. Voor testjaar J wordt getraind op alle jaren 2019 .. J-1; nooit op het testjaar zelf.
Daarnaast: wat verdient de batterij uit dashboard 29 als hij op deze voorspelling handelt (vloer = gisteren, plafond = perfect)?
Tabellen (Engels):
  t73_forecast_model     zone x testjaar: MAE model, MAE gisteren, verbetering %, batterij-opbrengst model vs perfect
  t74_forecast_week      NL, een voorbeeldweek per testjaar: uur, werkelijke prijs, gisteren, model
  t75_forecast_features  NL, gestandaardiseerde coefficienten van het laatste model (welke kenmerken wegen het zwaarst)
Gebruik: PYTHONPATH=src python3 -m eti.voorspelmodel
"""
from pathlib import Path

import numpy as np
import pandas as pd

from eti import uurdata as u
from eti.batterij_realistisch import dagmatrix, opbrengst

UIT = [Path("tableau/data"), Path("tableau/data_en")]
JAREN = range(2019, 2027)
TEST = (2023, 2024, 2025, 2026)
LAMBDA = 10.0
EXO = ["Residual load", "Load", "Wind", "Solar"]


def kenmerken(df):
    """Uurdata -> DataFrame met doel (Price) en kenmerken; rijen zonder volledige vertraagde prijs vallen weg."""
    p = df.Price.astype(float)
    x = pd.DataFrame(index=df.index)
    x["Price"] = p
    x["Price yesterday"] = p.shift(24)
    x["Price last week"] = p.shift(168)
    dag = p.groupby(p.index.date).agg(["mean", "max", "min"])
    dag.index = pd.to_datetime(dag.index)
    gist = dag.shift(1).reindex(pd.to_datetime(p.index.date))
    x["Mean yesterday"] = gist["mean"].to_numpy()
    x["Spread yesterday"] = (gist["max"] - gist["min"]).to_numpy()
    wind = df.filter(like="Wind").sum(axis=1, min_count=1)
    x["Wind"] = wind / 1000
    x["Solar"] = df.get("Solar", pd.Series(np.nan, index=df.index)) / 1000
    x["Load"] = df.get("Load", pd.Series(np.nan, index=df.index)) / 1000
    x["Residual load"] = df.get("Residual load", x["Load"] * 1000 - wind - df.get("Solar", 0)) / 1000
    for c in EXO:
        x[c] = x[c].fillna(0.0)
    x["hour"] = x.index.hour
    x["weekday"] = x.index.dayofweek
    x["month"] = x.index.month
    return x.dropna(subset=["Price", "Price yesterday", "Price last week", "Mean yesterday"])


def matrix(x, kolommen=None, exo=True):
    num = x[["Price yesterday", "Price last week", "Mean yesterday", "Spread yesterday"] + (EXO if exo else [])]
    dum = pd.concat([pd.get_dummies(x["hour"], prefix="h", drop_first=True),
                     pd.get_dummies(x["weekday"], prefix="wd", drop_first=True),
                     pd.get_dummies(x["month"], prefix="m", drop_first=True)], axis=1).astype(float)
    m = pd.concat([num, dum], axis=1)
    if kolommen is not None:
        m = m.reindex(columns=kolommen, fill_value=0.0)
    return m


def fit(X, y):
    mu, sd = X.mean(), X.std().replace(0, 1)
    Z = ((X - mu) / sd).to_numpy()
    Z = np.column_stack([np.ones(len(Z)), Z])
    reg = LAMBDA * np.eye(Z.shape[1]); reg[0, 0] = 0
    b = np.linalg.solve(Z.T @ Z + reg, Z.T @ y.to_numpy())
    return {"mu": mu, "sd": sd, "b": b, "cols": X.columns}


def predict(mod, X):
    Z = ((X[mod["cols"]] - mod["mu"]) / mod["sd"]).to_numpy()
    return mod["b"][0] + Z @ mod["b"][1:]


def zone(z):
    delen = []
    for j in JAREN:
        df = u.uren(z, j)
        if df is None or df.empty:
            continue
        df = df.copy(); df.index = pd.to_datetime(df.index)
        delen.append(df)
    if not delen:
        return [], None, None
    df = pd.concat(delen).sort_index()
    df = df[~df.index.duplicated()]
    x = kenmerken(df)
    rijen, week, coef = [], None, None
    for jt in TEST:
        tr, te = x[x.index.year < jt], x[x.index.year == jt]
        if len(tr) < 24 * 300 or len(te) < 24 * 60:
            continue
        Xtr = matrix(tr); mod = fit(Xtr, tr["Price"])
        Xte = matrix(te, Xtr.columns)
        pred = pd.Series(predict(mod, Xte), index=te.index)
        mae_m = float((te["Price"] - pred).abs().mean())
        Xl = matrix(tr, exo=False); modl = fit(Xl, tr["Price"])  # zonder wind, zon en belasting: alleen kalender en oude prijzen
        mae_l = float((te["Price"] - predict(modl, matrix(te, Xl.columns, exo=False))).abs().mean())
        mae_g = float((te["Price"] - te["Price yesterday"]).abs().mean())
        m = dagmatrix(te["Price"]); kies = dagmatrix(pred).reindex(m.index); gist = dagmatrix(te["Price yesterday"]).reindex(m.index)
        ok = kies.dropna().index.intersection(gist.dropna().index)
        m, kies, gist = m.loc[ok], kies.loc[ok], gist.loc[ok]
        perf = opbrengst(m, m)
        rijen.append({"Zone": z, "Year": jt, "Hours": len(te), "Average price EUR/MWh": float(te["Price"].mean()),
                      "MAE model EUR/MWh": mae_m, "MAE lags and calendar only EUR/MWh": mae_l, "MAE yesterday EUR/MWh": mae_g,
                      "Improvement vs yesterday %": 100 * (1 - mae_m / mae_g) if mae_g > 0 else np.nan,
                      "Battery perfect EUR/MW": perf, "Battery model EUR/MW": opbrengst(m, kies),
                      "Battery yesterday EUR/MW": opbrengst(m, gist)})
        if z == "NL":
            wk = te[(te.index.month == 5) & (te.index.day >= 12) & (te.index.day < 19)]
            if len(wk):
                w = pd.DataFrame({"Zone": z, "Year": jt, "Time": wk.index, "Hour of week": range(len(wk)),
                                  "Actual EUR/MWh": wk["Price"].to_numpy(), "Yesterday EUR/MWh": wk["Price yesterday"].to_numpy(),
                                  "Model EUR/MWh": pred.loc[wk.index].to_numpy()})
                week = w if week is None else pd.concat([week, w])
            coef = pd.DataFrame({"Feature": list(mod["cols"]), "Standardised coefficient": mod["b"][1:], "Test year": jt})
    return rijen, week, coef


def main(lijst=None):
    rijen, weken, coef = [], [], None
    for z in (lijst or u.zones()):
        r, w, c = zone(z)
        rijen += r
        if w is not None:
            weken.append(w)
        if c is not None:
            coef = c
    t = pd.DataFrame(rijen)
    if t.empty:
        print("geen data"); return None
    namen = u.namen() if hasattr(u, "namen") else {}
    if isinstance(namen, dict):
        t.insert(1, "Zone name", t.Zone.map(namen).fillna(t.Zone))
    for k in ("model", "yesterday"):
        t[f"Battery {k} vs perfect"] = t[f"Battery {k} EUR/MW"] / t["Battery perfect EUR/MW"]
    t["Model beats yesterday"] = t["MAE model EUR/MWh"] < t["MAE yesterday EUR/MWh"]
    t74 = pd.concat(weken) if weken else pd.DataFrame()
    if coef is not None:
        coef = coef[~coef.Feature.str.match(r"^(h|wd|m)_")].copy()
        coef["Absolute"] = coef["Standardised coefficient"].abs()
        coef = coef.sort_values("Absolute", ascending=False)
    for d in UIT:
        d.mkdir(parents=True, exist_ok=True)
        t.round(4).to_csv(d / "t73_forecast_model.csv", index=False)
        t74.round(3).to_csv(d / "t74_forecast_week.csv", index=False)
        if coef is not None:
            coef.round(4).to_csv(d / "t75_forecast_features.csv", index=False)
    s = t[t.Year == 2025]
    print(f"2025: {len(s)} zones; model wint in {int(s['Model beats yesterday'].sum())}; mediane verbetering "
          f"{s['Improvement vs yesterday %'].median():.0f}%; batterij model {s['Battery model vs perfect'].median():.0%} "
          f"vs gisteren {s['Battery yesterday vs perfect'].median():.0%} van perfect")
    print(t[t.Zone == "NL"].round(2).to_string())
    return t


if __name__ == "__main__":
    main()
