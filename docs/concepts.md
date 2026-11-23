# Concepts explained

A plain-language guide to every idea used in this project, from first principles. Each section ends
with where it lives in the code.

## 1. Power and energy
* **Power** (kW, MW, GW) is the *rate* of producing or using electricity. **Energy** (kWh, MWh, TWh) is
  power × time. 2 MW for 15 minutes is 0.5 MWh.
* **Capacity factor** = actual energy / (capacity × 8,760 h). A Dutch solar park is around 10–12%,
  offshore wind around 45–55%, a nuclear plant above 90%.
* Code: `eti.config` (full-load hours), `exercises/solutions.py` (E01–E02).

## 2. How the power price is set
* **Merit order**: plants are dispatched from cheapest to most expensive marginal cost (sun, wind,
  nuclear, then coal, then gas). The *last* plant needed sets the price for everybody: **marginal pricing**.
* **Day-ahead market**: a daily European auction (SDAC) for each period of the next day. Since delivery
  day 1 October 2025 the periods are 15 minutes instead of one hour; this project averages them to hours.
* **Negative prices** happen when supply exceeds demand and some producers keep running anyway
  (subsidies per MWh, inflexible plants, contracts).
* Code: `eti.data`, `eti.live`, `eti.market`.

## 3. Cannibalisation and the capture rate
* Solar parks all produce at the same time, which pushes down the price in exactly those hours.
* **Capture price** = Σ(generation × price) / Σ generation: what one MWh of solar actually earned.
* **Capture rate** = capture price / average price. Below 1.0 means solar sells at a discount.
* The **duck curve** is the daily price (or net-load) shape with a midday dip that deepens as solar grows.
* **Regression**: the slope of price on national solar output estimates the euro-per-MWh price drop per
  extra GWh of solar; R² is the share of price variation explained by solar alone.
* Code: `market.capture_rate`, `market.ols`, figures `capture_rate.png`, `duck_curve.png`, `cannibalisation.png`.

## 4. Investment metrics
* **Cash flows**: capex up front (negative), then yearly revenue minus opex.
* **NPV** (net present value): cash flows discounted to today at a required return. NPV > 0 creates value.
* **IRR** (internal rate of return): the discount rate at which NPV = 0. Found by bisection (binary search).
* **Hurdle rate**: the minimum IRR an investor accepts for this risk.
* **LCOE** (levelised cost of electricity): discounted lifetime costs / discounted lifetime MWh, the
  break-even price. Compare it with the *capture* price, not the average price.
* **Nominal vs real**: (1 + nominal) = (1 + real) × (1 + inflation). Never mix them.
* Code: `eti.finance`.

## 5. Risk
* **Monte Carlo**: run the model thousands of times with uncertain inputs (here: revenue ±15%).
* **P10 / P50 / P90**: 10%, 50% and 90% of outcomes lie below these values. Banks lend against
  conservative cases (P90 production).
* **Probability below hurdle**: the share of simulations with IRR below the hurdle rate.
* **Tornado chart**: change one input at a time and rank inputs by their effect on IRR.
* Code: `finance.monte_carlo_irr`, `pipeline` (sensitivity), figures `irr_distribution.png`, `tornado.png`.

## 6. Debt (project finance)
* **CFADS**: cash flow available for debt service. **DSCR** = CFADS / (interest + repayment).
* **Sculpting**: repayments follow the cash flow so the DSCR equals the bank's target every year; the
  maximum loan is the present value of CFADS / DSCR at the loan rate. **Gearing** = debt / capex.
* Code: `finance.max_debt`.

## 7. Batteries
* A **10 MW / 20 MWh** battery delivers 10 MW for 2 hours. **C-rate** = power / energy = 0.5C.
* **Round-trip efficiency** (~85–90%): energy lost between charging and discharging.
* **Arbitrage**: charge cheap, discharge expensive. This model finds the best charge and discharge blocks
  per day in O(n) with perfect foresight: an **upper bound**.
