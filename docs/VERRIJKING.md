# Verrijking van de dashboards (27 november 2026)

Wat ontbreekt, wat kan worden aangevuld en waar de data al klaarstaat. Gerangschikt op effect per minuut werk.
Basis: de werkmap zoals laatst opgeslagen (17 dashboards), de vier dashboards van 26 en 27 november, en de tabellen in
`tableau/data_en` die nog op geen dashboard staan. De oudere dashboards zijn hiervoor niet opnieuw live bekeken.

## A. Een extra grafiek met data die al klaarstaat (10 tot 15 minuten per stuk)

| Dashboard | Toevoegen | Tabel | Wat het laat zien |
|---|---|---|---|
| 23 Energy poverty | `groups`: staaf per groep, filter `Characteristic` = Ownership, Household type, Main income source | t103 (nieuw) | Sociale huur 14,1% tegen koop 1,3%; bijstand 41,8% tegen werknemers 1,7%; alleenstaanden 11,5% |
| 23 Energy poverty | `labels`: staaf per energielabel | t103 | Label A 3,8%, label E 12,6%: isolatie is de hefboom |
| 23 Energy poverty | Zin in de ondertitel of onderrand | t97 | In alle 342 gemeenten ligt het aandeel in 2024 lager dan in 2019; samenhang met laag inkomen 0,92, met slechte isolatie 0,37 |
| 36 After net metering | `feedvalue`: marktprijs per uur in juni tegen het terugleverprofiel, of drie staven (marktwaarde teruglevering, gemiddelde prijs, kosten afname) | t101 (aangevuld) | Een teruggeleverde kWh was op de markt 4,2 ct waard, een afgenomen kWh kostte 10,1 ct; het jaargemiddelde was 8,7 ct. 14% van de teruglevering valt in uren met een gemiddeld negatieve prijs. Indicatief: profiel 2026 maal maand- en uurgemiddelde prijzen van 2025 |
| 18 Storage saturation | `drivers`: spreiding per dag tegen opbrengst, een punt per zone en jaar | t79 | De dagspreiding verklaart 94% van de batterij-opbrengst; elke euro spreiding is ongeveer 405 EUR per MW per jaar |
| 4 Experience curve | `storagecurve`: prijs van lithium-ion voor netopslag | t98 | Van 1.659 naar 285 USD per kWh tussen 2010 en 2021; 19% goedkoper per verdubbeling |
| 4 Experience curve | `countries`: kostprijs per land door de jaren | t93 | Nederland van 131 (2016) naar 42 USD per MWh (2024) |
| 15 Global South | `publicfinance`: publieke financiering voor zon tegen kapitaalkosten | t84 | India kreeg 7,6 miljard dollar en betaalt 10,8%; Maleisie 6 miljoen en 6,5% |
| 15 Global South | `waccmap`: kapitaalkosten in 64 landen | t85 | Onder investment grade 9,7% tegen 5,3% |
| 8 Netherlands | `gridcost`: netkosten Nederland tegen de EU | t96 | Van 5,7 naar 11,4 ct per kWh sinds 2019 |
| 8 Netherlands | `solved`: jaar waarin de congestie per gebied is opgelost | t29, t31 | Regionaal loopt het van 2026 tot 2038; bij TenneT geen enkel gebied voor 2032 |
| 5 Abatement cost curve | Referentieband met de subsidie per ton van de SDE++ | t94 | Zon op land 62 EUR per ton subsidie tegenover negatieve kosten in 11 van 26 landen |
| 27 Climate fund simulator | Het blad `returnCO2` staat in de werkmap maar op geen dashboard | t81 | Rendement tegen vermeden CO2 per bouwsteen |

## B. Wat op meerdere dashboards ontbreekt

1. **Geen startpagina.** Er zijn nu 21 tabbladen zonder overzicht. Een dashboard `Index` met per dashboard een regel (titel, de
   belangrijkste uitkomst, link) maakt de reeks bruikbaar voor wie via LinkedIn binnenkomt. De teksten staan al in de README.
2. **Gebeurtenissen in tijdreeksen.** `t42_gebeurtenissen` (11 gebeurtenissen: Fukushima, gascrisis, einde saldering) staat op geen
   dashboard. Een annotatie bij 2022 op dashboards 2, 16, 18 en 19 verklaart de piek zonder dat de lezer het moet raden.
3. **Dekking van de data.** `t59_coverage` laat per zone en jaar zien hoeveel van de zonopwek gedekt is. Een voetnoot met het
   dekkingspercentage op dashboards 16, 19 en 20 maakt duidelijk welke zones dun zijn.
4. **Eigen aannames tegen een externe bron.** `t41_toetsen` (10 toetsen) staat alleen in de data. Het hoort op dashboard 7.
5. **Controles voor de nieuwe bronnen.** De controlematrix telt 21 controles; de tabellen t94 tot t103 hebben er geen. Zes nieuwe
   controles liggen voor de hand: PBL twee keer gelezen, Eurostat tegen ACER, CBS-gemeenten gewogen tegen landelijk, wachtrij
   Nederland tegen het halfjaarrapport, NGFS-omrekening, en waterstof tegen het IEA-rapport (nog open). Let op: het getal 21 staat
   in de memo en in de README.
