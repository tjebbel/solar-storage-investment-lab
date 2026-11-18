"""Balanceringsinkomsten zelf gemodelleerd: FCR naast de dagmarkt en het bijsturen op onbalans, dag voor dag.

Wat erin zit:
- FCR: de capaciteitsprijs per blok van vier uur (fact_fcr_nl, euro per MW per uur). Een batterij die het blok wint,
  krijgt prijs maal vier uur per MW. Aanname: 1 MW batterij met twee uur opslag kan 1 MW FCR leveren.
- Dagmarkt en dagmarkt met bijsturen: de dagreeksen uit de eerdere proef (fact_abtest_dag_SA; plan op gisteren).
Strategieen: alleen dagmarkt, dagmarkt met bijsturen, alleen FCR, half om half, en per dag wisselen naar wat gisteren
het meest opleverde. 'Achteraf de beste' is de bovengrens, niet uitvoerbaar.

Wat er niet in zit, en waarom dat telt:
- De capaciteitsprijs van aFRR: ENTSO-E gaf die reeks niet terug (zie eti.balans). aFRR-energie staat in
  fact_afrr_energie_nl, maar zonder capaciteitsprijs en biedladder is daar geen eerlijke opbrengst uit te rekenen.
- Marktdiepte: de FCR-prijs is wat 1 MW erbij zou krijgen. De markt is klein; een vloot die instapt drukt de prijs.
- Netkosten en slijtage. De omzet is bruto.
Uitschieters in de FCR-prijs (blokken boven het 99,5e percentiel) zijn afgetopt, zoals in eti.balans.

Schrijft powerbi/data/fact_stapel_dag_ST.csv en fact_stapel_jaar_ST.csv en een figuur.
Gebruik:  PYTHONPATH=src python3 -m eti.stapel
"""
import os

import numpy as np
import pandas as pd

DATA, FIG = "powerbi/data", "reports/analyse/fig"
BLOKUREN, BLOKKEN_PER_DAG = 4, 6
NODIG = {"8% rendement": 85491, "5% rendement": 73422}       # euro per MW per jaar, uit de volledige batterijcase
STRATEGIEEN = {"dagmarkt": "Dagmarkt", "bijsturen": "Dagmarkt met bijsturen", "fcr": "Alleen FCR", "half": "Half FCR, half dagmarkt met bijsturen",
               "wissel": "Per dag wisselen op gisteren", "achteraf": "Achteraf de beste (bovengrens)"}


def fcr_per_dag(data=DATA):
    f = pd.read_csv(os.path.join(data, "fact_fcr_nl.csv"), parse_dates=["vanaf_utc"]).sort_values("vanaf_utc")
    f["prijs"] = f.prijs_eur_mw_uur.clip(upper=f.prijs_eur_mw_uur.quantile(0.995))
    lokaal = f.vanaf_utc.dt.tz_localize("UTC").dt.tz_convert("Europe/Amsterdam")
    f["datum"] = lokaal.dt.strftime("%Y-%m-%d")
    f = f[lokaal.dt.hour % BLOKUREN == 0]                       # alleen hele blokken; het afgekapte eerste blok van de reeks valt weg
    d = f.groupby("datum").agg(blokken=("prijs", "size"), fcr=("prijs", lambda s: float(s.sum() * BLOKUREN)), fcr_onafgetopt=("prijs_eur_mw_uur", lambda s: float(s.sum() * BLOKUREN)))
    return d[d.blokken == BLOKKEN_PER_DAG].drop(columns="blokken")


def dagtabel(data=DATA):
    a = pd.read_csv(os.path.join(data, "fact_abtest_dag_SA.csv"))[["datum", "jaar", "a", "b"]].rename(columns={"a": "dagmarkt", "b": "bijsturen"})
    d = a.merge(fcr_per_dag(data), on="datum", how="inner").sort_values("datum").reset_index(drop=True)
    d["half"] = 0.5 * d.fcr + 0.5 * d.bijsturen
    gisteren = d[["bijsturen", "fcr"]].shift(1)
    d["keuze"] = np.where(gisteren.fcr > gisteren.bijsturen, "fcr", "bijsturen")
    d.loc[0, "keuze"] = "bijsturen"
    d["wissel"] = np.where(d.keuze == "fcr", d.fcr, d.bijsturen)
    d["achteraf"] = d[["bijsturen", "fcr"]].max(axis=1)
    return d


