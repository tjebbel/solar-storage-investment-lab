"""Vervolgonderzoek 5: het schokjaar 2026 opgesplitst. Welk deel van de prijsstijging komt door gas, en welk door zon en wind?

Vraag. De stroomprijs lag in 2026 ver boven 2025. Hoeveel daarvan verklaart de gasprijs, hoeveel de verandering in het
aandeel zon en wind, en wat blijft over?

Aanpak. Een maandpaneel per biedzone, 2019 tot en met 2025:
    prijs[zone, maand] = vast effect zone + vast effect kalendermaand + b_gas * gasprijs + b_zon * zonaandeel + b_wind * windaandeel
Gasprijs: fact_gasprijs_maand (FRED, euro per MWh). Zon- en windaandeel: Ember per land en maand (in procenten).
De coefficienten komen uit 2019-2025; 2026 doet niet mee aan het schatten. Daarna, per zone, januari tot en met oktober
2026 tegen dezelfde maanden van 2025:
    verschil = b_gas * verschil gas + b_zon * verschil zon + b_wind * verschil wind + rest
De rest is wat het model niet verklaart (bijvoorbeeld de windstille week, kolen- en CO2-prijs, uitval van centrales).
Oktober 2026 is voorlopig (IMF via cbonds); november doet niet mee omdat Ember daar nog geen maandcijfers heeft.

Schrijft powerbi/data/fact_schokjaar_zone_SJ.csv (per zone) en fact_schokjaar_model_SJ.csv (coefficienten en fit).
Gebruik:  PYTHONPATH=src python3 -m eti.schokjaar
"""
import os

import numpy as np
import pandas as pd

DATA = "powerbi/data"
SCHATTEN, MAANDEN = range(2019, 2026), range(1, 11)


def paneel(data=DATA):
    lm = pd.read_csv(os.path.join(data, "fact_land_maand.csv"))[["land", "jaar", "maand", "gem_prijs"]]
    sleutel = pd.read_csv(os.path.join(data, "fact_land_jaar.csv"))[["land", "biedzone", "iso3"]].drop_duplicates("land")
    gas = pd.read_csv(os.path.join(data, "fact_gasprijs_maand.csv"))[["jaar", "maand", "eu_gas_eur_mwh"]].rename(columns={"eu_gas_eur_mwh": "gas"})
    e = pd.read_csv(os.path.join(data, "fact_ember_opwek_maand.csv"))
    e["Date"] = pd.to_datetime(e.Date)
    e = e[e["Electricity source"].isin(["Solar", "Wind"])]
    e = e.pivot_table(index=["ISO 3 code", "Date"], columns="Electricity source", values="Share of generation (%)").reset_index()
    e = e.rename(columns={"ISO 3 code": "iso3", "Solar": "zon", "Wind": "wind"})
    e["jaar"], e["maand"] = e.Date.dt.year, e.Date.dt.month
    p = lm.merge(sleutel, on="land").merge(gas, on=["jaar", "maand"]).merge(e[["iso3", "jaar", "maand", "zon", "wind"]], on=["iso3", "jaar", "maand"])
    return p.dropna(subset=["gem_prijs", "gas", "zon", "wind"])


def schat(p):
    s = p[p.jaar.isin(SCHATTEN)]
    X = pd.concat([s[["gas", "zon", "wind"]], pd.get_dummies(s.biedzone, prefix="z", dtype=float), pd.get_dummies(s.maand, prefix="m", drop_first=True, dtype=float)], axis=1)
    y = s.gem_prijs.to_numpy()
    b, *_ = np.linalg.lstsq(X.to_numpy(), y, rcond=None)
    fit = X.to_numpy() @ b
    r2 = 1 - ((y - fit) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    coef = dict(zip(X.columns, b))
    # standaardfout van de drie hoofdcoefficienten, geclusterd per maand (alle zones delen dezelfde gasprijs)
    res, Xa = y - fit, X.to_numpy()
    xtx = np.linalg.pinv(Xa.T @ Xa)
    meat = sum(np.outer(Xa[g].T @ res[g], Xa[g].T @ res[g]) for g in s.groupby(["jaar", "maand"]).indices.values())
    se = np.sqrt(np.diag(xtx @ meat @ xtx))[:3]
    return coef, r2, dict(zip(["gas", "zon", "wind"], se)), len(s)


def splits(p, coef):
    a = p[(p.jaar == 2025) & p.maand.isin(MAANDEN)].set_index(["biedzone", "maand"])
    b = p[(p.jaar == 2026) & p.maand.isin(MAANDEN)].set_index(["biedzone", "maand"])
    d = (b[["gem_prijs", "gas", "zon", "wind"]] - a[["gem_prijs", "gas", "zon", "wind"]]).dropna().reset_index()
    d["door_gas"], d["door_zon"], d["door_wind"] = coef["gas"] * d.gas, coef["zon"] * d.zon, coef["wind"] * d.wind
    d["rest"] = d.gem_prijs - d.door_gas - d.door_zon - d.door_wind
    z = d.groupby("biedzone")[["gem_prijs", "gas", "zon", "wind", "door_gas", "door_zon", "door_wind", "rest"]].mean().reset_index()
    z = z.rename(columns={"gem_prijs": "prijsstijging", "gas": "gas_verschil", "zon": "zon_verschil_pp", "wind": "wind_verschil_pp"})
    z["maanden"] = d.groupby("biedzone").size().values
    z["aandeel_gas"] = z.door_gas / z.prijsstijging
    return z.sort_values("prijsstijging", ascending=False).reset_index(drop=True)


def main(data=DATA, uit=DATA):
    p = paneel(data)
    coef, r2, se, n = schat(p)
    z = splits(p, coef)
    model = pd.DataFrame([{"coefficient": k, "waarde": coef[k], "standaardfout_geclusterd_per_maand": se[k]} for k in ("gas", "zon", "wind")])
    model["r2"], model["waarnemingen"], model["schatjaren"] = r2, n, "2019-2025"
    z.to_csv(os.path.join(uit, "fact_schokjaar_zone_SJ.csv"), index=False)
    model.to_csv(os.path.join(uit, "fact_schokjaar_model_SJ.csv"), index=False)
    pd.set_option("display.width", 200)
    print(model.round(3).to_string(index=False)); print()
    print(z.round(1).to_string(index=False))
    vol = z[z.maanden == len(MAANDEN)]                                            # zones met alle tien maanden (Zwitserland mist Ember-maanden)
    gem = vol[["prijsstijging", "door_gas", "door_zon", "door_wind", "rest"]].mean()
    print(f"\nGemiddeld over {len(vol)} zones met tien maanden:", gem.round(1).to_dict(), "aandeel gas:", round(gem.door_gas / gem.prijsstijging, 3))
    return model, z


if __name__ == "__main__":
    main()
