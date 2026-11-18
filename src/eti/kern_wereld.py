"""Kernenergie in Europa en de rest van de wereld, voor het derde Tableau-dashboard.

Bron: Ember, jaarlijkse opwek per land en regio (data/ember_global/release_generation_yearly_global.csv, 2000-2025).
Vragen:
1. Hoe ontwikkelen kernenergie, zon en wind zich in Europa tegenover de wereld, de VS, China en de rest van Azie?
2. Welke landen bouwen kernenergie af of uit, en hoe verhoudt dat zich tot de groei van zon en wind?
3. In welk jaar leverde zon voor het eerst meer stroom dan kernenergie (per land en regio)?
4. Hoe schoon is de stroom (gCO2/kWh) bij een groot aandeel kern, een groot aandeel zon en wind, of beide?
5. Wat is een kWh kernstroom op de Europese dagmarkt waard tegenover een kWh zonnestroom (capture rate)?
   Dat deel komt uit powerbi/data/fact_kernenergie_land_jaar.csv (eti.kernenergie, uurdata Energy-Charts).

Schrijft naar tableau/data:
  t6_kern_gebied_jaar.csv   gebied x jaar x bron (lange vorm): opwek in TWh en aandeel in %
  t7_kern_land.csv          land: kern, zon en wind in 2015 en 2025, CO2-intensiteit, benutting, jaar waarin zon kern inhaalt
  t8_kern_markt.csv         land x jaar x bron (lange vorm): capture rate van kern en zon op de Europese dagmarkt
Gebruik:  PYTHONPATH=src python3 -m eti.kern_wereld
"""
import os
import sys

import numpy as np
import pandas as pd

EMBER = "data/ember_global/release_generation_yearly_global.csv"
KERN_MARKT = "powerbi/data/fact_kernenergie_land_jaar.csv"
UIT = "tableau/data"
VAN, TOT = 2000, 2025

GEBIEDEN = {      # Ember-naam -> naam in het dashboard
    "World": "Wereld", "Europe": "Europa", "EU": "EU", "North America": "Noord-Amerika", "Asia": "Azie",
    "United States": "Verenigde Staten", "China": "China", "France": "Frankrijk", "Germany": "Duitsland",
    "Japan": "Japan", "South Korea": "Zuid-Korea", "India": "India", "United Kingdom": "Verenigd Koninkrijk",
    "Spain": "Spanje", "Sweden": "Zweden", "Belgium": "Belgie", "Netherlands": "Nederland",
}
BRONNEN = {"Nuclear": "Kernenergie", "Solar": "Zon", "Wind": "Wind", "Fossil": "Fossiel",
           "Hydro, bioenergy and other renewables": "Water, bio en overig"}


def lees(pad=EMBER):
    d = pd.read_csv(pad, low_memory=False)
    d = d[(d["Year"] >= VAN) & (d["Year"] <= TOT)]
    return d


def gebied_jaar(d):
    """Lange tabel voor de lijn- en vlakgrafieken: gebied x jaar x bron."""
    t = d[d["Area"].isin(GEBIEDEN) & d["Electricity source"].isin(BRONNEN)].copy()
    t["Gebied"] = t["Area"].map(GEBIEDEN)
    t["Bron"] = t["Electricity source"].map(BRONNEN)
    t["Soort gebied"] = np.where(t["Area type"] == "Region", "Regio", "Land")
    t = t.rename(columns={"Year": "Jaar", "Generation (TWh)": "Opwek TWh", "Share of generation (%)": "Aandeel %"})
    return t[["Gebied", "Soort gebied", "Jaar", "Bron", "Opwek TWh", "Aandeel %"]].sort_values(["Gebied", "Jaar", "Bron"])


def inhaaljaar(reeks_zon, reeks_kern):
    """Eerste jaar waarin zon meer opwekt dan kern en dat daarna zo blijft; NaN als dat (nog) niet zo is.
    Landen zonder kernenergie vallen buiten de vraag (NaN)."""
    s = pd.DataFrame({"zon": reeks_zon, "kern": reeks_kern}).dropna().sort_index()
    if s.empty or s["kern"].max() <= 0:
        return np.nan
    voor = s["zon"] > s["kern"]
    if not voor.iloc[-1]:
        return np.nan
    achter = np.where(~voor.values)[0]
    return int(s.index[achter[-1] + 1]) if len(achter) else int(s.index[0])


