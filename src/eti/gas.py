"""Gasprijs als verklaring van 'het jaar' en als invoer van buiten voor de prognose.

Waarom: in de eerdere analyses verklaarde het jaar meer dan het land, en de prognose kende alleen het verleden van de
stroomprijs zelf. Dit pakket zet er een oorzaak naast die van buiten komt: de Europese gasprijs.

Bron: maandreeksen van FRED, zonder sleutel. Gasprijs: IMF, 'Global price of Natural gas, EU' (PNGASEUUSDM, dollar per
MMBtu). Koers: Federal Reserve, EXUSEU (dollar per euro). Omrekening: euro per MWh = dollar per MMBtu / koers / 0,29307.
De momentopname staat in data/extern/gasprijs_fred.csv; `python3 -m eti.gas ververs` haalt eerst de laatste stand op.
De twee laatste maanden staan nog niet in FRED en zijn voorlopig (zie VOORLOPIG).

Schrijft powerbi/data/fact_gasprijs_maand.csv en fact_gas_{doorwerking,jaareffect,capture,toets,prognose}_GAS.csv
en twee figuren in reports/analyse/fig.   Gebruik:  PYTHONPATH=src python3 -m eti.gas [ververs]
"""
import io
import os
import sys
import urllib.request

import numpy as np
import pandas as pd

DATA, FIG, SNAPSHOT = "powerbi/data", "reports/analyse/fig", "data/extern/gasprijs_fred.csv"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={reeks}"
MWH_PER_MMBTU = 0.29307107
VOORLOPIG = {"2026-10": (88.3, "IMF-reeks oktober 2026 (28,98 dollar per MMBtu, via cbonds), koers 1,1198"),
             "2026-11": (87.0, "gemiddelde van de dagprijzen tot half november, indicatie")}
# Gaspaden voor 2027 in euro per MWh. Termijnmarkt: van het niveau van nu (85) in een rechte lijn naar 66 eind 2027,
# het pad dat de Europese Commissie in de herfstraming 2026 uit de termijnprijzen afleest.
PADEN = {"termijnmarkt (85 nu, 66 eind 2027)": [85 - 19 * m / 12 for m in range(1, 13)], "gas blijft op het niveau van nu (87)": [87.0] * 12,
         "gas terug naar begin 2026 (30)": [30.0] * 12}
DUITS_CAL27 = (144.71, "EEX Duitse basislast 2027, slot 6 november 2026")
UITKOMSTEN = {"gem_prijs": "gemiddelde prijs", "dagspreiding": "dagspreiding", "batterij_per_mw": "batterij 2 uur", "negatieve_uren": "negatieve uren", "capture_zon": "capture rate zon"}


def ververs(pad=SNAPSHOT):
    """Haalt de twee reeksen op bij FRED en werkt de momentopname bij. Zonder netwerk blijft de momentopname staan."""
    try:
        delen = {}
        for kolom, reeks in (("eu_gas_usd_mmbtu", "PNGASEUUSDM"), ("usd_per_eur", "EXUSEU")):
            with urllib.request.urlopen(FRED.format(reeks=reeks), timeout=20) as antwoord:
                t = pd.read_csv(io.StringIO(antwoord.read().decode("utf-8")))
            t.columns = ["periode", kolom]
            t[kolom] = pd.to_numeric(t[kolom], errors="coerce")
            delen[kolom] = t.assign(periode=t.periode.str[:7]).set_index("periode")[kolom]
        nieuw = pd.concat(delen, axis=1).loc["2018-01":].reset_index().assign(bron="FRED (IMF PNGASEUUSDM; Fed EXUSEU)")
        nieuw.round(4).to_csv(pad, index=False)
        print(f"  momentopname bijgewerkt: {len(nieuw)} maanden tot en met {nieuw.periode.iloc[-1]}")
        return True
    except Exception as fout:                                    # geen netwerk, of FRED weigert: de momentopname volstaat
        print(f"  niet ververst ({type(fout).__name__}): de momentopname blijft staan")
        return False


def maandreeks(pad=SNAPSHOT):
    g = pd.read_csv(pad)
    g["eu_gas_eur_mwh"] = g.eu_gas_usd_mmbtu / g.usd_per_eur / MWH_PER_MMBTU
    g["voorlopig"] = False
    for periode, (waarde, bron) in VOORLOPIG.items():
        if periode in set(g.periode):
            leeg = (g.periode == periode) & g.eu_gas_eur_mwh.isna()
            g.loc[leeg, ["eu_gas_eur_mwh", "voorlopig", "bron"]] = [waarde, True, bron]
        else:
            g = pd.concat([g, pd.DataFrame([{"periode": periode, "eu_gas_eur_mwh": waarde, "voorlopig": True, "bron": bron}])], ignore_index=True)
    g = g.dropna(subset=["eu_gas_eur_mwh"]).sort_values("periode").reset_index(drop=True)
    g["jaar"], g["maand"] = g.periode.str[:4].astype(int), g.periode.str[5:7].astype(int)
    return g


