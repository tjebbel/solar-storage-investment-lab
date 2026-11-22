# Plan: alle dashboards deze week, elke dag een LinkedIn-post

*Opgesteld in de nacht van 19 op 20 november 2026. Eén bestand met: wat er vannacht is gedaan, de planning per dagdeel,
een stappenplan per dashboard (met voor- en nadelen van elke methodekeuze), de begrippen in gewone taal en 30 LinkedIn-posts (in het Engels).*

---

## 1. Wat er vannacht is gedaan

**Nieuwe data (met bron per regel)**
- `data/extern/waardeketen_2025.csv`: omzet en nettowinst 2025 van tien fabrikanten (Tongwei, GCL, TCL Zhonghuan, LONGi, Trina,
  JA Solar, JinkoSolar, First Solar, Sungrow, Enphase), uit jaarverslagen en vakpers. Basis voor **dashboard 6**.
- `data/extern/ppa_prijzen.csv`: LevelTen P25-prijzen voor zon (Europa en vijf landen) en de Pexapark EURO Composite. Basis voor **dashboard 17**.
- Uuranalyses uit de lokale cache (`eti.uurdata`): middagdip, batterij-arbitrage, Hirth, koolstofvrij, met dekkingscontrole. Basis voor **16, 18, 19, 20**.

**Nieuwe tabellen** (Engelse kolommen, in `tableau/data_en`): t53-t59 (uurdata), t60 (waardeketen), t61 (PPA-prijzen), t62 (PPA tegen markt).
**KPI-tegels** (`t50`): nu voor dashboards 2-11 en 13-20 (alleen 12 ontbreekt: NGFS).
**Nieuwe modules en tests**: `eti.uurdata`, `eti.ppa_waardeketen`, 8 nieuwe tests; totaal 244 tests, alles groen.
**Uitleg**: `docs/concepts.md` sectie 11 (middagdip, perfecte voorkennis, Hirth, dekking, 24/7, PPA, winstpool).

**Inconsistenties gevonden en opgelost**
| Waar | Was | Nu |
|---|---|---|
| README | "18 controls" | 21 controles, 10 geslaagd, 6 open |
| README | dashboard 6 en 16-24 "planned" | 6, 16-20 "data ready", 21-24 "sources identified" |
| Bouwgids sectie 14 | "9 van 21", "7 nog open", "Achttien controles" | 10 van 21, 6 open, drie open afwijkingen benoemd |
| teksten_en.md | dashboard 7 "7 still open"; titel VS "triple" | "6 still open"; "2.5 times" (22,6 → 56,1 GW) |
| STAPPENPLAN_EN | "16-19 hebben eerst uurdata nodig" | uurdata staat lokaal; 16, 18, 19, 20 kunnen nu |
| C07 in de controlematrix | sprong op "Open" als de tests niet meedraaiden | `run_analyse.sh` draait `assurance_overzicht --tests` |
| uurdata | landen met landcijfers per zone dubbel geteld (Italië 304%) | elk land één keer (Italië 76%) |

**Inconsistenties die blijven (bewust, met uitleg)**
- *PPA-bronnen spreken elkaar tegen.* PV Tech noemde voor Q3 2025 een gemiddelde van 34,25 €/MWh, TaiyangNews 58,21 €/MWh (P25).
  Waarschijnlijk een andere maatstaf; wij gebruiken alleen de P25-reeks. Pexapark: april 51,80 en mei 44,90 "plus 1,2%"
  kan niet allebei kloppen; in de csv gemarkeerd.
- *Hirth-helling:* maanddata geven -0,020, jaardata (t43) -0,011. Geen fout, wel een andere vraag (zie §4).
- *Batterij:* perfecte voorkennis (t55, 71k) tegen realistisch (t1, 61k) voor NL 2025. Beide tonen, met het verschil als "prijs van voorspelfouten".
- *TCL Zhonghuan verlies:* 9,26 (bedrijfssamenvatting) of 9,7 mld CNY (TaiyangNews). Wij gebruiken 9,26.
- *Nederland zonder zondata in Energy-Charts* (2% dekking): NL valt uit 19 en 20; dat staat op het dashboard.

**Wat ik niet kon ophalen** (geen netwerk op de werkmachine; downloaden moet jij doen)
| Data | Voor | Waar | Tijd |
|---|---|---|---|
| NGFS Phase V scenario's | 12 | data.ece.iiasa.ac.at/ngfs → Guest login → Downloads (csv) | 15 min |
| Wereldbank Pink Sheet (maand, xlsx) | 21 | worldbank.org/commodities → "Monthly prices" | 5 min |
| IRENA/ILO Jobs Annual Review 2025 (pdf, tabellen) | 22 | irena.org/publications | 10 min |
| CBS/TNO Monitor Energiearmoede per gemeente | 23 | cbs.nl → Monitor Energiearmoede | 10 min |
| IEA Global Hydrogen Review 2025 assumptions annex | 24 | iea.org (CC BY 4.0) | 5 min |

Zet de bestanden in `data/raw/` (NGFS, licentie: niet op GitHub) of `data/extern/` (de rest) en meld het; ik maak er tabellen van.

---

## 2. Planning

Gemeten tempo: dashboard 2 kostte 4,5 uur inclusief leren; met de vaste werkwijze verwacht ik 2-3 uur per volledig dashboard.
**Tien dashboards in één weekend (25-30 uur) is niet haalbaar in volledige vorm.** Daarom twee formaten:

| Formaat | Inhoud | Tijd | Voor |
|---|---|---|---|
| **Volledig** | KPI-rij + hoofdgrafiek + 3 ondersteunende + onderrand | 2,5-3 uur | 3, 4, 5, 6, 7, 8, 17 |
| **Compact** | KPI-rij + hoofdgrafiek + 1 ondersteunende + onderrand | 1-1,5 uur | 9, 10, 11, 13, 14, 15, 16, 18, 19, 20 |

*Voor compact:* sneller, sterker verhaal (één boodschap per dashboard), beter voor LinkedIn (één beeld).
*Tegen compact:* minder context; een investeerder mist de onderbouwing. Oplossing: de onderbouwing staat in GitHub en in de knopinfo.
Een compact dashboard kan later altijd uitgebreid worden; de titel en link blijven dan gelijk.

| Dag | Ochtend | Middag | Avond (optioneel) |
|---|---|---|---|
| **vr 20 nov** | 7 Control matrix (gepubliceerd, 17/20) | 4 Experience curve (werkbladen klaar) | 4 publiceren |
| **za 21 nov** | 3 Nuclear · 5 Abatement curve | 6 Profit pool · 8 Netherlands | — |
| **zo 22 nov** (nieuw) | **17 PPA** (volledig) | 16 Duck curve · 18 Storage saturation | 19 Hirth · 20 Carbon-free |
| ma 23 nov (was zo) | 9 EU convergence · 10 United States | 11 China · 13 Grid flexibility · 14 Impact investor | — |
| di 24 nov | 15 Global South | 12 NGFS (als de data er is) | — |
| wo-vr | 21-24 zodra de data is gedownload; herstelpunten dashboard 1 en 2 | | |

Weekend = 17, 16, 18, 19, 20, 9, 10, 11, 13, 14 = **tien dashboards**, waarvan 9 compact. Haalbaar in twee volle dagen.

**Vaste volgorde per dashboard** (zie `tableau/STAPPENPLAN_EN.md`, "Vaste werkwijze"): bronnen → KPI-rij dupliceren →
hoofdgrafiek → overige → dashboard (hoogtes eerst) → onderrand → zelftoets → publiceren → link sturen.
Publiceer elk dashboard als tabblad in **Solar and storage in Europe**; de link is dan `.../SolarandstorageinEurope/<Tabnaam>`.

---

## 3. Stappenplannen per dashboard

Dashboards 3, 4, 5, 7-11, 13-15 staan uitgewerkt in `tableau/STAPPENPLAN_EN.md`. Hieronder de nieuwe (6, 16-20) volledig,
en per dashboard de **methodekeuzes met voor- en nadelen**.

