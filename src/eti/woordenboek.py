"""Datawoordenboek: beschrijft elke kolom van elke tabel in powerbi/data, als Markdown en als JSON-schema.

De cijfers (type, bereik, lege waarden, voorbeelden) komen uit het profiel van eti.da; de betekenis (beschrijving,
eenheid, regels, verwante kolommen, bekende problemen) staat hieronder in KOLOMMEN en TABELLEN. Een kolom zonder
beschrijving krijgt de aantekening 'nog te beschrijven', zodat zichtbaar is wat ontbreekt.
`valideer()` toetst een tabel tegen het schema; eti.kwaliteit gebruikt dat voor de dagelijkse controle.

Gebruik:  PYTHONPATH=src python3 -m eti.woordenboek        (eerst eti.da draaien)
Uitvoer:  reports/analyse/datawoordenboek.md en reports/analyse/datawoordenboek.schema.json
"""
import json
import os
import sys

import pandas as pd

DATA, UIT = "powerbi/data", "reports/analyse"

# tabel -> (wat een rij is, bron)
TABELLEN = {
    "fact_land_jaar": ("een biedzone in een jaar: prijs, marktwaarde van zon en wind, negatieve uren", "Energy-Charts (prijs, opwek), Open-Meteo (instraling), Ember (aandelen)"),
    "fact_land_maand": ("een biedzone in een maand", "Energy-Charts, Open-Meteo"),
    "fact_flex_land": ("een land in een jaar voor een batterij van 1, 2 of 4 uur", "eigen berekening op Energy-Charts-prijzen"),
    "fact_tech_land": ("een land in een jaar voor zon of wind: capture-prijs en rendement zonder contract", "eigen berekening"),
    "fact_nl_uur_alle_jaren": ("een uur in Nederland: dagmarktprijs en opwek per bron", "Energy-Charts (ENTSO-E)"),
    "fact_nl_jaar": ("een jaar in Nederland: kengetallen van het modelpark van 10 MW", "eigen model"),
    "fact_onbalans_nl": ("een kwartier in Nederland: onbalansprijzen", "ENTSO-E (document A85)"),
    "fact_onbalans_regel": ("een stuurregel voor de batterij in een jaar", "eigen simulatie (eti.onbalansregel)"),
    "fact_fcr_nl": ("een blok van vier uur: prijs van primaire reserve (FCR)", "ENTSO-E (document A84)"),
    "fact_afrr_energie_nl": ("een kwartier: prijs van geactiveerde regelenergie (aFRR), op en af", "ENTSO-E (document A84)"),
    "fact_balans_nl_jaar": ("een jaar: samenvatting van FCR en aFRR", "eigen berekening"),
    "fact_batterij_volledige_case": ("een variant van de batterijcase met netkosten", "eigen model, marktcijfers uit het memo"),
    "fact_batterij_irr": ("een jaar, strategie en investeringsbedrag: IRR van de batterij", "eigen model"),
    "fact_batterij_stapeling": ("een jaar en strategie: omzet van de batterij", "eigen model"),
    "fact_wereld_markten": ("een markt buiten de EU in een jaar", "EIA, gridstatus, CAISO, AEMO, JEPX, Elexon"),
    "fact_vs_halfjaar": ("Texas of Californie, 1 januari tot en met 24 juni van een jaar", "EIA, gridstatus, CAISO"),
    "fact_vs_opwek_jaar": ("Texas of Californie in een jaar per brandstof", "EIA (uurdata opwek per bron)"),
    "fact_kernenergie_land_jaar": ("een biedzone met kernenergie in een jaar", "Energy-Charts; eigen berekening (eti.kernenergie)"),
    "fact_kernenergie_verband": ("een rangcorrelatie tussen het kernaandeel en een marktmaat", "eigen berekening"),
    "fact_ruimtelijk_paneel": ("een regressie van de capture rate op eigen en buur-zonaandeel", "eigen berekening (eti.ruimtelijk)"),
    "fact_ntc": ("een grens tussen twee landen: handelscapaciteit", "ENTSO-E TYNDP"),
    "fact_regio_jaar": ("een studieregio in 2025, 2030 of 2050: kosten en impact per euro", "eigen model, aannames uit het memo"),
    "dim_regio": ("een studieregio: kapitaalkosten, vollasturen, investering", "aannames uit het memo, per regio nagezocht"),
    "dim_land": ("een land met indelingen", "Ember, eigen indeling"),
    "dim_markt": ("een markt met de studieregio waar ze bij hoort", "eigen indeling"),
    "fact_australie": ("een Australische deelstaat in een jaar", "AEMO via Open Electricity"),
    "fact_uk_prijs": ("een halfuur in Groot-Brittannie: marktprijs", "Elexon"),
    "fact_gas_henryhub": ("een dag: gasprijs Henry Hub", "EIA"),
    "fact_weer_uur": ("een uur op een meetpunt: instraling en weer", "Open-Meteo"),
    "fact_vs_dag": ("een dag in Texas of Californie: prijs, dagspreiding, batterijopbrengst, zon en wat de batterijvloot deed", "EIA, gridstatus, CAISO OASIS; eigen berekening"),
    "fact_gasprijs_maand": ("een maand: de Europese gasprijs in dollar per MMBtu en in euro per MWh", "IMF en Federal Reserve via FRED"),
    "fact_nl_zonprofiel_toets": ("een jaar: de Nederlandse zonreeks getoetst aan instraling en aan het jaartotaal van Ember", "Energy-Charts, Open-Meteo, Ember; eigen berekening"),
    "dim_datum": ("een dag: jaar, kwartaal, maand, week, weekdag en feestdag, als datumtabel voor Power BI", "eigen berekening"),
    "fact_onzekerheid_land": ("een land in een jaar: onzekerheidsband uit 10.000 trekkingen", "eigen berekening (bootstrap)"),
    "fact_studieregio_jaar": ("een studieregio in een jaar: opwek, aandelen en uitstoot", "Ember"),
}
VOORVOEGSEL = {"fact_ember_": "Ember (CC BY 4.0)", "fact_owid_": "Our World in Data", "fact_worldbank": "Wereldbank", "fact_stromen_": "ENTSO-E, Energy-Charts",
               "fact_land_profiel_": "Energy-Charts", "fact_prijsmodel": "eigen model", "fact_": "eigen berekening"}

