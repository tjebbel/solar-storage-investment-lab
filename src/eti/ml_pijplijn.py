"""ML-pijplijn: welke biedzones verdienen volgend jaar meer dan de Europese mediaan met een batterij?

Doel: de batterij-omzet van een zone in jaar t+1, gedeeld door de mediaan van alle zones in dat jaar (1 = mediaan).
Het niveau van volgend jaar hangt aan de gasprijs en is uit deze data niet te voorspellen; de plaats in de rangorde
wel. Het model leert de verandering ten opzichte van dit jaar, zodat 'geen verandering' altijd binnen bereik is.
Kenmerken: de stand van jaar t (omzet, dagspreiding, prijs, capture rate, opwekmix), afgeleide kenmerken en de regio.
De toets is streng: kruisvalidatie laat steeds een heel doeljaar weg, en het laatste doeljaar blijft apart als
eindtoets. De lat is 'volgend jaar is gelijk aan dit jaar'. Een model wordt alleen aanbevolen als het in de
kruisvalidatie minstens 5% onder de lat komt; anders is de lat zelf de aanbeveling.

Gebruik:  PYTHONPATH=src python3 -m eti.ml_pijplijn            trainen, vergelijken, bewaren (resultaten/ml)
          PYTHONPATH=src python3 -m eti.ml_pijplijn voorspel   het bewaarde model toepassen op het laatste jaar
Nodig: scikit-learn en joblib.
"""
import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

from . import da

DATA, UIT = "powerbi/data", "resultaten/ml"
MODEL, META = "batterij_verhouding.joblib", "batterij_verhouding.json"
GETALLEN = ["verhouding", "groei_verhouding", "dagspreiding_tov_prijs", "prijs_tov_mediaan", "capture_zon", "negatieve_uren", "voorspel_ratio",
            "aandeel_zon_pct", "aandeel_wind_pct", "aandeel_kern_pct", "aandeel_gas_pct", "aandeel_waterkracht_pct", "log_vraag"]
CATEGORIE = ["regio"]
DOEL = "verhouding_volgend_jaar"
VERANDERING = "verandering_volgend_jaar"          # wat het model leert: doel min de verhouding van dit jaar
MARGE = 0.05                                      # zoveel beter dan de lat moet een model in de kruisvalidatie zijn


# ------------------------------------------------------------------------------------------------- kenmerken
def _lees_json(pad):
    with open(pad, encoding="utf-8") as fh:
        return json.load(fh)


def kenmerken(p):
    """Een rij per zone en jaar t met de kenmerken van dat jaar en, waar bekend, het doel van jaar t+1."""
    p = p[p.batterij_per_mw.notna()].sort_values(["biedzone", "jaar"]).copy()
    p["mediaan_omzet"] = p.groupby("jaar").batterij_per_mw.transform("median")
    p["verhouding"] = p.batterij_per_mw / p.mediaan_omzet
    p["groei_verhouding"] = p.verhouding - p.groupby("biedzone").verhouding.shift(1)
    p["dagspreiding_tov_prijs"] = p.dagspreiding / p.gem_prijs
    p["prijs_tov_mediaan"] = p.gem_prijs / p.groupby("jaar").gem_prijs.transform("median")
    p["log_vraag"] = np.log(p.vraag_twh)
    p["capture_zon"] = p.capture_zon.where(p.capture_zon.between(0, 2))
    p[DOEL] = p.groupby("biedzone").verhouding.shift(-1)
    p[VERANDERING] = p[DOEL] - p.verhouding
    p["doeljaar"] = p.jaar + 1
    p["doel_onvolledig"] = p.groupby("biedzone").deeljaar.shift(-1, fill_value=False).astype(bool)       # zelfde uitkomst in pandas 2 en 3
    return p.dropna(subset=["groei_verhouding"])


def splits(k):
    """Trainen op hele doeljaren behalve het laatste; dat laatste hele doeljaar is de eindtoets; een onvolledig
    doeljaar is een extra blik vooruit; rijen zonder doel zijn de voorspelling."""
    bekend = k[k[DOEL].notna()]
    heel = bekend[~bekend.doel_onvolledig]
    laatste = heel.doeljaar.max()
    return heel[heel.doeljaar < laatste], heel[heel.doeljaar == laatste], bekend[bekend.doel_onvolledig], k[k[DOEL].isna()]


# ---------------------------------------------------------------------------------------------------- modellen
def pijplijn(model):
    from sklearn.compose import ColumnTransformer
    from sklearn.feature_selection import SelectKBest, f_regression
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    voor = ColumnTransformer([("getal", Pipeline([("vul", SimpleImputer(strategy="median")), ("schaal", StandardScaler())]), GETALLEN),
                              ("categorie", OneHotEncoder(handle_unknown="ignore"), CATEGORIE)])
    return Pipeline([("voorbewerking", voor), ("keuze", SelectKBest(f_regression, k="all")), ("model", model)])


