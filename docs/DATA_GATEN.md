# Ontbrekende regio's, landen en energiebronnen: waar de data te halen is (28 november 2026)

Stand van de repo: 37 Europese biedzones met uurprijzen (Energy-Charts), plus CAISO, ERCOT, AEMO (Zuid-Australie), JEPX en Elexon.
De kaart op dashboard 1 meldt zelf "No data UK, Ireland & the Balkans". Buiten Europa zijn er alleen zonlocaties (PVGIS) en
kapitaalkosten, geen marktprijzen. Per bron staat hieronder wat het toevoegt en wie het moet ophalen.

## A. Gaten in Europa

| Gat | Bron | Wat het toevoegt | Ophalen |
|---|---|---|---|
| Ierland, Verenigd Koninkrijk, Balkan, Baltische staten als land | Ember, European Wholesale Electricity Price Data (uur, dag, maand; ENTSO-E, opgeschoond) | Een bestand met uurprijzen voor alle Europese landen: vult de kaart op dashboard 1, en de dashboards 2, 16, 18 en 19 | ember-energy.org/data/european-wholesale-electricity-price-data, zip met uurdata |
| Montenegro, Noord-Macedonie, Ierland (SEM) per biedzone | ENTSO-E Transparency of ACER CHEST (figuren bij het marktmonitoringrapport, per biedzone, csv) | Dezelfde zones als ACER gebruikt, met prijzen per zone en jaar | aegis.acer.europa.eu/chest (gratis account voor export) |
| Opwek per bron voor landen zonder Energy-Charts | Ember, Monthly Electricity Data (88 gebieden) en Yearly Electricity Data (meer dan 200) | Zon, wind, waterkracht, gas, kolen en kern per maand: nodig om de capture rate buiten de 37 zones te schatten | ember-energy.org/data/monthly-electricity-data |
| Batterijen per land | SolarPower Europe, EU Battery Storage Market Review 2025; European Energy Storage Inventory (Commissie) | Geinstalleerd vermogen per land: de ontbrekende as op dashboards 18, 29 en 38 (verzadiging tegenover opbrengst) | rapport (pdf) en het dashboard van de Commissie |
| Curtailment | Ember, European Electricity Review 2026; rapport over prijsgevoelige curtailment per land | Hoeveel zon wordt weggegooid: aanvulling op negatieve uren (dashboards 8, 16, 28) | pdf; cijfers per land overnemen |

## B. Gaten buiten Europa

| Gat | Bron | Wat het toevoegt | Ophalen |
|---|---|---|---|
| India | IEX, Day-Ahead Market snapshot (kwartierblokken vanaf 1 april 2022) | Eerste marktprijs in het Mondiale Zuiden: maakt dashboard 15 van zon en kapitaal tot zon, kapitaal en opbrengst | iexindia.com, market data; per periode exporteren |
| Australie, alle deelstaten | Open Electricity API (NEM en WEM), licentie CC BY-NC | Vijf deelstaten naast Zuid-Australie op dashboard 28 | gratis account en API-sleutel |
| Zon- en windparken wereldwijd | Global Energy Monitor, Global Solar Power Tracker en Global Wind Power Tracker | Wat gebouwd is en wat gepland is, per land: de pijplijn voor dashboards 10, 11 en 15 | globalenergymonitor.org, Download data (formulier) |
| Opwek per bron wereldwijd | Ember Yearly Electricity Data | Dekt Afrika, Latijns-Amerika en Zuidoost-Azie op jaarbasis | zie boven |

## C. Ontbrekende energiebronnen en aanknopingspunten

| Onderwerp | Bron | Wat het toevoegt |
|---|---|---|
| Wind | Al in de repo: `Capture rate wind` staat in t2 maar op geen dashboard | Zon tegenover wind in dezelfde grafiek: wind verliest minder waarde. Geen download nodig |
| Batterijprijzen | BloombergNEF, prijsenquete december 2025 | Pakketprijs 108 dollar per kWh; voor stationaire opslag 70 dollar. Actueler dan de Schmidt-reeks (t98, tot 2021) |
| Batterijpijplijn | Ember, European Electricity Review 2026 | Pijplijn boven 40 GW in de EU; sluit aan op de wachtrij (t95) |
| Netkosten en groothandel samen | ACER CHEST, data bij het marktmonitoringrapport | Groothandelsprijs naast "energy and supply" per regio: koppelt dashboard 41 aan dashboard 2 |

