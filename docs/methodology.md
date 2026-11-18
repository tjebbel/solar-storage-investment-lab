# Methodology and limitations

## Question
Should an investor add a 10 MW / 20 MWh battery to a 20 MW solar park in the Netherlands,
and what does that do to return, risk and avoided emissions?

## Data
* Hourly day-ahead prices and generation by technology. The repository ships a **synthetic**
  year (`eti.data.synthetic_year`) so that everything runs offline and in CI.
* `eti.live` downloads real Dutch day-ahead prices and generation from the Energy-Charts API
  (`make run-live YEAR=2025`), averages 15-minute values to hours and maps technologies. Parsers are
  tested offline with fixtures shaped like the documented API responses.
* `eti.data.parse_entsoe_xml` reads ENTSO-E day-ahead documents (tested on `data/sample`).
  Use it to replace the synthetic year with real data. Since delivery day 1 October 2025 the
  day-ahead market settles in 15-minute periods; aggregate to hours or adapt the battery model.

## Methods
* **Capture rate** = generation-weighted price / average price (missing prices excluded).
* **Cannibalisation**: least-squares slope of price on national solar output.
* **Solar project**: national solar profile scaled to 20 MW × 1,000 full-load hours; revenue at
  hourly prices; NPV, IRR (bisection), LCOE, sculpted debt capacity at a DSCR target.
* **Risk**: Monte Carlo on yearly revenue (normal, sd 15%), P10/P50/P90 IRR and probability
  below the hurdle rate.
* **Battery**: one cycle per day, best charge/discharge blocks with perfect foresight, O(n)
  per day. This is an **upper bound** for arbitrage, and excludes ancillary services
  (FCR, aFRR), imbalance and intraday revenues. The model reports the extra revenue per MW
  that would be needed to reach the hurdle rate.
* **Avoided emissions**: generation × hourly grid emission factor (from the generation mix),
  compared with a yearly-average factor. Battery effect: discharge × factor × efficiency minus
  charge × factor. Avoided emissions are reported separately from Scope 1–3.

## Limitations
Synthetic prices; average (not marginal) emission factors; no taxes, inflation, grid fees,
SDE++ or PPA structures; constant capex and opex. All assumptions live in `src/eti/config.py`.


## Editie 2 (november 2026): geverifieerde aannames

| Input | Waarde | Bron |
|---|---|---|
| Vollasturen zon NL | 740 | PBL, Eindadvies SCE 2025, grondgebonden zon-PV |
| Capex / O&M zon NL | EUR 449/kWp, EUR 15,7/kWp/jaar | idem |
| Vennootschapsbelasting | 25,8% | NL toptarief; lineaire afschrijving |
| Netintensiteit | NL 263, VS 384, China 560, India 708, Spanje ~100 g/kWh | Electricity Maps, Ember 2024, REE 2024 |
| Capex VS / India / Spanje / China | USD 1,69/W-AC; USD 525/kW; EUR 0,70/W; CNY 2,06-3,30/W | LBNL 2026, IRENA 2024, IEA PVPS, EPC-biedingen 2024 |
| Kapitaalkosten | geavanceerd 4-6%, opkomend 10-15% | IEA Cost of Capital Observatory, CPI |

Batterij: naast de bovengrens met perfecte voorkennis wordt een realistische variant berekend die plant op de prijzen van gisteren.
Vermeden CO2 per regio gebruikt een netfactor die lineair daalt naar 10% van vandaag in 2050.