# kolom -> beschrijving, eenheid, regels, verwant, alias; een sleutel (tabel, kolom) gaat voor
KOLOMMEN = {
    "jaar": ("Kalenderjaar. 2026 is onvolledig (tot 15 november).", "jaar", "geheel getal; filter 2026 uit vergelijkingen tussen jaren", "uren", ""),
    "maand": ("Kalendermaand, 1 tot 12 (UTC).", "maand", "1 tot 12", "jaar", ""),
    "uur": ("Uur van de dag in UTC, 0 tot 23.", "uur", "0 tot 23; lokale tijd is UTC+1 of +2", "timestamp_utc", ""),
    "uur_bron": ("Uur zoals de bron het telt, 1 tot 24 (het uur dat eindigt). De kolom uur is hieruit afgeleid: uur = uur_bron - 1.", "uur", "1 tot 24", "bronbestand", ""),
    "timestamp_utc": ("Begin van het uur of kwartier, in UTC.", "tijdstip", "uniek per tabel; geen zomertijd", "jaar, maand, uur", "tijdstip"),
    "land": ("Naam van het land of de biedzone in het Nederlands.", "", "sleutel samen met jaar", "biedzone, iso3", "markt"),
    "biedzone": ("Code van de biedzone (NL, DE-LU, IT-North, NO1).", "", "37 zones", "land", "zone, bidding zone"),
    "iso3": ("Landcode volgens ISO 3166 (drie letters).", "", "koppelt aan Ember", "land", "ISO 3 code"),
    "gem_prijs": ("Gemiddelde dagmarktprijs over alle uren van de periode.", "euro per MWh", "ongewogen over de uren", "mediaan_prijs, capture_zon", "basislastprijs, baseload"),
    "mediaan_prijs": ("Mediaan van de uurprijzen.", "euro per MWh", "", "gem_prijs", ""),
    "prijs_eur_mwh": ("Dagmarktprijs van het uur.", "euro per MWh", "tussen -500 en 5.000 (marktgrenzen)", "solar_mw", "day-ahead prijs"),
    "capture_zon": ("Capture rate van zon: de prijs die zon ontvangt (gewogen naar opwek) gedeeld door de gemiddelde prijs.", "verhouding", "tussen 0 en 2; boven 2 is een rekenfout", "capture_bron, gem_prijs", "marktwaardefactor, value factor"),
    "capture_wind": ("Capture rate van wind, zelfde definitie als voor zon.", "verhouding", "tussen 0 en 2", "aandeel_wind", ""),
    "capture_rate": ("Capture rate van de genoemde techniek of brandstof.", "verhouding", "tussen 0 en 2", "capture_price", ""),
    "capture_price": ("Prijs die de techniek gemiddeld ontvangt (gewogen naar opwek).", "euro per MWh", "capture_rate maal gem_prijs", "gem_prijs", "capture-prijs"),
    "capture_bron": ("Waar het opwekprofiel vandaan komt: gemeten opwek of een schatting uit instraling.", "", "instraling is een benadering; apart houden van gemeten zones", "capture_zon", ""),
    "negatieve_uren": ("Aantal uren met een dagmarktprijs onder nul.", "uren", "0 tot 8.784", "uren", ""),
    "uren_boven_200": ("Aantal uren met een prijs boven 200 euro per MWh.", "uren", "", "gem_prijs", ""),
    "dagspreiding": ("Gemiddeld verschil tussen de hoogste en laagste uurprijs van een dag.", "euro per MWh", "niet negatief", "omzet_realistisch_per_mw", "daily spread"),
    "uren": ("Aantal uren met een prijs in de periode.", "uren", "8.760 of 8.784 in een heel jaar", "jaar", ""),
    "aandeel_zon": ("Aandeel van zon in de opwek volgens ENTSO-E.", "fractie", "0 tot 1; onderschat zon achter de meter", "aandeel_zon_energycharts", ""),
    "aandeel_wind": ("Aandeel van wind in de opwek volgens ENTSO-E.", "fractie", "0 tot 1", "capture_wind", ""),
    "aandeel_zon_energycharts": ("Aandeel van zon in de opwek volgens Energy-Charts.", "fractie", "0 tot 1", "aandeel_zon", ""),
    "aandeel_wind_energycharts": ("Aandeel van wind in de opwek volgens Energy-Charts.", "fractie", "0 tot 1", "aandeel_wind", ""),
    "uren_opslag": ("Duur van de batterij: uren ontladen op vol vermogen.", "uur", "1, 2 of 4", "omzet_realistisch_per_mw", ""),
    "omzet_perfect_per_mw": ("Dagmarktomzet van de batterij met kennis vooraf van alle prijzen (bovengrens).", "euro per MW per jaar", "een cyclus per dag", "omzet_realistisch_per_mw", ""),
    "omzet_realistisch_per_mw": ("Dagmarktomzet van de batterij met een plan op de prijzen van gisteren.", "euro per MW per jaar", "verliesdagen overgeslagen; zonder netkosten en balancering", "voorspel_ratio, dagspreiding", "batterij_per_mw"),
    "voorspel_ratio": ("Realistische omzet gedeeld door de omzet met kennis vooraf.", "verhouding", "0 tot 1", "omzet_perfect_per_mw", ""),
    "irr_realistisch": ("IRR van de batterij bij de realistische dagmarktomzet.", "fractie per jaar", "leeg als de investering nooit terugkomt; leeg is dus slechter dan negatief", "omzet_realistisch_per_mw", ""),
    "irr": ("Intern rendement van het project.", "fractie per jaar", "leeg als de investering nooit terugkomt", "", "IRR"),
    "irr_merchant": ("IRR zonder contract, als de capture-prijs van dat jaar de hele levensduur zou gelden.", "fractie per jaar", "leeg als de investering nooit terugkomt", "capture_price", ""),
    "technologie": ("Techniek: zon of wind.", "", "", "capture_price", ""),
    "aandeel_productie_negatief": ("Deel van de opwek dat in uren met een negatieve prijs valt.", "fractie", "0 tot 1", "negatieve_uren", ""),
    "solar_mw": ("Gemeten zonopwek in het uur.", "MW", "alleen de vorm van het profiel gebruiken, niet het niveau", "prijs_eur_mwh", ""),
    "wind_mw": ("Gemeten windopwek in het uur (land en zee).", "MW", "", "", ""),
    "gas_mw": ("Opwek uit gas in het uur.", "MW", "", "coal_mw", ""),
    "coal_mw": ("Opwek uit kolen in het uur.", "MW", "", "gas_mw", ""),
    "nuclear_mw": ("Opwek uit kernenergie in het uur.", "MW", "", "", ""),
    "biomass_mw": ("Opwek uit biomassa in het uur.", "MW", "", "", ""),
    "waste_mw": ("Opwek uit afval in het uur.", "MW", "", "", ""),
    "other_renewable_mw": ("Overige hernieuwbare opwek.", "MW", "altijd nul: niet gebruiken", "", ""),
    "prijs_tekort_eur_mwh": ("Onbalansprijs bij een tekort: wat laden zonder inkoop kost.", "euro per MWh", "kan sterk negatief of zeer hoog zijn", "prijs_overschot_eur_mwh", ""),
    "prijs_overschot_eur_mwh": ("Onbalansprijs bij een overschot: wat ontladen zonder verkoop oplevert.", "euro per MWh", "", "prijs_tekort_eur_mwh", ""),
    "irr_zon": ("IRR van het zonnepark van 10 MW voor belasting, bij de marktwaarde van dat jaar.", "fractie per jaar", "", "capture_rate, lcoe", ""),
    "irr_zon_na_belasting": ("IRR van het zonnepark na vennootschapsbelasting.", "fractie per jaar", "", "irr_zon", ""),
    "lcoe": ("Kosten per MWh over de levensduur (levelized cost of energy).", "euro per MWh", "", "capture_price", ""),
    "lcoe_eur_mwh": ("Kosten per MWh over de levensduur in de regio en het jaar.", "euro per MWh", "aanname uit het eigen model", "wacc", "LCOE"),
    "batterij_omzet_perfect": ("Dagmarktomzet van de batterij van 10 MW met kennis vooraf.", "euro per jaar", "delen door 10 voor per MW", "batterij_omzet_realistisch", ""),
    "batterij_omzet_realistisch": ("Dagmarktomzet van de batterij van 10 MW met een plan op gisteren.", "euro per jaar", "delen door 10 voor per MW", "irr_batterij", ""),
    "irr_batterij": ("IRR van de batterij op dagmarkthandel.", "fractie per jaar", "leeg als de investering nooit terugkomt", "", ""),
    "co2_vermeden_uur": ("Vermeden CO2 van het zonnepark, berekend per uur met de opwekmix van dat uur.", "ton per jaar", "de voorkeursmethode", "co2_vermeden_jaargem", ""),
    "co2_vermeden_jaargem": ("Vermeden CO2 berekend met de gemiddelde netintensiteit van het jaar.", "ton per jaar", "overschat sinds 2023", "co2_vermeden_uur", ""),
    "markt": ("Naam van de markt buiten de EU (Texas, Californie, Japan, een Australische deelstaat).", "", "", "jaar", ""),
    "gem_prijs_eur": ("Gemiddelde groothandelsprijs, omgerekend naar euro.", "euro per MWh", "wisselkoers van het jaar", "", ""),
    "capture_zon_instraling": ("Capture rate van zon, geschat met een instralingsprofiel in plaats van gemeten opwek.", "verhouding", "benadering; niet mengen met gemeten zones", "capture_rate", ""),
    "batterij_2u_realistisch_eur_per_mw": ("Dagmarktomzet van een batterij van 2 uur, plan op gisteren, lokale dagen.", "euro per MW per jaar", "", "", ""),
    "brandstof": ("Opwekbron volgens EIA (SUN, WND, NUC, NG, BAT en andere).", "", "in Californie zit batterij in OTH", "twh", ""),
    "twh": ("Opwek in het jaar.", "TWh", "", "aandeel_opwek", ""),
    "aandeel_opwek": ("Aandeel van de brandstof in de totale opwek.", "fractie", "0 tot 1", "twh", ""),
    "aandeel_in_negatieve_uren": ("Deel van de opwek van deze bron dat in uren met een negatieve prijs valt.", "fractie", "0 tot 1", "negatieve_uren", ""),
    "hoogste_uur_mw": ("Hoogste opwek in een uur.", "MW", "", "", ""),
    "wacc": ("Gewogen kapitaalkosten.", "fractie per jaar", "0 tot 0,3", "lcoe_eur_mwh", "kapitaalkosten"),
    "vollasturen": ("Vollasturen van zon per jaar.", "uur per jaar", "", "capex_eur_kw", ""),
    "capex_eur_kw": ("Investering per kW vermogen.", "euro per kW", "", "", ""),
    "netintensiteit_g_kwh": ("CO2-intensiteit van het net.", "gram per kWh", "", "", ""),
    "t_co2_per_meur_jaar": ("Vermeden CO2 per miljoen euro investering per jaar.", "ton per miljoen euro per jaar", "", "", "impact per euro"),
    "regio": ("Studieregio (Nederland, Europa, VS, China, India).", "", "", "", ""),
    "kern_twh": ("Opwek uit kernenergie in het jaar.", "TWh", "", "aandeel_kern", ""),
    "aandeel_kern": ("Aandeel van kernenergie in de opwek.", "fractie", "0 tot 1", "", ""),
    "capture_kern": ("Capture rate van kernenergie.", "verhouding", "", "", ""),
    "prijs_eur_mw_uur": ("Prijs van FCR-vermogen per MW per uur, per blok van vier uur.", "euro per MW per uur", "", "", ""),
    "op_eur_mwh": ("Prijs van geactiveerde opregelenergie in het kwartier.", "euro per MWh", "leeg als niet geactiveerd", "af_eur_mwh", ""),
    "af_eur_mwh": ("Prijs van geactiveerde afregelenergie in het kwartier.", "euro per MWh", "leeg als niet geactiveerd", "op_eur_mwh", ""),
    "omzet_per_mw": ("Omzet per MW per jaar van de genoemde strategie.", "euro per MW per jaar", "", "", ""),
    "ntc_heen_mw": ("Handelscapaciteit van het eerste naar het tweede land.", "MW", "", "ntc_terug_mw", ""),
    "ntc_terug_mw": ("Handelscapaciteit in de andere richting.", "MW", "", "ntc_heen_mw", ""),
    "Area": ("Land of regio volgens Ember.", "", "", "ISO 3 code", ""),
    "ISO 3 code": ("Landcode volgens ISO 3166; leeg voor regio's.", "", "", "Area", "iso3"),
    "Year": ("Kalenderjaar.", "jaar", "", "", "jaar"),
    "Electricity source": ("Opwekbron of saldo (Solar, Wind, Gas, Demand, Net imports).", "", "", "", ""),
    "Generation (TWh)": ("Opwek in het jaar.", "TWh", "", "", ""),
    "Share of generation (%)": ("Aandeel in de totale opwek.", "procent", "0 tot 100", "", ""),
    "Capacity (GW)": ("Opgesteld vermogen.", "GW", "voor een deel van de landen en jaren leeg", "", ""),
    "Emissions (MtCO2e)": ("Uitstoot van de elektriciteitsopwek.", "megaton CO2-equivalent", "", "", ""),
    ("fact_nl_uur_alle_jaren", "solar_mw"): ("Gemeten zonopwek in het uur.", "MW", "alleen de vorm van het profiel gebruiken, niet het niveau", "prijs_eur_mwh", ""),
}
# bekende kwaliteitsproblemen per (tabel, kolom) of kolom
PROBLEMEN = {
    ("fact_nl_uur_alle_jaren", "solar_mw"): "Telt 1 tot 4% van de Nederlandse zonopwek, vooral grote parken (0,5 TWh tegen 28,5 TWh volgens Ember in 2025). De vorm volgt de instraling; de parken schakelen af bij negatieve prijzen, dus de capture rate is die van een park dat dat doet (fact_nl_zonprofiel_toets).",
    ("fact_nl_uur_alle_jaren", "other_renewable_mw"): "Altijd nul.",
    ("fact_nl_uur_alle_jaren", "wind_mw"): "Telt op tot 22,7 TWh in 2025; Ember geeft 33,7 TWh.",
    ("fact_land_jaar", "capture_zon"): "SE3 en SE4 in 2021 geven 3,51 en 2,97 door een vrijwel lege opwekreeks; 51 van de 296 rijen komen uit instraling.",
    ("fact_land_jaar", "aandeel_zon"): "Onderschat zon achter de meter; gebruik het aandeel van Ember.",
    ("fact_flex_land", "irr_realistisch"): "34% leeg: dat zijn de zone-jaren met de laagste omzet, geen ontbrekende metingen.",
    ("fact_batterij_volledige_case", "irr"): "40% leeg: varianten waarin de investering nooit terugkomt.",
    ("fact_kernenergie_land_jaar", "benutting_tov_vermogen"): "Onbetrouwbaar voor Belgie (boven 1).",
    ("fact_afrr_energie_nl", "op_eur_mwh"): "Reeks stopt op 26 september 2025.",
    ("fact_afrr_energie_nl", "af_eur_mwh"): "Reeks stopt op 26 september 2025.",
    ("fact_wereld_markten", "capture_zon_instraling"): "Schatting uit instraling, zonder afschakelen. De gemeten opwek in Californie ligt hoger (0,50 tegen 0,39 in 2025): parken schakelen af bij negatieve prijzen.",
    ("fact_weer_uur", "straling_w_m2"): "Gestempeld op het eind van het uur (gemiddelde over het voorgaande uur). Schuif een uur terug voordat je met prijzen of opwek rekent.",
    ("fact_vs_dag", "opwek_uren"): "Minder dan 24 betekent dat EIA die dag uren mist; de opwekkolommen zijn dan niet bruikbaar.",
    ("fact_ember_opwek_jaar", "Share of generation (%)"): "Bij de rijen Demand en Net imports is dit een verhouding tot de opwek: onder 0 en boven 100 komt voor.",
    ("fact_vs_opwek_jaar", "capture_rate"): "Kleine bronnen die alleen bij schaarste draaien halen waarden boven 2 (waterkracht Texas 2023: 2,99).",
    "jaar": "2026 loopt tot 15 november.",
}
BEREIK = {"capture_zon": (0, 2), "capture_wind": (0, 2), "capture_rate": (0, 5), "negatieve_uren": (0, 8784), "uren": (0, 8784), "maand": (1, 12), "uur": (0, 23),
          "prijs_eur_mwh": (-500, 5000), "voorspel_ratio": (0, 1.0001), "wacc": (0, 0.3), "dagspreiding": (0, 5000), "uren_opslag": (1, 4),
          "uur_bron": (1, 24)}
