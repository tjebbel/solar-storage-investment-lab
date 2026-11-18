"""Data-analyse (_DA): verkenning, verbanden, segmenten, tijdpatronen, uitschieters en drijfveren.

Twee lagen:
- profiel van ALLE tabellen in powerbi/data (statistieken, ontbrekende waarden, verdeling, waardetellingen);
- verdieping op het zone-jaarpaneel: 37 Europese biedzones x 2019-2026, met capture rates, dagspreiding,
  negatieve uren, batterij-omzet en de opwekmix van het land (Ember).

Uitvoer: nieuwe tabellen met _DA in de naam, in dezelfde map als de bronnen.
Gebruik:  PYTHONPATH=src python3 -m eti.da [datamap] [uitvoermap]
Nodig: pandas en numpy; voor clustering, isolation forest en drijfveren ook scikit-learn.
"""
import os
import sys

import numpy as np
import pandas as pd

DATA = "powerbi/data"
LIMIET = 400_000                    # zoveel rijen per tabel voor het profiel (grote uurtabellen)
REGIO = {**{z: "Noordwest-Europa" for z in ("NL", "BE", "DE-LU", "FR", "AT", "CH", "DK1", "DK2")},
         **{z: "Iberie" for z in ("ES", "PT")},
         **{z: "Italie" for z in ("IT-North", "IT-Centre-North", "IT-South", "IT-Sicily")},
         **{z: "Scandinavie" for z in ("NO1", "NO2", "NO3", "NO4", "NO5", "SE1", "SE2", "SE3", "SE4", "FI")},
         **{z: "Baltische staten" for z in ("EE", "LV", "LT")},
         **{z: "Midden- en Zuidoost-Europa" for z in ("PL", "CZ", "SK", "HU", "RO", "BG", "GR", "HR", "SI", "RS")}}
EMBER = {"Solar": "aandeel_zon_pct", "Wind": "aandeel_wind_pct", "Nuclear": "aandeel_kern_pct", "Gas": "aandeel_gas_pct",
         "Hydro": "aandeel_waterkracht_pct", "Coal": "aandeel_kolen_pct"}
KERN = ["capture_zon", "capture_wind", "gem_prijs", "dagspreiding", "negatieve_uren", "uren_boven_200", "aandeel_zon_pct",
        "aandeel_wind_pct", "aandeel_kern_pct", "aandeel_gas_pct", "aandeel_waterkracht_pct", "aandeel_kolen_pct", "vraag_twh",
        "batterij_per_mw", "voorspel_ratio"]
DOELEN = {"capture_zon": [], "batterij_per_mw": ["voorspel_ratio"], "dagspreiding": ["batterij_per_mw", "voorspel_ratio"],
          "negatieve_uren": []}
# kenmerken die een land zelf kiest of die van buiten komen (opwekmix, vraag, prijsniveau, jaar), zonder marktuitkomsten
STRUCTUUR = ["jaar", "gem_prijs", "aandeel_zon_pct", "aandeel_wind_pct", "aandeel_kern_pct", "aandeel_gas_pct",
             "aandeel_waterkracht_pct", "aandeel_kolen_pct", "vraag_twh"]


# ---------------------------------------------------------------------------------------------------------------- 1
def tabellen(data=DATA):
    return sorted(f for f in os.listdir(data) if f.endswith(".csv") and not f[:-4].endswith(("_DA", "_SA", "_ML", "_KW", "_VZ", "_GAS", "_ST")))


def verdeling(s):
    """Grove typering van een numerieke kolom: constant, ongeveer normaal, scheef of mogelijk tweetoppig."""
    s = s.dropna()
    if len(s) < 8 or s.nunique() <= 1:
        return "constant of te weinig waarden"
    scheef, kurt = float(s.skew()), float(s.kurt())
    if len(s) > 30 and (scheef ** 2 + 1) / (kurt + 3) > 0.555 and abs(scheef) < 1:
        return "mogelijk tweetoppig"
    if abs(scheef) < 0.5 and abs(kurt) < 1:
        return "ongeveer normaal"
    if abs(scheef) < 0.5:
        return "symmetrisch met zware staarten" if kurt > 0 else "symmetrisch en plat"
    kant = "rechts" if scheef > 0 else "links"
    return f"sterk scheef naar {kant}" if abs(scheef) >= 1 else f"licht scheef naar {kant}"


