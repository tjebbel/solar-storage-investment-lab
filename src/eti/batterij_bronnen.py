"""Vervolgonderzoek 3: waar komt de opbrengst van een batterij vandaan, per zone? Dagmarkt, FCR en aFRR naast elkaar.

Drie bronnen, met wat de data wel en niet toelaat:
- Dagmarkt (arbitrage): per zone en jaar, 2 uur opslag, plan op de prijzen van gisteren (fact_flex_land,
  omzet_realistisch_per_mw). Dit is voor alle 37 zones beschikbaar.
- FCR: de capaciteitsprijs per blok van vier uur (fact_fcr_nl). FCR wordt sinds 2020 grotendeels in een gezamenlijke
  veiling ingekocht (FCR Cooperation: Belgie, Denemarken-West, Duitsland, Frankrijk, Nederland, Oostenrijk, Slovenie,
  Zwitserland). De Nederlandse prijs staat daarom ook voor de andere leden, als benadering: bij beperkte
  grenscapaciteit wijkt de prijs per land af. Voor zones buiten de samenwerking is er geen FCR-prijs in de data.
- aFRR-capaciteit: ENTSO-E gaf deze reeks niet terug. Er zijn twee ijkpunten voor Nederland van Modo Energy: 105 euro per
  MW per uur in 2022 en 27 euro per MW per uur in 2026. Hier alleen het ijkpunt 2026, met een toewijzing van 50% en
  100% van de uren. Voor andere landen is er geen prijs.
Let op: dezelfde MW kan op hetzelfde moment niet voor FCR en aFRR worden aangeboden. De bronnen zijn alternatieven per
uur, geen optelsom. De som van de beste keuze per dag staat al in eti.stapel (alleen Nederland).

Schrijft powerbi/data/fact_batterij_bronnen_BB.csv (per zone en jaar) en fact_batterij_bronnen_nl_BB.csv.
Gebruik:  PYTHONPATH=src python3 -m eti.batterij_bronnen
"""
import os

import numpy as np
import pandas as pd

from . import stapel

DATA = "powerbi/data"
FCR_LEDEN = {"BE", "DK1", "DE-LU", "DE", "FR", "NL", "AT", "SI", "CH"}
AFRR_NL_2026, AFRR_NL_2022 = 27.0, 105.0         # euro per MW per uur, Modo Energy
TOEWIJZING = (0.5, 1.0)
UREN = 8760


def per_zone(data=DATA):
    lj = pd.read_csv(os.path.join(data, "fact_land_jaar.csv"))[["land", "biedzone", "jaar"]]
    fl = pd.read_csv(os.path.join(data, "fact_flex_land.csv"))
    fl = fl[fl.uren_opslag == 2][["land", "jaar", "omzet_realistisch_per_mw"]]
    z = lj.merge(fl, on=["land", "jaar"], how="left").rename(columns={"omzet_realistisch_per_mw": "dagmarkt_per_mw"})
    fcr = stapel.fcr_per_dag(data).reset_index()
    fcr["jaar"] = fcr.datum.str[:4].astype(int)
    fcr_jaar = fcr.groupby("jaar").agg(dagen=("fcr", "size"), fcr_per_mw=("fcr", lambda s: s.mean() * 365))
    z["fcr_lid"] = z.biedzone.isin(FCR_LEDEN)
    z = z.merge(fcr_jaar, on="jaar", how="left")
    z.loc[~z.fcr_lid, ["fcr_per_mw", "dagen"]] = np.nan
    z = z.rename(columns={"dagen": "fcr_dagen_in_data"})
    nl = z.biedzone == "NL"
    for t in TOEWIJZING:
        z[f"afrr_capaciteit_{int(t * 100)}pct_per_mw"] = np.where(nl & (z.jaar == 2026), AFRR_NL_2026 * UREN * t, np.nan)
    z["fcr_gedeeld_door_dagmarkt"] = z.fcr_per_mw / z.dagmarkt_per_mw
    z["grootste_bron"] = np.where(z.fcr_per_mw > z.dagmarkt_per_mw, "FCR", np.where(z.dagmarkt_per_mw.notna(), "dagmarkt", None))
    return z.sort_values(["jaar", "dagmarkt_per_mw"], ascending=[True, False]).reset_index(drop=True)


def nederland(z):
    t = z[z.biedzone == "NL"][["jaar", "dagmarkt_per_mw", "fcr_per_mw", "fcr_dagen_in_data", "afrr_capaciteit_50pct_per_mw", "afrr_capaciteit_100pct_per_mw"]]
    return t[t.jaar >= 2022]


def main(data=DATA, uit=DATA):
    z = per_zone(data)
    z.to_csv(os.path.join(uit, "fact_batterij_bronnen_BB.csv"), index=False)
    n = nederland(z)
    n.to_csv(os.path.join(uit, "fact_batterij_bronnen_nl_BB.csv"), index=False)
    pd.set_option("display.width", 220)
    print(n.round(0).to_string(index=False))
    j = z[z.jaar == 2025]
    print("\n2025, FCR-leden:"); print(j[j.fcr_lid][["biedzone", "dagmarkt_per_mw", "fcr_per_mw", "fcr_gedeeld_door_dagmarkt"]].round(2).to_string(index=False))
    print("\n2025: zones met dagmarkt boven de FCR-opbrengst:", int((j.dagmarkt_per_mw > j.fcr_per_mw.max()).sum()), "van", len(j))
    return z, n


if __name__ == "__main__":
    main()
