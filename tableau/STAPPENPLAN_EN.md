# Stappenplannen Engelse dashboards (vanaf 20 november 2026)

Planning, de nieuwe stappenplannen voor 6 en 16-20, voor- en nadelen per methode en 30 LinkedIn-posts: `docs/PLAN_WEEK_EN_LINKEDIN.md`.

Alle nieuwe dashboards komen **alleen in het Engels**, als extra tabblad in de werkmap `tableau/Solar and storage in Europe.twbx`.
Publiceren gebeurt altijd onder dezelfde naam **Solar and storage in Europe**. De link wordt dan
`https://public.tableau.com/app/profile/tjebbe.lodeizen/viz/SolarandstorageinEurope/<Dashboardnaam>`.

## Wat er klaarstaat

- **Data**: `tableau/data_en/`. Tabellen die nog niet in de werkmap zitten hebben **Engelse kolomnamen**, dus je hoeft niets
  te hernoemen. Uitzondering: t1-t5, t9, t10, t43 en t47-t50 houden hun Nederlandse kolomnamen, omdat dashboard 1 en 2 ze al gebruiken.
- **KPI-tegels**: `t50_kpi_dashboards` (al in de werkmap) bevat nu tegels voor dashboard 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14 en 15.
- **Teksten**: `tableau/teksten_en.md` (titels, subtitels, onderrand per dashboard).
- **Ontwerpnorm**: bovenaan `tableau/BOUWGIDS_TABLEAU.md`. Doel: zelftoets 16/20 of hoger vóór publiceren.

## Vaste werkwijze (lessen van dashboard 1 en 2)

1. **Bron toevoegen**: Data → Nieuwe gegevensbron → Tekstbestand → `tableau/data_en/<tabel>.csv` → meteen **Extraheren**.
2. **Getalnotatie één keer goed**: rechtsklik op het veld in het gegevensvenster → Standaardeigenschappen → Getalnotatie.
   Jaartallen: 0 decimalen, **zonder** scheidingsteken voor duizendtallen.
3. **Kleuren**: Kleuren bewerken → dubbelklik op het vakje → Mac-kleurkiezer → RGB-schuifjes → hexcode. Ondoorzichtigheid 100%.
   Vaste betekenis: teal `1F9E89` = goed, magenta `C4457A` = slecht, grijs `A8A29E`/`D6D3D1` = neutraal of normaal,
   oranje `E39A2D` = Nederland. Bronnen: zon `C9961A`, wind `2A9DB5`, kern `7A5195`, gas/fossiel `A0522D`, water/bio `1F9E89`.
4. **KPI-rij in 2 minuten**: rechtsklik op het tabblad `KPI 2` → Dupliceren → hernoem → filter Dashboard op het nieuwe nummer.
5. **Dashboard opbouwen**: eerst Grootte (vast, 1200 breed), dan objecten van boven naar beneden slepen, dan in tabblad Lay-out de
   hoogtes invullen. Legenda's meteen onder hun grafiek, horizontaal; geen legendakolom rechts. Dubbele legenda's weg.
6. **Onderrand**: horizontale container met twee tekstvakken, "What we do not know for sure" en "What comes next";
   koppen 11 pt vet, tekst 10 pt grijs, elk punt op een eigen regel.
7. **Werkbladen verbergen** voor publiceren: rechtsklik op het dashboardtabblad → Alle werkbladen verbergen.

---

## Dashboard 7 "Control matrix" (vrijdagochtend, ongeveer 2,5 uur)

**Boodschap**: van de 21 controles zijn er 10 geslaagd en 6 nog open. Het grootste risico is de keuze van de emissiefactor
(gemiddeld of marginaal). Dit is een readiness-beoordeling, geen accountantsverklaring.

**Bronnen**: `t15_controles`, `t16_risico`, `t52_validatie_extern` (alle drie met Engelse kolomnamen) en `t50_kpi_dashboards` (al aanwezig).

### Stap 1. Bronnen toevoegen (5 min)
Voeg t15, t16 en t52 toe uit `tableau/data_en/`, elk als extract.
**Controle**: in t15 zie je de kolommen Control, Domain, Objective, Side A, Side B, Result, Status, Source, Recalculated.

