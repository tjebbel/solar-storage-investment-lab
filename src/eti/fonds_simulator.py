"""Dashboard 27 "Climate fund simulator": rendement tegen vermeden CO2 voor een fonds dat in zon en batterijen in Europa belegt.

Doel: laten zien dat rendement en impact in één beslissing passen, en hoe onzeker beide zijn. Geen beleggingsadvies: een model
met openbare invoer en expliciete aannames, om de afweging zichtbaar te maken.

Invoer (alles 2025):
  zon       t13_kostencurve: capture-prijs zon, LCOE (noord 67,39 / zuid 51,09 EUR/MWh), gemiddelde emissiefactor per land
  batterij  t55_battery_arbitrage: opbrengst 2-uursbatterij (perfecte voorkennis) per zone
  CO2       t64_avoided_per_mwh: marginale factor (bandbreedte) per zone, alleen betrouwbare zones

Projectmodel zon (per MWh jaaropbrengst, consistent met de LCOE): looptijd 25 jaar, WACC 5%, 85% van de LCOE is kapitaal.
  capex = 0,85 x LCOE / CRF(5%, 25); opex = 0,15 x LCOE per MWh; opbrengst jaar t = capture-prijs x prijsniveau x (1 - g)^t.
Projectmodel batterij (per MW): capex 2 x 204 = 408 kEUR (BNEF 2025: turnkey Europa 177 USD/kWh = ~157 EUR/kWh, plus 30% voor
  netaansluiting en bouw; AANNAME), opex 2% van capex, looptijd 15 jaar, 2% degradatie per jaar; opbrengst jaar 1 = t55 x 0,86
  (realistisch tegen perfecte voorkennis: NL 61k tegen 71k) x niveau, daarna -d per jaar (verzadiging).
Onzekerheid (Monte Carlo, 1000 trekkingen, gemeenschappelijk voor alle landen in een trekking):
  prijsniveau lognormaal sigma 0,20; zonwaardedaling g uniform 0-3% per jaar (Hirth: -0,02 capture rate per procentpunt zon);
  LCOE x normaal(1; 0,10); batterijopbrengst x lognormaal sigma 0,25; verzadiging d uniform 0-8% per jaar; batterij-capex x uniform 0,8-1,2.
Belangrijke beperkingen (lees ze bij elke uitkomst):
  - Batterijopbrengst is alleen day-ahead-arbitrage. In Duitsland komt tot 67% van de inkomsten van een 2-uursbatterij uit
    reservemarkten (aFRR, FCR; Capstone, nov 2025). De batterij-IRR is dus een ondergrens, vooral in het westen.
  - Portefeuille-IRR = gewogen gemiddelde van de project-IRR's, geen IRR van samengevoegde kasstromen (benadering).
  - Het fonds laat waarde aangroeien tegen de project-IRR en keert pas bij verkoop uit; echte infrafondsen keren jaarlijks uit.
Fonds: 100 M EUR, 4 jaar investeren, 6 jaar aanhouden, 2% beheervergoeding, 20% carry boven 8% (fonds(); variant op eti.lenses).

Tabellen (Engels, tableau/data en tableau/data_en):
  t65_fund_assets      per land/zone en techniek: basisgeval, P10/P50/P90 project-IRR, CO2 per M EUR per jaar (gemiddeld, marginaal binnenlands en fossiele reactie; jaar 1)
  t66_fund_draws       trekking x bouwsteen (4): gemiddelde project-IRR en CO2 per M EUR; voor schuifjes in Tableau
  t67_fund_portfolios  vijf voorbeeldportefeuilles: P10/P50/P90 project-IRR, netto fonds-IRR (P50), TVPI, CO2 per M EUR
Gebruik: PYTHONPATH=src python3 -m eti.fonds_simulator
"""
from pathlib import Path

import numpy as np
import pandas as pd

from eti import finance

