"""Figuren 'De wereld buiten Europa' (reports/wereld.png) en het Australische dagprofiel
(reports/australie_dagprofiel.png) en de verzadiging van opslag (reports/verzadiging.png), getekend uit de tabellen
in powerbi/data.

Gebruik:  PYTHONPATH=src python3 -m eti.fig_wereld [datamap] [uitvoerbestand]
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402

NAVY, TEAL, GEEL, KORAAL, GRIJS = "#14284B", "#2A9D8F", "#E9C46A", "#E76F51", "#8D99AE"
REGIOS = [("Australie (Zuid)", "Zuid-Australië", NAVY), ("Australie (Victoria)", "Victoria", TEAL),
          ("Australie (Queensland)", "Queensland", GEEL), ("Australie (NSW)", "Nieuw-Zuid-Wales", KORAAL)]
STUDIEREGIOS = [("Nederland", NAVY), ("Europa", TEAL), ("VS", GEEL), ("China", KORAAL), ("Rest van de wereld", GRIJS)]


def stijl():
    heeft_inter = any(f.name == "Inter" for f in font_manager.fontManager.ttflist)
    plt.rcParams.update({
        "font.family": "Inter" if heeft_inter else "DejaVu Sans", "font.size": 9, "axes.titlesize": 11,
        "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "legend.fontsize": 7.5, "savefig.dpi": 200, "savefig.bbox": "tight",
    })


def main(data="powerbi/data", uit="reports/wereld.png"):
    stijl()
    lees = lambda naam: pd.read_csv(os.path.join(data, naam))
    au = lees("fact_australie.csv")
    nl = lees("fact_land_jaar.csv").query("land == 'Nederland'").sort_values("jaar")
    flex = lees("fact_flex_land.csv").query("land == 'Nederland' and uren_opslag == 2").sort_values("jaar")
    vollast = lees("fact_instraling_wereld.csv").groupby("locatie").vollasturen_schatting.mean().sort_values()
    regio = lees("fact_studieregio_jaar.csv").query("Year >= 2010")

    fig, ax = plt.subplots(2, 2, figsize=(9.6, 7.2))
    a, b, c, d = ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]

    for sleutel, etiket, kleur in REGIOS:
        r = au[au.regio == sleutel].sort_values("jaar")
        a.plot(r.jaar, r.capture_zon_instraling, color=kleur, lw=1.6, label=etiket)
        b.plot(r.jaar, r.batterij_2u_realistisch_eur_per_mw / 1000, color=kleur, lw=1.6, label=etiket)
    a.plot(nl.jaar, nl.capture_zon, color="black", lw=2.2, ls="--", label="Nederland")
    b.plot(flex.jaar, flex.omzet_realistisch_per_mw / 1000, color="black", lw=2.2, ls="--", label="Nederland")
    a.set_title("a. Australië als voorland: capture rate zon")
    b.set_title("b. Batterij 2 uur (k€/MW/jaar)")
    b.set_ylim(0, 190)                                  # ruimte boven de lijnen voor de legenda
    for p in (a, b):
        p.set_xticks(range(2019, 2027))
    a.legend(loc="upper right")
    b.legend(loc="upper left", ncol=2)

    c.barh(list(vollast.index), vollast.values, color=[KORAAL if n == "Nederland" else GEEL for n in vollast.index])
    c.set_title("c. Vollasturen zon (NASA POWER, schatting)")
    c.tick_params(axis="y", labelsize=6.5)
    c.margins(y=0.01)

    for naam, kleur in STUDIEREGIOS:
        r = regio[regio.studieregio == naam].sort_values("Year")
        d.plot(r.Year, r.intensiteit_g_kwh, color=kleur, lw=1.6, label=naam)
    d.set_title("d. CO₂-intensiteit stroom per studieregio (g/kWh)")
    d.legend(loc="upper right")

    fig.tight_layout()
    os.makedirs(os.path.dirname(uit) or ".", exist_ok=True)
    fig.savefig(uit)
    plt.close(fig)
    return uit


def dagprofiel(data="powerbi/data", uit="reports/australie_dagprofiel.png"):
    """Australie, januari tot en met oktober per jaar: mediane dagomzet van de batterij en mediane avond- en middagprijs."""
    stijl()
    p = pd.read_csv(os.path.join(data, "fact_australie_dagprofiel.csv"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 3.7))
    for sleutel, etiket, kleur in REGIOS:
        r = p[p.regio == sleutel].sort_values("jaar")
        a.plot(r.jaar, r.mediaan_dagomzet_eur_per_mw, color=kleur, lw=1.6, label=etiket)
        b.plot(r.jaar, r.mediaan_avondprijs_eur_mwh, color=kleur, lw=1.6)
        b.plot(r.jaar, r.mediaan_middagprijs_eur_mwh, color=kleur, lw=1.6, ls="--")
    a.set_title("a. Mediane dagomzet batterij 2 uur (€ per MW per dag)")
    b.set_title("b. Mediane prijs: avond (lijn) en middag (streep), €/MWh")
    a.set_ylim(0, None)
    a.legend(loc="upper left")
    b.axhline(0, color=GRIJS, lw=0.8)
    for p_ in (a, b):
        p_.set_xticks(sorted(p.jaar.unique()))
    fig.text(0.01, -0.02, "Januari tot en met oktober van elk jaar, lokale dagen. Avond: 17-21 uur; middag: 10-15 uur. Bron: AEMO, eigen berekening.",
             fontsize=7, color=GRIJS)
    fig.tight_layout()
    os.makedirs(os.path.dirname(uit) or ".", exist_ok=True)
    fig.savefig(uit)
    plt.close(fig)
    return uit


def verzadiging(data="powerbi/data", uit="reports/verzadiging.png"):
    """Dagmarktomzet van een batterij van 2 uur per MW: links per jaar, rechts dezelfde periode (1 januari t/m 24 juni)."""
    stijl()
    lees = lambda naam: pd.read_csv(os.path.join(data, naam))
    w, half = lees("fact_wereld_markten.csv"), lees("fact_vs_halfjaar.csv")
    au = lees("fact_australie.csv")
    au = au[au.regio != "Australie (Tasmanie)"].groupby("jaar").batterij_2u_realistisch_eur_per_mw.mean()
    nl = lees("fact_flex_land.csv").query("land == 'Nederland' and uren_opslag == 2").set_index("jaar").omzet_realistisch_per_mw
    kol = "batterij_2u_realistisch_eur_per_mw"
    reeks = lambda markt, t=w: t[t.markt == markt].set_index("jaar")[kol]
    ca, tx = reeks("VS Californie (CAISO)"), reeks("VS Texas (ERCOT)")

    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 3.5))
    for naam, s, kleur in (("Nederland", nl, NAVY), ("Australië (vasteland)", au, TEAL), ("Californië", ca, KORAAL)):
        a.plot(s.index, s.values / 1000, marker="o", ms=3.5, lw=1.8, color=kleur, label=naam)
    heel = tx[tx.index <= 2024]
    a.plot(heel.index, heel.values / 1000, marker="o", ms=3.5, lw=1.8, color=GEEL, label="Texas (2025 t/m juni)")
    a.plot([2024, 2025], [tx[2024] / 1000, tx[2025] / 1000], ls=":", lw=1.8, color=GEEL)
    a.plot([2025], [tx[2025] / 1000], marker="o", ms=4.5, mfc="white", color=GEEL)
    a.set_title("a. Dagmarktomzet batterij per MW (k€ per jaar)")
    a.set_ylim(0, None); a.legend(loc="upper left"); a.grid(axis="y", lw=0.4, alpha=0.5)

    jaren = list(range(2020, 2027))
    for i, (naam, markt, kleur) in enumerate((("Texas", "VS Texas (ERCOT)", GEEL), ("Californië", "VS Californie (CAISO)", KORAAL))):
        s = reeks(markt, half).reindex(jaren)
        b.bar([j + (i - 0.5) * 0.38 for j in jaren], s.values / 1000, width=0.36, color=kleur, label=naam)
    b.set_title("b. Zelfde periode: 1 januari t/m 24 juni (k€ per jaar)")
    b.set_xticks(jaren); b.legend(loc="upper left"); b.grid(axis="y", lw=0.4, alpha=0.5)
    fig.tight_layout()
    fig.savefig(uit)
    plt.close(fig)
    return uit


if __name__ == "__main__":
    print(main(*sys.argv[1:3]))
    print(dagprofiel(*([sys.argv[1]] if len(sys.argv) > 1 else [])))
    print(verzadiging(*([sys.argv[1]] if len(sys.argv) > 1 else [])))