### Stap 2. KPI-rij "KPI 7" (5 min)
Dupliceer `KPI 2`, noem het `KPI 7`, zet het filter Dashboard op **7**.
**Controle**: `10 of 21` (teal) · `6` (magenta, met C04, C10, C13, C15, C19, C20) · `12 of 21` (grijs) · `score 9 of 9` (magenta).

### Stap 3. Werkblad "Status" (10 min, t15), de hoofdgrafiek
1. Nieuw werkblad `Status`. Sleep **Status** naar Rijen en **CNT(Control)** naar Kolommen (sleep Control naar Kolommen,
   rechtsklik → Meting → Aantal). Markering **Staaf**.
2. Sleep **Status** ook naar Kleur:

   | Status | Hex |
   |---|---|
   | Passed | `1F9E89` |
   | Passed with limitation | `8CCFC3` |
   | Deviation explained | `E39A2D` |
   | Deviation open | `C4457A` |
   | Open | `A8A29E` |
3. Sorteer handmatig in deze volgorde (rechtsklik op Status → Sorteren → Handmatig): Passed, Passed with limitation,
   Deviation explained, Deviation open, Open.
4. Labels aan (Label → Markeringslabels tonen). Verberg de as onderaan (rechtsklik → Koptekst tonen uit) en de legenda.
5. Titel: `Status at a glance` · subtitel (10 pt grijs): `21 controls; green = passed, magenta = deviation still open.`
**Controle**: 8 · 2 · 5 · 3 · 3 (samen 21).

### Stap 4. Werkblad "Control matrix" (25 min, t15)
1. Nieuw werkblad `Control matrix`. Sleep naar Rijen, in deze volgorde: **Domain**, **Control**, **Objective**, **Result**.
2. Markering **Vierkant**, sleep **Status** naar Kleur (zelfde kleuren als stap 3). Sleep **Status** ook naar Label: in het
   vierkant staat dan de tekst. Je hebt nu één gekleurde kolom met de status, met links de vier tekstkolommen.
3. Sorteer Domain handmatig: Calculation, Sources, Data quality, Assumptions, Code, Reporting.
4. Breedte: sleep de kolomgrenzen zodat Objective en Result leesbaar zijn (Result mag over twee regels: Opmaak → Uitlijning →
   Terugloop aan).
5. Opmaak → Randen: rijscheiding **Deelvenster** op Domain-niveau (dunne grijze lijn tussen de domeinen), geen strepen.
6. Knopinfo: `<Control>: <Objective>` / `Side A: <Side A>` / `Side B: <Side B>` / `Source: <Source>` / `Recalculated each run: <Recalculated>`.
7. Titel: `Control matrix: what was checked, against what, and the result`.
**Controle**: 21 rijen. C02 = `66 of 66 values equal` (Passed), C03 = `66 of 66 values equal (English workbook, 2026)` (Passed),
C19 en C20 = Deviation open.

### Stap 5. Werkblad "Risk map" (20 min, t16)
1. Nieuw werkblad `Risk map`. **Likelihood** naar Kolommen en **Impact** naar Rijen, beide **discreet** (rechtsklik → Discreet,
   en als Dimensie). Zet Impact aflopend (3 boven).
2. Markering **Vierkant**, Formaat groot, zodat de 3 × 3 vakken elkaar bijna raken.
3. Maak een berekend veld `Risk score` = `MAX([Likelihood] * [Impact])` en sleep het naar Kleur. Kleuren bewerken: palet
   oplopend, van `F5F5F4` (laag) naar `C4457A` (hoog), stappen 3.
4. Sleep **CNT(Risk)** naar Label (rechtsklik → Meting → Aantal): het getal in elk vak = aantal risico's.
5. Knopinfo: sleep **Risk** naar Knopinfo, rechtsklik → Kenmerk. Of: zet in de knopinfo `<CNT(Risk)> risks`.
6. Titel: `Risk map: likelihood x impact` · subtitel `Score 1-9. Hover for the risks in each cell.`
**Controle**: vak (3,3) = 1 risico, vak (3,2) = 5, vak (2,3) = 3.

