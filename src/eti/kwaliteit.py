"""Bewaking van de datakwaliteit, met meldingen.

Zeven soorten controles: versheid, volume, verschuiving van de verdeling, lege waarden, schema, bereik en
verwijzingen tussen tabellen. Elke controle geeft een of meer bevindingen met een ernst (kritiek, waarschuwing, info),
een status (geslaagd of gezakt) en context. De bevindingen gaan naar een logbestand; de stand van de vorige run
(aantal rijen, aandeel leeg) wordt bewaard om sprongen te zien. Bij een kritieke bevinding eindigt het script met
code 2, zodat cron of een pijplijn de publicatie kan tegenhouden.

Gebruik:  PYTHONPATH=src python3 -m eti.kwaliteit            (schema uit reports/analyse/datawoordenboek.schema.json)
Cron:     30 6 * * *  cd <repo> && PYTHONPATH=src python3 -m eti.kwaliteit || echo "datakwaliteit: kritiek"
"""
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import woordenboek

# ------------------------------------------------------------------------------------------------ instellingen
DATA = "powerbi/data"
SCHEMA = "reports/analyse/datawoordenboek.schema.json"
UIT = "resultaten/kwaliteit"
# tabel -> wat er bewaakt wordt. tijd: kolom met het tijdstip; vers: (waarschuwing, kritiek) in dagen;
# verdeling: kolommen waarvan de recente verdeling tegen de eerdere wordt gelegd; sleutel: moet uniek zijn.
TABELLEN = {
    "fact_nl_uur_alle_jaren": {"tijd": "timestamp_utc", "vers": (2, 4), "verdeling": ["prijs_eur_mwh"], "sleutel": ["timestamp_utc"]},
    "fact_onbalans_nl": {"tijd": "timestamp_utc", "vers": (2, 4), "verdeling": ["prijs_tekort_eur_mwh"], "sleutel": ["timestamp_utc"]},
    "fact_land_jaar": {"sleutel": ["biedzone", "jaar"]},
    "fact_land_maand": {"sleutel": ["land", "jaar", "maand"]},
    "fact_flex_land": {"sleutel": ["land", "jaar", "uren_opslag"]},
    "fact_tech_land": {"sleutel": ["land", "jaar", "technologie"]},
    "fact_wereld_markten": {"sleutel": ["markt", "jaar"]},
}
VERWIJZINGEN = [("fact_flex_land", "land", "fact_land_jaar", "land"), ("fact_land_maand", "land", "fact_land_jaar", "land"),
                ("fact_tech_land", "land", "fact_land_jaar", "land"), ("fact_land_jaar", "iso3", "dim_land", "iso3")]
VOLUME_DALING, VOLUME_STIJGING = 0.01, 0.25           # minder rijen dan de vorige run is verdacht; ineens 25% meer ook
LEEG_SPRONG = 0.05                                    # aandeel leeg stijgt met meer dan 5 procentpunt
PSI_MATIG, PSI_STERK = 0.25, 1.0                      # populatiestabiliteitsindex: verschuiving van de verdeling
VENSTER_DAGEN = 30                                    # recente periode voor de verdeling
ERNST = {"kritiek": 2, "waarschuwing": 1, "info": 0}


def bevinding(controle, tabel, ernst, geslaagd, toelichting, **context):
    return {"controle": controle, "tabel": tabel, "ernst": ernst, "status": "geslaagd" if geslaagd else "gezakt", "toelichting": toelichting,
            "context": json.dumps(context, ensure_ascii=False, default=str)}


# --------------------------------------------------------------------------------------------------- controles
def versheid(tabel, df, tijd, grenzen, nu=None):
    """Hoe oud is de laatste meting? Boven de eerste grens een waarschuwing, boven de tweede kritiek."""
    nu = nu or datetime.now(timezone.utc)
    laatste = pd.to_datetime(df[tijd], utc=True).max()
    dagen = (nu - laatste).total_seconds() / 86400
    ernst = "kritiek" if dagen > grenzen[1] else "waarschuwing" if dagen > grenzen[0] else "info"
    return [bevinding("versheid", tabel, ernst, dagen <= grenzen[0], f"laatste meting {dagen:.1f} dagen oud", laatste=laatste, grens_dagen=grenzen)]


def volume(tabel, df, vorig):
    """Aantal rijen tegenover de vorige run: een daling of een sprong omhoog valt op."""
    n, was = len(df), (vorig or {}).get("rijen")
    if n == 0:
        return [bevinding("volume", tabel, "kritiek", False, "tabel is leeg", rijen=0)]
    if not was:
        return [bevinding("volume", tabel, "info", True, f"{n} rijen; geen eerdere run om mee te vergelijken", rijen=n)]
    verandering = n / was - 1
    if verandering < -VOLUME_DALING:
        return [bevinding("volume", tabel, "kritiek", False, f"{n} rijen, {-verandering:.1%} minder dan de vorige run ({was})", rijen=n, vorig=was)]
    if verandering > VOLUME_STIJGING:
        return [bevinding("volume", tabel, "waarschuwing", False, f"{n} rijen, {verandering:.1%} meer dan de vorige run ({was})", rijen=n, vorig=was)]
    return [bevinding("volume", tabel, "info", True, f"{n} rijen ({verandering:+.2%} tegenover de vorige run)", rijen=n, vorig=was)]