def kandidaten():
    """Vier soorten modellen met een klein zoekrooster. k = aantal kenmerken dat de keuzestap doorlaat."""
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.neighbors import KNeighborsRegressor
    return {
        "ridge": (Ridge(), {"model__alpha": [0.1, 1.0, 10.0, 100.0], "keuze__k": [4, 8, "all"]}),
        "bosmodel": (RandomForestRegressor(n_estimators=300, random_state=1), {"model__max_depth": [3, 6, None], "model__min_samples_leaf": [2, 5], "keuze__k": [8, "all"]}),
        "gradient boosting": (GradientBoostingRegressor(random_state=1), {"model__n_estimators": [100, 300], "model__learning_rate": [0.03, 0.1], "model__max_depth": [2, 3], "keuze__k": ["all"]}),
        "naaste buren": (KNeighborsRegressor(), {"model__n_neighbors": [3, 5, 9, 15], "keuze__k": [4, 8]}),
    }


def maten(echt, voorspeld):
    e = np.asarray(echt) - np.asarray(voorspeld)
    return {"rmse": float(np.sqrt((e ** 2).mean())), "mae": float(np.abs(e).mean()),
            "r2": float(1 - (e ** 2).sum() / ((np.asarray(echt) - np.mean(echt)) ** 2).sum())}