### Stap 6. Werkblad "Top risks" (15 min, t16)
1. Nieuw werkblad `Top risks`. **Risk** naar Rijen, **SUM(Score)** naar Kolommen, markering Staaf.
2. Sorteer Risk aflopend op Score. Filter: Score ≥ 6 (sleep Score naar Filters → Bereik → 6 tot 9). Je houdt 9 risico's over.
3. Kleur: alles grijs `A8A29E`, behalve score 9: maak een berekend veld `Top` = `[Score] = 9`, naar Kleur, True `C4457A`, False `A8A29E`.
4. Label: Score. Knopinfo: **Mitigation** en **Dashboards**.
5. Titel: `The nine largest risks and what we do about them` · subtitel `Hover for the mitigation and the dashboards it affects.`
**Controle**: bovenaan *Average or marginal emission factor* (9), daarna acht risico's met score 6.

### Stap 7. Werkblad "External validation" (15 min, t52)
1. Nieuw werkblad `External validation`. **Subject**, **This project**, **External** naar Rijen. Markering Vierkant,
   **Verdict** naar Kleur en Label.
2. Maak een berekend veld `Verdict group`:
   ```
   IF [Verdict] = "agrees" THEN "agrees"
   ELSEIF STARTSWITH([Verdict], "explainable") THEN "explainable"
   ELSE "deviation open" END
   ```
   Zet dat op Kleur in plaats van Verdict: agrees `1F9E89`, explainable `E39A2D`, deviation open `C4457A`.
3. Knopinfo: **Source** en **Verdict** (volledig).
4. Titel: `Checked against outside sources: 9 of 12 agree`.
**Controle**: 12 rijen; Spain 2025 en TenneT offtake = deviation open; learning rate = explainable.

### Stap 8. Dashboard "Control matrix" (30 min)
1. Nieuw dashboard, naam **`Control matrix`**, Grootte vast **1200 × 1900**.
2. Van boven naar beneden:

   | Rij | Inhoud | Hoogte |
   |---|---|---|
   | 1 | Tekst: `Can you trust these figures? 21 controls, 6 still open` (20 pt) / `In the tradition of the Big Four (COSO, ISAE 3000). A readiness assessment, not an assurance opinion. Status 20 November 2026.` (10 pt grijs) | 80 |
   | 2 | KPI 7 | 150 |
   | 3 | Afbeelding `docs/img/chain_en.png` (Objecten → Afbeelding; Passend maken; bron: eti.keten_en) met kop `From source to dashboard` | 220 |
   | 4 | Status (40%) naast Risk map (60%) | 300 |
   | 5 | Control matrix | 620 |
   | 6 | Top risks (55%) naast External validation (45%) | 380 |
   | 7 | Onderrand (twee tekstvakken) | 150 |
3. Onderrand links, **What we do not know for sure**:
   `1. Six controls are still open; C04 waits for Power BI / Fabric access.`
   `2. Avoided emissions (CBS) are not an emission reduction: do not net them off scope 1-3 (GHG Protocol).`
   `3. Omnibus I (EU 2026/470) dropped the reasonable-assurance requirement; only limited assurance remains, for far fewer companies.`
4. Onderrand rechts, **What comes next**:
   `Next controls: C04 (Power BI), C10 (cross-border flows), C13 (CBS vs Ember), C15 (status codes), C19 (Spain capture rate), C20 (TenneT queue).`
   `Next dashboards: 5 (abatement cost curve) · 14 (impact investor).`
   `Code and checks: github.com/tjebbel/solar-storage-investment-lab`

### Stap 9. Zelftoets en publiceren (15 min)
1. Zelftoets: titel = bevinding met getal? Elke kleur één betekenis? Geen Nederlands woord meer? Score ≥ 16?
2. Werkbladen verbergen, Server → Tableau Public → Opslaan als **Solar and storage in Europe**.
3. Controleer de link `.../SolarandstorageinEurope/Controlmatrix`. Sla daarna ook lokaal op (Bestand → Opslaan als, in `tableau/`).
4. Stuur mij de link: ik beoordeel hem en zet hem in de README.

