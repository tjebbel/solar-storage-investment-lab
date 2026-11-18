"""Verbanden tussen de kernmaten per biedzone, zodat de cijfers in memo en naslagwerk na te rekenen zijn.

1. Rangcorrelaties (Spearman) over alle zone-jaren en binnen jaren (gemiddelde van de correlaties per jaar).
2. Paneelregressie op landniveau: capture rate van zon op het eigen zonaandeel, met land- en jaareffecten.

Schrijft fact_verbanden.csv en fact_paneel_kannibalisatie.csv in powerbi/data.
Gebruik:  PYTHONPATH=src python3 -m eti.verbanden [datamap] [uitvoermap]
"""
import os
import sys

import numpy as np
import pandas as pd

OUT = "powerbi/data"
PAREN = [("Batterij-omzet en dagspreiding", "omzet_realistisch_per_mw", "dagspreiding"),
         ("Batterij-omzet en gemiddelde prijs", "omzet_realistisch_per_mw", "gem_prijs"),
         ("Capture rate zon en negatieve uren", "capture_zon", "negatieve_uren"),
         ("Capture rate zon en eigen zonaandeel", "capture_zon", "aandeel_zon"),
         ("Capture rate wind en eigen windaandeel", "capture_wind", "aandeel_wind"),
         ("Voorspelratio batterij en dagspreiding", "voorspel_ratio", "dagspreiding"),
         ("Batterij-omzet en capture rate zon", "omzet_realistisch_per_mw", "capture_zon")]


def spearman(x, y):
    """Rangcorrelatie; gelijke waarden krijgen hun gemiddelde rang."""
    return float(np.corrcoef(pd.Series(list(x)).rank().values, pd.Series(list(y)).rank().values)[0, 1])


def ols(y, kolommen):
    """Kleinste kwadraten met constante -> (coefficienten, standaardfouten, R2). Standaardfouten niet geclusterd."""
    y = np.asarray(y, dtype=float)
    X = np.column_stack([np.ones(len(y))] + [np.asarray(k, dtype=float) for k in kolommen])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rest = y - X @ b
    vrij = max(1, len(y) - np.linalg.matrix_rank(X))
    se = np.sqrt(np.diag(rest @ rest / vrij * np.linalg.pinv(X.T @ X)))
    return b, se, float(1 - rest.var() / y.var())


def zonejaren(data=OUT, tot=2025):
    """Een rij per biedzone en jaar (hele jaren tot en met `tot`), met de batterij van 2 uur erbij."""
    land = pd.read_csv(os.path.join(data, "fact_land_jaar.csv"))
    flex = pd.read_csv(os.path.join(data, "fact_flex_land.csv")).query("uren_opslag == 2")
    z = land.merge(flex[["land", "jaar", "omzet_realistisch_per_mw", "voorspel_ratio"]], on=["land", "jaar"])
    return z[z.jaar <= tot]


def correlaties(z):
    rijen = []
    for naam, a, b in PAREN:
        d = z[[a, b, "jaar"]].dropna()
        per_jaar = {int(j): spearman(g[a], g[b]) for j, g in d.groupby("jaar")}
        rijen.append({"verband": naam, "zonejaren": len(d), "rho_alle_zonejaren": spearman(d[a], d[b]),
                      "rho_binnen_jaren": float(np.mean(list(per_jaar.values()))),
                      **{f"rho_{j}": r for j, r in per_jaar.items()}})
    return pd.DataFrame(rijen)


def landpaneel(z, alleen_opwek=False):
    """Landniveau: de capture rate is het gemiddelde over de biedzones van een land; zonaandeel in procenten (Ember).
    Met alleen_opwek tellen alleen zone-jaren mee waarvan de capture rate uit opwekdata komt (geen instralingsprofiel)."""
    if alleen_opwek:
        z = z[z.capture_bron.astype(str).str.startswith("opwek")]
    p = (z.groupby(["iso3", "jaar"]).agg(capture=("capture_zon", "mean"), aandeel=("aandeel_zon", "mean"))
          .dropna().reset_index())
    p["aandeel_pct"] = p.aandeel * 100
    return p


def paneel(p, steekproef="alle zones"):
    y, a = p.capture.values, p.aandeel_pct.values
    jaar = pd.get_dummies(p.jaar, drop_first=True).values.astype(float)
    land = pd.get_dummies(p.iso3, drop_first=True).values.astype(float)
    specs = [("eigen zonaandeel", [a], True), ("jaareffecten", [jaar], False), ("landeffecten", [land], False),
             ("zonaandeel + jaareffecten", [a, jaar], True), ("zonaandeel + landeffecten", [a, land], True),
             ("zonaandeel + land- en jaareffecten", [a, land, jaar], True)]
    rijen = []
    for naam, kolommen, heeft_helling in specs:
        b, se, r2 = ols(y, kolommen)
        rijen.append({"steekproef": steekproef, "specificatie": naam, "landjaren": len(p), "landen": p.iso3.nunique(), "r2": r2,
                      "constante": b[0], "helling_per_procentpunt": b[1] if heeft_helling else None,
                      "t_waarde": b[1] / se[1] if heeft_helling else None})
    laatste = p[p.jaar == p.jaar.max()]
    b, se, r2 = ols(laatste.capture.values, [laatste.aandeel_pct.values])
    rijen.append({"steekproef": steekproef, "specificatie": f"eigen zonaandeel, alleen {int(p.jaar.max())}", "landjaren": len(laatste),
                  "landen": laatste.iso3.nunique(), "r2": r2, "constante": b[0], "helling_per_procentpunt": b[1],
                  "t_waarde": b[1] / se[1]})
    return pd.DataFrame(rijen)


def main(data=OUT, uit=OUT):
    z = zonejaren(data)
    c = correlaties(z)
    r = pd.concat([paneel(landpaneel(z)), paneel(landpaneel(z, alleen_opwek=True), "alleen opwekdata")], ignore_index=True)
    os.makedirs(uit, exist_ok=True)
    c.to_csv(os.path.join(uit, "fact_verbanden.csv"), index=False)
    r.to_csv(os.path.join(uit, "fact_paneel_kannibalisatie.csv"), index=False)
    print(c.round(2).to_string(index=False))
    print(r.round(4).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