D = Path("tableau/data_en")
UIT = [Path("tableau/data"), Path("tableau/data_en")]
N, ZAAD = 1000, 2026
WACC, LOOPTIJD, KAPITAAL = 0.05, 25, 0.85
BAT_CAPEX, BAT_OPEX, BAT_LOOPTIJD, BAT_DEGR, REALISTISCH = 408_000, 0.02, 15, 0.02, 0.86
RESERVE = 1.5   # illustratieve opslag voor aFRR/FCR in de gevoeligheidsrij van t67
KLASSEN = {
    "Solar South": ("solar", ["Italy", "Spain", "Portugal", "Greece", "Croatia", "Bulgaria", "Romania", "Slovenia"]),
    "Solar North": ("solar", ["Germany", "Netherlands", "Belgium", "Poland", "Denmark", "Austria", "Czechia", "Hungary"]),
    "Battery East": ("battery", ["Estonia", "Lithuania", "Latvia", "Bulgaria", "Romania", "Greece", "Hungary"]),
    "Battery West": ("battery", ["Germany", "Netherlands", "Belgium", "France", "Austria"]),
}
PORTEFEUILLES = {
    "South and east": {"Solar South": 0.5, "Battery East": 0.5},
    "North and west": {"Solar North": 0.6, "Battery West": 0.4},
    "Balanced": {"Solar South": 0.25, "Solar North": 0.25, "Battery East": 0.25, "Battery West": 0.25},
    "Solar only": {"Solar South": 0.5, "Solar North": 0.5},
    "Batteries only": {"Battery East": 0.5, "Battery West": 0.5},
}


def fonds(project_irr, commitment=100, draw_years=4, hold=6, fee=0.02, carry=0.20, hurdle=0.08, life=10):
    """Gesloten fonds zoals eti.lenses.fund_cashflows, maar de carry wordt afgetrokken in het jaar van de laatste uitkering
    (in lenses valt die in jaar 10 zonder uitkering, waardoor bij hoge rendementen geen IRR te vinden is)."""
    inn, uit = [0.0] * (life + 1), [0.0] * (life + 1)
    for y in range(draw_years):
        inn[y] += commitment / draw_years
        uit[min(y + hold, life)] += commitment / draw_years * (1 + project_irr) ** hold
    fees = [commitment * fee if y < life else 0.0 for y in range(life + 1)]
    lp = [uit[y] - inn[y] - fees[y] for y in range(life + 1)]
    ingelegd, uitgekeerd = sum(inn) + sum(fees), sum(uit)
    pref = sum((inn[y] + fees[y]) * (1 + hurdle) ** (life - y) for y in range(life + 1))
    c = carry * (uitgekeerd - ingelegd) if uitgekeerd > pref else 0.0
    laatste = max(y for y in range(life + 1) if uit[y] > 0)
    lp[laatste] -= c
    return {"net_irr": finance.irr_safe(lp), "tvpi": (uitgekeerd - c) / ingelegd}


def crf(w, n):
    return w / (1 - (1 + w) ** -n)


def irr_zon(prijs, lcoe, g):
    capex = KAPITAAL * lcoe / crf(WACC, LOOPTIJD)
    cf = [-capex] + [prijs * (1 - g) ** t - (1 - KAPITAAL) * lcoe for t in range(1, LOOPTIJD + 1)]
    return finance.irr_safe(cf)


def irr_batterij(opbrengst, d, capex_x):
    capex = BAT_CAPEX * capex_x
    cf = [-capex] + [opbrengst * (1 - d) ** (t - 1) * (1 - BAT_DEGR) ** (t - 1) - BAT_OPEX * capex for t in range(1, BAT_LOOPTIJD + 1)]
    return finance.irr_safe(cf)


def invoer():
    k = pd.read_csv(D / "t13_kostencurve.csv").set_index("Country")
    b = pd.read_csv(D / "t55_battery_arbitrage.csv"); b = b[b.Year == 2025]
    m = pd.read_csv(D / "t64_avoided_per_mwh.csv"); m = m[(m.Year == 2025) & m.Reliable]
    mz = m.groupby("Country")[["Marginal factor, solar hours, domestic t/MWh", "Marginal factor, solar hours, fossil response t/MWh"]].mean()
    mb = m.groupby("Country")[["Battery net CO2 t per MW per year, domestic", "Battery net CO2 t per MW per year, fossil response"]].mean()
    b["Country"] = b["Zone name"].str.replace(r" \(.*\)$", "", regex=True)
    bo = b.groupby("Country")["Revenue per MW"].mean()
    rijen = []
    for klasse, (tech, landen) in KLASSEN.items():
        for land in landen:
            r = {"Building block": klasse, "Technology": tech, "Country": land}
            if tech == "solar":
                if land not in k.index:
                    continue
                r |= {"Price EUR/MWh": k.at[land, "Solar capture price EUR/MWh"], "LCOE EUR/MWh": k.at[land, "LCOE"],
                      "Average factor t/MWh": k.at[land, "Average emission factor t/MWh"],
                      "Marginal domestic t/MWh": mz.get("Marginal factor, solar hours, domestic t/MWh", {}).get(land, np.nan),
                      "Marginal fossil response t/MWh": mz.get("Marginal factor, solar hours, fossil response t/MWh", {}).get(land, np.nan)}
            else:
                if land not in bo.index:
                    continue
                r |= {"Revenue per MW 2025 (perfect foresight)": bo[land],
                      "CO2 domestic t per MW per year": mb.get("Battery net CO2 t per MW per year, domestic", {}).get(land, np.nan),
                      "CO2 fossil response t per MW per year": mb.get("Battery net CO2 t per MW per year, fossil response", {}).get(land, np.nan)}
            rijen.append(r)
    return pd.DataFrame(rijen)