---

> **Volledige stappenplannen voor 16, 19, 5, 20, 14, 8, 18, 17, 6 en 9 staan in `tableau/STAPPENPLAN_VOLLEDIG.md` (21 nov).**

## Dashboard 4 "Experience curve and portfolio" (ongeveer 3 uur)

Bronnen (Engelse kolommen): `t11_ervaringscurve`, `t45_leercurve`, `t12_portefeuille`, `t46_portefeuille_uitleg`, `t42_gebeurtenissen`.
KPI: dupliceer KPI 2 → filter **4**.
1. **Experience curve** (t11): Cumulative GW (x) tegen Price USD per W (y), **beide assen logaritmisch** (As bewerken → Logaritmisch),
   markering Cirkel + Lijn (dubbele as of Pad), Year als label. Trendlijn Exponentieel/Macht. Referentietekst: `35% cheaper per doubling (95%: 21-46%)`.
   Annotatie 2024 (rechtsklik op het punt → Annoteren → Markering): `sales below cost`. **Controle**: 2025 = 0.095 USD/W.
2. **Variants** (t45): Variant op Rijen, Learning rate als staaf met foutbalk (Interval low/high als referentieband per cel);
   referentielijn ITRPV 0.26. **Controle**: all years 0.35.
3. **Portfolio 2025** (t12, filter Snapshot = 2025): Battery revenue vs median (x) tegen Solar capacity growth per year (y), Quadrant
   op Kleur (Star `E39A2D`, Cash cow `1F9E89`, Question mark `4A5FC1`, Dog `A8A29E`), Solar capacity GW op Formaat, Country code als label.
   Referentielijnen op beide medianen. **Controle**: BGR, LTU, POL en ROU zijn Star.
4. **2022 to 2025** (t46): Country op Rijen, Quadrant 2022 en Quadrant 2025 als twee kolommen met kleur; Explanation in de knopinfo.
   **Controle**: Netherlands Star → Dog.
5. Dashboard `Experience curve`, 1200 × 1800; teksten uit `teksten_en.md`.

## Dashboard 3 "Nuclear" (ongeveer 3 uur)

Bronnen: `t6_kern_gebied_jaar`, `t7_kern_land`, `t8_kern_markt`, `t44_kern_zon`. KPI: filter **3**.
Volg bouwgids sectie 13 (stappen 1-10), met de Engelse veldnamen: Area, Source, Generation TWh; Country, Nuclear trajectory,
Nuclear change 2015-2025 TWh; Nuclear share 2025 %, CO2 grams per kWh 2025; Capture rate; Solar GW for nuclear TWh.
Bronkleuren volgens de vaste werkwijze. **Controle**: world 2025 nuclear 2,805 vs solar 2,807 TWh; capture rate 2025 nuclear 1.03, solar 0.61.

## Dashboard 5 "Abatement cost curve" (ongeveer 2,5 uur)

Bron: `t13_kostencurve`. KPI: filter **5**. Stijl: McKinsey-kostencurve.
1. **Cost curve**: berekend veld `Start Mt` = `[Cumulative Mt (average factor)] - [Potential Mt (average factor)]`.
   Kolommen: `Start Mt` (continu), Rijen: `Cost per tonne (average factor)`, markering **Gantt-balk**, `Potential Mt (average factor)`
   op **Formaat** (dan is de balk precies zo breed als het potentieel). Country als label, kleur: kosten < 0 teal, > 0 grijs,
   Netherlands oranje. Filter: Potential > 0. Referentielijnen y = 74 `EU ETS 2025 average` en y = 90 `EU ETS November 2026`.
   **Controle**: Italy links (-153 EUR/t, 15.1 Mt), samen ongeveer 45.6 Mt.
2. **Average vs marginal factor**: dezelfde grafiek met de marginale kolommen (of een parameter `Emission factor` met keuze
   average/marginal en twee berekende velden). **Controle**: totaal 102.6 Mt marginaal.