def train(data=DATA, uit=UIT):
    """Vergelijkt de modellen, kiest op de kruisvalidatie, toetst op het aparte jaar en bewaart model en verslag."""
    import joblib
    import sklearn
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import GridSearchCV, LeaveOneGroupOut
    k = kenmerken(da.paneel(data))
    tr, te, vooruit, nieuw = splits(k)
    X, y, groepen = tr[GETALLEN + CATEGORIE], tr[VERANDERING], tr.doeljaar
    rijen, gevonden = [], {}
    lat_cv = [maten(g[DOEL], g.verhouding)["rmse"] for _, g in tr.groupby("doeljaar")]
    rijen.append({"model": "lat: gelijk aan dit jaar", "cv_rmse": float(np.mean(lat_cv)), **{"toets_" + a: b for a, b in maten(te[DOEL], te.verhouding).items()}})
    for naam, (model, rooster) in kandidaten().items():
        zoek = GridSearchCV(pijplijn(model), rooster, cv=LeaveOneGroupOut(), scoring="neg_root_mean_squared_error", n_jobs=1)
        zoek.fit(X, y, groups=groepen)
        gevonden[naam] = zoek
        rijen.append({"model": naam, "cv_rmse": float(-zoek.best_score_), "beste_instelling": json.dumps(zoek.best_params_),
                      **{"toets_" + a: b for a, b in maten(te[DOEL], te.verhouding + zoek.predict(te[GETALLEN + CATEGORIE])).items()}})
    tabel = pd.DataFrame(rijen)
    beste = tabel[tabel.model != "lat: gelijk aan dit jaar"].sort_values("cv_rmse").model.iloc[0]      # kiezen op kruisvalidatie, nooit op de toets
    tabel["gekozen"] = tabel.model == beste
    lat_rmse = tabel.cv_rmse.iloc[0]
    tabel["verbetering_op_de_lat_cv"] = 1 - tabel.cv_rmse / lat_rmse
    aanbevolen = beste if tabel.loc[tabel.gekozen, "cv_rmse"].iloc[0] <= (1 - MARGE) * lat_rmse else "lat: gelijk aan dit jaar"
    model = gevonden[beste].best_estimator_
    voorspeld = te.verhouding + model.predict(te[GETALLEN + CATEGORIE])
    pi = permutation_importance(model, te[GETALLEN + CATEGORIE], te[VERANDERING], n_repeats=30, random_state=1, scoring="neg_root_mean_squared_error")
    belang = pd.DataFrame({"kenmerk": GETALLEN + CATEGORIE, "toename_fout_bij_schudden": pi.importances_mean, "spreiding": pi.importances_std}).sort_values("toename_fout_bij_schudden", ascending=False)
    diag = te.assign(voorspeld=voorspeld, fout=voorspeld - te[DOEL])
    per_regio = diag.groupby("regio").agg(zones=("biedzone", "size"), gemiddelde_fout=("fout", "mean"), mae=("fout", lambda s: s.abs().mean())).reset_index()
    os.makedirs(uit, exist_ok=True)
    eind = pijplijn(gevonden[beste].best_estimator_.named_steps["model"]).set_params(**gevonden[beste].best_params_)
    alles = pd.concat([tr, te])
    eind.fit(alles[GETALLEN + CATEGORIE], alles[VERANDERING])          # eindmodel op alle hele jaren, voor de voorspelling vooruit
    joblib.dump(eind, os.path.join(uit, MODEL))
    meta = {"doel": DOEL, "kenmerken": GETALLEN + CATEGORIE, "model": beste, "aanbevolen": aanbevolen, "instelling": gevonden[beste].best_params_, "getraind_op": str(date.today()),
            "doeljaren_training": sorted(int(j) for j in tr.doeljaar.unique()), "toetsjaar": int(te.doeljaar.iloc[0]), "sklearn": sklearn.__version__,
            "toets": maten(te[DOEL], voorspeld), "lat": maten(te[DOEL], te.verhouding), "rijen_training": len(tr)}
    with open(os.path.join(uit, META), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1, default=str)
    tabel.to_csv(os.path.join(uit, "modelvergelijking.csv"), index=False)
    belang.to_csv(os.path.join(uit, "belang_kenmerken.csv"), index=False)
    per_regio.to_csv(os.path.join(uit, "fout_per_regio.csv"), index=False)
    diag[["biedzone", "regio", "jaar", "doeljaar", "verhouding", DOEL, "voorspeld", "fout"]].to_csv(os.path.join(uit, "toets_per_zone.csv"), index=False)
    figuur(diag, meta, uit)
    if len(vooruit):                                                    # blik vooruit: het onvolledige jaar
        v = vooruit.assign(voorspeld=vooruit.verhouding + eind.predict(vooruit[GETALLEN + CATEGORIE]))
        meta["onvolledig_jaar"] = {"jaar": int(v.doeljaar.iloc[0]), **maten(v[DOEL], v.voorspeld), "lat_rmse": maten(v[DOEL], v.verhouding)["rmse"]}
        with open(os.path.join(uit, META), "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=1, default=str)
    return tabel, belang, meta


def figuur(diag, meta, uit):
    """Voorspeld tegen werkelijk voor het toetsjaar."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from . import vis
    vis.stijl()
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    grens = [0, max(diag[DOEL].max(), diag.voorspeld.max()) * 1.08]
    ax.plot(grens, grens, color=vis.K["gedempt"], lw=0.8)
    ax.scatter(diag[DOEL], diag.voorspeld, s=42, color=vis.K["blauw"], edgecolor=vis.K["vlak"], linewidth=1.2, zorder=3)
    for r in diag.reindex(diag.fout.abs().sort_values(ascending=False).index).head(4).itertuples():
        ax.annotate(r.biedzone, (getattr(r, DOEL), r.voorspeld), xytext=(5, 4), textcoords="offset points", fontsize=8.5, color=vis.K["inkt2"])
    ax.set_xlim(grens); ax.set_ylim(grens); ax.grid(axis="x")
    ax.set_xlabel(f"werkelijk in {meta['toetsjaar']} (1 = Europese mediaan)"); ax.set_ylabel("voorspeld")
    vis.kop(fig, f"Model {meta['toets']['rmse']:.2f} tegen lat {meta['lat']['rmse']:.2f}: fout in de rangorde van zones".replace("0.", "0,"),
            f"Batterij-omzet ten opzichte van de mediaan, toetsjaar {meta['toetsjaar']}. Op de lijn is de voorspelling goed.", "Bron: eigen model (eti.ml_pijplijn).")
    fig.savefig(os.path.join(uit, "voorspeld_tegen_werkelijk.png"))
    plt.close(fig)


# -------------------------------------------------------------------------------------------------- toepassen
def voorspel(rijen, uit=UIT):
    """Past het bewaarde model toe op nieuwe rijen met de kolommen uit het verslag: de verhouding van volgend jaar is
    die van dit jaar plus de voorspelde verandering. Controleert eerst de invoer."""
    import joblib
    meta = _lees_json(os.path.join(uit, META))
    ontbreekt = [k for k in meta["kenmerken"] if k not in rijen.columns]
    if ontbreekt:
        raise ValueError("kolommen ontbreken voor de voorspelling: " + ", ".join(ontbreekt))
    return rijen["verhouding"].values + joblib.load(os.path.join(uit, MODEL)).predict(rijen[meta["kenmerken"]])


def vooruitblik(data=DATA, uit=UIT):
    """Voorspelling voor het jaar na het laatste jaar in de data: welke zones boven de mediaan uitkomen."""
    k = kenmerken(da.paneel(data))
    laatste = k[k.jaar == k.jaar.max()].copy()
    laatste["voorspeld"] = voorspel(laatste, uit)
    meta = _lees_json(os.path.join(uit, META))
    laatste["aanbevolen"] = laatste.voorspeld if meta["aanbevolen"] == meta["model"] else laatste.verhouding     # haalde het model de lat niet, dan geldt de lat
    t = laatste[["biedzone", "land", "regio", "jaar", "doeljaar", "verhouding", "voorspeld", "aanbevolen"]].sort_values("aanbevolen", ascending=False)
    t.to_csv(os.path.join(uit, "vooruitblik.csv"), index=False)
    return t


def main(opdracht="train", data=DATA, uit=UIT):
    if opdracht == "voorspel":
        t = vooruitblik(data, uit)
        print(t.head(10).round(2).to_string(index=False))
        return t
    tabel, belang, meta = train(data, uit)
    print(tabel.drop(columns=["beste_instelling"]).round(3).to_string(index=False))
    print("belangrijkste kenmerken:", ", ".join(f"{r.kenmerk} ({r.toename_fout_bij_schudden:.3f})" for r in belang.head(4).itertuples()))
    print("verslag:", {k: meta[k] for k in ("model", "aanbevolen", "toetsjaar", "toets", "lat") if k in meta}, meta.get("onvolledig_jaar", ""))
    vooruitblik(data, uit)
    return tabel


if __name__ == "__main__":
    main(*sys.argv[1:4])