def maandprijzen(data=DATA):
    """Maandprijzen per land met de gasprijs erbij; de laatste maand van de tabel is onvolledig en doet niet mee."""
    m = pd.read_csv(os.path.join(data, "fact_land_maand.csv"))
    laatste = m[["jaar", "maand"]].apply(tuple, axis=1).max()
    m = m[m[["jaar", "maand"]].apply(tuple, axis=1) < laatste]
    return m.merge(maandreeks()[["jaar", "maand", "eu_gas_eur_mwh", "voorlopig"]], on=["jaar", "maand"], how="inner")


def maandmodel(m):
    """prijs = a + b * gas + maandeffect. Geeft (coefficienten, ontwerpmatrix-functie)."""
    def X(t):
        return np.column_stack([np.ones(len(t)), t.eu_gas_eur_mwh.values] + [(t.maand == k).values.astype(float) for k in range(2, 13)])
    b = np.linalg.lstsq(X(m), m.gem_prijs.values, rcond=None)[0]
    return b, X


def doorwerking(data=DATA):
    from .sa import ols
    rijen = []
    for land, t in maandprijzen(data).groupby("land"):
        _, X = maandmodel(t)
        u = ols(t.gem_prijs.values, X(t), t.jaar.values)
        rijen.append({"land": land, "euro_stroom_per_euro_gas": u["b"][1], "se": u["se"][1], "p": u["p"][1], "r2": u["r2"], "maanden": u["n"],
                      "correlatie": float(np.corrcoef(t.gem_prijs, t.eu_gas_eur_mwh)[0, 1])})
    return pd.DataFrame(rijen).sort_values("euro_stroom_per_euro_gas", ascending=False)


def r2_binnen(y, X, groep):
    """R2 nadat het gemiddelde per zone eraf is: wat verklaren de kenmerken van de beweging binnen een zone?"""
    y = y - y.groupby(groep).transform("mean")
    X = (X - X.groupby(groep).transform("mean")).values
    rest = y.values - X @ np.linalg.lstsq(X, y.values, rcond=None)[0]
    return float(1 - rest.var() / y.values.var())


def jaareffect(data=DATA):
    z = pd.read_csv(os.path.join(data, "fact_zonejaar_DA.csv"))
    gas = maandreeks().groupby("jaar").eu_gas_eur_mwh.mean().rename("gas")
    z = z.merge(gas, on="jaar")
    rijen = []
    for kolom, naam in UITKOMSTEN.items():
        t = z.dropna(subset=[kolom, "aandeel_zon_pct", "aandeel_wind_pct"])
        jaren = pd.get_dummies(t.jaar, drop_first=True, dtype=float)
        r_jaar, r_gas = r2_binnen(t[kolom], jaren, t.biedzone), r2_binnen(t[kolom], t[["gas"]], t.biedzone)
        r_mix = r2_binnen(t[kolom], t[["gas", "aandeel_zon_pct", "aandeel_wind_pct"]], t.biedzone)
        helling = np.polyfit(t.gas - t.groupby("biedzone").gas.transform("mean"), t[kolom] - t.groupby("biedzone")[kolom].transform("mean"), 1)[0]
        rijen.append({"uitkomst": kolom, "naam": naam, "zonejaren": len(t), "r2_jaareffecten": r_jaar, "r2_alleen_gas": r_gas, "r2_gas_zon_wind": r_mix,
                      "aandeel_van_jaareffect": r_gas / r_jaar if r_jaar else np.nan, "per_euro_gas": helling})
    return pd.DataFrame(rijen)


def capture_met_gas(data=DATA):
    """Het capture-model uit eti.sa, een keer met jaareffecten en een keer met de gasprijs op de plek van het jaar."""
    from . import sa
    d = sa.regressiedata(data).merge(maandreeks().groupby("jaar").eu_gas_eur_mwh.mean().rename("gas"), on="jaar")
    jaren = sorted(d.jaar.unique())
    kern = [np.ones(len(d)), d.aandeel_zon_pct.values, d.buur_zon_pct.values]
    varianten = {"met jaareffecten": (kern + [(d.jaar == j).values.astype(float) for j in jaren[1:]], ["constante", "eigen zon (pp)", "zon bij de buren (pp)"] + [f"jaar {j}" for j in jaren[1:]]),
                 "met de gasprijs": (kern + [d.gas.values], ["constante", "eigen zon (pp)", "zon bij de buren (pp)", "gasprijs (euro per MWh)"]),
                 "zonder jaar of gas": (kern, ["constante", "eigen zon (pp)", "zon bij de buren (pp)"])}
    rijen = []
    for naam, (X, namen) in varianten.items():
        u = sa.ols(d.capture_zon.values, np.column_stack(X), d.iso3.values)
        for i, term in enumerate(namen):
            if not term.startswith(("jaar ", "constante")):
                rijen.append({"model": naam, "term": term, "coef": u["b"][i], "se": u["se"][i], "t": u["t"][i], "p": u["p"][i], "r2": u["r2"], "n": u["n"], "landen": u["G"]})
    return pd.DataFrame(rijen)


