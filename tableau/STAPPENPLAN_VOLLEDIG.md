# Stappenplannen volledig formaat: dashboards 16, 19, 5, 20, 14, 8, 18, 17, 6, 9 (deel 1) en 25-30 (deel 2)

Geschreven za 21 november 2026 (ochtend). Volgorde = postvolgorde. Alle bronnen uit `tableau/data_en`; alle controlewaarden zijn
uit de data herberekend. Werkwijze per dashboard (ongeveer 1,5 uur bij het huidige tempo):

**Vast sjabloon (eerst één keer maken van dashboard 16, daarna dupliceren):**
1. Bronnen toevoegen (Data → Nieuwe gegevensbron → Tekstbestand).
2. KPI-rij: dupliceer `KPI 16` → hernoem `KPI <n>` → filter Dashboard = n.
3. Hoofdgrafiek + drie ondersteunende werkbladen (stappen hieronder). Kleuren: teal `1F9E89` goed, magenta `C4457A` slecht,
   grijzen `A8A29E` / `D6D3D1` / `78716C`, oranje `E39A2D` = Nederland, zon `C9961A`, wind `2A9DB5`, kern `7A5195`, gas `A0522D`,
   batterij `4A5FC1`.
4. Dashboard: dupliceer het vorige dashboard (rechtsklik tabblad → Dupliceren), vervang de werkbladen (sleep nieuw werkblad op het
   oude, oude verwijderen), pas teksten aan. Vaste maat **1200 × 1900**:

   | Rij | Inhoud | Hoogte |
   |---|---|---|
   | 1 | Titel 20 pt + subtitel 10 pt grijs | 90 |
   | 2 | KPI-rij (titel uit) | 150 |
   | 3 | Hoofdgrafiek, volle breedte | 480 |
   | 4 | Ondersteunend A (600) naast B (600) | 440 |
   | 5 | Ondersteunend C (600) naast tekstvak "How to read this" (600) | 400 |
   | 6 | Onderrand: What we do not know for sure (600) · What comes next (600), koppen 12 pt vet | 170 |

5. Zelftoets: titel = bevinding met getal; één kleur = één betekenis; geen Nederlands woord; geen selectie; geen scrollbalk.
6. Publiceren (Server → Tableau Public → Opslaan), link sturen, lokaal opslaan.

---

## Dashboard 16 "Duck curve" (rest; stap 1-3 gedaan of bezig)

**Stap 4. "Dip over time"** (t54): Year (dimensie, discreet) op Kolommen, Midday dip EUR/MWh op Rijen (SUM), markering Lijn,
Zone name op **Detail**, kleur grijs `D6D3D1` met doorzichtigheid 50%. Dan `Is NL` (berekend veld zoals in stap 3) op **Kleur**:
True `E39A2D`, False `D6D3D1`; zet NL vooraan (rechtsklik legenda → Sorteren). Referentielijn **mediaan per cel**
(Analyse → Referentielijn → Per cel → Mediaan), donkergrijs `44403C`, label `median of 37 zones`.
Titel: `The dip deepens every year: Netherlands 0 in 2019, 39 in 2025, 59 in 2026` · subtitel `2026 to 15 November`.
**Controle** NL: 2019 0.3 · 2022 45.8 · 2023 25.1 · 2024 28.7 · 2025 38.7 · 2026 58.9. Mediaan: 2023 15.3 · 2025 29.1 · 2026 49.4.

**Stap 5. "Negative hours"** (t54): filter Year 2023 en 2025; Zone name op Rijen, Negative hours op Kolommen, Year op **Kleur**
(2023 `D6D3D1`, 2025 `44403C`), markering Staaf naast elkaar (Year ook op Rijen rechts van Zone name, of gebruik Meetwaarden).
Top 15 op Negative hours 2025 (filter Boven). NL-label vet.
Titel: `The Netherlands has the second-most negative-price hours in Europe: 584 in 2025`.
**Controle** 2025: Sweden (North-Central) 681 · Netherlands 584 · Germany 576 · Spain 556 · Sweden (North) 520 · Belgium 519. NL 2023: 316.

**Tekstvak "How to read this"**: `The midday dip is the day-average price minus the 11-15h price. A deeper dip means solar sells into
cheaper hours. The evening-to-midday ratio (NL 2.6) is less sensitive to the overall price level.`

**Dashboard** `Duck curve` · Titel `The duck gets deeper: in all 37 zones the midday price fell further behind the day average`
· subtitel `Hourly day-ahead prices, 37 European bidding zones, 2019 to 15 November 2026 (Energy-Charts)`.
Rij 3 The duck · rij 4 Dip per zone + Dip over time · rij 5 Negative hours + tekstvak.
Onderrand links: `1. Hours in local time; quarter-hours averaged from October 2025. 2. The dip also grows when evening prices rise
(gas), not only when solar grows. 3. 2026 runs to 15 November.`

---

## Dashboard 19 "Hirth replication"

**Bronnen** `t56_hirth`, `t56b_hirth_months`. **KPI 19**: `-0.020` (magenta) · `-0.019` Germany (magenta) · `0.52` (magenta) · `5 of 25` (grijs).

1. **Hoofdgrafiek "Germany month by month"** (t56b): Solar share % (Kolommen) × Solar capture rate (Rijen), AVG; Year + Month op
   Detail; markering Cirkel `C9961A` 70%. Zone name filter als keuzelijst (Eén waarde), standaard Germany. Analyse → Trendlijn
   lineair, `44403C`. Referentielijn y = 1 `worth as much as the average hour`.
   Titel: `Hirth was right: the more solar, the less each MWh is worth` · subtitel `Monthly solar share vs solar capture rate, Germany 2019-2026; choose a zone`.
   **Controle** Germany: 94 punten; van 1.4% share (jan 2021, 1.05) tot 33.7% (jun 2026, 0.59). Hover trendlijn: helling ≈ -0.019.
2. **"Slope per zone"** (t56, filter Reliable = True → 20 zones): Zone name op Rijen, Slope per percentage point op Kolommen, Cirkel
   `44403C`; Interval low/high op Detail → Referentieband per cel (van low tot high) `D6D3D1`. Sorteer op slope.
   Titel: `Every zone loses value as solar grows; the median slope is -0.020`.
   **Controle**: France -0.060 (steilst, 0.050-0.070), Czechia -0.049, Germany -0.019, Estonia -0.009 (vlakst). 20 zones.
3. **"At 10% and at 30% solar"** (t56, Reliable): Meetwaarden Capture rate at 10% share en at 30% share; Zone name op Rijen,
   Meetwaardenamen op Kleur (10% `D6D3D1`, 30% `C9961A`), markering Cirkel (dumbbell). Titel: `At 30% solar, about half the value is left (median 0.52)`.
