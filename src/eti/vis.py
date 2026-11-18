"""Grafieken bij de bevindingen (matplotlib en seaborn), in een stijl.

Elke functie maakt een figuur met een titel die de bevinding zegt, assen met eenheden en zo weinig inkt als kan.
Kleur: blauw en oranje voor reeksen, grijs voor context, blauw tegenover rood rond een neutraal midden voor
boven of onder een grens. Het palet is getoetst op kleurenblindheid (zie reports/analyse/03_visualisatie.md).
Twee reeksen of meer krijgen een legenda en een label bij de lijn of staaf; er is nergens een tweede y-as.

Uitvoer: tien PNG's en bijschriften.txt in reports/analyse/fig.
Gebruik:  PYTHONPATH=src python3 -m eti.vis [datamap] [uitvoermap]     (eerst eti.da, eti.sa en eti.prognose draaien)
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

DATA, UIT = "powerbi/data", "reports/analyse/fig"
K = {"blauw": "#2a78d6", "oranje": "#eb6834", "aqua": "#1baf7a", "geel": "#eda100", "rood": "#e34948", "grijs": "#c3c2b7",
     "lichtblauw": "#b7d3f6", "inkt": "#0b0b0b", "inkt2": "#52514e", "gedempt": "#898781", "raster": "#e1e0d9", "vlak": "#fcfcfb",
     "midden": "#f0efec"}
ROND_MIDDEN = LinearSegmentedColormap.from_list("blauw_rood", [K["blauw"], K["midden"], K["rood"]])
MAAND = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]


def stijl():
    """Een stijl voor alle figuren: rustig raster, geen kader, tekst in inktkleuren."""
    sns.set_theme(style="white", rc={
        "figure.facecolor": K["vlak"], "axes.facecolor": K["vlak"], "savefig.facecolor": K["vlak"], "axes.edgecolor": K["grijs"],
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y", "grid.color": K["raster"],
        "grid.linewidth": 0.8, "axes.axisbelow": True, "axes.labelcolor": K["inkt2"], "axes.labelsize": 10, "xtick.color": K["gedempt"],
        "ytick.color": K["gedempt"], "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "text.color": K["inkt"], "lines.linewidth": 2,
        "lines.solid_capstyle": "round", "legend.frameon": False, "legend.fontsize": 9.5, "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"], "savefig.dpi": 200, "savefig.bbox": "tight"})


def kop(fig, titel, onder, bron):
    """Titel (de bevinding), ondertitel (wat er staat, met eenheid) en bronregel, op vaste afstand van de assen."""
    fig.canvas.draw()
    hoogte = fig.get_figheight()
    boven = max(ax.get_position().y1 for ax in fig.axes)
    onderkant = min(ax.get_tightbbox(fig.canvas.get_renderer()).y0 for ax in fig.axes) / (hoogte * fig.dpi)
    fig.text(0.0, boven + 0.50 / hoogte, titel, ha="left", va="bottom", fontsize=13.5, fontweight="bold", color=K["inkt"])
    fig.text(0.0, boven + 0.22 / hoogte, onder, ha="left", va="bottom", fontsize=10, color=K["inkt2"])
    fig.text(0.0, onderkant - 0.12 / hoogte, bron, ha="left", va="top", fontsize=8.5, color=K["gedempt"])


def bewaar(fig, uit, naam, bijschrift, lijst):
    os.makedirs(uit, exist_ok=True)
    fig.savefig(os.path.join(uit, naam))
    plt.close(fig)
    lijst.append((naam, bijschrift))


def punt(ax, x, y, kleur, groot=7, open_=False):
    """Marker met een ring in de achtergrondkleur, zodat overlappende punten te onderscheiden blijven."""
    ax.plot(x, y, "o", ms=groot, color=K["vlak"] if open_ else kleur, mec=kleur if open_ else K["vlak"], mew=1.6, zorder=4)


def eur(x):
    return f"{x:,.0f}".replace(",", ".")


# ---------------------------------------------------------------------------------------------------- figuren
def capture_daling(data, uit, lijst):
    p = pd.read_csv(os.path.join(data, "fact_zonejaar_DA.csv"))
    w = p[p.capture_zon.between(0, 2)].pivot(index="biedzone", columns="jaar", values="capture_zon")[[2019, 2025]].dropna().sort_values(2025)
    fig, ax = plt.subplots(figsize=(7.2, 9.2))
    for i, (zone, r) in enumerate(w.iterrows()):
        nl = zone == "NL"
        ax.plot([r[2019], r[2025]], [i, i], color=K["oranje"] if nl else K["grijs"], lw=2.4 if nl else 1.4, zorder=2)
        punt(ax, r[2019], i, K["grijs"] if not nl else K["oranje"], open_=True)
        punt(ax, r[2025], i, K["oranje"] if nl else K["blauw"])
    ax.set_yticks(range(len(w)))
    ax.set_yticklabels(w.index, fontsize=8.5)
    ax.get_yticklabels()[list(w.index).index("NL")].set_fontweight("bold")
    ax.axvline(1.0, color=K["gedempt"], lw=0.8)
    ax.text(1.0, len(w) - 0.2, " jaargemiddelde prijs", fontsize=8.5, color=K["gedempt"], va="bottom")
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.set_xlabel("capture rate van zon (prijs die zon ontvangt, gedeeld door de gemiddelde prijs)")
    ax.set_ylim(-0.8, len(w) + 0.6)
    ax.plot([], [], "o", ms=7, color=K["vlak"], mec=K["grijs"], mew=1.6, label="2019")
    ax.plot([], [], "o", ms=7, color=K["blauw"], mec=K["vlak"], mew=1.6, label="2025")
    ax.legend(loc="lower right")
    daling = (w[2025] < w[2019]).sum()
    kop(fig, f"In alle {daling} zones is zon minder waard dan in 2019" if daling == len(w) else f"In {daling} van de {len(w)} zones is zon minder waard dan in 2019",
        f"Capture rate per biedzone; gemiddelde daling {abs((w[2025] - w[2019]).mean()):.2f}. Nederland in oranje.".replace(".", ",", 1),
        "Bron: Energy-Charts, Open-Meteo; eigen berekening (fact_zonejaar_DA).")
    bewaar(fig, uit, "01_capture_daling.png", f"Deze grafiek laat zien dat de capture rate van zon tussen 2019 en 2025 in alle {len(w)} biedzones is gedaald, "
           f"gemiddeld met {abs((w[2025] - w[2019]).mean()):.2f}. De belangrijkste conclusie is: reken geen enkel zonproject meer door met de marktwaarde van voor 2023.", lijst)


def jaar_tegen_land(data, uit, lijst):
    c = pd.read_csv(os.path.join(data, "fact_correlatie_DA.csv")).query("soort == 'eta2'")
    namen = {"dagspreiding": "Dagspreiding", "batterij_per_mw": "Batterij-omzet", "negatieve_uren": "Negatieve uren", "capture_zon": "Capture rate zon"}
    w = c[c.var1.isin(["jaar", "land"])].pivot(index="var2", columns="var1", values="waarde").loc[list(namen)] * 100
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    y = np.arange(len(w))
    for k, (kol, kleur, naam) in enumerate((("jaar", K["blauw"], "kalenderjaar"), ("land", K["oranje"], "land"))):
        ax.barh(y + (k - 0.5) * 0.34, w[kol], height=0.3, color=kleur, label=naam, edgecolor=K["vlak"], linewidth=1.2)
        for yi, v in zip(y, w[kol]):
            ax.text(v + 1, yi + (k - 0.5) * 0.34, f"{v:.0f}%", va="center", fontsize=9.5, color=K["inkt2"])
    ax.set_yticks(y); ax.set_yticklabels([namen[i] for i in w.index]); ax.invert_yaxis()
    ax.set_xlim(0, 75); ax.set_xlabel("deel van de variatie tussen zone-jaren dat verklaard wordt (%)")
    ax.grid(axis="x"); ax.grid(axis="y", visible=False); ax.legend(loc="lower right")
    kop(fig, "Het jaar verklaart meer dan het land", "37 biedzones, 2019 tot en met 2025. Spreiden over landen spreidt minder dan het lijkt.",
        "Bron: eigen berekening (fact_correlatie_DA, eta-kwadraat).")
    bewaar(fig, uit, "02_jaar_tegen_land.png", f"Deze grafiek laat zien dat het kalenderjaar {w.jaar.iloc[0]:.0f}% van de variatie in dagspreiding verklaart en het land "
           f"{w.land.iloc[0]:.0f}%. De belangrijkste conclusie is: spreid een portefeuille over techniek en contractvorm, niet alleen over landen.", lijst)


def uurprofiel(data, uit, lijst):
    t = pd.read_csv(os.path.join(data, "fact_tijd_DA.csv")).query("reeks == 'uurprofiel'")
    a, b = (t[t.dimensie == f"uur {j}"].set_index(t[t.dimensie == f"uur {j}"].sleutel.astype(int)).waarde for j in (2019, 2025))
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.plot(a.index, a.values, color=K["grijs"], label="2019")
    ax.plot(b.index, b.values, color=K["blauw"], label="2025")
    ax.axhline(1, color=K["gedempt"], lw=0.8)
    for reeks, kleur, naam in ((a, K["gedempt"], "2019"), (b, K["blauw"], "2025")):
        ax.text(23.3, reeks.iloc[-1], naam, color=K["inkt2"], va="center", fontsize=10)
        punt(ax, 23, reeks.iloc[-1], kleur if naam == "2025" else K["grijs"])
    dal, piek = int(b.idxmin()), int(b.idxmax())
    ax.annotate(f"{dal} uur: {b[dal]:.2f}".replace(".", ","), (dal, b[dal]), (dal, b[dal] - 0.2), ha="center", fontsize=9.5, color=K["inkt2"],
                arrowprops={"arrowstyle": "-", "color": K["gedempt"], "lw": 0.8})
    ax.annotate(f"{piek} uur: {b[piek]:.2f}".replace(".", ","), (piek, b[piek]), (piek - 3.2, b[piek] + 0.1), ha="center", fontsize=9.5, color=K["inkt2"],
                arrowprops={"arrowstyle": "-", "color": K["gedempt"], "lw": 0.8})
    ax.set_xticks(range(0, 24, 3)); ax.set_xlim(0, 25.5); ax.set_ylim(0.2, 1.75)
    ax.set_xlabel("uur van de dag (lokale tijd)"); ax.set_ylabel("prijs (1 = gemiddelde van het jaar)")
    ax.legend(loc="upper left", ncol=2)
    kop(fig, "De middagprijs is gehalveerd, de avondpiek gegroeid", f"Nederlandse dagmarktprijs per uur ten opzichte van het jaargemiddelde. Om {dal} uur was dat {a[dal]:.2f} in 2019.".replace("0.", "0,"),
        "Bron: Energy-Charts; eigen berekening (fact_tijd_DA).")
    bewaar(fig, uit, "03_uurprofiel.png", f"Deze grafiek laat zien dat de prijs om {dal} uur in 2025 op {b[dal]:.0%} van het jaargemiddelde lag, tegen {a[dal]:.0%} in 2019, "
           f"en om {piek} uur op {b[piek]:.0%}. De belangrijkste conclusie is: de waarde zit in verschuiven van middag naar avond, niet in meer middagproductie.", lijst)


def rendement(data, uit, lijst):
    t = pd.read_csv(os.path.join(data, "fact_toetsen_SA.csv"))
    t = t[t.toets.str.contains("IRR boven kapitaalkosten")]
    t["techniek"] = t.toets.str.split(":").str[0].replace({"Batterij 2 uur, dagmarkt": "Batterij (2 uur, dagmarkt)"})
    t["soort"] = np.where(t.toets.str.contains("gewone"), "gewoon", "schok")
    w = t.pivot(index="techniek", columns="soort", values="aandeel_boven_drempel").loc[["Wind", "Zon", "Batterij (2 uur, dagmarkt)"]] * 100
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    y = np.arange(len(w))
    for k, (kol, kleur, naam) in enumerate((("gewoon", K["blauw"], "gewone jaren (2023-2025)"), ("schok", K["oranje"], "schokjaren (2021, 2022, 2026)"))):
        ax.barh(y + (k - 0.5) * 0.34, w[kol], height=0.3, color=kleur, label=naam, edgecolor=K["vlak"], linewidth=1.2)
        for yi, v in zip(y, w[kol]):
            ax.text(v + 1.5, yi + (k - 0.5) * 0.34, f"{v:.0f}%", va="center", fontsize=9.5, color=K["inkt2"])
    ax.axvline(50, color=K["gedempt"], lw=0.8); ax.text(50, -0.62, "de helft van de zones", ha="center", fontsize=8.5, color=K["gedempt"])
    ax.set_yticks(y); ax.set_yticklabels(w.index); ax.invert_yaxis(); ax.set_xlim(0, 105); ax.set_ylim(len(w) - 0.45, -0.8)
    ax.set_xlabel("aandeel zones met een IRR boven de kapitaalkosten van 5% (%)")
    ax.grid(axis="x"); ax.grid(axis="y", visible=False); ax.legend(loc="lower right")
    kop(fig, "Alleen wind verdient in gewone jaren zijn kapitaalkosten", "Rendement zonder contract; 36 of 37 biedzones per techniek. In schokjaren keert het beeld om voor zon.",
        "Bron: eigen berekening (fact_toetsen_SA).")
    bewaar(fig, uit, "04_rendement.png", f"Deze grafiek laat zien dat wind in {w.gewoon.iloc[0]:.0f}% van de zones meer oplevert dan de kapitaalkosten, zon in {w.gewoon.iloc[1]:.0f}% "
           f"en een batterij op dagmarkthandel in {w.gewoon.iloc[2]:.0f}%. De belangrijkste conclusie is: zon vraagt een contract en opslag vraagt meer inkomstenbronnen.", lijst)


def bijsturen(data, uit, lijst):
    a = pd.read_csv(os.path.join(data, "fact_abtest_SA.csv")).query("onderdeel == 'gepaard per jaar'")
    j, v, lo, hi = a.segment.astype(int).values, a.verschil.values * 0.365, a.ci_laag.values * 0.365, a.ci_hoog.values * 0.365
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.axhline(0, color=K["gedempt"], lw=0.8)
    ax.vlines(j, lo, hi, color=K["blauw"], lw=2)
    for x, y in zip(j, v):
        punt(ax, x, y, K["blauw"], groot=9)
        ax.text(x + 0.08, y, f"{y:+.0f}", va="center", fontsize=10, color=K["inkt2"])
    ax.set_xticks(j); ax.set_xticklabels([str(x) if x < j.max() else f"{x}\n(tot 15 nov)" for x in j]); ax.set_xlim(j.min() - 0.5, j.max() + 0.6)
    ax.set_ylabel("extra omzet (duizend euro per MW per jaar)")
    kop(fig, f"Bijsturen op onbalans: van +{v[0]:.0f}.000 euro per MW in {j[0]} naar vrijwel niets in {j[-1]}",
        "Verschil tussen bijsturen en alleen het dagmarktplan, op dezelfde dagen. Streep: 95%-interval.", "Bron: ENTSO-E, Energy-Charts; eigen simulatie (fact_abtest_SA).")
    bewaar(fig, uit, "05_bijsturen.png", f"Deze grafiek laat zien dat bijsturen op de onbalansprijs in {j[0]} {v[0]:.0f} duizend euro per MW extra opleverde en in {j[-1]} nog {v[-1]:.0f} duizend, "
           "met een interval dat nul omvat. De belangrijkste conclusie is: neem deze inkomsten niet op in de basiscase en blijf meten.", lijst)


def prijs_prognose(data, uit, lijst):
    d = pd.read_csv(os.path.join(data, "fact_decompositie_SA.csv")).query("reeks == 'prijs'")
    f = pd.read_csv(os.path.join(data, "fact_prognose_SA.csv")).query("reeks == 'prijs' and soort == 'prognose'")
    jaar = pd.read_csv(os.path.join(data, "fact_prognose_jaar_SA.csv")).query("reeks == 'prijs' and jaar == 2027").iloc[0]
    x0, x1 = pd.to_datetime(d.periode), pd.to_datetime(f.periode)
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.fill_between(x1, f.laag95, f.hoog95, color=K["lichtblauw"], alpha=0.45, lw=0, label="95%-interval")
    ax.fill_between(x1, f.laag80, f.hoog80, color=K["lichtblauw"], lw=0, label="80%-interval")
    ax.plot(x0, d.waarde, color=K["inkt2"], lw=1.6, label="gemeten")
    ax.plot([x0.iloc[-1]] + list(x1), [d.waarde.iloc[-1]] + list(f.waarde), color=K["blauw"], label="prognose")
    normaal = d[pd.to_datetime(d.periode).dt.year.isin([2023, 2024, 2025])].waarde.mean()
    ax.axhline(normaal, color=K["gedempt"], lw=0.8)
    ax.text(x0.iloc[0], normaal + 6, f"gemiddelde 2023-2025: {normaal:.0f}", fontsize=8.5, color=K["gedempt"])
    piek = d.loc[d.waarde.idxmax()]
    ax.annotate(f"augustus 2022: {piek.waarde:.0f}", (pd.to_datetime(piek.periode), piek.waarde), (pd.to_datetime("2021-12-01"), piek.waarde - 8),
                fontsize=9.5, color=K["inkt2"], va="center", ha="right", arrowprops={"arrowstyle": "-", "color": K["gedempt"], "lw": 0.8})
    ax.set_ylabel("euro per MWh (maandgemiddelde)"); ax.set_ylim(0, None)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86))
    kop(fig, f"Prijs weer op crisisniveau; voor 2027 verwacht het model {jaar.midden_na_correctie:.0f} tot {jaar.waarde:.0f} euro",
        f"80% van de uitkomsten ligt tussen {jaar.laag80:.0f} en {jaar.hoog80:.0f} euro per MWh. Model: terugkeer naar het gemiddelde.",
        "Bron: Energy-Charts; eigen prognose (fact_prognose_SA). Het interval is de fout die het model eerder werkelijk maakte.")
    bewaar(fig, uit, "06_prijs_prognose.png", f"Deze grafiek laat zien dat de Nederlandse dagmarktprijs eind 2026 weer het niveau van de crisis van 2022 nadert en dat het model voor 2027 "
           f"{jaar.midden_na_correctie:.0f} tot {jaar.waarde:.0f} euro per MWh verwacht, met een brede marge. De belangrijkste conclusie is: toets elk plan ook op een terugkeer naar {normaal:.0f} euro.", lijst)


def scenario_marge(data, uit, lijst):
    s = pd.read_csv(os.path.join(data, "fact_scenario_SA.csv"))
    w = s[s.jaar.isin([2030, 2050])].pivot(index="scenario", columns="jaar", values="marge_eur_mwh").sort_values(2030)
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    y = np.arange(len(w))
    ax.barh(y, w[2030], height=0.42, color=[K["rood"] if v < 0 else K["blauw"] for v in w[2030]], edgecolor=K["vlak"], linewidth=1.2)
    for yi, (a, b) in enumerate(zip(w[2030], w[2050])):
        punt(ax, b, yi, K["inkt2"], open_=True)
        ax.text(a + (0.9 if a >= 0 else -0.9), yi, f"{a:+.0f}", ha="left" if a >= 0 else "right", va="center", fontsize=9.5, color=K["inkt2"])
    ax.axvline(0, color=K["gedempt"], lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels([n[0].upper() + n[1:] for n in w.index]); ax.set_ylim(-0.6, len(w) - 0.2)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=K["blauw"], label="2030: kosten gedekt"), Patch(color=K["rood"], label="2030: kosten niet gedekt"),
                       Line2D([], [], marker="o", ls="", ms=7, color=K["vlak"], mec=K["inkt2"], mew=1.6, label="2050 (lagere kosten)")],
              loc="lower right", fontsize=9)
    ax.set_xlim(min(w[2030].min(), w[2050].min()) - 6, max(w[2030].max(), w[2050].max()) + 4)
    ax.set_xlabel("marge van zon zonder contract: capture-prijs min kosten (euro per MWh)"); ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    n = int((w[2030] < 0).sum())
    kop(fig, f"In {['geen', 'een', 'twee', 'drie', 'vier', 'vijf'][n]} van de vijf scenario's dekt zon zonder contract zijn kosten in 2030 niet",
        "Nederland. Scenario's zijn aannames, geen voorspelling. In 2050 helpen lagere kosten (rondjes).", "Bron: eigen scenario's (fact_scenario_SA); kosten uit het eigen model.")
    bewaar(fig, uit, "07_scenario_marge.png", f"Deze grafiek laat zien dat zon zonder contract in {n} van de vijf scenario's in 2030 minder opbrengt dan het kost, en dat lagere kosten dat "
           "richting 2050 in de meeste scenario's goedmaken. De belangrijkste conclusie is: het rendement hangt aan de gasprijs en aan het tempo van flexibiliteit, niet aan de zon zelf.", lijst)


def maand_uur(data, uit, lijst, jaar=2025):
    u = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), parse_dates=["timestamp_utc"]).dropna(subset=["prijs_eur_mwh"])
    lokaal = u.timestamp_utc.dt.tz_localize("UTC").dt.tz_convert("Europe/Amsterdam")
    u = u.assign(m=lokaal.dt.month, h=lokaal.dt.hour, j=lokaal.dt.year).query("j == @jaar")
    w = u.pivot_table(index="m", columns="h", values="prijs_eur_mwh") / u.prijs_eur_mwh.mean()
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    sns.heatmap(w, ax=ax, cmap=ROND_MIDDEN, center=1.0, vmin=0.0, vmax=2.0, linewidths=0.6, linecolor=K["vlak"],
                cbar_kws={"label": "prijs (1 = gemiddelde van het jaar)", "shrink": 0.85})
    ax.set_yticklabels(MAAND, rotation=0); ax.set_xticks(np.arange(0, 24, 3) + 0.5); ax.set_xticklabels(range(0, 24, 3), rotation=0)
    ax.set_xlabel("uur van de dag (lokale tijd)"); ax.set_ylabel(""); ax.grid(False)
    laag = w.stack().idxmin()
    zomer = w.loc[4:8, 11:15].mean().mean()
    kop(fig, "Het gat zit in de zomermiddag", f"Nederlandse dagmarktprijs {jaar} per maand en uur. Van april tot augustus tussen 11 en 15 uur: {zomer:.2f} keer het jaargemiddelde.".replace("0.", "0,"),
        "Bron: Energy-Charts; eigen berekening. Blauw is goedkoper dan gemiddeld, rood duurder.")
    bewaar(fig, uit, "08_maand_uur.png", f"Deze grafiek laat zien dat stroom van april tot augustus rond het middaguur {zomer:.0%} van de gemiddelde jaarprijs kost, met het dieptepunt in "
           f"{MAAND[laag[0] - 1]} om {laag[1]} uur. De belangrijkste conclusie is: opslag en flexibele vraag verdienen hun geld in vijf maanden van het jaar.", lijst)


def capture_per_maand(data, uit, lijst):
    t = pd.read_csv(os.path.join(data, "fact_tijd_DA.csv")).query("reeks == 'capture rate zon' and dimensie == 'maand (2023 en later)'")
    v = t.set_index(t.sleutel.astype(int)).waarde.sort_index()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(range(12), v.values, width=0.5, color=[K["blauw"] if x >= 0.95 else K["grijs"] for x in v.values], edgecolor=K["vlak"], linewidth=1.2)
    ax.axhline(1, color=K["gedempt"], lw=0.8); ax.text(5.5, 1.012, "gemiddelde prijs van het jaar", ha="center", fontsize=8.5, color=K["gedempt"])
    for i in (int(v.idxmin()) - 1, int(v.idxmax()) - 1):
        ax.text(i, v.iloc[i] + 0.025, f"{v.iloc[i]:.2f}".replace(".", ","), ha="center", fontsize=9.5, color=K["inkt2"])
    ax.set_xticks(range(12)); ax.set_xticklabels(MAAND); ax.set_ylim(0, 1.2); ax.set_ylabel("capture rate van zon")
    goed = [MAAND[i] for i, x in enumerate(v.values) if x >= 0.95]
    kop(fig, "Zon verdient alleen in de wintermaanden de gemiddelde prijs", f"Nederland, gemiddelde van 2023 tot en met 2026. Blauw: maanden op of boven 0,95 ({', '.join(goed)}).",
        "Bron: Energy-Charts; eigen berekening (fact_tijd_DA).")
    bewaar(fig, uit, "09_capture_per_maand.png", f"Deze grafiek laat zien dat zon in {MAAND[int(v.idxmin()) - 1]} {v.min():.0%} van de gemiddelde prijs ontvangt en alleen in {', '.join(goed)} "
           "ongeveer de volle prijs. De belangrijkste conclusie is: de maanden met de meeste opwek zijn de maanden met de laagste waarde per MWh.", lijst)


def nederland_twee(data, uit, lijst):
    p = pd.read_csv(os.path.join(data, "fact_zonejaar_DA.csv")).query("biedzone == 'NL'").sort_values("jaar")
    fig, (a, b) = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True, gridspec_kw={"hspace": 0.28})
    heel = p[~p.deeljaar]
    for ax, kol, kleur, schaal, label in ((a, "capture_zon", K["blauw"], 1, "capture rate van zon"), (b, "batterij_per_mw", K["oranje"], 1000, "batterij 2 uur (duizend euro per MW per jaar)")):
        ax.plot(heel.jaar, heel[kol] / schaal, color=kleur)
        ax.plot(p.jaar.iloc[-2:], p[kol].iloc[-2:] / schaal, color=kleur, ls=(0, (1, 2)))
        for x, y in zip(heel.jaar, heel[kol] / schaal):
            punt(ax, x, y, kleur)
        punt(ax, p.jaar.iloc[-1], p[kol].iloc[-1] / schaal, kleur, open_=True)
        ax.set_ylabel(label); ax.set_ylim(0, None)
        for r in (p.iloc[0], p.iloc[-1]):
            ax.text(r.jaar, r[kol] / schaal + ax.get_ylim()[1] * 0.06, f"{r[kol] / schaal:.2f}".replace(".", ",") if schaal == 1 else f"{r[kol] / schaal:.0f}",
                    ha="center", fontsize=9.5, color=K["inkt2"])
    b.set_xticks(p.jaar); b.set_xticklabels([str(j) if not d else f"{j}\n(tot 15 nov)" for j, d in zip(p.jaar, p.deeljaar)])
    kop(fig, "Nederland: zon verliest waarde terwijl de batterij wint", "Twee maten, elk met een eigen as onder elkaar. Open punt: onvolledig jaar. De piek van 2022 is de gascrisis.",
        "Bron: Energy-Charts; eigen berekening (fact_zonejaar_DA).")
    bewaar(fig, uit, "10_nederland_twee.png", f"Deze grafiek laat zien dat de capture rate van zon in Nederland van {p.capture_zon.iloc[0]:.2f} naar {p.capture_zon.iloc[-1]:.2f} ging, terwijl de "
           f"dagmarktomzet van een batterij steeg van {p.batterij_per_mw.iloc[0] / 1000:.0f} naar {p.batterij_per_mw.iloc[-1] / 1000:.0f} duizend euro per MW. "
           "De belangrijkste conclusie is: zon en opslag dekken elkaar af; samen in een portefeuille is het risico kleiner dan elk apart.", lijst)


FIGUREN = [capture_daling, jaar_tegen_land, uurprofiel, rendement, bijsturen, prijs_prognose, scenario_marge, maand_uur, capture_per_maand, nederland_twee]


def main(data=DATA, uit=UIT):
    stijl()
    lijst = []
    for f in FIGUREN:
        f(data, uit, lijst)
        print(f"  -> {lijst[-1][0]}")
    with open(os.path.join(uit, "bijschriften.txt"), "w", encoding="utf-8") as fh:
        for naam, tekst in lijst:
            fh.write(f"{naam}\n{tekst}\n\n")
    return lijst


if __name__ == "__main__":
    main(*sys.argv[1:3])
