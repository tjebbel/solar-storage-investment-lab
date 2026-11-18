# Rapportage

> Stand van dit verslag: 17 november 2026, middag. Daarna zijn data gerepareerd en analyses toegevoegd; wat daardoor verschoof staat in `07_vervolg.md` (hoofdstuk 9).

Stand: 17 november 2026. Deze teksten steunen op `01_data_analyse_DA.md`, `02_statistische_analyse_SA.md` en de
grafieken in `fig/`. Bijbehorende bestanden: `sjablonen/kpi_rapport_sjabloon.md` (invulklaar), `datawoordenboek.md`
en `datawoordenboek.schema.json` (gemaakt door `src/eti/woordenboek.py`).

## 1. Managementsamenvatting

<!-- telling:samenvatting -->
**Kern.** Beleggen in de energietransitie loont, maar niet vanzelf. Wind verdient in gewone jaren zijn
kapitaalkosten terug. Zon zonder vaste afnameprijs en een batterij die alleen op de dagmarkt handelt doen dat niet.
De uitkomst hangt meer af van het jaar dan van het land, en 2026 is een uitzonderlijk jaar: door dure gas zijn de
stroomprijzen sinds mei ruim anderhalf keer zo hoog als een jaar eerder.

**Bevindingen**

1. *Zon is overal minder waard geworden.* In alle 37 Europese marktgebieden ontvangt zon een kleiner deel van de
   gemiddelde stroomprijs dan in 2019; in Nederland 62% in 2025 tegen 94% toen. Voor een park van 10 MW scheelt dat
   ongeveer €270.000 omzet per jaar. Reken dus niet meer met de marktwaarde van voor 2023.
2. *Het jaar weegt zwaarder dan het land.* Het kalenderjaar verklaart 59% van de verschillen in dagelijkse
   prijsschommeling, het land 29%. Spreiden over landen beschermt daarom weinig.
3. *Alleen wind haalt zijn kapitaalkosten.* Bij kapitaalkosten van 5% rendeert wind daarboven in 73% van de
   gebieden, zon in 25% en een batterij op dagmarkthandel in 8%. In jaren met een gasschok (2021, 2022, 2026)
   haalt zon het in 86%. Het rendement van zon is dus een gok op de gasprijs.
4. *Wat vandaag werkt, slijt.* Bijsturen op de kortetermijnmarkt leverde een batterij in 2023 €73.000 per MW extra
   op en in 2026 nog €6.000. In Californië en Texas halveerde de batterij-omzet binnen drie jaar toen de vloot
   groeide.
5. *2026 is een schokjaar.* De Nederlandse stroomprijs was in de eerste helft van november €255 per megawattuur,
   tegen €94 een jaar eerder. Voor 2027 verwacht het model €148 tot €158; de termijnmarkt staat rond €145.

**Aanbevolen acties**

- Keur nieuwe zonprojecten alleen goed met een afnamecontract of met opslag erbij, en toets elk voorstel op een jaar
  als 2024 (prijs €77, zon ontvangt 60%).
- Eis voor opslag meerdere inkomstenbronnen en reken netkosten mee: de dagmarkt leverde €61.000 tot €82.000 per MW,
  terwijl €85.500 nodig is voor 8% rendement.
- Combineer zon en opslag in één portefeuille: wat het ene schaadt, helpt het andere. Spreid verder over techniek en
  contractvorm.
- Rapporteer vermeden CO2 per uur. Voor het modelpark daalde die van 5.988 ton in 2019 naar 3.750 ton in 2025.

**Risico's en kanttekeningen.** Elk jaarrendement veronderstelt dat dat jaar de hele levensduur aanhoudt. De
marktgebieden bewegen samen, dus de onzekerheid is groter dan 37 losse waarnemingen suggereren. 2026 loopt tot 15
november. De batterijcijfers bevatten geen balanceringsmarkten en geen netkosten. Alles na 2027 is een scenario.

**Vervolgstappen.** Eerst de balanceringsinkomsten zelf modelleren, zodat de volledige batterijcase op eigen data
staat. Daarna de omzetdaling per gigawatt batterijvermogen schatten voor Californië en Texas. Ten slotte elke maand
de vaste set van acht kerncijfers bijwerken.
<!-- einde:samenvatting -->

## 2. Het verhaal in data

