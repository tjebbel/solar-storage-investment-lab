"""Statistische analyse (_SA): hypothesetoetsen, A/B-test, regressie en cohorten.

Vraag: is beleggen in de energietransitie aantrekkelijk voor rendement en impact? De toetsen splitsen dat in
deelvragen die de data kan beantwoorden (zon, wind en opslag tegen de kapitaalkosten; waardedaling van zon; vermeden
CO2). De A/B-test vergelijkt twee stuurstrategieen van de batterij per dag. De regressie verklaart de capture rate
van zon; de cohorten volgen zones vanaf het jaar waarin zon 5% van de opwek haalde.

Uitvoer: tabellen met _SA in de naam. De prognose staat in eti.prognose.
Gebruik:  PYTHONPATH=src python3 -m eti.sa [datamap] [uitvoermap]
Nodig: pandas, numpy, scipy, scikit-learn.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

from . import da

DATA = "powerbi/data"
WACC = 0.05                       # kapitaalkosten Nederland (dim_regio)
STREEF = 0.08                     # rendementseis voor marktrisico zonder contract
NORMAAL = (2023, 2024, 2025)      # jaren zonder prijsschok
SCHOK = (2021, 2022, 2026)        # jaren met een gemiddelde Nederlandse prijs boven EUR 100 per MWh
LCOE = {"Noordwest-Europa": 67.39, "Zuid-Europa": 51.09}      # fact_regio_jaar 2025 (Nederland, Spanje)
KANDIDATEN = ["aandeel_zon_pct", "buur_zon_pct", "aandeel_wind_pct", "aandeel_waterkracht_pct", "aandeel_kern_pct",
              "aandeel_gas_pct", "log_prijs"]


# ------------------------------------------------------------------------------------------------- hulpfuncties
def holm(p):
    """Holm-correctie voor meervoudig toetsen: aangepaste p-waarden in de oorspronkelijke volgorde."""
    p = np.asarray(p, float)
    adj, hoogste = np.empty(len(p)), 0.0
    for plek, i in enumerate(np.argsort(p)):
        hoogste = max(hoogste, (len(p) - plek) * p[i])
        adj[i] = min(1.0, hoogste)
    return adj


def bootstrap(x, functie=np.median, n=10_000, seed=1):
    """95%-interval van een kengetal door opnieuw trekken met teruglegging."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    w = functie(rng.choice(x, (n, len(x))), axis=1)
    return float(np.quantile(w, 0.025)), float(np.quantile(w, 0.975))


def wilson(k, n, z=1.96):
    """Betrouwbaarheidsinterval van een aandeel (Wilson)."""
    if n == 0:
        return np.nan, np.nan
    p, d = k / n, 1 + z * z / n
    m, h = (p + z * z / (2 * n)) / d, z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return m - h, m + h


def een_steekproef(naam, x, drempel, h0, h1):
    """H0: de mediaan ligt op of onder de drempel. Wilcoxon-rangtekentoets (eenzijdig), tekentoets als controle."""
    x = np.asarray(x, float)
    d = x - drempel
    w = stats.wilcoxon(d, alternative="greater")
    r = stats.rankdata(np.abs(d))
    boven = int((d > 0).sum())
    lo, hi = bootstrap(x)
    return {"toets": naam, "methode": "Wilcoxon-rangtekentoets, eenzijdig", "h0": h0, "h1": h1, "n": len(x),
            "statistiek": float(w.statistic), "p": float(w.pvalue),
            "p_controle": float(stats.binomtest(boven, len(x), 0.5, alternative="greater").pvalue),
            "effectgrootte": float((r[d > 0].sum() - r[d < 0].sum()) / r.sum()), "effectmaat": "rang-biseriele correlatie",
            "schatting": float(np.median(x)), "ci_laag": lo, "ci_hoog": hi, "drempel": drempel,
            "aandeel_boven_drempel": boven / len(x), "normaliteit_p": float(stats.shapiro(d).pvalue)}


def gepaard(naam, voor, na, h0, h1, eenzijdig="less"):
    """Gepaarde vergelijking (zelfde zones of jaren). Wilcoxon als hoofdtoets, gepaarde t-toets als controle."""
    voor, na = np.asarray(voor, float), np.asarray(na, float)
    d = na - voor
    lo, hi = stats.t.interval(0.95, len(d) - 1, loc=d.mean(), scale=stats.sem(d))
    return {"toets": naam, "methode": "Wilcoxon gepaard, eenzijdig", "h0": h0, "h1": h1, "n": len(d),
            "statistiek": float(stats.wilcoxon(d, alternative=eenzijdig).statistic),
            "p": float(stats.wilcoxon(d, alternative=eenzijdig).pvalue),
            "p_controle": float(stats.ttest_rel(na, voor, alternative=eenzijdig).pvalue),
            "effectgrootte": float(d.mean() / d.std(ddof=1)), "effectmaat": "Cohen's d (gepaard)",
            "schatting": float(d.mean()), "ci_laag": float(lo), "ci_hoog": float(hi), "drempel": 0.0,
            "aandeel_boven_drempel": float((d > 0).mean()), "normaliteit_p": float(stats.shapiro(d).pvalue)}