### Dashboard 7 Control matrix (vr ochtend, 2,5 uur) — zie STAPPENPLAN_EN
**Keuze: readiness-beoordeling in plaats van een "audit".**
*Voor:* eerlijk (geen accountant heeft getekend), past bij ISAE 3000-taal, laat open punten zien (6 van 21) wat vertrouwen wekt.
*Tegen:* "6 open" kan zwak ogen voor een recruiter. *Weging:* juist de openheid onderscheidt dit portfolio; de titel benoemt het
als vraag ("Can you trust these figures?") en de onderrand zegt wat er volgt.

### Dashboard 4 Experience curve (vr ochtend, 3 uur) — zie STAPPENPLAN_EN
**Keuze: exportprijs van Chinese panelen als prijsreeks.**
*Voor:* openbaar, maandelijks, groot volume (≈250 GW/jaar). *Tegen:* het is een exportwaarde, geen fabrieksprijs; in 2023-24 werd
onder de kostprijs verkocht, dus de leersnelheid (35%) is te hoog ten opzichte van de lange reeks (ITRPV 26%). *Weging:* toon beide,
met de referentielijn 26% en de annotatie "sales below cost".
**Keuze: BCG-matrix op landen.** *Voor:* herkenbaar voor investeerders. *Tegen:* bedoeld voor productportefeuilles; de x-as is hier
batterijopbrengst, geen marktaandeel. *Weging:* zeg het in de subtitel (staat in teksten_en).

### Dashboard 3 Nuclear (vr ochtend, 3 uur) — zie STAPPENPLAN_EN
**Keuze: capture rate als maat voor marktwaarde.** *Voor:* één getal, vergelijkbaar met zon (1,03 tegen 0,61). *Tegen:* kern draait
continu, dus het gemiddelde uur is per definitie zijn uur; dat zegt niets over kosten of bouwrisico. *Weging:* het tekstvak "Two sides"
benoemt systeemkosten en bouwrisico; geen oordeel.

### Dashboard 5 Abatement cost curve (vr middag, 2,5 uur) — zie STAPPENPLAN_EN
**Keuze: gemiddelde of marginale emissiefactor** (het grootste risico in de matrix, score 9).
*Gemiddeld* (totale uitstoot / totale opwek): eenvoudig, officieel (Ember), maar onderschat wat zon echt verdringt (vaak gas).
*Marginaal* (de centrale die uitgezet wordt, vaak gas, ≈0,35 t/MWh): beter voor beslissingen, maar een aanname.
Uitkomst: 46 Mt (gemiddeld) tegen 103 Mt (marginaal). *Weging:* toon beide met een parameter; de titel gebruikt het voorzichtige getal.
**Keuze: LCOE van twee referentielanden.** *Tegen:* grof voor 26 landen. *Weging:* noem het in "What we do not know".

### Dashboard 6 Profit pool (vr middag, 2,5 uur) — NIEUW
**Boodschap:** in 2025 verdiende bijna niemand in de Chinese keten geld; de winst zit bij omvormers en opslag en in beschermde markten.
**Bronnen:** `t60_value_chain` (10 bedrijven), KPI filter **6**.
1. **Bronnen** (5 min): voeg t60 toe uit `data_en`, extract. KPI-rij: dupliceer KPI 2 → filter 6.
   *Controle:* `7 of 8` (magenta) · `-9%` (magenta) · `15% (Sungrow)` (teal) · `29% (First Solar)` (grijs).
2. **Hoofdgrafiek "Margin along the chain"** (30 min): Kolommen `Revenue USD bn` (continu), Rijen `Net margin %`, markering Cirkel,
   `Company` op Label, `Group` op Kleur (China `A8A29E`, Outside China `1F9E89`), `Revenue USD bn` op Formaat.
   Referentielijn y = 0. Of als staaf: `Company` op Rijen gesorteerd op `Chain order`, `Net margin %` als staaf, kleur negatief magenta.
   Titel: `In 2025 the solar chain lost money everywhere except in inverters, storage and protected markets`.
   *Controle:* TCL Zhonghuan -32%, GCL -20%, Tongwei -11%, LONGi -9%, Trina -10,5%, JA -9%, Jinko -7%, First Solar +29%, Sungrow +15%, Enphase +12%.
3. **"Chain view"** (20 min): `Segment` op Kolommen gesorteerd op `Chain order` (polysilicium → wafer → module → omvormer),
   `AVG(Net margin %)` als staaf, kleur op teken. Titel: `The further downstream, the better the margin`.
4. **"Who is big"** (15 min): `Company` × `Revenue USD bn`, staaf, gesorteerd. Laat zien dat de grootste (Sungrow 13, Tongwei 12) tegenovergesteld presteren.
5. **Dashboard** `Profit pool`, 1200 × 1500. Onderrand links: `1. Net margin includes one-off impairments; gross margin is shown in the tooltip.
   2. First Solar and Enphase include US tax credits (45X). 3. Exchange rate 6.85 CNY per USD (2025 average).`
   Rechts: `Next: dashboard 4 (experience curve) · 11 (China build wave) · 21 (silver and copper as cost drivers).`
**Methodekeuze: nettomarge in plaats van een echte winstpool (omzet × marge per segment, wereldwijd).**
*Voor:* openbare, controleerbare jaarcijfers; per bedrijf traceerbaar. *Tegen:* tien bedrijven zijn niet de hele markt; geïntegreerde
bedrijven (Tongwei, LONGi) zitten in meer schakels; projectontwikkelaars en installateurs ontbreken. *Weging:* noem het "margin along the chain",
niet "profit pool", in de titel; zet de IEA-bevinding (meer dan 90% van de Chinese makers verliesgevend, buiten China 10-15% marge) in de subtitel.

### Dashboard 8 Netherlands (vr middag, 3 uur) — zie STAPPENPLAN_EN
**Keuze: congestie per provincie en gemeente in plaats van een kaart.** *Voor:* Tableau kent geen Nederlandse gemeentegrenzen zonder
extra bestand; staven zijn exact. *Tegen:* een kaart spreekt meer aan. *Weging:* later een kaart via postcode-4 (Tableau kent die).
**Keuze: eigen wachtrij (8,05 GW) naast officieel (9,1 GW).** Laat het verschil zien; dat is controle C20 en maakt het geloofwaardig.

### Dashboard 17 PPA or merchant (za ochtend, 3 uur) — NIEUW, volledig
**Boodschap:** een zon-PPA bracht in Duitsland in 2025 meer op dan de markt (50 tegen 46 €/MWh), in Italië veel minder (61 tegen 95);
Europese PPA-prijzen zakten 14% in twee jaar en een hybride PPA (zon + batterij) kost 24% meer.
**Bronnen:** `t61_ppa_prices`, `t62_ppa_vs_merchant`, `t1_zonejaar` (al in de werkmap), KPI filter **17**.
1. **Bronnen** (5 min) t61, t62; KPI-rij filter 17. *Controle:* `55 EUR/MWh` · `31 EUR/MWh` (Spanje) · `+4 EUR/MWh` (Duitsland) · `+24%`.
2. **Hoofdgrafiek "PPA vs market"** (30 min, t62): `Country` op Rijen; `PPA P25 Q4 2025 EUR/MWh` en `Solar capture price EUR/MWh` via
   Meetwaarden als **dumbbell**: markering Cirkel, Meetnamen op Kleur (PPA `4A5FC1`, capture `E39A2D`), plus een lijn tussen de punten
   (dubbele as met markering Lijn en Meetnamen op Pad). Label het verschil. Titel: `Was a solar PPA worth it in 2025? Yes in Germany, no in Italy and Spain`.
3. **"PPA price trend"** (20 min, t61): filter Index = P25 continental index; `Date` × `Price EUR/MWh`, lijn met punten; gestippeld voor `Derived = yes`.
   Referentielijn: Q3 2024 = 63,64. Titel: `European solar PPA prices: -14% in two years`.
