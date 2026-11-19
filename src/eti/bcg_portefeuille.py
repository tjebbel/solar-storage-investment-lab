"""Dashboard 4, in de traditie van BCG: ervaringscurve van zonnepanelen en een portefeuille van Europese markten.

Ervaringscurve (Wright 1936; Henderson 1968): log(prijs) = a + b log(cumulatief vermogen); leersnelheid = 1 - 2^b.
  Prijs: exportwaarde van panelen (Ember, USD per W = USD / (MW x 10^6)), alle exporteurs samen per jaar.
  Volume: cumulatief zonvermogen wereldwijd (Ember, GW). Twee schattingen: alle jaren, en zonder 2021-2022
  (prijspiek polysilicium). Met een 95%-interval uit de standaardfout van de helling.
Portefeuille (aangepaste groei-aandeelmatrix van Henderson 1970): per land
  y = jaarlijkse groei van het zonvermogen (CAGR, december tot december, Ember capaciteit per maand);
  x = batterij-omzet per MW tegenover de mediaan van alle landen in hetzelfde jaar (t1, gemiddelde over zones).
  Kwadrant: ster (x>=1, y>=mediaan groei), melkkoe (x>=1, y<mediaan), vraagteken (x<1, y>=mediaan), hond (x<1, y<mediaan).
  Twee momentopnamen: 2022 (groei 2018-2022) en 2025 (groei 2021-2025), voor de pijlen in Tableau.

Schrijft tableau/data/t11_ervaringscurve.csv, t12_portefeuille.csv en resultaten/bcg_portefeuille.txt.
Gebruik:  PYTHONPATH=src python3 -m eti.bcg_portefeuille
"""
import os

import numpy as np
import pandas as pd

EXPORT = "data/ember_global/mart_solar_exports_full_release_monthly.csv"
OPWEK = "data/ember_global/release_generation_yearly_global.csv"
CAP = "powerbi/data/fact_ember_capaciteit_maand.csv"
T1 = "tableau/data/t1_zonejaar.csv"
UIT = "tableau/data"


def ervaringscurve(export=EXPORT, opwek=OPWEK):
    e = pd.read_csv(export, low_memory=False)
    p = e[(e["Commodity type"] == "Panels") & (e["Area type"] == "Country or economy")].copy()
    p["Jaar"] = p["Date"].str[:4].astype(int)
    g = p.groupby("Jaar").agg(usd=("Amount (USD)", "sum"), mw=("Capacity (MW)", "sum"), maanden=("Date", "nunique"))
    g["Prijs USD per W"] = g["usd"] / (g["mw"] * 1e6)
    y = pd.read_csv(opwek, low_memory=False)
    cap = y[(y["Area"] == "World") & (y["Electricity source"] == "Solar")].set_index("Year")["Capacity (GW)"]
    t = g.join(cap.rename("Cumulatief GW"), how="inner").rename_axis("Jaar").reset_index()
    t["Volledig jaar"] = t["maanden"] == 12
    return t[["Jaar", "Prijs USD per W", "Cumulatief GW", "Volledig jaar"]]


def leersnelheid(t, zonder=()):
    d = t[t["Volledig jaar"] & ~t["Jaar"].isin(zonder)]
    x, y = np.log(d["Cumulatief GW"]), np.log(d["Prijs USD per W"])
    b, a = np.polyfit(x, y, 1)
    res = y - (a + b * x)
    se = np.sqrt((res ** 2).sum() / (len(d) - 2) / ((x - x.mean()) ** 2).sum())
    t975 = {5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}.get(len(d) - 2, 2.0)
    lr = lambda h: 1 - 2 ** h
    return {"jaren": f"{d['Jaar'].min()}-{d['Jaar'].max()}" + (f" zonder {','.join(map(str, zonder))}" if zonder else ""),
            "n": len(d), "helling": b, "leersnelheid": lr(b), "interval_laag": lr(b + t975 * se), "interval_hoog": lr(b - t975 * se),
            "r2": 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()}


def groei(cap=CAP, van=2021, tot=2025):
    c = pd.read_csv(cap)
    z = c[(c["Source"] == "Solar") & (c["Month"] == 12)].pivot_table(index="ISO 3 Code", columns="Year", values="Installed Capacity")
    return ((z[tot] / z[van]) ** (1 / (tot - van)) - 1).rename("groei"), z[tot].rename("gw")


def portefeuille(t1=T1, cap=CAP):
    t = pd.read_csv(t1)
    rijen = []
    for jaar, van in ((2022, 2018), (2025, 2021)):
        g, gw = groei(cap, van, jaar)
        l = t[t["Jaar"] == jaar].groupby(["Landcode"]).agg(Land=("Zonenaam", "first"), Regio=("Regio", "first"),
                                                           batterij=("Batterij-omzet per MW", "mean"),
                                                           capture=("Capture rate zon", "mean")).reset_index()
        l["Land"] = l["Land"].str.replace(r" \(.*\)$", "", regex=True)
        l["x"] = l["batterij"] / l["batterij"].median()
        l = l.join(g, on="Landcode").join(gw, on="Landcode").dropna(subset=["groei"])
        drempel = l["groei"].median()
        l["Kwadrant"] = np.select([(l.x >= 1) & (l.groei >= drempel), l.x >= 1, l.groei >= drempel],
                                  ["Ster", "Melkkoe", "Vraagteken"], "Hond")
        l["Moment"], l["Groeiperiode"], l["Groeidrempel"] = jaar, f"{van}-{jaar}", drempel
        rijen.append(l)
    p = pd.concat(rijen).rename(columns={"x": "Batterij-omzet tegen mediaan", "groei": "Groei zonvermogen per jaar",
                                         "gw": "Zonvermogen GW", "batterij": "Batterij-omzet per MW", "capture": "Capture rate zon"})
    return p


def main():
    e = ervaringscurve()
    p = portefeuille()
    e.to_csv(os.path.join(UIT, "t11_ervaringscurve.csv"), index=False)
    p.to_csv(os.path.join(UIT, "t12_portefeuille.csv"), index=False)
    r = [leersnelheid(e), leersnelheid(e, zonder=(2021, 2022))]
    regels = [f"Ervaringscurve {x['jaren']}: leersnelheid {x['leersnelheid']:.1%} (95%: {x['interval_laag']:.1%} tot "
              f"{x['interval_hoog']:.1%}), R2 {x['r2']:.2f}, n={x['n']}" for x in r]
    for jaar in (2022, 2025):
        q = p[p["Moment"] == jaar]
        regels.append(f"Portefeuille {jaar}: " + "; ".join(
            f"{k}: {', '.join(q[q['Kwadrant'] == k]['Landcode'])}" for k in ["Ster", "Melkkoe", "Vraagteken", "Hond"]))
    w = p.pivot_table(index="Landcode", columns="Moment", values="Kwadrant", aggfunc="first").dropna()
    regels.append("Van ster naar iets anders (2022 -> 2025): " + ", ".join(
        f"{i} ({w.loc[i, 2025]})" for i in w.index if w.loc[i, 2022] == "Ster" and w.loc[i, 2025] != "Ster"))
    tekst = "\n".join(regels)
    print(tekst)
    open("resultaten/bcg_portefeuille.txt", "w", encoding="utf-8").write(tekst + "\n")


if __name__ == "__main__":
    main()