## D. Volgorde van ophalen
1. **Ember uurprijzen Europa**: een download, vult het grootste zichtbare gat (de kaart) en vier dashboards.
2. **Ember maand- en jaardata**: een download, dekt wind, waterkracht en de rest van de wereld.
3. **SolarPower Europe batterijen per land**: overnemen uit het rapport; maakt drie batterijdashboards af.
4. **IEX India**: handwerk per periode; alleen als dashboard 15 een marktprijs moet krijgen.
5. De rest na de herbeoordeling.

## E. Wat zonder download kan
- Wind naast zon (t2).
- BNEF-prijzen als twee punten achter t98 (bron vermelden; niet uit een bestand).
- Curtailment Duitsland 2025 als voetnoot op dashboard 16.

## F. Opgehaald en verwerkt op 28 november 2026
| Tabel | Bron | Inhoud |
|---|---|---|
| t104_europe_price_countries | Ember, uurprijzen Europa (zip, 43 MB, 34 landen) | 249 rijen: prijs, negatieve uren, dagspreiding en middagindex per land en jaar, met het aandeel zon en wind. Nieuw: Ierland, Verenigd Koninkrijk, Montenegro, Noord-Macedonie, Albanie, Kosovo, Moldavie, Luxemburg |
| t105_world_generation | Ember, jaardata (224 gebieden) | 21.064 rijen: opwek, aandeel en vermogen per land, bron en jaar, 2015-2025, zes werelddelen |
| t106_wind_vs_solar | eigen t2 | capture rate van zon en wind per jaar, mediaan van 37 zones en Nederland (mediaan van maandwaarden) |
| t107_battery_fleet | SolarPower Europe, EU Battery Storage Market Review 2025 | vijf EU-landen, het VK en de EU: bijgeplaatst 2024 en 2025, en totaal eind 2025 (totaal per land van een grafiek afgelezen) |

Bronbestanden: `data/raw/ember/` (niet op GitHub). Code: `src/eti/ember_extra.py`. De maanddata van Ember (184.503 rijen) zijn
opgehaald maar nog niet tot een tabel verwerkt.

Niet opgehaald, omdat een account, sleutel of formulier nodig is: ACER CHEST, Open Electricity (Australie), Global Energy Monitor
en IEX India (export per periode met de hand).

## G. Wereldwijde investeringscontext, opgehaald op 28 november 2026 (middag)
| Tabel | Bron | Inhoud |
|---|---|---|
| t108_country_risk | Damodaran (NYU Stern), landenrisico januari 2026 | 157 landen: Moody's-rating, default spread, landenrisicopremie en totale aandelenrisicopremie. Basis voor een kapitaalkost per land |
| t109_carbon_prices | Wereldbank, Carbon Pricing Dashboard (mei 2026) | 1.324 rijen: CO2-prijs per instrument (ETS of belasting) en jaar, 1990-2026, met regio en inkomensgroep |
| t110_public_investment | IRENA, IRENASTAT (2026 H2) | 8.366 rijen: internationale publieke investeringen per ontvangend land, technologie en jaar, 2000-2024, in miljoen dollar van 2023 |
| t111_country_macro | Wereldbank, WDI | 217 landen, 2015-2025: leenrente, bbp per hoofd, toegang tot stroom, inflatie, bevolking |

Bronbestanden: `data/raw/wereld/` (niet op GitHub). Code: `src/eti/wereld_bronnen.py`
(draaien met `PYTHONPATH=src python -m eti.wereld_bronnen`). Ook opgehaald, nog geen tabel: de energiedataset van
Our World in Data (23.195 rijen, tot en met 2024).

Let op:
- t110 telt alleen internationale publieke stromen (ontwikkelingsbanken en hulp), geen private investeringen.
  De export van IRENA verliest accenten in drie landnamen; de code herstelt die.
