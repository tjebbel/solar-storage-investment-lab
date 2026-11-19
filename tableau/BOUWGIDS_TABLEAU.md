# Bouwgids Tableau: "Zon en opslag in Europa: eerste bevindingen"

Doel: in twee werksessies een openbaar Tableau-dashboard met de eerste bevindingen van dit project, gepubliceerd op
Tableau Public en gelinkt vanuit de README op GitHub. Power BI (met de DAX-toets) volgt later; het tweede dashboard in
deze gids ("Signalering Nederland") is daarvoor de Tableau-tweeling, zodat je de rekenregels alvast in de vingers hebt.

Stand van de data: 18 november 2026. Werktijd: ongeveer 2,5 uur voor sessie 1 en 2,5 uur voor sessie 2.

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

### 10. Dashboard 2 "Signalering Nederland" (stappenplan 19 november, ongeveer 2,5 uur)

**Boodschap van het dashboard.** In het najaar van 2026 is de stroomprijs in Nederland drie maanden achter elkaar een
schok: de z-score is 4,1 in september, 3,5 in oktober en 5,4 in november (tot 15 november). Toch dekt zon in 2026 in zes
van de elf maanden zijn kostprijs. Het dashboard rekent hetzelfde als de DAX-maten en Python (66 van 66).

**Wat klaar staat:** `tableau/data/t2_land_maand.csv` (signalering NL), `t9_signalering_zones.csv` (heatmap Europa) en
`t10_dekking_nl.csv` (dekking per jaar). De verwachte uitkomst staat in `powerbi/maten_verwacht.csv`.

**Stap 0, voorbereiden (10 min).** Open `NL_solar.twbx`. Voeg via **Data > Nieuwe gegevensbron > Tekstbestand** t9 en t10
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

**Boodschap.** Zon en kern leverden in 2025 wereldwijd evenveel stroom (2807 en 2805 TWh). In Europa levert kern nog ruim
twee keer zoveel als zon, maar kernstroom houdt zijn marktwaarde (capture rate 1,00) en zon niet (0,61).

**Bronnen.** Voeg t6, t7 en t8 toe als eigen bron, elk meteen als extract. Gebruik dezelfde instellingen als bij t1–t5.

1. **"Kern en zon, wereld en Europa"** (t6). `Jaar` (continu) op Kolommen, `SUM(Opwek TWh)` op Rijen, `Bron` op Kleur
   (Kernenergie paars, Zon geel, Wind blauw, Fossiel grijs, Water/bio lichtgroen). `Gebied` op Filters en als keuzelijst
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

### 14. Dashboard 7 "Controlematrix en risicokaart" (vrijdag 20 november, ongeveer 2 uur)

**Boodschap.** Twaalf controles: vier geslaagd, twee geslaagd met beperking, drie afwijkingen die verklaard zijn en drie die
nog open staan. Het grootste risico is de keuze van de emissiefactor. Dit is een beoordeling van de gereedheid, geen
accountantsverklaring.

**Voorbereiden.** Laat je toetsuitkomst van donderdag aan mij weten. Ik zet controle C03 daarna op *Geslaagd* en draai
`PYTHONPATH=src .venv/bin/python -m eti.assurance_overzicht --tests` opnieuw. Voeg t15 en t16 toe als extract.

1. **"Gegevensstroom"**: een Afbeelding-object in het dashboard met `docs/img/keten.png` (de keten van bron tot document).
2. **"Controlematrix"** (t15). `Controle`, `Domein` en `Doel` op Rijen; `Uitkomst` als tekst; `Status` op Kleur
   (Geslaagd groen, Geslaagd met beperking lichtgroen, Afwijking verklaard oranje, Open grijs). Opmaak: rijstreping uit,
   alleen dunne lijnen tussen de domeinen. **Controle:** 12 rijen; C02 = `66 van 66 waarden gelijk`.
3. **"Status in één oogopslag"** (t15). Een horizontale staaf: `CNT(Controle)` per `Status`, met dezelfde kleuren en labels.
4. **"Risicokaart"** (t16). `Kans` (discreet) op Kolommen, `Impact` (discreet) op Rijen, markering Vierkant, `MAX(Score)` op Kleur
   (licht naar rood), `CNT(Risico)` als label. Knopinfo met `Risico` en `Maatregel`. Zet ernaast een staafgrafiek van
   `Score` per `Risico`, gesorteerd, met `Maatregel` in de knopinfo. **Controle:** bovenaan staat *Gemiddelde of marginale
   emissiefactor*, met score 9.
5. **Dashboard** 1200 × 1150: titel `Kan je op deze cijfers vertrouwen? 12 controles, 3 nog open`; subtitel
   `In de traditie van de Big Four (COSO, ISAE 3000). Een readiness-beoordeling, geen accountantsverklaring.`
   Rij 1: gegevensstroom. Rij 2: controlematrix (65%) en status (35%). Rij 3: risicokaart en risicostaaf.
6. **Publiceren en GitHub**: afbeelding `docs/img/tableau_controles.png`.

### 15. Dashboard 4 "Ervaringscurve en portefeuille" (vrijdag 20 november, ongeveer 2 uur)

**Boodschap.** Zonnepanelen worden per verdubbeling van het wereldvermogen ongeveer 35% goedkoper (95%: 21–46%). In Europa zijn
Bulgarije, Litouwen, Polen en Roemenië de sterren van 2025. Nederland zakte van ster naar de grens met hond.

1. **"Ervaringscurve"** (t11). `Cumulatief GW` op Kolommen en `Prijs USD per W` op Rijen, beide met een **logaritmische as**
   (As bewerken > Logaritmisch). Markering Cirkel, `Jaar` als label. Analyse > Trendlijn > **Macht**. Klik met rechts op de lijn >
   Trendlijn beschrijven: de exponent b moet ongeveer −0,62 zijn, want 1 − 2^−0,62 ≈ 35%. Titel:
   `Per verdubbeling 35% goedkoper (95%: 21–46%)`. Subtitel: `Exportwaarde Chinese panelen, geen fabrieksprijs; 2017–2025;
   de piek in 2021–2022 komt door polysilicium.`
2. **"Portefeuille 2025"** (t12, filter `Moment` = 2025). `Batterij-omzet tegen mediaan` (x) tegen
   `Groei zonvermogen per jaar` (y). Markering Cirkel, `Zonvermogen GW` op Formaat, `Kwadrant` op Kleur (Ster goud, Melkkoe
   groen, Vraagteken blauw, Hond grijs), `Landcode` als label. Referentielijnen: x = 1 (`mediaan batterij-omzet`) en
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

## Controlelijst voor je publiceert

- [ ] Landinstelling van alle vijf de bronnen staat op *English (United States)*; Nederland 2025 toont 0,62 en € 61.041.
- [ ] Elk werkblad heeft een titel die de **bevinding** zegt, niet alleen het onderwerp.
- [ ] 2026 is overal als "tot 15 november" herkenbaar.
- [ ] Kleuren per segment en per oorzaak zijn overal gelijk; geen regenboog op de kaart.
- [ ] Status en signaal staan als tekst in beeld, niet alleen als kleur.
- [ ] Toets van dashboard 2: 66 van 66 waarden kloppen.
- [ ] Bronnen en de link naar GitHub staan op het dashboard.
- [ ] Het tekstvak "Wat we niet zeker weten" staat erop (segmentgrenzen, park of dak, aFRR-prijs).

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