# ---------------------------------------------------------------------------------------------------- 1 toetsen
def irr_per_zone(data=DATA, jaren=NORMAAL):
    """Mediaan van de IRR per zone over de gekozen jaren, voor zon en wind (marktprijs, zonder contract) en voor de
    batterij van twee uur op de dagmarkt. Een lege IRR (investering komt nooit terug) telt als -100%."""
    t = pd.read_csv(os.path.join(data, "fact_tech_land.csv"))
    t = t[t.jaar.isin(jaren)].assign(irr=lambda d: d.irr_merchant.fillna(-1.0))
    uit = {tech: g.groupby("land").irr.median() for tech, g in t.groupby("technologie")}
    f = pd.read_csv(os.path.join(data, "fact_flex_land.csv")).query("uren_opslag == 2")
    f = f[f.jaar.isin(jaren)].assign(irr=lambda d: d.irr_realistisch.fillna(-1.0))
    uit["batterij"] = f.groupby("land").irr.median()
    return uit


def toetsen(data=DATA):
    """De familie toetsen bij de vraag 'aantrekkelijk voor rendement en impact', met Holm-correctie."""
    rijen = []
    for jaren, label, familie in ((NORMAAL, "gewone jaren 2023-2025", "hoofdtoets"), (SCHOK, "schokjaren 2021, 2022, 2026", "gevoeligheid")):
        per = irr_per_zone(data, jaren)
        for tech, naam in (("zon", "Zon"), ("wind", "Wind"), ("batterij", "Batterij 2 uur, dagmarkt")):
            rijen.append(een_steekproef(f"{naam}: IRR boven kapitaalkosten ({label})", per[tech].values, WACC,
                                        f"mediaan IRR van {naam.lower()} is hooguit {WACC:.0%}", f"mediaan IRR is hoger dan {WACC:.0%}"))
            rijen[-1].update({"aandeel_boven_streefrendement": float((per[tech] > STREEF).mean()), "familie": familie})
    per = irr_per_zone(data, NORMAAL)
    samen = pd.concat([per["zon"].rename("zon"), per["wind"].rename("wind")], axis=1).dropna()
    samen = samen[(samen > -1).all(axis=1)]                      # zonder zones waar de investering nooit terugkomt
    rijen.append(gepaard("Wind rendeert beter dan zon (2023-2025, zelfde landen)", samen.zon, samen.wind,
                         "wind en zon rendeeren gelijk", "wind rendeert hoger dan zon", "greater"))
    p = da.paneel(data)
    c = p[p.capture_zon.between(0, 2)].pivot(index="biedzone", columns="jaar", values="capture_zon")[[2019, 2025]].dropna()
    rijen.append(gepaard("Capture rate zon lager in 2025 dan in 2019 (zelfde zones)", c[2019], c[2025],
                         "de capture rate is niet gedaald", "de capture rate is gedaald"))
    nl = pd.read_csv(os.path.join(data, "fact_nl_jaar.csv"))
    vroeg, laat = nl[nl.jaar <= 2022].co2_vermeden_uur, nl[nl.jaar >= 2023].co2_vermeden_uur
    u = stats.mannwhitneyu(laat, vroeg, alternative="less")
    lo, hi = laat.min() / vroeg.mean(), laat.max() / vroeg.mean()   # spreiding van de latere jaren t.o.v. het eerdere gemiddelde
    rijen.append({"toets": "Vermeden CO2 per jaar lager in 2023-2026 dan in 2019-2022 (Nederland)", "methode": "Mann-Whitney, eenzijdig",
                  "h0": "vermeden CO2 is niet gedaald", "h1": "vermeden CO2 is gedaald", "n": len(nl), "statistiek": float(u.statistic),
                  "p": float(u.pvalue), "p_controle": float(stats.kendalltau(nl.jaar, nl.co2_vermeden_uur).pvalue),
                  "effectgrootte": float(1 - 2 * u.statistic / (len(vroeg) * len(laat))), "effectmaat": "rang-biseriele correlatie",
                  "schatting": float(laat.mean() / vroeg.mean() - 1), "ci_laag": lo - 1, "ci_hoog": hi - 1, "drempel": 0.0,
                  "aandeel_boven_drempel": np.nan, "normaliteit_p": np.nan})
    rijen.append(gepaard("Vermeden CO2: uurmethode lager dan jaargemiddelde (Nederland, 8 jaren)", nl.co2_vermeden_jaargem,
                         nl.co2_vermeden_uur, "beide methoden geven hetzelfde", "de uurmethode geeft minder vermeden CO2"))
    t = pd.DataFrame(rijen)
    t["familie"] = t.familie.fillna("hoofdtoets")
    hoofd = t.familie == "hoofdtoets"                             # de correctie geldt voor de zeven hoofdtoetsen
    t.loc[hoofd, "p_holm"] = holm(t.loc[hoofd, "p"])
    t["h0_verworpen"] = np.where(hoofd, t.p_holm < 0.05, t.p < 0.05)
    return t


