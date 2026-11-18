"""Volledig analysescript in een bestand: van csv tot grafieken en samenvatting.

Vraag: wat is er met de marktwaarde van zon gebeurd, en compenseert opslag dat? Het script leest drie tabellen,
controleert ze, schoont ze op, verkent ze, voert drie analyses uit (gepaarde toets, samenhang tussen zon en opslag,
een verklarend model met kruisvalidatie), bewaart drie grafieken als PNG en schrijft een samenvatting en een logboek.
Het leunt bewust niet op de andere modules: alles wat het doet staat hieronder.

Gebruik:  python3 src/eti/analyse_script.py [datamap] [uitvoermap]
Nodig: pandas, numpy, matplotlib, seaborn, scipy, scikit-learn.
"""
import logging
import os
import sys

if sys.path and os.path.abspath(sys.path[0]) == os.path.dirname(os.path.abspath(__file__)):
    sys.path.pop(0)          # als script gestart staat src/eti vooraan en verdringt eti/numbers.py de standaardmodule numbers

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GroupKFold, cross_val_predict

DATA, UIT = "powerbi/data", "resultaten/analyse_script"
VERPLICHT = {"fact_land_jaar.csv": ["land", "biedzone", "jaar", "gem_prijs", "capture_zon", "negatieve_uren", "dagspreiding", "uren", "iso3"],
             "fact_flex_land.csv": ["land", "jaar", "uren_opslag", "omzet_realistisch_per_mw"],
             "fact_ember_opwek_jaar.csv": ["ISO 3 code", "Year", "Electricity source", "Share of generation (%)"]}
BEREIK = {"capture_zon": (0, 2), "negatieve_uren": (0, 8784), "gem_prijs": (-500, 5000), "dagspreiding": (0, 5000)}
HEEL_JAAR = 8700                                  # minstens zoveel uren met een prijs
KENMERKEN = ["gem_prijs", "aandeel_zon_pct", "aandeel_wind_pct", "aandeel_gas_pct", "aandeel_waterkracht_pct", "jaar"]
BLAUW, ORANJE, GRIJS, INKT, VLAK = "#2a78d6", "#eb6834", "#c3c2b7", "#52514e", "#fcfcfb"
log = logging.getLogger("analyse")


class DataFout(Exception):
    """De invoer voldoet niet aan wat de analyse nodig heeft; doorrekenen zou onzin opleveren."""


# ------------------------------------------------------------------------------------------- 1 laden en toetsen
def laad(data=DATA):
    """Leest de tabellen en controleert kolommen, typen, lege sleutels en bereik. Stopt bij een structurele fout."""
    tabellen = {}
    for bestand, kolommen in VERPLICHT.items():
        pad = os.path.join(data, bestand)
        if not os.path.exists(pad):
            raise DataFout(f"{pad} ontbreekt")
        df = pd.read_csv(pad, low_memory=False)
        ontbreekt = [k for k in kolommen if k not in df.columns]
        if ontbreekt:
            raise DataFout(f"{bestand}: kolommen ontbreken: {', '.join(ontbreekt)}")
        if df.empty:
            raise DataFout(f"{bestand} is leeg")
        tabellen[bestand] = df
        log.info("gelezen %s: %d rijen, %d kolommen, %.1f%% lege cellen", bestand, len(df), df.shape[1], df.isna().mean().mean() * 100)
    land = tabellen["fact_land_jaar.csv"]
    for k in ("gem_prijs", "capture_zon", "negatieve_uren", "dagspreiding", "uren", "jaar"):
        if not pd.api.types.is_numeric_dtype(land[k]):
            raise DataFout(f"fact_land_jaar.{k} is geen getal ({land[k].dtype})")
    if land[["biedzone", "jaar"]].isna().any().any():
        raise DataFout("fact_land_jaar heeft lege sleutels (biedzone of jaar)")
    for k, (laag, hoog) in BEREIK.items():
        buiten = int((~land[k].between(laag, hoog) & land[k].notna()).sum())
        if buiten:
            log.warning("fact_land_jaar.%s: %d waarden buiten %s tot %s; die worden bij het opschonen leeg gemaakt", k, buiten, laag, hoog)
    return tabellen