4. **"Countries"** (15 min, t61): filter P25 country, staaf per land en periode. Spanje 32,5 → 30,9; VK 87,4 als uitschieter.
5. **"Composite"** (10 min, t61): Pexapark alle technieken per maand (apr-sep 2026), lijn. Laat zien dat de markt in september weer steeg (48,3).
6. **Tekstvak "How to read a PPA"**: `A pay-as-produced solar PPA pays a fixed price for every MWh produced, so the buyer takes the
   cannibalisation risk. That is why solar PPAs are cheaper than wind. A hybrid PPA adds a battery and delivers in the evening: +24%.`
7. **Dashboard** `PPA or merchant`, 1200 × 1600. Onderrand links: `1. A PPA is a 10-year price; the capture price is one year. 2. P25 = the
   25th percentile of offers, not signed deals. 3. Two derived quarters (Q2, Q3 2026) are calculated from LevelTen's index.`
   Rechts: `Next: 18 (storage saturation) · 16 (duck curve) · 13 (flexibility).`
**Methodekeuzes, voor en tegen**
- *P25 als PPA-prijs.* Voor: openbaar, per kwartaal, per land. Tegen: aanbiedingen, geen gesloten contracten; P25 is de scherpe kant.
  Weging: zeg het; de capture-prijs is ook een "beste geval" (zonder profielkosten).
- *Eén jaar markt tegen een tienjarig contract.* Voor: laat zien wat 2025 had opgeleverd. Tegen: een PPA dekt risico over tien jaar;
  in 2022 had de markt veel meer opgeleverd, in 2024 minder. Weging: zet in de knopinfo de capture-prijs 2023 en 2024 (uit t1).
- *Gemiddelde van de Italiaanse zones.* Italië heeft vier zones met verschillende prijzen; het gemiddelde is een benadering.

### Dashboard 16 Duck-curve atlas (za ochtend, compact 1,5 uur) — NIEUW
**Boodschap:** in alle 37 zones werd de middagdip tussen 2023 en 2025 dieper; Griekenland het diepst (53 €/MWh), Nederland van 25 naar 39.
**Bronnen:** `t53_duck_profile`, `t54_duck_depth`; KPI filter **16** (`Greece: 53 EUR/MWh` · `39 EUR/MWh` · `37 of 37` · `265 h`).
1. **Hoofdgrafiek "The duck"** (t53): `Hour` (discreet) × `AVG(Price)`, lijn per `Year` (filter 2019, 2023, 2025; kleur grijs, grijs, oranje),
   filter `Zone name` als keuzelijst (standaard Netherlands). Titel: `The duck gets deeper: Dutch power price by hour of the day`.
2. **"Dip per zone"** (t54, 2025): `Zone name` gesorteerd op `Midday dip EUR/MWh`, staaf; NL oranje. Knopinfo: Evening to midday ratio, Negative hours.
3. Onderrand: `1. Hours in local time; prices hourly (quarter-hours averaged from October 2025). 2. The dip is the day average minus 11-15h,
   so it also grows when evening prices rise. 3. 2026 runs to 15 November.`
**Voor/tegen "dip = daggemiddelde − middag":** *Voor:* één getal, makkelijk te vergelijken. *Tegen:* stijgt ook als de avond duurder
wordt (gascrisis) zonder dat er meer zon is. *Weging:* toon ook de verhouding avond/middag (2,6× NL) die minder gevoelig is voor het prijsniveau.

### Dashboard 18 Storage saturation (za middag, compact 1,5 uur) — NIEUW
**Boodschap:** de arbitrage-opbrengst steeg van 49k (2023) naar 64k €/MW (mediaan 2025), nog geen verzadiging.
**Bronnen:** `t55_battery_arbitrage`; KPI filter **18** (`64k` · `Estonia: 95k` · `NL 71k` · `277 days`).
1. **Hoofdgrafiek** (t55): `Year` × `MEDIAN(Revenue per MW)`, staaf, met NL als oranje lijn (dubbele as, gesynchroniseerd).
   Titel: `No saturation yet: battery arbitrage revenue keeps rising`.
2. **"Zones 2025"**: `Zone name` × `Revenue per MW`, gesorteerd; referentielijn op de mediaan.
3. Onderrand: `1. Perfect foresight is an upper bound; the realistic model (dashboard 1) gives 61k for the Netherlands. 2. Only day-ahead
   arbitrage; reserve markets (FCR, aFRR) add revenue. 3. Saturation shows up when many batteries flatten the spread; watch 2026-2027.`
**Voor/tegen perfecte voorkennis:** *Voor:* reproduceerbaar, geen voorspelmodel nodig, goed voor vergelijken tussen zones. *Tegen:*
overschat de opbrengst (~15% in NL). *Weging:* altijd naast het realistische getal tonen.

### Dashboard 19 Hirth replication (za middag, compact 1,5 uur) — NIEUW
**Boodschap:** elk extra procentpunt zon verlaagt de capture rate met 0,02; bij 30% zon blijft ongeveer de helft van de waarde over (0,52).
**Bronnen:** `t56_hirth`, `t56b_hirth_months`; KPI filter **19**.
1. **Hoofdgrafiek** (t56b): `Solar share %` × `Solar capture rate`, cirkels per maand, filter Zone (standaard Germany), trendlijn lineair.
   Titel: `Hirth was right: the more solar, the less each MWh is worth`.
2. **"Slope per zone"** (t56, filter Reliable = True): staaf met foutbalk (Interval low/high als referentieband per cel), gesorteerd.
3. Onderrand: `1. Monthly data include the season (more sun and lower prices in summer), so slopes are steeper than yearly (-0.011).
   2. Zones with less than 10% solar or a poor fit are left out (5). 3. The Netherlands is missing: Energy-Charts has 2% of its solar.`
**Voor/tegen maanddata:** *Voor:* 94 punten per zone in plaats van 8; een betrouwbaarheidsinterval wordt mogelijk. *Tegen:* seizoen en
kannibalisatie lopen door elkaar. *Weging:* toon beide hellingen; een volgende stap is maand-vaste effecten (de vraag: binnen dezelfde maand
over jaren). Dat staat als verbetering in de backlog.

### Dashboard 20 Hourly carbon-free (za middag, compact 1,5 uur) — NIEUW
**Boodschap:** Frankrijk is 96% koolstofvrij en haalt 90% in bijna elk uur; Duitsland 54% en nooit 90%.
**Bronnen:** `t57_carbon_free`, `t58_carbon_free_hour`; KPI filter **20**.
1. **Hoofdgrafiek** (t58, 2025, filter Solar coverage ok): `Hour` × `Carbon-free share %`, lijn per `Season`, filter Zone (standaard Germany).
   Titel: `Green on paper, grey at night: carbon-free share by hour`.
2. **"Zones"** (t57, 2025): `Zone name` × `Carbon-free share %` (staaf) met `Hours below 50% %` als label.
3. Onderrand: `1. Biomass is not counted as carbon-free (conservative). 2. Zones with less than 60% solar coverage are left out (15).
   3. Imports are not traced: a zone that imports French nuclear power looks dirtier than it is.`
**Voor/tegen biomassa uitsluiten:** *Voor:* voorzichtig, biomassa is omstreden. *Tegen:* officiële statistiek telt het als hernieuwbaar;
landen met veel biomassa (Denemarken, Finland) lijken slechter. *Weging:* noemen, en in de knopinfo het aandeel inclusief biomassa (volgende versie).

### Dashboards 9, 10, 11, 13, 14, 15 (zo, compact) — zie STAPPENPLAN_EN, hoofdgrafiek + één ondersteunende
| # | Hoofdgrafiek | Belangrijkste methodekeuze, voor en tegen |
|---|---|---|
| 9 | mediaan met P10-P90-band per maand | *relatieve spreiding* (P90-P10)/mediaan: voor = los van prijsniveau; tegen = explodeert als de mediaan laag is (2020). Toon ook de absolute spreiding. |
| 10 | voorraad zon/batterij/gas (lijnen) | *EIA-860M = AC, nutsschaal*: voor = maandelijks en officieel; tegen = daken ontbreken, Ember telt DC. Noemen (risico in t16). |
| 11 | export per bestemming (gestapeld) | *exportwaarde ≠ fabrieksprijs*: zie dashboard 4. 2026 heeft 9 maanden: jaarbasis tonen met label "annualised". |
| 13 | negatieve uren per jaar | *EV-laadprofiel is een aanname*: voor = maakt orde van grootte zichtbaar; tegen = geen meting. Als scenario markeren. |
| 14 | ton CO2 per miljoen euro per regio | *vermeden ≠ gereduceerd*: verplicht kader (GHG Protocol). Additionaliteit: NL hoog (marge −14 €/MWh = zonder steun niet rendabel). |
| 15 | vollasturen t.o.v. Nederland | *WACC uit IEA voor vijf regio's*: Afrika onzeker (risico score 6). Laat de gevoeligheid zien: India 44 → 28 €/MWh bij 5%. |

