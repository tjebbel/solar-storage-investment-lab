"""Aanvullingen voor dashboards 2, 3, 4 en 10 (ronde 19 november, na de CBS-, EIA- en netcongestiedata).

  t42_gebeurtenissen.csv  annotaties voor tijdlijnen: datum, gebied, gebeurtenis, dashboards, soort, bron.
                          Alleen gebeurtenissen met een vaste datum; bronkolom zegt waar het na te slaan is.
  t43_kannibalisatie.csv  per zone en jaar: capture rate zon (t1) tegen zonaandeel in de opwek (Ember), plus helling.
  t44_kern_zon.csv        per land 2025: TWh, GW en benutting van kern en zon; GW zon nodig voor dezelfde TWh als kern.
  t45_leercurve.csv       leersnelheid in vier varianten (alle jaren, zonder 2021-22, zonder 2023-24, zonder 2021-24).
  t46_portefeuille_uitleg.csv  per land in t12: verklaring van een kwadrantwissel (verzadiging, capture rate, netcongestie).
Gebruik:  PYTHONPATH=src python3 -m eti.dashboard_extra
"""
from pathlib import Path
import numpy as np
import pandas as pd

from .bcg_portefeuille import leersnelheid

UIT = Path("tableau/data")
OPWEK = "powerbi/data/fact_ember_opwek_jaar.csv"

GEBEURTENISSEN = [
    ("2011-03-11", "Japan", "Kernramp Fukushima", "3", "kern", "IAEA"),
    ("2021-09-01", "Europa", "Gasprijzen beginnen sterk te stijgen", "2", "markt", "TTF-reeks in t2 / fact_gasprijs_maand"),
    ("2022-02-24", "Europa", "Russische invasie van Oekraine", "2, 3, 9", "geopolitiek", "algemeen"),
    ("2022-08-01", "Europa", "Piek gas- en stroomprijzen (augustus 2022)", "2", "markt", "t2: hoogste maandprijs"),
    ("2022-08-16", "VS", "Inflation Reduction Act getekend", "10", "beleid", "congress.gov"),
    ("2023-04-15", "Duitsland", "Laatste drie Duitse kerncentrales dicht", "3", "kern", "BASE / Ember"),
    ("2025-07-04", "VS", "One Big Beautiful Bill Act getekend (afbouw belastingkredieten zon en wind)", "10", "beleid", "congress.gov"),
    ("2026-01-26", "Nederland", "Notitie reikwijdte en detailniveau nieuwbouw kerncentrales vastgesteld", "3, 8", "kern",
     "RVO, vaststellingsbesluit 26-01-2026"),
    ("2027-01-01", "Nederland", "Einde salderingsregeling", "2, 8", "beleid", "Wet herziening salderingsregeling"),
]


def gebeurtenissen():
    g = pd.DataFrame(GEBEURTENISSEN, columns=["Datum", "Gebied", "Gebeurtenis", "Dashboards", "Soort", "Na te slaan bij"])
    g["Datum"] = pd.to_datetime(g["Datum"]).dt.strftime("%Y-%m-%d")
    return g


def _ember(bron, kol="Share of generation (%)"):
    o = pd.read_csv(OPWEK)
    o = o[(o["Area type"] == "Country or economy") & (o["Electricity source"] == bron)]
    return o.set_index(["ISO 3 code", "Year"])[kol]


def kannibalisatie(t1="tableau/data/t1_zonejaar.csv"):
    t = pd.read_csv(t1)
    t = t[t["Heel jaar"] == 1].copy()
    aandeel = _ember("Solar")
    t["Zonaandeel %"] = [aandeel.get((l, j), np.nan) for l, j in zip(t["Landcode"], t["Jaar"])]
    t = t.dropna(subset=["Zonaandeel %", "Capture rate zon"])
    b, a = np.polyfit(t["Zonaandeel %"], t["Capture rate zon"], 1)
    t["Helling (per procentpunt)"] = round(b, 4)
    t["Lijn"] = a + b * t["Zonaandeel %"]
    return t[["Zone", "Zonenaam", "Landcode", "Jaar", "Zonaandeel %", "Capture rate zon", "Gemiddelde prijs",
              "Negatieve uren", "Lijn", "Helling (per procentpunt)"]], b


def kern_zon(t7="tableau/data/t7_kern_land.csv"):
    k = pd.read_csv(t7)
    zon_gw = _ember("Solar", "Capacity (GW)")
    k["Zonvermogen GW 2025"] = [zon_gw.get((i, 2025), np.nan) for i in k["ISO3"]]
    k["Benutting zon 2025"] = k["Zon TWh 2025"] / (k["Zonvermogen GW 2025"] * 8.76)
    k["Benutting kern 2025"] = k["Benutting kern 2025"]
    k["GW zon voor kern-TWh"] = k["Kern TWh 2025"] / (k["Benutting zon 2025"] * 8.76)
    k["Verhouding GW zon / GW kern"] = k["GW zon voor kern-TWh"] / k["Kernvermogen GW 2025"]
    hou = ["Land", "ISO3", "Continent", "Kern TWh 2025", "Zon TWh 2025", "Kernvermogen GW 2025", "Zonvermogen GW 2025",
           "Benutting kern 2025", "Benutting zon 2025", "GW zon voor kern-TWh", "Verhouding GW zon / GW kern", "Koers kern"]
    return k[hou][k["Kern TWh 2025"] > 0].round(3)