# ------------------------------------------------------------------------------------------------ 2 opschonen
def schoon(tabellen):
    """Een rij per biedzone en jaar met de batterij van 2 uur en de opwekmix. Dubbele rijen eruit, waarden buiten
    bereik leeg, tekst getrimd, onvolledige jaren gemarkeerd."""
    land = tabellen["fact_land_jaar.csv"].copy()
    land["land"], land["biedzone"] = land.land.str.strip(), land.biedzone.str.strip()
    voor = len(land)
    land = land.sort_values("uren", ascending=False).drop_duplicates(["biedzone", "jaar"])
    if len(land) < voor:
        log.warning("%d dubbele zone-jaren verwijderd (de rij met de meeste uren blijft)", voor - len(land))
    for k, (laag, hoog) in BEREIK.items():
        land[k] = land[k].where(land[k].between(laag, hoog))
    land["heel_jaar"] = land.uren >= HEEL_JAAR
    flex = tabellen["fact_flex_land.csv"].query("uren_opslag == 2").drop_duplicates(["land", "jaar"])
    flex = flex.rename(columns={"omzet_realistisch_per_mw": "batterij_per_mw"})[["land", "jaar", "batterij_per_mw"]]
    e = tabellen["fact_ember_opwek_jaar.csv"]
    e = e[e["ISO 3 code"].notna()]
    namen = {"Solar": "aandeel_zon_pct", "Wind": "aandeel_wind_pct", "Gas": "aandeel_gas_pct", "Hydro": "aandeel_waterkracht_pct"}
    mix = e[e["Electricity source"].isin(namen)].pivot_table(index=["ISO 3 code", "Year"], columns="Electricity source", values="Share of generation (%)", aggfunc="first")
    mix = mix.rename(columns=namen).reset_index().rename(columns={"ISO 3 code": "iso3", "Year": "jaar"})
    p = land.merge(flex, on=["land", "jaar"], how="left").merge(mix, on=["iso3", "jaar"], how="left")
    for k in namen.values():                                   # opwekmix ontbreekt voor het lopende jaar: laatste bekende waarde van het land
        p[k] = p.sort_values("jaar").groupby("biedzone")[k].ffill()
    log.info("opgeschoond: %d zone-jaren, %d zones, %d hele jaren; %d lege capture rates", len(p), p.biedzone.nunique(), p[p.heel_jaar].jaar.nunique(), int(p.capture_zon.isna().sum()))
    return p.sort_values(["biedzone", "jaar"]).reset_index(drop=True)


# ------------------------------------------------------------------------------------------------- 3 verkennen
def verken(p):
    """Kengetallen, verdeling en rangcorrelaties over de hele jaren."""
    v = p[p.heel_jaar]
    kol = ["gem_prijs", "capture_zon", "negatieve_uren", "dagspreiding", "batterij_per_mw", "aandeel_zon_pct", "aandeel_wind_pct"]
    kengetallen = v[kol].describe().T.assign(mediaan=v[kol].median(), scheefheid=v[kol].skew())
    normaal = {k: float(stats.shapiro(v[k].dropna()).pvalue) for k in kol}
    correlatie = v[kol].corr(method="spearman")
    log.info("verkend: %d zone-jaren; %d van de %d kolommen wijken af van een normale verdeling", len(v), sum(x < 0.05 for x in normaal.values()), len(kol))
    return kengetallen, correlatie, normaal