4. **"Year by year"** (t56b): Year (discreet) × MEDIAN(Solar capture rate) — klik pil → Meting → Mediaan, lijn `C9961A`, labels.
   Titel: `Median monthly capture rate across 25 zones: 1.01 in 2019, 0.70 in 2026`.
   **Controle**: 2019 1.01 · 2022 0.94 · 2023 0.87 · 2024 0.79 · 2025 0.77 · 2026 0.70.

**Tekstvak**: `Lion Hirth (2013) showed that the market value of solar falls as its share grows. This replication uses monthly
data to November 2026: each extra percentage point of solar lowers the capture rate by about 0.02.`
**Dashboard** `Hirth replication` · titel `Each extra percent of solar costs 2% of its value` · subtitel `Replication of Hirth (2013),
25 European zones, monthly 2019 to 15 November 2026`. Onderrand links: `1. Monthly data include the season, so slopes are steeper
than yearly (-0.011). 2. Five zones are left out: too little solar or a poor fit (R2 below 0.4). 3. The Netherlands is missing:
Energy-Charts covers 2% of its solar.`

---

## Dashboard 5 "Abatement cost curve"

**Bron** `t13_kostencurve`. **KPI 5** (marginale factor, bijgewerkt 21 nov avond): `7 of 26` (teal) · `103 Mt CO2/yr` (grijs) · `Italy: -109 EUR/t` (teal) · `35 EUR/t` NL (magenta, vergelijking: average factor 55).
Waarom marginaal als standaard: nieuwe zon verdringt vooral gas (zie dashboard 25), en met de gemiddelde factor loopt de y-as tot 1.304 EUR/t (Sweden, Norway) zodat de rest van de curve plat wordt.

0. **Parameter** `Emission factor` (tekenreeks, lijst: `Marginal (gas)`, `Average`; **huidige waarde `Marginal (gas)`**), toon parametercontrole. Berekende velden:
   `Cost per tonne` = `IF [Emission factor]="Average" THEN [Cost per tonne (average factor)] ELSE [Cost per tonne (marginal factor)] END`
   `Potential Mt` = idem met Potential; `Cumulative Mt` = idem met Cumulative; `Start Mt` = `[Cumulative Mt] - [Potential Mt]`.
1. **Hoofdgrafiek "Cost curve"**: Start Mt (SUM, continu) op Kolommen, Cost per tonne (SUM) op Rijen, markering **Gantt-balk**,
   Potential Mt (SUM) op **Formaat**; Country op Detail en Label. Filter Potential Mt > 0. Kleur: berekend veld
   `Band` = `IF [Country]="Netherlands" THEN "Netherlands" ELSEIF [Cost per tonne] < 0 THEN "At a profit" ELSE "At a cost" END`
   (At a profit `1F9E89`, At a cost `A8A29E`, Netherlands `E39A2D`). Referentielijnen y = 74 `EU ETS 2025 average` en y = 90 `EU ETS November 2026`, y = 0 grijs.
   Titel: `Solar abates CO2 at a profit in 7 of 26 countries` · subtitel `Width = extra solar to 2030 targets (Mt CO2/yr); height = cost per tonne; switch the emission factor top right`.
   **Controle Marginal (standaard)**: totaal 102.6 Mt; Italy links (-109; 21.2 Mt), dan Croatia -46 · Slovenia -37 · Romania -33 · Greece -22; Spain breedste balk (37; 30.1 Mt); Sweden rechts (115).
   **Controle Average**: totaal 45.6 Mt, Italy -153 (15.1 Mt); Sweden en Norway ~1.300 EUR/t. Zet de y-as op **Automatisch** zodat hij meeschaalt.
   NL heeft potentieel 0 (doel al gehaald) → verschijnt niet in de curve; staat wel in grafiek 2.
2. **"Margin per country"**: Country op Rijen, Margin EUR/MWh op Kolommen, staaf, gesorteerd; kleur `Band`. Referentielijn 0.
   Titel: `Where solar earns more than it costs: capture price minus LCOE, 2025`.
   **Controle**: Italy +43.7 · Bulgaria +22.2 · Croatia +18.3 · Slovenia +14.8 · Serbia +13.5 · Romania +13.3 · Greece +8.7 (7 positief) ·
   Poland -0.1 · NL -14.0 · Sweden -46.2.
3. **"Why the factor matters"**: Country × Average emission factor t/MWh, staaf `78716C`, gesorteerd.
   Titel: `Clean grids make CO2 expensive to abate: Sweden 0.04 t/MWh, Poland 0.59`. **Controle** Serbia 0.70, Poland 0.59, France 0.04.

**Tekstvak**: `Read it like a McKinsey cost curve: bars to the left of zero save money and CO2 at the same time. The marginal factor
assumes solar replaces gas; the average factor assumes it replaces today's mix. That choice doubles the potential (46 vs 103 Mt).`
**Dashboard** `Abatement cost curve` · subtitel `Solar capture price vs LCOE per country, 2025; potential to 2030 targets`.
Onderrand links: `1. LCOE for two reference countries only (north 67, south 51 EUR/MWh). 2. Avoided CO2 is not an emission
reduction (GHG Protocol). 3. Germany, Bulgaria and Serbia have no 2030 target in the data, so no width.`

---

## Dashboard 20 "Hourly carbon-free"

**Bronnen** `t57_carbon_free`, `t58_carbon_free_hour`. **KPI 20**: `France: 96%` (teal) · `54%` Germany (grijs) · `67%` (teal) · `21% of hours` (teal).
Filter overal **Solar coverage ok = True** (22 zones).

1. **Hoofdgrafiek "By hour"** (t58, Year 2025): Hour (dimensie, discreet) × AVG(Carbon-free share %), lijn per Season
   (Summer `C9961A`, Winter `2A9DB5`); Zone name keuzelijst, standaard Germany. Referentielijn 90 `24/7 ambition` gestreept.
   Titel: `Green on paper, grey at night: Germany is 78% carbon-free at 1 pm in summer, 42% at 8 pm in winter`.
   **Controle** Germany 2025: uur 2 summer 45 / winter 43 · uur 13 summer 78 / winter 55 · uur 20 summer 47 / winter 42.