FRACTIES = ("aandeel_zon", "aandeel_wind", "aandeel_kern", "aandeel_opwek", "aandeel_in_negatieve_uren", "aandeel_productie_negatief", "aandeel_zon_energycharts",
            "aandeel_wind_energycharts", "aandeel_dagen_met_verlies")
TIJD = ("timestamp_utc", "vanaf_utc", "kwartier_utc", "datum", "Date", "periode")


def bron(tabel):
    if tabel in TABELLEN:
        return TABELLEN[tabel][1]
    return next((v for k, v in VOORVOEGSEL.items() if tabel.startswith(k)), "eigen berekening")


def meta(tabel, kolom):
    """(beschrijving, eenheid, regels, verwant, alias) voor een kolom; leeg als ze nog niet beschreven is."""
    return KOLOMMEN.get((tabel, kolom)) or KOLOMMEN.get(kolom) or ("", "", "", "", "")


def getal(x):
    if x != x:
        return ""
    return f"{x:,.0f}".replace(",", ".") if abs(x) >= 1000 else f"{x:.3g}".replace(".", ",")


def bouw(data=DATA):
    """Leest het profiel en geeft (regels voor de markdown, schema als dict, dekking)."""
    p = pd.read_csv(os.path.join(data, "fact_profiel_DA.csv"))
    w = pd.read_csv(os.path.join(data, "fact_waarden_DA.csv"))
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Tabellen in powerbi/data", "type": "object", "$defs": {}}
    regels, beschreven = [], 0
    for tabel, kol in p.groupby("dataset", sort=True):
        rij, br = TABELLEN.get(tabel, ("(nog te beschrijven)", ""))[0], bron(tabel)
        regels += [f"## {tabel}", "", f"Een rij is {rij}. Bron: {br}. Rijen: {getal(float(kol.rijen.iloc[0]))}.", "",
                   "| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |", "|---|---|---|---|---|---|---|---|---|---|"]
        eig, verplicht = {}, []
        for r in kol.itertuples():
            b, eenheid, regel, verwant, alias = meta(tabel, r.kolom)
            beschreven += bool(b)
            probleem = PROBLEMEN.get((tabel, r.kolom)) or PROBLEMEN.get(r.kolom, "")
            waarden = w[(w.dataset == tabel) & (w.kolom == r.kolom)]
            leeg = "geen" if r.ontbreekt == 0 else f"{r.ontbreekt_pct:.0f}% leeg".replace("0% leeg", "enkele leeg")
            if r.type == "getal":
                bereik, vb = f"{getal(r.min)} tot {getal(r.max)}", f"mediaan {getal(r.mediaan)}"
                e = {"type": "number" if r.ontbreekt == 0 else ["number", "null"], "x-waargenomen": [None if r.min != r.min else float(r.min), None if r.max != r.max else float(r.max)]}
                grens = BEREIK.get((tabel, r.kolom)) or BEREIK.get(r.kolom) or ((0, 1.0001) if r.kolom in FRACTIES else None)
                if grens:
                    e["minimum"], e["maximum"] = grens
            else:
                namen = [v for v in waarden.waarde if not str(v).startswith("overig (")]
                volledig = len(namen) == len(waarden) and len(namen) <= 12
                bereik = f"{int(r.uniek)} verschillende waarden"
                vb = "; ".join(str(v) for v in namen[:3])
                e = {"type": "string" if r.ontbreekt == 0 else ["string", "null"]}
                if r.kolom in TIJD:
                    e["format"] = "date-time" if "utc" in r.kolom else "date"
                elif volledig and r.uniek > 0:
                    e["enum"] = [str(v) for v in namen] + ([None] if r.ontbreekt else [])
            if b:
                e["description"] = b + (f" Eenheid: {eenheid}." if eenheid else "")
            if r.ontbreekt == 0:
                verplicht.append(r.kolom)
            eig[r.kolom] = e
            naam = f"`{r.kolom}`" + (f" (ook: {alias})" if alias else "")
            regels.append(f"| {naam} | {r.type} | {b or 'nog te beschrijven'} | {eenheid} | {bereik} | {leeg} | {regel} | {verwant} | {probleem} | {vb} |")
        regels.append("")
        schema["$defs"][tabel] = {"type": "object", "description": f"Een rij is {rij}. Bron: {br}.", "properties": eig, "required": verplicht, "x-rijen": int(kol.rijen.iloc[0])}
    return regels, schema, (beschreven, len(p), p.dataset.nunique())