3. **Margin per country**: Country op Rijen, Margin EUR/MWh als staaf rond nul, gesorteerd. **Controle**: 7 positief.
4. Titel: `Solar abates CO2 at a profit in 7 of 26 countries`. Onderrand: gemiddelde vs marginale factor; LCOE voor maar twee referentielanden.

## Dashboard 8 "Netherlands: grid congestion and the end of net metering" (ongeveer 3 uur)

Bronnen: `t37_nl_stroom`, `t40_res_regio`, `t30_congestie_rnb`, `t32_congestie_gemeente`, `t51_congestie_afstemming`, `t25_flex_nl`. KPI: filter **8**.
1. **Solar build-out** (t40): Year × SUM(Solar MWp), gestapeld Solar large MWp / Solar small MWp. Titel: `Growth halves: +5% in 2025`.
2. **Shortage per province** (t30): Province op Rijen, SUM(Shortage offtake MW) en SUM(Shortage feed-in MW) naast elkaar.
3. **Municipalities** (t32): top 20 op Offtake shortage %, staaf, magenta.
4. **Reconciliation** (t51): tabel Queue, This project GW, Official GW, Status (Deviation explained oranje, Deviation open magenta).
5. **Negative hours** (t25): Year × Negative hours, staaf; 2026 tot 15 november arceren of in de titel.
6. Event box: `From 1 January 2027 Dutch net metering ends.` Titel: `Dutch solar hits the grid wall: 8 GW waits for offtake`.

## Dashboard 9 "European Union: price convergence" (ongeveer 2 uur)

Bron: `t18_convergentie`. KPI: filter **9**.
1. **Fan chart**: Month × Median (lijn), met een referentieband P10-P90 (Analyse → Referentieband, van P10 tot P90, grijs).
2. **Relative spread**: Month × Relative spread (lijn), referentielijn = gemiddelde 2019 (0.42).
3. Titel: `One market, 37 prices: the spread is twice the 2019 level`. **Controle**: 2022-07 relative spread 1.14; 2026-11 median 253.

## Dashboard 10 "United States: tax credits and the build-out" (ongeveer 2,5 uur)

Bronnen: `t33_vs_voorraad`, `t34_vs_toevoeging`, `t35_vs_staat`, `t36_vs_gepland`, `t21_vs_staten`, `t20_bouwgolf` (filter Country = United States). KPI: filter **10**.
1. **Stock**: Snapshot × Solar GW, Wind GW, Battery GW, Gas GW (Meetwaarden, lijnen, bronkleuren; batterij blauw `4A5FC1`).
2. **Monthly additions** (t34): Date × Solar GW en Battery GW, staven; annotatie OBBBA 4 July 2025 en grens bouwstart 4 July 2026 (t20 Event).
3. **Pipeline** (t36): Planned year × SUM(Capacity MW) per Group, filter Status U/V/TS/T.
4. **States** (t21): kaart (State, geografische rol Staat) met Solar share % of top-15 staaf. **Controle**: California 37%.

## Dashboard 11 "China: market prices and the build wave" (ongeveer 2 uur)

Bronnen: `t22_china_export`, `t20_bouwgolf` (filter Country = China), `t11_ervaringscurve`. KPI: filter **11**.
1. **Exports by destination** (t22): Year × SUM(GW), gestapeld per Destination (max. 5 kleuren, rest Other).
2. **Export price** (t22): Year × SUM(USD billion)/SUM(GW), lijn. **Controle**: 2025 = 0.095 USD/W.
3. **Build wave** (t20, China): Month × Additions GW, staven, Document 136 (1 June 2025) als annotatie.
   Let op: t20 heeft voor China soms twee rijen per maand (twee bronnen); gebruik **MAX** in plaats van SUM.

## Dashboard 13 "Grid operator: flexibility and EVs" (ongeveer 2 uur)

