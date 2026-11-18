"""Balanceringsprijzen voor Nederland uit de ruwe ENTSO-E-bestanden van de nachtrun (documenttype A84).

Wat erin zit: de prijs van FCR-capaciteit per blok van vier uur (zakelijk type A95, euro per MW per uur) en de prijs
van geactiveerde aFRR-energie per kwartier, op en af (A96, euro per MWh; de bron stopt in september 2025).
Wat ontbreekt: de capaciteitsprijs van aFRR. Die reeks gaf ENTSO-E niet terug.

Schrijft powerbi/data/fact_fcr_nl.csv, fact_afrr_energie_nl.csv en fact_balans_nl_jaar.csv.
Gebruik:  PYTHONPATH=src python3 -m eti.balans
"""
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta

import pandas as pd

OUT, RAW = "powerbi/data", "data/raw"
FCR, AFRR, OP, AF = "A95", "A96", "A01", "A02"


def _kaal(tag):
    return tag.rsplit("}", 1)[-1]


def lees_reeksen(xml):
    """Een A84-document -> [(zakelijk type, richting, [(begin van het kwartier in UTC, prijs)])].
    De bron geeft alleen de punten waar de prijs verandert; elk punt geldt tot het volgende punt of het einde."""
    uit = []
    for ts in (e for e in ET.fromstring(xml).iter() if _kaal(e.tag) == "TimeSeries"):
        veld = {_kaal(c.tag): c.text for c in ts}
        for periode in (c for c in ts if _kaal(c.tag) == "Period"):
            start = einde = None
            punten = []
            for c in periode.iter():
                naam = _kaal(c.tag)
                if naam == "start":
                    start = datetime.strptime(c.text[:16], "%Y-%m-%dT%H:%M")
                elif naam == "end":
                    einde = datetime.strptime(c.text[:16], "%Y-%m-%dT%H:%M")
                elif naam == "Point":
                    p = {_kaal(x.tag): x.text for x in c}
                    if "activation_Price.amount" in p:
                        punten.append((int(p["position"]), float(p["activation_Price.amount"])))
            if start is None or einde is None or not punten:
                continue
            aantal = int((einde - start).total_seconds() // 900)
            punten.sort()
            reeks = []
            for i, (pos, prijs) in enumerate(punten):
                tot = punten[i + 1][0] if i + 1 < len(punten) else aantal + 1
                reeks += [(start + timedelta(minutes=15 * (k - 1)), prijs) for k in range(pos, min(tot, aantal + 1))]
            uit.append((veld.get("businessType"), veld.get("flowDirection.direction"), reeks))
    return uit


def lees_alles(raw=RAW):
    """Alle maandbestanden -> (FCR per kwartier, aFRR op per kwartier, aFRR af per kwartier) als Series."""
    delen = {(FCR, OP): {}, (AFRR, OP): {}, (AFRR, AF): {}}
    for pad in sorted(glob.glob(os.path.join(raw, "balans_prijs_geactiveerd_20??_??.bin"))):
        b = open(pad, "rb").read()
        docs = [zipfile.ZipFile(io.BytesIO(b)).read(n) for n in zipfile.ZipFile(io.BytesIO(b)).namelist()] if b[:2] == b"PK" else [b]
        for d in docs:
            for soort, richting, reeks in lees_reeksen(d):
                if (soort, richting) in delen:
                    delen[(soort, richting)].update(reeks)
    return [pd.Series(delen[k], dtype=float).sort_index() for k in ((FCR, OP), (AFRR, OP), (AFRR, AF))]


def jaartabel(fcr, op, af):
    """Per jaar: FCR-prijs (mediaan, gemiddelde zonder de hoogste halve procent) en wat 1 MW bij volledige inzet zou
    opleveren; voor aFRR het aandeel kwartieren met een activatieprijs en de gemiddelde prijs in die kwartieren."""
    rijen = []
    for jaar in sorted({t.year for t in fcr.index} | {t.year for t in op.index}):
        f, o, a = (s[[t.year == jaar for t in s.index]] for s in (fcr, op, af))
        rij = {"jaar": jaar}
        if len(f):
            g = f.clip(upper=f.quantile(0.995))
            rij.update({"fcr_kwartieren": len(f), "fcr_mediaan_eur_mw_uur": float(f.median()), "fcr_gemiddeld_eur_mw_uur": float(g.mean()),
                        "fcr_omzet_per_mw_bij_volledige_inzet": float(g.mean() * 8760)})
        if len(o):
            actief_op, actief_af = o[o != 0], a[a != 0]
            rij.update({"afrr_kwartieren": len(o), "afrr_op_aandeel_kwartieren": len(actief_op) / len(o),
                        "afrr_op_prijs_gemiddeld": float(actief_op.mean()) if len(actief_op) else None,
                        "afrr_af_aandeel_kwartieren": len(actief_af) / len(a) if len(a) else None,
                        "afrr_af_prijs_gemiddeld": float(actief_af.mean()) if len(actief_af) else None})
        rijen.append(rij)
    return pd.DataFrame(rijen)


def main(raw=RAW, uit=OUT):
    fcr, op, af = lees_alles(raw)
    if not len(fcr) and not len(op):
        print("  geen balansbestanden gevonden: draai eerst de stap balans_probe"); return None
    os.makedirs(uit, exist_ok=True)
    wissel = fcr[(fcr != fcr.shift()) | (fcr.index.to_series().diff() != pd.Timedelta(minutes=15))]
    wissel.rename("prijs_eur_mw_uur").rename_axis("vanaf_utc").to_csv(os.path.join(uit, "fact_fcr_nl.csv"))
    pd.DataFrame({"op_eur_mwh": op, "af_eur_mwh": af}).rename_axis("kwartier_utc").to_csv(os.path.join(uit, "fact_afrr_energie_nl.csv"))
    t = jaartabel(fcr, op, af)
    t.to_csv(os.path.join(uit, "fact_balans_nl_jaar.csv"), index=False)
    print(t.round(2).to_string(index=False))
    print(f"  FCR {fcr.index.min()} tot {fcr.index.max()}; aFRR-energie {op.index.min()} tot {op.index.max()}")
    return t


if __name__ == "__main__":
    main(*sys.argv[1:3])
