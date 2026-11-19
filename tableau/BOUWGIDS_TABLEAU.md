# Bouwgids Tableau: "Zon en opslag in Europa: eerste bevindingen"

Doel: in twee werksessies een openbaar Tableau-dashboard met de eerste bevindingen van dit project, gepubliceerd op
Tableau Public en gelinkt vanuit de README op GitHub. Power BI (met de DAX-toets) volgt later; het tweede dashboard in
deze gids ("Signalering Nederland") is daarvoor de Tableau-tweeling, zodat je de rekenregels alvast in de vingers hebt.

Stand van de data: 18 november 2026. Werktijd: ongeveer 2,5 uur voor sessie 1 en 2,5 uur voor sessie 2.

---

## Ontwerpnorm: geldt voor elk dashboard (vanaf 19 november)

Elk dashboard wordt **vooraf** gebouwd volgens de beoordeling in `docs/ontwerp_beoordeling.md` (vier categorieën, elk 1-5,
samen /20). Doel: **16 of hoger vóór publicatie**, zonder nawerk. Publiek: directie, investeerders, recruiters, zonexperts,
beleidsmakers. Doel van de reeks: voortgang van zon, batterijen en investeringen volgen. Beslissing: welke vervolgstudie.

**Vaste opbouw (van boven naar onder)**
1. **Titel = de bevinding** (een bewering met een getal), subtitel = bron, periode (2026 "tot 15 november") en eenheid.
2. **KPI-rij**: vier tegels uit `t50_kpi_dashboards.csv` (filter `Dashboard`). Per tegel `Tekst` groot (24-28 pt), daaronder
   `Vergelijking` en `Referentie` (11 pt grijs). Pijlkleur uit `Richting`: goed = #1F9E89, slecht = #C4457A, neutraal = grijs.
3. **Hoofdgrafiek** (volle breedte) die de titel bewijst. Daarna hoogstens **drie** ondersteunende grafieken. Meer dan
   vijf grafieken: splitsen of naar een ander dashboard.
4. **Twee talen**: elk dashboard verschijnt in het Nederlands en het Engels (sectie 17); Engelse teksten in `tableau/teksten_en.md`.
5. **Onderrand**: links "Wat we niet zeker weten" (2-3 punten), rechts "Wat volgt" (welke vervolgdashboards of -studies,
   met nummer) en de link naar GitHub.

**Grafieken en betrouwbaarheid**
- Juiste vorm: tijd = lijn, rangorde = gesorteerde staaf, samenstelling = gestapelde staaf (100% als het om aandeel gaat),
  verband = spreiding. Geen taart, geen dubbele y-as, geen 3D.
- Staafassen beginnen bij 0. Een lijnas mag ingekort, maar dan met referentielijn en de as-titel met eenheid.
- Kaarten alleen met een gesorteerde staaf ernaast (grote landen lijken anders belangrijker dan ze zijn).
- Elke as en tooltip heeft een eenheid; AC/DC, nominaal/reëel en voorlopig (CBS **) staan erbij waar dat speelt.

**Kleur en rust**
- Paletten uit `tableau/Preferences.tps` (gecontroleerd op kleurenblindheid). **Eén betekenis per kleur per dashboard.**
  Bronnen altijd: zon goud #C9961A, wind cyaan #2A9DB5, kern violet #7A5195, gas/fossiel sienna #A0522D, water/bio
  teal #1F9E89. Nederland altijd oranje #E39A2D; de rest grijs als Nederland de focus is.
- Hoogstens vijf kleuren per grafiek; meer categorieën = "overige" of kleine multiples.
- Labels direct aan de lijn of staaf in plaats van een legenda waar het kan; legenda vlak bij de grafiek. 2 decimalen
  voor ratio's, geen decimalen voor euro's en uren, duizendtalscheiding.
- Status en signaal altijd met tekst, nooit alleen kleur.

**Bruikbaarheid**
- Elk getal heeft een vergelijking (vorig jaar, EU-mediaan, doel of tweede bron).
- Referentielijnen voor drempels (capture rate 1,0; marktprijs 280 €/kWh; groeidrempel; LCOE).
- "Wat volgt" verwijst naar concrete vervolgdashboards (1-24) of de onderzoeksagenda in het naslagwerk.

**Zelftoets vóór publicatie** (schrijf de score in de commit): hiërarchie __/5 · grafieken __/5 · rust __/5 · bruikbaarheid __/5.
Onder 16: eerst de laagste categorie verbeteren.

---

## 0. Voorbereiden (15 minuten)

1. **Installeer Tableau Desktop Public Edition** (gratis, draait op de Mac): <https://public.tableau.com/s/download>. Je maakt daarbij een gratis Tableau Public-profiel aan.
   Alles wat je naar Tableau Public publiceert is openbaar. Dat is hier geen probleem: alle data komt uit openbare bronnen.
2. **Maak de databestanden** (vanuit de repo):
   ```bash
   cd ~/projecten/tjebbel/set_up/energy_dashboard/solar-storage-investment-lab
   PYTHONPATH=src .venv/bin/python -m eti.tableau_export
   ```
   Dat schrijft vijf bestanden naar `tableau/data/` (zie hieronder). Ze staan er al, maar zo weet je zeker dat ze bij de
   laatste analyse horen.
3. **Maak een map voor je werkboek**: `tableau/` in de repo. Sla het werkboek op als `tableau/zon_opslag_europa.twbx`.

De menunamen in deze gids zijn Engels (standaard in Tableau). Staat Tableau in het Nederlands, dan heten ze anders;
de volgorde van de stappen blijft gelijk.

### De vijf bestanden

| Bestand | Een rij is | Voor werkblad |
|---|---|---|
| `t1_zonejaar.csv` | biedzone x jaar (37 zones, 2019-2026) | 1 Kerncijfers, 2 Kaart, 3 Verloop, 4 Segmenten |
| `t2_land_maand.csv` | biedzone x maand | 8 Signalering (tweede dashboard) |
| `t3_batterij.csv` | scenario x doelrendement | 6 Batterij |
| `t4_schokjaar.csv` | biedzone x oorzaak | 5 Schokjaar |
| `t5_bronnen.csv` | jaar x vergelijking | 7 Twee bronnen |

Belangrijke kolommen: `Heel jaar` (1 = volledig jaar, 0 = 2026 tot 15 november); `Segment zekerheid` (`grensgeval` of
`stevig`, uit de gevoeligheidstoets); `Landcode` (ISO-3, voor de kaart).

---

## Sessie 1 (ongeveer 2,5 uur): data en de eerste vier werkbladen

### 1. Data verbinden (15 minuten)

1. *Connect* > *To a File* > *Text file* > kies `tableau/data/t1_zonejaar.csv`.
2. **Landinstelling (belangrijk op een Nederlandse Mac).** De bestanden gebruiken een punt als decimaalteken. Klik in het
   tabblad *Data Source* met rechts op de gegevensbron (bovenaan, de naam van het bestand) > *Locale...* > *English (United States)*.
   Doe je dit niet, dan leest Tableau `0.615` mogelijk als `615`. Controle: in de voorbeeldtabel staat bij Nederland 2025
   `Capture rate zon` = 0,615 en `Dagspreiding` = 123,8.
3. Controleer de typen (icoontje boven de kolom): `Jaar` = getal (geheel), en zet het met rechts > *Convert to Dimension*
   in het werkblad; `Landcode` = tekst, met rechts > *Geographic Role* > *Country/Region*; `Maand` (in t2) = datum.
4. Voeg de andere vier bestanden toe als **aparte gegevensbronnen** (*Data* > *New Data Source*), niet als koppeling.
   Elk werkblad gebruikt maar één bron; dat houdt het eenvoudig. Stel bij elke bron de landinstelling in (stap 2).