def jaartabel(d):
    rijen = []
    for jaar, t in d.groupby("jaar"):
        for sleutel, naam in STRATEGIEEN.items():
            omzet = t[sleutel].mean() * 365
            rijen.append({"jaar": jaar, "strategie": naam, "sleutel": sleutel, "dagen": len(t), "omzet_per_mw_jaar": omzet, "standaardafwijking_dag": t[sleutel].std(),
                          "slechtste_maand_per_mw_jaar": t.groupby(t.datum.str[:7])[sleutel].mean().min() * 365, "aandeel_dagen_fcr": float((t.keuze == "fcr").mean()) if sleutel == "wissel" else np.nan,
                          **{f"haalt_{k.split('%')[0]}pct": bool(omzet >= v) for k, v in NODIG.items()}})
    uit = pd.DataFrame(rijen)
    uit["correlatie_fcr_dagmarkt"] = uit.jaar.map(d.groupby("jaar").apply(lambda t: t.fcr.corr(t.bijsturen), include_groups=False))
    uit["fcr_onafgetopt_per_mw_jaar"] = uit.jaar.map(d.groupby("jaar").fcr_onafgetopt.mean() * 365).where(uit.sleutel == "fcr")
    return uit


def figuur(j, uit=FIG):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .vis import K, bewaar, kop, stijl
    stijl()
    lijst = []
    toon = [("dagmarkt", K["grijs"]), ("bijsturen", K["blauw"]), ("fcr", K["oranje"]), ("wissel", K["aqua"])]
    jaren = sorted(j.jaar.unique())
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    breedte = 0.2
    for i, (sleutel, kleur) in enumerate(toon):
        t = j[j.sleutel == sleutel].set_index("jaar").omzet_per_mw_jaar.reindex(jaren) / 1000
        x = np.arange(len(jaren)) + (i - 1.5) * breedte
        ax.bar(x, t.values, width=breedte - 0.02, color=kleur, label=STRATEGIEEN[sleutel])
        for xx, v in zip(x, t.values):
            ax.text(xx, v + 3, f"{v:.0f}", ha="center", fontsize=8, color=K["inkt2"])
    grens = NODIG["8% rendement"] / 1000
    ax.axhline(grens, color=K["inkt2"], lw=1, ls=(0, (4, 3)))
    ax.text(len(jaren) - 0.52, grens, f"nodig voor\n8%: {grens:.0f}", fontsize=8.5, color=K["inkt2"], ha="left", va="center")
    ax.set_xlim(-0.6, len(jaren) + 0.1)
    ax.set_xticks(range(len(jaren))); ax.set_xticklabels([str(y) if y < max(jaren) else f"{y}\n(tot half nov)" for y in jaren])
    ax.set_ylabel("duizend euro per MW per jaar"); ax.legend(loc="upper left", fontsize=8.5, ncol=2)
    ax.set_ylim(0, j[j.sleutel.isin([s for s, _ in toon])].omzet_per_mw_jaar.max() / 1000 * 1.32)
    f = j[j.sleutel == "fcr"].set_index("jaar").omzet_per_mw_jaar
    b = j[j.sleutel == "bijsturen"].set_index("jaar").omzet_per_mw_jaar
    eerste = min(y for y in jaren if f[y] > b[y])
    kop(fig, f"FCR betaalt sinds {eerste} het meest: {f[eerste] / 1000:.0f} duizend euro per MW in {eerste}, {f.iloc[-1] / 1000:.0f} in {jaren[-1]}",
        "Bruto omzet van 1 MW met twee uur opslag. FCR-prijs is wat 1 MW erbij zou krijgen; de markt is klein.",
        "Bron: ENTSO-E (FCR, onbalans), Energy-Charts (dagmarkt); eigen model (fact_stapel_jaar_ST). Zonder aFRR-capaciteit en netkosten.")
    bewaar(fig, uit, "15_stapel_fcr_dagmarkt.png", f"Deze grafiek laat zien dat 1 MW in FCR in {jaren[-1]} {f.iloc[-1] / 1000:.0f} duizend euro per jaar zou opleveren tegen {b.iloc[-1] / 1000:.0f} duizend op de dagmarkt met bijsturen, "
           "en dat per dag wisselen op basis van gisteren daar weinig aan toevoegt. De belangrijkste conclusie is: de waarde zit in de capaciteitsmarkt, en precies die is klein en vol te bieden.", lijst)
    with open(os.path.join(uit, "bijschriften_stapel.txt"), "w", encoding="utf-8") as fh:
        for naam, tekst in lijst:
            fh.write(f"{naam}\n{tekst}\n\n")
    return lijst


def main(data=DATA, fig=FIG):
    d = dagtabel(data)
    j = jaartabel(d)
    d.round(3).to_csv(os.path.join(data, "fact_stapel_dag_ST.csv"), index=False)
    j.round(3).to_csv(os.path.join(data, "fact_stapel_jaar_ST.csv"), index=False)
    figuur(j, fig)
    return d, j


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    d, j = main()
    print(j.pivot(index="strategie", columns="jaar", values="omzet_per_mw_jaar").round(0).to_string())
    print(j[j.sleutel == "wissel"][["jaar", "dagen", "aandeel_dagen_fcr", "correlatie_fcr_dagmarkt"]].round(2).to_string(index=False))
    print(j[j.sleutel == "fcr"][["jaar", "omzet_per_mw_jaar", "fcr_onafgetopt_per_mw_jaar", "slechtste_maand_per_mw_jaar"]].round(0).to_string(index=False))
