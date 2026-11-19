"""Engelse versies van de Tableau-tabellen, voor de Engelse dashboards.

Schrijft tableau/data_en/<zelfde naam>.csv met dezelfde KOLOMNAMEN (zodat Tableau "Replace Data Source" automatisch
koppelt) maar Engelse WAARDEN. De veldnamen zelf vertaal je in Tableau één keer per dashboard met de lijst in
tableau/veldnamen_en.csv (Rename; Tableau zet de nieuwe naam overal in assen en tooltips).
Teksten die niet in het woordenboek staan, komen in resultaten/vertaal_en_ontbrekend.txt; de test faalt dan.
Gebruik:  PYTHONPATH=src python3 -m eti.vertaal_en
"""
import re
from pathlib import Path
import pandas as pd

BRON, UIT = Path("tableau/data"), Path("tableau/data_en")
TABELLEN = ["t1_zonejaar", "t2_land_maand", "t3_batterij", "t3b_batterij_leesbaar", "t4_schokjaar", "t4b_schokjaar_top",
            "t5_bronnen", "t6_kern_gebied_jaar", "t7_kern_land", "t8_kern_markt", "t9_signalering_zones", "t10_dekking_nl",
            "t11_ervaringscurve", "t12_portefeuille", "t15_controles", "t16_risico", "t42_gebeurtenissen",
            "t43_kannibalisatie", "t44_kern_zon", "t45_leercurve", "t46_portefeuille_uitleg", "t47_kpi_nl",
            "t48_capture_rangorde", "t49_segmenten", "t50_kpi_dashboards"]
NIET = {"Zone", "Landcode", "ISO3", "Maand", "Datum", "Kleur", "Controle", "Pijl", "Groeiperiode"}
NIET_PER_TABEL = {"t7_kern_land": {"Land", "Continent"}, "t44_kern_zon": {"Land", "Continent"}}  # al Engels (Ember)
HOUDEN = {"VOORTGANG.md", "unittest", "Energy-Charts", "Power BI / Fabric (DAX)", "Python (eti.signalering_europa)",
          "SQLite (Python)", "Sandbox", "Tableau Public, dashboard 1", "congestie_pc6 (codes 0-3)", "tests/",
          "IEA Cost of Capital Observatory", "SQL Server 2022 (T-SQL)", "BASE / Ember", "IAEA", "congress.gov",
          "reports/analyse/08_vervolg_18nov.md; log_tsql.txt", "resultaten/benchmark_sql.md", "sql/05_reconciliatie.sql; t5"}

LAND = {"Oostenrijk": "Austria", "Belgie": "Belgium", "Bulgarije": "Bulgaria", "Zwitserland": "Switzerland",
        "Tsjechie": "Czechia", "Duitsland": "Germany", "Denemarken": "Denmark", "Estland": "Estonia", "Spanje": "Spain",
        "Finland": "Finland", "Frankrijk": "France", "Griekenland": "Greece", "Kroatie": "Croatia", "Hongarije": "Hungary",
        "Italie": "Italy", "Litouwen": "Lithuania", "Letland": "Latvia", "Nederland": "Netherlands", "Noorwegen": "Norway",
        "Polen": "Poland", "Portugal": "Portugal", "Roemenie": "Romania", "Servie": "Serbia", "Zweden": "Sweden",
        "Slovenie": "Slovenia", "Slowakije": "Slovakia", "Oekraine": "Ukraine", "Azie": "Asia", "China": "China",
        "EU": "EU", "Europa": "Europe", "India": "India", "Japan": "Japan", "Noord-Amerika": "North America",
        "Verenigd Koninkrijk": "United Kingdom", "Verenigde Staten": "United States", "Wereld": "World",
        "Zuid-Korea": "South Korea", "VS": "US"}
DEEL = {"West": "West", "Oost": "East", "Midden-Noord": "Centre-North", "Noord": "North", "Sicilie": "Sicily",
        "Zuid": "South", "Oslo": "Oslo", "Midden": "Central", "Noord-Midden": "North-Central"}

