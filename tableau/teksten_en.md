# English texts for the Tableau dashboards

Copy these into the English workbook (`tableau/Solar_storage_Europe_EN.twbx`). Data: `tableau/data_en/` (same file and
column names as `tableau/data/`, English values). Field names: rename once with `tableau/veldnamen_en.csv`.
Number format: decimal point, thousands comma (data source locale *English (United States)*).

## Dashboard 1 "First findings"
- Title: `Solar and storage in Europe: first findings`
- Subtitle: `37 bidding zones, 2019 to 15 November 2026. Sources: Energy-Charts, Ember, ENTSO-E, FRED. Code: github.com/tjebbel/solar-storage-investment-lab`
- KPI row: `Key figures for the Netherlands` (tiles from t47: Battery revenue, Solar capture rate, Average price, Negative hours, Daily spread)
- Map: `Where is solar worth least? Solar capture rate 2025` · subtitle `No data for the UK, Ireland and the Balkans` · legend `Solar capture rate (1.00 = average hour)`
- Ranking: `Top and bottom five zones`
- Lines: `Solar is losing value everywhere: average capture rate per region, 2019-2026` · subtitle `2026: to 15 November. Romania 2021: incomplete year. Unweighted average of zones in a region.` · reference line `solar worth as much as the average hour`
- Battery: `What may a battery cost for an 8% return?` · subtitle `Day-ahead alone works without grid charges, not with them. Reserve markets (FCR, aFRR) add room while those capacity markets keep paying. More cycles do not help: the battery wears out faster.` · reference line `280 EUR/kWh: market price today` · legend `Feasible at market price 280 EUR/kWh`
- Price rise: `Price rise Jan-Oct 2026 vs 2025: three quarters is gas` · subtitle `Model per zone and month on 2019-2025. 'Unexplained' includes low reservoir levels (Norway), the CO2 price and the windless week. Average over zones.`
- Segments: `From flat prices to battery markets and solar saturation: zones per segment, 2019-2026` · subtitle `In 2023-2025, 16 to 23 of the 37 zones are borderline (segment changes if thresholds move 20%). The Netherlands in 2025 too.`
- Box "What we do not know for sure": `1. Segment thresholds are a choice; many zones sit on the border. 2. Dutch capture rate: utility-scale (0.62) or rooftop (0.52). 3. aFRR price: only two data points (2022, 2026).`
- Box "What comes next": `Next: dashboard 2 (does solar cover its cost, month by month) · 4 (how fast solar gets cheaper) · 8 (grid congestion and the end of net metering) · 14 (return against avoided CO2).`

## Dashboard 2 "Signals Netherlands"
- Title: `Signals for the Netherlands: autumn 2026 is a price shock`
- Subtitle: `Same rules as the DAX measures and Python; 66 of 66 values checked. Source: Energy-Charts. 2026 to 15 November.`
- KPI row: from t50, Dashboard = 2 (`Months costs covered`, `Dutch solar capture rate`, `Dutch average price`, `Price signal, latest month`)
- Signals table: `Month by month: price, solar capture price, margin and signal` · axis `Margin = solar capture price minus LCOE (EUR/MWh)`
- Shocks: `Price shocks per zone and month, 2020-2026` · subtitle `Shock = price more than 3 standard deviations above the previous twelve months. 2026 to 15 November.`
- Coverage: `In how many months does solar cover its cost? Netherlands`
- Cannibalisation: `The more solar, the less each MWh of solar is worth` · tooltip `Good news for buyers of power (lower midday prices), bad news for solar builders.`
- Parameter note: `Margin = solar capture price minus the cost of solar power (LCOE). The z-score compares the month with the previous twelve months.`
- Context: `Solar supplied 21% of Dutch electricity in 2025 (CBS, provisional; Ember: 28.5 TWh vs CBS 25.8 TWh).`
- Event note: `From 1 January 2027 Dutch net metering ends: home batteries and self-consumption become more important.`
- What comes next: `Next: dashboard 8 (end of net metering, grid congestion) · 13 (flexibility) · 16 (duck-curve atlas).`

## Dashboard 3 "Nuclear in Europe and the world"
- Title: `Solar catches up with nuclear: world 2025, 2,807 vs 2,805 TWh`
- Subtitle: `Ember 2000-2025. Europe still gets more than twice as much power from nuclear as from solar, but nuclear keeps its market value (1.03) and solar does not (0.61).`
- KPI row: from t50, Dashboard = 3
- Course per country: `Nuclear trajectory per country, 2015-2025` · note `The trajectory is a rule (at least 10% and 2 TWh), not a policy judgement.`
- Clean with nuclear: `Clean with nuclear? Nuclear share vs CO2 intensity, 2025`
- Market value: `Market value: nuclear keeps its value, solar does not` · reference line `worth as much as the average hour` · subtitle `14 European countries, weighted by nuclear output per zone; 2026 to 15 November.`
- One GW is not one GW: `Matching US nuclear output takes over 4x as much solar capacity`
- Two sides: `Per MWh solar is cheaper; per available hour nuclear delivers more. System costs (storage, grid) and build risk (delays, overruns) decide who is right.`
- Netherlands box: `The Dutch government wants at least four nuclear plants; a first plant in 2035 is no longer realistic according to the minister; investment EUR 20-30 billion excluding financing; decision on plants 3 and 4 around 2028.`
- Limitations: `Ukraine has no 2025 figure; Belgium's capacity in Ember does not add up.`
- What comes next: `Next: dashboard 8 (Dutch nuclear plans) · 9 (EU) · 11 (China) · 20 (hourly carbon-free power).`

