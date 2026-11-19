"""Dashboard 13: de netbeheerder, met elektrisch rijden (optie G).

  t25_flex_nl.csv   per jaar: aFRR-energieprijzen op en af per kwartier (gemiddelde, mediaan, P99, aandeel kwartieren
                    boven 200 EUR/MWh en met negatieve afregelprijs), negatieve uren (t1)
  t26_ev_net.csv    per land: EV-vloot, jaarvraag (GWh), en een AANNAME-scenario voor de avondpiek:
                    ongestuurd laden = 50% van de dagvraag in 4 avonduren (17-21 uur), gestuurd laden = 50% in 5 middaguren.
                    Extra piek in GW = jaarvraag / 365 x aandeel / uren.  Dit is een illustratie, geen meting.
Bron: fact_afrr_energie_nl (kwartieren, 2023 tot 26 september 2025), fact_ember_ev_vloot, fact_grensstromen_nl, t1.
Gebruik:  PYTHONPATH=src python3 -m eti.net_flex
"""
import numpy as np
import pandas as pd

AANDEEL, UREN_AVOND, UREN_MIDDAG = 0.5, 4, 5


def flex(afrr="powerbi/data/fact_afrr_energie_nl.csv", t1="tableau/data/t1_zonejaar.csv",
         grens="powerbi/data/fact_grensstromen_nl.csv"):
    a = pd.read_csv(afrr)
    a["Jaar"] = a["kwartier_utc"].str[:4].astype(int)
    g = a.groupby("Jaar")
    f = pd.DataFrame({"Kwartieren": g.size(), "Op gemiddeld": g["op_eur_mwh"].mean(), "Op mediaan": g["op_eur_mwh"].median(),
                      "Op P99": g["op_eur_mwh"].quantile(0.99),
                      "Aandeel op boven 200 %": g["op_eur_mwh"].apply(lambda s: 100 * (s > 200).mean()),
                      "Af gemiddeld": g["af_eur_mwh"].mean(),
                      "Aandeel af negatief %": g["af_eur_mwh"].apply(lambda s: 100 * (s < 0).mean())})
    t = pd.read_csv(t1)
    f = f.join(t[t["Zone"] == "NL"].set_index("Jaar")["Negatieve uren"], how="outer")
    # netto import (fact_grensstromen_nl) bewust weggelaten: het teken en de dekking per jaar zijn nog niet gecontroleerd
    return f.rename_axis("Jaar").reset_index()


def ev(pad="powerbi/data/fact_ember_ev_vloot.csv"):
    e = pd.read_csv(pad)
    e = e[e["Area type"] == "Country or economy"].rename(columns={
        "Area": "Land", "EV fleet (vehicles)": "EV-vloot", "EV fleet electricity demand (GWh per year)": "Vraag GWh per jaar",
        "Oil displaced (thousand barrels of oil equivalent per year)": "Olie verdrongen kbbl per jaar"})
    dag = e["Vraag GWh per jaar"] / 365
    e["Piek ongestuurd GW (aanname)"] = dag * AANDEEL / UREN_AVOND        # GWh per dag / uren = GW
    e["Middagafname gestuurd GW (aanname)"] = dag * AANDEEL / UREN_MIDDAG
    return e[["Land", "ISO 3 code", "Latest available date", "EV-vloot", "Vraag GWh per jaar", "Olie verdrongen kbbl per jaar",
              "Piek ongestuurd GW (aanname)", "Middagafname gestuurd GW (aanname)"]].sort_values("Vraag GWh per jaar", ascending=False)


def main():
    f, e = flex(), ev()
    f.to_csv("tableau/data/t25_flex_nl.csv", index=False)
    e.to_csv("tableau/data/t26_ev_net.csv", index=False)
    nl = e[e["ISO 3 code"] == "NLD"].iloc[0]
    tekst = (f.round(1).to_string(index=False) + f"\n\nNederland: {nl['EV-vloot']:,.0f} EV's, {nl['Vraag GWh per jaar']:,.0f} GWh per jaar; "
             f"ongestuurd laden geeft (aanname) ongeveer {nl['Piek ongestuurd GW (aanname)']:.2f} GW extra avondpiek, "
             f"gestuurd laden neemt {nl['Middagafname gestuurd GW (aanname)']:.2f} GW van het middagoverschot op.")
    print(tekst)
    open("resultaten/net_flex.txt", "w", encoding="utf-8").write(tekst + "\n")


if __name__ == "__main__":
    main()
