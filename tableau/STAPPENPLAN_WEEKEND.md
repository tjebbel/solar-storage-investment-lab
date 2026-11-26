# Stappenplan weekend 27 tot 29 november 2026: de eerste drie dashboards

Vaste regels: bron verbinden via Verbinding bewerken naar `tableau/data_en/`; KPI-rij dupliceren van dashboard 18 en filteren op
`Dashboard`; elke titel een ondertitel; geen "Next"-regel; legendatitels verbergen; selectie wissen voor publiceren.
Kleuren: oranje `E39A2D` (Nederland, teruglevering), batterijblauw `4A5FC1`, magenta `C4457A`, teal `1F9E89`, warmgrijs `A8A29E`,
lichtgrijs `D6D3D1`, middengrijs `78716C`, donkergrijs `44403C`.

## Dashboard 36 "After net metering" (tab `netmetering`, 1200 x 1600)
Bronnen: `t101_household_profile`, `t90_feed_in_tariffs_2027`. KPI 36: `74%` · `80%` · `Eneco: 4.4 ct/kWh` · `2.9 ct/kWh`.
Dashboardtitel: `After net metering: a solar household feeds in when power is worth least`
Ondertitel: `Dutch standard household profile 2026 (NEDU E1A) and feed-in terms of 13 suppliers. Net metering ends on 1 January 2027.`

1. `dayprofile` (hoofdgrafiek). Filter `Month = 6`. Kolommen `Hour`; rijen Meetwaarden met `Offtake with solar` (lijn, donkergrijs
   `44403C`) en `Feed-in with solar` (vlak, oranje `E39A2D`).
   Titel: `In June a solar household feeds in at noon and buys in the evening`
   Ondertitel: `Average June day, share of yearly volume per hour. Orange = feed-in, grey = offtake.`
   Controle: teruglevering piekt om 12 uur; juni is 15,6% van de jaarteruglevering.
2. `feedmonth`. Kolommen `Month`; rijen `SUM(Feed-in with solar)` als staaf oranje `E39A2D`, weergegeven als percentage van totaal.
   Titel: `Four fifths of the feed-in falls between April and September`
   Ondertitel: `Share of yearly feed-in per month.`
   Controle: jan 1,4 · apr 12,2 · mei 15,2 · jun 15,6 · jul 15,3 · aug 13,2 · dec 0,8 (procent).
3. `suppliers` (t90, filter `As of = 2026-11-24`). Rijen `Supplier`, aflopend op `Net ct/kWh`; kolommen `Net ct/kWh`, staaf teal
   `1F9E89`; referentielijn mediaan (2,9) donkergrijs `44403C`. `Feed-in payment` en `Feed-in cost` in de knopinfo.
   Titel: `After costs a household keeps 0.3 to 4.4 cents per kWh fed in`
   Ondertitel: `Feed-in payment minus feed-in cost, 13 suppliers, 24 November 2026. Line = median.`
   Controle: Eneco 4,40 · Vattenfall 4,27 · Mega 3,98 · PowerPeers 2,93 · Vandebron 0,25.
Onderrand: `1. Profile = average household with solar (NEDU E1A, version 1.00); a single home differs. 2. Supplier terms change often;
check the date. 3. Mega pays 25.2 and charges 21.2 ct/kWh: only the net amount compares. 4. Source: MFFBAS/NEDU profiles 2026; keuze.nl.`

## Dashboard 28 "Europe's future is in California and South Australia" (tab `worldduck`, 1200 x 1600)
Bronnen: `t68_world_duck_profile`, `t69_world_duck_depth`. KPI 28: `1% of average` · `33% of average` · `55% of average` · `6.7% of hours`.
Dashboardtitel: `Europe's future is in California and South Australia`
Ondertitel: `Hourly power prices in seven markets, as an index of the yearly average. Sources: AEMO, CAISO, ERCOT, JEPX, Elexon, Energy-Charts.`

1. `worldprofile` (hoofdgrafiek, t68, filter `Year = 2025`). Kolommen `Hour`; rijen `AVG(Price index)`; `Market` op Kleur: Netherlands
   oranje `E39A2D`, South Australia magenta `C4457A`, California batterijblauw `4A5FC1`, Germany middengrijs `78716C`, de rest
   lichtgrijs `D6D3D1`. Referentielijn op 1.
   Titel: `At midday South Australia's power is almost free; the Netherlands is halfway there`
   Ondertitel: `Average price per hour in 2025, 1 = yearly average of that market.`