# ------------------------------------------------------------------------------------------------------ 2 A/B
def break_even_dag(doel=STREEF):
    """Omzet per MW per dag waarbij de batterij (EUR 560 per kW, 15 jaar, zonder netkosten) het streefrendement haalt."""
    from . import volledige_case as vc
    laag, hoog = 10_000.0, 400_000.0
    for _ in range(60):
        mid = (laag + hoog) / 2
        laag, hoog = (mid, hoog) if (vc.irr(mid, 0) or -1) < doel else (laag, mid)
    return hoog / 365


def ab_dagreeksen(data=DATA):
    """Dagomzet per MW: A volgt het dagmarktplan, B stuurt bij op de onbalansprijs van een kwartier eerder (variant per
    jaar vooraf gekozen, zoals in fact_onbalans_regel). Beide strategieen zijn voor elke dag doorgerekend."""
    from . import onbalansregel as ob
    df = ob.lees(data)
    schema, geen = ob.dagmarktschema(df), np.zeros(len(df), dtype=bool)
    kd, ko, st = ob.simuleer_gecombineerd(df, schema, geen, geen)
    dag = pd.DataFrame({"a": ob.per_dag(df, kd + ko, st).kas})
    regel = pd.read_csv(os.path.join(data, "fact_onbalans_regel.csv"))
    keuze = regel[(regel.regel == "Dagmarkt met bijsturen") & (regel.vertraging_kwartieren == 1) & regel.vooraf_gekozen]
    keuze = keuze.set_index("jaar").variant
    reeks = {}
    for variant in keuze.unique():
        laag, hoog = (int(v) / 100 for v in variant.split("/"))
        laad, ontlaad = ob.signalen_kwantiel(df, laag, hoog, 1)
        kd, ko, st = ob.simuleer_gecombineerd(df, schema, laad, ontlaad, 2.0)
        reeks[variant] = ob.per_dag(df, kd + ko, st).kas
    dag["datum"] = pd.to_datetime(dag.index)
    dag["jaar"] = dag.datum.dt.year
    dag["variant"] = dag.jaar.map(keuze)
    dag["b"] = [reeks[v].get(d, np.nan) if isinstance(v, str) else np.nan for d, v in zip(dag.index, dag.variant)]
    return dag.dropna(subset=["a", "b"]).reset_index(drop=True)


