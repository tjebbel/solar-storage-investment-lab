# Stappenplan woensdag 25 november 2026: nieuwe kostprijs en het Duitse doel doorvoeren

**Wat is veranderd in de data (24 nov, nacht)**
- `t13`: de kostprijs van zon is nu IRENA 2024 (per land voor FR, DE, GR, IT, NL, PL, ES; anders het Europese gemiddelde van
  55,4 EUR/MWh). Nieuwe kolommen: `LCOE own model`, `LCOE previous assumption`, `Target source` en twee extra kosten-per-ton-kolommen.
- `t13`: Duitsland (215 GW), Bulgarije en Servië hebben nu een 2030-doel, omgerekend uit vermogen.
- Doorgerekend in `t50`, `t65`-`t67`, `t70`, `t77`, `t81` en `t92`. Alle 267 tests slagen.
- Terugzetten kan met `git checkout -- tableau/data tableau/data_en src/eti` (zolang je nog niet hebt gecommit).

**Volgorde:** 0 (verversen) · 15 (stond al klaar) · 5 · 26 · 27 · 17 · 14 · 2 · publiceren. Reken op ongeveer anderhalf uur.

## 0. Verversen (één keer)
1. Open de werkmap. Menu **Gegevens** → per bron **Vernieuwen** (of Cmd+R op een blad van die bron) voor:
   `t13_kostencurve`, `t50_kpi_dashboards`, `t65_fund_assets`, `t66_fund_draws`, `t67_fund_portfolios`, `t70_revenue_at_risk`,
   `t77_ppa_vs_2030`, `t81_impact_frontier`, `t82_cost_of_capital`, `t27_impact`, `t10_dekking_nl`.
2. Controleer dat `t50` naar `tableau/data_en` wijst (anders worden de KPI-teksten Nederlands).
3. Klik vóór het publiceren op een lege plek, zodat er geen selectie wordt opgeslagen.

## 1. Dashboard 15 (Global South)
Zoals gisteren afgesproken: titel `penalty`, subtitel `capital`, onderrand punt 2 en 5, alias `Viet Nam` → `Vietnam`,
magenta (`C4457A`) voor Malaysia en Thailand. Zie `STAPPENPLAN_EN.md`, sectie dashboard 15.

## 2. Dashboard 5 (Abatement cost curve)
**KPI-rij** (komt vanzelf uit `t50`; controleer kleuren): `11 of 26` (teal `1F9E89`) · `140 Mt CO2/yr` (warmgrijs `A8A29E`) ·
`Italy: -96 EUR/t` (teal) · Netherlands `-36 EUR/t` (**nu teal**, was magenta).

1. **Cost curve**: titel wordt `Solar abates CO2 at a profit in 11 of 26 countries`.
   Subtitel: `Width = extra solar to 2030 targets (Mt CO2/yr); height = cost per tonne at IRENA 2024 project costs; switch the emission factor top right`.
   **Controle Marginal:** totaal 139,7 Mt. Van links: Italy -96 (21,2 Mt) · Greece -48 · Bulgaria -45 · Croatia -35 · Slovenia -26 ·
   Romania -23 · Hungary -18. **Germany +22 (36,7 Mt) is nu de breedste balk**, daarna Spain +32 (30,1 Mt). Rechts: France +75, Sweden +85.
   Nederland heeft potentieel 0 en staat niet in de curve.
   **Controle Average:** totaal 76,5 Mt; Italy -135; Sweden 966, Norway 875, France 725.
2. **Margin per country**: titel blijft. **Controle:** Italy +38,5 · Greece +19,4 · Bulgaria +17,9 · **Netherlands +14,2** ·
   Croatia +14,0 · Slovenia +10,5 · Serbia +9,2 · Romania +9,0 · Hungary +7,1 · Switzerland +4,9 · Slovakia +1,4 (11 positief) ·
   Germany -8,8 · Spain -12,9 · France -29,9 · Sweden -34,2. De oranje balk van Nederland staat nu aan de positieve kant.
3. **Nieuw werkblad `costrange`** (de bandbreedte): `Country` op Rijen; **Meetwaarden** op Kolommen met
   `Cost per tonne own model (marginal factor)`, `Cost per tonne (marginal factor)` en `Cost per tonne previous assumption (marginal factor)`;
   markering Cirkel; `Meetwaardenamen` op Kleur: own model lichtgrijs `D6D3D1`, IRENA teal `1F9E89`, previous assumption middengrijs `78716C`;
   referentieband per cel van minimum tot maximum (lichtgrijs); referentielijn op 0; sorteer op de IRENA-waarde.
   Titel: `The answer depends on the cost assumption: solar abates at a profit in 20, 11 or 7 of 26 countries`
   Subtitel: `Cost per tonne at three solar cost levels: own model (floor), IRENA 2024 projects (used here) and the previous two-value assumption`.
   **Controle:** onder nul in 20 landen (own model), 11 (IRENA), 7 (previous). Netherlands: -33 / -36 / +35. Germany: -7 / +22 / +53.