def valideer(df, tabelschema):
    """Toetst een tabel tegen haar schema. Geeft een lijst (soort, kolom, toelichting); leeg betekent in orde."""
    fouten, eig = [], tabelschema["properties"]
    for k in eig:
        if k not in df.columns:
            fouten.append(("kolom ontbreekt", k, "staat wel in het schema"))
    for k in df.columns:
        if k not in eig:
            fouten.append(("nieuwe kolom", k, "staat niet in het schema"))
    for k, e in eig.items():
        if k not in df.columns:
            continue
        s, soorten = df[k], e["type"] if isinstance(e["type"], list) else [e["type"]]
        if "null" not in soorten and s.isna().any():
            fouten.append(("lege waarden", k, f"{int(s.isna().sum())} leeg in een verplichte kolom"))
        if "number" in soorten:
            if not pd.api.types.is_numeric_dtype(s):
                fouten.append(("verkeerd type", k, f"verwacht een getal, gevonden {s.dtype}"))
                continue
            if "minimum" in e and (s.dropna() < e["minimum"]).any():
                fouten.append(("onder de ondergrens", k, f"{int((s < e['minimum']).sum())} waarden onder {e['minimum']}; laagste {s.min():.4g}"))
            if "maximum" in e and (s.dropna() > e["maximum"]).any():
                fouten.append(("boven de bovengrens", k, f"{int((s > e['maximum']).sum())} waarden boven {e['maximum']}; hoogste {s.max():.4g}"))
        elif "enum" in e:
            vreemd = set(s.dropna().astype(str)) - {v for v in e["enum"] if v is not None}
            if vreemd:
                fouten.append(("onbekende waarde", k, ", ".join(sorted(vreemd)[:5])))
    return fouten