def vergelijk(a, b, drempel=None):
    """Twee onafhankelijke groepen: verschil in gemiddelde (Welch), Mann-Whitney, effectgrootte en eventueel conversie."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = stats.ttest_ind(b, a, equal_var=False)
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    ci = t.confidence_interval(0.95)
    sd = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    uit = {"n_a": len(a), "n_b": len(b), "gem_a": a.mean(), "gem_b": b.mean(), "verschil": b.mean() - a.mean(),
           "relatief": b.mean() / a.mean() - 1 if a.mean() else np.nan, "ci_laag": ci.low, "ci_hoog": ci.high, "p": t.pvalue,
           "p_mannwhitney": stats.mannwhitneyu(b, a).pvalue, "cohen_d": (b.mean() - a.mean()) / sd if sd else np.nan,
           "standaardfout": se}
    if drempel is not None:
        ka, kb = int((a >= drempel).sum()), int((b >= drempel).sum())
        pa, pb, pp = ka / len(a), kb / len(b), (ka + kb) / (len(a) + len(b))
        z = (pb - pa) / np.sqrt(pp * (1 - pp) * (1 / len(a) + 1 / len(b))) if 0 < pp < 1 else 0.0
        h = 1.96 * np.sqrt(pa * (1 - pa) / len(a) + pb * (1 - pb) / len(b))
        uit.update({"conversie_a": pa, "conversie_b": pb, "conversie_verschil": pb - pa, "conversie_relatief": pb / pa - 1 if pa else np.nan,
                    "conversie_ci_laag": pb - pa - h, "conversie_ci_hoog": pb - pa + h, "conversie_p": 2 * stats.norm.sf(abs(z))})
    return {k: float(v) for k, v in uit.items()}


def onderscheidend(n_a, n_b, d, alfa=0.05):
    """Achteraf berekend onderscheidend vermogen bij effectgrootte d, en het kleinste effect dat met 80% kans opvalt."""
    schaal = np.sqrt(n_a * n_b / (n_a + n_b))
    z = stats.norm.ppf(1 - alfa / 2)
    return float(stats.norm.cdf(abs(d) * schaal - z)), float((z + stats.norm.ppf(0.8)) / schaal)


def ab_test(dag, seed=1):
    """Loot elke dag in groep A of B (zoals een proef met een batterij) en beoordeelt de proef. Lange tabel."""
    rng = np.random.default_rng(seed)
    dag = dag.copy()
    dag["groep"] = np.where(rng.random(len(dag)) < 0.5, "A", "B")
    dag["omzet"] = np.where(dag.groep == "A", dag.a, dag.b)
    dag["seizoen"] = np.where(dag.datum.dt.month.isin([4, 5, 6, 7, 8, 9]), "zomerhalfjaar", "winterhalfjaar")
    dag["weekdeel"] = np.where(dag.datum.dt.dayofweek >= 5, "weekend", "werkdag")
    grens = break_even_dag()
    rijen = []

    def voeg(onderdeel, segment, d):
        a, b = d[d.groep == "A"].omzet, d[d.groep == "B"].omzet
        if len(a) > 5 and len(b) > 5:
            r = vergelijk(a, b, grens)
            r["power"], mde = onderscheidend(r["n_a"], r["n_b"], r["cohen_d"])
            r["kleinste_aantoonbare_verschil"] = mde * np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
            rijen.append({"onderdeel": onderdeel, "segment": segment, **r})

    voeg("totaal", "alle dagen", dag)
    for kolom in ("jaar", "seizoen", "weekdeel"):
        for s, d in dag.groupby(kolom):
            voeg(kolom, str(s), d)
    t = pd.DataFrame(rijen)
    seg = t.onderdeel != "totaal"
    t.loc[seg, "p_holm"] = holm(t.loc[seg, "p"])
    na, nb = (dag.groep == "A").sum(), (dag.groep == "B").sum()
    extra = [{"onderdeel": "verdeling over de groepen", "segment": "chi-kwadraat tegen 50/50", "n_a": na, "n_b": nb,
              "p": float(stats.chisquare([na, nb]).pvalue)},
             {"onderdeel": "break-even", "segment": f"dagomzet per MW voor {STREEF:.0%} IRR", "verschil": grens}]
    d = dag.b - dag.a                                          # gepaard: beide strategieen op dezelfde dag
    lo, hi = stats.t.interval(0.95, len(d) - 1, loc=d.mean(), scale=stats.sem(d))
    extra.append({"onderdeel": "gepaard (alle dagen, beide strategieen)", "segment": "alle dagen", "n_a": len(d), "n_b": len(d),
                  "gem_a": dag.a.mean(), "gem_b": dag.b.mean(), "verschil": d.mean(), "relatief": dag.b.mean() / dag.a.mean() - 1,
                  "ci_laag": lo, "ci_hoog": hi, "p": float(stats.ttest_1samp(d, 0).pvalue)})
    for j, g in dag.groupby("jaar"):
        dj = g.b - g.a
        lo, hi = stats.t.interval(0.95, len(dj) - 1, loc=dj.mean(), scale=stats.sem(dj))
        extra.append({"onderdeel": "gepaard per jaar", "segment": str(j), "n_a": len(dj), "n_b": len(dj), "gem_a": g.a.mean(),
                      "gem_b": g.b.mean(), "verschil": dj.mean(), "relatief": g.b.mean() / g.a.mean() - 1, "ci_laag": lo, "ci_hoog": hi,
                      "p": float(stats.ttest_1samp(dj, 0).pvalue)})
    helling = stats.linregress(np.arange(len(d)), d)           # slijt het effect?
    extra.append({"onderdeel": "nieuwheidseffect", "segment": "trend van het dagverschil (EUR per MW per dag, per jaar)",
                  "verschil": helling.slope * 365, "p": float(helling.pvalue), "gem_a": d.iloc[:90].mean(), "gem_b": d.iloc[-90:].mean()})
    kijk, eerste = [], None                                    # gluren: elke maand toetsen tot het 'significant' is
    for einde in pd.date_range(dag.datum.min() + pd.Timedelta(days=30), dag.datum.max(), freq="30D"):
        g = dag[dag.datum <= einde]
        p = stats.ttest_ind(g[g.groep == "B"].omzet, g[g.groep == "A"].omzet, equal_var=False).pvalue
        kijk.append(p < 0.05)
        eerste = eerste or (einde.date() if p < 0.05 else None)
    extra.append({"onderdeel": "gluren", "segment": f"{len(kijk)} tussentijdse toetsen; eerste keer onder 0,05 op {eerste}",
                  "n_a": int(sum(kijk)), "n_b": len(kijk), "relatief": float(np.mean(kijk))})
    return pd.concat([t, pd.DataFrame(extra)], ignore_index=True), dag


# -------------------------------------------------------------------------------------------------- 3 regressie
def regressiedata(data=DATA):
    """Zone-jaren met gemeten capture rate (hele jaren), met het zonaandeel van de buurlanden erbij."""
    from . import ruimtelijk
    p = da.paneel(data)
    p = p[~p.deeljaar & p.capture_uit_opwek & p.capture_zon.between(0, 2)]
    gew = ruimtelijk.gewichten(pd.read_csv(os.path.join(data, "fact_ntc.csv")))
    buur = ruimtelijk.buuraandeel(gew, ruimtelijk.ember_zonaandeel(data)).rename(columns={"buur_pct": "buur_zon_pct"})
    p = p.merge(buur, on=["iso3", "jaar"], how="left")
    p["log_prijs"] = np.log(p.gem_prijs)
    return p.dropna(subset=KANDIDATEN + ["capture_zon"]).reset_index(drop=True)


def ontwerp(d, kenmerken, jaren=None):
    """Ontwerpmatrix: constante, kenmerken en jaardummy's (eerste jaar is de basis)."""
    jaren = jaren if jaren is not None else sorted(d.jaar.unique())
    X = [np.ones(len(d))] + [d[k].values.astype(float) for k in kenmerken] + [(d.jaar == j).values.astype(float) for j in jaren[1:]]
    return np.column_stack(X), ["constante"] + list(kenmerken) + [f"jaar_{j}" for j in jaren[1:]]