5. Hernoem de bronnen (rechts > *Rename*) naar `Zonejaar`, `Maand`, `Batterij`, `Schokjaar`, `Bronnen`.

### 2. Werkblad 1 "Kerncijfers" (20 minuten)

Vier grote getallen voor Nederland in het gekozen jaar.

1. Maak een parameter: *Data* pane > pijltje > *Create Parameter* > naam `Gekozen jaar`, type *Integer*, *List*, waarden
   2019 tot en met 2026, standaard **2025**. Rechts > *Show Parameter*.
2. Maak een berekend veld `Is gekozen jaar`: `[Jaar] = [Gekozen jaar]`. Sleep het naar *Filters* > *True*.
3. Sleep `Zone` naar *Filters* > alleen `NL`.
4. Sleep `Measure Names` naar *Columns* en `Measure Values` naar *Text*. Houd in *Measure Values* alleen over:
   `AVG(Capture rate zon)`, `AVG(Batterij-omzet per MW)`, `AVG(Negatieve uren)`, `AVG(Dagspreiding)`.
5. Opmaak: capture rate als getal met 2 decimalen; batterij-omzet als valuta (euro, 0 decimalen); lettergrootte 24.
6. Controle voor 2025: 0,62 · € 61.041 · 584 · 123,8.

### 3. Werkblad 2 "Kaart: capture rate zon" (25 minuten)

1. Dubbelklik op `Landcode`: Tableau maakt een kaart. Zet het markeringstype op *Map* (gevulde kaart).
2. Sleep `Capture rate zon` naar *Color* en zet de aggregatie op *Average*.
3. Filter `Is gekozen jaar` = True (rechts op het filter > *Apply to Worksheets* > *All Using This Data Source*, dan geldt
   het jaar voor alle werkbladen op deze bron).
4. Kleur: *Edit Colors* > een reeks van **één kleur, licht naar donker** (bijvoorbeeld *Orange* of *Blue*), en vink
   *Reversed* aan zodat **lage** capture rate donker is (daar is zon het minst waard). Geen regenboog.
5. Tooltip: `<Zonenaam>: capture rate zon <AVG(Capture rate zon)>, <AVG(Negatieve uren)> negatieve uren`.
6. Let op: landen met meer zones (Italie, Noorwegen, Zweden, Denemarken) krijgen het ongewogen gemiddelde van hun zones.
   Zet dat in de tooltip of de toelichting.

### 4. Werkblad 3 "Verloop per regio" (25 minuten)

1. `Jaar` naar *Columns* (als dimensie, discreet), `AVG(Capture rate zon)` naar *Rows*, `Regio` naar *Color*.
2. Dikte van de lijn: dun (2 px); markeringen aan.
3. Referentielijn: *Analytics* > *Constant Line* = 1,0 met label "zon even veel waard als het gemiddelde uur".
4. Maak 2026 herkenbaar als voorlopig: berekend veld `Periode` = `IF [Heel jaar] = 1 THEN "heel jaar" ELSE "tot 15 nov" END`,
   naar *Shape* (open rondje voor 2026) of noem het in de titel.
5. Titel: "Zon wordt overal minder waard (gemiddelde capture rate per regio)".

### 5. Werkblad 4 "Segmenten" (30 minuten)

1. `Jaar` naar *Columns*, `CNTD(Zone)` naar *Rows* (rechts op `Zone` > *Measure* > *Count (Distinct)*), `Segment` naar *Color*.
2. Vaste kleur per segment (*Edit Colors*), daarna nooit meer wijzigen:
   Vlakke prijzen = grijs · Batterijmarkt = blauw · Zon houdt waarde = oranje · Zonverzadigd = paars · Middenveld = lichtgrijs.
3. Sleep `Segment zekerheid` naar *Detail* en zet in de tooltip: "<Zone>: <Segment> (<Segment zekerheid>, <Segment stabiel (aandeel)> van de varianten)".
4. Optioneel: `Segment zekerheid` als filter, zodat de kijker alleen de stevige toewijzingen kan tonen.
5. Ondertitel (verplicht, dit is een bevinding): "In 2023-2025 is 16 tot 23 van de 37 zones een grensgeval; Nederland 2025 ook."

Sla op (*File* > *Save to Tableau Public As...* kan nog niet zonder publiceren; gebruik *File* > *Save As* > `.twbx` in de
repo-map `tableau/`). Desktop Public Edition kan lokaal opslaan.

---

## Sessie 2 (ongeveer 2,5 uur): drie werkbladen, dashboards, publiceren

### 6. Werkblad 5 "Schokjaar 2026" (25 minuten), bron `Schokjaar`

1. `Zone` naar *Rows*, `SUM(Euro per MWh)` naar *Columns*, `Oorzaak` naar *Color*: een gestapelde liggende staaf.
2. Sorteer `Zone` op `MAX(Prijsstijging totaal)`, aflopend.
3. Kleuren: Gas = donkerblauw, Zon = geel, Wind = lichtblauw, Niet verklaard = grijs.
4. Referentielijn bij 0.
5. Titel: "Prijsstijging jan-okt 2026 tegen 2025: driekwart is gas". Toelichting: "Model 2019-2025 per zone en maand
   (gas, zon, wind); 'niet verklaard' bevat onder meer waterstanden (Noorwegen), CO2-prijs en de windstille week."

### 7. Werkblad 6 "Batterij: wat mag hij kosten?" (25 minuten), bron `Batterij`

1. Filter `Doelrendement` = 8%.
2. `Scenario` naar *Rows*, `SUM(Hoogste bouwkosten per kWh)` naar *Columns*; sorteer aflopend.
3. Referentielijn: *Analytics* > *Reference Line* > waarde `AVG(Bouwkosten nu per kWh)` (280), label "bouwkosten nu".
4. Kleur: staven boven 280 een kleur, eronder grijs: berekend veld `Haalbaar` = `SUM([Hoogste bouwkosten per kWh]) >= 280`.
5. Titel: "Alleen de dagmarkt: net haalbaar zonder netkosten; met stapeling ruimte zolang FCR en aFRR betalen".

### 8. Werkblad 7 "Twee bronnen voor zon" (15 minuten), bron `Bronnen`

1. `Jaar` naar *Columns*, `SUM(Verschil (%))` naar *Rows*, `Vergelijking` naar *Color*. Referentielijn bij 0.
2. Titel: "Energy-Charts tegen Ember: het verschil verdwijnt zonder dekkingsgaten".

### 9. Dashboard 1 "Eerste bevindingen" (30 minuten)

1. *Dashboard* > *New Dashboard*; *Size* > *Fixed* 1200 x 1500 (lang scrollend dashboard leest goed op Tableau Public).
2. Indeling van boven naar beneden:
   - titel (tekst): "Zon en opslag in Europa: eerste bevindingen" en een regel: "37 biedzones, 2019 tot 15 november 2026. Bron: Energy-Charts, Ember, ENTSO-E, FRED. Analyse en code: github.com/<jouw-naam>/solar-storage-investment-lab";
   - rij 1: werkblad 1 (kerncijfers) met de parameter `Gekozen jaar` ernaast;
   - rij 2: werkblad 2 (kaart) links, werkblad 3 (verloop) rechts;
   - rij 3: werkblad 4 (segmenten);
   - rij 4: werkblad 5 (schokjaar) links, werkblad 6 (batterij) rechts;
   - rij 5: werkblad 7 (twee bronnen) en een tekstvak "Wat we niet zeker weten" met drie regels uit het onzekerhedenregister
     (segmentgrenzen, capture rate park of dak, aFRR-prijs).
