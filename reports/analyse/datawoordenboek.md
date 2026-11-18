# Datawoordenboek

88 tabellen en 653 kolommen in `powerbi/data` (zonder de `_DA`- en `_SA`-tabellen). Van 260 kolommen is de betekenis beschreven; bij de overige staat 'nog te beschrijven'.

Type, bereik, lege waarden en voorbeelden komen uit het profiel (`fact_profiel_DA`) en verversen bij elke run van `eti.da`. Beschrijving, eenheid, regels en bekende problemen staan in `src/eti/woordenboek.py`.

Het schema voor automatische controle staat in `datawoordenboek.schema.json`; `eti.woordenboek.valideer()` toetst een tabel ertegen.

## dim_datum

Een rij is een dag: jaar, kwartaal, maand, week, weekdag en feestdag, als datumtabel voor Power BI. Bron: eigen berekening. Rijen: 4.383.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `datum` | tekst | nog te beschrijven |  | 4383 verschillende waarden | geen |  |  |  | 2019-01-01; 2026-12-30; 2027-01-05 |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.030 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `kwartaal` | getal | nog te beschrijven |  | 1 tot 4 | geen |  |  |  | mediaan 3 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 7 |
| `dag` | getal | nog te beschrijven |  | 1 tot 31 | geen |  |  |  | mediaan 16 |
| `maandnaam` | tekst | nog te beschrijven |  | 12 verschillende waarden | geen |  |  |  | januari; maart; mei |
| `jaarmaand` | tekst | nog te beschrijven |  | 144 verschillende waarden | geen |  |  |  | 2019-01; 2023-07; 2027-01 |
| `jaarkwartaal` | tekst | nog te beschrijven |  | 48 verschillende waarden | geen |  |  |  | 2030 K4; 2022 K4; 2028 K3 |
| `isojaar` | getal | nog te beschrijven |  | 2.019 tot 2.031 | geen |  |  |  | mediaan 2.025 |
| `week` | getal | nog te beschrijven |  | 1 tot 53 | geen |  |  |  | mediaan 27 |
| `weekdag_nr` | getal | nog te beschrijven |  | 1 tot 7 | geen |  |  |  | mediaan 4 |
| `weekdag` | tekst | nog te beschrijven |  | 7 verschillende waarden | geen |  |  |  | dinsdag; woensdag; donderdag |
| `feestdag` | tekst | nog te beschrijven |  | 10 verschillende waarden | 97% leeg |  |  |  | Nieuwjaarsdag; Eerste paasdag; Tweede paasdag |
| `werkdag` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | True; False |
| `seizoen` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | zomerhalfjaar; winterhalfjaar |

## dim_land

Een rij is een land met indelingen. Bron: Ember, eigen indeling. Rijen: 209.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `iso3` (ook: ISO 3 code) | tekst | Landcode volgens ISO 3166 (drie letters). |  | 209 verschillende waarden | geen | koppelt aan Ember | land |  | AFG; LBN; NCL |
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 209 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Afghanistan; Lebanon; New Caledonia |
| `continent` | tekst | nog te beschrijven |  | 6 verschillende waarden | geen |  |  |  | Africa; Asia; Europe |
| `ember_regio` | tekst | nog te beschrijven |  | 7 verschillende waarden | geen |  |  |  | Africa; Latin America and Caribbean; Europe |
| `eu` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | False; True |
| `oecd` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | False; True |
| `g20` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | False; True |
| `studieregio` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | Rest van de wereld; Europa; China |

## dim_markt

Een rij is een markt met de studieregio waar ze bij hoort. Bron: eigen indeling. Rijen: 41.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `markt` | tekst | Naam van de markt buiten de EU (Texas, Californie, Japan, een Australische deelstaat). |  | 41 verschillende waarden | geen |  | jaar |  | Belgie; Noorwegen (Oslo); Noorwegen (Zuid) |
| `studieregio` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | Europa; Rest van de wereld; Nederland |

## dim_regio

Een rij is een studieregio: kapitaalkosten, vollasturen, investering. Bron: aannames uit het memo, per regio nagezocht. Rijen: 5.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `regio` | tekst | Studieregio (Nederland, Europa, VS, China, India). |  | 5 verschillende waarden | geen |  |  |  | Nederland; Europa (Spanje); VS (Texas) |
| `wacc` (ook: kapitaalkosten) | getal | Gewogen kapitaalkosten. | fractie per jaar | 0,045 tot 0,12 | geen | 0 tot 0,3 | lcoe_eur_mwh |  | mediaan 0,055 |
| `vollasturen` | getal | Vollasturen van zon per jaar. | uur per jaar | 740 tot 2.190 | geen |  | capex_eur_kw |  | mediaan 1.500 |
| `capex_eur_kw` | getal | Investering per kW vermogen. | euro per kW | 350 tot 1.450 | geen |  |  |  | mediaan 450 |
| `netintensiteit_g_kwh` | getal | CO2-intensiteit van het net. | gram per kWh | 100 tot 708 | geen |  |  |  | mediaan 384 |
| `fx_kosten` | getal | nog te beschrijven |  | -0,005 tot 0,045 | geen |  |  |  | mediaan 0 |

## fact_afrr_energie_nl

Een rij is een kwartier: prijs van geactiveerde regelenergie (aFRR), op en af. Bron: ENTSO-E (document A84). Rijen: 95.464.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `kwartier_utc` | tekst | nog te beschrijven |  | 95464 verschillende waarden | geen |  |  |  | 2023-01-01 00:00:00; 2024-10-27 04:00:00; 2024-10-27 06:15:00 |
| `op_eur_mwh` | getal | Prijs van geactiveerde opregelenergie in het kwartier. | euro per MWh | -10 tot 5.500 | geen | leeg als niet geactiveerd | af_eur_mwh | Reeks stopt op 26 september 2025. | mediaan 73,7 |
| `af_eur_mwh` | getal | Prijs van geactiveerde afregelenergie in het kwartier. | euro per MWh | -1.862 tot 447 | geen | leeg als niet geactiveerd | op_eur_mwh | Reeks stopt op 26 september 2025. | mediaan 0 |

## fact_australie

Een rij is een Australische deelstaat in een jaar. Bron: AEMO via Open Electricity. Rijen: 40.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `regio` | tekst | Studieregio (Nederland, Europa, VS, China, India). |  | 5 verschillende waarden | geen |  |  |  | Australie (Zuid); Australie (Victoria); Australie (Queensland) |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `uren` | getal | Aantal uren met een prijs in de periode. | uren | 7.287 tot 8.775 | geen | 8.760 of 8.784 in een heel jaar | jaar |  | mediaan 8.751 |
| `gem_prijs_eur` | getal | Gemiddelde groothandelsprijs, omgerekend naar euro. | euro per MWh | 20,1 tot 123 | geen | wisselkoers van het jaar |  |  | mediaan 50,1 |
| `capture_zon_instraling` | getal | Capture rate van zon, geschat met een instralingsprofiel in plaats van gemeten opwek. | verhouding | -0,0326 tot 1,19 | geen | benadering; niet mengen met gemeten zones | capture_rate |  | mediaan 0,502 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 1 tot 2.616 | geen | 0 tot 8.784 | uren |  | mediaan 646 |
| `batterij_2u_realistisch_eur_per_mw` | getal | Dagmarktomzet van een batterij van 2 uur, plan op gisteren, lokale dagen. | euro per MW per jaar | 6.426 tot 146.285 | geen |  |  |  | mediaan 42.861 |

## fact_australie_dagprofiel

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 32.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `regio` | tekst | Studieregio (Nederland, Europa, VS, China, India). |  | 4 verschillende waarden | geen |  |  |  | Australie (Zuid); Australie (Victoria); Australie (Queensland) |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `dagen_jan_okt` | getal | nog te beschrijven |  | 304 tot 305 | geen |  |  |  | mediaan 304 |
| `gem_dagomzet_eur_per_mw` | getal | nog te beschrijven |  | 61,7 tot 441 | geen |  |  |  | mediaan 155 |
| `mediaan_dagomzet_eur_per_mw` | getal | nog te beschrijven |  | 30,4 tot 204 | geen |  |  |  | mediaan 91,1 |
| `aandeel_top10_dagen` | getal | nog te beschrijven |  | 0,13 tot 0,579 | geen |  |  |  | mediaan 0,369 |
| `dagen_met_uurprijs_boven_1000_aud` | getal | nog te beschrijven |  | 1 tot 52 | geen |  |  |  | mediaan 8,5 |
| `mediaan_netto_spreiding_eur_mwh` | getal | nog te beschrijven |  | 22 tot 134 | geen |  |  |  | mediaan 77,9 |
| `mediaan_middagprijs_eur_mwh` | getal | nog te beschrijven |  | -13,4 tot 61,6 | geen |  |  |  | mediaan 17,3 |
| `mediaan_avondprijs_eur_mwh` | getal | nog te beschrijven |  | 33,8 tot 163 | geen |  |  |  | mediaan 72,6 |

## fact_balans_nl_jaar

Een rij is een jaar: samenvatting van FCR en aFRR. Bron: eigen berekening. Rijen: 4.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.023 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `fcr_kwartieren` | getal | nog te beschrijven |  | 30.761 tot 35.136 | geen |  |  |  | mediaan 35.038 |
| `fcr_mediaan_eur_mw_uur` | getal | nog te beschrijven |  | 11 tot 19,1 | geen |  |  |  | mediaan 13,2 |
| `fcr_gemiddeld_eur_mw_uur` | getal | nog te beschrijven |  | 12,8 tot 22,6 | geen |  |  |  | mediaan 17,7 |
| `fcr_omzet_per_mw_bij_volledige_inzet` | getal | nog te beschrijven |  | 112.176 tot 197.601 | geen |  |  |  | mediaan 155.086 |
| `afrr_kwartieren` | getal | nog te beschrijven |  | 25.505 tot 35.103 | 25% leeg |  |  |  | mediaan 34.856 |
| `afrr_op_aandeel_kwartieren` | getal | nog te beschrijven |  | 0,473 tot 0,667 | 25% leeg |  |  |  | mediaan 0,555 |
| `afrr_op_prijs_gemiddeld` | getal | nog te beschrijven |  | 141 tot 187 | 25% leeg |  |  |  | mediaan 170 |
| `afrr_af_aandeel_kwartieren` | getal | nog te beschrijven |  | 0,524 tot 0,676 | 25% leeg |  |  |  | mediaan 0,629 |
| `afrr_af_prijs_gemiddeld` | getal | nog te beschrijven |  | 0,142 tot 23,2 | 25% leeg |  |  |  | mediaan 18,7 |

## fact_batterij_breakeven_BI

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 9.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `cycli_per_dag` | getal | nog te beschrijven |  | 1 tot 2 | geen |  |  |  | mediaan 1 |
| `netkosten` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | geen netkosten; tijdsafhankelijk transportrecht; stapeling, vast transportrecht |
| `omzet_per_mw` | getal | Omzet per MW per jaar van de genoemde strategie. | euro per MW per jaar | 87.194 tot 305.000 | geen |  |  |  | mediaan 101.704 |
| `levensduur_jaar` | getal | nog te beschrijven |  | 8 tot 15 | geen |  |  |  | mediaan 15 |
| `max_capex_per_kwh_voor_8pct` | getal | nog te beschrijven |  | 77,3 tot 586 | geen |  |  |  | mediaan 246 |
| `max_capex_per_kwh_voor_5pct` | getal | nog te beschrijven |  | 87,6 tot 680 | geen |  |  |  | mediaan 273 |

## fact_batterij_bronnen_BB

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 296.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 37 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Italie (Sicilie); Oostenrijk; Denemarken (Oost) |
| `biedzone` (ook: zone, bidding zone) | tekst | Code van de biedzone (NL, DE-LU, IT-North, NO1). |  | 37 verschillende waarden | geen | 37 zones | land |  | IT-Sicily; AT; DK2 |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `dagmarkt_per_mw` | getal | nog te beschrijven |  | 597 tot 100.085 | geen |  |  |  | mediaan 30.374 |
| `fcr_lid` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | False; True |
| `fcr_dagen_in_data` | getal | nog te beschrijven |  | 264 tot 334 | 89% leeg |  |  |  | mediaan 310 |
| `fcr_per_mw` | getal | nog te beschrijven |  | 116.179 tot 201.977 | 89% leeg |  |  |  | mediaan 155.967 |
| `afrr_capaciteit_50pct_per_mw` | getal | nog te beschrijven |  | 118.260 tot 118.260 | 10enkele leeg |  |  |  | mediaan 118.260 |
| `afrr_capaciteit_100pct_per_mw` | getal | nog te beschrijven |  | 236.520 tot 236.520 | 10enkele leeg |  |  |  | mediaan 236.520 |
| `fcr_gedeeld_door_dagmarkt` | getal | nog te beschrijven |  | 2,32 tot 5,96 | 89% leeg |  |  |  | mediaan 2,9 |
| `grootste_bron` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | dagmarkt; FCR |

## fact_batterij_bronnen_nl_BB

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 5.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.022 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `dagmarkt_per_mw` | getal | nog te beschrijven |  | 47.320 tot 82.442 | geen |  |  |  | mediaan 61.041 |
| `fcr_per_mw` | getal | nog te beschrijven |  | 116.179 tot 201.977 | 2enkele leeg |  |  |  | mediaan 155.967 |
| `fcr_dagen_in_data` | getal | nog te beschrijven |  | 264 tot 334 | 2enkele leeg |  |  |  | mediaan 310 |
| `afrr_capaciteit_50pct_per_mw` | getal | nog te beschrijven |  | 118.260 tot 118.260 | 8enkele leeg |  |  |  | mediaan 118.260 |
| `afrr_capaciteit_100pct_per_mw` | getal | nog te beschrijven |  | 236.520 tot 236.520 | 8enkele leeg |  |  |  | mediaan 236.520 |