# ------------------------------------------------------------------------------------------------ 4 analyseren
def analyseer(p):
    """Drie analyses: (a) is de capture rate gedaald (gepaard per zone), (b) bewegen zon en opslag tegengesteld,
    (c) wat verklaart de batterij-omzet (model, getoetst op zones die het niet zag)."""
    v = p[p.heel_jaar]
    eerste, laatste = int(v.jaar.min()), int(v.jaar.max())
    w = v.pivot(index="biedzone", columns="jaar", values="capture_zon")[[eerste, laatste]].dropna()
    d = w[laatste] - w[eerste]
    toets = stats.wilcoxon(d, alternative="less")
    daling = {"van": eerste, "tot": laatste, "zones": len(d), "gemiddeld": float(d.mean()), "gedaald": int((d < 0).sum()), "p": float(toets.pvalue),
              "interval": tuple(float(x) for x in stats.t.interval(0.95, len(d) - 1, loc=d.mean(), scale=stats.sem(d)))}
    nu = v[v.jaar == laatste].dropna(subset=["capture_zon", "batterij_per_mw"])
    rho, p_rho = stats.spearmanr(nu.capture_zon, nu.batterij_per_mw)
    groei = v.sort_values("jaar").groupby("biedzone").agg(zon=("capture_zon", lambda s: s.iloc[-1] - s.iloc[0]), batterij=("batterij_per_mw", lambda s: s.iloc[-1] - s.iloc[0])).dropna()
    samenhang = {"jaar": laatste, "rho": float(rho), "p": float(p_rho), "zones": len(nu),
                 "zon_omlaag_batterij_omhoog": int(((groei.zon < 0) & (groei.batterij > 0)).sum()), "zones_met_verloop": len(groei)}
    m = v.dropna(subset=KENMERKEN + ["batterij_per_mw"])
    model = GradientBoostingRegressor(n_estimators=200, max_depth=2, learning_rate=0.05, random_state=1)
    voorspeld = cross_val_predict(model, m[KENMERKEN], m.batterij_per_mw, cv=GroupKFold(5), groups=m.biedzone)
    fout = m.batterij_per_mw - voorspeld
    model.fit(m[KENMERKEN], m.batterij_per_mw)
    belang = permutation_importance(model, m[KENMERKEN], m.batterij_per_mw, n_repeats=20, random_state=1)
    verklaring = {"zone_jaren": len(m), "r2": float(1 - (fout ** 2).sum() / ((m.batterij_per_mw - m.batterij_per_mw.mean()) ** 2).sum()),
                  "mae": float(fout.abs().mean()), "belang": sorted(zip(KENMERKEN, belang.importances_mean), key=lambda x: -x[1])}
    log.info("analyse: capture rate %+.2f (%d van %d zones gedaald); rho zon-opslag %.2f; model R2 %.2f", daling["gemiddeld"], daling["gedaald"], daling["zones"], rho, verklaring["r2"])
    return daling, samenhang, verklaring


# -------------------------------------------------------------------------------------------------- 5 tekenen
def teken(p, correlatie, uit):
    """Drie grafieken als PNG: verdeling per jaar, zon tegen opslag, en de correlaties."""
    sns.set_theme(style="white", rc={"figure.facecolor": VLAK, "axes.facecolor": VLAK, "savefig.facecolor": VLAK, "axes.spines.top": False, "axes.spines.right": False,
                                     "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#e1e0d9", "axes.edgecolor": GRIJS, "savefig.dpi": 200, "savefig.bbox": "tight"})
    v = p[p.heel_jaar]
    paden = []
    fig, ax = plt.subplots(figsize=(7, 3.6))
    sns.boxplot(data=v, x="jaar", y="capture_zon", color=BLAUW, width=0.5, fliersize=3, linewidth=1, ax=ax)
    ax.axhline(1, color=INKT, lw=0.8)
    ax.set_xlabel(""); ax.set_ylabel("capture rate van zon (1 = gemiddelde prijs)")
    ax.set_title(f"De marktwaarde van zon daalt in vrijwel elke zone: mediaan {v[v.jaar == v.jaar.min()].capture_zon.median():.2f} naar {v[v.jaar == v.jaar.max()].capture_zon.median():.2f}".replace(".", ","),
                 loc="left", fontsize=11.5, fontweight="bold")
    paden.append(os.path.join(uit, "1_capture_per_jaar.png")); fig.savefig(paden[-1]); plt.close(fig)

    nu = v[v.jaar == v.jaar.max()].dropna(subset=["capture_zon", "batterij_per_mw"])
    fig, ax = plt.subplots(figsize=(7, 4.2))
    sns.regplot(data=nu, x="capture_zon", y=nu.batterij_per_mw / 1000, scatter_kws={"s": 38, "color": BLAUW, "edgecolor": VLAK, "linewidths": 1.2}, line_kws={"color": ORANJE, "lw": 1.6}, ci=None, ax=ax)
    for r in pd.concat([nu.nlargest(3, "batterij_per_mw"), nu.nsmallest(2, "batterij_per_mw"), nu.nlargest(2, "capture_zon")]).drop_duplicates("biedzone").itertuples():
        ax.annotate(r.biedzone, (r.capture_zon, r.batterij_per_mw / 1000), xytext=(5, 4), textcoords="offset points", fontsize=8.5, color=INKT)
    ax.set_xlabel("capture rate van zon"); ax.set_ylabel("batterij 2 uur (duizend euro per MW per jaar)"); ax.grid(axis="x")
    ax.set_title(f"Waar zon weinig waard is, verdient opslag meer ({int(v.jaar.max())})", loc="left", fontsize=11.5, fontweight="bold")
    paden.append(os.path.join(uit, "2_zon_tegen_opslag.png")); fig.savefig(paden[-1]); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.4, 5))
    sns.heatmap(correlatie, annot=True, fmt=".2f", cmap=sns.diverging_palette(250, 15, s=75, l=50, as_cmap=True), center=0, vmin=-1, vmax=1, linewidths=0.6, linecolor=VLAK,
                cbar_kws={"label": "rangcorrelatie (Spearman)", "shrink": 0.8}, annot_kws={"fontsize": 8.5}, ax=ax)
    ax.grid(False)
    ax.set_title("Dagspreiding en batterij-omzet meten vrijwel hetzelfde", loc="left", fontsize=11.5, fontweight="bold")
    paden.append(os.path.join(uit, "3_correlaties.png")); fig.savefig(paden[-1]); plt.close(fig)
    log.info("grafieken bewaard: %s", ", ".join(os.path.basename(x) for x in paden))
    return paden