### Dashboard 12 NGFS (ma, zodra de data er is)
Ik bouw de tabellen binnen een uur na je download. Licentie: gebruik toegestaan, herverspreiding van grote delen niet: alleen afgeleide
cijfers in `tableau/data`, ruwe data in `data/raw/` (staat in .gitignore).

---

## 4. Begrippen in gewone taal (voor posts en gesprekken)

| Begrip | In één zin | Voorbeeld |
|---|---|---|
| Capture rate | Wat een MWh zon opbrengt ten opzichte van de gemiddelde stroomprijs. | 0,61: zon krijgt 61 cent per euro gemiddelde prijs. |
| Kannibalisatie | Hoe meer zon tegelijk, hoe lager de middagprijs, dus zon "eet" zijn eigen opbrengst op. | NL 2024 18% zon → 0,60; 2025 21% → 0,62 (jaardata, ruis). |
| Middagdip | Daggemiddelde min middagprijs. | NL 2025: 87 − 48 = 39 €/MWh. |
| Eendencurve | De prijs (of restlast) over de dag: hoog 's ochtends, diep 's middags, hoog 's avonds; lijkt op een eend. | Avond 2,6× de middag in NL. |
| Arbitrage | Goedkoop laden, duur ontladen. | 2-uursbatterij NL 2025: 71k €/MW (bovengrens). |
| Perfecte voorkennis | Rekenen alsof je morgen al kent: een bovengrens. | Realistisch 61k, dus ~15% "voorspelkosten". |
| Hirth-helling | Hoeveel de capture rate daalt per procentpunt extra zon. | −0,02: van 10% naar 30% zon = 0,89 → 0,52. |
| Dekking | Welk deel van de werkelijke opwek in de bron zit. | NL zon in Energy-Charts: 2%. |
| Koolstofvrij per uur (24/7) | Is elk uur schoon, niet alleen het jaartotaal? | Duitsland 54% per jaar, 0% van de uren boven 90%. |
| PPA (P25) | Vaste prijs voor 10 jaar; P25 = scherpste kwart van de aanbiedingen. | Europa Q3 2026: 55 €/MWh. |
| Pay-as-produced | De koper neemt elke geproduceerde MWh af, dus ook de goedkope middaguren. | Daarom is zon-PPA goedkoper dan wind. |
| Hybride PPA | Zon + batterij, levert ook 's avonds. | +24% t.o.v. zon alleen. |
| Nettomarge | Winst na alles (ook afschrijvingen en eenmalige posten) gedeeld door omzet. | LONGi −9%, Sungrow +15%. |
| 45X | Amerikaanse productiesubsidie per geproduceerde module. | Zit in de marge van First Solar (29%). |
| Gemiddelde vs marginale emissiefactor | Gemiddelde uitstoot per MWh vs de uitstoot van de centrale die echt uitgezet wordt. | 46 vs 103 Mt CO2 vermeden potentieel. |
| WACC | Gemiddelde kosten van kapitaal (rente + rendement). | India 12% vs NL 5%: zelfde paneel, andere prijs. |

---

## 5. LinkedIn: 30 posts in English (Fri 20 November to Sat 19 December)

Rules: post around 8:30 (best reach on working days), one image each (screenshot of the main chart, 1200 wide), link in the
first comment (LinkedIn lowers the reach of posts with a link in the text), three to five hashtags.
Link pattern: `https://public.tableau.com/app/profile/tjebbe.lodeizen/viz/SolarandstorageinEurope/<Tab>`.
Only schedule a post once its dashboard is published; the order follows the build plan with one day of slack.

> **Volledige stappenplannen voor 16, 19, 5, 20, 14, 8, 18, 17, 6 en 9 staan in `tableau/STAPPENPLAN_VOLLEDIG.md` (21 nov).**

### Besluit za 21 nov 08:25: geen compacte dashboards meer
Alle dashboards krijgen het volledige formaat: KPI-rij + hoofdgrafiek + 3 ondersteunende grafieken + onderrand (2,5-3,5 uur elk).
Gevolg: ongeveer één dashboard per dag (weekend twee). Bouwdeadline blijft de dag vóór de post; loopt een dashboard uit,
dan wisselt die dag met een tekstpost (methode of verdieping) en schuift de rest één dag op.

### Volledige reeks van 50 posts (za 21 nov, 08:30: na probleem en oorzaak eerst klimaatwaarde; vervangt de tabel hieronder vanaf 23 nov)

Status: ✅ online · R = data klaar, nog bouwen · D = data nodig (zie kolom) · T = alleen tekst.
Feestdagen (21 dec - 4 jan): lager bereik, dus lichtere posts en niet elke dag.

| # | Datum | Post | Status | Nodig |
|---|---|---|---|---|
| 1 | vr 20 nov | D1 First findings | ✅ gepost | |
| 2 | vr 20 nov | D2 Signals Netherlands | ✅ gepost | |
| 3 | za 21 nov | D4 Experience curve | ✅ | |
| 4 | zo 22 nov | D7 Control matrix | ✅ | |
| 5 | ma 23 nov | D16 Duck-curve atlas | R | bouwen za 21 |
| 6 | di 24 nov | D19 Hirth replication | R | bouwen za 21 |
| 7 | wo 25 nov | D5 Abatement cost curve | R | bouwen zo 22 |
| 8 | do 26 nov | D20 Hourly carbon-free | R | bouwen zo 22 |
| 9 | vr 27 nov | D3 Nuclear | ✅ | herstelpunten (onderrand, One GW, labels) |
| 10 | za 28 nov | D14 Impact investor | R | bouwen ma 23 - di 24 |
| 11 | zo 29 nov | Week one in review | T | |
| 12 | ma 30 nov | D8 Netherlands | R | bouwen wo 25 |
| 13 | di 1 dec | D18 Storage saturation | R | bouwen do 26 |
| 14 | wo 2 dec | D17 PPA or merchant | R | bouwen vr 27 - za 28 |
| 15 | do 3 dec | D6 Profit pool | R | bouwen zo 29 |
| 16 | vr 4 dec | D9 EU convergence | R | bouwen ma 30 |
| 17 | za 5 dec | Method: three tools, one answer | T | |
| 18 | zo 6 dec | Week two in review | T | |
| 19 | ma 7 dec | D10 United States | R | bouwen |
| 20 | di 8 dec | D11 China | R | bouwen |
| 21 | wo 9 dec | D15 Global South | R | bouwen |
| 22 | do 10 dec | D13 Grid flexibility and EVs | R | bouwen |
| 23 | vr 11 dec | Deep dive: the Spanish capture-rate puzzle (C19) | D | definitie Synertics navragen |
| 24 | za 12 dec | Method: coverage (two sources disagree) | T | |
| 25 | zo 13 dec | Week three in review | T | |
| 26 | ma 14 dec | D12 Stranded assets (NGFS) | D | NGFS-download (uiterlijk 7 dec) |
| 27 | di 15 dec | D21 Commodities as predictor | D | World Bank Pink Sheet |
| 28 | wo 16 dec | D22 Workforce | D | IRENA jobs report |
| 29 | do 17 dec | D23 Who benefits (energy poverty) | D | CBS/TNO |
| 30 | vr 18 dec | D24 Hydrogen | D | IEA hydrogen annex |
| 31 | za 19 dec | Method: one colour, one meaning | T | |
| 32 | zo 20 dec | Wrap-up: 24 dashboards in one picture | T | |
| 33 | ma 21 dec | Deep dive: marginal emission factor per hour | D | ENTSO-E opwek per bron |
| 34 | di 22 dec | Deep dive: 24/7 with and without biomass | R | backlog |
| 35 | wo 23 dec | Deep dive: Hirth with fixed effects | R | backlog |
| 36 | zo 27 dec | 2026 in review: prices and shocks | R | cijfers t/m 15 dec bijwerken |
| 37 | ma 29 dec | Netherlands: net metering ends 1 January | D | dak-uurprofiel, tarieven 2027 |
| 38 | wo 31 dec | Deep dive: the TenneT queue (C20) | D | officiële reeks TenneT |
| 39 | vr 2 jan | Deep dive: PPA prices over several years | D | LevelTen-reeks 2022-2026 |
| 40 | ma 5 jan | LCOE per country | D | IRENA/Lazard per land |
| 41 | di 6 jan | Cost of capital in Africa and Southeast Asia | D | IEA Cost of Capital Observatory |
| 42 | wo 7 jan | Panel price: factory gate vs export value | D | InfoLink/PVinsights |
| 43 | do 8 jan | Downstream value chain: installers and utilities | D | jaarverslagen |
| 44 | vr 9 jan | Cross-border flows (C10) | D | ENTSO-E grensstromen |
| 45 | za 10 jan | The same dashboard in Power BI / Fabric (C04) | D | Fabric-toegang |
| 46 | zo 11 jan | Control matrix update: 23 controls | R | C22-C23 toevoegen |
| 47 | ma 12 jan | First findings revisited: full year 2026 | D | volledige 2026-data |
| 48 | di 13 jan | Signals Netherlands: winter update | D | prijzen dec-jan |
| 49 | wo 14 jan | Lessons learned: 50 posts, what I would do differently | T | |
| 50 | do 15 jan | Series index and what comes next | T | |