def toets(nl):
    """Voorspel elk jaar met een model dat alleen de jaren ervoor zag, een keer met de echte gasprijs van dat jaar erbij
    (wat je weet als je de gasprijs kent) en een keer zonder (vorig jaar herhaald)."""
    rijen = []
    for jaar in range(2022, int(nl.jaar.max()) + 1):
        oud, nieuw = nl[nl.jaar < jaar], nl[nl.jaar == jaar]
        b, X = maandmodel(oud)
        echt, met_gas = nieuw.gem_prijs.mean(), (X(nieuw) @ b).mean()
        vorig = oud[(oud.jaar == jaar - 1) & oud.maand.isin(nieuw.maand)].gem_prijs.mean()
        rijen.append({"jaar": jaar, "maanden": len(nieuw), "gemeten": echt, "met_gasprijs": met_gas, "fout_met_gas_pct": (met_gas - echt) / echt * 100,
                      "vorig_jaar": vorig, "fout_vorig_jaar_pct": (vorig - echt) / echt * 100, "gas_per_mwh_stroom": b[1]})
    return pd.DataFrame(rijen)


def prognose(nl, t):
    b, X = maandmodel(nl)
    afw = np.abs(t.fout_met_gas_pct).values / 100
    marge = float(np.sort(afw)[-2]) if len(afw) > 2 else float(afw.max())          # op een na grootste fout uit de terugtoets
    rijen = []
    for naam, pad in PADEN.items():
        p = pd.DataFrame({"maand": range(1, 13), "eu_gas_eur_mwh": pad})
        prijs = float((X(p) @ b).mean())
        rijen.append({"scenario": naam, "gas_2027_eur_mwh": float(np.mean(pad)), "stroom_2027_eur_mwh": prijs, "laag": prijs * (1 - marge), "hoog": prijs * (1 + marge)})
    snij = float((X(pd.DataFrame({"maand": range(1, 13), "eu_gas_eur_mwh": [0.0] * 12})) @ b).mean())
    rijen.append({"scenario": f"gasprijs die past bij {DUITS_CAL27[1]}", "gas_2027_eur_mwh": (DUITS_CAL27[0] - snij) / b[1], "stroom_2027_eur_mwh": DUITS_CAL27[0]})
    uit = pd.DataFrame(rijen)
    uit["euro_stroom_per_euro_gas"], uit["sokkel_eur_mwh"], uit["marge_pct"] = b[1], snij, marge * 100
    return uit


