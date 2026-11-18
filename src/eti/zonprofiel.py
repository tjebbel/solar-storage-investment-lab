"""Toets van de Nederlandse zonreeks: klopt de vorm, ook al klopt het niveau niet?

De uurreeks solar_mw in fact_nl_uur_alle_jaren telt maar een klein deel van de Nederlandse zonne-opwek (de bron meet
vooral grote parken; daken ontbreken). Voor een capture rate is alleen de vorm van het profiel nodig, niet het niveau.
Deze module vergelijkt daarom per jaar de gemeten reeks met een profiel uit instraling (gemiddelde van vijf plaatsen,
Open-Meteo) en met het jaartotaal van Ember, en levert de schaalfactor naar het landelijke totaal.

Twee dingen die de toets zichtbaar maakt:
- De straling van Open-Meteo is gestempeld op het eind van het uur. Uitgelijnd op het begin van het uur volgt de gemeten
  reeks de instraling duidelijk beter (kolommen correlatie_uur en correlatie_uur_stempel).
- De gemeten parken leveren bij negatieve prijzen minder dan de zon toelaat: ze schakelen af. Daardoor ligt hun capture
  rate boven die van een profiel zonder afschakelen (kolom opbrengst_bij_negatieve_prijs).

Schrijft powerbi/data/fact_nl_zonprofiel_toets.csv.   Gebruik:  PYTHONPATH=src python3 -m eti.zonprofiel
"""
import os

import numpy as np
import pandas as pd

DATA = "powerbi/data"
STERKE_ZON = 250                                              # W per m2: genoeg licht om afschakelen te kunnen zien


def laad(data=DATA):
    u = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), usecols=["timestamp_utc", "jaar", "maand", "uur", "prijs_eur_mwh", "solar_mw"])
    w = pd.read_csv(os.path.join(data, "fact_weer_uur.csv"), usecols=["timestamp_utc", "straling_w_m2"])
    w = w.groupby("timestamp_utc").straling_w_m2.mean()
    begin = pd.Series(w.values, index=(pd.to_datetime(w.index) - pd.Timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"))      # naar het begin van het uur
    u["instraling"], u["instraling_stempel"] = u.timestamp_utc.map(begin), u.timestamp_utc.map(w)
    e = pd.read_csv(os.path.join(data, "fact_ember_opwek_jaar.csv"), low_memory=False)
    e = e[(e["ISO 3 code"] == "NLD") & (e["Electricity source"] == "Solar")].set_index("Year")
    return u, e


def capture(prijs, gewicht):
    ok = prijs.notna() & gewicht.notna()
    return float((prijs[ok] * gewicht[ok]).sum() / gewicht[ok].sum() / prijs[ok].mean()) if gewicht[ok].sum() > 0 else np.nan


def afschakelen(t):
    """Opbrengst per eenheid instraling in uren met een negatieve prijs, gedeeld door die in alle uren met sterke zon
    (april tot en met september). 1 = de parken draaien door, 0,6 = ze leveren 60 procent van wat de zon toelaat."""
    z = t[(t.instraling > STERKE_ZON) & t.maand.between(4, 9)]
    neg = z[z.prijs_eur_mwh < 0]
    if len(neg) < 20 or z.instraling.sum() == 0:
        return len(neg), np.nan
    return len(neg), float((neg.solar_mw.sum() / neg.instraling.sum()) / (z.solar_mw.sum() / z.instraling.sum()))


def toets(data=DATA):
    u, e = laad(data)
    rijen = []
    for jaar, t in u.groupby("jaar"):
        dag = t.assign(dag=t.timestamp_utc.str[:10]).groupby("dag")[["solar_mw", "instraling"]].sum()
        zomer = t.maand.between(4, 9)
        gemeten_twh = t.solar_mw.sum() / 1e6
        ember_twh = float(e["Generation (TWh)"].get(jaar, np.nan))
        vol = len(t) >= 8700                                    # het lopende jaar is niet te vergelijken met een jaartotaal
        uren_neg, verhouding = afschakelen(t)
        rijen.append({"jaar": jaar, "uren": len(t), "gemeten_twh": gemeten_twh, "ember_twh": ember_twh, "ember_vermogen_gw": float(e["Capacity (GW)"].get(jaar, np.nan)),
                      "dekking": gemeten_twh / ember_twh if vol and ember_twh else np.nan, "schaal_naar_ember": ember_twh / gemeten_twh if vol and gemeten_twh else np.nan,
                      "capture_gemeten": capture(t.prijs_eur_mwh, t.solar_mw), "capture_instraling": capture(t.prijs_eur_mwh, t.instraling),
                      "capture_instraling_stempel": capture(t.prijs_eur_mwh, t.instraling_stempel),
                      "correlatie_uur": float(t.solar_mw.corr(t.instraling)), "correlatie_uur_stempel": float(t.solar_mw.corr(t.instraling_stempel)),
                      "correlatie_dag": float(dag.solar_mw.corr(dag.instraling)), "negatieve_uren_met_zon": uren_neg, "opbrengst_bij_negatieve_prijs": verhouding,
                      "zomerhalfjaar_gemeten": float(t[zomer].solar_mw.sum() / t.solar_mw.sum()), "zomerhalfjaar_instraling": float(t[zomer].instraling.sum() / t.instraling.sum())})
    uit = pd.DataFrame(rijen)
    uit["verschil_capture"] = uit.capture_gemeten - uit.capture_instraling
    uit["fout_door_stempel"] = uit.capture_instraling_stempel - uit.capture_instraling
    return uit


def main(data=DATA):
    t = toets(data)
    t.round(4).to_csv(os.path.join(data, "fact_nl_zonprofiel_toets.csv"), index=False)
    return t


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    k = ["jaar", "dekking", "schaal_naar_ember", "capture_gemeten", "capture_instraling", "capture_instraling_stempel", "fout_door_stempel", "correlatie_uur", "correlatie_uur_stempel",
         "negatieve_uren_met_zon", "opbrengst_bij_negatieve_prijs"]
    print(main()[k].round(3).to_string(index=False))