### Volgorde herzien (za 21 nov, 07:45): verhaallijn in plaats van bouwvolgorde

Logica: probleem (waarde van zon daalt) -> oorzaak (uur en aandeel) -> thuismarkt -> oplossingen (opslag, contracten) ->
wie verdient er -> klimaatwaarde (CO2, 24/7, kern, impact) -> regio's -> methode -> nieuwe data -> afsluiting.
Sterkste inhoud op di-do (meeste bereik), methode en overzicht in het weekend. Uiterlijk af = dag vóór de post.

| Datum | Dashboard | Waarom hier | Status / uiterlijk af |
|---|---|---|---|
| vr 20 nov | 1 First findings + 2 Signals NL | opening | gepost |
| za 21 nov | 4 Experience curve | de paradox: bouwen wordt goedkoper, opbrengst daalt | gepubliceerd (15/20) |
| zo 22 nov | 7 Control matrix | vertrouwen; methode past in het weekend | gepubliceerd (17/20) |
| ma 23 nov | 16 Duck curve atlas | waar de waarde verdwijnt: per uur | bouwen za 21 |
| di 24 nov | 19 Hirth replication | hoeveel elk procent zon kost | bouwen za 21 |
| wo 25 nov | 8 Netherlands | thuismarkt: netcongestie, salderen | bouwen zo 22 |
| do 26 nov | 18 Storage saturation | oplossing 1: batterijen | bouwen zo 22 |
| vr 27 nov | 17 PPA or merchant | oplossing 2: contracten | bouwen ma 23 - di 24 |
| za 28 nov | 6 Profit pool | wie verdient er in de keten | bouwen wo 25 |
| zo 29 nov | Week one in review | overzicht | tekst |
| ma 30 nov | 5 Abatement cost curve | klimaatwaarde per euro | bouwen do 26 |
| di 1 dec | 20 Hourly carbon-free | groen op papier, grijs 's nachts | bouwen vr 27 |
| wo 2 dec | 3 Nuclear | het alternatief; geen oordeel | gepubliceerd, herstelpunten |
| do 3 dec | 14 Impact investor | wat dit betekent voor kapitaal | bouwen za 28 |
| vr 4 dec | 9 EU convergence | regio's | bouwen zo 29 |
| za 5 dec | 10 United States | | bouwen ma 30 |
| zo 6 dec | 11 China | | bouwen di 1 |
| ma 7 dec | 15 Global South | | bouwen wo 2 |
| di 8 dec | 13 Grid flexibility | | bouwen do 3 |
| wo 9 - vr 11 dec | methode: three tools · coverage · one colour | | tekst |
| za 12 - zo 13 dec | reserve · week two in review | | |
| ma 14 - vr 18 dec | 12 NGFS · 21 · 22 · 23 · 24 | nieuwe data | zodra gedownload |
| za 19 dec | Wrap-up | | tekst |

De posttekst per dashboard staat hieronder; de dagnummers daar volgen de oude volgorde.

**Day 1 (Fri 20 Nov) — Dashboard 1 First findings**
> Solar power is losing value everywhere in Europe. Where is it happening fastest?
> I analysed hourly prices for 37 European bidding zones (2019 to 15 November 2026) with Python and SQL and built the results in Tableau. Three things stood out:
> 1. Solar earns less per MWh every year. Its capture rate (what a MWh of solar earns versus the average power price) is around 0.61 in Europe: solar gets 39% less than the average hour.
> 2. The 2026 price rise is mostly gas. Split by driver, gas is the largest factor in almost every zone.
> 3. Batteries pay, but only with more than one revenue stream. Day-ahead trading alone does not reach an 8% return; adding reserve markets (FCR, aFRR) does.
> I also show what I do not know for sure, and checked the results against Modo Energy and Enervis: the German capture rates match.
> Dashboard 1 of a series on solar, storage and investment. Feedback from people in the energy sector is very welcome.
> #EnergyTransition #SolarEnergy #BatteryStorage #DataAnalytics #Tableau

**Day 2 (Fri 20 Nov, posted together with day 1) — Dashboard 2 Signals Netherlands**
> Three price shocks in a row. In September, October and November 2026 the Dutch power price was more than three standard deviations above the previous twelve months (z = 4.1, 3.5 and 5.4). Still, solar covered its cost in 6 of 11 months.
> What I learned: I calculated the same signals in Python, DAX (Power BI) and Tableau. 66 of 66 values matched. Only then did I trust the chart.
> Move the cost slider (LCOE) yourself; link in the comments.
> #EnergyTransition #DataAnalytics #Tableau #PowerBI

**Day 3 (Sat 21 Nov) — Dashboard 7 Control matrix** (gepubliceerd; afbeelding: KPI-rij + Status + Risk map)
> Can you trust my figures? I checked them before asking anyone else to.
> I built 21 controls on my own energy-market analysis, in the tradition of the Big Four (COSO, ISAE 3000):
> • the same calculation in two SQL dialects
> • the same 66 signal values in Python, DAX and Tableau: 66 of 66 equal
> • 12 comparisons with outside sources (Modo Energy, Enervis, ITRPV, Dutch parliamentary papers): 9 agree
> Result: 10 passed, 5 deviations explained, 6 still open. I show the open ones on purpose. One example: for Spain I find a solar capture rate of 0.55; an outside source reports 0.97. Until I know why, that number stays marked as open.
> The largest risk in the register: average versus marginal emission factor. It roughly doubles the avoided CO2 (46 versus 103 Mt a year).
> A readiness assessment, not an assurance opinion. Third dashboard in the series "Solar and storage in Europe"; link in the comments.
> #DataQuality #Assurance #ESG #DataAnalytics #Tableau

First comment: Interactive dashboard: https://public.tableau.com/app/profile/tjebbe.lodeizen/viz/SolarandstorageinEurope/Controlmatrix · Code and checks: https://github.com/tjebbel/solar-storage-investment-lab

**Day 4 (Sun 22 Nov) — Dashboard 4 Experience curve**
> Every doubling of installed solar capacity made panels 35% cheaper (2017-2025). The industry's long series (ITRPV) says 26%. Why the gap? In 2023-24 panels were sold below cost.
> In a BCG-style matrix by country, the Netherlands moved from "star" (2022) to "dog" (2025): growth stalled on grid congestion and saturation. #SolarEnergy #Strategy #BCG