def profiel(data=DATA):
    """Voor elke tabel en kolom: aantal, ontbrekend, statistieken en verdeling; voor tekstkolommen de tien meest
    voorkomende waarden plus 'overig'. Geeft (profiel, waarden)."""
    prof, waarden = [], []
    for naam in tabellen(data):
        pad = os.path.join(data, naam)
        try:
            df = pd.read_csv(pad, low_memory=False, nrows=LIMIET)
        except Exception as e:                                   # een kapot bestand mag de rest niet tegenhouden
            prof.append({"dataset": naam[:-4], "kolom": "(niet leesbaar)", "type": type(e).__name__})
            continue
        for kol in df.columns:
            s = df[kol]
            rij = {"dataset": naam[:-4], "kolom": kol, "rijen": len(df), "ontbreekt": int(s.isna().sum()),
                   "ontbreekt_pct": float(s.isna().mean() * 100) if len(df) else None, "uniek": int(s.nunique())}
            if pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s):
                x = s.dropna().astype(float)
                rij.update({"type": "getal", "gemiddelde": x.mean(), "mediaan": x.median(), "std": x.std(), "min": x.min(),
                            "q1": x.quantile(0.25), "q3": x.quantile(0.75), "max": x.max(),
                            "scheefheid": x.skew() if len(x) > 2 else None, "verdeling": verdeling(x)} if len(x) else {"type": "getal"})
            else:
                rij["type"] = "tekst"
                tel = s.astype("string").value_counts(dropna=True)
                for w, n in tel.head(10).items():
                    waarden.append({"dataset": naam[:-4], "kolom": kol, "waarde": str(w)[:80], "aantal": int(n)})
                if len(tel) > 10:
                    waarden.append({"dataset": naam[:-4], "kolom": kol, "waarde": f"overig ({len(tel) - 10} waarden)",
                                    "aantal": int(tel.iloc[10:].sum())})
            prof.append(rij)
    return pd.DataFrame(prof), pd.DataFrame(waarden)


# ---------------------------------------------------------------------------------------------------------------- 2
def paneel(data=DATA):
    """Een rij per biedzone en jaar, met de batterij van 2 uur en de opwekmix van het land erbij."""
    land = pd.read_csv(os.path.join(data, "fact_land_jaar.csv"))
    flex = pd.read_csv(os.path.join(data, "fact_flex_land.csv")).query("uren_opslag == 2")
    flex = flex.rename(columns={"omzet_realistisch_per_mw": "batterij_per_mw", "omzet_perfect_per_mw": "batterij_perfect_per_mw"})
    p = land.merge(flex[["land", "jaar", "batterij_per_mw", "batterij_perfect_per_mw", "voorspel_ratio"]], on=["land", "jaar"], how="left")
    e = pd.read_csv(os.path.join(data, "fact_ember_opwek_jaar.csv"))
    e = e[e["ISO 3 code"].notna()]
    mix = (e[e["Electricity source"].isin(EMBER)].pivot_table(index=["ISO 3 code", "Year"], columns="Electricity source",
                                                              values="Share of generation (%)", aggfunc="first").rename(columns=EMBER))
    vraag = e[e["Electricity source"] == "Demand"].groupby(["ISO 3 code", "Year"])["Generation (TWh)"].first().rename("vraag_twh")
    mix = mix.join(vraag).reset_index().rename(columns={"ISO 3 code": "iso3", "Year": "jaar"})
    p = p.drop(columns=[c for c in ("aandeel_zon", "aandeel_wind", "aandeel_zon_energycharts", "aandeel_wind_energycharts") if c in p])
    p = p.merge(mix, on=["iso3", "jaar"], how="left")
    p["regio"] = p.biedzone.map(REGIO)
    p["deeljaar"] = p.jaar >= 2026
    p["capture_uit_opwek"] = p.capture_bron.astype(str).str.startswith("opwek")
    eerst = ["land", "biedzone", "iso3", "regio", "jaar", "deeljaar", "capture_bron", "capture_uit_opwek", "uren"]
    return p[eerst + [c for c in p.columns if c not in eerst]]


def rang(a, b):
    """Rangcorrelatie (Spearman) zonder scipy."""
    d = pd.concat([a, b], axis=1).dropna()
    return float(d.iloc[:, 0].rank().corr(d.iloc[:, 1].rank())) if len(d) > 3 else np.nan


