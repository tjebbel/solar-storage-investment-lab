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

## Uuranalyses en nieuwe bronnen (20 november 2026)

**Uurdata (`eti.uurdata`).** Energy-Charts (Fraunhofer ISE) levert per zone en maand de dagmarktprijs en de opwek per type.
Kwartierwaarden (opwek; prijs vanaf oktober 2025) worden uurgemiddelden in lokale tijd (Lissabon voor PT, Helsinki-tijd voor
FI, EE, LV, LT, BG, RO, GR, anders Amsterdam-tijd). Per land-jaar vergelijken we de zon- en totale opwek met OWID/Ember;
onder 60% zondekking vallen zone-jaren uit de zon- en koolstofvrij-analyses. Waar Energy-Charts per zone de landcijfers geeft
(Italië, Denemarken, Noorwegen, Zweden) telt het land één keer.

**Batterij-arbitrage (t55).** Per dag laden in de twee goedkoopste en ontladen in de twee duurste uren, 88% rendement, één cyclus.
Perfecte voorkennis: bovengrens. Vergelijk met t1 (realistisch, plant op de prijzen van gisteren).

**Hirth (t56).** OLS per zone van de maandelijkse capture rate op het maandelijkse zonaandeel van de opwek; 95%-interval uit de
standaardfout. Betrouwbaar als het maximale zonaandeel ≥ 10%, R² ≥ 0,4 en minstens 36 maanden. Beperking: het seizoen zit in de
helling; maand-vaste effecten staan in de backlog.

**Koolstofvrij (t57, t58).** Koolstofvrij = kern, waterkracht (zonder pompverbruik), wind, zon, geothermie, overige hernieuwbaar;
biomassa telt niet mee. Import wordt niet gevolgd.

**Waardeketen (t60).** Omzet en nettowinst 2025 uit jaarverslagen en vakpers (bron per rij in `data/extern/waardeketen_2025.csv`),
6,85 CNY per USD. Nettomarge bevat eenmalige afwaarderingen; brutomarge waar beschikbaar.

**PPA (t61, t62).** LevelTen P25 (aanbiedingen, geen gesloten contracten) per kwartaal; twee kwartalen afgeleid uit de index
(Q3 2026 = 0,86 × 63,64). Pexapark EURO Composite (alle technieken) per maand. PPA tegen markt: P25 Q4 2025 tegen de
capture-prijs zon 2025 uit t1 (Italië: gemiddelde van vier zones). Bekende tegenstrijdigheden staan in de csv (kolom Note).


## Deepening for impact investors and analysts (21 November 2026, dashboards 25-30)

All built from local data; no new downloads. Code in `src/eti/`, tables in `tableau/data_en`, tests in `tests/`.

**25 Marginal vs average CO2 factor (`eti.marginaal`, t63-t64).** Hourly direct emissions from generation by fuel times IPCC
2006 default factors divided by a typical plant efficiency (lignite 0.96, hard coal 0.85, gas 0.40, oil 0.80 t/MWh; waste 0.5
and "Others" 0.6 are assumptions; biomass 0). Two marginal methods give a range: *fossil response* (Siler-Evans et al. 2012:
slope of hourly emission changes on fossil generation changes; assumes a solar MWh displaces a fossil MWh somewhere) and
*domestic* (Hawkes 2010: slope on residual-load changes; counts only the domestic fossil response). Hours with a price at or
below zero get a marginal factor of 0 (renewables are marginal). Batteries: 2-hour, one cycle a day, perfect foresight, net
CO2 = marginal factor at discharge x 0.88 minus at charge. Validation against OWID/Ember (lifecycle, so higher): Germany 0.85,
Poland 0.94. *Reliable* = generation coverage 80-120%, under 10% unclassified output, 0.6-1.2 x OWID. The Netherlands fails
(Energy-Charts books 33% as "Others" and misses most rooftop solar); use the CBS/Ember factor 0.25 for NL.
*Pros:* hourly, transparent, two methods show the real uncertainty. *Cons:* imports/exports are not traced; default factors,
not plant-specific; the fossil-response bound is meaningless where fossil output is tiny (left blank below 10%).