**Day 5 (Mon 23 Nov) — Dashboard 3 Nuclear**
> 2025: solar and nuclear produced the same amount of electricity worldwide, 2,807 and 2,805 TWh. In Europe nuclear still produces twice as much as solar. The real difference is value: nuclear earns 1.03 times the average price, solar 0.61.
> Per MWh solar is cheaper; per available hour nuclear delivers more. System costs and build risk decide who is right. No verdict from me, just the numbers. #NuclearEnergy #EnergyPolicy

**Day 6 (Tue 24 Nov) — Dashboard 5 Abatement cost curve**
> Where does solar make money while cutting CO2? In 7 of 26 European countries at 2025 prices: there the cost per tonne avoided is negative. Italy leads at -109 EUR/t; the Netherlands pays +35 EUR/t.
> One assumption more than doubles the potential: if new solar replaces gas (marginal factor) it is 103 Mt a year; if it replaces today's average mix, 46 Mt. I default to gas and let you switch. #CO2 #ClimateFinance #CostCurve

**Day 7 (Wed 25 Nov) — Dashboard 6 Margin along the chain**
> 7 of the 8 Chinese solar manufacturers I looked at lost money in 2025. Module makers averaged -9% net margin; wafer specialist TCL Zhonghuan -32%. Who made money: inverters and storage (Sungrow +15%, Enphase +12%) and First Solar in the protected US market (+29%, including tax credits).
> Lesson for investors: cheap panels are not the same as a healthy supply chain. #SupplyChain #SolarEnergy #Investing

**Day 8 (Thu 26 Nov) — Dashboard 8 Netherlands**
> The Netherlands gets 21% of its electricity from solar (CBS, 2025). But growth halved: +13% in 2024, +5% in 2025. Meanwhile 8 GW of demand waits for a grid connection, and there were 584 hours with a negative price.
> On 1 January 2027 Dutch net metering ends. Home batteries and self-consumption will matter more. #GridCongestion #NetMetering #EnergyTransition

**Day 9 (Fri 27 Nov) — Dashboard 17 PPA or merchant**
> Was a solar PPA worth it in 2025? In Germany, yes: 50 EUR/MWh versus 46 on the market. In Italy, no: 61 versus 95. European solar PPA prices fell 14% in two years; Spain is at 31 EUR/MWh.
> What does earn more: a hybrid PPA with a battery, 24% more expensive than solar-only because it also delivers in the evening. #PPA #PowerMarkets #BatteryStorage

**Day 10 (Sun 29 Nov) — Week one in review**
> Week one: nine dashboards on solar, storage and investment. Three things I did not expect: (1) all 37 European zones got a deeper midday price dip, (2) almost the entire Chinese solar supply chain is losing money, (3) Dutch solar data is largely missing from the European source almost everyone uses. Which question should I answer next week? #DataAnalytics #EnergyTransition

**Day 11 (Mon 30 Nov) — Dashboard 16 Duck curve**
> The duck is getting deeper. In all 37 European bidding zones the midday price fell further below the daily average than in 2023. Greece has the deepest dip (53 EUR/MWh); the Netherlands went from 25 to 39. A Dutch evening hour now costs 2.6 times a midday hour.
> Who profits? Anyone who can move power from noon to evening. #DuckCurve #Flexibility

**Day 12 (Tue 1 Dec) — Dashboard 18 Storage saturation**
> Is the battery market saturating yet? Not yet. Median arbitrage revenue rose from 49k (2023) to 64k EUR per MW per year (2025). Estonia leads with 95k.
> Caveat: this assumes perfect foresight. In the Netherlands that means 71k versus 61k in a realistic model: the gap is the price of forecast errors. #BatteryStorage #EnergyTrading

**Day 13 (Wed 2 Dec) — Dashboard 19 Hirth replication**
> In 2013 Lion Hirth showed that the value of solar power falls as its share grows. I replicated it with data to November 2026 for 25 zones. Result: every percentage point of solar costs 0.02 in capture rate. At 30% solar about half the value is left (0.52).
> Replication is boring and essential. #Research #Econometrics #SolarEnergy

**Day 14 (Thu 3 Dec) — Dashboard 20 Hourly carbon-free**
> Green on paper, grey at night. Germany had 54% carbon-free generation in 2025, but not a single hour above 90%. France: 96%, and above 90% almost every hour. The median zone was below 50% carbon-free in 21% of hours (2019: 36%).
> For companies with green power contracts: annual certificates are not the same as clean power every hour. #247CFE #ESG #Decarbonisation

**Day 15 (Fri 4 Dec) — Dashboard 9 EU convergence**
> One European market, 37 prices. In November 2026 the median was 253 EUR/MWh and the gap between expensive and cheap zones (P90-P10) 192. In relative terms the spread is twice the 2019 level (0.79 versus 0.42). Price convergence is still a promise. #EU #PowerMarkets

**Day 16 (Sat 5 Dec) — Dashboard 10 United States**
> US grid batteries grew 2.5 times in two years, to 56 GW (September 2026), with another 23 GW under construction. Utility-scale solar: 172 GW. California gets 37% of its power from solar. Despite the phase-out of tax credits (OBBBA), the US keeps building. #USA #BatteryStorage #CleanEnergy

**Day 17 (Sun 6 Dec) — Dashboard 11 China**
> China exports about a quarter of a terawatt of solar panels a year at 11 US cents per watt. Europe takes 41%. In 2017 the price was 34 cents. That is the other side of dashboard 6: cheap for buyers, losses for makers. #China #Trade #SolarEnergy

**Day 18 (Mon 7 Dec) — Dashboard 13 Grid flexibility**
> Flexibility has a price. The Netherlands had 584 hours with a negative power price in 2025, while the most expensive 1% of imbalance quarter-hours were above 550 EUR/MWh. With 1.4 million electric cars on Dutch roads, smart charging could shift about 0.9 GW to midday (an assumption). #GridOperators #EV #Flexibility

**Day 19 (Tue 8 Dec) — Dashboard 14 Impact investor**
> Where does a euro avoid the most CO2? Solar in India avoids six times as much CO2 per million euros as in the Netherlands (1,474 versus 246 tonnes a year). In the Netherlands additionality is high: without support, solar is not profitable today (-14 EUR/MWh). And avoided emissions are not a reduction in your own scope 1-3. #ImpactInvesting #ClimateFinance

**Day 20 (Wed 9 Dec) — Dashboard 15 Global South**
> Twice the sun, but capital at 12%. A panel in Egypt delivers 2.1 times the full-load hours of one in the Netherlands. Yet solar power in India costs 44 EUR/MWh; at Dutch financing costs (5%) it would be 28, or 38% cheaper. The biggest lever in the Global South is money, not sunshine. #Development #CostOfCapital

**Day 21 (Thu 10 Dec) — Method: three tools, one answer**
> How do you know a dashboard is right? I calculated the same signals in Python, DAX and Tableau and compared 66 values automatically. On the first attempt the signal column stayed empty, because of one setting in a table calculation. Lesson: a nice chart proves nothing; a test does. #DataQuality #Python #Tableau

**Day 22 (Fri 11 Dec) — Method: coverage**
> The data source almost everyone uses for European power generation contains only 2% of Dutch solar output. Rooftops are missing. Without a check I would have concluded that the Netherlands has almost no solar. I now compare every country with a second source and leave out zones below 60% coverage. #DataQuality #OpenData

**Day 23 (Sat 12 Dec) — Method: one colour, one meaning**
> My first dashboard scored 11 out of 20 on my own design rubric. The biggest mistake: blue meant five different things. Now the rule is: teal = good, magenta = bad, grey = normal, orange = the Netherlands. The second dashboard scored 15 at first publication and 16 after one round. #DataVisualization #Design