def co2_per_meur(r, lcoe_x=1.0, capex_x=1.0):
    """Vermeden ton CO2 per jaar per miljoen euro (jaar 1, net van vandaag): gemiddeld, marginaal binnenlands, marginaal fossiele reactie.
    Let op: t27 (dashboard 14) rekent met het gemiddelde over de looptijd (schoner net), dus lager."""
    if r.Technology == "solar":
        mwh = 1e6 / (KAPITAAL * r["LCOE EUR/MWh"] * lcoe_x / crf(WACC, LOOPTIJD))
        return mwh * r["Average factor t/MWh"], mwh * r["Marginal domestic t/MWh"], mwh * r["Marginal fossil response t/MWh"]
    mw = 1e6 / (BAT_CAPEX * capex_x)
    return np.nan, mw * r["CO2 domestic t per MW per year"], mw * r["CO2 fossil response t per MW per year"]


def simuleer(a, n=N, zaad=ZAAD, reserve=1.0):
    rng = np.random.default_rng(zaad)
    s = rng.lognormal(0, 0.20, n); g = rng.uniform(0, 0.03, n); lx = np.clip(rng.normal(1, 0.10, n), 0.7, 1.3)
    bx = rng.lognormal(0, 0.25, n); d = rng.uniform(0, 0.08, n); cx = rng.uniform(0.8, 1.2, n)
    uit = np.full((len(a), n), np.nan)
    for i, r in a.reset_index(drop=True).iterrows():
        for j in range(n):
            if r.Technology == "solar":
                uit[i, j] = irr_zon(r["Price EUR/MWh"] * s[j], r["LCOE EUR/MWh"] * lx[j], g[j])
            else:
                uit[i, j] = irr_batterij(r["Revenue per MW 2025 (perfect foresight)"] * REALISTISCH * reserve * bx[j], d[j], cx[j])
    return uit, dict(s=s, g=g, lx=lx, bx=bx, d=d, cx=cx)


