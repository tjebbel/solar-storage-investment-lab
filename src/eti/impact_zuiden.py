"""Dashboards 14 (impactbelegger) en 15 (zon in het Mondiale Zuiden).

  t27_impact.csv   per studieregio en jaar (2025, 2030, 2050): LCOE, WACC, ton CO2 per miljoen euro per jaar
                   (fact_regio_jaar) en de marge van zon tegen de markt waar die bekend is (Nederland, Spanje: t1).
                   De LCOE komt uit het studiemodel (Nederland: PBL-referentieproject, 740 vollasturen). Ernaast staat de
                   IRENA-kostprijs van 2024 en de marge daarbij, omdat dashboards 5, 26 en 27 die grondslag gebruiken.
                   Additionaliteit (indicatief): hoge marge zonder steun = het project komt er waarschijnlijk ook zonder
                   dit geld, dus weinig investeerdersimpact (Brest en Born 2013).
  t28_zuiden.csv   per locatie: instraling (kWh/m2) en vollasturen (gemiddelde 2015-2025, fact_instraling_wereld);
                   per studieregio: LCOE bij de eigen WACC en bij de Nederlandse WACC (5%).
                   AANNAME: 85% van de LCOE is kapitaal; looptijd 25 jaar.
                   LCOE(w2) = LCOE(w1) x (0,15 + 0,85 x CRF(w2) / CRF(w1)),  CRF(w) = w / (1 - (1 + w)^-25).
Gebruik:  PYTHONPATH=src python3 -m eti.impact_zuiden
"""
import numpy as np
import pandas as pd

KAPITAALDEEL, LOOPTIJD, WACC_NL = 0.85, 25, 0.05


def crf(w, n=LOOPTIJD):
    return w / (1 - (1 + w) ** -n)


def lcoe_bij(lcoe, w_eigen, w_nieuw):
    return lcoe * ((1 - KAPITAALDEEL) + KAPITAALDEEL * crf(w_nieuw) / crf(w_eigen))


def impact(regio="powerbi/data/fact_regio_jaar.csv", t1="tableau/data/t1_zonejaar.csv"):
    r = pd.read_csv(regio)
    t = pd.read_csv(t1)
    t = t[t["Jaar"] == 2025].assign(cp=lambda d: d["Gemiddelde prijs"] * d["Capture rate zon"])
    markt = {"Nederland": t[t["Landcode"] == "NLD"]["cp"].mean(), "Europa (Spanje)": t[t["Landcode"] == "ESP"]["cp"].mean()}
    r["Capture-prijs zon 2025"] = r["regio"].map(markt)
    r["Marge zon EUR/MWh"] = np.where(r["jaar"] == 2025, r["Capture-prijs zon 2025"] - r["lcoe_eur_mwh"], np.nan)
    r["Additionaliteit (indicatief)"] = np.select(
        [r["Marge zon EUR/MWh"].isna(), r["Marge zon EUR/MWh"] > 10, r["Marge zon EUR/MWh"] < 0],
        ["onbekend: geen marktprijs in het project", "laag: rendabel zonder steun", "hoog: zonder steun niet rendabel"],
        "middel")
    # Tweede grondslag naast het studiemodel: gemeten projecten van 2024 (IRENA), zelfde bron als dashboards 5, 26 en 27.
    from eti.lcoe import per_land
    irena = per_land(["NLD", "ESP"])["LCOE IRENA"]
    r["LCOE IRENA 2024 EUR/MWh"] = np.where(r["jaar"] == 2025, r["regio"].map({"Nederland": irena["NLD"], "Europa (Spanje)": irena["ESP"]}), np.nan)
    r["Marge zon bij IRENA EUR/MWh"] = r["Capture-prijs zon 2025"] - r["LCOE IRENA 2024 EUR/MWh"]
    r["LCOE bij 5% WACC"] = lcoe_bij(r["lcoe_eur_mwh"], r["wacc"], WACC_NL)
    return r.rename(columns={"regio": "Regio", "jaar": "Jaar", "lcoe_eur_mwh": "LCOE EUR/MWh", "wacc": "WACC",
                             "financieringsaandeel": "Financieringsaandeel", "t_co2_per_meur_jaar": "Ton CO2 per M EUR per jaar"})


def zuiden(pad="powerbi/data/fact_instraling_wereld.csv"):
    i = pd.read_csv(pad)
    return i.groupby("locatie").agg(Instraling=("ghi_kwh_m2", "mean"), Vollasturen=("vollasturen_schatting", "mean"),
                                    Jaren=("jaar", "nunique")).reset_index().rename(columns={"locatie": "Locatie"}).sort_values("Vollasturen", ascending=False)


def main():
    im, z = impact(), zuiden()
    im.to_csv("tableau/data/t27_impact.csv", index=False)
    z["Vollasturen tegen Nederland"] = z["Vollasturen"] / z.loc[z["Locatie"] == "Nederland", "Vollasturen"].iloc[0]
    z.to_csv("tableau/data/t28_zuiden.csv", index=False)
    k = im[im["Jaar"] == 2025][["Regio", "LCOE EUR/MWh", "WACC", "LCOE bij 5% WACC", "Ton CO2 per M EUR per jaar",
                                "Marge zon EUR/MWh", "Additionaliteit (indicatief)"]]
    tekst = k.round(2).to_string(index=False) + "\n\n" + z.round(2).to_string(index=False)
    print(tekst)
    open("resultaten/impact_zuiden.txt", "w", encoding="utf-8").write(tekst + "\n")


if __name__ == "__main__":
    main()