def psi(referentie, recent, bakken=10):
    """Populatiestabiliteitsindex tussen twee steekproeven (0 = gelijk; boven 0,25 een duidelijke verschuiving)."""
    referentie, recent = np.asarray(referentie, float), np.asarray(recent, float)
    grenzen = np.unique(np.quantile(referentie, np.linspace(0, 1, bakken + 1)))
    if len(grenzen) < 3:
        return 0.0
    grenzen[0], grenzen[-1] = -np.inf, np.inf
    a = np.histogram(referentie, grenzen)[0] / len(referentie)
    b = np.histogram(recent, grenzen)[0] / len(recent)
    a, b = np.clip(a, 1e-4, None), np.clip(b, 1e-4, None)
    return float(((b - a) * np.log(b / a)).sum())


def verschuiving(tabel, df, tijd, kolommen, dagen=VENSTER_DAGEN):
    """Legt de laatste `dagen` dagen van een kolom naast alles daarvoor."""
    uit, t = [], pd.to_datetime(df[tijd], utc=True)
    grens = t.max() - pd.Timedelta(days=dagen)
    for k in kolommen:
        ref, rec = df.loc[t <= grens, k].dropna(), df.loc[t > grens, k].dropna()
        if len(ref) < 100 or len(rec) < 30:
            uit.append(bevinding("verschuiving", tabel, "info", True, f"{k}: te weinig waarnemingen voor een vergelijking", kolom=k))
            continue
        waarde = psi(ref, rec)
        # Een verschuiving is een signaal om te kijken, geen reden om te stoppen: een echte marktschok ziet er net zo
        # uit als een fout in de bron. Daarom hooguit een waarschuwing; kritiek is voorbehouden aan kapotte data.
        ernst = "waarschuwing" if waarde > PSI_STERK else "info"
        sterkte = "sterke verschuiving, " if waarde > PSI_STERK else "matige verschuiving, " if waarde > PSI_MATIG else ""
        uit.append(bevinding("verschuiving", tabel, ernst, waarde <= PSI_MATIG,
                             f"{k}: {sterkte}PSI {waarde:.2f}; mediaan laatste {dagen} dagen {rec.median():.1f} tegen {ref.median():.1f} daarvoor", kolom=k, psi=round(waarde, 3)))
    return uit


def lege_waarden(tabel, df, vorig):
    """Aandeel leeg per kolom tegenover de vorige run."""
    uit, was = [], (vorig or {}).get("leeg", {})
    nu = df.isna().mean()
    for k, aandeel in nu.items():
        if k in was and aandeel - was[k] > LEEG_SPRONG:
            uit.append(bevinding("lege waarden", tabel, "waarschuwing", False, f"{k}: {aandeel:.1%} leeg, was {was[k]:.1%}", kolom=k))
    return uit or [bevinding("lege waarden", tabel, "info", True, "geen sprong in het aandeel lege waarden", hoogste=round(float(nu.max()), 3) if len(nu) else 0)]


def schema_en_bereik(tabel, df, schema):
    """Schema (kolommen, typen, verplichte velden) en bereik (grenzen, toegestane waarden) volgens het datawoordenboek."""
    if tabel not in schema.get("$defs", {}):
        return [bevinding("schema", tabel, "waarschuwing", False, "tabel staat niet in het datawoordenboek")]
    fouten = woordenboek.valideer(df, schema["$defs"][tabel])
    uit = []
    for soort, kolom, tekst in fouten:
        structuur = soort in ("kolom ontbreekt", "nieuwe kolom", "verkeerd type")
        ernst = "kritiek" if soort in ("kolom ontbreekt", "verkeerd type") else "waarschuwing"
        uit.append(bevinding("schema" if structuur else "bereik", tabel, ernst, False, f"{kolom}: {soort} ({tekst})", kolom=kolom))
    for naam in ("schema", "bereik"):
        if not any(b["controle"] == naam for b in uit):
            uit.append(bevinding(naam, tabel, "info", True, "in orde volgens het datawoordenboek"))
    return uit


def sleutel(tabel, df, kolommen):
    """De sleutel mag niet leeg zijn en niet dubbel voorkomen."""
    leeg = int(df[kolommen].isna().any(axis=1).sum())
    dubbel = int(df.duplicated(kolommen).sum())
    if leeg or dubbel:
        return [bevinding("sleutel", tabel, "kritiek", False, f"{leeg} rijen met een lege sleutel, {dubbel} dubbele sleutels", sleutel=kolommen)]
    return [bevinding("sleutel", tabel, "info", True, "sleutel is gevuld en uniek", sleutel=kolommen)]


