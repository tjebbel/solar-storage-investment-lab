"""Australie (NEM en WEM) uit de Open Electricity API: twee tabellen voor Tableau.

t120_australia_price_daily       dagprijs per netwerk (AUD per MWh)
t121_australia_generation_daily  opwekking per dag, regio en brandstof (MWh)

Bron: Open Electricity (CC BY-NC 4.0, niet-commercieel, met bronvermelding).
Ruwe antwoorden: data/raw/australie (niet op GitHub), opgehaald met eti.openelectricity_fetch.
Het gratis abonnement geeft alleen de laatste 730 dagen. Geen komma's in koppen of waarden.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "australie"
UIT = [ROOT / "tableau" / "data", ROOT / "tableau" / "data_en"]

GROEP = {"solar_utility": "Solar", "solar_rooftop": "Solar", "solar_thermal": "Solar",
         "wind": "Wind", "wind_offshore": "Wind", "hydro": "Hydro",
         "battery_charging": "Battery charging", "battery_discharging": "Battery discharging",
         "pumps": "Pumped hydro charging",
         "coal_black": "Coal", "coal_brown": "Coal"}


def groep(ft):
    if ft in GROEP:
        return GROEP[ft]
    if ft.startswith("gas"):
        return "Gas"
    if ft.startswith("bioenergy"):
        return "Bioenergy"
    return "Other"


def schrijf(naam, kop, rijen):
    for map_ in UIT:
        with open(map_ / naam, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(kop)
            w.writerows(rijen)
    assert all("," not in str(v) for r in rijen for v in r), naam
    print(naam, len(rijen), "rijen")


def reeksen(patroon):
    for pad in sorted(RAW.glob(patroon)):
        for blok in json.loads(pad.read_text(encoding="utf-8"))["data"]:
            for res in blok["results"]:
                yield blok, res


def main():
    prijs = []
    for blok, res in reeksen("*_prijs_dag_*.json"):
        for datum, waarde in res["data"]:
            if waarde is not None:
                prijs.append([blok["network_code"], datum[:10], round(waarde, 2)])
    schrijf("t120_australia_price_daily.csv", ["Network", "Date", "Price AUD per MWh"], prijs)

    opw = []
    for blok, res in reeksen("*_opwekking_fueltech_dag_*.json"):
        ft = res["columns"]["fueltech"]
        if ft == "battery":  # netto van laden en ontladen; die staan er al los in
            continue
        for datum, waarde in res["data"]:
            if waarde is not None:
                opw.append([blok["network_code"], res["columns"]["region"], ft, groep(ft),
                            datum[:10], round(waarde, 1)])
    schrijf("t121_australia_generation_daily.csv",
            ["Network", "Region", "Fuel technology", "Fuel group", "Date", "Energy MWh"], opw)


if __name__ == "__main__":
    main()