## Dashboard 4 "Experience curve and portfolio"
- Title: `Where is solar getting cheaper, and where does capital earn?`
- Subtitle: `In the tradition of BCG: experience curve (Henderson 1968) and an adapted growth-share matrix (Henderson 1970). x-axis = battery revenue vs the median, not market share.`
- KPI row: from t50, Dashboard = 4
- Experience curve: `35% cheaper per doubling (95%: 21-46%)` · subtitle `Export value of Chinese panels, not a factory price; 2017-2025; the 2021-2022 peak is due to polysilicon.`
- Variants: `The 35% does not depend on the crisis years or the overcapacity`
- Portfolio 2025: `Portfolio 2025: Bulgaria, Lithuania, Poland and Romania are the stars` · reference lines `median battery revenue`, `median growth 2021-2025`
- 2022 to 2025: `From 2022 to 2025: the Netherlands moved from star to dog` · tooltip: field `Explanation` (t46)
- Caveats: `(a) The BCG matrix is meant for product portfolios; here it is applied to countries. (b) Trade measures against Chinese panels and forced-labour risk in the polysilicon chain fall outside the matrix but are a due-diligence point for investors.` · US: `US: 31 GW of new solar in 2024, 30 GW in 2025 (EIA-860M, AC).`
- What comes next: `Next: dashboard 5 (abatement cost curve) · 6 (profit pool) · 18 (storage market saturation) · 21 (commodities as predictor).`

## Dashboard 7 "Control matrix and risk map"
- Title: `Can you trust these figures? 21 controls, 6 still open`
- Subtitle: `In the tradition of the Big Four (COSO, ISAE 3000). A readiness assessment, not an assurance opinion.`
- KPI row: from t50, Dashboard = 7
- Data flow: image `docs/img/keten.png`
- Matrix: `Control matrix` · Status bar: `Status at a glance` · Risk map: `Risk map: likelihood x impact`
- Rules box: `Omnibus I (EU 2026/470): the reasonable-assurance requirement was dropped; only limited assurance remains. Far fewer companies fall under the CSRD. Investors still want verifiable figures.`
- Avoided CO2 box: `Avoided emissions (CBS) are not an emission reduction: do not net them off scope 1-3 (GHG Protocol).`
- What comes next: `Next: C04 (Power BI), C10 (cross-border flows), C13 (CBS vs Ember), C15 (status codes), C20 (TenneT queue).`

## Dashboards 5, 8-11, 13-15 (English only, 19 November)
Titles, KPI checks and chart plans: `tableau/STAPPENPLAN_EN.md`. KPI tiles: t50 with filter Dashboard = 5, 8, 9, 10, 11, 13, 14 or 15.

- **5 Abatement cost curve**: `Solar abates CO2 at a profit in 7 of 26 countries` · subtitle `In the tradition of McKinsey's cost curve. Width = abatement potential to 2030, height = cost per tonne. 2025 capture prices; average grid emission factor (toggle: marginal, gas).`
- **8 Netherlands**: `Dutch solar hits the grid wall: 8 GW waits for offtake` · subtitle `CBS, netbeheerders' capacity map 2026, Energy-Charts. 2026 to 15 November.` · event `From 1 January 2027 Dutch net metering ends: home batteries and self-consumption become more important.`
- **9 European Union**: `One market, 37 prices: the spread is twice the 2019 level` · subtitle `Monthly day-ahead price per bidding zone; band = 10th to 90th percentile.`
- **10 United States**: `US batteries grew 2.5 times in two years: 56 GW, another 23 GW under construction` · subtitle `EIA-860M, utility scale (AC), to September 2026. OBBBA signed 4 July 2025.`
- **11 China**: `China ships a quarter of a terawatt of panels a year at 11 cents a watt` · subtitle `Customs export data (Ember), 2017 to September 2026. Document 136: new projects via the market from 1 June 2025.`
- **13 Grid operator**: `Flexibility is worth money: 584 negative hours and imbalance spikes above 500 EUR/MWh` · subtitle `Netherlands, 2025; EV demand is an assumption based on IEA fleet data.`
- **14 Impact investor**: `Where a euro buys the most CO2: six times more in India than in the Netherlands` · subtitle `Solar, tonnes of CO2 avoided per million EUR invested per year. Avoided emissions are not an emission reduction.`
- **15 Global South**: `Twice the sun, but capital at 12%: India's solar would be 38% cheaper at Dutch financing costs` · subtitle `PVGIS 11-year averages; WACC from the IEA Cost of Capital Observatory.`