def ols(y, X, groepen):
    """Kleinste kwadraten met standaardfouten geclusterd per groep (land). Geeft een dict met alles voor de diagnose."""
    n, k = X.shape
    xtx_inv = np.linalg.inv(X.T @ X)
    b = xtx_inv @ X.T @ y
    e = y - X @ b
    vlees = np.zeros((k, k))
    for g in np.unique(groepen):
        s = X[groepen == g].T @ e[groepen == g]
        vlees += np.outer(s, s)
    G = len(np.unique(groepen))
    V = xtx_inv @ vlees @ xtx_inv * G / (G - 1) * (n - 1) / (n - k)
    se = np.sqrt(np.diag(V))
    r2 = 1 - e.var() / y.var()
    return {"b": b, "se": se, "t": b / se, "p": 2 * stats.t.sf(np.abs(b / se), G - 1), "ci": stats.t.ppf(0.975, G - 1) * se, "e": e,
            "r2": r2, "r2_adj": 1 - (1 - r2) * (n - 1) / (n - k), "rmse": float(np.sqrt((e ** 2).mean())), "mae": float(np.abs(e).mean()),
            "s2": float(e @ e / (n - k)), "xtx_inv": xtx_inv, "n": n, "k": k, "G": G}


def kruisvalidatie(d, modellen, plooien=5):
    """Voorspelfout op landen die het model niet zag (GroupKFold per land)."""
    from sklearn.model_selection import GroupKFold
    y, rijen = d.capture_zon.values, []
    for naam, maak in modellen.items():
        voorspeld = np.full(len(d), np.nan)
        for tr, te in GroupKFold(plooien).split(d, y, d.iso3):
            voorspeld[te] = maak(d.iloc[tr], d.iloc[te])
        e = y - voorspeld
        rijen.append({"onderdeel": "modelkeuze (kruisvalidatie per land)", "term": naam, "r2": 1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum(),
                      "rmse": float(np.sqrt((e ** 2).mean())), "mae": float(np.abs(e).mean()), "n": len(d)})
    return rijen