# ---------------------------------------------------------------------------------------------- 6 samenvatten
def nl(x, decimalen=2):
    """Getal in Nederlandse notatie: komma voor decimalen, punt voor duizendtallen."""
    return f"{x:,.{decimalen}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def samenvatting(p, kengetallen, daling, samenhang, verklaring):
    """De bevindingen in gewone taal, met de getallen erbij."""
    lo, hi = daling["interval"]
    top = ", ".join(f"{naam} ({nl(waarde)})" for naam, waarde in verklaring["belang"][:3])
    regels = [
        "SAMENVATTING",
        f"Data: {len(p)} zone-jaren, {p.biedzone.nunique()} biedzones, {int(p.jaar.min())} tot {int(p.jaar.max())}; hele jaren tot en met {daling['tot']}.",
        "",
        f"1. De capture rate van zon daalde tussen {daling['van']} en {daling['tot']} met gemiddeld {nl(abs(daling['gemiddeld']))} (95%-interval {nl(abs(hi))} tot {nl(abs(lo))}).",
        f"   Dat gebeurde in {daling['gedaald']} van de {daling['zones']} zones; toeval is vrijwel uitgesloten (p = {daling['p']:.1e}).",
        f"2. Zon en opslag bewegen tegengesteld. In {samenhang['jaar']} is de rangcorrelatie tussen de capture rate van zon en de batterij-omzet {nl(samenhang['rho'])}",
        f"   over {samenhang['zones']} zones (p = {nl(samenhang['p'], 3)}). In {samenhang['zon_omlaag_batterij_omhoog']} van de {samenhang['zones_met_verloop']} zones ging zon omlaag terwijl de batterij-omzet steeg.",
        f"3. Een model op prijsniveau, opwekmix en jaar verklaart {verklaring['r2']:.0%} van de batterij-omzet in zones die het niet zag",
        f"   (gemiddelde fout {nl(verklaring['mae'], 0)} euro per MW). Belangrijkste kenmerken, met de toename van de fout als ze worden geschud: {top}.",
        "",
        f"Mediaan batterij-omzet over alle hele jaren: {nl(kengetallen.loc['batterij_per_mw', 'mediaan'], 0)} euro per MW; mediaan capture rate: {nl(kengetallen.loc['capture_zon', 'mediaan'])}.",
        "Beperkingen: zones bewegen samen, dus de onzekerheid is groter dan de toets aangeeft; de batterij-omzet is dagmarkthandel zonder netkosten.",
    ]
    return "\n".join(regels) + "\n"


def main(data=DATA, uit=UIT):
    os.makedirs(uit, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", force=True,
                        handlers=[logging.FileHandler(os.path.join(uit, "analyse.log"), mode="w", encoding="utf-8"), logging.StreamHandler()])
    logging.getLogger("matplotlib").setLevel(logging.WARNING)       # geen meldingen van de tekenbibliotheek in het logboek
    try:
        p = schoon(laad(data))
        kengetallen, correlatie, _ = verken(p)
        daling, samenhang, verklaring = analyseer(p)
        teken(p, correlatie, uit)
        tekst = samenvatting(p, kengetallen, daling, samenhang, verklaring)
        with open(os.path.join(uit, "samenvatting.txt"), "w", encoding="utf-8") as fh:
            fh.write(tekst)
        kengetallen.round(3).to_csv(os.path.join(uit, "kengetallen.csv"))
        print(tekst)
        return 0
    except DataFout as e:
        log.error("invoer niet bruikbaar: %s", e)
        return 1
    except Exception:
        log.exception("onverwachte fout; zie de regels hierboven voor de stap waarin het misging")
        return 2


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