2. **"Zones 2025"** (t57, 2025): Zone name × Carbon-free share %, staaf, gesorteerd; label Hours below 50 % (in knopinfo ook
   Hours above 90 %). Kleur grijs, NL bestaat niet (dekking) → geen oranje. Titel: `France and Switzerland are clean almost every hour; Poland 28%`.
   **Controle**: France 95.6 · Switzerland 94.7 · Finland 83.6 · Germany 53.6 · Poland 27.8; 22 rijen (Italië 4× dezelfde waarde, Denemarken 2×).
3. **"Progress"** (t57): Year × MEDIAN(Carbon-free share %) en MEDIAN(Hours below 50 %) (dubbele as of twee lijnen via Meetwaarden).
   Titel: `The median zone: 59% carbon-free in 2019, 67% in 2025; hours below 50% fell from 36% to 21%`.
   **Controle**: 2019 59.1 / 36.3 · 2023 66.8 / 22.1 · 2025 67.3 / 21.2 · 2026 72.1 / 11.1.
4. **"Annual vs hourly"** (t57, 2025): Carbon-free share % (x) × Hours above 90 % (y), cirkels, Zone name label.
   Titel: `A high annual share is not the same as clean hours: Finland 84% but only 7% of hours above 90%`.

**Tekstvak**: `Companies often buy annual green certificates. 24/7 carbon-free means matching every hour. Solar alone cannot do
that at night: storage, wind, hydro or nuclear fill the gap.`
**Dashboard** `Hourly carbon-free` · subtitel `Share of generation without fossil fuels, by hour, 22 zones with reliable data, 2019-2026`.
Onderrand links: `1. Biomass is not counted as carbon-free (conservative). 2. Zones with under 60% solar coverage are left out (15),
including the Netherlands. 3. Imports are not traced; Italy and Denmark report country data per zone.`

---

## Dashboard 14 "Impact investor"

**Bronnen** `t27_impact`, `t39_vermeden_co2`. **KPI 14**: `246 t/yr` (grijs) · `-14 EUR/MWh` (magenta) · `40.0 Mt` (teal) · `11.8 Mt` (teal).

1. **Hoofdgrafiek "CO2 per million euro"** (t27): Region op Rijen, Tonnes CO2 per M EUR per year op Kolommen, Year (dimensie) op
   Kleur (2025 `44403C`, 2030 `A8A29E`, 2050 `D6D3D1`), staven naast elkaar. NL-label oranje.
   Titel: `One million euro in Indian solar avoids six times as much CO2 as in the Netherlands` · subtitel `Tonnes CO2 avoided per year per million euro invested in solar`.
   **Controle** 2025: India 1,474 · China 1,091 · US (Texas) 329 · Netherlands 246 · Spain 122.
2. **"Capital cost"** (t27, 2025): Meetwaarden LCOE EUR/MWh en LCOE at 5% WACC per Region (dumbbell of twee staven), WACC in label.
   Titel: `India's solar would be 38% cheaper at European financing costs (44 vs 28 EUR/MWh)`.
3. **"Additionality"** (t27, 2025, Solar margin niet leeg): Region × Solar margin EUR/MWh, staaf magenta; label Additionality.
   Titel: `In the Netherlands and Spain solar loses money without support, so investment adds real capacity`.
   **Controle**: Netherlands -14.0 · Spain -15.0.
4. **"Avoided CO2 in the Netherlands"** (t39): filter Source = `Solar power`, `Onshore wind`, `Offshore wind`, `Biomass, total` (let op de exacte namen; `Biomass, total` is inclusief biobrandstof-ketels, niet de biobrandstoffen voor transport);
   Year × Avoided CO2 kt, gestapeld (zon `C9961A`, wind op land `2A9DB5`, wind op zee `1B6F80`, biomassa `78716C`).
   Titel: `Dutch renewables avoided 40 Mt CO2 in 2025; solar 11.8 Mt`. **Controle** 2025: Solar power 11,755 · Onshore 7,907 · Offshore 7,321 · Biomass 11,641 kt.

**Tekstvak**: `Avoided emissions are not an emission reduction: they cannot be netted off scope 1-3 (GHG Protocol). Additionality
asks whether the investment adds capacity that would otherwise not be built.`
**Dashboard** `Impact investor` · titel `Where does a climate euro do the most? Six times more CO2 avoided in India than in the Netherlands`.
Onderrand links: `1. WACC from IEA for five regions; Africa uncertain. 2. CO2 per euro uses each region's 2025 grid factor;
it falls as grids get cleaner (2030, 2050). 3. CBS 2025 figures are provisional.`

---

## Dashboard 8 "Netherlands"

**Bronnen** `t37_nl_stroom`, `t40_res_regio`, `t30_congestie_rnb`, `t32_congestie_gemeente`, `t51_congestie_afstemming`, `t25_flex_nl`.
**KPI 8** (na verversen t50!): `21%` (teal) · `+5% in 2025` (magenta, referentie **29.2 GWp (RES monitor)**) · `8.1 GW` (magenta) · `584 h` (magenta).
LET OP: t40 bevat een totaalregel `Nederland` en een regel `Niet in te delen`. **Filter RES region ≠ Nederland** in elk werkblad
dat regio's optelt (eerder telde de KPI dit dubbel: 58.4 in plaats van 29.2 GWp; hersteld 21 nov).

1. **Hoofdgrafiek "Build-out"** (t40, filter RES region = Nederland): Year × Solar large MWp en Solar small MWp (Meetwaarden,
   gestapeld; groot `C9961A`, klein `E8C36A`); label Solar growth % boven de staaf (dubbele as of tekst).
   Titel: `Dutch solar growth halved twice: +27% in 2023, +13% in 2024, +5% in 2025`.
   **Controle** (Nederland-regel): 2025 ≈ 29.2 GWp; groei 2021 33% · 2022 32% · 2023 27% · 2024 13% · 2025 5%.
2. **"Grid queue by province"** (t30): Province × Queue offtake MW (staaf `C4457A`) en Queue feed-in MW (staaf `A8A29E`), gesorteerd.
   Titel: `About 8 GW of demand and 4 GW of supply wait for a connection; Noord-Brabant 1.8 GW`.
   NB: t30 telt per provincie 7.90 GW, de KPI (t51) 8.05 GW; het verschil zit in gebieden die over provincies heen lopen (bv. `Noord-Holland, Utrecht`). Laat die rijen staan (ze zijn klein) en rond in titels af op "about 8 GW". **Controle** totaal offtake 7,900 · feed-in 4,066 MW; Noord-Brabant 1,782 offtake.
3. **"Municipalities"** (t32): top 20 op Offtake shortage %, staaf magenta. Titel: `192 of 342 municipalities have an offtake shortage in at least half their postcodes`.
   **Controle**: 192 van 342 gemeenten ≥ 50%; **67 gemeenten staan op 100%**, dus een top 20 is willekeurig. Beter: histogram (Offtake shortage % in klassen van 10) of filter = 100 met titel `67 municipalities have a shortage in every postcode`.