6. **Laatste update.** Geen enkel dashboard zegt tot welke datum de data loopt in de titelregel, alleen in de onderrand. Een vaste
   regel `Data to 15 November 2026` onder de dashboardtitel scheelt de lezer zoeken.

## C. Open punten per gepubliceerd dashboard (uit `docs/ontwerp_beoordeling.md`)

| Dashboard | Punt |
|---|---|
| 36 After net metering | Astitel `Solar (fraction of year)` naar `Share of yearly volume` |
| 28 World duck curve | Kleursleutel herhaalt de ondertitel; waardelabels in `negatives` |
| 23 Energy poverty | Astitel `Share of household`; staven paars in plaats van magenta `C4457A` |
| 18 Storage saturation | Label `Median (64k)` raakt de as |
| 2 Signals Netherlands | Referentieregel in KPI-tegel 1 breekt af over drie regels |
| 1, 3 en 4 | Onderrand: bronnen op dashboard 3, verouderde tekst op dashboard 4, dashboard 1 compacter |
| 15 Global South | Sinds 25 november niet live gecontroleerd; heeft drie grafieken waar de andere er vier of vijf hebben |

## D. Wat niet kan zonder nieuwe data

- **42:** Duitsland en Belgie ontbreken, omdat er geen landelijk cijfer bestaat.
- **44:** kosten per ontlaadduur (PNNL-waarden per techniek).
- **12:** Europa apart (de regio's van het model in plaats van vijf werelddelen).
- **22:** banen per land voor zon (alleen China bekend).

## E. Live controle van alle dashboards (27 november 2026, 08:50 tot 09:10)

Elk tabblad geopend op Tableau Public in een venster van 1500 bij 3000. `marginal` en `Controlmatrix` waren na ruim 25 seconden
nog aan het laden en zijn alleen voor het bovenste deel beoordeeld.

### Gebreken die een lezer direct ziet
| Dashboard | Wat er mis is |
|---|---|
| 16 Duck curve (`duckcurve`) | Alleen de hoofdgrafiek staat erop; daaronder is ongeveer 60% van het dashboard leeg. Ook na 50 seconden wachten. De drie andere grafieken (dip per zone, tijdstip, negatieve uren) ontbreken |
| 15 Global South (`GlobalSouth`) | Alleen de zonnegrafiek staat erop; de onderste helft is leeg. De grafieken over kapitaalkosten ontbreken, terwijl de titel en de KPI-rij juist daarover gaan |
| 5 Abatement cost curve (`costcurve`) | De as `Margin (EUR/MWh)` heeft een lichtblauw vlak: een selectie is meegepubliceerd |
| 8 Netherlands (`NL`) | KPI `8.1 GW` en de titel gebruiken de wachtrij van juli 2025; het halfjaarrapport geeft 10,0 GW (30 juni 2026). De grafiek van de negatieve uren neemt een derde van het dashboard in met veel wit |

### Regel "geen Next" nog niet overal doorgevoerd
`duckcurve`, `NL` en `carbonfree` hebben nog een blok `What comes next` met een regel `Next: ...`.

### Kleinere punten
| Dashboard | Punt |
|---|---|
| 1 First findings | Kaart toont voor de helft de Atlantische Oceaan; KPI-tegels zonder eenheid (`61,041`, `124`, `87`); zonecodes `NO3`, `SE4` in plaats van namen |
| 3 Nuclear | Alle vier KPI-tegels lichtgrijs en daardoor moeilijk leesbaar; landenlijst met 30 regels in kleine letters |
| 4 Experience curve | KPI-rij vult 80% van de breedte; tegel 3 lichtgrijs; geen bronregel in de onderrand |
| 14 Impact investor | KPI-tegels 1 en 2 lichtgrijs; roze punten vallen buiten het palet |
| 17 PPA or merchant | In orde |
| 19 Hirth replication | Dashboardtitel zonder ondertitel |
| 20 Hourly carbon-free | Dashboardtitel `Hourly carbon-free` zegt niet wat de uitkomst is; eindlabel `11.07` bij 2026 past niet bij de titel (21% in 2025) |
| 26 Revenue at risk | Dashboardtitel `Revenue at risk 2030` zonder uitkomst; punten paars in plaats van magenta `C4457A`; geen bronregel |
| 27 Climate fund simulator | Legendatitel `Hurdle col...` |
| 29 Battery without perfect foresight | Drie van de vier KPI-tegels lichtgrijs; legendatitels `Values`; Nederland niet oranje; geen bronregel |
| 2 Signals Netherlands | Zie 26 november: referentieregel in tegel 1 breekt af |

### Terugkerend patroon
- **Lichtgrijze KPI-tegels.** De richting "neutral" wordt op de oudere dashboards lichtgrijs `D6D3D1` getoond; op de nieuwe is het
  middengrijs `78716C`. Lichtgrijs op wit is slecht leesbaar. Een keer aanpassen in de kleurtoewijzing van `Richting` lost het op
  elk dashboard op dat dezelfde gegevensbron gebruikt.
- **Paars in plaats van magenta.** Op 23, 26 en 28 is magenta `C4457A` paars geworden; waarschijnlijk staat de dekking onder 100%.
- **KPI-rij niet op volle breedte** op 4, 5 en 8.