def vif(df):
    """Variantie-inflatie per kolom: 1 / (1 - R2) van de regressie op de andere kolommen. Boven 5 is verdacht."""
    x = df.dropna()
    z = (x - x.mean()) / x.std()
    uit = {}
    for k in z.columns:
        y, X = z[k].values, np.column_stack([np.ones(len(z))] + [z[c].values for c in z.columns if c != k])
        rest = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
        r2 = 1 - rest.var() / y.var()
        uit[k] = 1 / max(1e-9, 1 - r2)
    return uit


def eta2(groep, waarde):
    """Aandeel van de variantie in een getal dat een indeling verklaart (0 tot 1)."""
    d = pd.DataFrame({"g": groep, "w": waarde}).dropna()
    if d.g.nunique() < 2:
        return np.nan
    tussen = sum(len(x) * (x.w.mean() - d.w.mean()) ** 2 for _, x in d.groupby("g"))
    return float(tussen / ((d.w - d.w.mean()) ** 2).sum())


def correlaties(p):
    """Lange tabel met Pearson, Spearman, Spearman binnen jaren, VIF, eta-kwadraat en vertraagde verbanden."""
    v = p[~p.deeljaar]
    kol = [k for k in KERN if k in v]
    rijen = []
    for i, a in enumerate(kol):
        for b in kol[i + 1:]:
            d = v[[a, b]].dropna()
            if len(d) < 20:
                continue
            binnen = [rang(g[a], g[b]) for _, g in v.groupby("jaar") if g[[a, b]].dropna().shape[0] >= 10]
            pear, spear = float(d[a].corr(d[b])), rang(d[a], d[b])
            rijen.append({"soort": "paar", "var1": a, "var2": b, "pearson": pear, "spearman": spear,
                          "spearman_binnen_jaren": float(np.nanmean(binnen)) if binnen else np.nan, "n": len(d),
                          "sterk": bool(max(abs(pear), abs(spear)) > 0.5)})
    voorspellers = [k for k in kol if k not in ("capture_zon", "batterij_per_mw", "voorspel_ratio")]
    for k, w in vif(v[voorspellers]).items():
        rijen.append({"soort": "vif", "var1": k, "waarde": w, "n": len(v[voorspellers].dropna())})
    for indeling in ("regio", "jaar", "land", "capture_bron"):
        for doel in ("capture_zon", "batterij_per_mw", "dagspreiding", "negatieve_uren"):
            rijen.append({"soort": "eta2", "var1": indeling, "var2": doel, "waarde": eta2(v[indeling], v[doel]), "n": len(v)})
    s = v.sort_values(["biedzone", "jaar"]).copy()
    for a in ("aandeel_zon_pct", "aandeel_wind_pct", "gem_prijs"):
        for b in ("capture_zon", "batterij_per_mw", "negatieve_uren"):
            vorig = s.groupby("biedzone")[a].shift(1)
            da, db = s.groupby("biedzone")[a].diff(), s.groupby("biedzone")[b].diff()
            rijen.append({"soort": "vertraagd (vorig jaar)", "var1": a, "var2": b, "spearman": rang(vorig, s[b]), "n": int(vorig.notna().sum())})
            rijen.append({"soort": "verandering op verandering", "var1": a, "var2": b, "spearman": rang(da, db), "n": int(da.notna().sum())})
    return pd.DataFrame(rijen)


# ---------------------------------------------------------------------------------------------------------------- 3
def regelsegment(r):
    """Indeling met vuistregels uit de investeringspraktijk (op de waarden van het jaar zelf)."""
    if r.capture_zon < 0.60 and r.negatieve_uren >= 300:
        return "Zonverzadigd"
    if r.dagspreiding >= 120:
        return "Batterijmarkt"
    if r.dagspreiding < 60:
        return "Vlakke prijzen"
    if r.capture_zon >= 0.75:
        return "Zon houdt waarde"
    return "Middenveld"


CLUSTERKOLOMMEN = ["capture_zon", "dagspreiding", "negatieve_uren", "gem_prijs", "aandeel_zon_pct", "aandeel_wind_pct", "batterij_per_mw"]