Bronnen: `t25_flex_nl`, `t26_ev_net`. KPI: filter **13**.
1. **Negative hours** (t25): Year × Negative hours.
2. **Imbalance prices 2025** (t25): Upward average, Upward median, Upward P99 als staven (één jaar, drie maten).
3. **EV fleet** (t26): top 15 Country op EV fleet, Netherlands oranje. Tweede grafiek: Managed midday demand GW vs Unmanaged peak GW.
4. Titel: `Flexibility is worth money: 584 negative hours and imbalance spikes above 500 EUR/MWh`.

## Dashboard 14 "Impact investor: return against avoided CO2" (ongeveer 2 uur)

Bronnen: `t27_impact`, `t39_vermeden_co2`. KPI: filter **14**.
1. **CO2 per million EUR** (t27): Region × Year (2025, 2030, 2050), staven Tonnes CO2 per M EUR per year. **Controle**: India 2025 = 1,474.
2. **Additionality** (t27): Region × Solar margin EUR/MWh (2025), kleur Additionality.
3. **Avoided CO2 NL** (t39): Year × Avoided CO2 kt per Source (Solar power, Onshore wind, Offshore wind, Biomass total), gestapeld.
4. Box: `Avoided emissions are not an emission reduction (GHG Protocol).`

## Dashboard 15 "Global South: why the cost of capital matters" (ongeveer 2 uur)

Bronnen: `t28_zuiden`, `t27_impact`. KPI: filter **15**.
1. **Sun** (t28): Location × Full-load hours vs Netherlands, gesorteerd, referentielijn 1.0 (Netherlands) en 1.5.
2. **Capital** (t27): Region × WACC (2025) en LCOE EUR/MWh vs LCOE at 5% WACC (twee staven per regio).
3. Titel: `Twice the sun, but capital at 12%: India's solar would be 38% cheaper at Dutch financing costs`.

---

## Nog niet mogelijk (wat er nodig is)

| Dashboard | Wat ontbreekt |
|---|---|
| 6 Profit pool (Bain) | Klaar (20 november): t60 met tien fabrikanten; stappenplan in `docs/PLAN_WEEK_EN_LINKEDIN.md` §3. |
| 12 Stranded assets (NGFS) | NGFS-scenariodata (licentie: alleen lokaal, niet op GitHub). Download via de NGFS Scenario Explorer. |
| 16 Duck-curve atlas | Klaar (20 nov): `eti.uurdata` → t53-t54; stappenplan in `STAPPENPLAN_VOLLEDIG.md`. |
| 17 PPA or merchant | Data herzien 23 november: t61, t62 (11 landen, kolom Source) en t76 (25 landen) uit LevelTen, Pexapark en KYOS; gepubliceerd 23 november (17/20), met de 2030-stresstest (t77) als tweede grafiek. Stappenplan: `STAPPENPLAN_VOLLEDIG.md`. |
| 18 Storage saturation | Klaar (20 nov): `eti.uurdata` → t55; stappenplan in `STAPPENPLAN_VOLLEDIG.md`. |
| 19 Hirth replication | Klaar (20 nov): `eti.uurdata` → t56, t56b; stappenplan in `STAPPENPLAN_VOLLEDIG.md`. |
| 20-24 | 20 klaar (t57-t58); 21 Wereldbank Pink Sheet (zilver, koper); 22 IRENA/ILO Renewable Energy and Jobs 2025; 23 CBS/TNO Monitor Energiearmoede 2019-2025; 24 IEA Global Hydrogen Review 2025 (CC BY 4.0) en de LCOH-calculator van de European Hydrogen Observatory. |

| 25-30 | Klaar (21 nov): t63-t72 uit lokale data; stappenplannen in `STAPPENPLAN_VOLLEDIG.md` deel 2. |
| 37, 38 en versie 2 van 27 en 30 | Data klaar (23 nov): `eti.verdieping` → t77-t81; stappenplannen in `STAPPENPLAN_VOLLEDIG.md` deel 3; uitkomsten in `docs/deep_dives.md`. |
| 31 Power BI / Fabric | Wacht op Fabric-toegang (controle C04). |

Downloads die nog nodig zijn (12, 21-24 en versie 2 van 8, 15, 17): zie `docs/DOWNLOADS.md`.