* **Revenue stack**: arbitrage, ancillary services (FCR, aFRR, mFRR), imbalance, congestion contracts.
  The model reports the extra revenue per MW needed to reach the hurdle rate.
* **Grid tariffs**: when a battery pays transport tariffs on both charging and discharging, the margin per
  cycle shrinks twice (exercise E26). This is a key reason why Dutch merchant batteries are hard to finance.
* Code: `eti.battery`, figure `battery_day.png`.

## 8. Emissions and impact
* **Emission factor**: kg CO₂ per MWh. The grid factor changes every hour with the generation mix.
* **Average vs hourly vs marginal**: a yearly average ignores *when* a plant produces. Solar produces when
  the grid is already cleanest, so an average factor overstates its avoided emissions. A marginal factor
  (the plant that actually ramps down) is better still; this project uses hourly *average* factors as a
  transparent middle ground.
* **Avoided emissions** are reported separately from Scope 1–3 (GHG Protocol); they may not be netted.
* **24/7 carbon-free energy (CFE)**: matching consumption with clean supply *every hour*, stricter than
  matching the yearly total with certificates (exercise E21).
* Biomass and waste are simplified here; real accounting treats biogenic CO₂ separately.
* Code: `eti.esg`, figure `co2_methods.png`.

## 9. Data engineering
* **UTC** for storage and keys, local time for display (daylight-saving days have 23 or 25 hours).
* **Star schema**: facts (prices, generation) with dimensions (technology). **Idempotent upserts**: rerunning
  a load never creates duplicates. **Fixtures**: recorded API-shaped files that let tests run offline.
* Code: `eti.warehouse`, `eti.live`, `tests/`.

## 10. Data sources and licences
* Energy-Charts (Fraunhofer ISE) provides an open API; most data is CC BY 4.0 with attribution. Price data
  originates from the exchange and may carry the original provider's terms: fetch at runtime, publish only
  your own aggregates and charts, with attribution.
* ENTSO-E Transparency Platform: free with a personal token (`ENTSOE_TOKEN`).

## 11. Added 20 November 2026 (dashboards 6 and 16-20)

**Duck curve and midday dip.** When a lot of solar produces at the same time, the midday price falls and the evening price
(when the sun is gone and gas sets the price) stays high. We measure the *midday dip* as the day-average price minus the
average 11:00-15:00 price. Example: the Netherlands, 2025: day average 87, midday 48, so the dip is 39 EUR/MWh; the evening
price (126) is 2.6 times the midday price. In 2023 the dip was 25. All 37 zones had a deeper dip in 2025 than in 2023.

**Battery arbitrage with perfect foresight.** A 2-hour battery charges in the two cheapest hours of the day and discharges in
the two most expensive ones (88% round-trip efficiency, one cycle per day). Because it "knows" tomorrow's prices, this is an
*upper bound*: real traders earn less. Our realistic model (t1) gives 61k EUR/MW for the Netherlands in 2025, the upper bound
gives 71k. The gap (about 15%) is the price of forecast errors.

**Hirth replication.** Hirth (2013) showed that the market value of solar falls as its share grows. We regress the monthly
solar capture rate on the monthly solar share of generation, per zone. A slope of -0.020 means: every extra percentage point of
solar lowers the capture rate by 0.02. Monthly data mixes in the season (more sun and lower prices in summer), so the slope is
steeper than the yearly estimate (-0.011 in t43). Both are shown, with the reason.

**Coverage check.** Energy-Charts gets generation from ENTSO-E. For some countries most rooftop solar is missing (the
Netherlands: 2% of the solar that Ember/OWID reports). Before using solar or carbon-free figures we compare each country with
OWID; below 60% the zone is left out of those analyses. Price-only analyses (dip, battery) stay.

**Carbon-free share and 24/7 matching.** Carbon-free = nuclear, hydro, wind, solar, geothermal (biomass is left out to stay
conservative). An *annual* certificate can claim 100% green power even if many hours are fossil; *hourly* (24/7) matching asks
whether each hour is covered. We show the share of hours below 50% carbon-free: in the median zone 21% in 2025, down from 36%
in 2019.

