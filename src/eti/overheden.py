"""Dashboards 9 tot en met 11: de EU, de VS en China, met dezelfde opbouw (doel, instrument en effect, trilemma).

  t18_convergentie.csv   per maand: spreiding van de groothandelsprijs over de 37 zones (p10, mediaan, p90, IQR)
  t20_bouwgolf.csv       per maand: nieuw zon- en windvermogen (GW) in de VS, China, Duitsland en Nederland,
                         met de beleidsdata als markering (OBBBA 4-7-2025, bouwstart-grens 4-7-2026, Document 136 1-6-2025)
  t21_vs_staten.csv      per Amerikaanse staat: aandeel zon en wind in de opwek, laatste jaar
  t22_china_export.csv   per jaar en continent van bestemming: export van Chinese panelen in GW en USD
Gebeurtenisstudie: gemiddelde maandelijkse toevoeging in de 6 maanden voor en na de beleidsdatum, plus de piekmaand.
Bronnen: Ember (capaciteit per maand, opwek per staat, Chinese zonexport), t2 (prijzen).
Gebruik:  PYTHONPATH=src python3 -m eti.overheden
"""
import os

import numpy as np
import pandas as pd

UIT = "tableau/data"
GEBEURTENISSEN = {"USA": [("2025-07-01", "OBBBA getekend (4 juli 2025)"), ("2026-07-01", "Grens bouwstart zon en wind (4 juli 2026)")],
                  "CHN": [("2025-06-01", "Document 136: nieuwe projecten via de markt (1 juni 2025)")]}
LANDEN = {"USA": "Verenigde Staten", "CHN": "China", "DEU": "Duitsland", "NLD": "Nederland"}


def convergentie(t2="tableau/data/t2_land_maand.csv"):
    d = pd.read_csv(t2)
    g = d.groupby("Maand")["Gemiddelde prijs"]
    t = pd.DataFrame({"Zones": g.count(), "P10": g.quantile(0.1), "Mediaan": g.median(), "P90": g.quantile(0.9)})
    t["IQR"] = g.quantile(0.75) - g.quantile(0.25)
    t["Spreiding P90-P10"] = t["P90"] - t["P10"]
    t["Relatieve spreiding"] = t["Spreiding P90-P10"] / t["Mediaan"].abs()
    return t.reset_index()


def bouwgolf(cap="powerbi/data/fact_ember_capaciteit_maand.csv"):
    c = pd.read_csv(cap)
    c = c[c["ISO 3 Code"].isin(LANDEN) & c["Source"].isin(["Solar", "Wind"])].copy()
    c["Maand"] = pd.to_datetime(dict(year=c["Year"], month=c["Month"], day=1))
    c["Land"] = c["ISO 3 Code"].map(LANDEN)
    c["Bron"] = c["Source"].map({"Solar": "Zon", "Wind": "Wind"})
    c = c.rename(columns={"Installed Capacity": "Vermogen GW", "Capacity additions (month-on-month)": "Toevoeging GW"})
    c["Gebeurtenis"] = ""
    for iso, lijst in GEBEURTENISSEN.items():
        for datum, naam in lijst:
            c.loc[(c["ISO 3 Code"] == iso) & (c["Maand"] == datum), "Gebeurtenis"] = naam
    return c[["Land", "ISO 3 Code", "Bron", "Maand", "Vermogen GW", "Toevoeging GW", "Gebeurtenis"]].sort_values(["Land", "Bron", "Maand"])


def gebeurtenisstudie(b, venster=6):
    rijen = []
    for iso, lijst in GEBEURTENISSEN.items():
        z = b[(b["ISO 3 Code"] == iso) & (b["Bron"] == "Zon")].set_index("Maand")["Toevoeging GW"]
        for datum, naam in lijst:
            d = pd.Timestamp(datum)
            voor = z[(z.index < d) & (z.index >= d - pd.DateOffset(months=venster))]
            na = z[(z.index > d) & (z.index <= d + pd.DateOffset(months=venster))]
            rond = z[(z.index >= d - pd.DateOffset(months=venster)) & (z.index <= d)]
            rijen.append({"Land": LANDEN[iso], "Gebeurtenis": naam, "GW per maand ervoor": voor.mean(),
                          "GW per maand erna": na.mean() if len(na) else np.nan, "Maanden erna": len(na),
                          "Piekmaand": rond.idxmax().strftime("%Y-%m") if len(rond) else "", "Piek GW": rond.max()})
    return pd.DataFrame(rijen)


def vs_staten(pad="powerbi/data/fact_ember_vs_staat.csv"):
    v = pd.read_csv(pad)
    jaar = v["Year"].max()
    v = v[(v["Year"] == jaar) & v["Electricity source"].isin(["Solar", "Wind"])]
    t = v.pivot_table(index="State", columns="Electricity source", values="Share of generation (%)").fillna(0)
    t.columns = [f"Aandeel {'zon' if k == 'Solar' else 'wind'} %" for k in t.columns]
    t["Aandeel zon en wind %"] = t.sum(axis=1)
    t["Jaar"] = jaar
    return t.reset_index().rename(columns={"State": "Staat"}).sort_values("Aandeel zon en wind %", ascending=False)


def china_export(pad="data/ember_global/mart_solar_exports_full_release_monthly.csv"):
    e = pd.read_csv(pad, low_memory=False)
    e = e[(e["Area type"] == "Country or economy") & (e["Commodity type"] == "Panels")].copy()
    e["Jaar"] = e["Date"].str[:4].astype(int)
    e["Bestemming"] = e["Region"].fillna("Onbekend")
    t = e.groupby(["Jaar", "Bestemming"]).agg(GW=("Capacity (MW)", lambda s: s.sum() / 1000),
                                               USD_mld=("Amount (USD)", lambda s: s.sum() / 1e9),
                                               maanden=("Date", "nunique")).reset_index()
    t["Prijs USD per W"] = t["USD_mld"] / t["GW"]
    return t.rename(columns={"USD_mld": "USD miljard", "maanden": "Maanden"})


def main():
    conv, b = convergentie(), bouwgolf()
    st, vs, ce = gebeurtenisstudie(b), vs_staten(), china_export()
    conv.to_csv(os.path.join(UIT, "t18_convergentie.csv"), index=False)
    b.to_csv(os.path.join(UIT, "t20_bouwgolf.csv"), index=False)
    vs.to_csv(os.path.join(UIT, "t21_vs_staten.csv"), index=False)
    ce.to_csv(os.path.join(UIT, "t22_china_export.csv"), index=False)
    st.to_csv("resultaten/gebeurtenisstudie.csv", index=False)
    conv["Jaar"] = conv["Maand"].str[:4]
    j = conv.groupby("Jaar")[["Mediaan", "Spreiding P90-P10", "Relatieve spreiding"]].mean().round(2)
    r = ["Prijsspreiding over de zones per jaar (gemiddelde van de maanden):", j.to_string(), "", "Gebeurtenisstudie zon:",
         st.round(1).to_string(index=False), "", "Top 5 staten zon en wind:", vs.head(5).round(1).to_string(index=False), "",
         "Chinese panelexport (GW) per jaar en bestemming:",
         ce.pivot_table(index="Jaar", columns="Bestemming", values="GW").round(0).to_string()]
    tekst = "\n".join(r)
    print(tekst)
    open("resultaten/overheden.txt", "w", encoding="utf-8").write(tekst + "\n")


if __name__ == "__main__":
    main()