**26 Revenue at risk 2030 (`eti.omzet_risico`, t70).** Capture rate 2030 = 2025 + Hirth slope x (2030 target share - 2025
share), floor 0.2, price level of 2025 held constant to isolate cannibalisation. Range from the slope's 95% interval. Flags:
extrapolated beyond the shares the regression saw (8 of 23 countries), floor hit, target already met (NL, LT).
*Main limitation:* storage and flexible demand flatten the slope as they grow, so this is an upper bound at 2019-2026 flexibility.

**27 Climate fund simulator (`eti.fonds_simulator`, t65-t67).** Solar project cash flows consistent with the LCOE (25 years,
WACC 5%, 85% capital); battery capex 408k EUR/MW for 2 hours (BNEF 2025 turnkey Europe 177 USD/kWh plus 30% balance of plant;
assumption), revenue = perfect-foresight arbitrage x 0.86 (realistic, see 29). 1,000 Monte Carlo draws with common shocks
(price level, solar value decline 0-3%/yr, LCOE, battery revenue, saturation 0-8%/yr, capex). Fund: 100 M EUR, 4-year
deployment, 6-year hold, 2/20 with an 8% hurdle (`eti.lenses.fund_cashflows`). CO2 per M EUR is year 1 on today's grid
(dashboard 14 uses a lifetime average, so lower). *Not investment advice:* a transparent model to make the trade-off visible.
Critical points: (1) battery revenue is day-ahead arbitrage only; in Germany reserve markets can be up to 67% of a 2-hour
battery's income (Capstone, Nov 2025). A sensitivity row with 1.5x revenue lifts the batteries-only portfolio from 5.5% to
16.4% project IRR (12.1% net), so the battery result is a floor and the most assumption-driven number in the dashboard.
(2) The portfolio IRR is a weighted average of project IRRs, not the IRR of pooled cash flows. (3) The fund grows value at the
project IRR and pays out at exit; infrastructure funds distribute yearly. (4) `eti.lenses.fund_cashflows` deducts carry in
year 10 when there is no distribution, which breaks the IRR at high returns; `fonds_simulator.fonds()` deducts it at the last
distribution (identical results below the hurdle). (5) EU ETS reference: 74 EUR/t average 2025, about 90 EUR/t in November 2026.

**28 World duck curve (`eti.wereld_duck`, t68-t69).** Hourly prices from CAISO SP15, ERCOT, AEMO SA1, JEPX and the UK APX
index next to NL and DE, as an index (price / year average) so currencies compare. South Australia's midday price averaged
1% of its year average in 2025 with 30% negative hours; California 33% and 11%; the Netherlands 55% and 6.7%.

**29-30 Battery strategies and forecast baseline (read as floor and ceiling: a real trader bids with a forecast and
re-optimises intraday, so lands in between) (`eti.batterij_realistisch`, t71-t72).** Same battery as t55, traded on
yesterday's prices, last week's prices or a fixed duck schedule. Trading on yesterday's prices captures a median 80% of the
perfect-foresight bound (NL 83%: 59k vs 71k EUR/MW, close to the 61k of the realistic model in dashboard 1); the Baltics only
60%. The same naive forecasts give the error a model must beat: NL 24 EUR/MWh MAE (27% of the average price) in 2025.

### Dashboard 30: voorspelmodel (22 nov 2026)
`eti.voorspelmodel` schat per zone een ridge-regressie (lambda 10, gestandaardiseerde kenmerken) voor de day-ahead-uurprijs.
Kenmerken: prijs van hetzelfde uur gisteren en een week eerder, daggemiddelde en spreiding van gisteren, uur-, weekdag- en
maanddummies, en belasting, restlast, wind en zon van de dag zelf. Backtest met uitbreidend venster: voor testjaar J wordt op
2019 t/m J-1 getraind. Resultaat 2025: het model wint in 36 van 37 zones van "de prijzen van gisteren" (mediaan 19,7 tegen 23,0
EUR/MWh, 16% beter); een batterij die erop handelt haalt 87% van perfecte voorkennis in plaats van 80%.
Kritische punten: (1) belasting, wind en zon zijn gerealiseerde waarden, niet de prognoses van de dag ervoor; daarom staat het
model zonder die kenmerken ernaast (NL 22,6 tegen 21,7 EUR/MWh): het grootste deel van de winst komt uit prijzen en kalender.
(2) Lineair model: geen prijspieken en geen aparte logica voor negatieve prijzen. (3) Noorwegen (Noord) verliest: daar bepaalt
waterkracht de prijs en voegt het model niets toe.