3. Maak de kaart een filter: selecteer de kaart > trechtericoon *Use as Filter*. Klikken op een land filtert dan het verloop.
4. Verberg dubbele legenda's; houd per kleur één legenda over.

### 9b. Revisie dashboard 1 "Eerste bevindingen" (19 november, na de ontwerpbeoordeling; ongeveer 1,5 uur)

Score vooraf 12/20 (hiërarchie 2, grafieken 4, rust 3, bruikbaarheid 3). Doel: 16+. Werk in een **kopie** van het tabblad
(rechts op het dashboard > *Duplicate*), zodat de gepubliceerde versie blijft werken tot de nieuwe klaar is.

0. **Kleuren eenmalig**: kopieer `tableau/Preferences.tps` naar `~/Documents/My Tableau Repository/Preferences.tps` en herstart
   Tableau. Je krijgt negen paletten: *ETI segmenten*, *ETI oorzaak prijs*, *ETI focus*, *ETI haalbaar*, *ETI capture rate*, *ETI bronnen*, *ETI kwadrant*, *ETI status*, *ETI richting*.
   Regel: één betekenis per kleur. Blauw (#4A5FC1) is voortaan alleen *Batterijmarkt*.
1. **KPI-tegels** (t47, als extract; filter `Jaar` gelijk aan `Gekozen jaar`). Per KPI een werkblad: `Waarde NL` groot (28 pt),
   daaronder `Pijl` + `Vorig jaar` en `EU-mediaan` (11 pt grijs); `Lezing` in de knopinfo. Vijf tegels naast elkaar bovenaan,
   elk 20% breed, dunne rand. **Controle 2025:** Batterij-omzet 61.041 ▲ (52.710; EU 52.655) · Capture rate 0,615 ▲
   (0,603; EU 0,615, *op EU-mediaan*) · Negatieve uren 584 ▲ (458; EU 265) · Dagspreiding 124 ▲ (114; EU 111) ·
   Gemiddelde prijs 87 ▲ (77; EU 86). Voor 2026 "(tot 15 nov.)" in de titel: `Heel jaar` = 0.
2. **Kaart**: palet *ETI capture rate* (divergerend, midden 1,0 = even veel waard als het gemiddelde uur; magenta = minder waard).
   Legenda direct onder de kaart, 2 decimalen, titel `Capture rate zon (1,00 = gemiddeld uur)`.
3. **Rangorde naast de kaart** (t48, filter `Toon` = waar). Staaf `Capture rate zon` per `Zone`, gesorteerd, `Groep` op kleur
   (Top 5 groen #1F9E89, Bodem 5 magenta #C4457A, Nederland oranje #E39A2D). **Controle 2025:** top FI, IT-North,
   IT-Centre-North, NO2, NO1; bodem PT, NO4, DE-LU, BE, AT; NL rang 19 van 37.
4. **Lijnen per regio**: palet *ETI focus*: NW-Europa oranje, de rest grijs. Legenda weg; label aan het eind van de lijn
   (*Label* > *Line Ends*).
5. **Batterij** (t3b in plaats van t3): `Scenario leesbaar` op Rijen, gesorteerd op `Volgorde`; `Scenario soort` in de knopinfo en het label `Basisgeval` vet (stapelen zonder capaciteitsvergoeding; het hoge scenario heet `Hoog: als capaciteitsprijzen herstellen`); `Haalbaar` op kleur met
   *ETI haalbaar*. Legenda-titel `Haalbaar bij marktprijs 280 €/kWh`.
6. **Prijsstijging 2026** (t4b in plaats van t4): tien zones plus `Overige 18 (gemiddeld)`, gesorteerd op `Volgorde`;
   `Oorzaak` met *ETI oorzaak prijs* (Gas sienna, Wind cyaan, Zon goud, Niet verklaard grijs; zelfde bronkleuren als op alle dashboards); `Toelichting` in de knopinfo.
7. **Segmenten** (t1 met t49 via een relatie op `Segment`): kleur *ETI segmenten*, `Segment` gesorteerd op `Volgorde`
   (vlak → zon houdt waarde → middenveld → batterijmarkt → verzadigd). Overweeg *Percent of Total* per jaar; labels op de segmenten.
8. **Energy-Charts tegen Ember**: van dit dashboard af; naar dashboard 7 naast de controlematrix.
9. **Slot "Wat volgt"** naast "Wat we niet zeker weten": `Vervolg: dashboard 2 (dekt zon zijn kosten, maand voor maand) ·
   4 (hoe snel wordt zon goedkoper) · 8 (netcongestie en het einde van de saldering) · 14 (rendement tegen vermeden CO2).`
10. **Volgorde**: titel → KPI's → kaart + rangorde → lijnen → segmenten → batterij + prijsstijging → onzekerheid + wat volgt.
11. **Publiceren** als nieuwe versie van hetzelfde tabblad (link blijft gelijk); nieuwe afbeelding over
    `docs/img/tableau_eerste_bevindingen.png`.

### 10. Dashboard 2 "Signalering Nederland" (stappenplan 19 november, ongeveer 2,5 uur)

**Ontwerpnorm voor dit dashboard** (eerst doen, zie bovenaan): KPI-rij uit t50 met filter `Dashboard` = 2; paletten uit `Preferences.tps`; onderrand met "Wat we niet zeker weten" en "Wat volgt": dashboard 8 (einde saldering, netcongestie), 13 (flexibiliteit), 16 (atlas van de eendencurve). KPI-controle: `6 van 11` maanden gedekt (2025: 5 van 12); capture rate 0,59 (EU 0,61); laatste maand `Schok (z = 5.4)`, 27 van 37 zones. Zelftoets ≥ 16/20 vóór publiceren.

**Boodschap van het dashboard.** In het najaar van 2026 is de stroomprijs in Nederland drie maanden achter elkaar een
schok: de z-score is 4,1 in september, 3,5 in oktober en 5,4 in november (tot 15 november). Toch dekt zon in 2026 in zes
van de elf maanden zijn kostprijs. Het dashboard rekent hetzelfde als de DAX-maten en Python (66 van 66).

**Wat klaar staat:** `tableau/data/t2_land_maand.csv` (signalering NL), `t9_signalering_zones.csv` (heatmap Europa) en
`t10_dekking_nl.csv` (dekking per jaar). De verwachte uitkomst staat in `powerbi/maten_verwacht.csv`.

**Stap 0, voorbereiden (10 min).** Open `Zon en opslag in Europa.twbx`. Voeg via **Data > Nieuwe gegevensbron > Tekstbestand** t9 en t10
toe, elk als eigen bron (komma, UTF-8, landinstelling Engels (VS)). Zet ze meteen op **Extraheren**: zonder extract kun je
straks niet publiceren.

**Stap 1, werkblad "Signalering" (40 min, bron t2).** Volg de rekenregels van de oude stap 10 hieronder (parameter `LCOE`,
zeven berekende velden, `Toon jaar` als filter, tabelberekening alleen over `Maand`). Rond af op 2 decimalen.
Controle: januari 2026 = 107,66 · 107,51 · 40,12 · Gedekt · 1,11 · Gewoon; september 2026 = z-score 4,07 · Schok.

**Stap 2, de toets (10 min).** Werkblad > Kopiëren > Kruistabel, plak in TextEdit (platte tekst), sla op als
`resultaten/tableau_signalering_2026.txt` en draai:
`PYTHONPATH=src .venv/bin/python -m eti.powerbi_toets vergelijk resultaten/tableau_signalering_2026.txt`.
Verwacht: "66 van 66 waarden kloppen". Klopt het niet, stuur de uitvoer; dan is het bijna altijd de tabelberekening.

**Stap 3, werkblad "Schokken in Europa" (25 min, bron t9).** `Zonenaam` naar Rijen, `Maand` naar Kolommen (exacte maand,
discreet; of continu met *Vierkant* als markering), `Prijs signaal` naar Kleur: Gewoon lichtgrijs, Let op oranje,
Schok rood. Sorteer de zones op het aantal schokmaanden (rechtsklik `Zonenaam` > Sorteren > Veld: aantal, waar Prijs
signaal = Schok). Titel: `Prijsschokken per zone en maand, 2020-2026`. Subtitel: `Schok = prijs meer dan 3 standaardafwijkingen
van de twaalf maanden ervoor. 2026 tot 15 november.` Knopinfo: zone, maand, prijs, z-score.

**Stap 4, werkblad "Dekking zon NL" (20 min, bron t10).** `Jaar` (discreet) naar Kolommen, `SUM(Maanden)` naar Rijen,
`Status zon` naar Kleur (Gedekt groen, Krap oranje, Kosten niet gedekt rood, dezelfde kleuren als in Signalering),
`Scenario` naar Filters als **enkele waarde (lijst)**, getoond. Labels aan. Titel:
`In hoeveel maanden dekt zon zijn kostprijs? Nederland`.

**Stap 5, kerncijfers (15 min).** Drie kleine tekstwerkbladen, elk met filter Nederland en jaar 2026, lettergrootte 20 en vet:
gedekte maanden uit t10 (`SUM(Maanden)` met Scenario = LCOE 2025 en Status zon = Gedekt; verwacht 6), de hoogste
z-score uit t9 (`MAX(Prijs z-score)`; verwacht 5,40, november) en de gemiddelde capture-prijs zon uit t9
(`AVG(Capture-prijs zon)`; verwacht 92,79). Elk met een korte titel eronder: `maanden kostprijs gedekt`, `hoogste z-score`, `euro per MWh`.

**Stap 6, dashboard (30 min).** Nieuw dashboard *Signalering Nederland*, vaste grootte 1200 × 1150.
1. Bovenaan een tekstvak: titel `Signalering Nederland: najaar 2026 is een prijsschok` en subtitel
   `Dezelfde rekenregels als de DAX-maten en Python; 66 van 66 waarden gecontroleerd. Bron: Energy-Charts. 2026 tot 15 november.`
2. Rij 1: kerncijfers. Rij 2: Signalering (links, 60%) en Dekking (rechts, 40%). Rij 3: Schokken in Europa (volle breedte).
3. Parameter `LCOE` zichtbaar rechtsboven, met de uitleg: `Marge = capture-prijs min de kostprijs van zonnestroom (LCOE).
   De z-score vergelijkt de maand met de twaalf maanden ervoor.`
4. Buitenste opvulling 8 px; legenda's horizontaal onder hun grafiek; geen legendakolom rechts (zie de lessen van dashboard 1).

**Stap 7, publiceren (15 min).**
- Klik met rechts op het tabblad van elk dashboard > **Alle werkbladen verbergen**, zodat alleen de twee dashboards tabbladen zijn.
- **Server > Tableau Public > Opslaan in Tableau Public**, met dezelfde naam als dashboard 1. De bestaande viz wordt
  bijgewerkt en de link blijft gelijk. Zet op de pagina **Toon werkbladen als tabbladen** aan: bezoekers zien dan de twee
  dashboards als tabbladen.
- Controleer in de browser: het tabblad Signalering laat januari 2026 = 107,66 zien, en de LCOE-schuif werkt.

**Stap 8, GitHub (10 min).**
```bash
cd ~/projecten/tjebbel/set_up/energy_dashboard/solar-storage-investment-lab
# Dashboard > Afbeelding exporteren > docs/img/tableau_signalering.png
cp ~/Documents/"Mijn Tableau Repository"/Werkmappen/NL_solar.twbx tableau/NL_solar.twbx   # alleen als hij daar staat
git add tableau/NL_solar.twbx tableau/data/t9_signalering_zones.csv tableau/data/t10_dekking_nl.csv \
        resultaten/tableau_signalering_2026.txt docs/img/tableau_signalering.png README.md
git commit -m "Dashboard 2 Signalering Nederland: gepubliceerd en getoetst (66 van 66)"
git push
```
Voeg in de README onder het eerste dashboard een regel en de afbeelding toe: `Dashboard 2: Signalering Nederland`.
Laat daarna `PYTHONPATH=src .venv/bin/python -m eti.assurance_overzicht` zien wat de status van controle C03 is; geef de
uitkomst door, dan zet ik C03 op geslaagd.

#### Rekenregels (oorspronkelijke stap 10)

Dit zijn dezelfde rekenregels als in `powerbi/maten_analyse.dax`, met dezelfde verwachte uitkomst
(`powerbi/maten_verwacht.csv`). In Python is nagerekend dat deze Tableau-logica exact die waarden geeft.

1. Parameter `LCOE` (*Float*, standaard **67.39**, euro per MWh, Nederland 2025).
2. Berekende velden (*Analysis* > *Create Calculated Field*):

   | Veld | Formule |
   |---|---|
   | `Gem prijs` | `AVG([Gemiddelde prijs])` |
   | `Capture-prijs zon` | `AVG([Gemiddelde prijs]) * AVG([Capture rate zon])` |
   | `Marge zon` | `[Capture-prijs zon] - [LCOE]` |
   | `Status zon` | `IF ISNULL([Marge zon]) THEN NULL ELSEIF [Marge zon] < 0 THEN "Kosten niet gedekt" ELSEIF [Marge zon] < 5 THEN "Krap" ELSE "Gedekt" END` |
   | `Prijs z-score` | `(AVG([Gemiddelde prijs]) - WINDOW_AVG(AVG([Gemiddelde prijs]), -12, -1)) / WINDOW_STDEV(AVG([Gemiddelde prijs]), -12, -1)` |
   | `Prijs signaal` | `IF ISNULL([Prijs z-score]) THEN NULL ELSEIF ABS([Prijs z-score]) >= 3 THEN "Schok" ELSEIF ABS([Prijs z-score]) >= 2 THEN "Let op" ELSE "Gewoon" END` |
   | `Toon jaar` | `LOOKUP(MIN(YEAR([Maand])), 0)` |

3. Werkblad 8 "Signalering": `Zonenaam` naar *Filters* = Nederland; `Maand` naar *Rows* als **exacte maand, discreet**
   (rechts > *Month* in de tweede lijst, *Month May 2015*-vorm); `Measure Names` naar *Columns*; in *Measure Values*:
   `Gem prijs`, `Capture-prijs zon`, `Marge zon`, `Prijs z-score`; `Status zon` en `Prijs signaal` naar *Rows* rechts van `Maand`
   (rechts op het veld > *Discrete*, zodat ze als kolom met tekst verschijnen).
4. **Tabelberekening instellen** (anders klopt de z-score niet): rechts op `Prijs z-score` > *Edit Table Calculation* >
   *Specific Dimensions* > alleen `Maand` aangevinkt. Doe hetzelfde voor `Prijs signaal` (dat rekent met de z-score).
5. **Jaar filteren zonder het venster te breken**: zet `Toon jaar` op *Filters* > *Range of values* > 2026 tot 2026.
   Een gewoon filter op `Jaar` = 2026 haalt de twaalf maanden ervoor weg en dan is het venster leeg. `Toon jaar` is een
   tabelberekening en filtert pas na de berekening.
6. Kleur `Status zon`: Gedekt = groen, Krap = oranje, Kosten niet gedekt = rood, altijd met de tekst erbij (niet alleen kleur).
7. **Toets**: rond alle getallen af op 2 decimalen (*Format* > *Number* > 2 decimalen) en vergelijk met de verwachting:
   - klik op het werkblad, *Worksheet* > *Copy* > *Crosstab*; plak in TextEdit (*Format* > *Make Plain Text*) en sla op als
     `resultaten/tableau_signalering_2026.txt`. Een export naar Excel (`.xlsx`) mag ook;
   - `PYTHONPATH=src .venv/bin/python -m eti.powerbi_toets vergelijk resultaten/tableau_signalering_2026.txt`
   - De vergelijker herkent zelf de maandkolom ("January 2026" of "januari 2026"), het scheidingsteken en een decimale komma.
   - Verwacht: "66 van 66 waarden kloppen". Januari 2026: 107,66 · 107,51 · 40,12 · Gedekt · 1,11 · Gewoon.
8. Dashboard 2: werkblad 8 plus de parameter `LCOE` zichtbaar, met de uitleg: "Marge = capture-prijs min de kostprijs van
   zonnestroom (LCOE). De z-score vergelijkt de maand met de twaalf maanden ervoor."

**Uitbreidingen dashboard 2 (19 november, ochtend; optioneel, ongeveer 45 minuten).**
9. **Annotaties** (t42, als extract). Voeg t42 toe; in werkblad 8 of een tijdlijnwerkblad: `Datum` als referentielijnen via een
   tweede bron is omslachtig, dus gebruik *Annotate > Point* op de maanden 2022-08 (`piek gas- en stroomprijzen`) en zet in het
   tekstvak onder het dashboard: `Vanaf 1 januari 2027 vervalt de salderingsregeling: thuisbatterijen en zelfverbruik worden
   belangrijker.` Filter t42 op `Dashboards` bevat 2.
10. **Werkblad 9 "Kannibalisatie"** (t43). `Zonaandeel %` (x) tegen `Capture rate zon` (y), markering Cirkel, `Jaar` op Kleur
    (doorlopend grijs naar donker), filter `Zone` met NL gemarkeerd (label alleen NL). Trendlijn Lineair. Titel:
    `Hoe meer zon, hoe minder elke MWh zon waard is`. **Controle:** helling ongeveer −0,011 per procentpunt; NL 2024: 18% en 0,60,
    NL 2025: 21% en 0,62. Tooltip: `Goed nieuws voor wie stroom koopt (lagere middagprijzen), slecht nieuws voor wie zon bouwt.`
11. **Context-KPI**: tekstvak `Zon leverde in 2025 21% van de Nederlandse stroom (CBS, voorlopig; Ember: 28,5 TWh tegen CBS 25,8 TWh).`
12. **Label controleren**: de marge rekent met de **capture-prijs**, niet met de gemiddelde prijs. Zet dat letterlijk in de as-titel.

#### 10-EN. Dashboard 2 direct in het Engels bouwen (vanaf 19 november: alle nieuwe dashboards alleen in het Engels)

Werk in `tableau/Solar and storage in Europe.twbx` (landinstelling **English (US)**, punt als decimaalteken).
Teksten uit `tableau/teksten_en.md`, sectie "Dashboard 2 Signals Netherlands".

0. **Bronnen** uit `tableau/data_en/`: t2, t9, t10, t43, t50 (elk *Extraheren*). Hernoem de velden die je gebruikt met `tableau/veldnamen_en.csv`.
1. **Parameter** `LCOE` (Float, 67.39).
2. **Berekende velden, met Engelse namen** (de toets herkent deze namen en waarden):

   | Field | Formula |
   |---|---|
   | `Avg price` | `AVG([Gemiddelde prijs])` |
   | `Solar capture price` | `AVG([Gemiddelde prijs]) * AVG([Capture rate zon])` |
   | `Solar margin` | `[Solar capture price] - [LCOE]` |
   | `Solar status` | `IF ISNULL([Solar margin]) THEN NULL ELSEIF [Solar margin] < 0 THEN "Costs not covered" ELSEIF [Solar margin] < 5 THEN "Tight" ELSE "Covered" END` |
   | `Price z-score` | `(AVG([Gemiddelde prijs]) - WINDOW_AVG(AVG([Gemiddelde prijs]), -12, -1)) / WINDOW_STDEV(AVG([Gemiddelde prijs]), -12, -1)` |
   | `Price signal` | `IF ISNULL([Price z-score]) THEN NULL ELSEIF ABS([Price z-score]) >= 3 THEN "Shock" ELSEIF ABS([Price z-score]) >= 2 THEN "Watch" ELSE "Normal" END` |
   | `Show year` | `LOOKUP(MIN(YEAR([Maand])), 0)` |

   (Gebruik in de formules de oorspronkelijke kolomnaam als je de velden nog niet hebt hernoemd; na hernoemen past Tableau de formule zelf aan.)
3. **Werkblad `Signals`**: filter Zone name = Netherlands, `Show year` = 2026 (bereik), Month als exacte maand discreet op Rows,
   `Solar status` en `Price signal` discreet op Rows, Measure Values met de vier getallen. Tabelberekening: *Specific Dimensions* > alleen Month.
   Controle: January 2026 = 107.66 · 107.51 · 40.12 · Covered · 1.11 · Normal.
4. **Toets**: Worksheet > Copy > Crosstab > TextEdit (platte tekst) > `resultaten/tableau_signalering_2026_en.txt`, dan
   `PYTHONPATH=src .venv/bin/python -m eti.powerbi_toets vergelijk resultaten/tableau_signalering_2026_en.txt` → "66 van 66".
5. **Werkblad `Shocks`** (t9): heatmap Zone name × Month, kleur `Prijs signaal`: Normal lichtgrijs, Watch oranje #E39A2D, Shock magenta #C4457A.
6. **Werkblad `Coverage`** (t10): Year × SUM(Maanden), kleur Status zon: Covered teal #1F9E89, Tight oranje, Costs not covered magenta. Scenario als enkele-waardefilter.
7. **Werkblad `Cannibalisation`** (t43): Solar share % × Solar capture rate, trendlijn lineair, alleen NL gelabeld, rest grijs.
8. **KPI-rij** uit t50 met filter Dashboard = 2, palet *ETI richting* (good teal, bad magenta, neutral grijs), legenda verborgen.
9. **Dashboard `Signals Netherlands`**, vaste grootte 1200 × 1600: titel en subtitel; KPI-rij; Signals (60%) | Coverage (40%);
   Shocks volle breedte; Cannibalisation + tekstvak met parameteruitleg; onderrand "What we don't know for sure" en "What comes next".
   Legenda's direct onder hun grafiek, geen legendakolom rechts.
10. **Zelftoets ≥ 16/20**, dan *Server > Tableau Public > Save* als **`Solar and storage in Europe`** (tab "Signals Netherlands").

### 11. Publiceren op Tableau Public (15 minuten)

1. *File* > *Save to Tableau Public As...* > log in > naam: `Zon en opslag in Europa - eerste bevindingen`.
2. Tableau zet de csv's om in een extract en uploadt alles. In de browser opent je werkboek.
3. Op de pagina van het werkboek: *Edit Details* (potloodje):
   - beschrijving: twee zinnen over de vraag (loont een batterij naast een zonnepark?) en een link naar de GitHub-repo;
   - *Show Workbook Sheets as Tabs* aan (dan zijn beide dashboards bereikbaar);
   - *Allow access*: downloaden toestaan (goed voor een portfolio: iedereen kan zien hoe het gebouwd is).
4. Kopieer de link (*Share* > *Copy Link*).

### 12. Op GitHub zetten (15 minuten)

1. Maak een schermafbeelding: in Tableau *Dashboard* > *Export Image...* > `docs/img/tableau_eerste_bevindingen.png`.
2. Voeg aan `README.md` (onder *Key findings*) toe:
   ```markdown
   ## Interactive dashboard (Tableau Public)

   [![Zon en opslag in Europa: eerste bevindingen](docs/img/tableau_eerste_bevindingen.png)](<LINK-NAAR-TABLEAU-PUBLIC>)

   37 European bidding zones, 2019 to November 2026: solar capture rates, market segments (with a sensitivity check),
   the 2026 price shock split into gas, solar, wind and unexplained, and the battery cost at which an 8% return is still
   possible. Built with Tableau Desktop Public Edition from `tableau/data` (`python -m eti.tableau_export`).
   Build guide: [tableau/BOUWGIDS_TABLEAU.md](tableau/BOUWGIDS_TABLEAU.md).
   ```
   GitHub kan een Tableau-dashboard niet insluiten; een klikbare afbeelding is de gebruikelijke manier.
3. Zet in de repo: `tableau/zon_opslag_europa.twbx`, `tableau/data/*.csv`, `docs/img/tableau_eerste_bevindingen.png`.
   Het `.twbx`-bestand bevat de data al; dat is een paar MB en mag in Git.

---

### 13. Dashboard 3 "Kernenergie in Europa en de wereld" (donderdag 19 november, ongeveer 2 uur)

**Ontwerpnorm voor dit dashboard** (eerst doen, zie bovenaan): KPI-rij uit t50 met filter `Dashboard` = 3; paletten uit `Preferences.tps`; onderrand met "Wat we niet zeker weten" en "Wat volgt": dashboard 8 (Nederlandse kerncentrales), 9 (EU), 11 (China), 20 (koolstofvrij per uur). Bronkleuren volgens de norm (kern violet, zon goud, wind cyaan, fossiel sienna, water/bio teal). KPI-controle: `2,805 tegen 2,807 TWh`; Europa `996 tegen 444 TWh`; `1.03 tegen 0.61`. Zelftoets ≥ 16/20 vóór publiceren.

**Boodschap.** Zon en kern leverden in 2025 wereldwijd evenveel stroom (2807 en 2805 TWh). In Europa levert kern nog ruim
twee keer zoveel als zon, maar kernstroom houdt zijn marktwaarde (capture rate 1,00) en zon niet (0,61).

**Bronnen.** Voeg t6, t7 en t8 toe als eigen bron, elk meteen als extract. Gebruik dezelfde instellingen als bij t1–t5.

1. **"Kern en zon, wereld en Europa"** (t6). `Jaar` (continu) op Kolommen, `SUM(Opwek TWh)` op Rijen, `Bron` op Kleur
   (palet *ETI bronnen*: Kernenergie violet #7A5195, Zon goud #C9961A, Wind cyaan #2A9DB5, Fossiel sienna #A0522D, Water/bio teal #1F9E89). `Gebied` op Filters en als keuzelijst
   (Wereld, Europa, China, Verenigde Staten, Frankrijk, Duitsland). Titel: `Zon haalt kern in: wereld 2025, 2807 tegen 2805 TWh`.
   **Controle:** Wereld 2025, Kernenergie 2805 en Zon 2807; Europa 2025, Kernenergie 996.
2. **"Koers per land"** (t7). `Land` op Rijen, gesorteerd op `Kern verschil 2015-2025 TWh`; die meting op Kolommen
   (staven rond nul), `Koers kern` op Kleur (Uitbouw groen, Herstart lichtgroen, Stabiel grijs, Afbouw oranje, Gestopt rood,
   Geen gegevens 2025 wit met rand). **Controle:** China +314, Duitsland −92, Japan *Herstart*, Oekraïne *Geen gegevens 2025*.
3. **"Schoon met kern?"** (t7). Spreidingsdiagram: `Aandeel kern 2025 %` (x) tegen `CO2 gram per kWh 2025` (y),
   `Kern TWh 2025` op Formaat, `Europa` op Kleur, `Land` als label (alleen de vijf grootste en Zweden, Frankrijk, Duitsland).
   **Controle:** Frankrijk 68% en 41 g, Zweden 27% en 35 g, Duitsland 0% en 334 g.
4. **"Marktwaarde"** (t8). `Jaar` op Kolommen, `AVG(Capture rate)` op Rijen, `Bron` op Kleur. Referentielijn op 1,0 met het label
   `even veel waard als het gemiddelde uur`. **Controle:** 2025: kern 1,03, zon 0,61. Subtitel: `14 Europese landen, gewogen
   naar kernproductie per zone; 2026 tot 15 november.`
5. **Dashboard** 1200 × 1200, in deze volgorde: titel, werkblad 1 (volle breedte), dan 2 en 3 naast elkaar, dan 4. Zet er een
   tekstvak bij met de beperkingen: Oekraïne heeft geen cijfer voor 2025; het vermogen van België in Ember klopt niet; de koers
   is een rekenregel (minstens 10% en 2 TWh), geen beleidsoordeel.
6. **Publiceren en GitHub**: zoals stap 10, stappen 7 en 8; afbeelding `docs/img/tableau_kernenergie.png`.

**Uitbreidingen dashboard 3 (19 november, ochtend; ongeveer 40 minuten).**
7. **Werkblad 5 "Eén GW is niet één GW"** (t44, als extract). Staaf per land (top 8 op `Kern TWh 2025`): `Kernvermogen GW 2025`
   naast `GW zon voor kern-TWh`, met `Benutting kern 2025` en `Benutting zon 2025` in de knopinfo. Titel:
   `Voor de kernstroom van de VS is ruim 4x zoveel zonvermogen nodig`. **Controle:** VS 97 GW kern, 427 GW zon, benutting
   0,93 tegen 0,21; Frankrijk 0,73 tegen 0,12, 382 GW.
8. **Tekstvak "Nederland"** (geen data, alleen tekst met bron): `Het kabinet wil ten minste vier kerncentrales; de eerste in 2035
   is volgens de minister niet meer realistisch; investering 20–30 miljard euro exclusief financiering; besluit over centrales 3
   en 4 rond 2028.` Bronnen in de knopinfo: Kamerbrieven KGG (11-02-2025, voortgangsbrief 2025), Rijksoverheid 19-06-2026.
9. **Twee kanten, geen oordeel**: subtitel `Per MWh is zon goedkoper; per beschikbaar uur levert kern meer. Systeemkosten
   (opslag, net) en bouwrisico (vertraging, overschrijding) bepalen wie gelijk krijgt.`
10. **Annotaties** uit t42 (filter op 3): Fukushima 2011, Duitsland dicht 15-04-2023, NL besluit reikwijdte 26-01-2026.

### 14. Dashboard 7 "Controlematrix en risicokaart" (vrijdag 20 november, ongeveer 2 uur)

**Ontwerpnorm voor dit dashboard** (eerst doen, zie bovenaan): KPI-rij uit t50 met filter `Dashboard` = 7; paletten uit `Preferences.tps`; onderrand met "Wat we niet zeker weten" en "Wat volgt": C03 (Tableau-toets vandaag), C04 (Power BI), C10 (grensstromen), C13 (CBS tegen Ember), C15 (statuscodes). Statuskleuren: Geslaagd #1F9E89, met beperking #8CCFC3, Afwijking verklaard #E39A2D, Afwijking open #C4457A, Open grijs. KPI-controle: `9 van 21` geslaagd, 7 open. Nieuw: werkblad "Externe validatie" (t52): tabel met Onderwerp, Ons project, Extern, Oordeel (kleur: sluit aan teal, afwijking open magenta), Bron in de knopinfo. Zelftoets ≥ 16/20 vóór publiceren.

**Boodschap.** Achttien controles (bijgewerkt 19 november): zes geslaagd, twee geslaagd met beperking, vijf afwijkingen die
verklaard zijn, één open afwijking (CBS en Ember verschillen 10% in zonnestroom) en vier die nog open staan. Het grootste risico is de keuze van de emissiefactor. Dit is een beoordeling van de gereedheid, geen
accountantsverklaring.

**Voorbereiden.** Laat je toetsuitkomst van donderdag aan mij weten. Ik zet controle C03 daarna op *Geslaagd* en draai
`PYTHONPATH=src .venv/bin/python -m eti.assurance_overzicht --tests` opnieuw. Voeg t15 en t16 toe als extract.

1. **"Gegevensstroom"**: een Afbeelding-object in het dashboard met `docs/img/keten.png` (de keten van bron tot document).
2. **"Controlematrix"** (t15). `Controle`, `Domein` en `Doel` op Rijen; `Uitkomst` als tekst; `Status` op Kleur
   (palet *ETI status*: Geslaagd teal, met beperking lichtteal, Afwijking verklaard oranje, Afwijking open magenta, Open grijs). Opmaak: rijstreping uit,
   alleen dunne lijnen tussen de domeinen. **Controle:** 21 rijen; C02 = `66 van 66 waarden gelijk`; C18 en C21 = Geslaagd; C19 en C20 = Afwijking open.
3. **"Status in één oogopslag"** (t15). Een horizontale staaf: `CNT(Controle)` per `Status`, met dezelfde kleuren en labels.
4. **"Risicokaart"** (t16). `Kans` (discreet) op Kolommen, `Impact` (discreet) op Rijen, markering Vierkant, `MAX(Score)` op Kleur
   (licht naar rood), `CNT(Risico)` als label. Knopinfo met `Risico` en `Maatregel`. Zet ernaast een staafgrafiek van
   `Score` per `Risico`, gesorteerd, met `Maatregel` in de knopinfo. **Controle:** bovenaan staat *Gemiddelde of marginale
   emissiefactor*, met score 9.
5. **Dashboard** 1200 × 1150: titel `Kan je op deze cijfers vertrouwen? 21 controles, 7 nog open`; subtitel
   `In de traditie van de Big Four (COSO, ISAE 3000). Een readiness-beoordeling, geen accountantsverklaring.`
   Rij 1: gegevensstroom. Rij 2: controlematrix (65%) en status (35%). Rij 3: risicokaart en risicostaaf.
6. **Publiceren en GitHub**: afbeelding `docs/img/tableau_controles.png`.

**Uitbreidingen dashboard 7 (19 november, ochtend).**
7. **Nieuwe controles C13–C18**: zelfde werkblad, nieuw domein `Aannames`. Kleur `Afwijking open` donkeroranje.
8. **Tekstvak "Wat is veranderd in de regels"**: `Omnibus I (EU 2026/470): de verplichting tot redelijke zekerheid is geschrapt;
   alleen beperkte zekerheid blijft. Veel minder bedrijven vallen onder de CSRD. Investeerders willen nog steeds controleerbare cijfers.`
9. **Vermeden CO2 apart**: als je t39 gebruikt, zet het in een eigen kader met de titel `Vermeden uitstoot (CBS) is geen
   emissiereductie: niet aftrekken van scope 1-3 (GHG Protocol)`. Nieuwe risico's in t16 staan er al in (15 rijen).


### 15. Dashboard 4 "Ervaringscurve en portefeuille" (vrijdag 20 november, ongeveer 2 uur)

**Ontwerpnorm voor dit dashboard** (eerst doen, zie bovenaan): KPI-rij uit t50 met filter `Dashboard` = 4; paletten uit `Preferences.tps`; onderrand met "Wat we niet zeker weten" en "Wat volgt": dashboard 5 (kostencurve), 6 (winstpool), 18 (verzadiging opslagmarkt), 21 (grondstoffen als voorspeller). Kwadrantkleuren: Ster #E39A2D, Melkkoe #1F9E89, Vraagteken #4A5FC1, Hond grijs. KPI-controle: `35% per verdubbeling` (21-46%); `0.095 USD/W` (-19%); NL `Hond` (2022: Ster). In de ervaringscurve een referentielijn op de ITRPV-waarde 26% (t45, rij `referentie ITRPV 1976-2025`) en de annotatie 2024 `verkoop onder kostprijs` (t42). Zelftoets ≥ 16/20 vóór publiceren.

**Boodschap.** Zonnepanelen worden per verdubbeling van het wereldvermogen ongeveer 35% goedkoper (95%: 21–46%). In Europa zijn
Bulgarije, Litouwen, Polen en Roemenië de sterren van 2025. Nederland zakte van ster naar de grens met hond.

1. **"Ervaringscurve"** (t11). `Cumulatief GW` op Kolommen en `Prijs USD per W` op Rijen, beide met een **logaritmische as**
   (As bewerken > Logaritmisch). Markering Cirkel, `Jaar` als label. Analyse > Trendlijn > **Macht**. Klik met rechts op de lijn >
   Trendlijn beschrijven: de exponent b moet ongeveer −0,62 zijn, want 1 − 2^−0,62 ≈ 35%. Titel:
   `Per verdubbeling 35% goedkoper (95%: 21–46%)`. Subtitel: `Exportwaarde Chinese panelen, geen fabrieksprijs; 2017–2025;
   de piek in 2021–2022 komt door polysilicium.`
2. **"Portefeuille 2025"** (t12, filter `Moment` = 2025). `Batterij-omzet tegen mediaan` (x) tegen
   `Groei zonvermogen per jaar` (y). Markering Cirkel, `Zonvermogen GW` op Formaat, `Kwadrant` op Kleur (palet *ETI kwadrant*: Ster oranje, Melkkoe teal, Vraagteken blauw, Hond grijs), `Landcode` als label. Referentielijnen: x = 1 (`mediaan batterij-omzet`) en
   y = 0,30 (`mediaan groei 2021–2025`). **Controle:** Ster = BGR, LTU, POL, ROU; Hond = BEL, CZE, FRA, ITA, NLD.
3. **"Van 2022 naar 2025"** (t12, beide momenten). Dezelfde assen. Markering Lijn, `Landcode` op Detail en `Moment` op **Pad**.
   Dat geeft een pijl per land. Zet er een tweede as bij met cirkels voor alleen 2025 (berekend veld:
   `IF [Moment] = 2025 THEN [Groei zonvermogen per jaar] END`), gedeelde as, gekleurd naar kwadrant.
   **Controle:** NLD gaat van ster naar hond; HUN van ster naar melkkoe.
4. **Dashboard** 1200 × 1100: titel `Waar wordt zon goedkoper, en waar verdient kapitaal?`; subtitel
   `In de traditie van BCG: ervaringscurve (Henderson 1968) en een aangepaste groei-aandeelmatrix (Henderson 1970).
   x-as = batterij-omzet tegen de mediaan, niet het marktaandeel.` Rij 1: ervaringscurve (volle breedte). Rij 2: portefeuille 2025
   en van 2022 naar 2025 naast elkaar. Kanttekening in een tekstvak: de matrix is aangepast (landen als markten) en Nederland ligt
   precies op de grens (1,00).
5. **Publiceren en GitHub**: afbeelding `docs/img/tableau_bcg.png`.

**Uitbreidingen dashboard 4 (19 november, ochtend).**
6. **Leercurve-varianten** (t45). Kleine tabel of balk met interval: alle jaren 35,0% (21,5–46,2), zonder 2021-22 35,6%,
   zonder 2023-24 34,3% (14,3–49,6), zonder 2021-24 37,9% (33,1–42,4). Boodschap: **de 35% hangt niet aan de crisisjaren of de
   overcapaciteit**; wel ligt hij boven de langjarige literatuurwaarde (ongeveer 20–25%): korte reeks, exportprijs, geen fabrieksprijs.
7. **Knopinfo kwadrantwissel** (t46, koppel op `Landcode`): `Verklaring`. **Controle NLD:** `groei 47% -> 19% per jaar (drempel
   eronder); capture rate 0.93 -> 0.62; verzadiging, geen verval: ... 56% van de postcodes heeft een afnametekort`.
8. **Kanttekeningen in het tekstvak**: (a) BCG-matrix is bedoeld voor productportefeuilles, hier toegepast op landen;
   (b) handelsmaatregelen tegen Chinese panelen en het risico van gedwongen arbeid in de polysiliciumketen vallen buiten de matrix,
   maar zijn voor investeerders een due-diligencepunt.
9. **VS als referentie** (geen bubbel: geen batterij-omzet beschikbaar): tekst `VS: 31 GW zon nieuw in 2024, 30 GW in 2025 (EIA-860M, AC).`

### 16. Sjabloon voor elk volgend dashboard (5, 6, 8-24)

Ik lever bij elk nieuw dashboard, vóórdat je begint: (1) de KPI-tegels in `t50_kpi_dashboards.csv`, (2) een conceptkop
(bevinding met getal), (3) een schets van de opbouw volgens de ontwerpnorm, (4) controlewaarden per werkblad,
(5) "Wat we niet zeker weten" en "Wat volgt" als kant-en-klare tekst, (6) de Engelse teksten in `teksten_en.md` en de
vertaling van nieuwe tabellen in `eti.vertaal_en`, en (7) een vooraf ingevulde zelftoets met wat er
nog misgaat. Jij bouwt, toetst de controlewaarden en publiceert. Daarna beoordeel ik de gepubliceerde afbeelding met
`docs/ontwerp_beoordeling.md`; onder 16/20 komt er een korte revisie.

### 17. Engelse versies (voor elk dashboard; ongeveer 30-45 minuten per dashboard)

Eén Engelse werkmap naast de Nederlandse, met dezelfde opbouw. Zo blijven beide links stabiel en hoeft er geen taalknop in.

1. **Data**: `PYTHONPATH=src .venv/bin/python -m eti.vertaal_en` (zit ook in `run_analyse.sh`). Dat maakt `tableau/data_en/`
   met dezelfde bestands- en kolomnamen en Engelse waarden. Controle: de uitvoer meldt `ontbrekend in woordenboek: 0`;
   anders staan de ontbrekende teksten in `resultaten/vertaal_en_ontbrekend.txt` (zeg het mij, dan vul ik het woordenboek aan).
2. **Werkmap**: open de Nederlandse werkmap > *File* > *Save As* > `tableau/Solar_storage_Europe_EN.twbx`.
3. **Bronnen omzetten**: per bron *Data* > *Edit Data Source* > rechts op de verbinding > *Edit Connection* > kies hetzelfde
   bestand in `tableau/data_en/`. Omdat de kolomnamen gelijk zijn, blijven alle werkbladen werken. Daarna per bron
   *Extract* > *Refresh*.
4. **Veldnamen**: hernoem in het datavenster alleen de velden die je in beeld gebruikt, met `tableau/veldnamen_en.csv`
   (rechts > *Rename*). Tableau zet de nieuwe naam automatisch in assen, legenda's en knopinfo.
5. **Teksten**: titels, subtitels, tekstvakken, referentielijnen en dashboardnamen uit `tableau/teksten_en.md`.
   Tabbladen: `First findings`, `Signals Netherlands`, `Nuclear`, `Control matrix`, `Experience curve`.
6. **Controle**: zelfde getallen als de Nederlandse versie, met een punt als decimaalteken (0.62, niet 0,62);
   geen Nederlandse woorden in filters, legenda's en knopinfo; zelftoets ≥ 16/20.
7. **Publiceren** als aparte werkmap met de naam **`Solar and storage in Europe`** (link wordt `.../viz/SolarandstorageinEurope/<tabblad>`);
   de Nederlandse werkmap publiceer je altijd als **`Zon en opslag in Europa`** (`.../viz/ZonenopslaginEuropa/<tabblad>`).
   Gebruik bij elke nieuwe publicatie precies dezelfde naam: dan overschrijft Tableau de vorige versie en blijven links werken.
   Afbeelding `docs/img/<naam>_en.png`.
   Zet de link in de README naast de Nederlandse ("Dutch | English").
8. **Volgende keren**: bouw eerst de Nederlandse versie, publiceer, en herhaal stap 3–7 in de Engelse werkmap
   (nieuwe bronnen toevoegen uit `data_en/`). Ik lever bij elk nieuw dashboard de Engelse teksten mee in `teksten_en.md`.

## Controlelijst voor je publiceert

- [ ] Landinstelling van alle vijf de bronnen staat op *English (United States)*; Nederland 2025 toont 0,62 en € 61.041.
- [ ] Elk werkblad heeft een titel die de **bevinding** zegt, niet alleen het onderwerp.
- [ ] 2026 is overal als "tot 15 november" herkenbaar.
- [ ] Kleuren per segment en per oorzaak zijn overal gelijk; geen regenboog op de kaart.
- [ ] Status en signaal staan als tekst in beeld, niet alleen als kleur.
- [ ] Toets van dashboard 2: 66 van 66 waarden kloppen.
- [ ] Bronnen en de link naar GitHub staan op het dashboard.
- [ ] Het tekstvak "Wat we niet zeker weten" staat erop (segmentgrenzen, park of dak, aFRR-prijs).
- [ ] KPI-rij uit t50 met vergelijking en referentie; pijlkleur volgens `Richting`.
- [ ] Eén betekenis per kleur; paletten uit `Preferences.tps`; Nederland oranje.
- [ ] Hoogstens vier grafieken naast de KPI-rij; staafassen vanaf 0; elke as met eenheid.
- [ ] Tekstvak "Wat volgt" met dashboardnummers.
- [ ] Zelftoets ≥ 16/20, score in de commitboodschap.
- [ ] Engelse versie gepubliceerd (sectie 17); `vertaal_en` meldt 0 ontbrekend; beide links in de README.

## Valkuilen

| Wat je ziet | Oorzaak | Oplossing |
|---|---|---|
| Getallen 1000 keer te groot | decimaalpunt gelezen als duizendtal (Nederlandse landinstelling) | landinstelling van de bron op *English (United States)* (stap 1.2) |
| Kaart toont vraagtekens of niets | `Landcode` heeft geen geografische rol | rechts > *Geographic Role* > *Country/Region* |
| z-score leeg of anders dan verwacht | tabelberekening loopt over de verkeerde as, of het jaar is weggefilterd | stap 10.4 en 10.5 |
| `Jaar` wordt opgeteld (2025 x 37) | `Jaar` staat als meetwaarde | rechts > *Convert to Dimension* |
| Segmentkleuren verspringen na filteren | kleuren niet vastgezet | *Edit Colors* per segment, eenmalig (stap 5.2) |
| Publiceren mislukt | werkboek gebruikt een lokale koppeling die Tableau Public niet kent | alleen tekstbestanden gebruiken, zoals hier |

## Later: Power BI

Wanneer Fabric draait (Azure-account met een `onmicrosoft.com`-gebruiker), volg je `powerbi/BOUWGIDS.md`. De maten uit
dashboard 2 zijn dan één op één de DAX-maten uit `powerbi/maten_analyse.dax`, en dezelfde vergelijker toetst ze.