def figuren(nl, pr, je, uit=FIG):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .vis import K, bewaar, kop, punt, stijl
    stijl()
    lijst = []
    b, sokkel = pr.euro_stroom_per_euro_gas.iloc[0], pr.sokkel_eur_mwh.iloc[0]
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    oud, nu = nl[nl.jaar < 2026], nl[nl.jaar == 2026]
    ax.plot(oud.eu_gas_eur_mwh, oud.gem_prijs, "o", ms=5, color=K["vlak"], mec=K["gedempt"], mew=1.2, label="maand, 2019-2025")
    ax.plot(nu.eu_gas_eur_mwh, nu.gem_prijs, "o", ms=6.5, color=K["oranje"], mec=K["vlak"], mew=1.2, label="maand, 2026", zorder=5)
    x = np.array([0, nl.eu_gas_eur_mwh.max()])
    ax.plot(x, sokkel + b * x, color=K["blauw"], lw=2, label="model")
    for (_, r), (dx, dy) in zip(pr.iloc[:3].iterrows(), ((16, -34), (18, -10), (14, -22))):
        punt(ax, r.gas_2027_eur_mwh, r.stroom_2027_eur_mwh, K["blauw"], groot=10, open_=True)
        ax.annotate(f"2027, {r.scenario.split(' (')[0]}: {r.stroom_2027_eur_mwh:.0f}", (r.gas_2027_eur_mwh, r.stroom_2027_eur_mwh), xytext=(dx, dy), textcoords="offset points", fontsize=9, color=K["inkt2"])
    ax.set_xlabel("gasprijs (euro per MWh)"); ax.set_ylabel("stroomprijs Nederland (euro per MWh)")
    ax.set_xlim(0, None); ax.set_ylim(0, None); ax.legend(loc="upper left", fontsize=9)
    r2 = float(np.corrcoef(nl.gem_prijs, nl.eu_gas_eur_mwh)[0, 1] ** 2)
    kop(fig, f"Een euro meer voor gas is {b:.2f} euro meer voor stroom".replace(".", ","),
        f"Maandgemiddelden Nederland, 2019 tot en met oktober 2026. De gasprijs alleen verklaart {r2:.0%} van de maandprijs.",
        "Bron: Energy-Charts (stroom), IMF en Federal Reserve via FRED (gas); eigen model (fact_gas_prognose_GAS).")
    bewaar(fig, uit, "13_gas_en_stroomprijs.png", f"Deze grafiek laat zien dat de Nederlandse maandprijs van stroom de gasprijs volgt: {b:.2f} euro per MWh stroom voor elke euro per MWh gas, "
           f"bovenop een sokkel van {sokkel:.0f} euro. De belangrijkste conclusie is: wie de stroomprijs van 2027 wil ramen, heeft eerst een mening over gas nodig.".replace(".", ",", 1), lijst)

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    y = np.arange(len(je))[::-1]
    for dy, kolom, kleur, naam in ((0.26, "r2_jaareffecten", K["grijs"], "jaareffecten"), (0, "r2_alleen_gas", K["blauw"], "alleen gasprijs"), (-0.26, "r2_gas_zon_wind", K["aqua"], "gasprijs, zon en wind")):
        ax.barh(y + dy, je[kolom], height=0.24, color=kleur, label=naam)
        for yy, v in zip(y + dy, je[kolom]):
            ax.text(v + 0.012, yy, f"{v:.0%}", va="center", fontsize=8.5, color=K["inkt2"])
    ax.set_yticks(y); ax.set_yticklabels(je.naam); ax.set_xlim(0, 1.42); ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xlabel("verklaard deel van de beweging binnen een zone", loc="left")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}")); ax.legend(loc="center right", fontsize=9)
    p = je.set_index("uitkomst")
    deel = p.loc["gem_prijs", "aandeel_van_jaareffect"]
    kop(fig, f"Het jaar is vooral gas: {'vrijwel het hele' if deel > 0.97 else f'{deel:.0%} van het'} jaareffect in de prijs, {p.loc['dagspreiding', 'aandeel_van_jaareffect']:.0%} in de dagspreiding",
        "Hoeveel van de beweging van jaar op jaar binnen een biedzone verklaart elk model? 37 zones, 2019-2026.",
        "Bron: Energy-Charts, Ember, FRED; eigen berekening (fact_gas_jaareffect_GAS).")
    bewaar(fig, uit, "14_jaareffect_is_gas.png", f"Deze grafiek laat zien dat de gasprijs alleen {p.loc['gem_prijs', 'r2_alleen_gas']:.0%} van de jaarbeweging in de prijs verklaart, tegen "
           f"{p.loc['gem_prijs', 'r2_jaareffecten']:.0%} voor losse jaareffecten, en dat dit voor de capture rate van zon veel minder is "
           f"({p.loc['capture_zon', 'r2_alleen_gas']:.0%} tegen {p.loc['capture_zon', 'r2_jaareffecten']:.0%}). De belangrijkste conclusie is: prijs en spreiding volgen gas, de waarde van zon volgt iets anders.", lijst)
    with open(os.path.join(uit, "bijschriften_gas.txt"), "w", encoding="utf-8") as fh:
        for naam, tekst in lijst:
            fh.write(f"{naam}\n{tekst}\n\n")
    return lijst


def main(data=DATA, fig=FIG, opdracht=""):
    if opdracht == "ververs":
        ververs()
    g = maandreeks()
    g[["periode", "jaar", "maand", "eu_gas_usd_mmbtu", "usd_per_eur", "eu_gas_eur_mwh", "voorlopig", "bron"]].round(4).to_csv(os.path.join(data, "fact_gasprijs_maand.csv"), index=False)
    m = maandprijzen(data)
    nl = m[m.land == "Nederland"].sort_values(["jaar", "maand"])
    dw, je, cap, t = doorwerking(data), jaareffect(data), capture_met_gas(data), toets(nl)
    pr = prognose(nl, t)
    for naam, tabel in (("doorwerking", dw), ("jaareffect", je), ("capture", cap), ("toets", t), ("prognose", pr)):
        tabel.round(4).to_csv(os.path.join(data, f"fact_gas_{naam}_GAS.csv"), index=False)
    figuren(nl, pr, je, fig)
    return g, dw, je, cap, t, pr


if __name__ == "__main__":
    uit = main(opdracht=sys.argv[1] if len(sys.argv) > 1 else "")
    pd.set_option("display.width", 250)
    for tabel in uit[2:]:
        print(tabel.round(3).to_string(index=False)); print()
