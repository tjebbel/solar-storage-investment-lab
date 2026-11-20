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