def clusters(p, jaar=2025, k_bereik=range(2, 7), herhalingen=40):
    """K-means op de zones van een jaar. K wordt gekozen op twee maten samen: de silhouetscore (hoe scherp de groepen
    van elkaar gescheiden zijn) en de stabiliteit (krijgt een zone in een herhaalde steekproef dezelfde groep; de
    aangepaste Rand-index, 1 = altijd). Van de K's waarvan de silhouetscore binnen 0,03 van de beste ligt en de
    kleinste groep minstens drie zones telt, wint de stabielste. Geeft (labels, tabel per K, centra, gemiddelden)."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score, silhouette_score
    x = p[p.jaar == jaar].dropna(subset=CLUSTERKOLOMMEN).set_index("biedzone")[CLUSTERKOLOMMEN]
    z = (x - x.mean()) / x.std()
    rng = np.random.default_rng(1)
    rijen = []
    for k in k_bereik:
        basis = KMeans(n_clusters=k, n_init=20, random_state=1).fit(z)
        ari = []
        for _ in range(herhalingen):
            idx = rng.choice(len(z), len(z), replace=True)
            m = KMeans(n_clusters=k, n_init=5, random_state=int(rng.integers(1_000_000))).fit(z.iloc[idx])
            ari.append(adjusted_rand_score(basis.labels_, m.predict(z)))
        rijen.append({"k": k, "silhouet": float(silhouette_score(z, basis.labels_)), "stabiliteit": float(np.mean(ari)),
                      "kleinste_groep": int(np.bincount(basis.labels_).min())})
    t = pd.DataFrame(rijen)
    kandidaten = t[(t.silhouet >= t.silhouet.max() - 0.03) & (t.kleinste_groep >= 3)]
    k = int((kandidaten if len(kandidaten) else t).sort_values("stabiliteit", ascending=False).k.iloc[0])
    t["gekozen"] = t.k == k
    model = KMeans(n_clusters=k, n_init=20, random_state=1).fit(z)
    lab = pd.Series(model.labels_, index=x.index, name="cluster")
    centra = x.groupby(lab).mean()
    centra["zones"] = lab.value_counts().sort_index()
    return lab, t, centra, x.mean()


def clusternamen(centra):
    """Geeft elk cluster een eigen naam voor niet-technische lezers. De duidelijkste groep krijgt eerst een naam;
    een naam wordt alleen gebruikt als het cluster er ook aan voldoet."""
    over, namen = list(centra.index), {}

    def kies(naam, kolom, hoogste, voorwaarde):
        kand = [i for i in over if voorwaarde(centra.loc[i])]
        if kand:
            i = centra.loc[kand, kolom].idxmax() if hoogste else centra.loc[kand, kolom].idxmin()
            namen[i] = naam
            over.remove(i)

    kies("Waterkracht dempt de dag", "dagspreiding", False, lambda r: r.dagspreiding < 60)
    kies("Zon houdt waarde", "capture_zon", True, lambda r: r.capture_zon >= 0.75)
    kies("Zonverzadigd met veel negatieve uren", "negatieve_uren", True, lambda r: r.negatieve_uren >= 300)
    kies("Grote dagspreiding, sterke batterijcase", "dagspreiding", True, lambda r: r.dagspreiding >= 120)
    for n, i in enumerate(list(over), 1):
        namen[i] = "Europees midden" if len(over) == 1 else f"Europees midden {n}"
    return pd.Series(namen)


def gedrag(p, jaar=2025):
    """Gedragsindeling per zone, naar het voorbeeld van recency-frequency-monetary: hoe lang geleden haalde zon voor
    het laatst een capture rate van 0,80, hoe vaak is de prijs negatief, en wat verdient een batterij."""
    v = p[~p.deeljaar]
    rijen = []
    for zone, g in v.groupby("biedzone"):
        nu = g[g.jaar == jaar]
        if nu.empty:
            continue
        goed = g[g.capture_zon >= 0.80].jaar
        rijen.append({"biedzone": zone, "jaren_sinds_capture_080": int(jaar - goed.max()) if len(goed) else int(jaar - g.jaar.min() + 1),
                      "negatieve_uren": float(nu.negatieve_uren.iloc[0]), "batterij_per_mw": float(nu.batterij_per_mw.iloc[0])})
    r = pd.DataFrame(rijen)
    for kol, naam, omgekeerd in (("jaren_sinds_capture_080", "score_recent", True), ("negatieve_uren", "score_frequentie", False),
                                 ("batterij_per_mw", "score_waarde", False)):
        rangnr = r[kol].rank(pct=True, ascending=not omgekeerd)
        r[naam] = np.ceil(rangnr * 3).clip(1, 3).astype(int)
    def label(x):
        if x.score_waarde == 3 and x.score_frequentie >= 2:
            return "Opslag eerst"
        if x.score_recent == 3 and x.score_frequentie == 1:
            return "Zon nog rendabel"
        if x.score_recent == 1 and x.score_frequentie == 3:
            return "Zon alleen met contract of opslag"
        return "Selectief"
    r["gedragssegment"] = r.apply(label, axis=1)
    return r


def segmenten(p):
    """Voegt regelsegment, cluster en gedragssegment toe en geeft de profielen per segment."""
    p = p.copy()
    compleet = p[["capture_zon", "negatieve_uren", "dagspreiding"]].notna().all(axis=1)
    p["regelsegment"] = None
    p.loc[compleet, "regelsegment"] = p[compleet].apply(regelsegment, axis=1)
    scores = pd.DataFrame()
    try:
        lab, scores, centra, _ = clusters(p)
        p["cluster_2025"] = p.biedzone.map(lab)
        p["clusternaam_2025"] = p.cluster_2025.map(clusternamen(centra))
    except ImportError:
        p["cluster_2025"], p["clusternaam_2025"] = np.nan, None
    g = gedrag(p)
    p = p.merge(g[["biedzone", "gedragssegment"]], on="biedzone", how="left")
    totaal = p[p.jaar == 2025][CLUSTERKOLOMMEN].mean()
    prof = []
    for soort, kol in (("regels", "regelsegment"), ("cluster", "clusternaam_2025"), ("gedrag", "gedragssegment")):
        for naam, x in p[p.jaar == 2025].groupby(kol):
            rij = {"indeling": soort, "segment": naam, "zones": len(x), "aandeel_zones": len(x) / (p.jaar == 2025).sum(),
                   "leden": ", ".join(sorted(x.biedzone))}
            for k in CLUSTERKOLOMMEN:
                rij[k] = x[k].mean()
                rij[k + "_tov_gemiddelde"] = x[k].mean() / totaal[k] - 1 if totaal[k] else np.nan
            prof.append(rij)
    return p, pd.DataFrame(prof), g, scores


# ---------------------------------------------------------------------------------------------------------------- 4
def tijdpatronen(data=DATA):
    """Nederlandse uurprijs: trend, seizoen, weekdag, uur van de dag, breekpunten en groeicijfers (lange tabel)."""
    u = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), parse_dates=["timestamp_utc"])
    u = u.dropna(subset=["prijs_eur_mwh"]).set_index("timestamp_utc").sort_index()
    lokaal = u.index.tz_localize("UTC").tz_convert("Europe/Amsterdam") if u.index.tz is None else u.index.tz_convert("Europe/Amsterdam")
    u["weekdag"], u["uur_lokaal"], u["m"], u["j"] = lokaal.dayofweek, lokaal.hour, lokaal.month, lokaal.year
    rijen = []
    def voeg(reeks, dim, sleutel, waarde, extra=None):
        rijen.append({"reeks": reeks, "dimensie": dim, "sleutel": str(sleutel), "waarde": float(waarde) if pd.notna(waarde) else None, "extra": extra})
    jaar = u.groupby("j").prijs_eur_mwh.mean()
    for j, w in jaar.items():
        voeg("prijs", "jaar", j, w)
    for j, w in jaar.pct_change().dropna().items():
        voeg("prijs", "groei jaar op jaar", j, w)
    for j, w in u.groupby("j").prijs_eur_mwh.apply(lambda s: (s < 0).sum()).items():
        voeg("negatieve uren", "jaar", j, w)
    dag = u.prijs_eur_mwh.groupby([u.j, lokaal.dayofyear]).agg(lambda s: s.max() - s.min())
    for j, w in dag.groupby(level=0).mean().items():
        voeg("dagspreiding", "jaar", j, w)
    heel = u[u.j < u.j.max()]                             # seizoenspatronen alleen uit hele jaren
    for naam, kol in (("maand", "m"), ("weekdag", "weekdag"), ("uur", "uur_lokaal")):
        per_jaar = heel.groupby(["j", kol]).prijs_eur_mwh.mean()
        index = per_jaar / heel.groupby("j").prijs_eur_mwh.mean().reindex(per_jaar.index, level=0).values
        for sleutel, w in index.groupby(level=1).median().items():
            lo, hi = index.xs(sleutel, level=1).min(), index.xs(sleutel, level=1).max()
            voeg("prijsindex (1 = jaargemiddelde)", naam, sleutel, w, f"mediaan over hele jaren; laagste {lo:.2f}, hoogste {hi:.2f}")
        for sleutel, w in ((index > 1).groupby(level=1).mean()).items():
            voeg("aandeel jaren boven het jaargemiddelde", naam, sleutel, w)
    for j in sorted({2019, 2022, 2025, int(u.j.max())}):
        deel = u[u.j == j]
        if len(deel):
            for h, w in (deel.groupby("uur_lokaal").prijs_eur_mwh.mean() / deel.prijs_eur_mwh.mean()).items():
                voeg("uurprofiel", f"uur {j}", h, w)
    maand = u.prijs_eur_mwh.resample("MS").mean()
    for naam, n in (("maand op maand", 1), ("kwartaal op kwartaal", 3), ("jaar op jaar (per maand)", 12)):
        basis = maand if n != 3 else u.prijs_eur_mwh.resample("QS").mean()
        groei = basis.pct_change(1 if n == 3 else n).dropna()
        for t, w in groei.tail(8 if n == 3 else 12).items():
            voeg("prijs", "groei " + naam, t.strftime("%Y-%m"), w)
    for t, w in maand.tail(13).items():
        voeg("prijs", "maand", t.strftime("%Y-%m"), w, f"{int((u.index.to_period('M') == t.to_period('M')).sum())} uren")
    pad = os.path.join(data, "fact_land_maand.csv")
    if os.path.exists(pad):                              # is een prijsbeweging Nederlands of Europees?
        lm = pd.read_csv(pad)
        nu, toen = lm[lm.jaar == lm.jaar.max()], lm[lm.jaar == lm.jaar.max() - 1]
        s = nu.merge(toen, on=["land", "maand"], suffixes=("", "_vorig"))
        s["groei"] = s.gem_prijs / s.gem_prijs_vorig - 1
        for m, g in s.groupby("maand"):
            voeg("prijs alle zones", "mediaan groei jaar op jaar", f"{int(lm.jaar.max())}-{int(m):02d}", g.groei.median(),
                 f"{int((g.groei > 0).sum())} van {len(g)} zones stijgen")
    sprong = (maand.rolling(12).mean().diff(6)).dropna()
    for t in list(sprong.abs().nlargest(1).index) + list(sprong.nlargest(1).index) + list(sprong.nsmallest(1).index):
        voeg("prijs", "breekpunt (verandering van het 12-maandsgemiddelde in zes maanden)", t.strftime("%Y-%m"), sprong[t])
    z = (maand - maand.rolling(12, min_periods=6).mean().shift(1)) / maand.rolling(12, min_periods=6).std().shift(1)
    for t, w in z.abs().nlargest(5).items():
        voeg("prijs", "afwijkende maand (z-score t.o.v. de twaalf maanden ervoor)", t.strftime("%Y-%m"), z[t], f"{maand[t]:.0f} euro per MWh")
    if "solar_mw" in u:
        capture = u.groupby("j")[["prijs_eur_mwh", "solar_mw"]].apply(lambda d: (d.prijs_eur_mwh * d.solar_mw).sum() / d.solar_mw.sum() / d.prijs_eur_mwh.mean() if d.solar_mw.sum() else np.nan)
        for j, w in capture.items():
            voeg("capture rate zon", "jaar", j, w)
        cm = u.groupby(["j", "m"])[["prijs_eur_mwh", "solar_mw"]].apply(lambda d: (d.prijs_eur_mwh * d.solar_mw).sum() / d.solar_mw.sum() / d.prijs_eur_mwh.mean() if d.solar_mw.sum() else np.nan)
        for m, w in cm[cm.index.get_level_values(0) >= 2023].groupby(level=1).mean().items():
            voeg("capture rate zon", "maand (2023 en later)", m, w)
    return pd.DataFrame(rijen)


# ---------------------------------------------------------------------------------------------------------------- 5
GRENZEN = {"capture_zon": (0.0, 2.0), "capture_wind": (0.0, 2.0), "negatieve_uren": (0, 8784), "uren": (0, 8784),
           "aandeel_zon_pct": (0, 100), "aandeel_wind_pct": (0, 100), "dagspreiding": (0, 2000), "voorspel_ratio": (0, 1.0001)}


def uitschieters(p):
    """Drie methoden per kolom (IQR, z-score, isolation forest over de kernkolommen), een indeling per uitschieter en
    het effect op gemiddelde en mediaan. Geeft (lijst, effect, paneel met vlaggen en begrensde kolommen)."""
    kol = [k for k in KERN if k in p]
    p = p.copy()
    woud = pd.Series(False, index=p.index)
    try:
        from sklearn.ensemble import IsolationForest
        x = p[kol].dropna()
        z = (x - x.mean()) / x.std()
        woud.loc[x.index] = IsolationForest(n_estimators=300, contamination=0.05, random_state=1).fit_predict(z) == -1
    except ImportError:
        pass
    p["isolation_forest"] = woud
    rijen, effect = [], []
    for k in kol:
        s = p[k].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = (p[k] < q1 - 1.5 * (q3 - q1)) | (p[k] > q3 + 1.5 * (q3 - q1))
        zs = ((p[k] - s.mean()) / s.std()).abs() > 3
        laag, hoog = GRENZEN.get(k, (-np.inf, np.inf))
        fout = (p[k] < laag) | (p[k] > hoog)
        vlag = iqr | zs | fout
        for i in p.index[vlag]:
            r = p.loc[i]
            methoden = [m for m, v in (("IQR", iqr[i]), ("z-score", zs[i]), ("isolation forest", woud[i]), ("buiten geldig bereik", fout[i])) if v]
            if fout[i]:
                cat, advies = "invoer- of rekenfout", "verwijderen en de bron nalopen"
            elif not r.capture_uit_opwek and k in ("capture_zon", "capture_wind"):
                cat, advies = "systemisch: capture rate uit een instralingsprofiel", "houden met vlag; niet mengen met gemeten zones"
            elif r.jaar == 2022 and k in ("gem_prijs", "uren_boven_200", "dagspreiding", "batterij_per_mw"):
                cat, advies = "systemisch: energiecrisis 2022", "houden; in modellen een jaareffect opnemen"
            elif r.deeljaar:
                cat, advies = "systemisch: onvolledig jaar 2026", "houden met vlag; niet vergelijken met hele jaren"
            else:
                cat, advies = "echte uiterste waarde", "houden; voor modellen begrenzen op het 1e en 99e percentiel"
            rijen.append({"biedzone": r.biedzone, "land": r.land, "jaar": int(r.jaar), "kolom": k, "waarde": r[k], "methoden": " + ".join(methoden),
                          "categorie": cat, "advies": advies, "capture_zon": r.capture_zon, "gem_prijs": r.gem_prijs,
                          "negatieve_uren": r.negatieve_uren, "capture_bron": r.capture_bron})
        zonder = p.loc[~vlag, k]
        effect.append({"kolom": k, "uitschieters": int(vlag.sum()), "aandeel": float(vlag.mean()), "gemiddelde_met": s.mean(),
                       "gemiddelde_zonder": zonder.mean(), "mediaan_met": s.median(), "mediaan_zonder": zonder.median(),
                       "verschil_gemiddelde_pct": (zonder.mean() / s.mean() - 1) * 100 if s.mean() else np.nan})
        p.loc[fout, k] = np.nan
        p[k + "_begrensd"] = p[k].clip(p[k].quantile(0.01), p[k].quantile(0.99))
    lijst = pd.DataFrame(rijen)
    p["uitschieters_in_rij"] = p.set_index(["biedzone", "jaar"]).index.map(lijst.groupby(["biedzone", "jaar"]).size()).fillna(0).astype(int) if len(lijst) else 0
    return lijst, pd.DataFrame(effect), p


def schoon(p):
    """De schone dataset voor modellen: rekenfouten zijn leeg gemaakt (dat deed uitschieters al), uiterste waarden zijn
    begrensd op het 1e en 99e percentiel en het onvolledige jaar is eruit. De vlaggen blijven staan."""
    s = p[~p.deeljaar].copy()
    for k in [k for k in KERN if k + "_begrensd" in s]:
        s[k] = s[k + "_begrensd"]
    return s.drop(columns=[c for c in s.columns if c.endswith("_begrensd")])


# ---------------------------------------------------------------------------------------------------------------- 6
def drijfveren(p):
    """Belang van elk kenmerk voor vier doelvariabelen volgens vier methoden, met rangorde per methode."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.feature_selection import mutual_info_regression
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import train_test_split
    v = p[~p.deeljaar]
    uit = []
    for doel, weg in DOELEN.items():
        for kenmerkset, kandidaten in (("structuur", STRUCTUUR), ("markt", KERN + ["jaar"])):
            kenmerken = [k for k in kandidaten if k in v and k != doel and k not in weg]
            d = v[kenmerken + [doel]].dropna()
            d = d[d[doel].between(*GRENZEN.get(doel, (-np.inf, np.inf)))]
            X, y = d[kenmerken], d[doel]
            Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=1)
            woud = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=1).fit(Xtr, ytr)
            perm = permutation_importance(woud, Xte, yte, n_repeats=20, random_state=1)
            mi = mutual_info_regression(X, y, random_state=1)
            t = pd.DataFrame({"doel": doel, "kenmerkset": kenmerkset, "kenmerk": kenmerken, "spearman": [rang(X[k], y) for k in kenmerken],
                              "wederzijdse_informatie": mi, "bosmodel": woud.feature_importances_, "permutatie": perm.importances_mean})
            t["rang_spearman"] = t.spearman.abs().rank(ascending=False).astype(int)
            for k in ("wederzijdse_informatie", "bosmodel", "permutatie"):
                t["rang_" + k] = t[k].rank(ascending=False).astype(int)
            rangen = [c for c in t.columns if c.startswith("rang_")]
            t["gemiddelde_rang"] = t[rangen].mean(axis=1)
            t["in_top3_bij_methoden"] = (t[rangen] <= 3).sum(axis=1)
            t["r2_testset"], t["n"] = float(woud.score(Xte, yte)), len(d)
            uit.append(t.sort_values("gemiddelde_rang"))
    return pd.concat(uit, ignore_index=True)