W = {
    # categorieen
    "Noordwest-Europa": "North-West Europe", "Midden- en Zuidoost-Europa": "Central & South-East Europe",
    "Baltische staten": "Baltic states", "Iberie": "Iberia", "Scandinavie": "Scandinavia",
    "Vlakke prijzen": "Flat prices", "Zon houdt waarde": "Solar holds value", "Batterijmarkt": "Battery market",
    "Middenveld": "Middle ground", "Zonverzadigd": "Solar-saturated", "stevig": "robust", "grensgeval": "borderline",
    "Kosten niet gedekt": "Costs not covered", "Gedekt": "Covered", "Krap": "Tight",
    "Hond": "Dog", "Melkkoe": "Cash cow", "Vraagteken": "Question mark", "Ster": "Star",
    "Gas": "Gas", "Zon": "Solar", "Wind": "Wind", "Niet verklaard": "Unexplained", "Fossiel": "Fossil",
    "Kernenergie": "Nuclear", "Water, bio en overig": "Hydro, bio and other", "Regio": "Region", "Land": "Country",
    "Rest van de wereld": "Rest of the world", "Stabiel": "Stable", "Uitbouw": "Expanding", "Afbouw": "Declining",
    "Herstart": "Restarting", "Gestopt": "Phased out", "Geen gegevens 2025": "No 2025 data",
    "Gewoon": "Normal", "Let op": "Watch", "Schok": "Shock", "haalbaar": "feasible", "niet haalbaar": "not feasible",
    "overig": "other", "Bodem 5": "Bottom 5", "Top 5": "Top 5", "goed": "good", "slecht": "bad", "neutraal": "neutral",
    "ja": "yes", "nee": "no", "kern": "nuclear", "markt": "market", "geopolitiek": "geopolitics", "beleid": "policy",
    "alle": "all", "alle landen": "all countries", "zonder dekkingsgaten": "without coverage gaps",
    "alle jaren": "all years", "zonder 2021-22 (crisis)": "excl. 2021-22 (crisis)",
    "zonder 2023-24 (overcapaciteit)": "excl. 2023-24 (overcapacity)", "zonder 2021-24": "excl. 2021-24",
    "onder EU-mediaan": "below EU median", "boven EU-mediaan": "above EU median", "op EU-mediaan": "at EU median",
    "EUR/MW per jaar": "EUR/MW per year", "fractie": "ratio", "uren": "hours",
    "Batterij-omzet": "Battery revenue", "Capture rate zon": "Solar capture rate", "Gemiddelde prijs": "Average price",
    "Negatieve uren": "Negative hours", "Dagspreiding": "Daily spread", "hoger is beter voor batterijen":
    "higher is better for batteries", "hoger is beter voor zon": "higher is better for solar", "context": "context",
    "hoger: slechter voor zon, beter voor batterijen": "higher: worse for solar, better for batteries",
    "geen wissel": "no change", "nieuw in 2025 (in 2022 te weinig gegevens)": "new in 2025 (too little data in 2022)",
    # batterij
    "dagmarkt, geen netkosten, 1 cyclus per dag": "day-ahead, no grid charges, 1 cycle per day",
    "dagmarkt, tijdsafhankelijk transportrecht, 1 cyclus per dag": "day-ahead, time-dependent grid contract, 1 cycle per day",
    "dagmarkt, geen netkosten, 1,5 cyclus per dag": "day-ahead, no grid charges, 1.5 cycles per day",
    "dagmarkt, tijdsafhankelijk transportrecht, 1,5 cyclus per dag": "day-ahead, time-dependent grid contract, 1.5 cycles per day",
    "dagmarkt, geen netkosten, 2 cyclus per dag": "day-ahead, no grid charges, 2 cycles per day",
    "dagmarkt, tijdsafhankelijk transportrecht, 2 cyclus per dag": "day-ahead, time-dependent grid contract, 2 cycles per day",
    "stapeling, vast transportrecht": "stacking, firm grid contract",
    "stapeling, tijdsafhankelijk transportrecht": "stacking, time-dependent grid contract",
    "stapeling zonder capaciteitsvergoedingen, tijdsafhankelijk": "stacking without capacity payments, time-dependent",
    "Alleen dagmarkt, geen netkosten, 1 cyclus": "Day-ahead only, no grid charges, 1 cycle",
    "Alleen dagmarkt, met netkosten, 1 cyclus": "Day-ahead only, with grid charges, 1 cycle",
    "Alleen dagmarkt, geen netkosten, 1,5 cyclus": "Day-ahead only, no grid charges, 1.5 cycles",
    "Alleen dagmarkt, met netkosten, 1,5 cyclus": "Day-ahead only, with grid charges, 1.5 cycles",
    "Alleen dagmarkt, geen netkosten, 2 cycli": "Day-ahead only, no grid charges, 2 cycles",
    "Alleen dagmarkt, met netkosten, 2 cycli": "Day-ahead only, with grid charges, 2 cycles",
    "Dagmarkt + reservemarkten, vast netcontract": "Day-ahead + reserve markets, firm grid contract",
    "Dagmarkt + reservemarkten, flexibel netcontract": "Day-ahead + reserve markets, flexible grid contract",
    "Dagmarkt + reservemarkten zonder capaciteitsvergoeding": "Day-ahead + reserve markets, no capacity payment",
    "Noorwegen: 'niet verklaard' is vooral de lage waterstand": "Norway: 'unexplained' is mostly low reservoir levels",
    # gebeurtenissen
    "Kernramp Fukushima": "Fukushima nuclear disaster", "Gasprijzen beginnen sterk te stijgen": "Gas prices start to surge",
    "Russische invasie van Oekraine": "Russian invasion of Ukraine",
    "Piek gas- en stroomprijzen (augustus 2022)": "Peak gas and power prices (August 2022)",
    "Inflation Reduction Act getekend": "Inflation Reduction Act signed",
    "Laatste drie Duitse kerncentrales dicht": "Last three German nuclear plants close",
    "One Big Beautiful Bill Act getekend (afbouw belastingkredieten zon en wind)":
        "One Big Beautiful Bill Act signed (phase-out of solar and wind tax credits)",
    "Notitie reikwijdte en detailniveau nieuwbouw kerncentrales vastgesteld":
        "Scope decision for new Dutch nuclear plants adopted",
    "Einde salderingsregeling": "End of Dutch net metering", "algemeen": "general",
    "TTF-reeks in t2 / fact_gasprijs_maand": "TTF series in t2 / fact_gasprijs_maand",
    "t2: hoogste maandprijs": "t2: highest monthly price", "RVO, vaststellingsbesluit 26-01-2026": "RVO, decision 26-01-2026",
    "Wet herziening salderingsregeling": "Net Metering Revision Act",
    # controles
    "Berekening": "Calculation", "Bronnen": "Sources", "Code": "Code", "Gegevenskwaliteit": "Data quality",
    "Rapportage": "Reporting", "Aannames": "Assumptions", "Geslaagd": "Passed", "Open": "Open",
    "Afwijking verklaard": "Deviation explained", "Geslaagd met beperking": "Passed with limitation",
    "Afwijking open": "Deviation open", "Afwijking": "Deviation",
    "Zelfde uitkomst in twee SQL-dialecten": "Same result in two SQL dialects",
    "Signaleringsmaten gelijk aan de verwachting": "Signal measures match the expected values",
    "Tableau rekent hetzelfde als DAX en Python": "Tableau calculates the same as DAX and Python",
    "Power BI rekent hetzelfde": "Power BI calculates the same",
    "Zonaandeel in twee bronnen sluit aan": "Solar share agrees across two sources",
    "Correctiefactor werkt buiten de steekproef": "Correction factor works out of sample",
    "Testsuite slaagt": "Test suite passes", "Prestaties reproduceerbaar op een tweede machine": "Performance reproducible on a second machine",
    "Volledigheid kerncijfers per land": "Completeness of nuclear figures per country",
    "Teken en dekking grensstromen": "Sign and coverage of cross-border flows",
    "Twee bronnen voor de Chinese bouwgolf": "Two sources for the Chinese build wave",
    "Gepubliceerde cijfers gelijk aan de bron": "Published figures match the source",
    "Zonnestroom NL in twee bronnen": "Dutch solar generation in two sources",
    "Zonvermogen VS in twee bronnen": "US solar capacity in two sources",
    "Betekenis statuscodes netcongestie": "Meaning of grid congestion status codes",
    "Voorlopige cijfers zichtbaar": "Provisional figures visible",
    "WACC per regio tegen een externe bron": "WACC per region against an external source",
    "Marginale emissiefactor tegen een externe bron": "Marginal emission factor against an external source",
    "Tableau (werkblad Signalering)": "Tableau (Signals worksheet)", "Correctie geschat op 2019-2022": "Correction estimated on 2019-2022",
    "Ember capaciteit (mei 2025: 110,9 GW)": "Ember capacity (May 2025: 110.9 GW)", "CBS-tabellen t37-t39": "CBS tables t37-t39",
    "eigen WACC (t27)": "own WACC (t27)", "0,40 t/MWh (t13)": "0.40 t/MWh (t13)",
    "powerbi/maten_verwacht.csv (DAX-ontwerp)": "powerbi/maten_verwacht.csv (DAX design)",
    "verwachte uitkomsten": "expected results", "iMac (SQLite en Docker SQL Server)": "iMac (SQLite and Docker SQL Server)",
    "verwacht: alle landen met kern": "expected: all countries with nuclear", "ENTSO-E/Ember jaarcijfers": "ENTSO-E/Ember annual data",
    "NEA via OPIS (mei 2025: 92,9 GW)": "NEA via OPIS (May 2025: 92.9 GW)", "Ember jaarcijfers": "Ember annual data",
    "Ember maandcapaciteit": "Ember monthly capacity", "legenda capaciteitskaart Netbeheer Nederland": "legend of the Netbeheer Nederland capacity map",
    "CBS-markering **": "CBS marker **", "RVO-emissiefactor, CBS": "RVO emission factor, CBS",
    "berekend bij deze run": "calculated in this run", "bouwgids stap 10": "build guide step 10", "sessie 18-11": "session 18-11",
    "stappen 00-05 gelijk in aantallen en waarden": "steps 00-05 equal in counts and values",
    "nog uit te voeren met eti.powerbi_toets vergelijk": "still to run with eti.powerbi_toets vergelijk",
    "wacht op Fabric-toegang": "waiting for Fabric access",
    "82 sluiten aan, 34 dekkingsgaten, 66 wijken af; het verschil verdwijnt zonder dekkingsgaten":
        "82 agree, 34 coverage gaps, 66 differ; the difference disappears without coverage gaps",
    "patroon gelijk; SQL Server-plan draaide de tweede keer serieel": "same pattern; SQL Server plan ran serially the second time",
    "Oekraine zonder 2025-cijfer; vermogen Belgie geeft benutting boven 100% (leeg gelaten)":
        "Ukraine has no 2025 figure; Belgium's capacity gives utilisation above 100% (left blank)",
    "nog niet gecontroleerd; daarom niet gepubliceerd": "not yet checked; therefore not published",
    "zelfde patroon, ander niveau; bron in subtitel vermelden": "same pattern, different level; name the source in the subtitle",
    "visueel gecontroleerd op 18-11 (kaart 2025: 0,50-0,89; referentielijn 280)": "visually checked on 18-11 (map 2025: 0.50-0.89; reference line 280)",
    "aanname RAGKind-volgorde; nog een postcode op de kaart opzoeken": "assumed RAGKind order; still to check one postcode on the map",
    "vlag Voorlopig aanwezig en 2025 overal gemarkeerd": "Provisional flag present and 2025 marked everywhere",
    # risico's
    "Gemiddelde of marginale emissiefactor": "Average or marginal emission factor",
    "Segmentgrenzen zijn een keuze; 16-23 zones per jaar zijn grensgeval": "Segment thresholds are a choice; 16-23 zones a year are borderline",
    "Capture rate Nederland: park (0,62) of dak (0,52)": "Dutch capture rate: utility-scale (0.62) or rooftop (0.52)",
    "aFRR-capaciteitsprijs: twee ijkpunten (2022, 2026)": "aFRR capacity price: two data points (2022, 2026)",
    "LCOE alleen voor vijf regio's": "LCOE for five regions only", "WACC voor Afrika onzeker": "WACC for Africa uncertain",
    "Statuscodes netcongestie verkeerd gelezen": "Grid congestion status codes misread",
    "AC en DC door elkaar (EIA tegenover Ember/CBS)": "AC and DC mixed up (EIA versus Ember/CBS)",
    "Vermeden CO2 (CBS) gelezen als emissiereductie": "Avoided CO2 (CBS) read as an emission reduction",
    "Ember herziet cijfers achteraf": "Ember revises figures afterwards",
    "Paneelprijs is een exportwaarde, geen fabrieksprijs": "Panel price is an export value, not a factory price",
    "Grensstromen: teken en dekking niet gecontroleerd": "Cross-border flows: sign and coverage not checked",
    "Zonnestroom NL: CBS en Ember verschillen ~10%": "Dutch solar: CBS and Ember differ by ~10%",
    "2026 is een onvolledig jaar (tot 15 november)": "2026 is an incomplete year (to 15 November)",
    "Laadprofiel elektrische auto's is een aanname": "EV charging profile is an assumption",
    "beide varianten tonen": "show both variants", "gevoeligheid tonen (+-20%)": "show sensitivity (+-20%)",
    "beide tonen; keuze per vraag": "show both; choose per question", "tijdreeks ophalen": "fetch a time series",
    "noord/zuid-aanname in subtitel; bandbreedte": "north/south assumption in subtitle; range",
    "als band tonen": "show as a range", "een postcode op de kaart controleren (C15)": "check one postcode on the map (C15)",
    "eenheid in elke as en tooltip": "unit on every axis and tooltip",
    "apart tonen, niet verrekenen (GHG Protocol)": "show separately, do not net off (GHG Protocol)",
    "downloaddatum vastleggen": "record the download date", "leersnelheid met interval tonen": "show learning rate with interval",
    "eerst controleren (C10)": "check first (C10)", "bron per grafiek vermelden (C13)": "name the source per chart (C13)",
    "in elke titel vermelden": "state in every title", "als scenario markeren": "mark as a scenario",
    # KPI's
    "Maanden kosten gedekt": "Months costs covered", "Capture rate zon NL": "Dutch solar capture rate",
    "Gemiddelde prijs NL": "Dutch average price", "Prijssignaal laatste maand": "Price signal, latest month",
    "Wereld: kern tegen zon": "World: nuclear vs solar", "Europa: kern tegen zon": "Europe: nuclear vs solar",
    "Marktwaarde kern tegen zon": "Market value: nuclear vs solar", "Landen uitbouw tegen afbouw": "Countries expanding vs declining",
    "Leersnelheid": "Learning rate", "Paneelprijs": "Panel price", "Sterren 2025": "Stars 2025",
    "Controles geslaagd": "Controls passed", "Nog open": "Still open", "Opnieuw berekend bij elke run": "Recalculated every run",
    "Grootste risico": "Largest risk", "Ember, 2025": "Ember, 2025", "1,00 = gemiddeld uur": "1.00 = average hour",
    "regel: >=10% en 2 TWh": "rule: >=10% and 2 TWh", "literatuur ca. 20-25%": "literature approx. 20-25%",
    "exportwaarde China": "China export value", "groei > 30%/jaar": "growth > 30%/year",
    "verzadiging, netcongestie": "saturation, grid congestion", "doel: alle 18": "target: all 18",
    "doel: 0 voor publicatie": "target: 0 before publication", "rest: handmatig vastgelegd": "rest: recorded manually",
    "kans x impact, max 9": "likelihood x impact, max 9", "capture rate 2025": "capture rate 2025",
}