def main():
    a = invoer()
    irr, trek = simuleer(a)
    a["Base case IRR"] = [irr_zon(r["Price EUR/MWh"], r["LCOE EUR/MWh"], 0.015) if r.Technology == "solar"
                          else irr_batterij(r["Revenue per MW 2025 (perfect foresight)"] * REALISTISCH, 0.04, 1.0) for _, r in a.iterrows()]
    a["IRR P10"], a["IRR P50"], a["IRR P90"] = (np.nanpercentile(irr, q, axis=1) for q in (10, 50, 90))
    a["Share of draws with IRR above 8%"] = np.mean(np.nan_to_num(irr, nan=-1) > 0.08, axis=1)
    a["Share of draws without payback"] = np.mean(np.isnan(irr), axis=1)
    c = np.array([co2_per_meur(r) for _, r in a.iterrows()])
    a["CO2 per M EUR per year, average"], a["CO2 per M EUR per year, marginal domestic"], a["CO2 per M EUR per year, marginal fossil response"] = c.T
    # trekkingen per bouwsteen (gelijk gewogen gemiddelde van de landen). Verdient een project zijn investering nooit terug
    # (geen IRR; 0,2% van de trekkingen, bijna alleen batterijen in het westen), dan telt het als -30%.
    rijen = []
    for klasse in KLASSEN:
        idx = np.where(a["Building block"] == klasse)[0]
        sub = np.nan_to_num(irr[idx], nan=-0.30)
        co = a.iloc[idx][["CO2 per M EUR per year, average", "CO2 per M EUR per year, marginal domestic", "CO2 per M EUR per year, marginal fossil response"]].mean()
        for j in range(irr.shape[1]):
            rijen.append({"Draw": j + 1, "Building block": klasse, "Project IRR": sub[:, j].mean(),
                          "CO2 per M EUR per year, average": co.iloc[0], "CO2 per M EUR per year, marginal domestic": co.iloc[1],
                          "CO2 per M EUR per year, marginal fossil response": co.iloc[2],
                          "Price level": trek["s"][j], "Solar value decline per year": trek["g"][j], "Battery saturation per year": trek["d"][j]})
    t66 = pd.DataFrame(rijen)
    w = t66.pivot(index="Draw", columns="Building block", values="Project IRR")
    co = t66.groupby("Building block")[["CO2 per M EUR per year, average", "CO2 per M EUR per year, marginal domestic",
                                        "CO2 per M EUR per year, marginal fossil response"]].first()
    port = []
    for naam, gew in PORTEFEUILLES.items():
        r = sum(w[k] * v for k, v in gew.items())
        p50 = float(np.percentile(r, 50))
        f = fonds(p50) if p50 > -0.5 else {"net_irr": np.nan, "tvpi": np.nan}
        cm = {c: sum(co.at[k, c] * v for k, v in gew.items() if not np.isnan(co.at[k, c])) for c in co.columns}
        port.append({"Portfolio": naam, "Weights": ", ".join(f"{k} {v:.0%}" for k, v in gew.items()),
                     "Project IRR P10": np.percentile(r, 10), "Project IRR P50": p50, "Project IRR P90": np.percentile(r, 90),
                     "Share of draws above 8%": float((r > 0.08).mean()),
                     "Fund net IRR (P50)": f["net_irr"], "Fund TVPI (P50)": f["tvpi"],
                     "CO2 per M EUR per year, marginal domestic": cm["CO2 per M EUR per year, marginal domestic"],
                     "CO2 per M EUR per year, marginal fossil response": cm["CO2 per M EUR per year, marginal fossil response"]})
    # gevoeligheid: batterijen met reservemarkten (illustratief x1,5 op de arbitrage-opbrengst; aanname, geen meting)
    b = a[a.Technology == "battery"].reset_index(drop=True)
    irr_r, _ = simuleer(b, reserve=RESERVE)
    r = np.nan_to_num(irr_r, nan=-0.30).mean(axis=0)
    p50 = float(np.percentile(r, 50)); fr = fonds(p50)
    bo = [x for x in port if x["Portfolio"] == "Batteries only"][0]
    port.append({"Portfolio": f"Batteries only, with reserve markets (x{RESERVE})", "Weights": "Battery East 50%, Battery West 50%",
                 "Project IRR P10": np.percentile(r, 10), "Project IRR P50": p50, "Project IRR P90": np.percentile(r, 90),
                 "Share of draws above 8%": float((r > 0.08).mean()), "Fund net IRR (P50)": fr["net_irr"], "Fund TVPI (P50)": fr["tvpi"],
                 "CO2 per M EUR per year, marginal domestic": bo["CO2 per M EUR per year, marginal domestic"],
                 "CO2 per M EUR per year, marginal fossil response": bo["CO2 per M EUR per year, marginal fossil response"]})
    t67 = pd.DataFrame(port)
    for uit in UIT:
        uit.mkdir(parents=True, exist_ok=True)
        a.round(4).to_csv(uit / "t65_fund_assets.csv", index=False)
        t66.round(4).to_csv(uit / "t66_fund_draws.csv", index=False)
        t67.round(4).to_csv(uit / "t67_fund_portfolios.csv", index=False)
    return a, t66, t67


if __name__ == "__main__":
    a, t66, t67 = main()
    pd.set_option("display.width", 250)
    print(a[["Building block", "Country", "Base case IRR", "IRR P10", "IRR P50", "IRR P90", "CO2 per M EUR per year, average",
             "CO2 per M EUR per year, marginal domestic", "CO2 per M EUR per year, marginal fossil response"]].round(3).to_string())
    print(t67.round(3).to_string())
