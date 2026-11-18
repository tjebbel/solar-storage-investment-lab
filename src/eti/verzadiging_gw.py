"""Verzadigingscurve per GW batterijvermogen, voor Texas en Californie.

Vraag: wat doet de omvang van de batterijvloot met wat een batterij per MW verdient, los van de gasprijs, de hoeveelheid
zon, de vraag en het seizoen? Grondstof: fact_vs_dag (eti.vs_dag) en de dagprijs van gas (fact_gas_henryhub).

De vloot is niet gemeten als opgesteld vermogen maar afgeleid uit wat de batterijen op hun drukste uren leverden:
het 90e percentiel van de dagpieken over dertig dagen, dat daarna niet meer mag dalen. Voor Texas staat de vloot
tot eind 2024 in de restpost van EIA (OTH), daarna apart (BAT); voor Californie staat hij steeds in de restpost.

Model: ln(opbrengst per dag) = a + b * vloot in GW + zon, gasprijs, vraag en maand. Dus b is de daling per GW erbij.
De vorm in GW past beter dan de vorm in logaritmen (hogere R2 in beide markten) en hoort bij verzadiging: weinig
effect zolang de vloot klein is tegenover de avondpiek, veel zodra hij die benadert.

Wat het model wel en niet kan: de vloot groeit vrijwel alleen in de tijd (correlatie 0,90 tot 0,98). Het model scheidt
hem van alles wat per dag wisselt, maar niet van andere dingen die geleidelijk veranderen. Daarom staan er naast het
basismodel gevoeligheidsruns in de tabel (zonder schokken, met tijdtrend, met jaareffecten, in logaritmen, als aandeel
van de piekvraag) en een toets op het verschil tussen de twee markten. Lees de curve als bovengrens van wat de data
dragen, niet als natuurwet.

Schrijft powerbi/data/fact_verzadiging_{jaar,kwartaal,model,curve}_VZ.csv en twee figuren in reports/analyse/fig.
Gebruik:  PYTHONPATH=src python3 -m eti.verzadiging_gw
"""
import os

import numpy as np
import pandas as pd

DATA, FIG = "powerbi/data", "reports/analyse/fig"
KORT = {"VS Texas (ERCOT)": "Texas", "VS Californie (CAISO)": "Californie"}
SCHOKKEN = {"VS Texas (ERCOT)": (("2021-02-10", "2021-02-22"), ("2023-06-15", "2023-09-15")), "VS Californie (CAISO)": (("2020-08-14", "2020-09-08"), ("2022-09-01", "2022-09-10"))}
MIN_VLOOT_MW = 100
CONTROLES = ["ln_zon", "ln_gas", "ln_last"]
OPWEKKOLOMMEN = ["zon_mwh", "wind_mwh", "opwek_mwh", "zon_piek_mw", "opwek_piek_mw", "bat_ontladen_max_mw", "bat_laden_max_mw", "bat_ontladen_mwh", "oth_max_mw",
                 "oth_laden_max_mw", "bat_aandeel_piekuur"]