def per_land(d):
    """Een rij per land dat sinds 2000 ooit kernstroom maakte."""
    l = d[d["Area type"] == "Country or economy"]
    breed = l.pivot_table(index=["Area", "ISO 3 code", "Year"], columns="Electricity source",
                          values="Generation (TWh)", aggfunc="first").reset_index()
    aandeel = l.pivot_table(index=["Area", "Year"], columns="Electricity source", values="Share of generation (%)",
                            aggfunc="first")
    cap = l[l["Electricity source"] == "Nuclear"].set_index(["Area", "Year"])["Capacity (GW)"]
    ci = l[l["Electricity source"] == "Total generation"].set_index(["Area", "Year"])["Emissions intensity (gCO2e/kWh)"]
    info = l.drop_duplicates("Area").set_index("Area")[["Continent", "EU member"]]
    rijen = []
    for land, g in breed.groupby("Area"):
        g = g.set_index("Year")
        if "Nuclear" not in g or g["Nuclear"].fillna(0).max() <= 0:
            continue
        def w(bron, jaar, bron_df=g):
            return bron_df[bron].get(jaar, np.nan) if bron in bron_df else np.nan
        kern25, cap25 = w("Nuclear", TOT), cap.get((land, TOT), np.nan)
        rijen.append({
            "Land": land, "ISO3": g["ISO 3 code"].iloc[0], "Continent": info.loc[land, "Continent"],
            "Europa": "Europa" if info.loc[land, "Continent"] == "Europe" else "Rest van de wereld",
            "EU": bool(info.loc[land, "EU member"]),
            "Kern TWh 2010": w("Nuclear", 2010), "Kern TWh 2015": w("Nuclear", 2015), "Kern TWh 2025": kern25,
            "Zon TWh 2015": w("Solar", 2015), "Zon TWh 2025": w("Solar", TOT),
            "Wind TWh 2015": w("Wind", 2015), "Wind TWh 2025": w("Wind", TOT),
            "Aandeel kern 2025 %": aandeel["Nuclear"].get((land, TOT), np.nan),
            "Aandeel zon en wind 2025 %": aandeel["Wind and solar"].get((land, TOT), np.nan),
            "Aandeel fossiel 2025 %": aandeel["Fossil"].get((land, TOT), np.nan),
            "CO2 gram per kWh 2025": ci.get((land, TOT), np.nan),
            "Kernvermogen GW 2025": cap25,
            # boven 1 kan niet: dan klopt het vermogen in Ember niet (Belgie), dus leeg laten
            "Benutting kern 2025": (lambda b: b if b <= 1.0 else np.nan)(kern25 / (cap25 * 8.76)) if cap25 and cap25 > 0 else np.nan,
            "Jaar zon voorbij kern": inhaaljaar(g["Solar"] if "Solar" in g else pd.Series(dtype=float), g["Nuclear"]),
        })
    t = pd.DataFrame(rijen)
    t["Kern verschil 2015-2025 TWh"] = t["Kern TWh 2025"] - t["Kern TWh 2015"]
    t["Zon en wind verschil 2015-2025 TWh"] = (t["Zon TWh 2025"] + t["Wind TWh 2025"]) - (t["Zon TWh 2015"] + t["Wind TWh 2015"])
    t["Kern verschil 2015-2025 %"] = 100 * t["Kern verschil 2015-2025 TWh"] / t["Kern TWh 2015"].where(t["Kern TWh 2015"] > 0)
    t["Koers kern"] = koers(t)
    return t.sort_values("Kern TWh 2025", ascending=False)


def koers(t):
    """Geen gegevens 2025: Ember heeft dat jaar geen cijfer (Oekraine). Gestopt: geen kernstroom meer in 2025. Herstart: in 2015 minder dan twee derde van 2010 en daarna weer gegroeid
    (Japan na Fukushima). Afbouw/uitbouw: minstens 10% en 2 TWh minder/meer dan in 2015. Anders stabiel."""
    k10, k15, k25 = (t[f"Kern TWh {j}"].fillna(0) for j in (2010, 2015, 2025))
    d, pct = k25 - k15, t["Kern verschil 2015-2025 %"].fillna(0)
    return np.select([t["Kern TWh 2025"].isna(), k25 <= 0.01, (k15 < k10 * 2 / 3) & (d >= 2), (d <= -2) & (pct <= -10), (d >= 2) & ((pct >= 10) | (k15 <= 0))],
                     ["Geen gegevens 2025", "Gestopt", "Herstart", "Afbouw", "Uitbouw"], "Stabiel")


def inhaal_gebieden(d):
    g = d[d["Area"].isin(GEBIEDEN)]
    uit = {}
    for gebied, x in g.groupby("Area"):
        z = x[x["Electricity source"] == "Solar"].set_index("Year")["Generation (TWh)"]
        k = x[x["Electricity source"] == "Nuclear"].set_index("Year")["Generation (TWh)"]
        uit[GEBIEDEN[gebied]] = inhaaljaar(z, k)
    return uit


def markt(pad=KERN_MARKT):
    """Capture rate van kern en zon per land en jaar op de Europese dagmarkt, gewogen naar kernproductie per zone."""
    if not os.path.exists(pad):
        return pd.DataFrame()
    m = pd.read_csv(pad)
    rijen = []
    for (land, jaar), g in m.groupby(["land", "jaar"]):
        w = g["kern_twh"].fillna(0)
        if w.sum() <= 0:
            continue
        rijen.append({"Land": land, "Jaar": jaar, "Kernenergie": np.average(g["capture_kern"], weights=w),
                      "Zon": np.average(g["capture_zon"].fillna(g["capture_zon"].mean()), weights=w),
                      "Aandeel kern in negatieve uren %": 100 * np.average(g["aandeel_in_negatieve_uren"], weights=w)})
    t = pd.DataFrame(rijen)
    if t.empty:
        return t
    return t.melt(id_vars=["Land", "Jaar", "Aandeel kern in negatieve uren %"], value_vars=["Kernenergie", "Zon"],
                  var_name="Bron", value_name="Capture rate").sort_values(["Land", "Jaar", "Bron"])