4. **"Negative hours"** (t25): Year × Negative hours, staaf `44403C`, 2026 lichter (`A8A29E`, tot 15 nov).
   Titel: `Negative prices: 3 hours in 2019, 584 in 2025`. **Controle**: 2023 315 · 2024 458 · 2025 584 · 2026 399.
5. **Reconciliation** (t51) als kleine tabel in het tekstvak-vak (Queue, This project GW, Official GW, Status-kleur).

**Tekstvak "From 1 January 2027"**: `Dutch net metering ends on 1 January 2027. Rooftop owners will be paid a feed-in tariff
instead of offsetting at the retail price, which makes self-consumption and home batteries more valuable.`
**Dashboard** `Netherlands` · titel `Dutch solar hits the grid wall: growth fell to 5% while 8 GW waits for a connection`.
Onderrand links: `1. The capacity map (2026) and the official queue (July 2025) differ; TenneT's 38 GW is not yet explained (C20).
2. RES-monitor capacity is MWp (DC); CBS counts 25.9 GW. 3. 2026 runs to 15 November.`

---

## Dashboard 18 "Storage saturation"

**Bron** `t55_battery_arbitrage`. **KPI 18**: `64k EUR/MW` (grijs) · `Estonia: 95k` (teal) · `71k` NL (teal) · `277 days` (grijs).

1. **Hoofdgrafiek "Revenue by year"**: Year × MEDIAN(Revenue per MW), staaf `4A5FC1`; tweede pil Revenue per MW met filter
   (berekend veld `NL revenue` = `IF [Zone name]="Netherlands" THEN [Revenue per MW] END`, SUM) als lijn `E39A2D`, dubbele as, gesynchroniseerd.
   Titel: `No saturation yet: median battery arbitrage revenue rose from 49k (2023) to 64k EUR/MW (2025)`.
   **Controle** mediaan: 2019 13.7k · 2022 93.6k · 2023 48.6k · 2024 52.8k · 2025 64.0k · 2026 72.2k; NL: 2022 110.8k · 2025 71.1k · 2026 80.5k.
2. **"Zones 2025"**: Zone name × Revenue per MW, staaf, gesorteerd, NL oranje (Is NL), referentielijn mediaan.
   Titel: `The Baltics and South-East Europe earn most; Nordic zones least`. **Controle**: Estonia 95.2k · Bulgaria 94.3k · Lithuania 94.2k · Norway (North) 7.4k.
3. **"Good days"**: Year × Days with margin above 100 voor Netherlands (lijn oranje) en MEDIAN alle zones (grijs).
   Titel: `In 2025 a Dutch battery earned more than 100 EUR/MW on 285 days`. **Controle** NL: 2021 156 · 2022 344 · 2025 285.

**Tekstvak**: `Perfect foresight is an upper bound: it assumes the battery knows tomorrow's prices. A realistic model gives 61k
instead of 71k for the Netherlands. Saturation shows up when many batteries flatten the evening peak.`
**Dashboard** `Storage saturation` · subtitel `2-hour battery, one cycle per day, 88% round-trip efficiency, day-ahead arbitrage only, 37 zones`.
Onderrand links: `1. Upper bound: no forecast error. 2. Reserve markets (FCR, aFRR) are not included. 3. 2022 was the gas crisis;
2026 runs to 15 November.`

---

## Dashboard 17 "PPA or merchant" (herzien 23 november; werkbladen gebouwd)

**Bronnen** `t61_ppa_prices`, `t62_ppa_vs_merchant` (11 landen, kolom `Source`), `t76_ppa_countries` (25 landen). Na een nieuwe run
de bronnen vernieuwen met Cmd+R. **KPI 17**: `55 EUR/MWh` · `31 EUR/MWh` (`lowest LevelTen country`), beide magenta `C4457A` ·
`+4 EUR/MWh` · `+24%`, beide teal `1F9E89`. Subtitel: `LevelTen P25 offers and Pexapark composite vs realised solar capture prices`.

1. **`dumbbelppa`** (t62): `Country with gap` op Rijen (berekend veld: `[Country] + "  " + IF [PPA minus capture price] > 0 THEN "+"
   ELSE "" END + STR(ROUND([PPA minus capture price],0))`), aflopend gesorteerd op SUM(PPA minus capture price). Meetwaarden op
   Kolommen met alleen `PPA P25 Q4 2025 EUR/MWh` en `Solar capture price EUR/MWh`; Namen van meetwaarden op Kleur (PPA batterijblauw
   `4A5FC1`, capture oranje `E39A2D`) en op Filters. Type Vorm, `Source` op Vorm: LevelTen gevulde cirkel, KYOS open cirkel
   (niet op Kleur: dat splitst de reeks). Referentieband per cel van minimum naar maximum, lichtgrijs `D6D3D1`, geen lijn.
   Alias in de legenda: `PPA price (P25 or equivalent)`. Titel: `Was a solar PPA worth it in 2025? Only in France and Germany` ·
   subtitel `Solid = LevelTen P25 offers; open = KYOS estimates, which run about 25% below LevelTen where both exist`.
   **Controle**: France +27 · Germany +4 · Spain -4 · Belgium -5 · Portugal -6 · Greece -7 · Poland -11 · Netherlands -20 ·
   Romania -20 · Hungary -23 · Italy -34.
2. **`ppatrend`** (t61, filter Index = `P25 continental index`): KWARTAAL(Date) × SUM(Price EUR/MWh), lijn `4A5FC1`, labels met één
   decimaal. Tweede pil Price op Rijen als dubbele, gesynchroniseerde as: type Vorm, `Derived` op Vorm (`yes` open, `no` gevuld).
   Referentielijn constante 63.64, lichtgrijs gestippeld, op de linkeras. Titel: `European solar PPA prices fell 14% in two years` ·
   subtitel `LevelTen P25 continental index, EUR/MWh; open points are derived quarters`.
   **Controle**: Q3 2024 63.6 → Q3 2025 58.2 → Q4 2025 57.4 → Q1 2026 55.1 → Q2 2026 54.5 → Q3 2026 54.7. Q4 2024 t/m Q2 2025
   staan niet in de bronnen: de lijn loopt daar rechtdoor.
