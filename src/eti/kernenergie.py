"""Kernenergie in de uurdata: wat is een kWh uit een kerncentrale waard, en hoe flexibel draait de vloot?

Leest de maandbestanden die al in data/raw staan (Energy-Charts: prijs en opwek per bron per biedzone); internet is
niet nodig. Per biedzone en jaar:
- capture rate en capture price van kernenergie, met dezelfde definitie als voor zon en wind;
- het deel van de productie dat in uren met een negatieve prijs valt;
- modulatie: de productie in negatieve uren gedeeld door de productie in de overige uren van dezelfde dag, en de
  mediane daguitslag (hoogste min laagste uur, als deel van het hoogste uur);
- benutting: gemiddelde productie gedeeld door het opgestelde vermogen, en door de hoogste uurproductie van de reeks.
Daarnaast een verband op landniveau: hangt het aandeel kernenergie (Ember) samen met de dagspreiding, de
batterij-omzet, de negatieve uren en de capture rate van zon?

Schrijft powerbi/data/fact_kernenergie_land_jaar.csv en fact_kernenergie_verband.csv.
Gebruik:  PYTHONPATH=src python3 -m eti.kernenergie
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

from . import verbanden

OUT, RAW = "powerbi/data", "data/raw"
GEEN_OPWEK = ("consumption", "load", "cross border", "renewable share")      # reeksen die geen opwek zijn
BESTAND = re.compile(r"^power_(.+)_(\d{4})_(\d{2})\.json$")
LANDELIJK = {"SE1", "SE2", "SE4"}      # Energy-Charts geeft voor elke Zweedse zone de landelijke opwek; de centrales staan in SE3


def uurreeks(opwek, prijs):
    """Energy-Charts public_power en price van een maand -> DataFrame per uur (UTC) met prijs, kern en totaal (MWh per
    uur). Kwartierwaarden worden per uur gemiddeld. Geeft None als de zone geen reeks 'Nuclear' heeft."""
    tijd = pd.to_datetime(opwek.get("unix_seconds") or [], unit="s", utc=True)
    kern, totaal = None, pd.Series(0.0, index=tijd)
    for reeks in opwek.get("production_types") or []:
        naam = reeks["name"].lower()
        if any(x in naam for x in GEEN_OPWEK) or len(reeks["data"]) != len(tijd):
            continue
        waarden = pd.to_numeric(pd.Series(reeks["data"], index=tijd), errors="coerce").clip(lower=0)
        totaal = totaal + waarden.fillna(0)
        if naam == "nuclear":
            kern = waarden
    if kern is None or not len(tijd):
        return None
    per_uur = pd.DataFrame({"kern": kern, "totaal": totaal}).resample("h").mean()
    p = pd.Series(pd.to_numeric(pd.Series(prijs.get("price") or []), errors="coerce").values,
                  index=pd.to_datetime(prijs.get("unix_seconds") or [], unit="s", utc=True)).resample("h").mean()
    return per_uur.join(p.rename("prijs"), how="inner").dropna(subset=["prijs", "kern"])


def lees_zone(zone, raw=RAW):
    """Alle maanden van een zone achter elkaar; None als de zone geen kernenergie heeft."""
    delen = []
    for naam in sorted(os.listdir(raw)):
        m = BESTAND.match(naam)
        if not m or m.group(1) != zone:
            continue
        prijspad = os.path.join(raw, naam.replace("power_", "price_", 1))
        if not os.path.exists(prijspad):
            continue
        try:
            deel = uurreeks(json.load(open(os.path.join(raw, naam))), json.load(open(prijspad)))
        except (ValueError, KeyError):
            continue
        if deel is None:
            if not delen:
                return None                 # de eerste maand heeft geen reeks 'Nuclear': zone zonder kernenergie
            continue                        # later weggevallen (Duitsland na april 2023)
        delen.append(deel)
    if not delen:
        return None
    u = pd.concat(delen)
    return u[~u.index.duplicated()].sort_index()


def kengetallen(u, top=None, vermogen_mw=None):
    """Kengetallen van een jaar. top: hoogste uurproductie van de hele reeks; vermogen_mw: opgesteld vermogen."""
    if u is None or len(u) < 24 * 30 or u.kern.sum() <= 0:
        return None
    neg = u.prijs < 0
    verhouding, uitslag = [], []
    for _, d in u.groupby(u.index.date):
        n = d.prijs < 0
        if n.any() and (~n).any() and d.kern[~n].mean() > 0:
            verhouding.append(d.kern[n].mean() / d.kern[~n].mean())
        if len(d) >= 20 and d.kern.max() > 0:
            uitslag.append((d.kern.max() - d.kern.min()) / d.kern.max())
    opbrengst = float((u.prijs * u.kern).sum() / u.kern.sum())
    return {"uren": int(len(u)), "kern_twh": float(u.kern.sum() / 1e6),
            "aandeel_kern": float(u.kern.sum() / u.totaal.sum()) if u.totaal.sum() else None,
            "gem_prijs": float(u.prijs.mean()), "capture_price_kern": opbrengst, "capture_kern": opbrengst / float(u.prijs.mean()),
            "negatieve_uren": int(neg.sum()), "aandeel_in_negatieve_uren": float(u.kern[neg].sum() / u.kern.sum()),
            "productie_bij_negatieve_prijs": float(np.mean(verhouding)) if verhouding else None,
            "dagen_met_negatieve_prijs": len(verhouding),
            "daguitslag_mediaan": float(np.median(uitslag)) if uitslag else None,
            "benutting_tov_top": float(u.kern.mean() / top) if top else None,
            "benutting_tov_vermogen": float(u.kern.mean() / vermogen_mw) if vermogen_mw else None}


def zones(raw=RAW):
    return sorted({m.group(1) for m in (BESTAND.match(f) for f in os.listdir(raw)) if m})


def per_land_jaar(data=OUT, raw=RAW):
    land = pd.read_csv(os.path.join(data, "fact_land_jaar.csv"))
    naam = dict(land[["biedzone", "land"]].drop_duplicates().values)
    andere = land.set_index(["biedzone", "jaar"])[["capture_zon", "capture_wind"]]
    gw = pd.read_csv(os.path.join(data, "fact_vermogen_land.csv"))
    gw = gw[gw.technologie == "nuclear"].groupby(["land", "jaar"]).gw.sum()
    rijen = []
    for zone in zones(raw):
        if zone in LANDELIJK:
            continue
        u = lees_zone(zone, raw)
        if u is None or u.kern.sum() <= 0:
            continue
        top = float(u.kern.quantile(0.999))
        for jaar, deel in u.groupby(u.index.year):
            vermogen = gw.get((naam.get(zone), jaar))
            k = kengetallen(deel, top, vermogen * 1000 if vermogen and vermogen > 0 else None)
            if k:
                extra = andere.loc[(zone, jaar)].to_dict() if (zone, jaar) in andere.index else {}
                rijen.append({"land": naam.get(zone, zone), "biedzone": zone, "jaar": int(jaar), **k, **extra})
        print(f"  {zone}: {len(u)} uren", flush=True)
    return pd.DataFrame(rijen)


def rang(a, b):
    """Rangcorrelatie (Spearman) zonder scipy: de gewone correlatie van de rangnummers."""
    return float(a.rank().corr(b.rank()))


def verband(data=OUT):
    """Rangcorrelaties op landniveau tussen het aandeel kernenergie (Ember) en vier marktmaten."""
    z = verbanden.zonejaren(data)
    e = pd.read_csv(os.path.join(data, "fact_ember_opwek_jaar.csv"))
    e = e[(e["Electricity source"] == "Nuclear") & e["ISO 3 code"].notna()]
    e = e.rename(columns={"ISO 3 code": "iso3", "Year": "jaar", "Share of generation (%)": "aandeel_kern_pct"})
    p = (z.groupby(["iso3", "jaar"]).agg(dagspreiding=("dagspreiding", "mean"), batterij=("omzet_realistisch_per_mw", "mean"),
                                         capture_zon=("capture_zon", "mean"), negatieve_uren=("negatieve_uren", "mean")).reset_index()
          .merge(e[["iso3", "jaar", "aandeel_kern_pct"]], on=["iso3", "jaar"], how="left"))
    p["aandeel_kern_pct"] = p.aandeel_kern_pct.fillna(0.0)
    rijen = []
    for kolom, label in (("dagspreiding", "dagspreiding"), ("batterij", "batterij-omzet 2 uur"), ("capture_zon", "capture rate zon"),
                         ("negatieve_uren", "negatieve uren")):
        q = p.dropna(subset=[kolom])
        binnen = [rang(g.aandeel_kern_pct, g[kolom]) for _, g in q.groupby("jaar") if len(g) >= 8]
        rijen.append({"verband": f"aandeel kernenergie en {label}", "alle_landjaren": rang(q.aandeel_kern_pct, q[kolom]),
                      "binnen_jaren": float(np.nanmean(binnen)) if binnen else None, "landjaren": len(q), "landen": q.iso3.nunique()})
    return pd.DataFrame(rijen)


def main(data=OUT, uit=OUT, raw=RAW):
    t = per_land_jaar(data, raw)
    v = verband(data)
    os.makedirs(uit, exist_ok=True)
    t.to_csv(os.path.join(uit, "fact_kernenergie_land_jaar.csv"), index=False)
    v.to_csv(os.path.join(uit, "fact_kernenergie_verband.csv"), index=False)
    toon = t[t.jaar == 2025][["land", "kern_twh", "aandeel_kern", "capture_kern", "capture_zon", "aandeel_in_negatieve_uren",
                              "productie_bij_negatieve_prijs", "daguitslag_mediaan", "benutting_tov_vermogen"]]
    print(toon.round(3).to_string(index=False))
    print(v.round(2).to_string(index=False))
    return t, v


if __name__ == "__main__":
    main(*sys.argv[1:4])