def laad(data=DATA):
    d = pd.read_csv(os.path.join(data, "fact_vs_dag.csv"), parse_dates=["datum"]).sort_values(["markt", "datum"])
    onvolledig = d.opwek_uren < 24                              # dagen waarop EIA uren mist: de opwekcijfers zeggen dan niets
    d.loc[onvolledig, OPWEKKOLOMMEN] = np.nan
    gas = pd.read_csv(os.path.join(data, "fact_gas_henryhub.csv"), parse_dates=["datum"]).dropna().sort_values("datum").set_index("datum").usd_mmbtu
    gas = gas.reindex(pd.date_range(gas.index.min(), d.datum.max())).ffill()
    delen = []
    for markt, x in d.groupby("markt"):
        x = x.copy()
        ruw = x.bat_ontladen_max_mw.where(x.bat_ontladen_max_mw.notna(), x.oth_max_mw)
        if "Texas" in markt:
            ruw = ruw.where(x.datum >= "2021-01-01")          # in 2020 bevat de restpost van Texas nog andere bronnen
        x["vloot_mw"] = ruw.rolling(30, min_periods=5).quantile(0.9).cummax()
        x["gas"] = gas.reindex(x.datum).values
        x["zon_aandeel"] = x.zon_mwh / x.opwek_mwh
        x["last"] = x.opwek_mwh / x.groupby(x.datum.dt.year).opwek_mwh.transform("mean")      # vraag tegenover het jaargemiddelde
        x["vloot_rel"] = x.vloot_mw / x.opwek_piek_mw.rolling(365, min_periods=60).quantile(0.99) * 100      # procent van de piekopwek
        x["schok"] = False
        for van, tot in SCHOKKEN.get(markt, ()):
            x.loc[x.datum.between(van, tot), "schok"] = True
        delen.append(x)
    d = pd.concat(delen, ignore_index=True)
    d["jaar"], d["maand"] = d.datum.dt.year, d.datum.dt.month
    d["vloot_gw"] = d.vloot_mw / 1000
    with np.errstate(divide="ignore", invalid="ignore"):
        for naam, kolom in (("ln_vloot", "vloot_gw"), ("ln_zon", "zon_aandeel"), ("ln_gas", "gas"), ("ln_last", "last")):
            d[naam] = np.log(d[kolom].where(d[kolom] > 0))
    return d


def jaartabel(d):
    g = d.groupby(["markt", "jaar"])
    t = g.agg(dagen=("datum", "size"), vloot_gw=("vloot_gw", "max"), zonpiek_gw=("zon_piek_mw", "max"), gem_prijs_eur=("gem_prijs_eur", "mean"),
              gas_usd_mmbtu=("gas", "mean"), spreiding_2u=("spreiding_2u", "mean"), piekpremie=("piekpremie", "mean"), daldiepte=("daldiepte", "mean"),
              batterij_plan_per_mw_jaar=("batterij_plan_per_mw", "mean"), batterij_achteraf_per_mw_jaar=("batterij_achteraf_per_mw", "mean"),
              zon_aandeel=("zon_aandeel", "mean"), bat_aandeel_piekuur=("bat_aandeel_piekuur", "mean")).reset_index()
    t["zonpiek_gw"] /= 1000
    t["vloot_per_gw_zon"] = t.vloot_gw / t.zonpiek_gw
    for k in ("batterij_plan_per_mw_jaar", "batterij_achteraf_per_mw_jaar"):
        t[k] *= 365                                              # naar een heel jaar, ook voor het lopende jaar
    return t


def kwartaaltabel(d):
    d = d.assign(kwartaal=d.datum.dt.to_period("Q").astype(str))
    t = d.groupby(["markt", "kwartaal"]).agg(dagen=("datum", "size"), vloot_gw=("vloot_gw", "last"), spreiding_2u=("spreiding_2u", "mean"), piekpremie=("piekpremie", "mean"),
                                              daldiepte=("daldiepte", "mean"), batterij_plan_per_mw_jaar=("batterij_plan_per_mw", "mean")).reset_index()
    t["batterij_plan_per_mw_jaar"] *= 365
    return t[t.dagen >= 60]


def ontwerp(x, trend=False, vloot="vloot_gw"):
    kolommen = [vloot] + CONTROLES
    X = [np.ones(len(x))] + [x[k].values for k in kolommen] + [(x.maand == m).values.astype(float) for m in range(2, 13)]
    namen = ["constante"] + kolommen + [f"maand_{m}" for m in range(2, 13)]
    if trend == "trend":
        X.append(((x.datum - x.datum.min()).dt.days / 365.25).values); namen.append("jaren_sinds_start")
    if trend == "jaren":                                         # jaareffecten: de vloot telt dan alleen via de groei binnen een jaar
        for j in sorted(x.jaar.unique())[1:]:
            X.append((x.jaar == j).values.astype(float)); namen.append(f"jaar_{j}")
    return np.column_stack(X), namen