**Day 24 (Sun 13 Dec) — Week two in review**
> Two weeks, nineteen dashboards. The common thread: solar gets cheaper and less valuable at the same time, and the money moves to whoever can shift power in time (batteries, flexibility, hybrid PPAs). What is still missing from this story? #EnergyTransition

**Day 25 (Mon 14 Dec) — Dashboard 12 NGFS (if published; otherwise: emission factors explained)**
> *(NGFS)* What happens to solar and gas plants in the climate scenarios of central banks? ... *(figures after the download)*
> *(Alternative)* Average or marginal? One choice that doubles the CO2 that solar avoids. Explained in 60 seconds ...

**Day 26 (Tue 15 Dec) — Dashboard 21 Commodities (or: PPAs explained)**
> Silver has become one of the largest costs of a solar cell after silicon. ... *(figures after the Pink Sheet download)*

**Day 27 (Wed 16 Dec) — Dashboard 22 Workforce**
> 7.3 million people worked in solar PV in 2024, 4.2 million of them in China (IRENA/ILO). ...

**Day 28 (Thu 17 Dec) — Dashboard 23 Who benefits**
> 503,000 Dutch households lived in energy poverty in 2025 (CBS/TNO). Who has solar panels, and who pays for the grid? ...

**Day 29 (Fri 18 Dec) — Dashboard 24 Hydrogen**
> The pipeline for low-emission hydrogen by 2030 shrank from 49 to 37 million tonnes (IEA). What does that mean for cheap midday power? ...

**Day 30 (Sat 19 Dec) — Wrap-up**
> 30 days, more than twenty dashboards, one repository. What I learned about data, about energy and about myself. And: I am looking for a role in climate finance or energy analytics. Tips are welcome. #Careers #ClimateFinance

*Posts 25-29 get their figures once the data is in; the opening is already written, so you only fill in the numbers.*

---

## 6. Beste vervolgstappen (in volgorde, bijgewerkt vr 20 nov 19:45)

Gemeten tempo vr 20 nov: dashboard 7 ongeveer 2,5 uur, dashboard 4 ongeveer 3,5 uur (met pauze). Uiterste bouwdatum = dag vóór de post.

1. **Za 21 nov:** post dashboard 7 (8:30). Bouwen: 3, 5, 6, 8 (uiterlijk: 3 op zo 22, 5 op ma 23, 6 op di 24, 8 op wo 25).
2. **Zo 22 nov:** post dashboard 4. Bouwen: 17 volledig (uiterlijk do 26), daarna 16 en 18 compact.
3. **Ma 23 - vr 27 nov:** 19, 20 (uiterlijk 1-2 dec), 9, 10, 11, 13, 14, 15 compact (uiterlijk 3-8 dec). Download de vijf bestanden voor 12 en 21-24.
4. **Za 28 nov:** geen post (reserve); herstelpunten dashboard 1 en 2.
5. **Week 30 nov - 6 dec:** 12 en 21-24 zodra de data er is (posts 14-18 dec); methode-posts voorbereiden.
6. **Elke avond:** commit + push, schermafbeelding van de hoofdgrafiek naar `docs/img/`, README-regel bijwerken.
7. **Herstelpunten** (als er tijd over is): dashboard 1 segmentkleuren en "Undeclared" (EN), dashboard 2 één trendlijn en jaartallen zonder komma.
8. **Methode-verbetering** (backlog): Hirth met maand-vaste effecten; koolstofvrij inclusief biomassa als tweede maat; PPA met capture-prijs 2023-2024 in de knopinfo.

## 7. Vanaf maandag 23 november: verdieping (za 21 nov)

