"""Wereldwijde investeringscontext per land: vier tabellen voor Tableau.

t108_country_risk        landenrisico en risicopremie (Damodaran, januari 2026)
t109_carbon_prices       CO2-prijs per instrument en jaar (Wereldbank, mei 2026)
t110_public_investment   publieke investeringen in hernieuwbaar per land,
                         technologie en jaar (IRENA, 2023 miljoen USD)
t111_country_macro       rente, bbp per hoofd, toegang tot stroom, inflatie,
                         bevolking (Wereldbank WDI)

De ruwe bestanden staan in data/raw/wereld (niet op GitHub).
Kolomnamen en waarden bevatten geen komma's, anders breekt de import in Tableau.
"""
import csv
import io
import os
import sys
import zipfile
from pathlib import Path

import openpyxl

ROOT = Path(os.environ.get("ETI_ROOT", Path(__file__).resolve().parents[2]))
RAW = Path(os.environ.get("ETI_RAW", ROOT / "data" / "raw" / "wereld"))
UIT = [Path(p) for p in os.environ.get(
    "ETI_UIT", f"{ROOT / 'tableau' / 'data'}{os.pathsep}{ROOT / 'tableau' / 'data_en'}"
).split(os.pathsep)]


def schoon(x):
    """Tekst zonder komma's en zonder dubbele spaties."""
    if x is None:
        return ""
    return " ".join(str(x).replace(",", "").replace("\xa0", " ").split())


def getal(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def schrijf(naam, kop, rijen):
    for map_ in UIT:
        map_.mkdir(parents=True, exist_ok=True)
        with open(map_ / naam, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(kop)
            w.writerows(rijen)
    print(f"{naam}: {len(rijen)} rijen")
    return rijen


def landenrisico():
    wb = openpyxl.load_workbook(RAW / "damodaran_ctryprem_2026.xlsx", read_only=True, data_only=True)
    rijen, begonnen = [], False
    for r in wb["ERPs by country"].iter_rows(values_only=True):
        if r[0] == "Country":
            begonnen = True
            continue
        if not begonnen or not r[0] or None in (getal(r[3]), getal(r[4]), getal(r[5])):
            continue
        rijen.append([
            schoon(r[0]), schoon(r[1]), schoon(r[2]),
            round(getal(r[3]) * 100, 2), round(getal(r[4]) * 100, 2), round(getal(r[5]) * 100, 2),
        ])
    return schrijf("t108_country_risk.csv",
                   ["Country", "Region", "Moodys rating", "Default spread pct",
                    "Equity risk premium pct", "Country risk premium pct"], rijen)


def co2_prijzen():
    wb = openpyxl.load_workbook(RAW / "worldbank_carbon_pricing_may2026.xlsx", read_only=True, data_only=True)
    info = {}
    kop = None
    for r in wb["Compliance_Gen Info"].iter_rows(values_only=True):
        if r[0] == "Unique ID":
            kop = list(r)
            continue
        if kop and r[0]:
            d = dict(zip(kop, r))
            info[r[0]] = (schoon(d.get("Status")), schoon(d.get("Jurisdiction covered")))
    rijen, kop = [], None
    for r in wb["Compliance_Price"].iter_rows(values_only=True):
        if r[0] == "Unique ID":
            kop = list(r)
            continue
        if not kop or not r[0]:
            continue
        status, gebied = info.get(r[0], ("", ""))
        for k, v in zip(kop[6:], r[6:]):
            p = getal(v)
            if p is None or not str(k).isdigit():
                continue
            rijen.append([schoon(r[0]), schoon(r[1]), schoon(r[2]), gebied, schoon(r[3]),
                          schoon(r[4]), status, int(k), round(p, 2)])
    return schrijf("t109_carbon_prices.csv",
                   ["Instrument id", "Instrument", "Type", "Jurisdiction", "Region",
                    "Income group", "Status", "Year", "Price USD per tCO2e"], rijen)


# De export van IRENA verliest letters met accenten; hier staan de juiste namen.
NAAM = {
    "T\ufffdrkiye": "Turkiye",
    "C\ufffdte d'Ivoire": "Cote d'Ivoire",
    "R\ufffdunion": "Reunion",
}
FOSSIEL = {"Other fossil fuels", "Nuclear energy", "Natural gas", "Oil", "Coal", "Non-renewable waste"}


def publieke_investeringen():
    rijen = []
    with open(RAW / "irena_public_investments_2026H2.csv", encoding="utf-8-sig", newline="") as f:
        lezer = csv.reader(f)
        next(lezer)
        for land, tech, jaar, v in lezer:
            p = getal(v)
            if p is None:
                continue
            land = NAAM.get(land, land)
            if "\ufffd" in land:
                raise ValueError(f"landnaam met kapot teken: {land!r}")
            groep = "Non-renewable" if tech in FOSSIEL else "Renewable"
            rijen.append([schoon(land), schoon(tech), groep, int(jaar), round(p, 2)])
    return schrijf("t110_public_investment.csv",
                   ["Country", "Technology", "Group", "Year", "Public investment USD million 2023"], rijen)


WDI = {
    "FR.INR.LEND": "Lending interest rate pct",
    "NY.GDP.PCAP.CD": "GDP per capita USD",
    "EG.ELC.ACCS.ZS": "Access to electricity pct",
    "FP.CPI.TOTL.ZG": "Inflation pct",
    "SP.POP.TOTL": "Population",
}


def macro():
    z = zipfile.ZipFile(RAW / "worldbank_wdi_5_indicatoren.zip")
    data = [n for n in z.namelist() if n.startswith("API")][0]
    meta = [n for n in z.namelist() if n.startswith("Metadata_Country")][0]
    regio = {}
    for d in csv.DictReader(io.StringIO(z.read(meta).decode("utf-8-sig"))):
        if d.get("Region"):  # aggregaten hebben geen regio
            regio[d["Country Code"]] = (schoon(d["Region"]), schoon(d["IncomeGroup"]))
    tekst = z.read(data).decode("utf-8-sig").splitlines()[4:]
    lezer = csv.reader(tekst)
    kop = next(lezer)
    jaren = [k for k in kop if k.isdigit()]
    cel = {}
    for r in lezer:
        if len(r) < 5 or r[1] not in regio or r[3] not in WDI:
            continue
        for j in jaren:
            v = getal(r[kop.index(j)])
            if v is not None:
                cel.setdefault((r[1], schoon(r[0]), int(j)), {})[r[3]] = v
    rijen = []
    for (code, land, jaar), d in sorted(cel.items()):
        rijen.append([code, land, *regio[code], jaar] +
                     [round(d[c], 2) if c in d else "" for c in WDI])
    return schrijf("t111_country_macro.csv",
                   ["Country code", "Country", "Region", "Income group", "Year"] + list(WDI.values()), rijen)


def main():
    landenrisico()
    co2_prijzen()
    publieke_investeringen()
    macro()


if __name__ == "__main__":
    sys.exit(main())