def schat(d, markt, doel="batterij_achteraf_per_mw", zonder_schokken=False, trend=False, vloot="vloot_gw"):
    from .sa import ols
    x = d[(d.markt == markt) & (d.vloot_mw >= MIN_VLOOT_MW) & (d[doel] > 0)].dropna(subset=[vloot] + CONTROLES)
    if zonder_schokken:
        x = x[~x.schok]
    X, namen = ontwerp(x, trend, vloot)
    uit = ols(np.log(x[doel].values), X, x.datum.dt.strftime("%Y-%m").values)
    uit["namen"], uit["x"] = namen, x
    return uit


OMZET = "batterij_achteraf_per_mw"
MODELLEN = (("basis", OMZET, False, False, "vloot_gw"), ("zonder schokken", OMZET, True, False, "vloot_gw"), ("met tijdtrend", OMZET, False, "trend", "vloot_gw"),
            ("met jaareffecten", OMZET, False, "jaren", "vloot_gw"), ("in logaritmen", OMZET, False, False, "ln_vloot"), ("als aandeel van de piekvraag", OMZET, False, False, "vloot_rel"),
            ("dagspreiding", "spreiding_2u", False, False, "vloot_gw"), ("piekpremie", "piekpremie", False, False, "vloot_gw"), ("daldiepte", "daldiepte", False, False, "vloot_gw"))


def verschiltoets(d):
    """Texas min Californie per dag: gezamenlijke schokken (gasprijs, landelijke trends) vallen weg. Als de vloot de oorzaak is,
    hoort de Texaanse vloot een negatief teken te krijgen en de Californische een positief."""
    from .sa import ols
    k = ["batterij_achteraf_per_mw", "vloot_gw", "vloot_mw", "ln_zon", "ln_last"]
    t, c = (d[d.markt == m].set_index("datum")[k] for m in KORT)
    x = t.join(c, lsuffix="_tx", rsuffix="_ca", how="inner")
    x = x[(x.vloot_mw_tx >= MIN_VLOOT_MW) & (x.vloot_mw_ca >= MIN_VLOOT_MW) & (x.batterij_achteraf_per_mw_tx > 0) & (x.batterij_achteraf_per_mw_ca > 0)].dropna()
    X = np.column_stack([np.ones(len(x)), x.vloot_gw_tx, x.vloot_gw_ca, x.ln_zon_tx, x.ln_zon_ca, x.ln_last_tx, x.ln_last_ca] + [(x.index.month == m).astype(float) for m in range(2, 13)])
    m = ols(np.log(x.batterij_achteraf_per_mw_tx.values / x.batterij_achteraf_per_mw_ca.values), X, x.index.strftime("%Y-%m").values)
    return [{"markt": "Texas min Californie", "model": "verschil tussen de markten", "afhankelijke": "ln omzet Texas - ln omzet Californie", "term": term, "coef": m["b"][i], "se": m["se"][i],
             "t": m["t"][i], "p": m["p"][i], "ci_laag": m["b"][i] - m["ci"][i], "ci_hoog": m["b"][i] + m["ci"][i], "n": m["n"], "clusters": m["G"], "r2": m["r2"]}
            for i, term in ((1, "vloot_gw Texas"), (2, "vloot_gw Californie"))]


def modeltabel(d):
    rijen, basis = [], {}
    for markt in KORT:
        for naam, doel, zonder, trend, vloot in MODELLEN:
            m = schat(d, markt, doel, zonder, trend, vloot)
            if naam == "basis":
                basis[markt] = m
            for i, term in enumerate(m["namen"]):
                if term.startswith(("maand_", "jaar_")) or term == "constante":
                    continue
                rijen.append({"markt": markt, "model": naam, "afhankelijke": "ln " + doel, "term": term, "coef": m["b"][i], "se": m["se"][i], "t": m["t"][i], "p": m["p"][i],
                              "ci_laag": m["b"][i] - m["ci"][i], "ci_hoog": m["b"][i] + m["ci"][i], "n": m["n"], "clusters": m["G"], "r2": m["r2"]})
    return pd.DataFrame(rijen + verschiltoets(d)), basis