def tweelingen(p, grens=0.8):
    """Paren kenmerken die vrijwel hetzelfde meten (rangcorrelatie boven de grens)."""
    v = p[~p.deeljaar]
    kol = [k for k in KERN if k in v]
    return pd.DataFrame([{"kenmerk_1": a, "kenmerk_2": b, "spearman": rang(v[a], v[b])} for i, a in enumerate(kol) for b in kol[i + 1:]
                         if abs(rang(v[a], v[b])) > grens])


def main(data=DATA, uit=None):
    uit = uit or data
    os.makedirs(uit, exist_ok=True)
    schrijf = lambda df, naam: (df.to_csv(os.path.join(uit, naam), index=False), print(f"  -> {naam}: {len(df)} rijen"))
    prof, waarden = profiel(data)
    schrijf(prof, "fact_profiel_DA.csv"); schrijf(waarden, "fact_waarden_DA.csv")
    p = paneel(data)
    schrijf(correlaties(p), "fact_correlatie_DA.csv")
    p, segprof, g, kkeuze = segmenten(p)
    schrijf(segprof, "fact_segmentprofiel_DA.csv"); schrijf(g, "fact_gedragssegment_DA.csv"); schrijf(kkeuze, "fact_clusterkeuze_DA.csv")
    schrijf(tijdpatronen(data), "fact_tijd_DA.csv")
    lijst, effect, p = uitschieters(p)
    schrijf(lijst, "fact_uitschieters_DA.csv"); schrijf(effect, "fact_uitschieters_effect_DA.csv")
    schrijf(p, "fact_zonejaar_DA.csv"); schrijf(schoon(p), "fact_zonejaar_schoon_DA.csv")
    try:
        schrijf(drijfveren(p), "fact_drijfveren_DA.csv"); schrijf(tweelingen(p), "fact_tweelingen_DA.csv")
    except ImportError:
        print("  drijfveren overgeslagen: scikit-learn ontbreekt (pip install scikit-learn)")
    return p


if __name__ == "__main__":
    main(*sys.argv[1:3])
