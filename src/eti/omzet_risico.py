"""Dashboard 26 "Revenue at risk 2030": wat de Hirth-helling betekent voor de opbrengst van zon als landen hun 2030-doel halen.

Invoer: t1_zonejaar (capture rate en gemiddelde prijs 2025 per zone, gemiddeld per land), t13_kostencurve (zon 2025 en doel 2030,
TWh; LCOE), t56_hirth (helling per zone, alleen betrouwbare zones; ontbreekt die, dan de mediaan -0,020), OWID (totale opwek 2024).
Rekenregel: capture rate 2030 = capture rate 2025 + helling x (zonaandeel 2030 - zonaandeel 2025) in procentpunten, ondergrens 0,2.
  Zonaandeel = zon TWh / totale opwek (constant gehouden; groeiend verbruik maakt de daling kleiner).
  Opbrengst per MWh 2030 = capture rate 2030 x gemiddelde prijs 2025 (prijsniveau constant: dat isoleert het kannibalisatie-effect).
  Revenue at risk = opbrengst 2025 - opbrengst 2030 per MWh, en x 2030-productie = miljoen euro per jaar.
Bandbreedte: helling uit het 95%-interval van t56 (laag/hoog).
Waarschuwingen in de tabel: "Within observed range" (het 2030-aandeel ligt binnen de hoogste maandaandelen die de regressie zag;
anders extrapolatie), "Hits floor 0.2" en "Target already met" (NL en LT: doel 2030 al gehaald, dus 0 extra risico in deze rekenregel).
Belangrijkste beperking: batterijen en flexibele vraag maken de helling vlakker naarmate ze groeien; dit is een bovengrens bij
de flexibiliteit van 2019-2026.
Tabel (Engels): t70_revenue_at_risk. Gebruik: PYTHONPATH=src python3 -m eti.omzet_risico
"""
from pathlib import Path

import numpy as np
import pandas as pd

D = Path("tableau/data_en")
UIT = [Path("tableau/data"), Path("tableau/data_en")]
MEDIAAN = -0.020


def main():
    t1 = pd.read_csv(D / "t1_zonejaar.csv"); t1 = t1[t1.Jaar == 2025]
    t1["Country"] = t1.Zonenaam.str.replace(r" \(.*\)$", "", regex=True)
    cr = t1.groupby("Country")[["Capture rate zon", "Gemiddelde prijs"]].mean()
    k = pd.read_csv(D / "t13_kostencurve.csv").set_index("Country")
    h = pd.read_csv(D / "t56_hirth.csv"); h = h[h.Reliable]
    h["Country"] = h["Zone name"].str.replace(r" \(.*\)$", "", regex=True)
    hl = h.groupby("Country")[["Slope per percentage point", "Interval low", "Interval high", "Max solar share %"]].mean()
    o = pd.read_csv("data/raw/owid-energy-data.csv", usecols=["country", "year", "electricity_generation"]).dropna()
    gen = o.sort_values("year").groupby("country").electricity_generation.last()
    rij = []
    for land in k.index:
        if land not in cr.index or land not in gen.index or pd.isna(k.at[land, "Solar target TWh 2030"]):
            continue
        z25, z30, g = k.at[land, "Solar TWh 2025"], max(k.at[land, "Solar target TWh 2030"], k.at[land, "Solar TWh 2025"]), gen[land]
        s25, s30 = 100 * z25 / g, 100 * z30 / g
        bron = "own slope" if land in hl.index else "median slope"
        sl = hl.loc[land] if land in hl.index else pd.Series({"Slope per percentage point": MEDIAAN, "Interval low": -0.025, "Interval high": -0.015})
        c25, p = cr.at[land, "Capture rate zon"], cr.at[land, "Gemiddelde prijs"]
        uit = {"Country": land, "Solar share 2025 %": s25, "Solar share 2030 %": s30, "Slope source": bron,
               "Slope": sl["Slope per percentage point"], "Capture rate 2025": c25, "Average price 2025 EUR/MWh": p,
               "LCOE EUR/MWh": k.at[land, "LCOE"], "LCOE own model EUR/MWh": k.at[land, "LCOE own model"],
               "LCOE source": k.at[land, "LCOE source"], "Solar TWh 2030": z30}
        for lab, b in (("", sl["Slope per percentage point"]), (" (steep)", sl["Interval low"]), (" (flat)", sl["Interval high"])):
            c30 = max(0.2, c25 + b * (s30 - s25))
            uit[f"Capture rate 2030{lab}"] = c30
            uit[f"Revenue at risk EUR/MWh{lab}"] = (c25 - c30) * p
        uit["Solar revenue 2025 EUR/MWh"] = c25 * p
        uit["Solar revenue 2030 EUR/MWh"] = uit["Capture rate 2030"] * p
        uit["Revenue at risk M EUR per year"] = uit["Revenue at risk EUR/MWh"] * z30
        uit["Below LCOE in 2030"] = uit["Solar revenue 2030 EUR/MWh"] < uit["LCOE EUR/MWh"]
        # tweede grondslag: eigen model per land (eti.lcoe; ondergrens, elk land een eigen waarde), zie dashboard 32
        uit["Below own-model LCOE in 2030"] = uit["Solar revenue 2030 EUR/MWh"] < uit["LCOE own model EUR/MWh"]
        uit["Below LCOE in 2025"] = uit["Solar revenue 2025 EUR/MWh"] < uit["LCOE EUR/MWh"]
        uit["Hits floor 0.2"] = uit["Capture rate 2030"] <= 0.2001
        maxs = hl.at[land, "Max solar share %"] if land in hl.index else 30.0
        uit["Within observed range"] = s30 <= maxs          # buiten het waargenomen bereik is de lineaire helling een extrapolatie
        uit["Target already met"] = k.at[land, "Solar target TWh 2030"] <= z25
        uit["Target above 50% of today's generation"] = s30 > 50   # Denemarken: 24,6 TWh doel (Ember) op 33 TWh opwek; export telt niet mee
        rij.append(uit)
    t = pd.DataFrame(rij).sort_values("Revenue at risk EUR/MWh", ascending=False)
    for d in UIT:
        t.round(4).to_csv(d / "t70_revenue_at_risk.csv", index=False)
    return t


if __name__ == "__main__":
    t = main()
    pd.set_option("display.width", 250)
    print(t[["Country", "Solar share 2025 %", "Solar share 2030 %", "Slope source", "Capture rate 2025", "Capture rate 2030",
             "Revenue at risk EUR/MWh", "Revenue at risk EUR/MWh (steep)", "Revenue at risk EUR/MWh (flat)",
             "Revenue at risk M EUR per year", "Below LCOE in 2030"]].round(2).to_string())