## fact_batterij_irr

Een rij is een jaar, strategie en investeringsbedrag: IRR van de batterij. Bron: eigen model. Rijen: 48.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.023 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `strategie` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | Dagmarkt; Gestapeld vooraf, onbalans plan op gisteren; Gestapeld vooraf, onbalans op dagmarktplan |
| `capex_per_mwh` | getal | nog te beschrijven |  | 200.000 tot 300.000 | geen |  |  |  | mediaan 250.000 |
| `irr` (ook: IRR) | getal | Intern rendement van het project. | fractie per jaar | -0,0662 tot 0,492 | geen | leeg als de investering nooit terugkomt |  |  | mediaan 0,0509 |

## fact_batterij_irr_grid_BI

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 63.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `cycli_per_dag` | getal | nog te beschrijven |  | 1 tot 2 | geen |  |  |  | mediaan 1 |
| `omzet_per_mw` | getal | Omzet per MW per jaar van de genoemde strategie. | euro per MW per jaar | 87.194 tot 305.000 | geen |  |  |  | mediaan 101.704 |
| `meeropbrengst_vs_1_cyclus` | getal | nog te beschrijven |  | 0 tot 0,166 | geen |  |  |  | mediaan 0 |
| `levensduur_jaar` | getal | nog te beschrijven |  | 8 tot 15 | geen |  |  |  | mediaan 15 |
| `netkosten` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | geen netkosten; tijdsafhankelijk transportrecht; stapeling, vast transportrecht |
| `capex_per_kwh` | getal | nog te beschrijven |  | 150 tot 400 | geen |  |  |  | mediaan 280 |
| `irr` (ook: IRR) | getal | Intern rendement van het project. | fractie per jaar | -0,27 tot 0,571 | 8% leeg | leeg als de investering nooit terugkomt |  |  | mediaan 0,0444 |

## fact_batterij_stapeling

Een rij is een jaar en strategie: omzet van de batterij. Bron: eigen model. Rijen: 40.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.023 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `strategie` | tekst | nog te beschrijven |  | 10 verschillende waarden | geen |  |  |  | Dagmarkt; Dagmarkt zonder overslaan; Dagmarkt perfect |
| `omzet_eur` | getal | nog te beschrijven |  | 56.351 tot 2.133.437 | geen |  |  |  | mediaan 580.571 |
| `omzet_per_mw` | getal | Omzet per MW per jaar van de genoemde strategie. | euro per MW per jaar | 5.635 tot 213.344 | geen |  |  |  | mediaan 58.057 |
| `irr` (ook: IRR) | getal | Intern rendement van het project. | fractie per jaar | -0,266 tot 0,31 | 5% leeg | leeg als de investering nooit terugkomt |  |  | mediaan -0,00114 |

## fact_batterij_volledige_case

Een rij is een variant van de batterijcase met netkosten. Bron: eigen model, marktcijfers uit het memo. Rijen: 10.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `inkomsten` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | Dagmarkt met bijsturen (eigen model); Volledige stapeling (benchmark); Volledige stapeling, omzet daalt 10 procent per jaar in vijf jaar |
| `netaansluiting` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | vast transportrecht; tijdsafhankelijk transportrecht; geen netkosten, zoals in de memo |
| `omzet_per_mw` | getal | Omzet per MW per jaar van de genoemde strategie. | euro per MW per jaar | 87.194 tot 305.000 | geen |  |  |  | mediaan 215.800 |
| `netkosten_per_mw` | getal | nog te beschrijven |  | 0 tot 150.000 | geen |  |  |  | mediaan 98.500 |
| `na_netkosten_per_mw` | getal | nog te beschrijven |  | -62.806 tot 185.500 | geen |  |  |  | mediaan 113.097 |
| `capex_per_kw` | getal | nog te beschrijven |  | 560 tot 560 | geen |  |  |  | mediaan 560 |
| `daling_per_jaar` | getal | nog te beschrijven |  | 0 tot 0,1 | geen |  |  |  | mediaan 0 |
| `irr` (ook: IRR) | getal | Intern rendement van het project. | fractie per jaar | 0,0178 tot 0,278 | 4enkele leeg | leeg als de investering nooit terugkomt |  | 40% leeg: varianten waarin de investering nooit terugkomt. | mediaan 0,162 |

## fact_bronnen_jaar_RC

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 7.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.025 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `landen` | getal | nog te beschrijven |  | 26 tot 26 | geen |  |  |  | mediaan 26 |
| `verschil_alle_pct` | getal | nog te beschrijven |  | -11,7 tot -5,88 | geen |  |  |  | mediaan -8,03 |
| `landen_zonder_gat` | getal | nog te beschrijven |  | 18 tot 23 | geen |  |  |  | mediaan 21 |
| `verschil_zonder_gat_pct` | getal | nog te beschrijven |  | -1,85 tot 4,58 | geen |  |  |  | mediaan 0,79 |
| `mediane_verhouding_zonder_gat` | getal | nog te beschrijven |  | 0,982 tot 1,04 | geen |  |  |  | mediaan 1,02 |
| `dekkingsgaten` | getal | nog te beschrijven |  | 3 tot 8 | geen |  |  |  | mediaan 5 |

## fact_bronnen_land_RC

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 26.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `iso3` (ook: ISO 3 code) | tekst | Landcode volgens ISO 3166 (drie letters). |  | 26 verschillende waarden | geen | koppelt aan Ember | land |  | ESP; FRA; LTU |
| `jaren` | getal | nog te beschrijven |  | 7 tot 7 | geen |  |  |  | mediaan 7 |
| `dekkingsgat_jaren` | getal | nog te beschrijven |  | 0 tot 7 | geen |  |  |  | mediaan 0 |
| `bruikbare_jaren` | getal | nog te beschrijven |  | 0 tot 7 | geen |  |  |  | mediaan 7 |
| `verhouding_mediaan` | getal | nog te beschrijven |  | 0,55 tot 1,62 | 12% leeg |  |  |  | mediaan 1,04 |
| `verhouding_min` | getal | nog te beschrijven |  | 0,361 tot 1,52 | 12% leeg |  |  |  | mediaan 0,85 |
| `verhouding_max` | getal | nog te beschrijven |  | 0,757 tot 1,71 | 12% leeg |  |  |  | mediaan 1,08 |
| `aandeel_jaren_lager` | getal | nog te beschrijven |  | 0 tot 1 | 12% leeg |  |  |  | mediaan 0,429 |
| `regime` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | structureel hoger in A; wisselend of gelijk; structureel lager in A |
| `geschat_ontbrekend_aandeel_zon` | getal | nog te beschrijven |  | 0 tot 0,45 | geen |  |  |  | mediaan 0 |
| `laatste_jaar` | getal | nog te beschrijven |  | 2.025 tot 2.025 | geen |  |  |  | mediaan 2.025 |
| `ember_zon_twh_laatste_jaar` | getal | nog te beschrijven |  | 0,348 tot 89,7 | geen |  |  |  | mediaan 5,95 |
| `geschat_ontbrekend_twh` | getal | nog te beschrijven |  | 0 tot 4,64 | geen |  |  |  | mediaan 0 |

## fact_bronnen_toets_RC

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 4.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `groep` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | alle landen; structureel hoger in A; structureel lager in A |
| `land_jaren` | getal | nog te beschrijven |  | 18 tot 65 | geen |  |  |  | mediaan 23,5 |
| `mediane_fout_zonder_correctie` | getal | nog te beschrijven |  | 0,0638 tot 0,246 | geen |  |  |  | mediaan 0,138 |
| `mediane_fout_met_correctie` | getal | nog te beschrijven |  | 0,0205 tot 0,089 | geen |  |  |  | mediaan 0,0723 |
| `aandeel_beter` | getal | nog te beschrijven |  | 0,13 tot 0,889 | geen |  |  |  | mediaan 0,717 |

## fact_capture_curve

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 6.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `capture_rate` | getal | Capture rate van de genoemde techniek of brandstof. | verhouding | 0,6 tot 1,1 | geen | tussen 0 en 2 | capture_price |  | mediaan 0,85 |
| `irr` (ook: IRR) | getal | Intern rendement van het project. | fractie per jaar | 0,0296 tot 0,131 | geen | leeg als de investering nooit terugkomt |  |  | mediaan 0,0842 |

