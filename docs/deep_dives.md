# Deep dives: what the tables say when you combine them

*23 November 2026. Reproduce with `PYTHONPATH=src python3 -m eti.verdieping` (tables t77-t81 in `tableau/data_en`); tests in
`tests/test_verdieping.py`. No new sources: every number comes from tables that already feed the dashboards. Method and
limits: `docs/methodology.md`, section "Kruisanalyses". Terms: `docs/concepts.md`, section 13.*

Each dashboard in the series answers one question from one table. The five analyses below join tables to answer the
questions a reader asks next. Every one is a stress test or a description of 2019-2026, not a forecast.

## 1. A PPA is a bet on 2030, not on 2025 (t77; for developers, lenders, corporate buyers)

Dashboard 17 compares a ten-year PPA price with one year of market revenue. Joined with the 2030 stress test of dashboard
26, the picture turns around.

| | Countries (of 19) |
|---|---|
| PPA above the 2025 market | 3 (France, Sweden, Norway) |
| PPA above the 2030 stress-test revenue | 12 |
| Market paid more in 2025, PPA protects by 2030 | 9 (among them Greece and Spain) |
| Market above the PPA in both years | 7 (Italy, Poland, Belgium, Switzerland, Slovakia, Hungary, Netherlands) |
| PPA above the reference LCOE | 2 (Italy, Greece) |

LevelTen offers only: France 63 against 36 (2025) and 15 (2030); Greece 53 against 60 and 24; Spain 33 against 36 and 13;
Italy 61 against 95 and 67.

**What it means.** A seller who signed in Spain or Greece gave up a few euros in 2025 and bought protection against a
fall of more than 20 EUR/MWh. A buyer takes that risk over. And in 17 of 19 countries the PPA price is below the
reference cost of a new plant: the market does not pay for new merchant-free solar at these prices.

**Limits.** 2030 is a stress test at 2025 price levels (targets met, no extra flexibility). In 7 countries it is an
extrapolation beyond the solar share the regression saw, or hits the floor of 0.2. Fifteen of the 19 prices are KYOS
estimates, which run about 25% below LevelTen. LCOE has two reference values. Germany is missing (no 2030 target in t13).

## 2. Solar loses, batteries gain (t78; for portfolio managers and battery investors)

Between 2023 and 2025 the solar capture price fell and day-ahead battery revenue rose in 28 of 37 zones. In the other 9
both fell (the general price level came down). No zone saw solar gain.

| | Median zone |
|---|---|
| Solar capture price, 2023 to 2025 | -19 EUR/MWh |
| Battery revenue (2 hours, 1 cycle a day) | +17k EUR/MW a year |
| Battery MW per solar MW that offsets the loss | 1.3 (middle half of zones: 0.8-1.9) |

Netherlands: solar 71 to 53 EUR/MWh, battery 47k to 61k EUR/MW, ratio 1.3. Greece 1.1, Germany 1.4, Spain 2.0.
Within a zone the capture rate and battery revenue move in opposite directions in 73% of zones (2019-2025).

**What it means.** A fund that holds solar and batteries in the same zone holds a partial hedge: the mechanism that
lowers one raises the other. The ratio says the hedge is not cheap: more than one MW of battery per MW of solar.

**Limits.** 1,000 solar full-load hours for every zone; two years; revenue change only, no capex; day-ahead only.

## 3. What drives battery revenue (t79; for industry and product experts)

259 zone-years, 2019-2025. Share of the differences in battery revenue explained by one indicator:

| Indicator | R2 |
|---|---|
| Daily spread (EUR/MWh) | 0.94 |
| Average price level | 0.49 |
| Midday dip | 0.48 |
| Evening to midday ratio | 0.45 |
| Negative-price hours | 0.01 |

One EUR/MWh of extra daily spread is worth about EUR 405 per MW a year. Serbia, Hungary and Greece earn EUR 16-18k more
than their spread predicts in 2025 (the spread lasts more hours); Finland and northern Sweden earn less.

**What it means.** The headline number "negative-price hours" says nothing about what a battery earns. A siting screen
should start from daily spread. **Limit:** spread and revenue are computed from the same hourly prices, so part of the
94% is arithmetic; the finding is the ranking of indicators, not the 94% itself.

## 4. Forecast accuracy is not forecast value (t80; for data analysts)

The ridge model of dashboard 30 beats "yesterday's prices" on error in 36 of 37 zones in 2025. Measured in money:

| | 2025, median zone |
|---|---|
| Error reduction (MAE) | 16% |
| Extra battery revenue | +3.8k EUR/MW a year (+10.6%) |
| Still left to perfect foresight | 8.4k EUR/MW a year |

The model earns more in all 148 zone-years (2023-2026). But the size of the error reduction and the size of the revenue
gain are unrelated (correlation -0.04). Netherlands 2025: error 21.7 against 23.9 EUR/MWh, revenue 63.5k against 58.7k
of a possible 70.9k EUR/MW.

**What it means.** A battery needs the right order of hours, not the right level of prices. Selecting a model on MAE is
not the same as selecting it on revenue; the next model should be scored on revenue captured.

## 5. Return against avoided CO2 (t81; for impact investors)

The fund simulator has 28 building blocks; 19 have a marginal emission factor.

- Two are on the frontier (no other block is better on both): **solar in Italy** (IRR P50 12.1%, 659 t CO2 per million
  euro a year) and **solar in Bulgaria** (8.1%, 1,420 t).
- 9 of 28 reach 8% at P50: solar in Italy and Bulgaria, and all seven eastern battery blocks.
- Batteries bring return but little CO2: -19 to +145 t per million euro, against 377-1,420 for solar.
- The method drives the impact claim: fossil response gives a median 3 times the avoided CO2 of the domestic method.

**What it means.** Return and impact coincide in few places. A portfolio that wants both leans on southern and eastern
solar for impact and on eastern batteries for return, which is what the "South and east" mix in dashboard 27 does.
**Limit:** nine blocks (Spain, Portugal, the Netherlands, Denmark, Austria, Estonia, France) have no reliable marginal
factor and are left out.

## Data audit, 23 November

All 76 tables were profiled (rows, missing values, duplicates) and cross-checked.

| Check | Result |
|---|---|
| Duplicate rows | none in any table |
| Solar capture price 2025 across t13, t62, t65, t70 | identical to 0.01 EUR/MWh, except Norway (2.1) and Sweden (1.1): zones weighted differently |
| t70 countries | 23; Germany, Bulgaria and Serbia missing (no 2030 target in t13) |
| LCOE in t13 and t70 | two values for all countries (Spain 51.09, the Netherlands 67.39) |
| t64 marginal factors 2025 | 26 of 37 zones reliable |
| t50 KPI row 17 | English copy still said "lowest in Europe"; corrected to "lowest LevelTen country" |

## What to build from this

| Priority | Item | Table | Why |
|---|---|---|---|
| 1 | Worksheet "Return against CO2" on dashboard 27 | t81 | closest to a climate fund's question |
| 2 | Dashboard 37 "A PPA is a bet on 2030" | t77 | completes dashboard 17 |
| 3 | Dashboard 38 "Solar loses, batteries gain" | t78, t79 | the portfolio argument for storage |
| 4 | Worksheet "Accuracy is not value" on dashboard 30 | t80 | shows judgement about model quality |
| 5 | German 2030 target and LCOE per country | t13 | removes the two largest gaps (needs a download) |