3. **`countries`** (t76): Market op Rijen, aflopend op SUM(Price EUR/MWh); staaf met label (0 decimalen); `Source` op Kleur
   (LevelTen donker `4A5FC1`, KYOS licht `9AA5E0`). Aliassen: `LevelTen P25 offers, Q4 2025` en `KYOS estimates, 2026-2035`.
   Titel: `Solar PPA prices run from 26 EUR/MWh in Sweden to 87 in the UK` · subtitel `Dark = LevelTen P25 offers, Q4 2025;
   light = KYOS estimates for 2026-2035`. **Controle**: UK 87 · France 63 · Italy 61 · Germany 50 · Spain 33 · Sweden 26; 25 landen.
4. **`composite`** (t61, filter Index = `EURO Composite`; uitgebreid 23 nov naar 21 maanden): MAAND(Date) als doorlopende datum ×
   SUM(Price EUR/MWh), lijn middengrijs `78716C`; tweede as met `Derived` op Vorm (open = afgeleid), labels alleen op begin, dal en eind.
   Titel: `All technologies: from 52 EUR/MWh in December 2024 to a low of 43 in February 2026, back to 48 in September` · subtitel
   `Pexapark EURO Composite, monthly, EUR/MWh; open points are derived from the next month's change`.
   **Controle**: Dec 2024 51.8 · Jan 2025 52.5 · Jun 2025 49.6 · Dec 2025 45.1 · Feb 2026 42.7 · May 2026 44.9 · Sep 2026 48.3.
   Maart 2026 ontbreekt. April 2026: de bron meldt 51,80, wat botst met mei (+1,2% naar 44,90); afgeleid 44,4 gebruikt.

**Dashboard** `PPA or merchant`, 1200 × 2300, tegels: koptekst `PPA or merchant: what is a fixed solar price worth?` · `KPI 17` ·
`dumbbelppa` · `ppa2030` (t77: PPA tegen 2025 en de stresstest 2030) · `ppatrend` en `composite` naast elkaar · `countries` ·
onderrand "Important to know" en tekstvak "How to read a PPA?". Legenda's zonder titel, `Richting` en `Derived` verborgen.
**Tekstvak "How to read a PPA"**: `A pay-as-produced solar PPA pays a fixed price for every MWh produced, so the buyer takes the
cannibalisation risk. That is why solar PPAs are cheaper than wind. A hybrid PPA adds a battery and delivers in the evening: +24%.`
Onderrand links: `1. A PPA is a 10-year price; the capture price is one year. 2. LevelTen P25 = 25th percentile of offers, not
signed deals; France and Greece as reported by pv magazine. 3. KYOS = P25-equivalent model estimate for 2026-2035 (June 2025),
about 25% below LevelTen; indicative only. 4. 2030 is a stress test at 2025 price levels, not a forecast; Germany has no 2030
target in the data. 5. Open points in the trend charts are derived; March 2026 is missing.` Geen "Next"-regel (ontwerpregel 23 nov).
**Gepubliceerd 23 november, 17/20**, met `ppa2030` (t77) als tweede grafiek: https://public.tableau.com/app/profile/tjebbe.lodeizen/viz/SolarandstorageinEurope/PPA

---

## Dashboard 6 "Profit pool"

**Bron** `t60_value_chain`. **KPI 6**: `7 of 8` (magenta) · `-9%` (magenta) · `15% (Sungrow)` (teal) · `29% (First Solar)` (grijs).

1. **Hoofdgrafiek "Margin along the chain"**: Company op Rijen gesorteerd op Chain order, Net margin % als staaf, kleur
   `Profitable` (True `1F9E89`, False `C4457A`); Segment en Gross margin % in knopinfo; referentielijn 0.
   Titel: `In 2025 the solar chain lost money everywhere except in inverters, storage and protected markets`.
   **Controle**: TCL Zhonghuan -31.9 · GCL -19.9 · Tongwei -11.4 · Trina -10.5 · JA -9.4 · LONGi -9.1 · Jinko -6.8 · Enphase +11.7 · Sungrow +15.1 · First Solar +29.3.
2. **"Chain view"**: Chain order (dimensie) × AVG(Net margin %), staaf; alias 1 Polysilicon · 2 Wafers · 3 Wafers and modules · 4 Modules · 5 Thin film (US) · 6 Inverters and storage.
   Titel: `The further downstream, the better the margin`.
3. **"Who is big"**: Company × Revenue USD bn, staaf, kleur Group (China `A8A29E`, Outside China `1F9E89`).
   Titel: `The two largest (Sungrow 13.0 and Tongwei 12.3 bn USD) sit at opposite ends`.

**Tekstvak**: `Net margin includes one-off impairments. The IEA finds more than 90% of Chinese makers loss-making in 2025 and 10-15%
margins outside China. Ten companies are not the whole market: developers and installers are missing.`
**Dashboard** `Profit pool` · subtitel `Net margin of ten listed solar companies, 2025 annual results; 6.85 CNY per USD`.
Onderrand links: `1. Net margin, not a full profit pool. 2. First Solar and Enphase include US tax credits (45X). 3. Integrated
companies span several segments.`

---

## Dashboard 9 "EU convergence"

**Bronnen** `t18_convergentie`, `t9_signalering_zones` (al in werkmap). **KPI 9**: `253 EUR/MWh` (grijs) · `192` (magenta) · `0.79` (magenta) · `80 of 83` (grijs).

1. **Hoofdgrafiek "Fan chart"** (t18): Month (continu) × Median, lijn `44403C`; P10 en P90 op Detail → Referentieband per cel? Werkt
   niet op een continue as; gebruik **Meetwaarden** P10, Median, P90 als drie lijnen (P10/P90 `D6D3D1`), of een gebiedsgrafiek.
   Titel: `One market, 37 prices: the gap between expensive and cheap zones is twice the 2019 level`.
   **Controle**: 2026-11 P10 91.7 · median 252.9 · P90 283.6; 2019-01 median 56.7.
2. **"Relative spread"** (t18): Month × Relative spread, lijn `C4457A`; referentielijn 0.42 `2019 average`.
   **Controle**: piek 2024-07 1.62; jaargemiddelde 2019 0.42 · 2024 0.97 · 2026 0.79.
3. **"Shock spreads"** (t9): Maand × CNT(Zonenaam) met filter Prijs signaal = Shock, staaf `C4457A`, vanaf 2025.
   Titel: `In November 2026, 27 of 37 zones were in a price shock`. **Controle**: 2026-09 16 · 2026-10 19 · 2026-11 27.
4. **"Zones 2026"** (t9, Jaar 2026): Zonenaam × AVG(Gemiddelde prijs), staaf gesorteerd, NL oranje.
   Titel: `Italy pays around 160 EUR/MWh in 2026, northern Norway 32`. **Controle**: Italy (Centre-North) 166 · Netherlands 127 · Norway (North) 32.