- t108 is een premie voor aandelen in dollars. Een kapitaalkost voor een zonnepark vraagt daarnaast een aanname
  voor de schuldrente en de verhouding eigen en vreemd vermogen.
- t111: de leenrente ontbreekt voor veel landen (onder meer het eurogebied).

Nog met de hand op te halen (account of formulier): IEA World Energy Investment 2026, IEA World Energy Outlook 2026
(gratis dataset), IEA Cost of Capital Observatory, Global Solar Atlas (zonpotentie per land), BloombergNEF Climatescope
en de Wereldbank-scores voor regelgeving (RISE).

## H. Uploads van 28 november 2026 (tabellen t112-t119)
| Tabel | Bron | Inhoud |
|---|---|---|
| t112_wei_investment | IEA World Energy Investment 2026 | 11 regio's, 12 categorieen, 2015-2026, miljard USD (totaal, schone energie, fossiel, zon, wind, batterijen, kern) |
| t113_weo_world_scenarios | IEA WEO 2026, Annex A (CC BY-NC-SA) | totale energievoorziening, elektriciteit, capaciteit, eindverbruik en CO2 per scenario, 2010-2050 |
| t114_lbnl_solar_cost | LBNL, US Utility-Scale Solar 2026 | LCOE (2025 USD per MWh, met en zonder belastingkrediet) per jaar 2010-2025 en installatiekosten (2025 USD per Wac) 2007-2025 |
| t115_solargis_pv_potential | Solargis / Wereldbank, PV-potentieentabel 2020 | 209 landen: GHI, praktisch en economisch PV-potentieel en seizoensindex |
| t116_rise_scores | RISE (Wereldbank), pijlers EE en RE | totaalscore per land en jaar, 2010-2023 |
| t117_iex_india_dam_28nov2026 | IEX India, dag-vooruitmarkt en GDAM | 96 kwartieren op 28 november 2026; alleen dat ene handelsdag, GDAM zonder prijskolom |
| t118_gem_solar_wind | Global Energy Monitor, zon (1 MW+) en wind (februari 2026) | aantal projecten en MW per land en status |

Let op:
- t112 en t113 zijn wereldtotalen en regio's, geen landen.
- t116 is een score van 0 tot 100 en geen meting; de pijlers zijn niet vergelijkbaar tussen landen met verschillende inkomensgroepen.
- t117 dekt een dag. Voor een reeks zijn meer dagen nodig.
- t118 telt projecten met hun huidige status; geannuleerde en onbekende projecten zitten er ook in.
- t114: de kolomnamen beschrijven de eenheid per rij (LCOE of installatiekosten).

Nog niet opgehaald of niet getabeld: ACER CHEST (account nodig), Open Electricity (sleutel staat in .env, data nog niet opgehaald),
Global Solar Atlas-rasters (kaartlagen, geen tabel), IEA Cost of Capital Observatory (033bad13, nog niet geopend),
Climatescope-scores per land (alleen top 10 uit het rapport, t119 in outputs).

## I. Australie via Open Electricity, opgehaald op 28 november 2026
| Tabel | Bron | Inhoud |
|---|---|---|
| t120_australia_price_daily | Open Electricity API v4 (CC BY-NC 4.0) | dagprijs voor NEM en WEM in AUD per MWh, 1 januari 2025 tot en met 26 november 2026 |
| t121_australia_generation_daily | Open Electricity API v4 (CC BY-NC 4.0) | opwekking per dag, regio (NSW1, QLD1, SA1, TAS1, VIC1, WEM) en brandstof in MWh, zelfde periode |

Code: `eti.openelectricity_fetch` (ophalen, sleutel uit .env) en `eti.australie_tabellen` (tabellen).
Let op:
- Het gratis abonnement (Community) geeft alleen de laatste 730 dagen; 2024 ontbreekt daardoor.
- 31 december 2025 ontbreekt (de einddatum van de aanvraag telt niet mee).
- De prijs is een gemiddelde per netwerk, niet per regio. Dagwaarden tonen geen middagdip; daarvoor zijn uur- of 5-minutenwaarden nodig.
- Licentie: niet-commercieel gebruik met bronvermelding "Open Electricity".