Doel: dieper in de materie én zichtbaar worden voor impactinvesteerders (klimaatfondsen, LP's) en data-analisten.
Lokaal beschikbaar zonder nieuwe downloads: uurprijzen en opwek per bron (37 zones), grensstromen (`cbet`), onbalans (`imb`, `balans`),
weer (`weer`, `nasa`), en buiten Europa CAISO, AEMO, JEPX, Elexon, EIA.

### Eerst afmaken (posts 5-10 december)
10 United States · 11 China · 15 Global South · 13 Grid flexibility; herstelpunten 3. Daarna 12 en 21-24 zodra de downloads er zijn.

### Nieuwe dashboards 25-30 (volgorde = prioriteit)
| # | Dashboard | Voor wie | Waarom | Data |
|---|---|---|---|---|
| 25 | **What does a MWh really avoid?** Marginale emissiefactor per uur; zon vs batterij (laden 's middags, ontladen 's avonds) | impact, ESG | lost het grootste risico (score 9) op; laat zien dat een batterij CO2 kan verhogen of verlagen | power_* per uur (klaar) |
| 26 | **Revenue at risk 2030**: capture rate per zone in 2030 met de Hirth-helling en de nationale doelen | investeerders, banken | vertaalt 19 naar euro's per MWh; brug naar 12 (stranded assets) | t56 + t13-doelen (klaar) |
| 27 | **Climate fund simulator**: 100 M EUR over zon/batterij/wind in 10 landen, rendement tegen ton CO2, met schuifjes (WACC, helling, batterijopbrengst); Monte Carlo in Python | klimaatfondsen | combineert 4, 5, 14, 17, 18, 19 tot één investeringsbeslissing | bestaande tabellen |
| 28 | **Europe's future is in California and South Australia**: duck curve en negatieve uren in CAISO, AEMO (SA), JEPX, Elexon tegen NL/DE | iedereen | sterk LinkedIn-verhaal; internationale vergelijking | lokaal (klaar) |
| 29 | **Battery without perfect foresight**: vloer (prijzen van gisteren, 80% van het plafond) en plafond (perfecte voorkennis); onbalans en aFRR in versie 2 | batterij-investeerders, analisten | verklaart 71k vs 61k (open risico): NL 59k met prijzen van gisteren | t71 klaar; imb, balans voor v2 |
| 30 | **Forecasting showcase**: day-ahead prijs of capture rate voorspellen met weer en opwek, met backtest en model card | data-analisten, werkgevers | laat ML, validatie en eerlijkheid over fouten zien | weer, nasa, price (klaar) |
| 31 | **Same dashboard in Power BI / Fabric** (C04): Signals NL in Fabric met SQL-endpoint en DAX | data-analisten (Microsoft-stack) | leerdoel Fabric/Azure/Power BI; sluit C04 | Fabric-toegang |

### Verdieping van bestaande dashboards (versie 2)
- 14 Impact investor v2: met de marginale uurfactor uit 25 en een additionaliteitstoets per land.
- 17 PPA v2: meerjarige PPA-reeks en capture-prijs 2022-2025 per jaar (D).
- 18 Storage v2 = 29.
- 20 Carbon-free v2: met biomassa als tweede maat en grensstromen (`cbet`).
- 8 Netherlands v2: einde salderen met dak-uurprofiel (D), post 29 december.

### Zichtbaarheid (naast de dagelijkse post)
1. Eén lang artikel (LinkedIn-artikel of Substack): "What 24 dashboards taught me about the value of solar", met link naar GitHub.
2. Een investeerdersmemo van twee pagina's (PDF uit Docs) als bijlage bij gesprekken: drie bevindingen, drie risico's, drie kansen.
3. GitHub: README met samenvatting en afbeeldingen bovenaan; tag een release `v1.0` na dashboard 24.
4. Tableau Public: profielbeschrijving, de drie beste dashboards uitlichten, indienen voor Viz of the Day.
5. Bronnen en auteurs netjes noemen in posts (Modo, Pexapark, LevelTen, Hirth 2013); vraag onderzoekers om feedback op de replicatie.
6. Elke week reageren onder posts van klimaatfondsen en energie-analisten met een eigen grafiek (geen links).
7. Dataset (opgeschoonde uurdata + datawoordenboek) openbaar maken op GitHub of Kaggle, alleen als de bronlicentie het toestaat (Energy-Charts: licentie per reeks controleren; NGFS nooit).


### Stand za 21 nov, 11:00: data voor de verdieping staat klaar
- 25 Marginal emissions: `eti.marginaal` → t63-t64 (37 zones, 2019-2026, twee methoden, betrouwbaarheidsvlag).
- 26 Revenue at risk: `eti.omzet_risico` → t70.
- 27 Fund simulator: `eti.fonds_simulator` → t65-t67 (1.000 trekkingen, netto fonds-IRR).
- 28 World duck: `eti.wereld_duck` → t68-t69 (CAISO, ERCOT, AEMO SA, JEPX, VK, NL, DE).
- 29-30 Battery strategies en forecast baseline: `eti.batterij_realistisch` → t71-t72.
- KPI-tegels in t50 (Dashboard 25-30). Stappenplannen: `tableau/STAPPENPLAN_VOLLEDIG.md` deel 2. Downloads: `docs/DOWNLOADS.md`.

### Week van 23 november (gesprek Carbon Equity donderdag 26 november)
| Dag | Bouwen | Daarnaast |
|---|---|---|
| ma 23 | 25 Marginal emissions | post 16 |
| di 24 | 27 Climate fund simulator | post 19 |
| wo 25 | 28 World duck · investeerdersmemo (2 pagina's: drie bevindingen, drie risico's, drie kansen, met 25 en 27) | post 5 |
| do 26 | gesprek; 26 Revenue at risk als er tijd is | post 20 |
| vr 27 - zo 29 | 10 United States · 11 China · 15 Global South · 13 Grid flexibility (posts 5-10 dec) | posts 3, 14, review |
| daarna | 29, 30 (model), 31 (Power BI/Fabric), versie 2 van 14, 20, 8, 17 | |

LinkedIn: 25, 27 en 28 passen na de klimaatfase; voorstel om 28 op ma 30 nov te zetten (sterkste deelbare post) en 8 een dag op te schuiven,
25 op wo 9 dec (vóór de methodeposts) en 27 als afsluiter van de klimaatlijn. Beslis na het gesprek van donderdag.

### Kritische herbeoordeling za 21 nov, 12:00 (wat is aangepast)
- 25: KPI telt nu landen, niet zones (Italië had vier zones met dezelfde landcijfers): 2 van 19 landen waar een batterij CO2 toevoegt (was "5 van 26 zones").
- 27: batterijopbrengst is alleen day-ahead en dus een ondergrens; gevoeligheidsrij met reservemarkten (x1,5): 16,4% project, 12,1% netto.
  Fout in eti.lenses (carry in een jaar zonder uitkering) omzeild met fonds(); backlog-story om lenses zelf te herstellen.
  Een project dat nooit terugverdient telt als -30% (was -100%: gaf één zone met 0,2% van de trekkingen te veel gewicht).
- 26: vlag voor doelen boven 50% van de huidige opwek (Denemarken 74%: doel 24,6 TWh op 33 TWh opwek).
- 29: gelezen als vloer en plafond, niet als "realistisch"; NL 59k met de prijzen van gisteren ligt dicht bij de 61k uit dashboard 1.
- 5: EU ETS-referentie bijgewerkt: 74 EUR/t gemiddeld in 2025 (ESMA), rond 90 EUR/t in november 2026.

### Planning twee weken (za 21 nov, 21:15; vervangt de weektabel hierboven)

Hirth kostte ongeveer 4 uur; acht dashboards op één dag is niet haalbaar. Elk dashboard is af vóór zijn postdag.

| Dag | Bouwen | LinkedIn 8:30 |
|---|---|---|
| zo 22 nov | 5 Abatement · 20 Hourly carbon-free · 14 Impact investor · 8 Netherlands | D7 Control matrix |
| ma 23 | 25 Marginal emissions | D16 Duck curve |
| di 24 | 27 Fund simulator | D19 Hirth |
| wo 25 | 28 World duck + investor memo (1 pagina) | D5 Abatement |
| do 26 | Gesprek Carbon Equity; 26 Revenue at risk als er tijd is | D20 Hourly carbon-free |
| vr 27 | 18 Storage saturation · 17 PPA | D3 Nuclear (eerst onderrand, One GW, labels) |
| za 28 | 6 Profit pool · 9 EU convergence | D14 Impact investor |
| zo 29 | Herstelpunten D16, D7, D1/D2, D19 (legendatitel, deeljaar 2026); buffer | Week one in review |
| ma 30 | 10 United States | D8 Netherlands |
| di 1 dec | 11 China | D18 Storage saturation |
| wo 2 | 15 Global South | D17 PPA or merchant |
| do 3 | 13 Grid flexibility and EVs | D6 Profit pool |
| vr 4 | 29 Battery floor/ceiling (26 als die nog open is) | D9 EU convergence |
| za 5 | Downloads volgens `DOWNLOADS.md` (NGFS uiterlijk 7 dec) | Method: three tools, one answer |
| zo 6 | Start 12 NGFS | Week two in review |

Controle zondag-dashboards (21 nov avond, uit `tableau/data_en` herberekend): alle controlewaarden in STAPPENPLAN_VOLLEDIG voor 5, 20, 14 en 8
kloppen; aangepast: KPI 5 naar marginale factor (Italy -109, NL 35), titel wachtrij D8 (about 8 GW), gemeenten D8 (67 op 100%), bronnaam `Biomass, total` in D14.

### LinkedIn-besluit zo 22 nov, 21:40
De post over D7 Control matrix is niet geplaatst: niet informatief en aantrekkelijk genoeg. Hij blijft in het archief als referentie
en om later op voort te bouwen. Ma 23 nov wordt D16 Duck curve de vierde post in de reeks (tekst: "Fourth dashboard in the series").
Alle volgende postnummers schuiven één op.

### Planning week 23-29 nov (zo 22 nov, 22:00; vervangt eerdere weektabellen)
Tempo zo 22 nov: 7 dashboards (19, 5, 20, 14, 8, 25, 27). Doel deze week: 26-30 en alles tussen 6 en 18 af; volgende week 31 en verder.

| Dag | Bouwen | LinkedIn 8:30 |
|---|---|---|
| ma 23 | 27 (8%-lijn) · 26 Revenue at risk · 28 World duck · 29 Realistic battery · 30 Forecasting (als het model klaarstaat) | D16 Duck curve (post 4) |
| di 24 | 30 (als ma niet gelukt) · 18 Storage saturation · 17 PPA or merchant | D19 Hirth |
| wo 25 | 6 Profit pool · 9 EU convergence · investor memo (1 pagina, met 25 en 27) | D5 Abatement |
| do 26 | Gesprek Carbon Equity; daarna 10 United States als er tijd is | D20 Hourly carbon-free |
| vr 27 | 11 China · 13 Grid flexibility | D3 Nuclear |
| za 28 | 15 Global South · 12 NGFS (NGFS-download eerst, deadline 7 dec) | D14 Impact investor |
| zo 29 | Herstelpunten D3, D16, D1/D2, D19, D8, D14; buffer | D8 Netherlands |

Volgende week: 31 (Power BI / Fabric, wacht op Fabric-toegang) en de deep dives uit de 50-postlijst (21-24 zodra de data binnen is).

### Dashboards 32-36 (zo 22 nov, 22:15): deep dives worden genummerde dashboards
| # | Dashboard | Voor wie | Nodig (zie DOWNLOADS.md) |
|---|---|---|---|
| 32 | LCOE per country | ontwikkelaars, investeerders | IRENA/Lazard per land; vervangt de twee referentielanden (noord 67, zuid 51) in 5, 14, 26 |
| 33 | Cost of capital in Africa and Southeast Asia | impactinvesteerders | IEA Cost of Capital Observatory; verdieping van 14 en 15 |
| 34 | Cross-border flows (C10) | handelaren, netbeheer | grensstromen staan lokaal (`cbet`); controle met ENTSO-E |
| 35 | The TenneT queue (C20) | NL-net, beleid | officiele TenneT-reeks; sluit open afwijking 38 GW |
| 36 | Netherlands after net metering | huishoudens, installateurs | dak-uurprofiel en tarieven 2027; post rond 29 december |

Volgorde volgende week (30 nov - 6 dec): 34 eerst (data staat lokaal), dan 31 zodra Fabric-toegang er is, daarna 32, 33, 35, 36 naarmate de downloads binnen zijn.