def verwijzing(kind, kindkolom, ouder, ouderkolom, tabellen):
    """Elke waarde in de kindtabel moet in de oudertabel voorkomen."""
    if kind not in tabellen or ouder not in tabellen:
        return [bevinding("verwijzing", kind, "waarschuwing", False, f"{kind} of {ouder} ontbreekt")]
    wees = sorted(set(tabellen[kind][kindkolom].dropna()) - set(tabellen[ouder][ouderkolom].dropna()))
    if wees:
        return [bevinding("verwijzing", kind, "waarschuwing", False, f"{len(wees)} waarden van {kindkolom} staan niet in {ouder}.{ouderkolom}", voorbeelden=wees[:5])]
    return [bevinding("verwijzing", kind, "info", True, f"{kindkolom} verwijst overal naar {ouder}.{ouderkolom}")]


# ------------------------------------------------------------------------------------------------------ draaien
def controleer(data=DATA, schema_pad=SCHEMA, stand=None, nu=None):
    """Draait alle controles. Geeft (bevindingen als DataFrame, nieuwe stand voor de volgende run)."""
    schema = json.load(open(schema_pad, encoding="utf-8")) if os.path.exists(schema_pad) else {}
    stand, nieuw, uit, tabellen = stand or {}, {}, [], {}
    for tabel in sorted(set(TABELLEN) | {v[2] for v in VERWIJZINGEN}):
        pad = os.path.join(data, tabel + ".csv")
        if not os.path.exists(pad):
            uit.append(bevinding("volume", tabel, "kritiek", False, "bestand ontbreekt", pad=pad))
            continue
        try:
            df = pd.read_csv(pad, low_memory=False)
        except Exception as e:                                       # een onleesbaar bestand is zelf een bevinding
            uit.append(bevinding("schema", tabel, "kritiek", False, f"bestand is niet te lezen: {type(e).__name__}: {e}"))
            continue
        tabellen[tabel] = df
        inst = TABELLEN.get(tabel, {})
        uit += volume(tabel, df, stand.get(tabel))
        uit += lege_waarden(tabel, df, stand.get(tabel))
        if schema:
            uit += schema_en_bereik(tabel, df, schema)
        if "sleutel" in inst:
            uit += sleutel(tabel, df, inst["sleutel"])
        if "tijd" in inst:
            uit += versheid(tabel, df, inst["tijd"], inst["vers"], nu)
            uit += verschuiving(tabel, df, inst["tijd"], inst.get("verdeling", []))
        nieuw[tabel] = {"rijen": len(df), "leeg": {k: float(v) for k, v in df.isna().mean().items()}}
    for v in VERWIJZINGEN:
        uit += verwijzing(*v, tabellen)
    if not schema:
        uit.append(bevinding("schema", "(alle)", "waarschuwing", False, f"{schema_pad} ontbreekt: draai eerst eti.da en eti.woordenboek"))
    b = pd.DataFrame(uit)
    b.insert(0, "moment", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    return b, nieuw


def samenvatting(b):
    """Tekst voor het scherm, de mail of het rapport: eerst wat mis is, het ergste bovenaan."""
    mis = b[b.status == "gezakt"].assign(rang=lambda d: d.ernst.map(ERNST)).sort_values("rang", ascending=False)
    telling = {e: int(((b.status == "gezakt") & (b.ernst == e)).sum()) for e in ("kritiek", "waarschuwing")}
    regels = [f"Datakwaliteit: {len(b)} controles, {int((b.status == 'geslaagd').sum())} geslaagd, {telling['kritiek']} kritiek, {telling['waarschuwing']} waarschuwing."]
    regels += [f"  [{r.ernst}] {r.tabel} / {r.controle}: {r.toelichting}" for r in mis.itertuples()]
    return "\n".join(regels), telling


def main(data=DATA, uit=UIT, schema_pad=SCHEMA):
    os.makedirs(uit, exist_ok=True)
    standpad, logpad = os.path.join(uit, "stand.json"), os.path.join(uit, "kwaliteit_log.csv")
    stand = json.load(open(standpad, encoding="utf-8")) if os.path.exists(standpad) else {}
    b, nieuw = controleer(data, schema_pad, stand)
    b.to_csv(logpad, mode="a", index=False, header=not os.path.exists(logpad))
    with open(standpad, "w", encoding="utf-8") as fh:
        json.dump(nieuw, fh)
    tekst, telling = samenvatting(b)
    with open(os.path.join(uit, "laatste_run.txt"), "w", encoding="utf-8") as fh:
        fh.write(tekst + "\n")
    print(tekst)
    return 2 if telling["kritiek"] else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