**Tekstvak**: `The EU wants one power market. Interconnectors should pull prices together; the spread shows how far that is.
Relative spread = (P90 - P10) / median: a value of 1 means the expensive zones pay twice as much as the cheap ones above the median.`
**Dashboard** `EU convergence` · subtitel `Monthly day-ahead prices, 37 European bidding zones, January 2019 to November 2026`.
Onderrand links: `1. Relative spread explodes when the median is low (2020). 2. Zones, not countries: Italy and Scandinavia count
several times. 3. November 2026 runs to the 15th.`

---

# Deel 2: verdieping vanaf maandag 23 november (eerst 25 en 27, vóór het gesprek van donderdag)

Bronnen staan klaar in `tableau/data_en` (t63-t72); KPI-tegels in t50 (Dashboard 25-30). Zelfde sjabloon als deel 1.

## Dashboard 25 "What does a MWh really avoid?"

**Bronnen** `t63_marginal_factor_hour`, `t64_avoided_per_mwh`. **KPI 25**: `0.15-0.56 t` Germany (grijs) · `0.36-0.67 t` Poland (teal) ·
`2 of 19` countries where a battery adds CO2 (magenta; Italy and Serbia, both methods agree, more than 5 t/MW/yr) · Netherlands `not measurable` (grijs).
Filter overal **Reliable = True** (26 zones in 2025), behalve in grafiek 4.

1. **Hoofdgrafiek "Three factors by hour"** (t63, Year 2025, Zone keuzelijst standaard Germany, Season keuzelijst standaard Summer):
   Hour (discreet) × Meetwaarden Average factor (lijn `78716C`), Marginal factor fossil response (lijn `C4457A`), Marginal factor
   domestic (lijn `E8A0BF` gestreept). Referentieband tussen de twee marginale lijnen is mooi maar optioneel.
   Titel: `What a solar MWh avoids depends on the method: 0.04 to 0.40 t at 1 pm in a German summer`.
   **Controle** Germany 2025 summer: uur 3 AEF 0.34 / fossil 0.81 / domestic 0.16 · uur 13 AEF 0.12 / 0.40 / 0.04 (52% van de uren prijs <= 0) · uur 20 AEF 0.32 / 0.73 / 0.11.
2. **"Range per zone"** (t64, 2025): Zone name op Rijen; Meetwaarden Marginal solar hours domestic en fossil response als
   dumbbell (cirkels), Average factor solar hours als ruit `78716C`. Sorteer op fossil response.
   Titel: `The range is wide everywhere: Bulgaria 0.04 to 0.87 t/MWh`. **Controle**: Bulgaria 0.04-0.87 · Poland 0.36-0.67 · Germany 0.15-0.56.
3. **"Batteries: more or less CO2?"** (t64, 2025): Zone name × Battery net CO2 t per MW per year (beide methoden, staven naast
   elkaar), kleur op teken (positief teal = vermijdt, negatief magenta = voegt toe). Titel: `A battery can add CO2: in Italy and Serbia both methods show more emissions, not less`. Knopinfo: `Charging hours can be dirtier than discharging hours; the sign depends on which plants set the price.`
   **Controle**: Germany +19 / +59 · Czechia +82 / -28 · Italy (North) -49 / -30.
4. **"Germany over time"** (t64, Zone Germany): Year × Average factor (year), Marginal fossil response en domestic (solar hours).
   Titel: `The fossil-response factor fell from 0.80 (2019) to 0.56 (2025) as coal left the margin`.

**Tekstvak**: `Impact reports often multiply solar output by the average grid factor. Decisions need the marginal factor: which
plant really backs off. Two honest methods give a range; report both, or state which one you use.`
**Dashboard** `Marginal emissions` · titel `What does a MWh of solar really avoid? Between 0.15 and 0.56 t in Germany`.
Onderrand links: `1. Direct emissions with IPCC default factors, not plant data. 2. Imports and exports are not traced.
3. The Netherlands is left out: Energy-Charts books a third of Dutch output as unclassified (use CBS: 0.25 t/MWh).`

## Dashboard 27 "Climate fund simulator"

**Bronnen** `t65_fund_assets`, `t66_fund_draws`, `t67_fund_portfolios`. **KPI 27**: `7.5%` (teal) · `4.6%` fund net (magenta) · `3-9x` (grijs) · `45%` (grijs).

0. **Parameters** (Tableau, getal, bereik 0-100, stap 5): `w Solar South` (25), `w Solar North` (25), `w Battery East` (25),
   `w Battery West` (25). Toon alle vier als schuif. Berekende velden in t66:
   `Weight` = `CASE [Building block] WHEN "Solar South" THEN [w Solar South] WHEN "Solar North" THEN [w Solar North]
   WHEN "Battery East" THEN [w Battery East] ELSE [w Battery West] END`
   `Portfolio IRR (draw)` = `SUM([Project IRR] * [Weight]) / SUM([Weight])` (op niveau Draw).
1. **Hoofdgrafiek "Your portfolio: 1,000 futures"** (t66): Draw op Detail, `Portfolio IRR (draw)` op Kolommen als histogram:
   maak een berekend veld `IRR bin` = `ROUND([Portfolio IRR (draw)] * 100)` via `{FIXED [Draw] : ...}` en tel draws per bin
   (staaf `4A5FC1`). Referentielijnen 0% en 8% (hurdle), en P10/P50/P90 als percentielband.
   Titel: `Your portfolio across 1,000 futures: median project return and the chance of beating 8%`.
   **Controle** met 25/25/25/25 (Balanced): P10 -0.6% · P50 4.2% · P90 9.0% · 15% van de draws boven 8%.
2. **"Return vs impact"** (t65): scatter per land: IRR P50 (x) × CO2 per M EUR per year (marginal fossil response; y), kleur
   Building block (Solar South `C9961A`, Solar North `E8C36A`, Battery East `4A5FC1`, Battery West `9AA5E0`), foutbalk P10-P90 op x.
   Titel: `Batteries in the east earn most; solar avoids most CO2 per euro`.
   **Controle** gemiddelden: Battery East 9.5% · Solar South 5.6% · Battery West 1.5% · Solar North 0.6%; CO2 fossil response: Solar South 921 · Solar North 645 · Battery West 135 · Battery East 36 t per M EUR per year.