REGELS = [  # (patroon, vervanging) voor teksten met getallen
    (r"^(\d+) van (\d+)$", r"\1 of \2"),
    (r"^(\d{4}): (\d+) van (\d+)$", r"\1: \2 of \3"),
    (r"^(\d{2}-\d{2}): (\d+) van (\d+)$", r"\1: \2 of \3"),
    (r"^(\d+) van (\d+) zones Schok$", r"\1 of \2 zones in Shock"),
    (r"^Schok \(z = (.+)\)$", r"Shock (z = \1)"), (r"^Let op \(z = (.+)\)$", r"Watch (z = \1)"),
    (r"^Gewoon \(z = (.+)\)$", r"Normal (z = \1)"),
    (r"^maand (\d{4}-\d{2})$", r"month \1"), (r"^EU-mediaan (.+)$", r"EU median \1"),
    (r"^(.+) tegen (.+)$", r"\1 vs \2"),
    (r"^(\d{4}) (zon|kern): (.+)$", lambda m: f"{m[1]} {'solar' if m[2] == 'zon' else 'nuclear'}: {m[3]}"),
    (r"^(\d+) uitbouw, (\d+) afbouw of gestopt$", r"\1 expanding, \2 declining or phased out"),
    (r"^(\d+) herstart, (\d+) stabiel$", r"\1 restarting, \2 stable"),
    (r"^(\d+)% per verdubbeling$", r"\1% per doubling"),
    (r"^2022: (Ster|Hond|Melkkoe|Vraagteken)$", lambda m: f"2022: {W[m[1]]}"),
    (r"^score (\d+): (.+)$", lambda m: f"score {m[1]}: {W.get(m[2], m[2])}"),
    (r"^LCOE (\d{4}) \((\d+),(\d+)\)$", r"LCOE \1 (\2.\3)"),
    (r"^LCOE (\d{4}): (\d+),(\d+) EUR/MWh$", r"LCOE \1: \2.\3 EUR/MWh"),
    (r"^mediane fout (.+) -> (.+) na correctie, (.+) van (\d+) land-jaren beter$",
     r"median error \1 -> \2 after correction, \3 of \4 country-years better"),
    (r"^(\d+) tests, (\d+) overgeslagen$", r"\1 tests, \2 skipped"),
    (r"^(\d+) van (\d+) waarden gelijk$", r"\1 of \2 values equal"),
    (r"^zonnestroom (\d{4}): CBS (.+) TWh \(voorlopig\), Ember (.+) TWh, verschil (.+); vermogen sluit wel aan \((\d+),(\d) GW\)$",
     r"solar generation \1: CBS \2 TWh (provisional), Ember \3 TWh, difference \4; capacity does agree (\5.\6 GW)"),
    (r"^zon VS (.+): EIA-860M (\d+) GW \(AC, installaties vanaf 1 MW\), Ember (\d+) GW \(DC, inclusief kleinschalig\); verhouding (.+)$",
     r"US solar \1: EIA-860M \2 GW (AC, plants from 1 MW), Ember \3 GW (DC, including small-scale); ratio \4"),
    (r"^eigen WACC hoger dan IEA 2021 behalve China; LCOE met IEA-WACC (.+) EUR/MWh; 2021 was een lagerentejaar$",
     lambda m: "own WACC above IEA 2021 except China; LCOE at IEA WACC " +
     m[1].replace("Nederland", "Netherlands").replace("Europa", "Europe").replace("VS", "US") + " EUR/MWh; 2021 was a low-rate year"),
    (r"^0,40 ligt in de band (.+)-(.+) \(RVO 56,2 kg/GJ bij 50-58% rendement; CBS 0,455\)$",
     r"0.40 lies within the band \1-\2 (RVO 56.2 kg/GJ at 50-58% efficiency; CBS 0.455)"),
    (r"^groei (.+) -> (.+) per jaar \(drempel (erboven|eronder)\); capture rate (.+) -> ([0-9.]+)(.*)$", None),
]


