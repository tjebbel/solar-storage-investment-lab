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