3. **"Five portfolios"** (t67): tabel Portfolio × Project IRR P10/P50/P90, Fund net IRR, TVPI, CO2 per M EUR (domestic - fossil response).
   **Controle**: South and east 7.5% / net 4.6% / TVPI 1.29 · North and west 0.8% / -2.4% · Solar only 3.1% / 0.0% / 153-783 t · Batteries only 5.5% / 2.5% / 54-86 t.
   Zesde rij (gevoeligheid): **Batteries only, with reserve markets (x1.5)**: 16.4% / net 12.1% / TVPI 1.86. Zet die rij apart
   (cursief of grijs) met de knopinfo `Illustrative: reserve markets (aFRR, FCR) can be up to 67% of a German battery's income (Capstone, Nov 2025); the 1.5x is an assumption, not a measurement.`
4. **"What drives it"** (t66, Building block = Solar South): Solar value decline per year (x) × Project IRR (y), cirkels; en
   Battery saturation per year × IRR voor Battery East. Titel: `The two risks that matter: solar value decline and battery saturation`.

**Tekstvak "How to read this"**: `Each dot is one possible future. Prices, the decline in solar value, battery saturation and
costs are drawn at random within published ranges. Move the sliders to build a portfolio; the fund return is after a 2% fee
and 20% carry above an 8% hurdle.`
**Dashboard** `Climate fund simulator` · titel `Return and impact in one decision: no portfolio wins on both`.
Onderrand links: `1. A model with public inputs, not investment advice. 2. Battery revenue is day-ahead arbitrage only, so a floor; with
reserve markets the battery case changes completely (16% instead of 5.5%). Battery capex 408k EUR/MW is an assumption. 3. CO2 per euro is year 1 on today's grid; it falls as grids get cleaner.`

## Dashboard 26 "Revenue at risk 2030"

**Bron** `t70_revenue_at_risk`. **KPI 26**: `22 EUR/MWh` mediaan (magenta) · `Spain: 3.2 bn EUR/yr` (magenta) · Italy `capture rate 0.58` (teal) · `8 of 23` geëxtrapoleerd (grijs).
1. **Hoofdgrafiek**: Country × Revenue at risk EUR/MWh (staaf), foutbalk (steep/flat) als referentieband per cel; vorm/arcering voor
   `Within observed range` = False (lichter). Titel: `If 2030 solar targets are met, solar loses a median 22 EUR/MWh of revenue`.
   **Controle**: Croatia 48 · Romania 40 · Denmark 36 · Greece 36 · Italy 28 · Spain 23 · Netherlands 0 (doel al gehaald).
2. **"Capture rate 2025 → 2030"**: dumbbell per land (2025 `A8A29E`, 2030 `C4457A`), referentielijn 0.2 (vloer).
3. **"Euros at stake"**: Revenue at risk M EUR per year, top 10. **Controle** Spain 3,186 · Italy 2,688 · France 1,372.
4. **"Above LCOE?"**: Solar revenue 2030 EUR/MWh vs LCOE per land; alleen Italy erboven.
Onderrand: `1. Price level of 2025 held constant. 2. Storage and flexible demand will flatten the slope: an upper bound.
3. Eight countries go beyond the shares the regression has seen.`

## Dashboard 28 "Europe's future is in California and South Australia"

**Bronnen** `t68_world_duck_profile`, `t69_world_duck_depth`. **KPI 28**: SA `1% of average` · California `33%` · NL `55%` (2019: 99%) · NL `6.7%` negative hours.
1. **Hoofdgrafiek**: Hour × Price index (1 = year average), lijn per Market, Year 2025; Kleuren: Netherlands `E39A2D`, South Australia `C4457A`, California `4A5FC1`, Germany `78716C`, rest `D6D3D1`.
   Titel: `At midday, South Australia's power is almost free; the Netherlands is halfway there`.
2. **"Midday index over time"** (t69): Year × Midday index per Market. **Controle** NL 2019 0.99 → 2023 0.74 → 2025 0.55; California 2025 0.33; SA 2023 -0.01.
3. **"Negative hours %"** (t69, 2025): staaf per markt. **Controle** SA 29.9 · California 11.1 · NL 6.7 · Germany 6.6 · UK 2.7 · Texas 0.3 · Japan 0.
4. **Tekstvak**: `California's grid batteries grew from 2 GW (2021) to 13 GW in four years (Ember). That is what flattened its evening peak.`
Onderrand: `1. Index = price / year average, so currencies compare. 2. South Australia uses market time (UTC+10). 3. Japan's
fiscal year 2019 starts in April.`

## Dashboard 29 "Battery without perfect foresight" (floor and ceiling)

**Bron** `t71_battery_strategies`. **KPI 29**: `80% of the ceiling` · NL `83%` (59k vs 71k) · Baltics `60%` · fixed schedule `56%`.
Lees: perfecte voorkennis = plafond; handelen op de prijzen van gisteren = vloer zonder voorspelling. Een echte handelaar zit ertussen.
1. **Hoofdgrafiek**: Zone name × Perfect foresight en Yesterday's prices EUR/MW (dumbbell), 2025, gesorteerd.
2. **"Capture by strategy"**: Year × MEDIAN(… vs perfect) voor drie strategieën.
3. **"Netherlands"**: Year × vier opbrengsten. Tekstvak: `Perfect foresight is a ceiling; the gap is the value of a good forecast.`

## Dashboard 30 "Forecasting showcase" (model klaar zo 22 nov; `eti.voorspelmodel`)

**Bronnen** `t73_forecast_model`, `t74_forecast_week`, `t75_forecast_features`. **KPI 30**: `22 EUR/MWh` NL model (gisteren: 24) · `36 of 37` zones ·
`87%` van perfecte voorkennis (gisteren: 80%) · `23 EUR/MWh` zonder weer en belasting.
Model: ridge-regressie per zone, getraind op 2019 t/m het jaar voor het testjaar (uitbreidend venster), getest op 2023, 2024, 2025, 2026.
1. **Hoofdgrafiek "One week in May"** (t74, Year keuzelijst standaard 2025): Hour of week (continu) × Meetwaarden Actual (lijn `44403C`),
   Model (`4A5FC1`), Yesterday (`A8A29E` gestreept). Titel: `The model follows the midday dip better than yesterday's prices`.
   **Controle**: 168 uren per jaar (12-18 mei).
2. **"Error per zone"** (t73, 2025): Zone name × MAE model en MAE yesterday (dumbbell, gesorteerd op Improvement vs yesterday %).
   Titel: `The model beats yesterday's prices in 36 of 37 zones; median error 20 vs 23 EUR/MWh`.
   **Controle**: Lithuania +20% · Germany +19% · Netherlands +9% (21.7 vs 23.9) · Norway (North) -5% (enige verliezer).