def leercurve(t11="tableau/data/t11_ervaringscurve.csv"):
    e = pd.read_csv(t11)
    var = {"alle jaren": (), "zonder 2021-22 (crisis)": (2021, 2022), "zonder 2023-24 (overcapaciteit)": (2023, 2024),
           "zonder 2021-24": (2021, 2022, 2023, 2024)}
    rij = []
    for naam, zonder in var.items():
        r = leersnelheid(e, zonder=zonder)
        rij.append({"Variant": naam, "n": r["n"], "Leersnelheid": r["leersnelheid"], "Interval laag": r["interval_laag"],
                    "Interval hoog": r["interval_hoog"], "R2": r.get("r2", np.nan)})
    return pd.DataFrame(rij).round(4)


def portefeuille_uitleg(t12="tableau/data/t12_portefeuille.csv", res="tableau/data/t40_res_regio.csv",
                        cong="tableau/data/t32_congestie_gemeente.csv"):
    p = pd.read_csv(t12)
    w = p.pivot_table(index=["Landcode", "Land"], columns="Moment",
                      values=["Kwadrant", "Capture rate zon", "Groei zonvermogen per jaar"], aggfunc="first")
    w.columns = [f"{a} {b}" for a, b in w.columns]
    w = w.reset_index()
    def uitleg(r):
        if pd.isna(r["Kwadrant 2022"]):
            return "nieuw in 2025 (in 2022 te weinig gegevens)"
        if r["Kwadrant 2022"] == r["Kwadrant 2025"]:
            return "geen wissel"
        g0, g1 = r["Groei zonvermogen per jaar 2022"], r["Groei zonvermogen per jaar 2025"]
        c0, c1 = r["Capture rate zon 2022"], r["Capture rate zon 2025"]
        return (f"groei {g0:.0%} -> {g1:.0%} per jaar (drempel {'erboven' if r['Kwadrant 2025'] in ('Ster', 'Vraagteken') else 'eronder'}); "
                f"capture rate {c0:.2f} -> {c1:.2f}")
    w["Verklaring"] = w.apply(uitleg, axis=1)
    if Path(cong).exists() and Path(res).exists():
        c = pd.read_csv(cong); g = c["postcodes"]
        tek = (c["afname Tekort %"] * g).sum() / g.sum()
        r = pd.read_csv(res); r = r[r["RES-regio"] == "Nederland"].set_index("Jaar")
        extra = (f"; verzadiging, geen verval: zonvermogen groeide in {r.index.max()} nog {r['Groei zon %'].iloc[-1]:.1f}% "
                 f"(CBS) en {tek:.0f}% van de postcodes heeft een afnametekort (netcongestie)")
        w.loc[w.Landcode == "NLD", "Verklaring"] += extra
    return w


def main():
    UIT.mkdir(parents=True, exist_ok=True)
    g = gebeurtenissen(); k, helling = kannibalisatie(); kz = kern_zon(); lc = leercurve(); pu = portefeuille_uitleg()
    for n, d in [("t42_gebeurtenissen", g), ("t43_kannibalisatie", k), ("t44_kern_zon", kz), ("t45_leercurve", lc),
                 ("t46_portefeuille_uitleg", pu)]:
        d.to_csv(UIT / f"{n}.csv", index=False)
    nl = k[k.Zone == "NL"].sort_values("Jaar")
    r = [f"Gebeurtenissen: {len(g)} annotaties.",
         f"Kannibalisatie: {len(k)} zone-jaren; capture rate daalt {abs(helling)*100:.2f} punt per procentpunt zonaandeel. "
         f"NL: " + ", ".join(f"{x.Jaar} {x['Zonaandeel %']:.0f}% -> {x['Capture rate zon']:.2f}" for _, x in nl.iterrows()),
         "Kern tegen zon 2025 (benutting kern / zon; GW zon nodig voor kern-TWh): " + "; ".join(
             f"{x.Land} {x['Benutting kern 2025']:.2f}/{x['Benutting zon 2025']:.2f}, {x['GW zon voor kern-TWh']:.0f} GW"
             for _, x in kz.dropna(subset=["Benutting zon 2025"]).nlargest(6, "Kern TWh 2025").iterrows()),
         "Leercurve: " + "; ".join(f"{x.Variant} {x.Leersnelheid:.1%} ({x['Interval laag']:.1%}-{x['Interval hoog']:.1%}, n={x.n})" for _, x in lc.iterrows()),
         "Kwadrantwissels: " + "; ".join(f"{x.Land}: {x['Kwadrant 2022']} -> {x['Kwadrant 2025']} ({x.Verklaring})"
                                       for _, x in pu[pu.Verklaring != "geen wissel"].iterrows())]
    Path("resultaten/dashboard_extra.txt").write_text("\n".join(r) + "\n")
    print("\n".join(r))


if __name__ == "__main__":
    main()