def aangepast(m):
    """Opbrengst per dag, teruggerekend naar de omstandigheden van de laatste twaalf maanden (zon, gas, vraag, seizoen)."""
    x, b, namen = m["x"], m["b"], m["namen"]
    X, _ = ontwerp(x)
    i = namen.index("vloot_gw")
    laatste = x.datum > x.datum.max() - pd.Timedelta(days=365)
    rest = np.delete(X, i, axis=1) @ np.delete(b, i)
    return x.assign(aangepast=np.exp(b[i] * x.vloot_gw.values + m["e"] + rest[laatste.values].mean()))


def curve(d, basis):
    rijen, punten = [], []
    for markt, m in basis.items():
        i = m["namen"].index("vloot_gw")
        beta, half = m["b"][i], m["ci"][i]
        x = d[(d.markt == markt)]
        laatste = x[x.datum > x.datum.max() - pd.Timedelta(days=365)]
        anker, nu = laatste.batterij_plan_per_mw.mean() * 365, x.vloot_gw.max()
        for v in np.unique(np.round(np.concatenate([np.linspace(0, 1.5 * nu, 46), [nu]]), 3)):
            f = v - nu                                           # GW meer of minder dan nu
            rijen.append({"markt": markt, "vloot_gw": v, "omzet_per_mw_jaar": anker * np.exp(beta * f), "laag": anker * np.exp(min((beta - half) * f, (beta + half) * f)),
                          "hoog": anker * np.exp(max((beta - half) * f, (beta + half) * f)), "anker": bool(abs(v - round(nu, 3)) < 1e-9), "per_gw": beta, "buiten_waarneming": bool(v > nu + 1e-9)})
        a = aangepast(m)
        schaal = anker / (a[a.datum > a.datum.max() - pd.Timedelta(days=365)].aangepast.mean() * 365)      # van achteraf bezien naar plan op gisteren
        k = a.assign(kwartaal=a.datum.dt.to_period("Q").astype(str)).groupby("kwartaal").agg(dagen=("datum", "size"), vloot_gw=("vloot_gw", "mean"), omzet=("aangepast", "mean"))
        k = k[k.dagen >= 45]
        punten.append(k.assign(markt=markt, omzet_aangepast_per_mw_jaar=k.omzet * 365 * schaal).reset_index()[["markt", "kwartaal", "vloot_gw", "omzet_aangepast_per_mw_jaar"]])
    return pd.DataFrame(rijen), pd.concat(punten, ignore_index=True)


