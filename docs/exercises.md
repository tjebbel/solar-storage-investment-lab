# Exercises

Thirty exercises from beginner to advanced. Solutions to the calculation exercises are in
`exercises/solutions.py` and are tested in `tests/test_solutions.py`. Run `make test`.

## A. Energy basics
* **E01** A 2 MW battery discharges for 15 minutes. How many MWh? Write `kw_to_kwh`.
* **E02** A 20 MW park produces 20,000 MWh a year. Capacity factor?
* **E03** Why does a nuclear plant have a much higher capacity factor than a solar park?

## B. Markets
* **E04** Write `merit_order_price` and find the price at demand 6, 9 and 12 GW.
* **E05** Prices are 100, 20, 100 €/MWh and solar produces 0, 10, 0 MWh. Capture price and capture rate?
* **E06** Open `price_heatmap.png`. In which months and hours are prices lowest? Explain with the merit order.
* **E07** Why do negative prices occur? Name two causes.

## C. Contracts and investment
* **E08** A financial PPA at €60/MWh. What does the buyer pay the producer per 1,000 MWh when the market is
  €40? And at €90? Write `ppa_settlement`.
* **E09** Why do hyperscalers sign 20–25 year PPAs with nuclear plants instead of buying certificates?
* **E10** Simple payback of €10m capex with €1.1m cash per year?
* **E11** Explain the difference between NPV and IRR in two sentences.
* **E12** Real rate at 7% nominal and 2.5% inflation?
* **E13** IRR of [−100, 110]?
* **E14** In `tornado.png`, which input matters most for solar IRR, and why?
* **E15** Change `hurdle_irr` to 0.10 in `config.py`, run `make run`. What happens to P(below hurdle)?

## D. Private markets
* **E16** A fund calls 30%, 30%, 20%, 10% of a €100 commitment and distributes 0, 5, 20, 50, 60, 50.
  Compute the cumulative cash flow (the J-curve).
* **E17** Distributions €60, remaining NAV €90, paid-in €100: TVPI?
* **E18** A fund-of-funds invests in 8 funds with 25 companies each and 10% overlap. How many companies?
* **E19** Why is private equity less liquid than listed shares, and what does an ELTIF change?
* **E20** What is a co-investment, and why would a family office want one?

## E. AI and energy
* **E21** Consumption 10 MWh every hour for 4 hours; clean supply 0, 20, 20, 0. Annual-style match and
  hourly (24/7) match? Write both functions.
* **E22** Why does 24/7 matching favour firm clean power (nuclear, geothermal) and storage?
* **E23** A 100 MW IT load with a PUE of 1.2: yearly electricity use?
* **E24** Run `make run-live YEAR=2025`. Compare the live capture rate with the synthetic one.
* **E25** Compare the duck curve of 2024 and 2025 with live data. What changed?

## F. Batteries and policy
* **E26** Spread €60/MWh, 300 cycles of 20 MWh. Margin before and after a €10/MWh tariff on both charging
  and discharging?
* **E27** Using E26, explain the Dutch–German difference in battery investment.
* **E28** Raise `battery_mw` revenue with an ancillary-services assumption. When does the battery IRR pass 8%?

## G. Impact
* **E29** Why is the yearly-average CO₂ factor too high for solar? Use `co2_methods.png`.
* **E30** Write a one-paragraph impact statement for an investment committee that is honest about method.