def samenvatting(gj, land, inhaal, mk):
    w = gj[(gj["Gebied"] == "Wereld")].pivot_table(index="Jaar", columns="Bron", values="Opwek TWh")
    e = gj[(gj["Gebied"] == "Europa")].pivot_table(index="Jaar", columns="Bron", values="Opwek TWh")
    a = gj[(gj["Gebied"] == "Wereld")].pivot_table(index="Jaar", columns="Bron", values="Aandeel %")
    r = [f"Wereld kern: {w.loc[VAN,'Kernenergie']:.0f} TWh in {VAN}, {w.loc[2015,'Kernenergie']:.0f} in 2015, "
         f"{w.loc[TOT,'Kernenergie']:.0f} in {TOT}; aandeel {a.loc[VAN,'Kernenergie']:.1f}% -> {a.loc[TOT,'Kernenergie']:.1f}%",
         f"Wereld zon: {w.loc[2015,'Zon']:.0f} TWh in 2015 -> {w.loc[TOT,'Zon']:.0f} in {TOT}; zon voorbij kern sinds {inhaal.get('Wereld')}",
         f"Europa kern: {e.loc[VAN,'Kernenergie']:.0f} TWh in {VAN} -> {e.loc[TOT,'Kernenergie']:.0f} in {TOT}; "
         f"zon {e.loc[TOT,'Zon']:.0f}, wind {e.loc[TOT,'Wind']:.0f} TWh"]
    for gebied in ["Europa", "EU", "Noord-Amerika", "Azie", "China", "Verenigde Staten", "Frankrijk", "Duitsland", "Japan", "India"]:
        r.append(f"  zon voorbij kern, {gebied}: {inhaal.get(gebied)}")
    for koers, g in land.groupby("Koers kern"):
        r.append(f"Koers {koers}: {', '.join(g['Land'].head(12))}{' ...' if len(g) > 12 else ''}")
    r.append("Grootste groei kern 2015-2025 (TWh): " + ", ".join(
        f"{n} {v:+.0f}" for n, v in land.nlargest(5, "Kern verschil 2015-2025 TWh")[["Land", "Kern verschil 2015-2025 TWh"]].values))
    r.append("Grootste krimp kern 2015-2025 (TWh): " + ", ".join(
        f"{n} {v:+.0f}" for n, v in land.nsmallest(5, "Kern verschil 2015-2025 TWh")[["Land", "Kern verschil 2015-2025 TWh"]].values))
    schoon = land[land["Aandeel fossiel 2025 %"].notna()]
    r.append("Laagste CO2-intensiteit onder landen met kern (g/kWh, 2025): " + ", ".join(
        f"{n} {v:.0f}" for n, v in schoon.nsmallest(6, "CO2 gram per kWh 2025")[["Land", "CO2 gram per kWh 2025"]].values))
    if not mk.empty:
        p = mk[mk["Jaar"] == mk["Jaar"].max()].pivot_table(index="Bron", values="Capture rate", aggfunc="mean")
        r.append(f"Europese dagmarkt {mk['Jaar'].max()}: capture rate kern gemiddeld {p.loc['Kernenergie'].iloc[0]:.2f}, "
                 f"zon in dezelfde landen {p.loc['Zon'].iloc[0]:.2f}")
    return "\n".join(r)


def main(ember=EMBER, kern_markt=KERN_MARKT, uit=UIT):
    if not os.path.exists(ember):
        sys.exit(f"{ember} ontbreekt: haal eerst de Ember-bestanden op (eti.ember_global)")
    d = lees(ember)
    gj, land, mk = gebied_jaar(d), per_land(d), markt(kern_markt)
    inhaal = inhaal_gebieden(d)
    os.makedirs(uit, exist_ok=True)
    gj.to_csv(os.path.join(uit, "t6_kern_gebied_jaar.csv"), index=False)
    land.to_csv(os.path.join(uit, "t7_kern_land.csv"), index=False)
    if not mk.empty:
        mk.to_csv(os.path.join(uit, "t8_kern_markt.csv"), index=False)
    tekst = samenvatting(gj, land, inhaal, mk)
    print(tekst)
    os.makedirs("resultaten", exist_ok=True)
    open("resultaten/kern_wereld.txt", "w", encoding="utf-8").write(tekst + "\n")
    print(f"\nGeschreven: {uit}/t6 ({len(gj)} rijen), t7 ({len(land)} landen), t8 ({len(mk)} rijen)")


if __name__ == "__main__":
    main()