def nl(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def figuren(jaar, krv, punten, model, uit=FIG):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .vis import K, bewaar, kop, punt, stijl
    stijl()
    lijst = []
    # ---- piekpremie en daldiepte per jaar
    fig, assen = plt.subplots(1, 2, figsize=(7.6, 3.5), gridspec_kw={"wspace": 0.28})
    val = {}
    for ax, markt in zip(assen, KORT):
        t = jaar[(jaar.markt == markt) & (jaar.jaar >= 2021)]
        for kolom, kleur, naam in (("piekpremie", K["blauw"], "piekpremie"), ("daldiepte", K["oranje"], "daldiepte")):
            ax.plot(t.jaar, t[kolom], color=kleur, lw=2)
            for x, y in zip(t.jaar, t[kolom]):
                punt(ax, x, y, kleur, groot=6)
        eind = {k: t[k].iloc[-1] for k in ("piekpremie", "daldiepte")}
        ruimte = 0.09 * ax.get_ylim()[1]                         # twee regels tekst per label: houd ze uit elkaar
        midden = (eind["piekpremie"] + eind["daldiepte"]) / 2
        plek = {"piekpremie": max(eind["piekpremie"], midden + ruimte), "daldiepte": min(eind["daldiepte"], midden - ruimte)}
        for kolom in plek:
            ax.text(t.jaar.iloc[-1] + 0.15, plek[kolom], f"{kolom}\n{eind[kolom]:.0f}", va="center", fontsize=9, color=K["inkt2"])
        top = t.loc[t.piekpremie.idxmax()]
        val[markt] = (int(top.jaar), top.piekpremie, t.piekpremie.iloc[-1], t.daldiepte.iloc[-1], t.vloot_gw.iloc[0], t.vloot_gw.iloc[-1])
        ax.set_title(f"{KORT[markt]}: vloot {t.vloot_gw.iloc[0]:.1f} naar {t.vloot_gw.iloc[-1]:.1f} GW".replace(".", ","), loc="left", fontsize=10, color=K["inkt2"])
        ax.set_xlim(2020.7, 2027.6); ax.set_xticks(range(2021, 2027)); ax.set_ylim(0, None)
    assen[0].set_ylabel("euro per MWh")
    tx, ca = val["VS Texas (ERCOT)"], val["VS Californie (CAISO)"]
    per_gw = {(m, t): 1 - np.exp(model[(model.markt == m) & (model.model == t)].coef.iloc[0]) for m in KORT for t in ("piekpremie", "daldiepte")}
    kop(fig, f"De avondpiek verdween: de piekpremie viel {1 - tx[2] / tx[1]:.0%} in Texas en {1 - ca[2] / ca[1]:.0%} in Californie",
        "Piekpremie: de twee duurste uren boven het daggemiddelde. Daldiepte: de twee goedkoopste eronder. Per jaar.",
        "Bron: EIA, gridstatus.io, CAISO OASIS; eigen berekening (fact_verzadiging_jaar_VZ). 2026 loopt tot half november.")
    bewaar(fig, uit, "11_piek_en_dal.png", f"Deze grafiek laat zien dat de piekpremie in Texas daalde van {tx[1]:.0f} euro per MWh in {tx[0]} naar {tx[2]:.0f} in 2026 en in Californie van {ca[1]:.0f} "
           f"in {ca[0]} naar {ca[2]:.0f}, terwijl de vloot in beide markten naar ongeveer 12 GW groeide. In het model daalt de piekpremie per GW erbij met {per_gw[('VS Texas (ERCOT)', 'piekpremie')]:.0%} (Texas) en "
           f"{per_gw[('VS Californie (CAISO)', 'piekpremie')]:.0%} (Californie), de daldiepte met {per_gw[('VS Texas (ERCOT)', 'daldiepte')]:.0%} en {per_gw[('VS Californie (CAISO)', 'daldiepte')]:.0%}. "
           "De belangrijkste conclusie is: de waarde verdwijnt vooral uit de avondpiek, veel minder uit het middagdal.", lijst)
    # ---- curve per GW
    fig, assen = plt.subplots(1, 2, figsize=(7.6, 3.7), gridspec_kw={"wspace": 0.28})
    tekst = {}
    for ax, markt in zip(assen, KORT):
        c, p = krv[krv.markt == markt].sort_values("vloot_gw"), punten[punten.markt == markt]
        binnen, buiten = c[~c.buiten_waarneming], c[c.buiten_waarneming | c.anker]
        ax.fill_between(c.vloot_gw, c.laag / 1000, c.hoog / 1000, color=K["lichtblauw"], alpha=0.6, lw=0, label="95%-interval")
        ax.plot(binnen.vloot_gw, binnen.omzet_per_mw_jaar / 1000, color=K["blauw"], lw=2, label="model")
        ax.plot(buiten.vloot_gw, buiten.omzet_per_mw_jaar / 1000, color=K["blauw"], lw=2, ls=(0, (3, 2)), label="doorgetrokken")
        ax.plot(p.vloot_gw, p.omzet_aangepast_per_mw_jaar / 1000, "o", ms=5, color=K["vlak"], mec=K["gedempt"], mew=1.3, label="kwartaal, omgerekend")
        a = c[c.anker].iloc[0]
        punt(ax, a.vloot_gw, a.omzet_per_mw_jaar / 1000, K["blauw"], groot=9)
        ax.annotate(f"nu: {a.vloot_gw:.1f} GW\n{a.omzet_per_mw_jaar / 1000:.0f} duizend euro".replace(".", ","), (a.vloot_gw, a.omzet_per_mw_jaar / 1000), xytext=(-4, 22), textcoords="offset points",
                    fontsize=9, color=K["inkt2"], ha="center")
        ax.set_title(KORT[markt], loc="left", fontsize=10, color=K["inkt2"]); ax.set_xlabel("batterijvloot (GW)")
        ax.set_xlim(0, c.vloot_gw.max()); ax.set_ylim(0, np.percentile(np.concatenate([p.omzet_aangepast_per_mw_jaar.values, c.omzet_per_mw_jaar.values]), 97) / 1000 * 1.15)
        tekst[markt] = (1 - np.exp(a.per_gw), a.vloot_gw, a.omzet_per_mw_jaar)
    assen[0].set_ylabel("duizend euro per MW per jaar"); assen[1].legend(loc="upper right", fontsize=8.5)
    tx, ca = tekst["VS Texas (ERCOT)"], tekst["VS Californie (CAISO)"]
    kop(fig, f"Per GW erbij {tx[0]:.0%} minder opbrengst per MW in Texas en {ca[0]:.0%} in Californie, in het basismodel",
        "Batterij van twee uur op de dagmarkt, plan op gisteren. Model bij zon, gasprijs, vraag en seizoen van de laatste twaalf maanden.",
        "Bron: EIA, gridstatus.io, CAISO OASIS; eigen model (fact_verzadiging_curve_VZ). Verband in de tijd, geen proef; zie de gevoeligheidsruns.")
    bewaar(fig, uit, "12_verzadiging_per_gw.png", f"Deze grafiek laat zien dat een batterij van twee uur in Texas nu {tx[2] / 1000:.0f} duizend euro per MW per jaar verdient bij een vloot van {nl(tx[1])} GW en in "
           f"Californie {ca[2] / 1000:.0f} duizend bij {nl(ca[1])} GW, en dat elke GW erbij in het basismodel {tx[0]:.0%} respectievelijk {ca[0]:.0%} kost. De belangrijkste conclusie is: "
           "reken in een batterijcase met een opbrengst per MW die daalt naarmate de vloot groeit, en behandel de precieze helling als onzeker.", lijst)
    with open(os.path.join(uit, "bijschriften_verzadiging.txt"), "w", encoding="utf-8") as fh:
        for naam, t in lijst:
            fh.write(f"{naam}\n{t}\n\n")
    return lijst


def main(data=DATA, uit=DATA, fig=FIG):
    d = laad(data)
    jaar, kwartaal = jaartabel(d), kwartaaltabel(d)
    model, basis = modeltabel(d)
    for markt, m in basis.items():                               # hoe sterk loopt de vloot gelijk op met de tijd?
        x = m["x"]
        model.loc[model.markt == markt, "correlatie_vloot_tijd"] = np.corrcoef(x.vloot_gw, (x.datum - x.datum.min()).dt.days)[0, 1]
    krv, punten = curve(d, basis)
    for naam, t in (("jaar", jaar), ("kwartaal", kwartaal), ("model", model), ("curve", krv), ("punten", punten)):
        t.round(4).to_csv(os.path.join(uit, f"fact_verzadiging_{naam}_VZ.csv"), index=False)
    lijst = figuren(jaar, krv, punten, model, fig)
    v = model[model.term.str.contains("vloot")]
    print(v[["markt", "model", "term", "coef", "se", "p", "n", "r2"]].round(3).to_string(index=False))
    return jaar, model, krv


if __name__ == "__main__":
    main()