**De vraag.** Waar verdient een euro in de energietransitie nog geld, en vermijdt hij dan ook uitstoot?

**Het bewijs, in volgorde.**

Het begint bij zon. Tussen 2019 en 2025 daalde in elk van de 37 Europese marktgebieden het deel van de gemiddelde
stroomprijs dat zon ontvangt, gemiddeld met ruim een derde.

[CHART: halterdiagram per biedzone, capture rate 2019 (open punt) en 2025 (dicht punt), Nederland in oranje;
`fig/01_capture_daling.png`]

De oorzaak is zichtbaar in één dag. In 2019 kostte stroom om 13 uur ongeveer evenveel als gemiddeld over het jaar.
In 2025 was dat de helft, terwijl de avondpiek opliep tot anderhalf keer het gemiddelde. Het gat zit in de
zomermiddag: van april tot augustus kost stroom dan 14% van de jaarprijs.

[CHART: prijs per uur van de dag, 2019 tegenover 2025; `fig/03_uurprofiel.png`]
[CHART: matrix maand × uur, blauw onder en rood boven het jaargemiddelde; `fig/08_maand_uur.png`]

Dit is geen Nederlands probleem dat je met een ander land oplost. Het kalenderjaar verklaart meer van de verschillen
dan het land (59% tegen 29% voor de dagelijkse prijsschommeling), en het zonaandeel van de buurlanden drukt de
marktwaarde sterker dan het eigen zonaandeel.

[CHART: staven, aandeel verklaard door jaar en door land voor vier maten; `fig/02_jaar_tegen_land.png`]

Wat betekent dat voor rendement? Wind verdient in driekwart van de gebieden zijn kapitaalkosten, zon in een kwart,
een batterij op dagmarkthandel vrijwel nergens.

[CHART: aandeel zones boven de kapitaalkosten per techniek, gewone jaren tegenover schokjaren; `fig/04_rendement.png`]

Opslag is het spiegelbeeld van zon: dezelfde middagdip die zon schaadt, vergroot het prijsverschil waar een batterij
van leeft. In Nederland zakte zon van 0,94 naar 0,59 terwijl de batterij-omzet steeg van €9.000 naar €82.000 per MW.

[CHART: twee panelen onder elkaar, capture rate en batterij-omzet in Nederland; `fig/10_nederland_twee.png`]

Maar voordeel slijt. De extra opbrengst van bijsturen op de kortetermijnmarkt is in drie jaar vrijwel verdwenen.

[CHART: punt met interval per jaar, extra omzet van bijsturen; `fig/05_bijsturen.png`]

En 2026 vertekent het beeld: de prijs staat weer op het niveau van de gascrisis.

[CHART: maandprijs sinds 2019 met prognose en band; `fig/06_prijs_prognose.png`]

**Het inzicht.** De energietransitie verschuift de waarde van produceren naar verschuiven en vastleggen. Wie alleen
megawatturen maakt, verdient steeds minder per stuk; wie ze kan bewaren of vooraf verkoopt, verdient aan dezelfde
beweging.