def main(data=DATA, uit=UIT):
    regels, schema, (beschreven, kolommen, tabellen) = bouw(data)
    kop = ["# Datawoordenboek", "", f"{tabellen} tabellen en {kolommen} kolommen in `powerbi/data` (zonder de `_DA`- en `_SA`-tabellen). "
           f"Van {beschreven} kolommen is de betekenis beschreven; bij de overige staat 'nog te beschrijven'.", "",
           "Type, bereik, lege waarden en voorbeelden komen uit het profiel (`fact_profiel_DA`) en verversen bij elke run van `eti.da`. "
           "Beschrijving, eenheid, regels en bekende problemen staan in `src/eti/woordenboek.py`.", "",
           "Het schema voor automatische controle staat in `datawoordenboek.schema.json`; `eti.woordenboek.valideer()` toetst een tabel ertegen.", ""]
    os.makedirs(uit, exist_ok=True)
    with open(os.path.join(uit, "datawoordenboek.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(kop + regels))
    with open(os.path.join(uit, "datawoordenboek.schema.json"), "w", encoding="utf-8") as fh:
        json.dump(schema, fh, ensure_ascii=False, indent=1)
    print(f"  -> datawoordenboek.md en datawoordenboek.schema.json: {tabellen} tabellen, {kolommen} kolommen, {beschreven} beschreven")
    return schema


if __name__ == "__main__":
    main(*sys.argv[1:3])