## fact_ember_capaciteit_maand

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 20.901.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Year` (ook: jaar) | getal | Kalenderjaar. | jaar | 2.016 tot 2.026 | geen |  |  |  | mediaan 2.021 |
| `Month` | getal | nog te beschrijven |  | 1 tot 12 | geen |  |  |  | mediaan 6 |
| `ISO 3 Code` | tekst | nog te beschrijven |  | 32 verschillende waarden | 18% leeg |  |  |  | DNK; NLD; DEU |
| `Area` | tekst | Land of regio volgens Ember. |  | 32 verschillende waarden | geen |  | ISO 3 code |  | Denmark; Netherlands; Germany |
| `Continent` | tekst | nog te beschrijven |  | 6 verschillende waarden | geen |  |  |  | Europe; Asia; South America |
| `Source` | tekst | nog te beschrijven |  | 6 verschillende waarden | geen |  |  |  | Solar; Wind; Wind and solar |
| `Installed Capacity` | getal | nog te beschrijven |  | 0 tot 2.275 | geen |  |  |  | mediaan 5,52 |
| `Capacity additions (month-on-month)` | getal | nog te beschrijven |  | -0,7 tot 137 | enkele leeg |  |  |  | mediaan 0,04 |

## fact_ember_china_provincie

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 3.308.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 1 verschillende waarden | geen |  | ISO 3 code |  | China |
| `Province` | tekst | nog te beschrijven |  | 32 verschillende waarden | geen |  |  |  | China (total); Anhui; Inner Mongolia |
| `Year` (ook: jaar) | getal | Kalenderjaar. | jaar | 2.011 tot 2.025 | geen |  |  |  | mediaan 2.018 |
| `Electricity source` | tekst | Opwekbron of saldo (Solar, Wind, Gas, Demand, Net imports). |  | 7 verschillende waarden | geen |  |  |  | Coal; Gas; Clean |
| `Generation (TWh)` | getal | Opwek in het jaar. | TWh | 0 tot 10.506 | geen |  |  |  | mediaan 41,4 |
| `Share of generation (%)` | getal | Aandeel in de totale opwek. | procent | 0 tot 100 | geen | 0 tot 100 |  |  | mediaan 20,7 |
| `Emissions (MtCO2e)` | getal | Uitstoot van de elektriciteitsopwek. | megaton CO2-equivalent | 0 tot 5.957 | geen |  |  |  | mediaan 2,96 |

## fact_ember_cleantech_export

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 137.203.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 250 verschillende waarden | geen |  | ISO 3 code |  | Maldives; Pakistan; Myanmar |
| `Date` | tekst | nog te beschrijven |  | 105 verschillende waarden | geen |  |  |  | 2024-08-01; 2026-06-01; 2026-04-01 |
| `Area type` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | Country or economy; Region |
| `Region` | tekst | nog te beschrijven |  | 7 verschillende waarden | 6% leeg |  |  |  | Africa; Latin America and Caribbean; Europe |
| `Commodity category` | tekst | nog te beschrijven |  | 6 verschillende waarden | geen |  |  |  | Solar PV; Batteries; EVs |
| `Amount (USD)` | getal | nog te beschrijven |  | 0 tot 12.336.521.672 | geen |  |  |  | mediaan 295.254 |
| `Amount 12 month rolling sum (USD)` | getal | nog te beschrijven |  | 0 tot 105.888.452.450 | 13% leeg |  |  |  | mediaan 5.976.021 |

## fact_ember_doelen

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 2.229.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `COUNTRY_CODE` | tekst | nog te beschrijven |  | 89 verschillende waarden | geen |  |  |  | PHL; PAK; CAN |
| `TARGET_YEAR` | getal | nog te beschrijven |  | 2.022 tot 2.050 | geen |  |  |  | mediaan 2.030 |
| `FUEL_CATEGORY` | tekst | nog te beschrijven |  | 25 verschillende waarden | geen |  |  |  | Solar; Hydro; Wind |
| `METRIC` | tekst | nog te beschrijven |  | 7 verschillende waarden | geen |  |  |  | capacity_total_gw; generation_twh; share_of_generation_pct |
| `VALUE` | getal | nog te beschrijven |  | 0 tot 31.316 | 5% leeg |  |  |  | mediaan 5,62 |
| `SOURCE_ID` | getal | nog te beschrijven |  | 1 tot 245 | geen |  |  |  | mediaan 128 |
| `NUMBER_OF_UPDATES` | getal | nog te beschrijven |  | 1 tot 4 | geen |  |  |  | mediaan 1 |
| `COLLECTION_YEAR` | getal | nog te beschrijven |  | 2.023 tot 2.026 | geen |  |  |  | mediaan 2.023 |

## fact_ember_elektrificatie

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 127.160.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `YEAR` | getal | nog te beschrijven |  | 2.000 tot 2.025 | geen |  |  |  | mediaan 2.012 |
| `COUNTRY_CODE` | tekst | nog te beschrijven |  | 29 verschillende waarden | 3% leeg |  |  |  | AUT; LVA; SWE |
| `COUNTRY_OR_REGION` | tekst | nog te beschrijven |  | 30 verschillende waarden | geen |  |  |  | Austria; Belgium; Sweden |
| `SECTOR_NAME` | tekst | nog te beschrijven |  | 21 verschillende waarden | geen |  |  |  | All sectors; Industry; Other sectors |
| `PARENT_SECTOR_NAME` | tekst | nog te beschrijven |  | 5 verschillende waarden | 5% leeg |  |  |  | Industry; All sectors; Transport |
| `FUEL` | tekst | nog te beschrijven |  | 8 verschillende waarden | geen |  |  |  | Coal; Electricity; Gas |
| `CONSUMPTION_TWH` | getal | nog te beschrijven |  | 0 tot 4.754 | geen |  |  |  | mediaan 0,19 |
| `SHARE_OF_CONSUMPTION_PCT` | getal | nog te beschrijven |  | 0 tot 100 | geen |  |  |  | mediaan 2,54 |

## fact_ember_ev_verkoop

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 46.411.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 59 verschillende waarden | geen |  | ISO 3 code |  | Switzerland; Sweden; Ireland |
| `ISO 3 code` (ook: iso3) | tekst | Landcode volgens ISO 3166; leeg voor regio's. |  | 57 verschillende waarden | 2% leeg |  | Area |  | CHE; SWE; IRL |
| `Date` | tekst | nog te beschrijven |  | 262 verschillende waarden | geen |  |  |  | 2024-09-01; 2024-11-01; 2024-02-01 |
| `Drivetrain` | tekst | nog te beschrijven |  | 10 verschillende waarden | geen |  |  |  | Battery electric; Electric vehicle (BEV+PHEV); All drivetrains |
| `Registrations` | getal | nog te beschrijven |  | 0 tot 8.630.681 | geen |  |  |  | mediaan 2.466 |
| `Share of registrations (%)` | getal | nog te beschrijven |  | 0 tot 100 | enkele leeg |  |  |  | mediaan 9,9 |

## fact_ember_ev_vloot

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 61.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 61 verschillende waarden | geen |  | ISO 3 code |  | Albania; Lithuania; Malaysia |
| `ISO 3 code` (ook: iso3) | tekst | Landcode volgens ISO 3166; leeg voor regio's. |  | 59 verschillende waarden | 3% leeg |  | Area |  | ALB; SVK; MYS |
| `Area type` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | Country or economy; Region |
| `Latest available date` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | 2026-09-01; 2026-10-01; 2026-06-01 |
| `EV fleet (vehicles)` | getal | nog te beschrijven |  | 5.411 tot 90.583.358 | geen |  |  |  | mediaan 257.898 |
| `EV fleet electricity demand (GWh per year)` | getal | nog te beschrijven |  | 11,9 tot 235.627 | geen |  |  |  | mediaan 774 |
| `Oil displaced (thousand barrels of oil equivalent per year)` | getal | nog te beschrijven |  | 24,1 tot 525.173 | geen |  |  |  | mediaan 1.262 |
| `Value of oil displaced (USD million per year)` | getal | nog te beschrijven |  | 2,4 tot 52.996 | geen |  |  |  | mediaan 127 |
| `Brent price 6-month average (USD/bbl)` | getal | nog te beschrijven |  | 101 tot 101 | geen |  |  |  | mediaan 101 |

## fact_ember_india_staat

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 17.214.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `State` | tekst | nog te beschrijven |  | 38 verschillende waarden | geen |  |  |  | Andaman and Nicobar; Andhra Pradesh; Maharashtra |
| `State type` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | state; Union territory; total |
| `Year` (ook: jaar) | getal | Kalenderjaar. | jaar | 2.019 tot 2.024 | geen |  |  |  | mediaan 2.021 |
| `Category` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | Power sector emissions; Electricity generation; Capacity |
| `Subcategory` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | Fuel; Aggregate fuel; Total |
| `Variable` | tekst | nog te beschrijven |  | 18 verschillende waarden | geen |  |  |  | Clean; Bioenergy; Wind |
| `Unit` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | %; GWh; ktCO2 |
| `Value` | getal | nog te beschrijven |  | 0 tot 1.804.424 | 1% leeg |  |  |  | mediaan 5,87 |

## fact_ember_opwek

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 54.651.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 224 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Israel; Nigeria; Latvia |
| `iso3` (ook: ISO 3 code) | tekst | Landcode volgens ISO 3166 (drie letters). |  | 209 verschillende waarden | 6% leeg | koppelt aan Ember | land |  | LVA; GEO; CRI |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.000 tot 2.025 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.012 |
| `bron` | tekst | nog te beschrijven |  | 10 verschillende waarden | geen |  |  |  | Other fossil; Solar; Bioenergy |
| `twh` | getal | Opwek in het jaar. | TWh | -93,8 tot 10.652 | geen |  | aandeel_opwek |  | mediaan 0 |
| `aandeel_pct` | getal | nog te beschrijven |  | -88,5 tot 7.533 | enkele leeg |  |  |  | mediaan 0 |

## fact_ember_opwek_jaar

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 85.398.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 224 verschillende waarden | geen |  | ISO 3 code |  | United Kingdom; Germany; China |
| `ISO 3 code` (ook: iso3) | tekst | Landcode volgens ISO 3166; leeg voor regio's. |  | 209 verschillende waarden | 6% leeg |  | Area |  | GBR; DEU; IND |
| `Year` (ook: jaar) | getal | Kalenderjaar. | jaar | 1.985 tot 2.025 | geen |  |  |  | mediaan 2.011 |
| `Area type` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | Country or economy; Region |
| `Electricity source` | tekst | Opwekbron of saldo (Solar, Wind, Gas, Demand, Net imports). |  | 14 verschillende waarden | geen |  |  |  | Fossil; Total generation; Demand |
| `Generation (TWh)` | getal | Opwek in het jaar. | TWh | -93,8 tot 31.925 | geen |  |  |  | mediaan 0,32 |
| `Share of generation (%)` | getal | Aandeel in de totale opwek. | procent | -88,5 tot 7.633 | enkele leeg | 0 tot 100 |  | Bij de rijen Demand en Net imports is dit een verhouding tot de opwek: onder 0 en boven 100 komt voor. | mediaan 3,32 |
| `Capacity (GW)` | getal | Opgesteld vermogen. | GW | 0 tot 10.195 | 31% leeg | voor een deel van de landen en jaren leeg |  |  | mediaan 0,13 |
| `Emissions (MtCO2e)` | getal | Uitstoot van de elektriciteitsopwek. | megaton CO2-equivalent | 0 tot 14.698 | 7% leeg |  |  |  | mediaan 0,012 |

## fact_ember_opwek_maand

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 31.337.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 32 verschillende waarden | geen |  | ISO 3 code |  | Australia; United States; Canada |
| `ISO 3 code` (ook: iso3) | tekst | Landcode volgens ISO 3166; leeg voor regio's. |  | 32 verschillende waarden | geen |  | Area |  | AUS; USA; CAN |
| `Date` | tekst | nog te beschrijven |  | 335 verschillende waarden | geen |  |  |  | 2025-05-01; 2024-08-01; 2025-06-01 |
| `Electricity source` | tekst | Opwekbron of saldo (Solar, Wind, Gas, Demand, Net imports). |  | 7 verschillende waarden | geen |  |  |  | Clean; Total generation; Fossil |
| `Generation (TWh)` | getal | Opwek in het jaar. | TWh | 0 tot 1.026 | geen |  |  |  | mediaan 3,19 |
| `Share of generation (%)` | getal | Aandeel in de totale opwek. | procent | 0 tot 100 | geen | 0 tot 100 |  |  | mediaan 26 |

## fact_ember_prijs_dag

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 123.425.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 34 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Germany; Luxembourg; Austria |
| `iso3` (ook: ISO 3 code) | tekst | Landcode volgens ISO 3166 (drie letters). |  | 34 verschillende waarden | geen | koppelt aan Ember | land |  | DEU; LUX; AUT |
| `datum` | tekst | nog te beschrijven |  | 4338 verschillende waarden | geen |  |  |  | 2026-10-25; 2026-11-08; 2026-11-02 |
| `prijs` | getal | nog te beschrijven |  | -202 tot 888 | enkele leeg |  |  |  | mediaan 56,2 |

## fact_ember_prijs_maand

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 4.077.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 34 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Austria; Lithuania; Sweden |
| `iso3` (ook: ISO 3 code) | tekst | Landcode volgens ISO 3166 (drie letters). |  | 34 verschillende waarden | geen | koppelt aan Ember | land |  | AUT; LTU; SWE |
| `datum` | tekst | nog te beschrijven |  | 143 verschillende waarden | geen |  |  |  | 2026-11-01; 2026-10-01; 2026-09-01 |
| `prijs` | getal | nog te beschrijven |  | 1,85 tot 544 | enkele leeg |  |  |  | mediaan 58,4 |

## fact_ember_vs_staat

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 8.119.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 1 verschillende waarden | geen |  | ISO 3 code |  | United States |
| `State` | tekst | nog te beschrijven |  | 53 verschillende waarden | geen |  |  |  | California; US (total); Colorado |
| `Year` (ook: jaar) | getal | Kalenderjaar. | jaar | 2.001 tot 2.025 | geen |  |  |  | mediaan 2.014 |
| `Electricity source` | tekst | Opwekbron of saldo (Solar, Wind, Gas, Demand, Net imports). |  | 7 verschillende waarden | geen |  |  |  | Fossil; Total generation; Clean |
| `Generation (TWh)` | getal | Opwek in het jaar. | TWh | -0,019 tot 4.520 | geen |  |  |  | mediaan 16,8 |
| `Share of generation (%)` | getal | Aandeel in de totale opwek. | procent | -0,121 tot 100 | enkele leeg | 0 tot 100 |  |  | mediaan 36,5 |
| `Emissions (MtCO2e)` | getal | Uitstoot van de elektriciteitsopwek. | megaton CO2-equivalent | -0,018 tot 2.479 | geen |  |  |  | mediaan 3,48 |

## fact_ember_zon_import

Een rij is (nog te beschrijven). Bron: Ember (CC BY 4.0). Rijen: 31.624.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `Area` | tekst | Land of regio volgens Ember. |  | 244 verschillende waarden | geen |  | ISO 3 code |  | World; G20; South Korea |
| `Date` | tekst | nog te beschrijven |  | 117 verschillende waarden | geen |  |  |  | 2025-12-01; 2025-07-01; 2025-11-01 |
| `Region` | tekst | nog te beschrijven |  | 7 verschillende waarden | 9% leeg |  |  |  | Africa; Europe; Asia |
| `Commodity type` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | Panels; Cells; Wafers |
| `Amount (USD)` | getal | nog te beschrijven |  | 0 tot 4.816.624.349 | geen |  |  |  | mediaan 486.227 |
| `Commodity price` | getal | nog te beschrijven |  | 0,03 tot 1,3 | geen |  |  |  | mediaan 0,18 |
| `Capacity (MW)` | getal | nog te beschrijven |  | 0 tot 32.253 | geen |  |  |  | mediaan 3,04 |

## fact_erosie

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 4.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `erosie` | getal | nog te beschrijven |  | 0 tot 0,03 | geen |  |  |  | mediaan 0,015 |
| `irr` (ook: IRR) | getal | Intern rendement van het project. | fractie per jaar | 0,0266 tot 0,072 | geen | leeg als de investering nooit terugkomt |  |  | mediaan 0,0506 |
| `irr_na_belasting` | getal | nog te beschrijven |  | 0,0167 tot 0,0554 | geen |  |  |  | mediaan 0,0375 |

## fact_fcr_nl

Een rij is een blok van vier uur: prijs van primaire reserve (FCR). Bron: ENTSO-E (document A84). Rijen: 8.255.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `vanaf_utc` | tekst | nog te beschrijven |  | 8255 verschillende waarden | geen |  |  |  | 2023-01-01 00:00:00; 2025-08-10 10:00:00; 2025-08-04 10:00:00 |
| `prijs_eur_mw_uur` | getal | Prijs van FCR-vermogen per MW per uur, per blok van vier uur. | euro per MW per uur | 2,78 tot 19.444 | geen |  |  |  | mediaan 13,8 |

## fact_flex_land

Een rij is een land in een jaar voor een batterij van 1, 2 of 4 uur. Bron: eigen berekening op Energy-Charts-prijzen. Rijen: 888.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 37 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Nederland; Slovenie; Letland |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `uren_opslag` | getal | Duur van de batterij: uren ontladen op vol vermogen. | uur | 1 tot 4 | geen | 1, 2 of 4 | omzet_realistisch_per_mw |  | mediaan 2 |
| `omzet_perfect_per_mw` | getal | Dagmarktomzet van de batterij met kennis vooraf van alle prijzen (bovengrens). | euro per MW per jaar | 580 tot 204.505 | geen | een cyclus per dag | omzet_realistisch_per_mw |  | mediaan 36.653 |
| `omzet_realistisch_per_mw` (ook: batterij_per_mw) | getal | Dagmarktomzet van de batterij met een plan op de prijzen van gisteren. | euro per MW per jaar | 294 tot 182.595 | geen | verliesdagen overgeslagen; zonder netkosten en balancering | voorspel_ratio, dagspreiding |  | mediaan 27.262 |
| `voorspel_ratio` | getal | Realistische omzet gedeeld door de omzet met kennis vooraf. | verhouding | 0,351 tot 0,959 | geen | 0 tot 1 | omzet_perfect_per_mw |  | mediaan 0,749 |
| `irr_realistisch` | getal | IRR van de batterij bij de realistische dagmarktomzet. | fractie per jaar | -0,321 tot 0,103 | 34% leeg | leeg als de investering nooit terugkomt; leeg is dus slechter dan negatief | omzet_realistisch_per_mw | 34% leeg: dat zijn de zone-jaren met de laagste omzet, geen ontbrekende metingen. | mediaan -0,053 |

## fact_gas_henryhub

Een rij is een dag: gasprijs Henry Hub. Bron: EIA. Rijen: 4.259.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `datum` | tekst | nog te beschrijven |  | 4259 verschillende waarden | geen |  |  |  | 2026-11-11; 2015-08-11; 2015-08-31 |
| `usd_mmbtu` | getal | nog te beschrijven |  | 1,21 tot 30,7 | enkele leeg |  |  |  | mediaan 3 |

## fact_gasprijs_maand

Een rij is een maand: de Europese gasprijs in dollar per MMBtu en in euro per MWh. Bron: IMF en Federal Reserve via FRED. Rijen: 107.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `periode` | tekst | nog te beschrijven |  | 107 verschillende waarden | geen |  |  |  | 2018-01; 2024-09; 2024-07 |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.018 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6 |
| `eu_gas_usd_mmbtu` | getal | nog te beschrijven |  | 1,46 tot 70 | 2% leeg |  |  |  | mediaan 10,4 |
| `usd_per_eur` | getal | nog te beschrijven |  | 0,985 tot 1,23 | 1% leeg |  |  |  | mediaan 1,13 |
| `eu_gas_eur_mwh` | getal | nog te beschrijven |  | 4,58 tot 236 | geen |  |  |  | mediaan 32,2 |
| `voorlopig` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | False; True |
| `bron` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | FRED (IMF PNGASEUUSDM; Fed EXUSEU); IMF-reeks oktober 2026 (28,98 dollar per MMBtu, via cbonds), koers 1,1198; gemiddelde van de dagprijzen tot half november, indicatie |

## fact_grensstromen_nl

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 566.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6 |
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 6 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Belgium; Germany; Norway |
| `netto_import_twh` | getal | nog te beschrijven |  | -2,25 tot 1,05 | geen |  |  |  | mediaan -0,0487 |

## fact_herijking

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 24.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.023 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `methode` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | Opwekdata Energy-Charts; Instralingsprofiel, niet afschakelen; Instralingsprofiel, afschakelen bij negatieve prijs |
| `vollasturen` | getal | Vollasturen van zon per jaar. | uur per jaar | 740 tot 950 | geen |  | capex_eur_kw |  | mediaan 845 |
| `capture_rate` | getal | Capture rate van de genoemde techniek of brandstof. | verhouding | 0,524 tot 0,756 | geen | tussen 0 en 2 | capture_price |  | mediaan 0,595 |
| `capture_prijs` | getal | nog te beschrijven |  | 43,4 tot 72,5 | geen |  |  |  | mediaan 60,1 |
| `irr_voor_belasting` | getal | nog te beschrijven |  | -0,016 tot 0,103 | geen |  |  |  | mediaan 0,0498 |

## fact_importpotentieel

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 368.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 46 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Albania; Portugal; Malta |
| `peiljaar` | getal | nog te beschrijven |  | 2.030 tot 2.040 | geen |  |  |  | mediaan 2.035 |
| `scenario` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | Huidig (2024); Reference; Projects |
| `waarde` | getal | nog te beschrijven |  | 0 tot 925 | geen |  |  |  | mediaan 59 |

## fact_instraling_wereld

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 264.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `locatie` | tekst | nog te beschrijven |  | 24 verschillende waarden | geen |  |  |  | Australie (Zuid); Brazilie; Zuid-Afrika |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.015 tot 2.025 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.020 |
| `ghi_kwh_m2` | getal | nog te beschrijven |  | 992 tot 2.392 | geen |  |  |  | mediaan 1.881 |
| `vollasturen_schatting` | getal | nog te beschrijven |  | 793 tot 1.913 | geen |  |  |  | mediaan 1.505 |

## fact_jcurve

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 11.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 0 tot 10 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 5 |
| `cumulatief_lp` | getal | nog te beschrijven |  | -112 tot 31,8 | geen |  |  |  | mediaan -54 |

## fact_kernenergie_land_jaar

Een rij is een biedzone met kernenergie in een jaar. Bron: Energy-Charts; eigen berekening (eti.kernenergie). Rijen: 113.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 14 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Nederland; Belgie; Bulgarije |
| `biedzone` (ook: zone, bidding zone) | tekst | Code van de biedzone (NL, DE-LU, IT-North, NO1). |  | 14 verschillende waarden | geen | 37 zones | land |  | NL; BE; BG |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.015 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `uren` | getal | Aantal uren met een prijs in de periode. | uren | 2.518 tot 8.784 | geen | 8.760 of 8.784 in een heel jaar | jaar |  | mediaan 8.760 |
| `kern_twh` | getal | Opwek uit kernenergie in het jaar. | TWh | 2,81 tot 378 | geen |  | aandeel_kern |  | mediaan 19,3 |
| `aandeel_kern` | getal | Aandeel van kernenergie in de opwek. | fractie | 0,0269 tot 0,717 | geen | 0 tot 1 |  |  | mediaan 0,367 |
| `gem_prijs` (ook: basislastprijs, baseload) | getal | Gemiddelde dagmarktprijs over alle uren van de periode. | euro per MWh | 21,2 tot 282 | geen | ongewogen over de uren | mediaan_prijs, capture_zon |  | mediaan 95,8 |
| `capture_price_kern` | getal | nog te beschrijven |  | 20,5 tot 283 | geen |  |  |  | mediaan 95,4 |
| `capture_kern` | getal | Capture rate van kernenergie. | verhouding | 0,837 tot 1,08 | geen |  |  |  | mediaan 1,01 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 0 tot 761 | geen | 0 tot 8.784 | uren |  | mediaan 76 |
| `aandeel_in_negatieve_uren` | getal | Deel van de opwek van deze bron dat in uren met een negatieve prijs valt. | fractie | 0 tot 0,0936 | geen | 0 tot 1 | negatieve_uren |  | mediaan 0,00848 |
| `productie_bij_negatieve_prijs` | getal | nog te beschrijven |  | 0,82 tot 1,05 | 19% leeg |  |  |  | mediaan 0,99 |
| `dagen_met_negatieve_prijs` | getal | nog te beschrijven |  | 0 tot 119 | geen |  |  |  | mediaan 20 |
| `daguitslag_mediaan` | getal | nog te beschrijven |  | 0,00173 tot 0,133 | geen |  |  |  | mediaan 0,00649 |
| `benutting_tov_top` | getal | nog te beschrijven |  | 0,201 tot 0,977 | geen |  |  |  | mediaan 0,814 |
| `benutting_tov_vermogen` | getal | nog te beschrijven |  | 0,517 tot 1,25 | 24% leeg |  |  | Onbetrouwbaar voor Belgie (boven 1). | mediaan 0,879 |
| `capture_zon` (ook: marktwaardefactor, value factor) | getal | Capture rate van zon: de prijs die zon ontvangt (gewogen naar opwek) gedeeld door de gemiddelde prijs. | verhouding | 0,511 tot 1,23 | 4% leeg | tussen 0 en 2; boven 2 is een rekenfout | capture_bron, gem_prijs |  | mediaan 0,821 |
| `capture_wind` | getal | Capture rate van wind, zelfde definitie als voor zon. | verhouding | 0,551 tot 1,11 | 4% leeg | tussen 0 en 2 | aandeel_wind |  | mediaan 0,932 |

## fact_kernenergie_verband

Een rij is een rangcorrelatie tussen het kernaandeel en een marktmaat. Bron: eigen berekening. Rijen: 4.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `verband` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | aandeel kernenergie en dagspreiding; aandeel kernenergie en batterij-omzet 2 uur; aandeel kernenergie en capture rate zon |
| `alle_landjaren` | getal | nog te beschrijven |  | -0,0634 tot 0,213 | geen |  |  |  | mediaan 0,0107 |
| `binnen_jaren` | getal | nog te beschrijven |  | -0,192 tot 0,299 | geen |  |  |  | mediaan 0,0171 |
| `landjaren` | getal | nog te beschrijven |  | 182 tot 182 | geen |  |  |  | mediaan 182 |
| `landen` | getal | nog te beschrijven |  | 26 tot 26 | geen |  |  |  | mediaan 26 |

## fact_klimaatscenario

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 4.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `scenario` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | Basis; Orderly; Fysiek |
| `npv_eur` | getal | nog te beschrijven |  | -2.661.394 tot 155.870 | geen |  |  |  | mediaan -830.276 |
| `irr` (ook: IRR) | getal | Intern rendement van het project. | fractie per jaar | 0,037 tot 0,072 | geen | leeg als de investering nooit terugkomt |  |  | mediaan 0,0591 |

## fact_kpi

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 15.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `project` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | Zon; Batterij; Impact |
| `kpi` | tekst | nog te beschrijven |  | 14 verschillende waarden | geen |  |  |  | IRR; IRR voor belasting; IRR na belasting |
| `waarde` | getal | nog te beschrijven |  | -0,0392 tot 473.292 | geen |  |  |  | mediaan 0,789 |

## fact_kwartier_batterij

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 38.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 19 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Nederland; Oostenrijk; Roemenie |
| `dagen` | getal | nog te beschrijven |  | 384 tot 391 | geen |  |  |  | mediaan 384 |
| `uren_opslag` | getal | Duur van de batterij: uren ontladen op vol vermogen. | uur | 1 tot 2 | geen | 1, 2 of 4 | omzet_realistisch_per_mw |  | mediaan 1,5 |
| `omzet_uur_per_mw` | getal | nog te beschrijven |  | 18.665 tot 100.280 | geen |  |  |  | mediaan 48.225 |
| `omzet_kwartier_per_mw` | getal | nog te beschrijven |  | 19.574 tot 104.951 | geen |  |  |  | mediaan 50.912 |
| `uplift` | getal | nog te beschrijven |  | 0,0148 tot 0,0804 | geen |  |  |  | mediaan 0,0488 |

## fact_land_jaar

Een rij is een biedzone in een jaar: prijs, marktwaarde van zon en wind, negatieve uren. Bron: Energy-Charts (prijs, opwek), Open-Meteo (instraling), Ember (aandelen). Rijen: 296.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 37 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Nederland; Slovenie; Letland |
| `biedzone` (ook: zone, bidding zone) | tekst | Code van de biedzone (NL, DE-LU, IT-North, NO1). |  | 37 verschillende waarden | geen | 37 zones | land |  | NL; SI; LV |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `gem_prijs` (ook: basislastprijs, baseload) | getal | Gemiddelde dagmarktprijs over alle uren van de periode. | euro per MWh | 8,72 tot 308 | geen | ongewogen over de uren | mediaan_prijs, capture_zon |  | mediaan 86,8 |
| `mediaan_prijs` | getal | Mediaan van de uurprijzen. | euro per MWh | 3,53 tot 267 | geen |  | gem_prijs |  | mediaan 78,9 |
| `capture_zon` (ook: marktwaardefactor, value factor) | getal | Capture rate van zon: de prijs die zon ontvangt (gewogen naar opwek) gedeeld door de gemiddelde prijs. | verhouding | 0,474 tot 1,23 | geen | tussen 0 en 2; boven 2 is een rekenfout | capture_bron, gem_prijs | SE3 en SE4 in 2021 geven 3,51 en 2,97 door een vrijwel lege opwekreeks; 51 van de 296 rijen komen uit instraling. | mediaan 0,847 |
| `capture_wind` | getal | Capture rate van wind, zelfde definitie als voor zon. | verhouding | 0,551 tot 1,12 | 1% leeg | tussen 0 en 2 | aandeel_wind |  | mediaan 0,935 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 0 tot 725 | geen | 0 tot 8.784 | uren |  | mediaan 35,5 |
| `uren_boven_200` | getal | Aantal uren met een prijs boven 200 euro per MWh. | uren | 0 tot 7.097 | geen |  | gem_prijs |  | mediaan 135 |
| `dagspreiding` (ook: daily spread) | getal | Gemiddeld verschil tussen de hoogste en laagste uurprijs van een dag. | euro per MWh | 3,14 tot 251 | geen | niet negatief | omzet_realistisch_per_mw |  | mediaan 79,5 |
| `aandeel_zon` | getal | Aandeel van zon in de opwek volgens ENTSO-E. | fractie | 0 tot 0,271 | 12% leeg | 0 tot 1; onderschat zon achter de meter | aandeel_zon_energycharts | Onderschat zon achter de meter; gebruik het aandeel van Ember. | mediaan 0,0411 |
| `aandeel_wind` | getal | Aandeel van wind in de opwek volgens ENTSO-E. | fractie | 0 tot 0,584 | 12% leeg | 0 tot 1 | capture_wind |  | mediaan 0,101 |
| `uren` | getal | Aantal uren met een prijs in de periode. | uren | 7.375 tot 8.784 | geen | 8.760 of 8.784 in een heel jaar | jaar |  | mediaan 8.760 |
| `iso3` (ook: ISO 3 code) | tekst | Landcode volgens ISO 3166 (drie letters). |  | 26 verschillende waarden | geen | koppelt aan Ember | land |  | NOR; ITA; SWE |
| `aandeel_zon_energycharts` | getal | Aandeel van zon in de opwek volgens Energy-Charts. | fractie | 0 tot 0,31 | geen | 0 tot 1 | aandeel_zon |  | mediaan 0,0364 |
| `aandeel_wind_energycharts` | getal | Aandeel van wind in de opwek volgens Energy-Charts. | fractie | 0 tot 0,598 | geen | 0 tot 1 | aandeel_wind |  | mediaan 0,192 |
| `capture_bron` | tekst | Waar het opwekprofiel vandaan komt: gemeten opwek of een schatting uit instraling. |  | 2 verschillende waarden | geen | instraling is een benadering; apart houden van gemeten zones | capture_zon |  | opwek (Energy-Charts); instraling (Open-Meteo, proxy) |
| `zon_dekking` | getal | nog te beschrijven |  | 0,083 tot 1 | 17% leeg |  |  |  | mediaan 1 |
| `capture_zon_gemeten` | getal | nog te beschrijven |  | 0,566 tot 3,51 | 97% leeg |  |  |  | mediaan 0,888 |

## fact_land_maand

Een rij is een biedzone in een maand. Bron: Energy-Charts, Open-Meteo. Rijen: 3.515.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 37 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Nederland; Slovenie; Letland |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6 |
| `gem_prijs` (ook: basislastprijs, baseload) | getal | Gemiddelde dagmarktprijs over alle uren van de periode. | euro per MWh | 0,94 tot 548 | geen | ongewogen over de uren | mediaan_prijs, capture_zon |  | mediaan 74,2 |
| `capture_zon` (ook: marktwaardefactor, value factor) | getal | Capture rate van zon: de prijs die zon ontvangt (gewogen naar opwek) gedeeld door de gemiddelde prijs. | verhouding | 0,103 tot 1,81 | 2enkele leeg | tussen 0 en 2; boven 2 is een rekenfout | capture_bron, gem_prijs |  | mediaan 0,935 |
| `capture_wind` | getal | Capture rate van wind, zelfde definitie als voor zon. | verhouding | 0,319 tot 1,27 | 1% leeg | tussen 0 en 2 | aandeel_wind |  | mediaan 0,938 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 0 tot 239 | geen | 0 tot 8.784 | uren |  | mediaan 0 |
| `dagspreiding` (ook: daily spread) | getal | Gemiddeld verschil tussen de hoogste en laagste uurprijs van een dag. | euro per MWh | 0,364 tot 573 | geen | niet negatief | omzet_realistisch_per_mw |  | mediaan 68 |

## fact_land_profiel_maand

Een rij is (nog te beschrijven). Bron: Energy-Charts. Rijen: 1.564.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 46 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Austria; Serbia; Belgium |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.024 tot 2.040 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.030 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6 |
| `res_e` | getal | nog te beschrijven |  | 0 tot 85,1 | geen |  |  |  | mediaan 30,5 |
| `net_p` | getal | nog te beschrijven |  | -90 tot 122 | geen |  |  |  | mediaan -2,24 |

## fact_land_profiel_uur

Een rij is (nog te beschrijven). Bron: Energy-Charts. Rijen: 2.760.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 45 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Austria; Italy; Sweden |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.024 tot 2.040 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.030 |
| `uur` | getal | Uur van de dag in UTC, 0 tot 23. | uur | 0 tot 23 | geen | 0 tot 23; lokale tijd is UTC+1 of +2 | timestamp_utc |  | mediaan 11,5 |
| `uur_bron` | getal | Uur zoals de bron het telt, 1 tot 24 (het uur dat eindigt). De kolom uur is hieruit afgeleid: uur = uur_bron - 1. | uur | 1 tot 24 | geen | 1 tot 24 | bronbestand |  | mediaan 12,5 |
| `res_e` | getal | nog te beschrijven |  | 0 tot 92,9 | geen |  |  |  | mediaan 35 |
| `net_p` | getal | nog te beschrijven |  | -97,3 tot 142 | geen |  |  |  | mediaan -2,99 |

## fact_maand_uur

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 288.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6,5 |
| `uur` | getal | Uur van de dag in UTC, 0 tot 23. | uur | 0 tot 23 | geen | 0 tot 23; lokale tijd is UTC+1 of +2 | timestamp_utc |  | mediaan 11,5 |
| `gem_prijs` (ook: basislastprijs, baseload) | getal | Gemiddelde dagmarktprijs over alle uren van de periode. | euro per MWh | 35,1 tot 131 | geen | ongewogen over de uren | mediaan_prijs, capture_zon |  | mediaan 98,8 |
| `zon_mw` | getal | nog te beschrijven |  | 0 tot 6.590 | geen |  |  |  | mediaan 422 |

## fact_markt_uur

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 8.770.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `timestamp_utc` (ook: tijdstip) | tekst | Begin van het uur of kwartier, in UTC. | tijdstip | 8770 verschillende waarden | geen | uniek per tabel; geen zomertijd | jaar, maand, uur |  | 2024-01-01T00:00Z; 2024-09-01T03:00Z; 2024-08-31T21:00Z |
| `datum` | tekst | nog te beschrijven |  | 366 verschillende waarden | geen |  |  |  | 2024-01-01; 2024-08-14; 2024-09-05 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 7 |
| `uur` | getal | Uur van de dag in UTC, 0 tot 23. | uur | 0 tot 23 | geen | 0 tot 23; lokale tijd is UTC+1 of +2 | timestamp_utc |  | mediaan 11,5 |
| `prijs_eur_mwh` (ook: day-ahead prijs) | getal | Dagmarktprijs van het uur. | euro per MWh | -40 tot 198 | geen | tussen -500 en 5.000 (marktgrenzen) | solar_mw |  | mediaan 100 |
| `zon_nl_mw` | getal | nog te beschrijven |  | 0 tot 8.939 | geen |  |  |  | mediaan 368 |
| `netfactor_kg_mwh` | getal | nog te beschrijven |  | 35,7 tot 435 | geen |  |  |  | mediaan 265 |

## fact_nl_jaar

Een rij is een jaar in Nederland: kengetallen van het modelpark van 10 MW. Bron: eigen model. Rijen: 8.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `capture_rate` | getal | Capture rate van de genoemde techniek of brandstof. | verhouding | 0,587 tot 0,942 | geen | tussen 0 en 2 | capture_price |  | mediaan 0,754 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 3 tot 584 | geen | 0 tot 8.784 | uren |  | mediaan 209 |
| `irr_zon` | getal | IRR van het zonnepark van 10 MW voor belasting, bij de marktwaarde van dat jaar. | fractie per jaar | -0,141 tot 0,328 | geen |  | capture_rate, lcoe |  | mediaan 0,0365 |
| `irr_zon_na_belasting` | getal | IRR van het zonnepark na vennootschapsbelasting. | fractie per jaar | -0,141 tot 0,252 | geen |  | irr_zon |  | mediaan 0,0278 |
| `lcoe` | getal | Kosten per MWh over de levensduur (levelized cost of energy). | euro per MWh | 76,5 tot 76,5 | geen |  | capture_price |  | mediaan 76,5 |
| `capture_price` (ook: capture-prijs) | getal | Prijs die de techniek gemiddeld ontvangt (gewogen naar opwek). | euro per MWh | 25,4 tot 224 | geen | capture_rate maal gem_prijs | gem_prijs |  | mediaan 62,2 |
| `batterij_omzet_perfect` | getal | Dagmarktomzet van de batterij van 10 MW met kennis vooraf. | euro per jaar | 126.988 tot 1.057.506 | geen | delen door 10 voor per MW | batterij_omzet_realistisch |  | mediaan 606.722 |
| `batterij_omzet_realistisch` | getal | Dagmarktomzet van de batterij van 10 MW met een plan op gisteren. | euro per jaar | 87.072 tot 824.424 | geen | delen door 10 voor per MW | irr_batterij |  | mediaan 500.151 |
| `irr_batterij` | getal | IRR van de batterij op dagmarkthandel. | fractie per jaar | -0,296 tot 0,111 | 12% leeg | leeg als de investering nooit terugkomt |  |  | mediaan 0,0101 |
| `co2_vermeden_uur` | getal | Vermeden CO2 van het zonnepark, berekend per uur met de opwekmix van dat uur. | ton per jaar | 3.616 tot 5.988 | geen | de voorkeursmethode | co2_vermeden_jaargem |  | mediaan 4.883 |
| `co2_vermeden_jaargem` | getal | Vermeden CO2 berekend met de gemiddelde netintensiteit van het jaar. | ton per jaar | 4.122 tot 6.116 | geen | overschat sinds 2023 | co2_vermeden_uur |  | mediaan 5.129 |

## fact_nl_uur_alle_jaren

Een rij is een uur in Nederland: dagmarktprijs en opwek per bron. Bron: Energy-Charts (ENTSO-E). Rijen: 69.010.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `timestamp_utc` (ook: tijdstip) | tekst | Begin van het uur of kwartier, in UTC. | tijdstip | 69010 verschillende waarden | geen | uniek per tabel; geen zomertijd | jaar, maand, uur |  | 2019-01-01 00:00; 2024-04-01 04:00; 2024-03-31 14:00 |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6 |
| `uur` | getal | Uur van de dag in UTC, 0 tot 23. | uur | 0 tot 23 | geen | 0 tot 23; lokale tijd is UTC+1 of +2 | timestamp_utc |  | mediaan 11 |
| `prijs_eur_mwh` (ook: day-ahead prijs) | getal | Dagmarktprijs van het uur. | euro per MWh | -500 tot 873 | geen | tussen -500 en 5.000 (marktgrenzen) | solar_mw |  | mediaan 81 |
| `solar_mw` | getal | Gemeten zonopwek in het uur. | MW | 0 tot 428 | geen | alleen de vorm van het profiel gebruiken, niet het niveau | prijs_eur_mwh | Telt 1 tot 4% van de Nederlandse zonopwek, vooral grote parken (0,5 TWh tegen 28,5 TWh volgens Ember in 2025). De vorm volgt de instraling; de parken schakelen af bij negatieve prijzen, dus de capture rate is die van een park dat dat doet (fact_nl_zonprofiel_toets). | mediaan 1,2 |
| `wind_mw` | getal | Gemeten windopwek in het uur (land en zee). | MW | 0,1 tot 6.971 | geen |  |  | Telt op tot 22,7 TWh in 2025; Ember geeft 33,7 TWh. | mediaan 1.347 |
| `gas_mw` | getal | Opwek uit gas in het uur. | MW | 372 tot 11.244 | geen |  | coal_mw |  | mediaan 4.225 |
| `coal_mw` | getal | Opwek uit kolen in het uur. | MW | 0 tot 3.950 | geen |  | gas_mw |  | mediaan 1.557 |
| `nuclear_mw` | getal | Opwek uit kernenergie in het uur. | MW | 0 tot 492 | geen |  |  |  | mediaan 477 |
| `biomass_mw` | getal | Opwek uit biomassa in het uur. | MW | 0 tot 614 | geen |  |  |  | mediaan 15,9 |
| `waste_mw` | getal | Opwek uit afval in het uur. | MW | 30,5 tot 514 | geen |  |  |  | mediaan 336 |
| `other_renewable_mw` | getal | Overige hernieuwbare opwek. | MW | 0 tot 0 | geen | altijd nul: niet gebruiken |  | Altijd nul. | mediaan 0 |

## fact_nl_zonprofiel_toets

Een rij is een jaar: de Nederlandse zonreeks getoetst aan instraling en aan het jaartotaal van Ember. Bron: Energy-Charts, Open-Meteo, Ember; eigen berekening. Rijen: 8.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `uren` | getal | Aantal uren met een prijs in de periode. | uren | 7.642 tot 8.784 | geen | 8.760 of 8.784 in een heel jaar | jaar |  | mediaan 8.760 |
| `gemeten_twh` | getal | nog te beschrijven |  | 0,0673 tot 0,547 | geen |  |  |  | mediaan 0,475 |
| `ember_twh` | getal | nog te beschrijven |  | 5,4 tot 28,5 | 12% leeg |  |  |  | mediaan 16,7 |
| `ember_vermogen_gw` | getal | nog te beschrijven |  | 7,23 tot 25,9 | 12% leeg |  |  |  | mediaan 17,4 |
| `dekking` | getal | nog te beschrijven |  | 0,0125 tot 0,0361 | 12% leeg |  |  |  | mediaan 0,0247 |
| `schaal_naar_ember` | getal | nog te beschrijven |  | 27,7 tot 80,2 | 12% leeg |  |  |  | mediaan 40,5 |
| `capture_gemeten` | getal | nog te beschrijven |  | 0,587 tot 0,942 | geen |  |  |  | mediaan 0,754 |
| `capture_instraling` | getal | nog te beschrijven |  | 0,524 tot 0,949 | geen |  |  |  | mediaan 0,732 |
| `capture_instraling_stempel` | getal | nog te beschrijven |  | 0,56 tot 0,95 | geen |  |  |  | mediaan 0,742 |
| `correlatie_uur` | getal | nog te beschrijven |  | 0,855 tot 0,97 | geen |  |  |  | mediaan 0,941 |
| `correlatie_uur_stempel` | getal | nog te beschrijven |  | 0,817 tot 0,928 | geen |  |  |  | mediaan 0,904 |
| `correlatie_dag` | getal | nog te beschrijven |  | 0,824 tot 0,967 | geen |  |  |  | mediaan 0,933 |
| `negatieve_uren_met_zon` | getal | nog te beschrijven |  | 2 tot 469 | geen |  |  |  | mediaan 120 |
| `opbrengst_bij_negatieve_prijs` | getal | nog te beschrijven |  | 0,585 tot 1,01 | 12% leeg |  |  |  | mediaan 0,799 |
| `zomerhalfjaar_gemeten` | getal | nog te beschrijven |  | 0,732 tot 0,797 | geen |  |  |  | mediaan 0,77 |
| `zomerhalfjaar_instraling` | getal | nog te beschrijven |  | 0,764 tot 0,798 | geen |  |  |  | mediaan 0,787 |
| `verschil_capture` | getal | nog te beschrijven |  | -0,0072 tot 0,0916 | geen |  |  |  | mediaan 0,0247 |
| `fout_door_stempel` | getal | nog te beschrijven |  | 0,0015 tot 0,0366 | geen |  |  |  | mediaan 0,0139 |

## fact_ntc

Een rij is een grens tussen twee landen: handelscapaciteit. Bron: ENTSO-E TYNDP. Rijen: 851.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `scenario` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | Reference; Projects; Needs |
| `grens` | tekst | nog te beschrijven |  | 123 verschillende waarden | geen |  |  |  | AL-GR; IT-TN; IT-MT |
| `van` | tekst | nog te beschrijven |  | 39 verschillende waarden | geen |  |  |  | DE; AT; BE |
| `naar` | tekst | nog te beschrijven |  | 40 verschillende waarden | geen |  |  |  | UK; RS; SE |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.024 tot 2.040 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.030 |
| `ntc_heen_mw` | getal | Handelscapaciteit van het eerste naar het tweede land. | MW | 0 tot 11.600 | geen |  | ntc_terug_mw |  | mediaan 1.000 |
| `ntc_terug_mw` | getal | Handelscapaciteit in de andere richting. | MW | 0 tot 11.600 | geen |  | ntc_heen_mw |  | mediaan 1.000 |

## fact_onbalans_nl

Een rij is een kwartier in Nederland: onbalansprijzen. Bron: ENTSO-E (document A85). Rijen: 135.836.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `timestamp_utc` (ook: tijdstip) | tekst | Begin van het uur of kwartier, in UTC. | tijdstip | 135836 verschillende waarden | geen | uniek per tabel; geen zomertijd | jaar, maand, uur |  | 2023-01-01 00:00; 2025-08-01 06:00; 2025-08-01 09:30 |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.023 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6 |
| `prijs_tekort_eur_mwh` | getal | Onbalansprijs bij een tekort: wat laden zonder inkoop kost. | euro per MWh | -3.895 tot 5.500 | geen | kan sterk negatief of zeer hoog zijn | prijs_overschot_eur_mwh |  | mediaan 90 |
| `prijs_overschot_eur_mwh` | getal | Onbalansprijs bij een overschot: wat ontladen zonder verkoop oplevert. | euro per MWh | -3.985 tot 5.500 | geen |  | prijs_tekort_eur_mwh |  | mediaan 76,2 |

## fact_onbalans_regel

Een rij is een stuurregel voor de batterij in een jaar. Bron: eigen simulatie (eti.onbalansregel). Rijen: 300.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `regel` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | Dagmarktregel; Kwantielregel; Dagmarkt met bijsturen |
| `variant` | tekst | nog te beschrijven |  | 11 verschillende waarden | geen |  |  |  | 10/90; 25/75; 33/67 |
| `max_cycli_per_dag` | getal | nog te beschrijven |  | 0 tot 2 | geen |  |  |  | mediaan 1 |
| `vertraging_kwartieren` | getal | nog te beschrijven |  | 0 tot 2 | geen |  |  |  | mediaan 1 |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.023 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.024 |
| `omzet_per_mw` | getal | Omzet per MW per jaar van de genoemde strategie. | euro per MW per jaar | -515 tot 194.954 | geen |  |  |  | mediaan 58.274 |
| `cycli_per_dag` | getal | nog te beschrijven |  | 0,172 tot 2,95 | geen |  |  |  | mediaan 0,982 |
| `dagen` | getal | nog te beschrijven |  | 319 tot 366 | geen |  |  |  | mediaan 365 |
| `aandeel_dagen_met_verlies` | getal | nog te beschrijven |  | 0,0247 tot 0,589 | geen |  |  |  | mediaan 0,229 |
| `vooraf_gekozen` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | False; True |
| `aandeel_van_perfect` | getal | nog te beschrijven |  | -0,00232 tot 0,477 | 29% leeg |  |  |  | mediaan 0,185 |
| `dagmarkt_per_mw` | getal | nog te beschrijven |  | 47.323 tot 81.706 | geen |  |  |  | mediaan 56.799 |
| `waarvan_onbalans_per_mw` | getal | nog te beschrijven |  | -24.377 tot 147.631 | 88% leeg |  |  |  | mediaan 21.571 |

## fact_onzekerheid_land

Een rij is een land in een jaar: onzekerheidsband uit 10.000 trekkingen. Bron: eigen berekening (bootstrap). Rijen: 148.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 20 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Nederland; Duitsland; Roemenie |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.023 |
| `trekkingen` | getal | nog te beschrijven |  | 10.000 tot 10.000 | geen |  |  |  | mediaan 10.000 |
| `capture_p10` | getal | nog te beschrijven |  | 0,444 tot 2,39 | geen |  |  |  | mediaan 0,78 |
| `capture_p50` | getal | nog te beschrijven |  | 0,472 tot 3,51 | geen |  |  |  | mediaan 0,816 |
| `capture_p90` | getal | nog te beschrijven |  | 0,5 tot 4,35 | geen |  |  |  | mediaan 0,855 |
| `batterij_p10` | getal | nog te beschrijven |  | 3.724 tot 92.220 | geen |  |  |  | mediaan 32.732 |
| `batterij_p50` | getal | nog te beschrijven |  | 4.307 tot 101.308 | geen |  |  |  | mediaan 35.307 |
| `batterij_p90` | getal | nog te beschrijven |  | 4.926 tot 110.937 | geen |  |  |  | mediaan 38.556 |

## fact_owid_co2

Een rij is (nog te beschrijven). Bron: Our World in Data. Rijen: 5.798.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `country` | tekst | nog te beschrijven |  | 223 verschillende waarden | geen |  |  |  | Afghanistan; Palau; New Caledonia |
| `iso_code` | tekst | nog te beschrijven |  | 223 verschillende waarden | geen |  |  |  | AFG; PLW; NCL |
| `year` | getal | nog te beschrijven |  | 2.000 tot 2.025 | geen |  |  |  | mediaan 2.012 |
| `co2` | getal | nog te beschrijven |  | 0 tot 12.417 | 1% leeg |  |  |  | mediaan 7,49 |
| `co2_per_capita` | getal | nog te beschrijven |  | 0,022 tot 59,7 | 2% leeg |  |  |  | mediaan 2,94 |
| `co2_per_gdp` | getal | nog te beschrijven |  | 0,03 tot 2,15 | 35% leeg |  |  |  | mediaan 0,226 |
| `share_global_co2` | getal | nog te beschrijven |  | 0 tot 32,3 | 1% leeg |  |  |  | mediaan 0,022 |
| `coal_co2` | getal | nog te beschrijven |  | 0 tot 8.843 | 38% leeg |  |  |  | mediaan 2,31 |
| `gas_co2` | getal | nog te beschrijven |  | 0 tot 1.803 | 44% leeg |  |  |  | mediaan 8,04 |
| `oil_co2` | getal | nog te beschrijven |  | 0 tot 2.581 | 2% leeg |  |  |  | mediaan 4,38 |
| `total_ghg` | getal | nog te beschrijven |  | -0,003 tot 14.107 | 14% leeg |  |  |  | mediaan 46 |
| `population` | getal | nog te beschrijven |  | 501 tot 1.463.865.527 | 1% leeg |  |  |  | mediaan 5.653.245 |
| `gdp` | getal | nog te beschrijven |  | 312.853.560 tot 26.966.016.991.166 | 35% leeg |  |  |  | mediaan 75.607.242.350 |

## fact_owid_energie

Een rij is (nog te beschrijven). Bron: Our World in Data. Rijen: 416.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `country` | tekst | nog te beschrijven |  | 16 verschillende waarden | geen |  |  |  | Belgium; Brazil; China |
| `iso_code` | tekst | nog te beschrijven |  | 14 verschillende waarden | 12% leeg |  |  |  | BEL; BRA; CHN |
| `year` | getal | nog te beschrijven |  | 2.000 tot 2.025 | geen |  |  |  | mediaan 2.012 |
| `solar_share_elec` | getal | nog te beschrijven |  | 0 tot 21,8 | geen |  |  |  | mediaan 0,572 |
| `wind_share_elec` | getal | nog te beschrijven |  | 0 tot 58,2 | 1% leeg |  |  |  | mediaan 4,31 |
| `renewables_share_elec` | getal | nog te beschrijven |  | 1,27 tot 91,2 | geen |  |  |  | mediaan 19 |
| `fossil_share_elec` | getal | nog te beschrijven |  | 5,1 tot 98,5 | geen |  |  |  | mediaan 62,6 |
| `nuclear_share_elec` | getal | nog te beschrijven |  | 0 tot 79,4 | geen |  |  |  | mediaan 10,2 |
| `carbon_intensity_elec` | getal | nog te beschrijven |  | 40,5 tot 955 | geen |  |  |  | mediaan 472 |
| `solar_electricity` | getal | nog te beschrijven |  | 0 tot 2.779 | geen |  |  |  | mediaan 3,08 |
| `wind_electricity` | getal | nog te beschrijven |  | 0 tot 2.713 | 1% leeg |  |  |  | mediaan 16,8 |
| `electricity_demand` | getal | nog te beschrijven |  | 34,7 tot 31.772 | geen |  |  |  | mediaan 508 |
| `per_capita_electricity` | getal | nog te beschrijven |  | 540 tot 13.724 | geen |  |  |  | mediaan 6.021 |
| `greenhouse_gas_emissions` | getal | nog te beschrijven |  | 3,81 tot 14.570 | geen |  |  |  | mediaan 144 |

## fact_paneel_kannibalisatie

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 14.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `steekproef` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | alle zones; alleen opwekdata |
| `specificatie` | tekst | nog te beschrijven |  | 7 verschillende waarden | geen |  |  |  | eigen zonaandeel; jaareffecten; landeffecten |
| `landjaren` | getal | nog te beschrijven |  | 25 tot 182 | geen |  |  |  | mediaan 155 |
| `landen` | getal | nog te beschrijven |  | 25 tot 26 | geen |  |  |  | mediaan 25,5 |
| `r2` | getal | nog te beschrijven |  | 0,109 tot 0,895 | geen |  |  |  | mediaan 0,65 |
| `constante` | getal | nog te beschrijven |  | 0,665 tot 1,03 | geen |  |  |  | mediaan 0,975 |
| `helling_per_procentpunt` | getal | nog te beschrijven |  | -0,0287 tot -0,00381 | 29% leeg |  |  |  | mediaan -0,0061 |
| `t_waarde` | getal | nog te beschrijven |  | -14,5 tot -1,71 | 29% leeg |  |  |  | mediaan -3,46 |

## fact_prijsmodel

Een rij is (nog te beschrijven). Bron: eigen model. Rijen: 8.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `uren` | getal | Aantal uren met een prijs in de periode. | uren | 7.618 tot 8.760 | geen | 8.760 of 8.784 in een heel jaar | jaar |  | mediaan 8.736 |
| `r2_test` | getal | nog te beschrijven |  | 0,429 tot 0,811 | geen |  |  |  | mediaan 0,514 |
| `mae_model` | getal | nog te beschrijven |  | 5,46 tot 50,3 | geen |  |  |  | mediaan 24,4 |
| `mae_naief` | getal | nog te beschrijven |  | 5,88 tot 48,6 | geen |  |  |  | mediaan 28,9 |
| `verbetering` | getal | nog te beschrijven |  | -0,129 tot 0,194 | geen |  |  |  | mediaan 0,0831 |

## fact_prijsmodel_coef

Een rij is (nog te beschrijven). Bron: eigen model. Rijen: 48.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `variabele` | tekst | nog te beschrijven |  | 6 verschillende waarden | geen |  |  |  | constante; straling; wind |
| `coefficient` | getal | nog te beschrijven |  | -47,7 tot 119 | geen |  |  |  | mediaan -0,0713 |

## fact_regio_jaar

Een rij is een studieregio in 2025, 2030 of 2050: kosten en impact per euro. Bron: eigen model, aannames uit het memo. Rijen: 15.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `regio` | tekst | Studieregio (Nederland, Europa, VS, China, India). |  | 5 verschillende waarden | geen |  |  |  | Nederland; Europa (Spanje); VS (Texas) |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.025 tot 2.050 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.030 |
| `lcoe_eur_mwh` (ook: LCOE) | getal | Kosten per MWh over de levensduur in de regio en het jaar. | euro per MWh | 15,2 tot 67,4 | geen | aanname uit het eigen model | wacc |  | mediaan 33,7 |
| `wacc` (ook: kapitaalkosten) | getal | Gewogen kapitaalkosten. | fractie per jaar | 0,045 tot 0,12 | geen | 0 tot 0,3 | lcoe_eur_mwh |  | mediaan 0,054 |
| `financieringsaandeel` | getal | nog te beschrijven |  | 0,274 tot 0,544 | geen |  |  |  | mediaan 0,317 |
| `t_co2_per_meur_jaar` (ook: impact per euro) | getal | Vermeden CO2 per miljoen euro investering per jaar. | ton per miljoen euro per jaar | 42,9 tot 1.474 | geen |  |  |  | mediaan 246 |

## fact_ruimtelijk_paneel

Een rij is een regressie van de capture rate op eigen en buur-zonaandeel. Bron: eigen berekening (eti.ruimtelijk). Rijen: 8.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `steekproef` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | alle zones; alleen opwekdata |
| `specificatie` | tekst | nog te beschrijven |  | 4 verschillende waarden | geen |  |  |  | eigen + buren; eigen + buren + landeffecten; eigen + buren + jaareffecten |
| `landjaren` | getal | nog te beschrijven |  | 155 tot 182 | geen |  |  |  | mediaan 168 |
| `landen` | getal | nog te beschrijven |  | 25 tot 26 | geen |  |  |  | mediaan 25,5 |
| `r2` | getal | nog te beschrijven |  | 0,608 tot 0,898 | geen |  |  |  | mediaan 0,773 |
| `coef_eigen` | getal | nog te beschrijven |  | -0,0124 tot -0,00433 | geen |  |  |  | mediaan -0,00774 |
| `t_eigen` | getal | nog te beschrijven |  | -4,67 tot -1,78 | geen |  |  |  | mediaan -3,26 |
| `coef_buren` | getal | nog te beschrijven |  | -0,0253 tot -0,00673 | geen |  |  |  | mediaan -0,0169 |
| `t_buren` | getal | nog te beschrijven |  | -8,8 tot -1,26 | geen |  |  |  | mediaan -4,53 |
| `correlatie_eigen_buren` | getal | nog te beschrijven |  | 0,369 tot 0,422 | geen |  |  |  | mediaan 0,395 |

## fact_schokjaar_model_SJ

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 3.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `coefficient` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | gas; zon; wind |
| `waarde` | getal | nog te beschrijven |  | -0,996 tot 1,58 | geen |  |  |  | mediaan 0,423 |
| `standaardfout_geclusterd_per_maand` | getal | nog te beschrijven |  | 0,0327 tot 0,188 | geen |  |  |  | mediaan 0,173 |
| `r2` | getal | nog te beschrijven |  | 0,841 tot 0,841 | geen |  |  |  | mediaan 0,841 |
| `waarnemingen` | getal | nog te beschrijven |  | 2.116 tot 2.116 | geen |  |  |  | mediaan 2.116 |
| `schatjaren` | tekst | nog te beschrijven |  | 1 verschillende waarden | geen |  |  |  | 2019-2025 |

## fact_schokjaar_zone_SJ

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 29.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `biedzone` (ook: zone, bidding zone) | tekst | Code van de biedzone (NL, DE-LU, IT-North, NO1). |  | 29 verschillende waarden | geen | 37 zones | land |  | NO3; RO; GR |
| `prijsstijging` | getal | nog te beschrijven |  | 1,71 tot 69 | geen |  |  |  | mediaan 31,1 |
| `gas_verschil` | getal | nog te beschrijven |  | 0,103 tot 15,8 | geen |  |  |  | mediaan 15,8 |
| `zon_verschil_pp` | getal | nog te beschrijven |  | -2,47 tot 6,99 | geen |  |  |  | mediaan 0,462 |
| `wind_verschil_pp` | getal | nog te beschrijven |  | -2,66 tot 5,94 | geen |  |  |  | mediaan 0,474 |
| `door_gas` | getal | nog te beschrijven |  | 0,162 tot 25 | geen |  |  |  | mediaan 25 |
| `door_zon` | getal | nog te beschrijven |  | -1,05 tot 2,96 | geen |  |  |  | mediaan 0,196 |
| `door_wind` | getal | nog te beschrijven |  | -5,91 tot 2,65 | geen |  |  |  | mediaan -0,472 |
| `rest` | getal | nog te beschrijven |  | -11,9 tot 45,9 | geen |  |  |  | mediaan 5,77 |
| `maanden` | getal | nog te beschrijven |  | 5 tot 10 | geen |  |  |  | mediaan 10 |
| `aandeel_gas` | getal | nog te beschrijven |  | 0,095 tot 2,1 | geen |  |  |  | mediaan 0,792 |

## fact_segment_drempel_SG

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 20.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `drempel` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | capture_laag; negatief_uren; spreiding_hoog |
| `omschrijving` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | capture rate onder (zonverzadigd); negatieve uren vanaf (zonverzadigd); dagspreiding vanaf (batterijmarkt) |
| `basis` | getal | nog te beschrijven |  | 0,6 tot 300 | geen |  |  |  | mediaan 60 |
| `factor` | getal | nog te beschrijven |  | 0,8 tot 1,2 | geen |  |  |  | mediaan 1 |
| `waarde` | getal | nog te beschrijven |  | 0,48 tot 360 | geen |  |  |  | mediaan 60 |
| `zonejaren` | getal | nog te beschrijven |  | 296 tot 296 | geen |  |  |  | mediaan 296 |
| `wisselen` | getal | nog te beschrijven |  | 3 tot 58 | geen |  |  |  | mediaan 10,5 |
| `aandeel_wisselen` | getal | nog te beschrijven |  | 0,0101 tot 0,196 | geen |  |  |  | mediaan 0,0355 |
| `wisselen_2025` | getal | nog te beschrijven |  | 0 tot 9 | geen |  |  |  | mediaan 2 |

## fact_segment_zone_SG

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 296.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `biedzone` (ook: zone, bidding zone) | tekst | Code van de biedzone (NL, DE-LU, IT-North, NO1). |  | 37 verschillende waarden | geen | 37 zones | land |  | AT; LT; NL |
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 37 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Oostenrijk; Litouwen; Nederland |
| `regio` | tekst | Studieregio (Nederland, Europa, VS, China, India). |  | 6 verschillende waarden | geen |  |  |  | Midden- en Zuidoost-Europa; Scandinavie; Noordwest-Europa |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `capture_zon` (ook: marktwaardefactor, value factor) | getal | Capture rate van zon: de prijs die zon ontvangt (gewogen naar opwek) gedeeld door de gemiddelde prijs. | verhouding | 0,474 tot 1,23 | geen | tussen 0 en 2; boven 2 is een rekenfout | capture_bron, gem_prijs |  | mediaan 0,847 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 0 tot 725 | geen | 0 tot 8.784 | uren |  | mediaan 35,5 |
| `dagspreiding` (ook: daily spread) | getal | Gemiddeld verschil tussen de hoogste en laagste uurprijs van een dag. | euro per MWh | 3,14 tot 251 | geen | niet negatief | omzet_realistisch_per_mw |  | mediaan 79,5 |
| `segment` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | Vlakke prijzen; Batterijmarkt; Zon houdt waarde |
| `aandeel_gelijk` | getal | nog te beschrijven |  | 0,286 tot 1 | geen |  |  |  | mediaan 1 |
| `grensgeval` | tekst | nog te beschrijven |  | 2 verschillende waarden | geen |  |  |  | False; True |

## fact_stromen_maand

Een rij is (nog te beschrijven). Bron: ENTSO-E, Energy-Charts. Rijen: 7.500.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `van` | tekst | nog te beschrijven |  | 50 verschillende waarden | geen |  |  |  | Germany; Italy; Serbia |
| `naar` | tekst | nog te beschrijven |  | 50 verschillende waarden | geen |  |  |  | DE; IT; GR |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.024 tot 2.040 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.030 |
| `maand` | getal | Kalendermaand, 1 tot 12 (UTC). | maand | 1 tot 12 | geen | 1 tot 12 | jaar |  | mediaan 6,5 |
| `stroom` | getal | nog te beschrijven |  | -100 tot 77,5 | geen |  |  |  | mediaan 0 |

## fact_stromen_uur

Een rij is (nog te beschrijven). Bron: ENTSO-E, Energy-Charts. Rijen: 15.000.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `van` | tekst | nog te beschrijven |  | 50 verschillende waarden | geen |  |  |  | Germany; Italy; Serbia |
| `naar` | tekst | nog te beschrijven |  | 50 verschillende waarden | geen |  |  |  | DE; IT; GR |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.024 tot 2.040 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.030 |
| `uur` | getal | Uur van de dag in UTC, 0 tot 23. | uur | 0 tot 23 | geen | 0 tot 23; lokale tijd is UTC+1 of +2 | timestamp_utc |  | mediaan 11,5 |
| `uur_bron` | getal | Uur zoals de bron het telt, 1 tot 24 (het uur dat eindigt). De kolom uur is hieruit afgeleid: uur = uur_bron - 1. | uur | 1 tot 24 | geen | 1 tot 24 | bronbestand |  | mediaan 12,5 |
| `stroom` | getal | nog te beschrijven |  | -100 tot 75 | geen |  |  |  | mediaan 0 |

## fact_studieregio_jaar

Een rij is een studieregio in een jaar: opwek, aandelen en uitstoot. Bron: Ember. Rijen: 185.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `studieregio` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | China; Europa; Rest van de wereld |
| `Year` (ook: jaar) | getal | Kalenderjaar. | jaar | 1.985 tot 2.025 | geen |  |  |  | mediaan 2.007 |
| `Clean` | getal | nog te beschrijven |  | 4,26 tot 4.315 | geen |  |  |  | mediaan 1.344 |
| `Fossil` | getal | nog te beschrijven |  | 56,7 tot 7.853 | geen |  |  |  | mediaan 2.219 |
| `Solar` | getal | nog te beschrijven |  | 0 tot 1.173 | geen |  |  |  | mediaan 0,67 |
| `Total generation` | getal | nog te beschrijven |  | 70,7 tot 11.893 | geen |  |  |  | mediaan 3.962 |
| `Wind` | getal | nog te beschrijven |  | 0 tot 1.128 | 3% leeg |  |  |  | mediaan 14,7 |
| `aandeel_solar_pct` | getal | nog te beschrijven |  | 0 tot 21,1 | geen |  |  |  | mediaan 0,0314 |
| `aandeel_wind_pct` | getal | nog te beschrijven |  | 0 tot 27,4 | 3% leeg |  |  |  | mediaan 1,17 |
| `aandeel_clean_pct` | getal | nog te beschrijven |  | 5,19 tot 62,6 | geen |  |  |  | mediaan 31,6 |
| `aandeel_fossil_pct` | getal | nog te beschrijven |  | 37,4 tot 94,8 | geen |  |  |  | mediaan 68,4 |
| `Emissions (MtCO2e)` | getal | Uitstoot van de elektriciteitsopwek. | megaton CO2-equivalent | 30,7 tot 6.122 | geen |  |  |  | mediaan 1.721 |
| `intensiteit_g_kwh` | getal | nog te beschrijven |  | 251 tot 791 | geen |  |  |  | mediaan 520 |

## fact_tech_land

Een rij is een land in een jaar voor zon of wind: capture-prijs en rendement zonder contract. Bron: eigen berekening. Rijen: 538.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 37 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Nederland; Portugal; Italie (Midden-Noord) |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.023 |
| `technologie` | tekst | Techniek: zon of wind. |  | 2 verschillende waarden | geen |  | capture_price |  | wind; zon |
| `capture_price` (ook: capture-prijs) | getal | Prijs die de techniek gemiddeld ontvangt (gewogen naar opwek). | euro per MWh | 4,64 tot 315 | geen | capture_rate maal gem_prijs | gem_prijs |  | mediaan 70,9 |
| `gem_prijs` (ook: basislastprijs, baseload) | getal | Gemiddelde dagmarktprijs over alle uren van de periode. | euro per MWh | 8,72 tot 308 | geen | ongewogen over de uren | mediaan_prijs, capture_zon |  | mediaan 87,9 |
| `aandeel_productie_negatief` | getal | Deel van de opwek dat in uren met een negatieve prijs valt. | fractie | 0 tot 0,242 | geen | 0 tot 1 | negatieve_uren |  | mediaan 0,00899 |
| `irr_merchant` | getal | IRR zonder contract, als de capture-prijs van dat jaar de hele levensduur zou gelden. | fractie per jaar | -0,2 tot 0,485 | 4% leeg | leeg als de investering nooit terugkomt | capture_price |  | mediaan 0,0716 |

## fact_uk_prijs

Een rij is een halfuur in Groot-Brittannie: marktprijs. Bron: Elexon. Rijen: 135.814.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `timestamp_utc` (ook: tijdstip) | tekst | Begin van het uur of kwartier, in UTC. | tijdstip | 135814 verschillende waarden | geen | uniek per tabel; geen zomertijd | jaar, maand, uur |  | 2019-01-07 23:30; 2024-04-22 17:00; 2024-04-22 10:00 |
| `prijs_gbp_mwh` | getal | nog te beschrijven |  | -103 tot 1.984 | geen |  |  |  | mediaan 78,8 |

## fact_verbanden

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 7.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `verband` | tekst | nog te beschrijven |  | 7 verschillende waarden | geen |  |  |  | Batterij-omzet en dagspreiding; Batterij-omzet en gemiddelde prijs; Capture rate zon en negatieve uren |
| `zonejaren` | getal | nog te beschrijven |  | 256 tot 259 | geen |  |  |  | mediaan 259 |
| `rho_alle_zonejaren` | getal | nog te beschrijven |  | -0,604 tot 0,98 | geen |  |  |  | mediaan -0,221 |
| `rho_binnen_jaren` | getal | nog te beschrijven |  | -0,55 tot 0,957 | geen |  |  |  | mediaan 0,0373 |
| `rho_2019` | getal | nog te beschrijven |  | -0,47 tot 0,985 | geen |  |  |  | mediaan 0,398 |
| `rho_2020` | getal | nog te beschrijven |  | -0,622 tot 0,922 | geen |  |  |  | mediaan 0,399 |
| `rho_2021` | getal | nog te beschrijven |  | -0,421 tot 0,953 | geen |  |  |  | mediaan 0,12 |
| `rho_2022` | getal | nog te beschrijven |  | -0,376 tot 0,934 | geen |  |  |  | mediaan 0,241 |
| `rho_2023` | getal | nog te beschrijven |  | -0,632 tot 0,967 | geen |  |  |  | mediaan -0,124 |
| `rho_2024` | getal | nog te beschrijven |  | -0,625 tot 0,978 | geen |  |  |  | mediaan -0,228 |
| `rho_2025` | getal | nog te beschrijven |  | -0,7 tot 0,961 | geen |  |  |  | mediaan -0,279 |

## fact_vermogen_land

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 3.656.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 20 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | Duitsland; Zwitserland; Nederland |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.002 tot 2.030 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.019 |
| `technologie` | tekst | Techniek: zon of wind. |  | 27 verschillende waarden | geen |  | capture_price |  | wind; coal; oil |
| `naam_bron` | tekst | nog te beschrijven |  | 36 verschillende waarden | geen |  |  |  | Wind onshore; Fossil gas; Hydro Run-of-River |
| `gw` | getal | nog te beschrijven |  | 0 tot 215 | geen |  |  |  | mediaan 0,65 |

## fact_vollasturen_schatting

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 40.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `locatie` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | De Bilt; Den Helder; Eindhoven |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.022 |
| `vollasturen_schatting` | getal | nog te beschrijven |  | 920 tot 1.121 | geen |  |  |  | mediaan 1.016 |

## fact_vs_dag

Een rij is een dag in Texas of Californie: prijs, dagspreiding, batterijopbrengst, zon en wat de batterijvloot deed. Bron: EIA, gridstatus, CAISO OASIS; eigen berekening. Rijen: 5.007.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `markt` | tekst | Naam van de markt buiten de EU (Texas, Californie, Japan, een Australische deelstaat). |  | 2 verschillende waarden | geen |  | jaar |  | VS Texas (ERCOT); VS Californie (CAISO) |
| `datum` | tekst | nog te beschrijven |  | 2514 verschillende waarden | geen |  |  |  | 2020-01-01; 2024-08-08; 2024-08-01 |
| `gem_prijs_eur` | getal | Gemiddelde groothandelsprijs, omgerekend naar euro. | euro per MWh | -8,88 tot 7.588 | geen | wisselkoers van het jaar |  |  | mediaan 27,9 |
| `spreiding_2u` | getal | nog te beschrijven |  | 4,68 tot 6.696 | geen |  |  |  | mediaan 38,9 |
| `piekpremie` | getal | nog te beschrijven |  | 2,32 tot 2.960 | geen |  |  |  | mediaan 22,4 |
| `daldiepte` | getal | nog te beschrijven |  | 1,96 tot 3.736 | geen |  |  |  | mediaan 14,9 |
| `uur_piek` | getal | nog te beschrijven |  | 0 tot 23 | geen |  |  |  | mediaan 17 |
| `uur_dal` | getal | nog te beschrijven |  | 0 tot 23 | geen |  |  |  | mediaan 9 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 0 tot 11 | geen | 0 tot 8.784 | uren |  | mediaan 0 |
| `batterij_achteraf_per_mw` | getal | nog te beschrijven |  | 0 tot 6.510 | geen |  |  |  | mediaan 63,5 |
| `batterij_plan_per_mw` | getal | nog te beschrijven |  | 0 tot 6.387 | enkele leeg |  |  |  | mediaan 58 |
| `zon_mwh` | getal | nog te beschrijven |  | 0 tot 368.932 | enkele leeg |  |  |  | mediaan 98.744 |
| `wind_mwh` | getal | nog te beschrijven |  | 3.223 tot 624.005 | enkele leeg |  |  |  | mediaan 100.397 |
| `opwek_mwh` | getal | nog te beschrijven |  | 14.858 tot 1.853.265 | enkele leeg |  |  |  | mediaan 830.704 |
| `zon_piek_mw` | getal | nog te beschrijven |  | 0 tot 34.982 | enkele leeg |  |  |  | mediaan 11.385 |
| `opwek_piek_mw` | getal | nog te beschrijven |  | 13.153 tot 92.033 | enkele leeg |  |  |  | mediaan 40.334 |
| `bat_ontladen_max_mw` | getal | nog te beschrijven |  | 164 tot 11.928 | 85% leeg |  |  |  | mediaan 4.542 |
| `bat_laden_max_mw` | getal | nog te beschrijven |  | -130 tot 11.553 | 85% leeg |  |  |  | mediaan -11 |
| `bat_ontladen_mwh` | getal | nog te beschrijven |  | 516 tot 38.095 | 85% leeg |  |  |  | mediaan 16.560 |
| `oth_max_mw` | getal | nog te beschrijven |  | 0 tot 22.949 | enkele leeg |  |  |  | mediaan 374 |
| `oth_laden_max_mw` | getal | nog te beschrijven |  | -9.228 tot 10.928 | enkele leeg |  |  |  | mediaan 0 |
| `bat_aandeel_piekuur` | getal | nog te beschrijven |  | 0 tot 0,506 | enkele leeg |  |  |  | mediaan 0,028 |
| `opwek_uren` | getal | nog te beschrijven |  | 0 tot 24 | geen |  |  | Minder dan 24 betekent dat EIA die dag uren mist; de opwekkolommen zijn dan niet bruikbaar. | mediaan 24 |

## fact_vs_halfjaar

Een rij is Texas of Californie, 1 januari tot en met 24 juni van een jaar. Bron: EIA, gridstatus, CAISO. Rijen: 14.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `markt` | tekst | Naam van de markt buiten de EU (Texas, Californie, Japan, een Australische deelstaat). |  | 2 verschillende waarden | geen |  | jaar |  | VS Texas (ERCOT); VS Californie (CAISO) |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.020 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.023 |
| `uren` | getal | Aantal uren met een prijs in de periode. | uren | 4.104 tot 4.224 | geen | 8.760 of 8.784 in een heel jaar | jaar |  | mediaan 4.200 |
| `gem_prijs_eur` | getal | Gemiddelde groothandelsprijs, omgerekend naar euro. | euro per MWh | 15,9 tot 224 | geen | wisselkoers van het jaar |  |  | mediaan 26,9 |
| `capture_zon_instraling` | getal | Capture rate van zon, geschat met een instralingsprofiel in plaats van gemeten opwek. | verhouding | -0,283 tot 1,31 | geen | benadering; niet mengen met gemeten zones | capture_rate |  | mediaan 0,579 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 0 tot 1.027 | geen | 0 tot 8.784 | uren |  | mediaan 49 |
| `batterij_2u_realistisch_eur_per_mw` | getal | Dagmarktomzet van een batterij van 2 uur, plan op gisteren, lokale dagen. | euro per MW per jaar | 11.876 tot 45.642 | geen |  |  |  | mediaan 32.206 |

## fact_vs_opwek_jaar

Een rij is Texas of Californie in een jaar per brandstof. Bron: EIA (uurdata opwek per bron). Rijen: 112.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `markt` | tekst | Naam van de markt buiten de EU (Texas, Californie, Japan, een Australische deelstaat). |  | 2 verschillende waarden | geen |  | jaar |  | VS Californie (CAISO); VS Texas (ERCOT) |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.020 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.023 |
| `brandstof` | tekst | Opwekbron volgens EIA (SUN, WND, NUC, NG, BAT en andere). |  | 11 verschillende waarden | geen | in Californie zit batterij in OTH | twh |  | COL; NG; NUC |
| `twh` | getal | Opwek in het jaar. | TWh | 0 tot 204 | geen |  | aandeel_opwek |  | mediaan 17,8 |
| `aandeel_opwek` | getal | Aandeel van de brandstof in de totale opwek. | fractie | 0 tot 0,53 | geen | 0 tot 1 | twh |  | mediaan 0,0932 |
| `capture_rate` | getal | Capture rate van de genoemde techniek of brandstof. | verhouding | 0,473 tot 3,33 | 2% leeg | tussen 0 en 2 | capture_price | Kleine bronnen die alleen bij schaarste draaien halen waarden boven 2 (waterkracht Texas 2023: 2,99). | mediaan 1,05 |
| `aandeel_in_negatieve_uren` | getal | Deel van de opwek van deze bron dat in uren met een negatieve prijs valt. | fractie | 0 tot 0,309 | 2% leeg | 0 tot 1 | negatieve_uren |  | mediaan 0,0028 |
| `hoogste_uur_mw` | getal | Hoogste opwek in een uur. | MW | 0 tot 51.156 | geen |  |  |  | mediaan 5.392 |
| `uren_met_prijs` | getal | nog te beschrijven |  | 376 tot 8.784 | geen |  |  |  | mediaan 8.756 |

## fact_weer_uur

Een rij is een uur op een meetpunt: instraling en weer. Bron: Open-Meteo. Rijen: 345.240.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `locatie` | tekst | nog te beschrijven |  | 5 verschillende waarden | geen |  |  |  | De Bilt; Groningen; Vlissingen |
| `timestamp_utc` (ook: tijdstip) | tekst | Begin van het uur of kwartier, in UTC. | tijdstip | 69048 verschillende waarden | geen | uniek per tabel; geen zomertijd | jaar, maand, uur |  | 2019-01-01 00:00; 2024-04-02 05:00; 2024-04-01 15:00 |
| `straling_w_m2` | getal | nog te beschrijven |  | 0 tot 900 | geen |  |  | Gestempeld op het eind van het uur (gemiddelde over het voorgaande uur). Schuif een uur terug voordat je met prijzen of opwek rekent. | mediaan 6 |
| `wind_100m_kmh` | getal | nog te beschrijven |  | 0 tot 108 | geen |  |  |  | mediaan 24,5 |
| `temp_c` | getal | nog te beschrijven |  | -15,4 tot 38,6 | geen |  |  |  | mediaan 11,2 |
| `bewolking_pct` | getal | nog te beschrijven |  | 0 tot 100 | geen |  |  |  | mediaan 88 |

## fact_wereld_markten

Een rij is een markt buiten de EU in een jaar. Bron: EIA, gridstatus, CAISO, AEMO, JEPX, Elexon. Rijen: 30.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `markt` | tekst | Naam van de markt buiten de EU (Texas, Californie, Japan, een Australische deelstaat). |  | 4 verschillende waarden | geen |  | jaar |  | Verenigd Koninkrijk; Japan (systeemprijs); VS Texas (ERCOT) |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.019 tot 2.026 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.023 |
| `uren` | getal | Aantal uren met een prijs in de periode. | uren | 6.609 tot 8.784 | geen | 8.760 of 8.784 in een heel jaar | jaar |  | mediaan 8.760 |
| `gem_prijs_eur` | getal | Gemiddelde groothandelsprijs, omgerekend naar euro. | euro per MWh | 18,7 tot 232 | geen | wisselkoers van het jaar |  |  | mediaan 52,6 |
| `capture_zon_instraling` | getal | Capture rate van zon, geschat met een instralingsprofiel in plaats van gemeten opwek. | verhouding | 0,282 tot 1,41 | geen | benadering; niet mengen met gemeten zones | capture_rate | Schatting uit instraling, zonder afschakelen. De gemeten opwek in Californie ligt hoger (0,50 tegen 0,39 in 2025): parken schakelen af bij negatieve prijzen. | mediaan 0,798 |
| `negatieve_uren` | getal | Aantal uren met een dagmarktprijs onder nul. | uren | 0 tot 1.171 | geen | 0 tot 8.784 | uren |  | mediaan 29 |
| `batterij_2u_realistisch_eur_per_mw` | getal | Dagmarktomzet van een batterij van 2 uur, plan op gisteren, lokale dagen. | euro per MW per jaar | 9.240 tot 97.736 | geen |  |  |  | mediaan 32.691 |

## fact_wereldbeeld

Een rij is (nog te beschrijven). Bron: eigen berekening. Rijen: 3.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `wereldbeeld` | tekst | nog te beschrijven |  | 3 verschillende waarden | geen |  |  |  | Huidig beleid; Orderly (Net Zero); Disorderly |
| `irr_zon` | getal | IRR van het zonnepark van 10 MW voor belasting, bij de marktwaarde van dat jaar. | fractie per jaar | 0,0301 tot 0,058 | geen |  | capture_rate, lcoe |  | mediaan 0,049 |
| `irr_batterij_standalone` | getal | nog te beschrijven |  | -0,117 tot -0,0175 | geen |  |  |  | mediaan -0,0342 |
| `irr_batterij_hybride` | getal | nog te beschrijven |  | -0,0331 tot 0,0277 | geen |  |  |  | mediaan 0,0189 |
| `netto_irr_belegger` | getal | nog te beschrijven |  | -0,000849 tot 0,0286 | geen |  |  |  | mediaan 0,0191 |

## fact_worldbank

Een rij is (nog te beschrijven). Bron: Wereldbank. Rijen: 40.762.

| Kolom | Type | Beschrijving | Eenheid | Waarden of bereik | Leeg | Regels | Verwant | Bekende problemen | Voorbeelden |
|---|---|---|---|---|---|---|---|---|---|
| `land` (ook: markt) | tekst | Naam van het land of de biedzone in het Nederlands. |  | 265 verschillende waarden | geen | sleutel samen met jaar | biedzone, iso3 |  | St. Lucia; Madagascar; Bhutan |
| `iso3` (ook: ISO 3 code) | tekst | Landcode volgens ISO 3166 (drie letters). |  | 261 verschillende waarden | 1% leeg | koppelt aan Ember | land |  | BDI; DMA; ATG |
| `jaar` | getal | Kalenderjaar. 2026 is onvolledig (tot 15 november). | jaar | 2.000 tot 2.025 | geen | geheel getal; filter 2026 uit vergelijkingen tussen jaren | uren | 2026 loopt tot 15 november. | mediaan 2.012 |
| `indicator` | tekst | nog te beschrijven |  | 7 verschillende waarden | geen |  |  |  | bevolking; bbp_per_hoofd_usd; toegang_elektriciteit_pct |
| `waarde` | getal | nog te beschrijven |  | 0 tot 8.215.424.893 | geen |  |  |  | mediaan 65,7 |