[CHART: marge van zon in 2030 in vijf scenario's, met 2050 als rondje; `fig/07_scenario_marge.png`]

**Tegenwerpingen.**
- *"In 2026 is zon weer rendabel."* Klopt, en in 2022 ook. Dat zijn jaren met een gasschok; een besluit over dertig
  jaar kan daar niet op rusten.
- *"De kosten dalen, dus het komt goed."* In 2050 dekt zon in vier van de vijf scenario's zijn kosten, puur door
  goedkopere panelen. Tot 2030 is dat in drie van de vijf niet zo.
- *"Batterijen lossen de middagdip op."* Dan herstelt zon, maar halveert de batterij-omzet, zoals in Californië en
  Texas. Dat pleit voor beide in één portefeuille, niet voor wachten.
- *"De rendementen zijn te somber."* Ze gaan uit van verkoop tegen de marktprijs. Met een vast contract of met
  balanceringsinkomsten liggen ze hoger; dat is precies de aanbeveling.

**Aanbeveling.** Investeer in de combinatie: zon met contract of opslag, opslag met meerdere inkomstenbronnen, en
wind als basis. Toets elk plan op een gewoon jaar en op een schokjaar.

**Zekerheid.** Hoog voor de richting (zon minder waard, alle gebieden, zeven jaar). Middelmatig voor de omvang per
gebied. Laag voor bedragen na 2027: dat zijn scenario's.

## 3. Drie versies

### Voor de directie (200 woorden)

<!-- telling:directie -->
**Besluit gevraagd:** nieuwe zonprojecten alleen nog goedkeuren met een vast afnamecontract of met opslag erbij.

**Waarom.** Zon levert stroom op het moment dat iedereen levert. In alle 37 Europese marktgebieden ontvangt zon
daardoor een kleiner deel van de stroomprijs dan in 2019; in Nederland 62% tegen 94%. Bij de huidige kosten verdient
zon zonder contract zijn kapitaal alleen terug in jaren met dure gas.

**Financieel.**
- Een park van 10 MW mist door de lagere marktwaarde ongeveer €270.000 omzet per jaar.
- Wind verdient in 73% van de gebieden zijn kapitaalkosten, zon in 25%, een batterij op dagmarkthandel in 8%.
- Een batterij heeft €85.500 per MW per jaar nodig; de dagmarkt leverde €61.000 in 2025 en €82.000 in 2026.

**Risico.** 2026 is een schokjaar: de prijs is ruim anderhalf keer zo hoog als vorig jaar. De winst van nu is geen
maatstaf. Voordelen slijten: de extra opbrengst van slim bijsturen ging in drie jaar van €73.000 naar €6.000 per MW.

**Kans.** Zon en opslag bewegen tegengesteld. Samen in één portefeuille is het risico kleiner dan elk apart.

**Volgende stap.** Laat elk investeringsvoorstel doorrekenen op een gewoon jaar (2024) en een schokjaar (2026), en
besluit op het gewone jaar.
<!-- einde:directie -->

### Voor managers (500 woorden)

<!-- telling:manager -->
**Wat er speelt.** De marktwaarde van zonnestroom daalt in heel Europa, terwijl opslag juist meer verdient. Dat
verandert hoe projecten beoordeeld, gecontracteerd en bewaakt moeten worden.

**Wat we gevonden hebben**

1. *Zon.* In Nederland ontving zon in 2019 nog 94% van de gemiddelde stroomprijs, in 2025 62%. De daling doet zich
   voor in alle 37 marktgebieden. De oorzaak is de middag: om 13 uur kost stroom nu de helft van het jaargemiddelde.
   Alleen van november tot en met januari ontvangt zon ongeveer de volle prijs.
2. *Opslag.* Een batterij van twee uur verdiende op de Nederlandse dagmarkt €61.000 per MW in 2025 en €82.000 in
   2026. Voor 8% rendement is €85.500 nodig. De dagmarkt alleen is dus niet genoeg.
3. *Bijsturen.* Bijsturen op de kortetermijnmarkt leverde in 2023 €73.000 per MW extra op, in 2024 €47.000, in 2025
   €11.000 en in 2026 €6.000. Dat laatste bedrag is niet van nul te onderscheiden.
4. *Regio's.* Dertien gebieden zijn nu vooral een opslagmarkt (Oost- en Zuidoost-Europa, Nederland). Negen zijn
   verzadigd met zon (onder meer Duitsland, Frankrijk, Spanje). In Italië en Finland houdt zon nog waarde.
5. *2026.* De prijzen liggen sinds mei ver boven vorig jaar, in november op €255 per megawattuur. Dat komt door gas
   en een windstille week, en het geldt voor 34 van de 37 gebieden.

**Wat dit betekent voor het werk**

- *Projectbeoordeling.* Reken elk zonproject door met de marktwaarde van 2024 en 2025, niet met het gemiddelde sinds
  2019. Vraag bij elk voorstel naar het contract of de opslag.
- *Contracten.* Leg in afnamecontracten vast wat er gebeurt bij negatieve prijzen. In Nederland viel in 2025 15% van
  de zonopwek in zulke uren.
- *Opslag.* Beoordeel een batterij op de hele inkomstenstapel en trek de netkosten eraf. Neem bijsturen niet op in de
  basiscase.
- *Portefeuille.* Beoordeel zon en opslag samen. Spreiden over landen helpt weinig: het jaar verklaart 59% van de
  verschillen, het land 29%.
- *Rapportage.* Gebruik de vaste set van acht kerncijfers per maand, met groen, geel en rood. Reken vermeden CO2 per
  uur; het jaargemiddelde overschat sinds 2023 met ongeveer een tiende.

**Waar op te letten**

- De waarschuwing voor de prijs staat op rood: november wijkt meer dan vijf standaardafwijkingen af van de twaalf
  maanden ervoor.
- Negatieve uren dalen in 2026 voor het eerst (399 tegen 584). Dat komt door de hogere prijs, niet door minder zon.
- In twee Zweedse gebieden klopt de marktwaarde van zon voor 2021 niet; die rijen zijn uitgesloten.

**Planning**

| Wanneer | Wat |
|---|---|
| Deze maand | Lopende waarderingen herzien met de prijs van 2026 als schok, niet als nieuw normaal |
| Dit kwartaal | Balanceringsinkomsten zelf doorrekenen; netkosten per aansluiting opnemen |
| Elk kwartaal | Segmentindeling van de 37 gebieden bijwerken; prognose toetsen aan de uitkomst |

**Onzekerheid.** De richting is zeker. Een voorspelling voor één gebied in één jaar heeft een marge van ongeveer een
kwart. Vooruitzichten na 2027 zijn scenario's.
<!-- einde:manager -->

### Voor analisten (800 woorden)

<!-- telling:analist -->
**Vraag en data.** Is beleggen in zon, wind en opslag aantrekkelijk voor rendement en impact? De analyse gebruikt 73
tabellen; de kern is een paneel van 37 Europese biedzones over 2019 tot en met 2025 (259 zone-jaren, 2026 apart
omdat het tot 15 november loopt), Nederlandse uurprijzen (69.011 uren), kwartierprijzen voor onbalans (135.837
kwartieren) en de opwekmix per land van Ember. De capture rate komt in 245 van de 296 zone-jaren uit gemeten opwek
en in 51 uit een instralingsprofiel.

**Methode in het kort**

- *Verkenning.* Profiel van alle 493 kolommen. Van de 350 numerieke kolommen is er 25 ongeveer normaal verdeeld;
  daarom medianen, rangcorrelaties en rangtoetsen.
- *Verbanden.* Pearson en Spearman, ook binnen jaren om de gezamenlijke beweging eruit te halen; VIF voor
  multicollineariteit; eta-kwadraat voor indelingen.
- *Toetsen.* Wilcoxon-rangtekentoets op de mediaan-IRR per zone tegen 5%, met Holm-correctie over zeven toetsen. Een
  lege IRR telt als −100%.
- *Regressie.* Capture rate op eigen zonaandeel, zonaandeel van de buurlanden (gewogen naar handelscapaciteit) en
  jaareffecten; standaardfouten geclusterd per land; modelkeuze met kruisvalidatie per land.
- *A/B-test.* Elke dag geloot in "dagmarktplan" of "dagmarktplan met bijsturen"; daarnaast de gepaarde vergelijking
  op dezelfde dag.
- *Cohorten.* Zones gegroepeerd naar het jaar waarin zon 5% van de opwek haalde; overlevingsanalyse tot de capture
  rate onder 0,70 zakt.
- *Prognose.* Vier modellen op maandreeksen, gekozen op de fout bij vooruit voorspellen vanaf 35 eerdere momenten;
  intervallen uit die werkelijke fouten.

**Uitkomsten**

| Onderdeel | Uitkomst |
|---|---|
| Capture rate 2025 tegen 2019 | −0,35 (95%-interval −0,39 tot −0,31), 37 van 37 zones, effectgrootte 2,7 |
| Mediaan IRR 2023-2025 | wind 8,6%; zon 1,5%; batterij dagmarkt −6,4% |
| Wind boven 5% | p = 0,013, na Holm 0,059 |
| Regressie | buurlanden −0,0106 per procentpunt (t = −2,8); eigen zonaandeel −0,0016 (niet significant); R² 0,73 |
| Kruisvalidatie per land | alleen jaareffecten R² 0,65; met zonaandelen 0,67; bosmodel 0,68 |
| Eta-kwadraat van het jaar | dagspreiding 0,59; batterij 0,49; negatieve uren 0,42; capture rate 0,28 |
| A/B-test, gepaard | 2023 +€200 per MW per dag; 2024 +€128; 2025 +€30; 2026 +€16 (interval −€33 tot +€65) |
| Cohorten | 21 van 25 zones onder 0,70, vrijwel allemaal in 2024 of 2025; geen cohortverschil in 2025 (p = 0,38) |
| Prognose prijs 2027 | €158; gecorrigeerd voor eerdere missers €148; 80%-interval €106 tot €190; MAPE 27% |

**Wat de methoden van elkaar verschillen.** Rangcorrelatie en wederzijdse informatie geven dubbelgangers allebei een
hoge score; het bosmodel en de permutatie geven het krediet aan één ervan. Dagspreiding en batterij-omzet meten
vrijwel hetzelfde (0,98). Voor uitleg is daarom alleen de set met structuurkenmerken gebruikt: jaar, prijsniveau,
opwekmix en vraag.

**Beperkingen**

1. *Afhankelijkheid.* Zones delen jaren en buren. De 259 zone-jaren zijn geen 259 onafhankelijke waarnemingen. Toetsen
   op zoneniveau (n = 37) en geclusterde standaardfouten vangen dat deels op.
2. *IRR per jaar.* De IRR veronderstelt dat de prijs van dat ene jaar de hele levensduur geldt. Het is een
   vergelijkingsmaat, geen verwachting.
3. *Opwekmix per land.* De vijf Noorse en vier Zweedse zones delen één mix.
4. *Zonprofiel Nederland.* De gemeten reeks dekt ongeveer 2% van de werkelijke opwek. De vorm is bruikbaar, het
   niveau niet.
5. *Batterij.* Prijsnemer, één cyclus per dag, geen degradatiekosten per cyclus, geen netkosten, geen
   balanceringsvermogen.
6. *A/B-test.* Simulatie op historische prijzen; in een echte proef beïnvloedt de batterij de onbalansprijs.
7. *Prognose.* Alleen het eigen verleden van de reeks; geen gasprijs of termijnmarkt als invoer. De holdout bevat
   de schok van 2026.
8. *Scenario's.* Het jaareffect op de capture rate na 2025 is een aanname (0, +0,01 of −0,03 per jaar).

**Wat nog getoetst moet worden**

- Een model met vaste zone-effecten en het buuraandeel, om het effect binnen zones te scheiden van dat tussen zones.
- Gasprijs en CO2-prijs als verklarende variabelen voor het jaareffect.
- De prognose opnieuw met de termijnprijs als invoer.
- De overlevingsanalyse met maanddata, zodat het moment van zakken scherper is.

**Reproduceren.** `PYTHONPATH=src python3 -m eti.da`, `eti.sa`, `eti.prognose`, `eti.vis`. Uitkomsten staan in
`powerbi/data/*_DA.csv` en `*_SA.csv`; de rekenfuncties zijn gedekt door `tests/test_da.py` en `tests/test_sa.py`.
<!-- einde:analist -->

## 4. KPI-rapport

Het sjabloon staat in `sjablonen/kpi_rapport_sjabloon.md`: kop, scorekaart met groen, geel en rood, een blok per
kerncijfer, toelichting, actielijst en een bijlage met definities. `src/eti/rapport_auto.py` vult het automatisch;
een ingevuld voorbeeld staat in `periodiek/`.

## 5. Anomalierapport: stroomprijs november 2026

**Wat er gebeurde.** De Nederlandse dagmarktprijs was in de eerste helft van november 2026 gemiddeld €255 per
megawattuur, 172% hoger dan in november 2025 en 5,4 standaardafwijkingen boven het gemiddelde van de twaalf maanden
ervoor.

**Gevolgen voor de onderneming.**
- *Zon zonder contract:* de prijs die zon ontvangt steeg in 2026 naar €71 per megawattuur (2025: €53), waardoor het
  rendement van het modelpark van 1,5% naar 5,8% ging. Tegelijk bleef het aandeel van de gemiddelde prijs laag (0,59).
- *Opslag:* de dagmarktomzet van een batterij van twee uur steeg naar €82.000 per MW (2025: €61.000), dicht bij de
  €85.500 die voor 8% nodig is.
- *Contracten:* wie tegen een vaste prijs levert, mist de bovenkant; wie tegen een vaste prijs afneemt, is beschermd.
- *Kerncijfers:* jaargemiddelde 2026 naar schatting €135 tegen €87 in 2025; vergelijkingen met vorig jaar zijn
  vertekend.

**Waarschijnlijke oorzaken, met bewijs.**
1. *Gasprijs.* De opbouw begint in mei en loopt door: +48%, +63%, +21%, +68%, +96%, +109% en +172% tegenover dezelfde
   maand een jaar eerder. Volgens prijsvergelijkers steeg de gasprijs op de TTF van ongeveer €30 per megawattuur begin
   2026 naar ongeveer €85 in november, met een piek van €103,94 op 30 oktober, de hoogste slotkoers sinds eind 2022
   ([Easyswitch](https://www.easyswitch.nl/energie-vergelijken/),
   [Energievergelijk](https://www.energievergelijk.nl/energieprijzen)). Gas zet in de avond de stroomprijs.
2. *Windstilte.* Rond 9 november viel de wind weg in Duitsland, het Verenigd Koninkrijk en de Benelux; de dagprijs
   kwam in Nederland op €342 en in Duitsland op €346, met avondkwartieren boven €600
   ([Bloomberg via BusinessMirror](https://businessmirror.com.ph/2026/11/09/european-power-prices-shoot-above-e600-as-wind-generation-slumps/),
   [Serbia Energy](https://serbia-energy.eu/european-power-prices-surge-above-e300-mwh-as-colder-weather-and-weaker-renewables-tighten-markets/)).
3. *Krap aanbod elders.* Dezelfde berichten noemen weinig waterkracht na een droog jaar en onderhoud aan Franse
   kerncentrales. In onze data stijgt Frankrijk het hardst: €243 tegen €59.

**Is het een vals alarm?**
- *Datakwaliteit:* nee. November telt 346 uren tot en met 15 november, zonder gaten; de laagste uurprijs is €97 en
  de hoogste €609. Een onafhankelijke bron noemt €274 als beursgemiddelde voor november
  ([Selectra](https://selectra.nl/energie/vergelijken/energieprijzen)).
- *Seizoen:* nee. November ligt gewoonlijk 8% boven het jaargemiddelde, niet 172%.
- *Eén land:* nee. 34 van de 37 biedzones stijgen jaar op jaar, met een mediaan van 139%. Alleen Noord-Noorwegen en
  Noord-Zweden dalen.
- *Eenmalig:* deels. De windstille week tilt het halve-maandgemiddelde op; oktober stond zonder die week al op €172.

**Direct doen.**
1. Markeer 2026 als schokjaar in alle vergelijkingen en modellen (naast 2022).
2. Herzie lopende waarderingen met twee prijzen: het gewone niveau (€87) en het schokniveau (€135).
3. Controleer bij contracten met vaste prijs de bepalingen over heronderhandeling en onderpand.
4. Zet de prijswaarschuwing in het dashboard op rood en ververs dagelijks tot de afwijking onder twee
   standaardafwijkingen zakt.

**Voorkomen dat het verrast.**
- Voeg de gasprijs toe aan de dagelijkse data en waarschuw bij een stijging van meer dan 25% in een maand.
- Leg in elk investeringsmodel een schokjaar als vaste gevoeligheid vast.
- Volg de termijnprijs voor het komende jaar naast de eigen prognose.

**Gevolgen voor prognoses en doelen.** Het model verwacht voor 2027 €148 tot €158 per megawattuur, met 80% kans
tussen €106 en €190. De Duitse termijnprijs voor 2027 stond op 6 november op €144,71
([Tacto](https://www.tacto.ai/en/energy/electricity-price)). Doelen voor batterij-omzet over 2026 en 2027 worden
waarschijnlijk gehaald op de prijs, niet op verdienste; beoordeel ze tegen het gewone niveau. De scenario's na 2028
gaan uit van terugkeer naar €87, behalve het scenario "gas blijft duur".

## 6. Datawoordenboek

`datawoordenboek.md` beschrijft alle 493 kolommen van de 73 tabellen: naam en andere namen, type, beschrijving,
eenheid, waarden of bereik, lege waarden, regels, verwante kolommen, bekende problemen en voorbeelden. Van 232
kolommen is de betekenis uitgeschreven (alle kerntabellen); de rest heeft type, bereik en voorbeelden en de
aantekening "nog te beschrijven". `datawoordenboek.schema.json` bevat per tabel een JSON-schema (versie 2020-12) met
type, verplichte kolommen, toegestane waarden en grenzen. `eti.woordenboek.valideer()` toetst een tabel tegen dat
schema. De controle vindt op dit moment twee afwijkingen, beide bekend: de capture rate van zon boven 2 in SE3 en
SE4 (2021).
