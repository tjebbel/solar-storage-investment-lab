"""Maakt het notebook-sjabloon notebooks/analyse_sjabloon.ipynb.

Het sjabloon heeft zes delen (instellen, overzicht, opschonen, verkennen, kernanalyse, bevindingen). Elk deel begint
met een uitleg wat er moet gebeuren en waar je het aanpast; elke codecel doet een ding. Zoals het wordt geleverd
draait het op fact_land_jaar; pas de cel 'Instellingen' aan voor een andere tabel.

Gebruik:  PYTHONPATH=src python3 -m eti.maak_notebook           (schrijft het notebook opnieuw)
"""
import json
import os
import sys

UIT = "notebooks/analyse_sjabloon.ipynb"

CELLEN = [
    ("md", """# Analyse: [titel van de vraag]

**Vraag:** [in een zin: wat wil je weten en voor wie]
**Data:** [tabel, periode, bron]
**Auteur en datum:** [naam], [datum]

Werk van boven naar beneden. Elke cel doet een ding; draai ze in volgorde (Kernel → Restart & Run All moet
zonder fouten doorlopen voordat je het notebook deelt)."""),
    ("md", """## 1. Instellen

Laad de bibliotheken en zet alle keuzes op een plek. **Pas alleen de cel 'Instellingen' aan** om het sjabloon op
een andere tabel te gebruiken: het pad, de sleutel (kolommen die samen een rij uniek maken), de doelkolom en de
grenzen waarbinnen een waarde geloofwaardig is."""),
    ("code", """import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats"""),
    ("code", """# Instellingen
DATA = "../powerbi/data"                 # map met de csv-bestanden, gezien vanuit notebooks/
TABEL = "fact_land_jaar.csv"
SLEUTEL = ["biedzone", "jaar"]           # samen uniek per rij
DOEL = "capture_zon"                     # de kolom waar de vraag over gaat
GROEP = "jaar"                           # indeling voor vergelijkingen
BEREIK = {"capture_zon": (0, 2), "negatieve_uren": (0, 8784)}    # buiten deze grenzen is een waarde een fout
VERGELIJK = (2019, 2025)                 # twee groepen voor de toets in deel 5"""),
    ("code", """sns.set_theme(style="white", rc={"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y",
                                 "grid.color": "#e1e0d9", "figure.dpi": 110})
BLAUW, ORANJE, GRIJS = "#2a78d6", "#eb6834", "#c3c2b7"
pd.set_option("display.max_columns", 40)"""),
    ("md", """## 2. Overzicht van de data

Lees de tabel en kijk eerst, voordat je iets verandert: hoeveel rijen en kolommen, welke typen, wat ontbreekt.
Noteer onder de cellen wat opvalt. Klopt het aantal rijen met wat je verwacht?"""),
    ("code", """ruw = pd.read_csv(f"{DATA}/{TABEL}", low_memory=False)
print(f"{len(ruw):,}".replace(",", ".") + f" rijen, {ruw.shape[1]} kolommen")"""),
    ("code", """ruw.head()"""),
    ("code", """overzicht = pd.DataFrame({"type": ruw.dtypes.astype(str), "leeg": ruw.isna().sum(), "leeg_pct": (ruw.isna().mean() * 100).round(1), "uniek": ruw.nunique()})
overzicht"""),
    ("code", """ruw.describe().T.assign(mediaan=ruw.median(numeric_only=True), scheefheid=ruw.skew(numeric_only=True)).round(2)"""),
    ("md", """## 3. Opschonen

Drie stappen, elk in een eigen cel: dubbele rijen, waarden buiten bereik, lege waarden. Schrijf bij elke stap op
**hoeveel** rijen of waarden het raakt en **waarom** je het zo doet. Gooi nooit stil iets weg: de laatste cel van dit
deel telt na wat er veranderd is."""),
    ("code", """dubbel = int(ruw.duplicated(SLEUTEL).sum())
df = ruw.drop_duplicates(SLEUTEL).copy()
print(f"{dubbel} dubbele sleutels verwijderd")"""),
    ("code", """buiten = {}
for kolom, (laag, hoog) in BEREIK.items():
    fout = df[kolom].notna() & ~df[kolom].between(laag, hoog)
    buiten[kolom] = int(fout.sum())
    df.loc[fout, kolom] = np.nan          # een onmogelijke waarde is geen meting: leeg maken, niet schatten
buiten"""),
    ("code", """# Lege waarden in de doelkolom: weglaten voor de analyse (niet invullen), en tellen.
leeg_doel = int(df[DOEL].isna().sum())
schoon = df.dropna(subset=[DOEL])
print(f"{leeg_doel} rijen zonder {DOEL} blijven buiten de analyse")"""),
    ("code", """assert len(schoon) == len(ruw) - dubbel - leeg_doel, "de telling van het opschonen sluit niet"
print(f"van {len(ruw)} naar {len(schoon)} rijen: {dubbel} dubbel, {leeg_doel} zonder doelwaarde, {sum(buiten.values())} waarden buiten bereik leeg gemaakt")"""),
    ("md", """## 4. Verkennen

Kijk naar de verdeling van de doelkolom, naar het verloop per groep en naar de samenhang met de andere kolommen.
Een grafiek per cel, met een titel die zegt wat je ziet. Schrijf onder elke grafiek een zin: wat valt op?"""),
    ("code", """fig, ax = plt.subplots(figsize=(7, 3))
sns.histplot(schoon[DOEL], bins=30, color=BLAUW, edgecolor="white", ax=ax)
ax.axvline(schoon[DOEL].median(), color=ORANJE, lw=1.5)
ax.set_title(f"Verdeling van {DOEL}: mediaan {schoon[DOEL].median():.2f}, scheefheid {schoon[DOEL].skew():.2f}", loc="left", fontweight="bold")
ax.set_xlabel(DOEL); ax.set_ylabel("aantal rijen")
plt.show()"""),
    ("code", """fig, ax = plt.subplots(figsize=(7, 3.2))
sns.boxplot(data=schoon, x=GROEP, y=DOEL, color=BLAUW, width=0.5, fliersize=3, linewidth=1, ax=ax)
ax.set_title(f"{DOEL} per {GROEP}", loc="left", fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel(DOEL)
plt.show()"""),
    ("code", """getallen = schoon.select_dtypes("number").drop(columns=[GROEP], errors="ignore")
getallen = getallen.loc[:, getallen.nunique() > 1]
correlatie = getallen.corr(method="spearman")
correlatie[DOEL].drop(DOEL).sort_values().round(2)"""),
    ("code", """fig, ax = plt.subplots(figsize=(7, 5.5))
sns.heatmap(correlatie, cmap=sns.diverging_palette(250, 15, s=75, l=50, as_cmap=True), center=0, vmin=-1, vmax=1, linewidths=0.5, linecolor="white",
            cbar_kws={"label": "rangcorrelatie (Spearman)"}, ax=ax)
ax.set_title("Samenhang tussen de numerieke kolommen", loc="left", fontweight="bold")
plt.show()"""),
    ("md", """## 5. Kernanalyse

Beantwoord hier de vraag van bovenaan. Schrijf eerst in gewone taal op wat je toetst (nulhypothese en alternatief),
kies de toets die bij de data past (zie de scheefheid in deel 4: bij scheve data een rangtoets), en geef naast de
uitkomst van de toets altijd de omvang van het effect en een interval. Zijn dezelfde eenheden op twee momenten
gemeten, vergelijk ze dan gepaard."""),
    ("code", """# Nulhypothese: DOEL is tussen de twee groepen niet gedaald. Alternatief: het is gedaald.
breed = schoon.pivot(index=SLEUTEL[0], columns=GROEP, values=DOEL)[list(VERGELIJK)].dropna()
verschil = breed[VERGELIJK[1]] - breed[VERGELIJK[0]]
print(f"{len(verschil)} eenheden met een waarde in beide groepen; normaliteit van het verschil: p = {stats.shapiro(verschil).pvalue:.3f}")"""),
    ("code", """toets = stats.wilcoxon(verschil, alternative="less")
laag, hoog = stats.t.interval(0.95, len(verschil) - 1, loc=verschil.mean(), scale=stats.sem(verschil))
uitkomst = {"gemiddeld verschil": round(float(verschil.mean()), 3), "interval 95%": (round(float(laag), 3), round(float(hoog), 3)),
            "effectgrootte (verschil / spreiding)": round(float(verschil.mean() / verschil.std(ddof=1)), 2),
            "aandeel gedaald": round(float((verschil < 0).mean()), 2), "p": float(toets.pvalue)}
uitkomst"""),
    ("code", """fig, ax = plt.subplots(figsize=(7, 3))
sns.histplot(verschil, bins=20, color=BLAUW, edgecolor="white", ax=ax)
ax.axvline(0, color="#52514e", lw=1)
ax.set_title(f"Verschil {VERGELIJK[1]} min {VERGELIJK[0]} per {SLEUTEL[0]}: gemiddeld {verschil.mean():+.2f}", loc="left", fontweight="bold")
ax.set_xlabel(f"verandering van {DOEL}"); ax.set_ylabel("aantal")
plt.show()"""),
    ("md", """## 6. Bevindingen en aanbevelingen

Vul in en verwijder de aanwijzingen tussen haken.

**In een zin:** [het antwoord op de vraag van bovenaan]

**Bevindingen**
1. [bevinding, met het getal en de vergelijking erbij] → [wat het betekent]
2. [...]
3. [...]

**Aanbevelingen**
- [wie doet wat, en wanneer]

**Beperkingen**
- [wat de data niet kan zeggen; welke aanname de uitkomst het meest bepaalt]

**Vervolg**
- [de eerstvolgende analyse die de grootste onzekerheid wegneemt]"""),
    ("code", """# Kerncijfers om hierboven over te nemen
pd.Series({"rijen in de analyse": len(schoon), f"mediaan {DOEL}": round(float(schoon[DOEL].median()), 3), **uitkomst}, name="waarde").to_frame()"""),
]


def notebook():
    cellen = []
    for i, (soort, tekst) in enumerate(CELLEN):
        regels = tekst.splitlines(keepends=True)
        cel = {"cell_type": "markdown" if soort == "md" else "code", "id": f"cel-{i:02d}", "metadata": {}, "source": regels}
        if soort == "code":
            cel.update({"execution_count": None, "outputs": []})
        cellen.append(cel)
    return {"cells": cellen, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 5}


def main(uit=UIT):
    os.makedirs(os.path.dirname(uit), exist_ok=True)
    with open(uit, "w", encoding="utf-8") as fh:
        json.dump(notebook(), fh, ensure_ascii=False, indent=1)
    print(f"  -> {uit}: {len(CELLEN)} cellen")


if __name__ == "__main__":
    main(*sys.argv[1:2])