4. **Tekstvak:** vervang de laatste zin door `That choice nearly doubles the potential (76 vs 140 Mt).`
5. **Onderrand:** vervang het punt over de kostprijs door
   `LCOE: IRENA 2024 project costs, per country for seven countries, otherwise the European average (55 EUR/MWh); see the range chart.`
   en voeg toe: `Germany, Bulgaria and Serbia: capacity target converted with the 2025 yield; targets are not forecasts (Germany: 215 GW by law).`

## 3. Dashboard 26 (Revenue at risk 2030)
**KPI-rij:** `22 EUR/MWh` (magenta `C4457A`) · **`Germany: 5.1 bn EUR/yr`** (magenta; was Spain 3.2) · Italy `capture rate 0.58` (teal;
referentie nu `5 of 26 countries stay above LCOE in 2030`) · `9 of 26 countries` (warmgrijs; was 8 of 23).

1. **Hoofdgrafiek:** titel blijft (`... a median 22 EUR/MWh ...`). Er staan drie landen bij: Germany 28, Bulgaria 4, Serbia 0.
   **Controle:** Croatia 48 · Romania 40 · Denmark 36 · Greece 36 · Germany 28 · Italy 28 · Spain 23 · Netherlands 0.
2. **Capture rate 2025 → 2030:** Germany 0,52 → 0,20 (raakt de vloer). Vijf landen raken de vloer.
3. **Euros at stake:** **Controle:** Germany 5.118 · Spain 3.186 · Italy 2.688 · France 1.372 · Denmark 876. Past de titel van dit
   blad een land noemen, zet dan Germany in plaats van Spain.
4. **Above LCOE?:** nu vijf landen erboven: Italy (67 tegen 56), Bulgaria (69 / 55), Serbia (65 / 55), Switzerland (57 / 55),
   Netherlands (53 / 39). Een titel als "only Italy" wordt:
   `Five of 26 countries would still earn more than solar costs in 2030`.
5. **Onderrand:** `Eight countries` → `Nine countries`; voeg toe: `LCOE: IRENA 2024. Germany's 2030 target is the legal 215 GW, not a forecast.`

## 4. Dashboard 27 (Climate fund simulator)
**KPI-rij:** `7.3%` (teal; was 7.5) · `4.4%` (magenta; was 4.6) · `3-9x` (warmgrijs) · `43%` (warmgrijs; was 45).

1. **Histogram** (Balanced, 25/25/25/25): **Controle** P10 -0,1% · P50 4,7% · P90 9,5% · 19% boven 8% (was 4,2% en 15%).
   Zet hier meteen de referentielijn op 8% in (stond nog open).
2. **Return vs impact:** de oude titel `Batteries in the east earn most; solar avoids most CO2 per euro` klopt nog.
   **Controle gemiddelden:** Battery East 9,5% · Solar South 5,2% · Solar North 2,9% · Battery West 1,5%;
   CO2: Solar South 882 · Solar North 727 · Battery West 135 · Battery East 36.
3. **Five portfolios:** **Controle:** South and east 7,3% / net 4,4% / TVPI 1,27 · North and west 2,2% / -1,0% · Balanced 4,7% / 1,7% ·
   Solar only 4,1% / 1,1% / 160-805 t · Batteries only 5,5% / 2,5% / 54-86 t · met reservemarkten 16,4% / 12,1%.
4. **Return against CO2** (t81): titel wordt
   `Three building blocks are not beaten on both return and CO2: solar in Italy, Greece and Bulgaria`.
   **Controle:** Italy 10,6% / 598 t · Greece 8,5% / 785 t · Bulgaria 7,0% / 1.309 t; 9 van 28 halen 8%.
5. **Onderrand:** `LCOE: IRENA 2024 per country (was two reference values).`

## 5. Dashboard 17 (PPA), werkblad `ppa2030`
1. Titel: `In 13 of 22 countries the PPA price is above what solar would earn in 2030`.
2. **Controle:** er staan drie landen bij (Germany, Bulgaria, Serbia). Germany 50 / 46 / 18 · France 63 / 36 / 15 ·
   Greece 53 / 60 / 24 · Spain 33 / 36 / 13 · Italy 61 / 95 / 67 · Netherlands 34 / 53 / 53.
   Drie groepen: 4 · 9 · 9 (was 3 · 9 · 7).
