"""Ruimtelijk paneel: drukt het zonaandeel van de buurlanden de capture rate, bovenop het eigen zonaandeel?

Buurgewicht: de handelscapaciteit per grens (NTC, ENTSO-E TYNDP, scenario Reference 2024), gemiddeld over beide
richtingen. Zonaandeel per land en jaar: Ember, ook voor buurlanden buiten het paneel (zoals het VK).
Standaardfouten geclusterd per land. Schrijft powerbi/data/fact_ruimtelijk_paneel.csv.
Gebruik:  PYTHONPATH=src python3 -m eti.ruimtelijk
"""
import os
import sys

import numpy as np
import pandas as pd

from . import verbanden

OUT = verbanden.OUT
ISO3 = {"AL": "ALB", "AT": "AUT", "BA": "BIH", "BE": "BEL", "BG": "BGR", "CH": "CHE", "CY": "CYP", "CZ": "CZE", "DE": "DEU",
        "DK": "DNK", "DZ": "DZA", "EE": "EST", "EG": "EGY", "ES": "ESP", "FI": "FIN", "FR": "FRA", "GR": "GRC", "HR": "HRV",
        "HU": "HUN", "IE": "IRL", "IL": "ISR", "IT": "ITA", "LT": "LTU", "LU": "LUX", "LV": "LVA", "LY": "LBY", "MA": "MAR",
        "MD": "MDA", "ME": "MNE", "MK": "MKD", "MT": "MLT", "NL": "NLD", "NO": "NOR", "PL": "POL", "PS": "PSE", "PT": "PRT",
        "RO": "ROU", "RS": "SRB", "RU": "RUS", "SA": "SAU", "SE": "SWE", "SI": "SVN", "SK": "SVK", "TN": "TUN", "TR": "TUR",
        "UA": "UKR", "UK": "GBR", "XK": "XKX"}          # knooppunten zonder land (BW, CW, NW) vallen weg


def ols_cluster(y, kolommen, groepen):
    """Kleinste kwadraten met constante en standaardfouten geclusterd per groep -> (coefficienten, standaardfouten, R2).
    Correctie voor kleine steekproeven: G/(G-1) * (n-1)/(n-k), met de dummy's meegeteld in k."""
    y = np.asarray(y, dtype=float)
    X = np.column_stack([np.ones(len(y))] + [np.asarray(k, dtype=float) for k in kolommen])
    inv = np.linalg.pinv(X.T @ X)
    b = inv @ X.T @ y
    rest = y - X @ b
    g = pd.factorize(np.asarray(groepen))[0]
    aantal = int(g.max()) + 1
    midden = np.zeros((X.shape[1], X.shape[1]))
    for i in range(aantal):
        s = X[g == i].T @ rest[g == i]
        midden += np.outer(s, s)
    n, k = len(y), np.linalg.matrix_rank(X)
    v = inv @ midden @ inv * (aantal / max(1, aantal - 1)) * ((n - 1) / max(1, n - k))
    return b, np.sqrt(np.clip(np.diag(v), 0, None)), float(1 - rest.var() / y.var())


def gewichten(ntc, scenario="Reference", jaar=2024):
    """Per land de buren met hun aandeel in de handelscapaciteit van dat land (telt per land op tot 1)."""
    r = ntc[(ntc.scenario == scenario) & (ntc.jaar == jaar)]
    rijen = []
    for van, naar, heen, terug in zip(r.van, r.naar, r.ntc_heen_mw, r.ntc_terug_mw):
        a, b, mw = ISO3.get(van), ISO3.get(naar), (heen + terug) / 2
        if a and b and a != b and mw > 0:
            rijen += [(a, b, mw), (b, a, mw)]
    g = pd.DataFrame(rijen, columns=["iso3", "buur", "mw"]).groupby(["iso3", "buur"], as_index=False).mw.sum()
    g["gewicht"] = g.mw / g.groupby("iso3").mw.transform("sum")
    return g


def buuraandeel(gew, aandeel):
    """Gewogen zonaandeel van de buren per land en jaar. Buren zonder cijfer vallen weg; de gewichten schalen mee."""
    m = gew.merge(aandeel.rename(columns={"iso3": "buur", "aandeel_pct": "buur_pct"}), on="buur")
    m["x"] = m.mw * m.buur_pct
    s = m.groupby(["iso3", "jaar"]).agg(x=("x", "sum"), mw=("mw", "sum")).reset_index()
    s["buur_pct"] = s.x / s.mw
    return s[["iso3", "jaar", "buur_pct"]]


def ember_zonaandeel(data=OUT):
    e = pd.read_csv(os.path.join(data, "fact_ember_opwek_jaar.csv"))
    e = e[(e["Electricity source"] == "Solar") & e["ISO 3 code"].notna()]
    e = e.rename(columns={"ISO 3 code": "iso3", "Year": "jaar", "Share of generation (%)": "aandeel_pct"})
    return e[["iso3", "jaar", "aandeel_pct"]].dropna()


def paneel(p, steekproef="alle zones"):
    """Capture rate op eigen en buur-zonaandeel (procentpunten), met en zonder land- en jaareffecten."""
    y, eigen, buur = p.capture.values, p.aandeel_pct.values, p.buur_pct.values
    jaar = pd.get_dummies(p.jaar, drop_first=True).values.astype(float)
    land = pd.get_dummies(p.iso3, drop_first=True).values.astype(float)
    specs = [("eigen + buren", [eigen, buur]), ("eigen + buren + landeffecten", [eigen, buur, land]),
             ("eigen + buren + jaareffecten", [eigen, buur, jaar]),
             ("eigen + buren + land- en jaareffecten", [eigen, buur, land, jaar])]
    rijen = []
    for naam, kolommen in specs:
        b, se, r2 = ols_cluster(y, kolommen, p.iso3.values)
        rijen.append({"steekproef": steekproef, "specificatie": naam, "landjaren": len(p), "landen": p.iso3.nunique(), "r2": r2,
                      "coef_eigen": b[1], "t_eigen": b[1] / se[1] if se[1] else None,
                      "coef_buren": b[2], "t_buren": b[2] / se[2] if se[2] else None,
                      "correlatie_eigen_buren": float(np.corrcoef(eigen, buur)[0, 1])})
    return pd.DataFrame(rijen)


def main(data=OUT, uit=OUT):
    z = verbanden.zonejaren(data)
    nb = buuraandeel(gewichten(pd.read_csv(os.path.join(data, "fact_ntc.csv"))), ember_zonaandeel(data))
    delen = []
    for naam, alleen in (("alle zones", False), ("alleen opwekdata", True)):
        p = verbanden.landpaneel(z, alleen_opwek=alleen).merge(nb, on=["iso3", "jaar"])
        delen.append(paneel(p, naam))
    r = pd.concat(delen, ignore_index=True)
    os.makedirs(uit, exist_ok=True)
    r.to_csv(os.path.join(uit, "fact_ruimtelijk_paneel.csv"), index=False)
    print(r.round(4).to_string(index=False))
    return r


if __name__ == "__main__":
    main(*sys.argv[1:3])