def zonenaam(s):
    m = re.match(r"^(\w+) \((.+)\)$", s)
    if m and m[1] in LAND and m[2] in DEEL:
        return f"{LAND[m[1]]} ({DEEL[m[2]]})"
    return LAND.get(s)


def vertaal(s):
    if s in W:
        return W[s]
    if s in HOUDEN or re.fullmatch(r"(eti\.\w+|fact_\w+|powerbi/[\w./]+|t\d+)", s):
        return s
    z = zonenaam(s)
    if z:
        return z
    for pat, rep in REGELS:
        m = re.match(pat, s)
        if not m:
            continue
        if rep is None:  # kwadrantuitleg
            boven = "above" if m[3] == "erboven" else "below"
            rest = m[6]
            if rest:
                r2 = re.match(r"^; verzadiging, geen verval: zonvermogen groeide in (\d{4}) nog (.+)% \(CBS\) en (\d+)% van de postcodes heeft een afnametekort \(netcongestie\)$", rest)
                rest = (f"; saturation, not decline: solar capacity grew only {r2[2]}% in {r2[1]} (CBS) and {r2[3]}% of "
                        f"postcodes have an offtake shortage (grid congestion)") if r2 else None
                if rest is None:
                    return None
            return f"growth {m[1]} -> {m[2]} per year ({boven} threshold); capture rate {m[4]} -> {m[5]}{rest}"
        out = m.expand(rep) if isinstance(rep, str) else rep(m)
        if " vs " in out and pat.startswith("^(.+) tegen"):
            a, b = out.split(" vs ", 1)
            return f"{a} vs {b}"
        return out
    if re.fullmatch(r"[\w./ ,;:%()*+<>=-]*", s) and not re.search(r"[a-z]{4,}", s.lower().replace("ember", "").replace("tableau", "")):
        return s  # codes, getallen, landcodes
    return None