3. **"What it is worth"** (t73): Year × MEDIAN(Battery model vs perfect) en MEDIAN(Battery yesterday vs perfect), lijnen.
   Titel: `A better forecast is worth 7 points of battery revenue: 87% vs 80% of the ceiling`. **Controle** NL 2025: 0.90 vs 0.83 (63.5k vs 58.7k van 70.9k EUR/MW).
4. **"What drives the forecast"** (t75): Feature × Standardised coefficient, staaf gesorteerd op Absolute.
   Titel: `Yesterday's price carries the forecast; wind and solar pull it down`. **Controle**: Price yesterday 37.9 · Mean yesterday 25.4 ·
   Price last week 20.6 · Wind -6.8 · Solar -4.3.

**Tekstvak (model card)**: `Ridge regression per zone on lagged prices, calendar, load, wind and solar. Trained on all years before
the test year, never on the test year itself. Load, wind and solar are the realised values, standing in for the day-ahead
forecasts a trader has, so the error is a lower bound for this model type. Without them the error is 23 instead of 22 EUR/MWh in
the Netherlands: most of the gain comes from prices and calendar, not from weather.`
Onderrand links: `1. A linear model: no price spikes, no negative-price logic. 2. Realised weather instead of forecasts flatters
the result slightly. 3. Battery revenue is day-ahead only, 2 hours, one cycle a day.`

---

# Deel 3: kruisanalyses op bestaande tabellen (23 november; `eti.verdieping`, t77-t81)

De hoofdgrafiek van 37 (t77) staat sinds 23 november in dashboard 17; een apart dashboard 37 is alleen nog nodig voor de
verdieping met meer LevelTen-kwartalen. Geen "Next"-regels op nieuwe dashboards.

Uitkomsten per doelgroep: `docs/deep_dives.md`. Methode en beperkingen: `docs/methodology.md`, sectie "Kruisanalyses".
Vaste kleuren: goed teal `1F9E89`, slecht magenta `C4457A`, PPA batterijblauw `4A5FC1`, capture/zon oranje `E39A2D`,
neutraal warmgrijs `A8A29E`, banden lichtgrijs `D6D3D1`.

## Dashboard 37 "A PPA is a bet on 2030, not on 2025" (t77)

1. **Hoofdgrafiek** (t77): Market op Rijen, gesorteerd op `PPA minus 2030 revenue`; Meetwaarden `PPA price EUR/MWh` (batterijblauw
   `4A5FC1`), `Solar revenue 2025 EUR/MWh` (oranje `E39A2D`) en `Solar revenue 2030 EUR/MWh` (magenta `C4457A`) als cirkels met een
   lichtgrijze band; `PPA source` op Vorm (LevelTen gevuld, KYOS open). Titel: `In 12 of 19 countries the PPA price is above what
   solar would earn in 2030` · subtitel `PPA price against solar revenue in 2025 and in the 2030 stress test; open = KYOS estimate`.
   **Controle**: France 63 / 36 / 15 · Greece 53 / 60 / 24 · Spain 33 / 36 / 13 · Italy 61 / 95 / 67 · Netherlands 34 / 53 / 53.
2. **"Three groups"** (t77): Reading × AANTAL, staaf. **Controle**: 3 · 9 · 7.
3. **"Against cost"** (t77): Market × `PPA minus LCOE`, staaf, teal boven nul en magenta eronder. Titel: `Only Italy and Greece
   have a PPA price above the reference LCOE`. **Controle**: Italy +9.6 · Greece +1.4 · Sweden -41.
Onderrand: `1. 2030 is a stress test at 2025 price levels, not a forecast. 2. In 7 countries 2030 is an extrapolation (see flag).
3. 15 of 19 prices are KYOS estimates, about 25% below LevelTen. 4. LCOE has two reference values (Spain, Netherlands).
5. Germany is missing: no 2030 target in the source.`

## Dashboard 38 "Solar loses, batteries gain: how much battery hedges a solar park?" (t78, t79)

1. **Hoofdgrafiek** (t78): `Solar capture price change` (x) tegen `Battery revenue per MW change` (y), een punt per zone, `Reading` op
   Kleur (hedge teal `1F9E89`, both down magenta `C4457A`), nullijnen. Titel: `In 28 of 37 zones solar lost value while batteries
   gained it, 2023-2025`. **Controle**: NL -17.5 / +13.7k · DE-LU -26.2 / +19.0k · ES -36.7 / +18.4k · GR -34.8 / +32.9k.
2. **"Hedge ratio"** (t78): Zone name × `Battery MW per solar MW to offset`, staaf gesorteerd, referentielijn mediaan.
   Titel: `About 1.3 MW of battery offsets the loss of 1 MW of solar (median)`. **Controle**: GR 1.1 · NL 1.3 · DE-LU 1.4 · ES 2.0.
3. **"What drives battery revenue"** (t79): `Daily spread EUR/MWh` × `Battery revenue per MW`, punt per zone-jaar, trendlijn; ernaast
   `Negative hours` × `Battery revenue per MW`. Titel: `Daily spread explains 94% of battery revenue; negative hours explain 1%`.
Onderrand: `1. 1,000 solar full-load hours assumed for every zone. 2. Two years only; capex is not included. 3. Day-ahead
arbitrage only. 4. Spread and revenue come from the same hourly prices, so part of the 94% is arithmetic.`

## Dashboard 30 versie 2: werkblad "Accuracy is not value" (t80)

`Improvement vs yesterday %` (x) tegen `Revenue gain %` (y), punt per zone, filter Year = 2025, trendlijn.
Titel: `A smaller error does not mean more revenue: the model earns more in all 148 zone-years, but not where its error fell most`.
**Controle** NL 2025: fout 21.7 tegen 23.9 EUR/MWh (9.4% beter), omzet 63.5k tegen 58.7k (+4.8k); mediaan 2025 +3.8k EUR/MW (+10.6%),
nog 8.4k tot perfecte voorkennis.

## Dashboard 27 versie 2: werkblad "Return against CO2" (t81)

`IRR P50` (x) tegen `CO2 per M EUR per year, marginal fossil response` (y), punt per bouwsteen, `Technology` op Vorm, `On the
frontier` op Kleur (teal `1F9E89`, rest warmgrijs `A8A29E`), referentielijn bij 8%. Titel: `Two of 19 building blocks are not
beaten on both return and CO2: solar in Italy and in Bulgaria`. **Controle**: Italy 12.1% / 659 t · Bulgaria 8.1% / 1,420 t;
9 van 28 halen 8% op P50. Voetnoot: `Nine building blocks have no reliable marginal factor and are left out of the frontier.`