2. `middaytrend` (t69). Kolommen `Year`; rijen `Midday index 11-15h`; `Market` op Kleur (zelfde kleuren).
   Titel: `The Dutch midday price fell from 99% to 55% of the average in six years`
   Ondertitel: `Price between 11 and 15h as a share of the yearly average, per market.`
   Controle Nederland: 2019 0,99 · 2023 0,74 · 2025 0,55. California 2025 0,33. South Australia 2025 0,01.
3. `negative` (t69, filter `Year = 2025`). Rijen `Market` aflopend; kolommen `Negative hours %`; Nederland oranje, rest warmgrijs `A8A29E`.
   Titel: `South Australia had negative prices in 30% of all hours`
   Ondertitel: `Share of hours with a price below zero, 2025.`
   Controle: South Australia 29,9 · California 11,1 · Netherlands 6,7 · Germany 6,6 · UK 2,7 · Texas 0,3 · Japan 0.
Tekstvak: `California's grid batteries grew from 2 GW (2021) to 13 GW in four years (Ember). That is what flattened its evening peak.`
Onderrand: `1. Index = price divided by the yearly average, so currencies compare. 2. South Australia uses market time (UTC+10).
3. 2026 is a partial year and is left out of the bars.`

## Dashboard 23 "Energy poverty" (tab `energypoverty`, 1200 x 1600)
Bronnen: `t88_energy_poverty`, `t97_energy_poverty_region`. KPI 23: `6.0%` · `Vaals: 14.2%` · `25 of 342` · `624 EUR/yr`.
Dashboardtitel: `Energy poverty: who pays for the transition`
Ondertitel: `Share of Dutch households with a low income and high energy cost or a poorly insulated home. Source: CBS and TNO, Monitor Energiearmoede.`

1. `povertymap` (hoofdgrafiek, t97, filters `Level = Gemeente`, `Year = 2024`). Zet `Name` op geografische rol Gemeente (Nederland);
   dubbelklik `Name` voor de kaart; `Energy poverty pct` op Kleur, een tint van lichtgrijs `D6D3D1` naar magenta `C4457A`.
   Lukt de kaart niet binnen tien minuten: staafdiagram van de 15 hoogste gemeenten, magenta `C4457A`.
   Titel: `Energy poverty runs from 1.6% in Rozendaal to 14.2% in Vaals`
   Ondertitel: `Share of households per municipality, 2024, 342 municipalities.`
   Controle: Vaals 14,2 · Heerlen 12,6 · Enschede 11,6 · Rotterdam 11,4 · Arnhem 10,2 · Amsterdam 9,9.
2. `povertytrend` (t88). Kolommen `Year`; rijen `Energy poverty pct`, lijn magenta `C4457A` met labels.
   Titel: `Support hid the problem in 2022 and 2023; it came back in 2024`
   Ondertitel: `Share of all households, 2019 to 2025. 2025 is a provisional estimate by TNO.`
   Controle: 2019 9,9 · 2021 6,8 · 2022 4,1 · 2023 3,7 · 2024 6,0 · 2025 6,0.
3. `provinces` (t97, filters `Level = Provincie`, `Year = 2024`). Rijen `Name` aflopend; kolommen `Energy poverty pct`, staaf warmgrijs
   `A8A29E`; referentielijn op 6,0 (landelijk) donkergrijs `44403C`.
   Titel: `Groningen is highest at 8.2%, Utrecht lowest at 4.6%`
   Ondertitel: `Share of households per province, 2024. Line = national share (6.0%).`
   Controle: Groningen 8,2 · Fryslan 7,0 · Limburg 6,7 · Utrecht 4,6.
Onderrand: `1. Definition: low income combined with high energy cost or low energy quality of the home (LIHE and/or LILEK).
2. 2023 and 2024 are provisional. 3. The gap of 624 EUR is what a household in energy poverty is short per year (2025).
4. Source: CBS, Monitor Energiearmoede 2019-2024 (table 3); CBS/TNO, 24 July 2026.`