3. Blad met `PPA minus LCOE` (als het erin zit): alleen Greece +12,1 en Italy +4,4 boven nul; titel `Only Greece and Italy ...`.
4. **Onderrand:** `In 7 countries` → `In 8 countries`; `15 of 19` → `17 of 22`; schrap `Germany is missing`;
   `LCOE has two reference values` → `LCOE: IRENA 2024`.
5. De dashboardtitel van 17 noemt `12 of 19`: maak daar `13 of 22` van.

## 6. Dashboard 14 (Impact investor): de twee kostprijzen naast elkaar
Dashboard 14 blijft op het studiemodel (Nederland 67 EUR/MWh, PBL-referentieproject): daar hangen ook de ton CO2 per miljoen
euro en de vergelijking met India aan. De IRENA-waarde staat er nu naast, zodat 5 en 14 elkaar niet meer tegenspreken.
1. **KPI 14, tweede tegel** (komt uit `t50`): `-14 EUR/MWh`, vergelijking `at IRENA 2024 project cost: +14 EUR/MWh`,
   referentie `PBL reference project; additionality depends on the cost basis`. **Kleur wordt warmgrijs `A8A29E`** (was magenta).
2. Staat er een blad met `Solar margin EUR/MWh` per regio: sleep `Solar margin at IRENA cost EUR/MWh` ernaast (Meetwaarden,
   twee staven per regio; studiemodel middengrijs `78716C`, IRENA teal `1F9E89`). **Controle:** Netherlands -14,0 en +14,2 ·
   Europe (Spain) -15,0 en -12,9. Alleen deze twee regio's hebben een marktprijs.
3. **Onderrand dashboard 14**, extra punt:
   `Dutch LCOE: 67 EUR/MWh is a PBL reference project (740 full-load hours); projects built in 2024 measured 39 EUR/MWh (IRENA). The margin flips from -14 to +14 EUR/MWh.`

## 6b. Dashboard 2 (Signals Netherlands): derde scenario in de dekkingsgrafiek
Dashboard 1 gebruikt sinds 24 november geen kostprijs meer (de dekkingsgrafiek is daar weggehaald; de KPI's zijn marktcijfers).
De kostprijs zit in dashboard 2. `t10` heeft nu drie scenario's: `LCOE 2025 (67.39)`, `LCOE 2030 (50.54)` en nieuw
`LCOE 2024 IRENA (39.22)`.
1. **KPI 2, eerste tegel** (uit `t50`): `6 of 11`, referentie wordt `LCOE 2025: 67.39 EUR/MWh; IRENA 2024: 11 of 11`. Kleur blijft teal.
2. **Dekkingsgrafiek** (gestapelde staaf per jaar): staat `Scenario` op Filter, vink dan ook `LCOE 2024 IRENA (39.22)` aan en zet
   `Scenario` op Kolommen vóór `Year`, zodat de drie scenario's naast elkaar staan. Kleuren blijven: Covered teal `1F9E89`,
   Tight oranje `E39A2D`, Costs not covered magenta `C4457A`.
   **Controle 2025:** studiemodel 5 gedekt · 0 krap · 7 niet; IRENA 9 · 1 · 2. **Controle 2026 (11 maanden):** 6 · 0 · 5 tegen 11 · 0 · 0.
   **Controle 2020:** in alle drie de scenario's vrijwel niets gedekt (0, 0 en 1 maand).
3. Titel van de grafiek, als die de kostprijs noemt:
   `Dutch solar covered its cost in 6 of 11 months of 2026 at the PBL reference cost, and in all 11 at measured 2024 project cost`
   Subtitel: `Months per year in which the solar capture price is above cost; three cost levels`.
4. **Onderrand**, extra punt:
   `Cost levels: 67 and 51 EUR/MWh are a PBL reference project (740 full-load hours, 2025 and 2030); 39 EUR/MWh is what IRENA measured for Dutch projects built in 2024.`

## 7. Publiceren en melden
Publiceer en stuur de links van `GlobalSouth`, `costcurve`, het tabblad van 26, `fundsim`, `PPA`, `impact` en het tabblad van dashboard 2.
Ik controleer elk dashboard live, leg de scores vast en werk daarna de overige documenten bij (`STAPPENPLAN_VOLLEDIG.md`,
`teksten_en.md`, `deep_dives.md` en het weekplan noemen nog de oude getallen).
