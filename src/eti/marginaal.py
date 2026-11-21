"""Dashboard 25 "What does a MWh really avoid?": gemiddelde en marginale CO2-factor per uur, en wat zon en een batterij vermijden.

Bron: de uurtabellen van eti.uurdata (Energy-Charts, opwek per brandstof, lokale tijd, cache in data/cache).

Methode
  Uitstoot per uur  E_t = som over fossiele brandstoffen van opwek (MW) x emissiefactor (t CO2 per MWh elektriciteit).
  Emissiefactoren   IPCC 2006 standaardwaarden per brandstof (kg CO2 per GJ) gedeeld door een typisch centralerendement:
                    bruinkool 101 / 38% = 0,96; steenkool 94,6 / 40% = 0,85; aardgas 56,1 / 50% = 0,40; olie 77,4 / 35% = 0,80;
                    kolengas 1,0 en "Others" 0,6 (aanname); afval 0,5 (aanname: half fossiel). Biomassa telt als 0, zoals in
                    de energiestatistiek; kern, water, wind en zon 0. Alleen directe uitstoot (geen keten), dus lager dan Ember/OWID.
  Gemiddelde factor AEF_t = E_t / totale opwek_t.
  Marginale factor  twee varianten, samen een bandbreedte:
                    - bovengrens "fossil response" (Siler-Evans e.a. 2012): helling van de uur-op-uur verandering in uitstoot tegen
                      de verandering in fossiele opwek. Neemt aan dat een extra MWh zon een fossiele MWh verdringt (ergens).
                    - ondergrens "domestic" (Hawkes 2010): helling tegen de verandering in de restlast (verbruik min wind en zon).
                      Telt alleen de binnenlandse fossiele reactie; wat kern, water of export opvangen telt als 0.
                    In een sterk verbonden net ligt de werkelijkheid ertussen. Per zone-jaar, per seizoen (zomer apr-sep, winter okt-mrt) en uur van de dag (48 hellingen,
                    begrensd tussen 0 en 1,2). Uren met een prijs <= 0 krijgen MEF 0: dan is hernieuwbare stroom de marginale bron
                    (curtailment) en verdringt extra zon of extra batterijladen geen fossiele centrale.
  Zon               vermeden t per MWh = gewogen met het zonprofiel van die zone-jaar (AEF en MEF).
  Batterij          2 uur, 1 cyclus per dag, 88% rendement, perfecte voorkennis (zoals t55): laden in de 2 goedkoopste, ontladen in de
                    2 duurste uren. Netto CO2 per MW per jaar = sum(MEF ontladen x 0,88 x 2) - sum(MEF laden x 2). Negatief = de batterij
                    verhoogt de uitstoot (laden op kolen, ontladen op gas).

Betrouwbaar (kolom Reliable): opwekdekking 80-120% van OWID, minder dan 10% ongeclassificeerde opwek ("Others") en een gemiddelde
factor tussen 0,6 en 1,2 keer de OWID-levenscycluswaarde. Nederland valt af: Energy-Charts boekt 39 TWh als "Others" en mist de
meeste zon. Gebruik voor Nederland de CBS/Ember-factor (t13: 0,25). De bovengrens is leeg in zones met minder dan 10% fossiele opwek.

Beperkingen: import en export worden niet gevolgd (een kleine zone met veel handel heeft een onzekere MEF); de regressie ziet alleen
binnenlandse fossiele centrales; de emissiefactoren zijn standaardwaarden, geen centrale-specifieke.

Tabellen (tableau/data en tableau/data_en, Engels):
  t63_marginal_factor_hour  zone x jaar x seizoen x uur: AEF, MEF, aandeel uren met prijs <= 0
  t64_avoided_per_mwh       zone x jaar: AEF jaar, AEF en MEF gewogen met zon, batterij-effect, validatie tegen OWID
Gebruik: PYTHONPATH=src python3 -m eti.marginaal  [zones...]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from eti import uurdata as u

EF = {"Fossil brown coal / lignite": 0.957, "Fossil hard coal": 0.851, "Fossil gas": 0.404, "Fossil oil": 0.796,
      "Fossil coal-derived gas": 1.0, "Fossil oil shale": 1.0, "Fossil peat": 1.0, "Others": 0.6, "Waste": 0.5}
FOSSIEL_COL = tuple(k for k in EF if k.startswith("Fossil"))
JAREN = range(2019, 2027)
RENDEMENT, UREN_OPSLAG = 0.88, 2


def uitstoot(df):
    """E_t (t/h), fossiele opwek (MW), totale opwek (MW)."""
    nul = pd.Series(0.0, index=df.index)
    e = sum((df[c].clip(lower=0).fillna(0) * f for c, f in EF.items() if c in df), nul)
    fos = sum((df[c].clip(lower=0).fillna(0) for c in FOSSIEL_COL if c in df), nul)
    totaal, _ = u.opwek(df)
    return e, fos, totaal


def seizoen(idx):
    return np.where((idx.month >= 4) & (idx.month <= 9), "Summer (Apr-Sep)", "Winter (Oct-Mar)")


def hellingen(e, rest):
    """MEF per (seizoen, uur): OLS-helling dE op dR (restlast), begrensd [0, 1.2]; minder dan 100 punten of geen spreiding -> NaN."""
    d = pd.DataFrame({"dE": e.diff(), "dF": rest.diff()}, index=e.index).dropna()
    d["s"], d["h"] = seizoen(d.index), d.index.hour
    uit = {}
    for (s, h), g in d.groupby(["s", "h"]):
        if len(g) < 100 or g.dF.var() <= 0 or g.dE.abs().sum() == 0:
            uit[(s, h)] = np.nan
            continue
        b = np.cov(g.dE, g.dF)[0, 1] / g.dF.var()
        uit[(s, h)] = float(np.clip(b, 0, 1.2))
    return uit


def zonejaar(zone, jaar):
    df = u.uren(zone, jaar)
    if df.empty or not any(c in df for c in FOSSIEL_COL + ("Nuclear", "Solar")):
        return None, None
    df = u._klaar(df)
    e, fos, totaal = uitstoot(df)
    if totaal.sum() <= 0:
        return None, None
    rest = df["Load"] - u.zon(df).fillna(0) - df[[c for c in df.columns if c.startswith("Wind")]].sum(axis=1) if "Load" in df else None
    if rest is None or rest.notna().sum() < 2000:
        return None, None
    s, h = seizoen(df.index), df.index.hour
    def reeks(hel):
        m = pd.Series([hel.get((a, b), np.nan) for a, b in zip(s, h)], index=df.index)
        m[df.Price <= 0] = 0.0
        return m
    mef, mef_laag = reeks(hellingen(e, fos)), reeks(hellingen(e, rest))
    aef = (e / totaal.where(totaal > 0)).clip(upper=1.2)
    # tabel per seizoen x uur
    t = pd.DataFrame({"Season": s, "Hour": h, "AEF": aef, "MEF": mef, "MEFL": mef_laag, "neg": (df.Price <= 0).astype(float)})
    per = t.groupby(["Season", "Hour"]).agg(**{"Average factor t/MWh": ("AEF", "mean"),
                                               "Marginal factor, fossil response t/MWh": ("MEF", "mean"),
                                               "Marginal factor, domestic t/MWh": ("MEFL", "mean"),
                                               "Share of hours with price <= 0 %": ("neg", "mean")}).reset_index()
    per["Share of hours with price <= 0 %"] *= 100
    per.insert(0, "Year", jaar); per.insert(0, "Zone", zone)
    # zon
    z = u.zon(df).clip(lower=0)
    zs = z.sum()
    # batterij: per dag 2 goedkoopste uren laden, 2 duurste ontladen
    p = df.Price
    netto, netto_l, ontladen_mwh = 0.0, 0.0, 0.0
    b = pd.DataFrame({"p": p, "m": mef, "l": mef_laag}).dropna()
    for _, dag in b.groupby(b.index.date):
        if len(dag) < 20:
            continue
        laag, hoog = dag.nsmallest(UREN_OPSLAG, "p"), dag.nlargest(UREN_OPSLAG, "p")
        netto += hoog.m.sum() * RENDEMENT - laag.m.sum()
        netto_l += hoog.l.sum() * RENDEMENT - laag.l.sum()
        ontladen_mwh += UREN_OPSLAG * RENDEMENT
    rij = {"Zone": zone, "Year": jaar,
           "Average factor t/MWh (year)": float(e.sum() / totaal.sum()),
           "Average factor, solar hours t/MWh": float((aef * z).sum() / zs) if zs > 0 else np.nan,
           "Marginal factor, solar hours, fossil response t/MWh": float((mef * z).sum() / zs) if zs > 0 else np.nan,
           "Marginal factor, solar hours, domestic t/MWh": float((mef_laag * z).sum() / zs) if zs > 0 else np.nan,
           "Battery net CO2 t per MW per year, fossil response": float(netto),
           "Battery net CO2 t per MW per year, domestic": float(netto_l),
           "Battery net CO2 t per MWh discharged, fossil response": float(netto / ontladen_mwh) if ontladen_mwh else np.nan,
           "Hours with price <= 0": int((p <= 0).sum()),
           "Fossil generation TWh": float(fos.sum() / 1e6), "Direct CO2 Mt": float(e.sum() / 1e6),
           "Fossil share %": float(100 * fos.sum() / totaal.sum()),
           "Others share %": float(100 * df["Others"].clip(lower=0).sum() / totaal.sum()) if "Others" in df else 0.0}
    return per, rij


def main(lijst=None, jaren=JAREN):
    lijst = lijst or u.zones()
    naam = u.namen()
    per, rijen = [], []
    for zone in lijst:
        for j in jaren:
            a, b = zonejaar(zone, j)
            if a is not None:
                per.append(a); rijen.append(b)
    t63 = pd.concat(per, ignore_index=True)
    t64 = pd.DataFrame(rijen)
    for t in (t63, t64):
        t.insert(1, "Zone name", t.Zone.map(lambda z: naam.get(z, z)))
    # validatie tegen OWID (Ember, levenscyclus, g/kWh) en dekking uit t59
    t64["Country"] = t64.Zone.map(u.land)
    o = pd.read_csv(u.RAW / "owid-energy-data.csv", usecols=["country", "year", "carbon_intensity_elec"])
    o = o.rename(columns={"country": "Country", "year": "Year", "carbon_intensity_elec": "OWID carbon intensity g/kWh"})
    t64 = t64.merge(o, on=["Country", "Year"], how="left")
    t64["Ours vs OWID"] = 1000 * t64["Average factor t/MWh (year)"] / t64["OWID carbon intensity g/kWh"]
    dek = Path("tableau/data_en/t59_coverage.csv")
    if dek.exists():
        d = pd.read_csv(dek)[["Zone", "Year", "Generation coverage", "Solar coverage ok"]]
        t64 = t64.merge(d, on=["Zone", "Year"], how="left")
        t64["Generation coverage ok"] = t64["Generation coverage"].between(0.8, 1.2)
    else:
        t64["Generation coverage ok"] = True
    # betrouwbaar: dekking goed, weinig ongeclassificeerde opwek, gemiddelde factor in lijn met OWID (dat is levenscyclus, dus hoger)
    t64["Reliable"] = (t64["Generation coverage ok"].fillna(False) & (t64["Others share %"] < 10)
                       & t64["Ours vs OWID"].between(0.6, 1.2))
    # de bovengrens zegt niets in zones met bijna geen fossiele centrales (elke kleine wijziging geeft de factor van gas)
    weinig = t64["Fossil share %"] < 10
    for c in ("Marginal factor, solar hours, fossil response t/MWh", "Battery net CO2 t per MW per year, fossil response",
              "Battery net CO2 t per MWh discharged, fossil response"):
        t64.loc[weinig, c] = np.nan
    for uit in u.UIT:
        uit.mkdir(parents=True, exist_ok=True)
        t63.round(4).to_csv(uit / "t63_marginal_factor_hour.csv", index=False)
        t64.round(4).to_csv(uit / "t64_avoided_per_mwh.csv", index=False)
    return t63, t64


if __name__ == "__main__":
    a, b = main(sys.argv[1:] or None)
    print(len(a), "rijen t63;", len(b), "rijen t64")
    k = b[b.Year == 2025].set_index("Zone name")
    print(k[["Average factor t/MWh (year)", "Average factor, solar hours t/MWh", "Marginal factor, solar hours, fossil response t/MWh",
             "Marginal factor, solar hours, domestic t/MWh", "Battery net CO2 t per MW per year, fossil response",
             "Battery net CO2 t per MW per year, domestic", "Ours vs OWID", "Reliable"]].round(3).to_string())