def regressie(data=DATA):
    """Verkenning, keuze van kenmerken, modelkeuze, aannames, coefficienten, residuen en voorbeelden. Twee tabellen."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LassoCV
    d = regressiedata(data)
    y, groepen, jaren = d.capture_zon.values, d.iso3.values, sorted(d.jaar.unique())
    rijen = [{"onderdeel": "verkenning", "term": k, "coef": da.rang(d[k], d.capture_zon), "n": len(d)} for k in KANDIDATEN]
    for k, v in da.vif(d[KANDIDATEN]).items():
        rijen.append({"onderdeel": "VIF", "term": k, "coef": v})
    Z = (d[KANDIDATEN] - d[KANDIDATEN].mean()) / d[KANDIDATEN].std()
    Xl = np.column_stack([Z.values] + [(d.jaar == j).values.astype(float) for j in jaren[1:]])
    lasso = LassoCV(cv=5, random_state=1).fit(Xl, y)
    gekozen = [k for k, c in zip(KANDIDATEN, lasso.coef_) if abs(c) > 1e-6]
    for k, c in zip(KANDIDATEN, lasso.coef_):
        rijen.append({"onderdeel": "kenmerkkeuze (lasso, gestandaardiseerd)", "term": k, "coef": float(c)})

    def lineair(kenmerken):
        def maak(tr, te):
            Xtr, _ = ontwerp(tr, kenmerken, jaren)
            Xte, _ = ontwerp(te, kenmerken, jaren)
            return Xte @ np.linalg.lstsq(Xtr, tr.capture_zon.values, rcond=None)[0]
        return maak

    def bos(tr, te):
        kol = KANDIDATEN + ["jaar"]
        return RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=1).fit(tr[kol], tr.capture_zon).predict(te[kol])

    modellen = {"alleen jaareffecten": lineair([]), "eigen zon + buren + jaareffecten": lineair(["aandeel_zon_pct", "buur_zon_pct"]),
                "lasso-keuze + jaareffecten": lineair(gekozen), "alle kandidaten + jaareffecten": lineair(KANDIDATEN), "bosmodel": bos}
    rijen += kruisvalidatie(d, modellen)
    kenmerken = ["aandeel_zon_pct", "buur_zon_pct"]               # het eenvoudigste model met de laagste voorspelfout
    X, namen = ontwerp(d, kenmerken, jaren)
    m = ols(y, X, groepen)
    for i, naam in enumerate(namen):
        rijen.append({"onderdeel": "coefficient", "term": naam, "coef": m["b"][i], "se": m["se"][i], "t": m["t"][i], "p": m["p"][i],
                      "ci_laag": m["b"][i] - m["ci"][i], "ci_hoog": m["b"][i] + m["ci"][i]})
    rijen.append({"onderdeel": "prestatie (binnen de steekproef)", "term": "gekozen model", "r2": m["r2"], "r2_adj": m["r2_adj"],
                  "rmse": m["rmse"], "mae": m["mae"], "n": m["n"]})
    e, fit = m["e"], X @ m["b"]
    hulp = np.linalg.lstsq(X, e ** 2, rcond=None)                 # Breusch-Pagan: hangt de spreiding af van de kenmerken?
    r2_bp = 1 - ((e ** 2 - X @ hulp[0]) ** 2).sum() / ((e ** 2 - (e ** 2).mean()) ** 2).sum()
    reset = ols(y, np.column_stack([X, fit ** 2]), groepen)        # RESET: mist het model een kromming?
    dw = []
    for _, g in d.assign(e=e).sort_values("jaar").groupby("biedzone"):
        if len(g) > 2:
            dw.append(((g.e.diff().dropna()) ** 2).sum() / (g.e ** 2).sum())
    for naam, waarde, p in (("normaliteit van de residuen (Shapiro-Wilk)", stats.shapiro(e).statistic, stats.shapiro(e).pvalue),
                            ("gelijke spreiding (Breusch-Pagan)", m["n"] * r2_bp, stats.chi2.sf(m["n"] * r2_bp, m["k"] - 1)),
                            ("lineariteit (RESET, kwadraat van de voorspelling)", reset["t"][-1], reset["p"][-1]),
                            ("autocorrelatie binnen zones (Durbin-Watson, gemiddeld)", float(np.mean(dw)), np.nan)):
        rijen.append({"onderdeel": "aanname", "term": naam, "coef": float(waarde), "p": float(p) if p == p else np.nan})
    d = d.assign(voorspeld=fit, residu=e)
    for _, r in d.reindex(d.residu.abs().sort_values(ascending=False).index).head(8).iterrows():
        rijen.append({"onderdeel": "grootste residuen", "term": f"{r.biedzone} {int(r.jaar)}", "coef": r.residu, "r2": r.capture_zon})
    for j, g in d.groupby("jaar"):
        rijen.append({"onderdeel": "residu per jaar", "term": str(j), "coef": g.residu.mean(), "rmse": float(np.sqrt((g.residu ** 2).mean()))})

    def voorspel(naam, rij, **anders):                             # voorspelinterval voor een nieuwe waarneming
        r = rij.copy()
        for k, v in anders.items():
            r[k] = r[k] + v
        x, _ = ontwerp(pd.DataFrame([r]), kenmerken, jaren)
        x = x[0]
        h = stats.t.ppf(0.975, m["n"] - m["k"]) * np.sqrt(m["s2"] * (1 + x @ m["xtx_inv"] @ x))
        return {"voorbeeld": naam, "voorspeld": float(x @ m["b"]), "laag": float(x @ m["b"] - h), "hoog": float(x @ m["b"] + h),
                "werkelijk": float(rij.capture_zon) if not anders else np.nan, **{k: float(r[k]) for k in kenmerken}}

    vb = []
    laatste = d[d.jaar == d.jaar.max()].set_index("biedzone")
    for zone in ("NL", "DE-LU", "ES", "IT-North", "PL"):
        if zone in laatste.index:
            vb.append(voorspel(f"{zone} {int(d.jaar.max())}", laatste.loc[zone]))
    if "NL" in laatste.index:
        vb.append(voorspel("NL: eigen zonaandeel +5 punten", laatste.loc["NL"], aandeel_zon_pct=5))
        vb.append(voorspel("NL: zonaandeel buren +5 punten", laatste.loc["NL"], buur_zon_pct=5))
        vb.append(voorspel("NL: beide +5 punten", laatste.loc["NL"], aandeel_zon_pct=5, buur_zon_pct=5))
    return pd.DataFrame(rijen), pd.DataFrame(vb), d


# --------------------------------------------------------------------------------------------------- 4 cohorten
def kaplan_meier(duur, gebeurd):
    """Overlevingscurve: aandeel zones dat na t jaar nog boven de grens zit. Geeft (tabel, mediane duur of NaN)."""
    duur, gebeurd = np.asarray(duur), np.asarray(gebeurd, bool)
    s, rijen, mediaan = 1.0, [], np.nan
    for t in sorted(set(duur[gebeurd])):
        risico, events = (duur >= t).sum(), ((duur == t) & gebeurd).sum()
        s *= 1 - events / risico
        rijen.append({"jaren": int(t), "in_risico": int(risico), "gebeurtenissen": int(events), "overleving": s})
        if s <= 0.5 and mediaan != mediaan:
            mediaan = float(t)
    return pd.DataFrame(rijen), mediaan


def cohorten(data=DATA, drempel=5.0, grens=0.70):
    """Cohort: het jaar waarin zon in het land voor het eerst `drempel` procent van de opwek haalde (Ember, alle jaren).
    Volgt per cohort de capture rate, de capture-prijs en de kostendekking, per jaar sinds de drempel en per kalenderjaar.
    Gebeurtenis voor de overlevingsanalyse: de capture rate zakt voor het eerst onder `grens`."""
    e = pd.read_csv(os.path.join(data, "fact_ember_opwek_jaar.csv"))
    e = e[(e["Electricity source"] == "Solar") & e["ISO 3 code"].notna()]
    start = e[e["Share of generation (%)"] >= drempel].groupby("ISO 3 code").Year.min().rename("startjaar")
    p = da.paneel(data)
    p = p[~p.deeljaar & p.capture_uit_opwek & p.capture_zon.between(0, 2)].merge(start, left_on="iso3", right_index=True, how="left")
    t = pd.read_csv(os.path.join(data, "fact_tech_land.csv")).query("technologie == 'zon'")[["land", "jaar", "capture_price"]]
    p = p.merge(t, on=["land", "jaar"], how="left")
    bakken = [(0, 2015, "tot en met 2015"), (2016, 2019, "2016-2019"), (2020, 2021, "2020-2021"), (2022, 2023, "2022-2023"), (2024, 2030, "2024-2025")]
    p["cohort"] = "nog onder de drempel"
    for a, b, naam in bakken:
        p.loc[p.startjaar.between(a, b), "cohort"] = naam
    p["sinds"] = p.jaar - p.startjaar
    rijen = []
    for as_, kolom in (("jaren sinds de drempel", "sinds"), ("kalenderjaar", "jaar")):
        for (c, k), g in p.dropna(subset=[kolom]).groupby(["cohort", kolom]):
            if as_ == "jaren sinds de drempel" and k < 0:
                continue
            rijen.append({"as": as_, "cohort": c, "periode": int(k), "zones": g.biedzone.nunique(), "capture_zon": g.capture_zon.mean(),
                          "capture_prijs": g.capture_price.mean(), "zonaandeel_pct": g.aandeel_zon_pct.mean(),
                          **{f"aandeel_dekt_lcoe_{int(v)}": float((g.capture_price >= v).mean()) for v in LCOE.values()}})
    tabel = pd.DataFrame(rijen)
    duur = []
    for zone, g in p.dropna(subset=["startjaar"]).sort_values("jaar").groupby("biedzone"):
        onder = g[g.capture_zon < grens]
        einde = onder.jaar.min() if len(onder) else g.jaar.max()
        duur.append({"biedzone": zone, "cohort": g.cohort.iloc[0], "startjaar": int(g.startjaar.iloc[0]), "eindjaar": int(einde),
                     "duur": int(max(einde - g.startjaar.iloc[0], 0)), "gebeurd": bool(len(onder))})
    duur = pd.DataFrame(duur)
    over = []
    for c, g in list(duur.groupby("cohort")) + [("alle zones", duur)]:
        km, med = kaplan_meier(g.duur, g.gebeurd)
        over.append({"cohort": c, "zones": len(g), "onder_grens_gezakt": int(g.gebeurd.sum()), "mediane_duur_jaren": med,
                     "jaren_bij_laatste_stap": int(km.jaren.max()) if len(km) else np.nan,
                     "overleving_bij_laatste_stap": float(km.overleving.iloc[-1]) if len(km) else 1.0})
    laatste = p[p.jaar == p.jaar.max()]
    groepen = [g.capture_zon.values for _, g in laatste.groupby("cohort") if len(g) >= 3]
    kw = stats.kruskal(*groepen) if len(groepen) >= 2 else None
    toets = [{"toets": f"Kruskal-Wallis: capture rate {int(p.jaar.max())} verschilt tussen cohorten", "statistiek": kw.statistic if kw else np.nan,
              "p": kw.pvalue if kw else np.nan, "n": int(sum(len(g) for g in groepen))}]
    for c, g in laatste.groupby("cohort"):
        rest = laatste[laatste.cohort != c].capture_zon
        if len(g) >= 3:
            u = stats.mannwhitneyu(g.capture_zon, rest)
            toets.append({"toets": f"{c} tegen de rest ({int(p.jaar.max())})", "statistiek": float(u.statistic), "p": float(u.pvalue), "n": len(g),
                          "verschil": float(g.capture_zon.mean() - rest.mean())})
    toets = pd.DataFrame(toets)
    toets.loc[toets.index[1:], "p_holm"] = holm(toets.p.iloc[1:])
    ev = duur[duur.gebeurd]
    toets = pd.concat([toets, pd.DataFrame([{"toets": "Latere cohorten zakken sneller onder de grens (Spearman startjaar en duur)",
                                             "statistiek": da.rang(ev.startjaar, ev.duur), "n": len(ev),
                                             "p": float(stats.spearmanr(ev.startjaar, ev.duur).pvalue) if len(ev) > 3 else np.nan}])], ignore_index=True)
    pad = os.path.join(data, "fact_land_maand.csv")
    maand = pd.DataFrame()
    if os.path.exists(pad):                                        # maandbeeld: voortschrijdend jaargemiddelde per cohort
        lm = pd.read_csv(pad).merge(p[["land", "cohort", "startjaar"]].drop_duplicates(), on="land")
        lm = lm[lm.capture_zon.between(0, 3)].sort_values(["land", "jaar", "maand"])
        lm["capture_12m"] = lm.groupby("land").capture_zon.transform(lambda s: s.rolling(12, min_periods=12).mean())
        lm["periode"] = lm.jaar.astype(str) + "-" + lm.maand.astype(str).str.zfill(2)
        maand = lm.dropna(subset=["capture_12m"]).groupby(["cohort", "periode"]).agg(zones=("land", "nunique"), capture_12m=("capture_12m", "mean")).reset_index()
    return tabel, pd.DataFrame(over), duur, toets, maand


def main(data=DATA, uit=None):
    uit = uit or data
    schrijf = lambda df, naam: (df.to_csv(os.path.join(uit, naam), index=False), print(f"  -> {naam}: {len(df)} rijen"))
    schrijf(toetsen(data), "fact_toetsen_SA.csv")
    ab, dag = ab_test(ab_dagreeksen(data))
    schrijf(ab, "fact_abtest_SA.csv"); schrijf(dag, "fact_abtest_dag_SA.csv")
    reg, vb, _ = regressie(data)
    schrijf(reg, "fact_regressie_SA.csv"); schrijf(vb, "fact_regressie_voorspelling_SA.csv")
    tabel, over, duur, toets, maand = cohorten(data)
    schrijf(tabel, "fact_cohort_SA.csv"); schrijf(over, "fact_cohort_overleving_SA.csv"); schrijf(duur, "fact_cohort_duur_SA.csv")
    schrijf(toets, "fact_cohort_toets_SA.csv"); schrijf(maand, "fact_cohort_maand_SA.csv")


if __name__ == "__main__":
    main(*sys.argv[1:3])