def main():
    UIT.mkdir(parents=True, exist_ok=True)
    ontbreekt = set()
    for t in TABELLEN:
        p = BRON / f"{t}.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p)
        for c in d.columns:
            if c in NIET or c in NIET_PER_TABEL.get(t, set()) or pd.api.types.is_numeric_dtype(d[c]) or d[c].isna().all():
                continue
            vals = {v: vertaal(v) for v in d[c].dropna().astype(str).unique()}
            ontbreekt |= {f"{t}.{c}: {v}" for v, e in vals.items() if e is None}
            d[c] = d[c].map(lambda v: v if pd.isna(v) else (vals.get(str(v)) or v))
        d.to_csv(UIT / f"{t}.csv", index=False, float_format="%.6g")
    Path("resultaten").mkdir(exist_ok=True)
    Path("resultaten/vertaal_en_ontbrekend.txt").write_text("\n".join(sorted(ontbreekt)) + "\n")
    print(f"{len(TABELLEN)} tabellen naar {UIT}; ontbrekend in woordenboek: {len(ontbreekt)}")
    for x in sorted(ontbreekt)[:40]:
        print("  ", x)
    return ontbreekt


VELD = {
    "Jaar": "Year", "Scenario": "Scenario", "Status zon": "Solar status", "Maanden": "Months", "Prijs USD per W": "Price USD per W",
    "Cumulatief GW": "Cumulative GW", "Volledig jaar": "Full year", "Landcode": "Country code", "Land": "Country",
    "Regio": "Region", "Batterij-omzet per MW": "Battery revenue per MW", "Capture rate zon": "Solar capture rate",
    "Batterij-omzet tegen mediaan": "Battery revenue vs median", "Groei zonvermogen per jaar": "Solar capacity growth per year",
    "Zonvermogen GW": "Solar capacity GW", "Kwadrant": "Quadrant", "Moment": "Snapshot", "Groeiperiode": "Growth period",
    "Groeidrempel": "Growth threshold", "Controle": "Control", "Domein": "Domain", "Doel": "Objective", "Kant A": "Side A",
    "Kant B": "Side B", "Uitkomst": "Result", "Status": "Status", "Bron": "Source", "Opnieuw berekend": "Recalculated",
    "Risico": "Risk", "Kans": "Likelihood", "Impact": "Impact", "Maatregel": "Mitigation", "Dashboards": "Dashboards",
    "Score": "Score", "Zone": "Zone", "Zonenaam": "Zone name", "Heel jaar": "Full year", "Gemiddelde prijs": "Average price",
    "Negatieve uren": "Negative hours", "Dagspreiding": "Daily spread", "Segment": "Segment",
    "Segment stabiel (aandeel)": "Segment stability (share)", "Segment zekerheid": "Segment certainty",
    "Maandnummer": "Month number", "Capture rate wind": "Wind capture rate", "Maand": "Month", "Cycli per dag": "Cycles per day",
    "Levensduur (jaar)": "Lifetime (years)", "Omzet per MW": "Revenue per MW", "Doelrendement": "Target return",
    "Hoogste bouwkosten per kWh": "Highest capex per kWh", "Bouwkosten nu per kWh": "Capex today per kWh",
    "Scenario leesbaar": "Scenario (plain)", "Haalbaar": "Feasible", "Volgorde": "Order", "Datum": "Date", "Gebied": "Area",
    "Gebeurtenis": "Event", "Soort": "Type", "Na te slaan bij": "Reference", "Zonaandeel %": "Solar share %", "Lijn": "Fit",
    "Helling (per procentpunt)": "Slope (per percentage point)", "ISO3": "ISO3", "Continent": "Continent",
    "Kern TWh 2025": "Nuclear TWh 2025", "Zon TWh 2025": "Solar TWh 2025", "Kernvermogen GW 2025": "Nuclear capacity GW 2025",
    "Zonvermogen GW 2025": "Solar capacity GW 2025", "Benutting kern 2025": "Nuclear capacity factor 2025",
    "Benutting zon 2025": "Solar capacity factor 2025", "GW zon voor kern-TWh": "Solar GW for nuclear TWh",
    "Verhouding GW zon / GW kern": "Ratio solar GW / nuclear GW", "Koers kern": "Nuclear trajectory", "Variant": "Variant",
    "n": "n", "Leersnelheid": "Learning rate", "Interval laag": "Interval low", "Interval hoog": "Interval high", "R2": "R2",
    "Capture rate zon 2022": "Solar capture rate 2022", "Capture rate zon 2025": "Solar capture rate 2025",
    "Groei zonvermogen per jaar 2022": "Solar capacity growth per year 2022",
    "Groei zonvermogen per jaar 2025": "Solar capacity growth per year 2025", "Kwadrant 2022": "Quadrant 2022",
    "Kwadrant 2025": "Quadrant 2025", "Verklaring": "Explanation", "KPI": "KPI", "Eenheid": "Unit", "Waarde NL": "Value NL",
    "Vorig jaar": "Previous year", "Verschil": "Change", "Verschil %": "Change %", "EU-mediaan": "EU median",
    "Positie": "Position", "Lezing": "Reading", "Pijl": "Arrow", "Rang": "Rank", "Groep": "Group", "Toon": "Show",
    "Kleur": "Colour", "Prijsstijging totaal": "Total price increase", "Oorzaak": "Driver", "Euro per MWh": "EUR per MWh",
    "Toelichting": "Note", "Dashboard": "Dashboard", "Waarde": "Value", "Tekst": "Text", "Vergelijking": "Comparison",
    "Referentie": "Reference", "Richting": "Direction", "Verschil (%)": "Difference (%)", "Soort gebied": "Area type",
    "Opwek TWh": "Generation TWh", "Aandeel %": "Share %", "Europa": "Europe", "EU": "EU", "Kern TWh 2010": "Nuclear TWh 2010",
    "Kern TWh 2015": "Nuclear TWh 2015", "Zon TWh 2015": "Solar TWh 2015", "Wind TWh 2015": "Wind TWh 2015",
    "Wind TWh 2025": "Wind TWh 2025", "Aandeel kern 2025 %": "Nuclear share 2025 %",
    "Aandeel zon en wind 2025 %": "Solar and wind share 2025 %", "Aandeel fossiel 2025 %": "Fossil share 2025 %",
    "CO2 gram per kWh 2025": "CO2 grams per kWh 2025", "Jaar zon voorbij kern": "Year solar overtook nuclear",
    "Kern verschil 2015-2025 TWh": "Nuclear change 2015-2025 TWh", "Zon en wind verschil 2015-2025 TWh":
    "Solar and wind change 2015-2025 TWh", "Kern verschil 2015-2025 %": "Nuclear change 2015-2025 %",
    "Aandeel kern in negatieve uren %": "Nuclear share in negative hours %", "Capture rate": "Capture rate",
    "Capture-prijs zon": "Solar capture price", "Prijs z-score": "Price z-score", "Prijs signaal": "Price signal",
}


def veldnamen():
    rij, ontbreekt = [], []
    for t in TABELLEN:
        p = BRON / f"{t}.csv"
        if not p.exists():
            continue
        for c in pd.read_csv(p, nrows=1).columns:
            if c in VELD:
                rij.append({"Tabel": t, "Veld": c, "English": VELD[c]})
            else:
                ontbreekt.append(f"{t}: {c}")
    pd.DataFrame(rij).to_csv("tableau/veldnamen_en.csv", index=False)
    return ontbreekt


if __name__ == "__main__":
    main()
    print("veldnamen zonder vertaling:", veldnamen())