**PPA (power purchase agreement).** A long contract (often 10 years) at a fixed price per MWh. *P25* is the 25th percentile of
offers, i.e. a competitive price. A *pay-as-produced* solar PPA pays for each MWh produced, so the buyer takes over the
cannibalisation risk; that is why solar PPAs are cheaper than wind or baseload PPAs. A *hybrid* PPA (solar plus battery) was 24%
more expensive than solar-only in Q2 2026 because it also delivers in the evening.

**Profit pool (Bain).** Where in the value chain is money made? Revenue times margin per segment. In 2025 Chinese polysilicon,
wafer and module makers lost money (net margins -7% to -32%), while inverter and storage makers (Sungrow 15%, Enphase 12%) and
a protected US module maker (First Solar 29%, including tax credits) were profitable. Net margin includes one-off impairments;
gross margin shows the operating picture.


## 12. Added 21 November 2026 (dashboards 25-30)

- **Average emission factor (AEF):** total CO2 divided by total generation in an hour or year. Good for reporting a footprint.
- **Marginal emission factor (MEF):** the CO2 change when demand or supply changes by one MWh. Good for *decisions*: what an
  extra solar MWh or a battery cycle really changes. Example: Germany 2025, solar hours: AEF 0.18 t/MWh, MEF 0.15-0.56.
- **Fossil response vs domestic method:** two ways to estimate the MEF; the first assumes a fossil plant somewhere backs off,
  the second counts only domestic plants. The truth in a connected grid lies in between.
- **Monte Carlo simulation:** run a model a thousand times with random but plausible inputs; read the result as a range
  (P10-P50-P90) instead of one number.
- **Project IRR vs fund net IRR:** the project return before the fund's costs, and what the investor (LP) keeps after the
  management fee, carry and the time money waits to be invested. Example: 7.5% project, 4.6% net.
- **TVPI and J-curve:** total value paid back per euro paid in; the early years of a fund are negative (fees, no exits yet).
- **Revenue at risk:** the euros per MWh a project would lose if a country's solar target is met and nothing else changes.
- **Perfect foresight vs forecast capture:** the upper bound for a battery that knows tomorrow's prices, and the share of it a
  real strategy captures (80% with yesterday's prices).
- **MAE (mean absolute error):** the average size of a forecast error, in EUR/MWh; a model is only useful if it beats a naive
  baseline such as "same hour yesterday".

## 13. Added 23 November 2026 (dashboard 17 and the deep dives, t76-t81)

- **P25 offer vs P25-equivalent estimate:** LevelTen's P25 is the 25th percentile of real offers on its marketplace. KYOS
  publishes a model estimate of the same quantity for 2026-2035 with a 20% risk discount. Where both exist KYOS is about 72%
  of LevelTen, so the two are never mixed in one claim: solid marks and dark bars are offers, open marks and light bars estimates.
- **PPA against the future, not the past:** a PPA fixes a price for about ten years. Comparing it with one past year's
  capture price answers "was it worth it"; comparing it with the 2030 stress test answers "what does it protect against".
- **Natural hedge and hedge ratio:** when solar's capture price falls, daily spreads widen and battery revenue rises. The
  hedge ratio is the MW of battery per MW of solar whose extra revenue offsets the solar loss. Example 2023-2025, median
  zone: solar lost 19 EUR/MWh, a battery gained 17k EUR/MW, ratio 1.3 at 1,000 full-load hours.
- **R-squared (R2):** the share of the differences in one number that another number explains. Daily spread explains 94% of
  battery revenue between zones and years; the count of negative-price hours explains 1%.
- **Value of a forecast:** what a better forecast earns, not how much smaller its error is. The two are different things:
  across 148 zone-years the error reduction and the extra battery revenue are uncorrelated (-0.04).
- **Pareto frontier:** the options that no other option beats on both goals at once. Of 19 fund building blocks with a
  marginal emission factor, two are on the return-versus-CO2 frontier: solar in Italy and solar in Bulgaria.
