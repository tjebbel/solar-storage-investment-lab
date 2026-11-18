# Statistische analyse (_SA)

> Stand van dit verslag: 17 november 2026, middag. Daarna zijn data gerepareerd en analyses toegevoegd; wat daardoor verschoof staat in `07_vervolg.md` (hoofdstuk 9).

Stand: 17 november 2026. Code: `src/eti/sa.py` (toetsen, A/B-test, regressie, cohorten) en `src/eti/prognose.py`.
Draaien: `PYTHONPATH=src python3 -m eti.sa` en `PYTHONPATH=src python3 -m eti.prognose` (samen tien seconden).
Nodig: scipy en scikit-learn (`pip install scipy scikit-learn`). Uitvoer: vijftien tabellen met `_SA` in de naam.

**Gekozen lezing.** De vraag "is beleggen in de energietransitie aantrekkelijk voor rendement en impact" is te breed
voor één toets. Ze is gesplitst in zeven deelvragen die de data kan beantwoorden. Rendement is de IRR zonder contract
(zon, wind) en op de dagmarkt (batterij), afgezet tegen de kapitaalkosten van 5% uit het eigen model. Impact is de
vermeden CO2 van het modelpark. De A/B-test vult het sjabloon met de twee stuurstrategieën van de batterij. De
cohorten zijn zones, gegroepeerd naar het jaar waarin zon 5% van de opwek haalde.

## 1. Hypothesetoetsen

**In gewone taal.** Nulhypothese: de belegging levert in de helft van de zones niet meer op dan het geld kost (mediaan
IRR hooguit 5%). Alternatief: ze levert meer op. Voor impact: de vermeden CO2 is niet gedaald, tegenover: ze is gedaald.

**Aannames en keuze van de toets.** De IRR's zijn niet normaal verdeeld (Shapiro-Wilk wijst normaliteit overal af) en
bevatten lege waarden voor projecten die hun investering nooit terugverdienen. Daarom rangtoetsen: de
Wilcoxon-rangtekentoets op de mediaan per zone, met de tekentoets als controle. Een lege IRR telt als −100%, zodat de
verliezers meetellen. Per zone is één waarde gebruikt (de mediaan over de jaren), omdat jaren binnen een zone niet
onafhankelijk zijn. Zones zijn dat onderling ook niet helemaal; lees de uitkomsten daarom als ondergrens van de
onzekerheid. Zeven toetsen in één familie: de kans op toevalstreffers is gecorrigeerd volgens Holm.

| Deelvraag | n | Uitkomst | 95%-interval | Boven 5% | Boven 8% | Oordeel |
|---|---|---|---|---|---|---|
| Zon zonder contract, 2023-2025 | 36 | mediaan IRR 1,5% | −2,0% tot 4,2% | 25% van de zones | 11% | niet aangetoond |
| Wind zonder contract, 2023-2025 | 37 | mediaan IRR 8,6% | 5,8% tot 13,8% | 73% | 54% | sterke aanwijzing, net niet hard |
| Batterij 2 uur, alleen dagmarkt, 2023-2025 | 37 | mediaan IRR −6,4% | −10,4% tot −2,1% | 8% | 0% | niet aangetoond |
| Wind rendeert beter dan zon | 32 | 9,3 punten verschil | 6,2 tot 12,5 | 31 van 32 landen | | aangetoond |
| Capture rate zon 2025 lager dan 2019 | 37 | −0,35 | −0,39 tot −0,31 | alle 37 zones gedaald | | aangetoond |
| Vermeden CO2 2023-2026 lager dan 2019-2022 | 8 jaren | −31% | −37% tot −24% (de vier latere jaren) | elk later jaar onder elk eerder jaar | | sterke aanwijzing |
| Uurmethode geeft minder vermeden CO2 dan jaargemiddelde | 8 jaren | −241 ton per jaar | −429 tot −53 | 7 van 8 jaren | | sterke aanwijzing |

Toetsgrootheden, p-waarden en effectgroottes staan in `fact_toetsen_SA.csv`. Voor wie ze wil: wind p = 0,013 en na
correctie 0,059; capture rate en wind tegen zon p < 0,001; beide CO2-toetsen na correctie 0,059.

**Effectgrootte.** De daling van de capture rate is 2,7 standaardafwijkingen van het verschil: zeer groot en zonder
uitzondering. Wind tegen zon: 1,1. Zon en batterij tegen de kapitaalkosten: rangcorrelatie −0,65 en −0,98, dus
overtuigend ónder de drempel.

**Gevoeligheid: schokjaren (2021, 2022, 2026).** Zon: mediaan 10,8%, 86% van de zones boven 5%. Wind: 15,8%, 89%.
Batterij: −0,4%, 5%. In schokjaren is zon dus wel aantrekkelijk; de batterij op dagmarkthandel alleen ook dan niet.

**Wat het betekent.** Rendement in de energietransitie is geen eigenschap van de sector maar van de combinatie van
techniek, contract en jaar. Wind verdient zijn kapitaalkosten in driekwart van de zones. Zon zonder contract doet dat
alleen als de gasprijs hoog is. Een batterij haalt het op prijsverschillen alleen nergens en heeft de
balanceringsmarkten nodig. Impact per geïnstalleerde MW daalt naarmate het net schoner wordt.

**Praktische betekenis.** Een capture rate die 0,35 lager ligt, kost bij €87 per MWh en 900 vollasturen ongeveer
€27.000 per MW per jaar, ofwel €274.000 voor het modelpark van 10 MW. De batterij heeft €85.500 per MW per jaar nodig
voor 8% (bij €560 per kW); de dagmarkt leverde in Nederland €61.000 in 2025 en €82.000 in 2026. De vermeden CO2 van
het modelpark ging van 5.988 ton (2019) naar 3.750 ton (2025).

## 2. A/B-test: bijsturen op de onbalansprijs

Ingevuld sjabloon. Eenheid: één dag van een batterij van 1 MW en 2 uur. Looptijd: 1 januari 2023 tot 15 november 2026,
1.415 dagen. Elke dag is geloot in groep A of B, zoals in een proef met één batterij.

| | Controle (A) | Behandeling (B) |
|---|---|---|
| Strategie | dagmarktplan volgen | dagmarktplan, bijsturen op de onbalansprijs van een kwartier eerder |
| Dagen | 712 | 703 |
| Hoofdmaat: omzet per MW per dag | €162 | €256 |
| Conversie: dagen waarop de batterij haar kosten voor 8% verdient (vanaf €234) | 23,2% | 45,4% |

| Onderdeel | Uitkomst |
|---|---|
| Verschil | +€93 per dag (+57%), 95%-interval €62 tot €124; conversie +22 punten |
| Significantie | ja; een verschil van deze omvang ontstaat niet door toeval |
| Onderscheidend vermogen | 100% voor het gevonden effect; kleinste aantoonbare verschil €44 per dag |
| Praktisch | €93 per dag is €34.000 per MW per jaar, 40% van wat voor 8% nodig is |
| Segmenten (na Holm) | winterhalfjaar +€83 (+76%), zomerhalfjaar +€104 (+49%); werkdag +€100, weekend +€77; alle aangetoond |
| Per jaar | 2023 +€191 (+152%); 2024 +€145 (+103%); 2025 +€36 (+21%, niet aangetoond); 2026 −€12 (−5%, niet aangetoond) |
| Nieuwheidseffect | ja, en sterk: eerste 90 dagen +€208 per dag, laatste 90 dagen −€39; het effect slinkt met €70 per dag per jaar |
| Controle met beide strategieën op dezelfde dag | 2023 +€200; 2024 +€128; 2025 +€30 (interval €2 tot €59); 2026 +€16 (interval −€33 tot +€65) |

**Aanbeveling: blijven testen, niet opnemen in de basiscase.** Over vier jaar gemeten is de uitkomst overtuigend
positief, maar dat gemiddelde beschrijft 2023 en 2024. In 2026 is het effect niet meer van nul te onderscheiden:
tussen −€12.000 en +€24.000 per MW per jaar. In het rustigste jaar had de proef met 160 dagen per groep een
onderscheidend vermogen van 5%; een verschil onder €104 per dag valt dan niet op.

**Rode vlaggen.**
- *Verdeling over de groepen:* in orde (712 tegen 703, geen afwijking van 50/50).
- *Gluren:* alle 47 maandelijkse tussentoetsen waren "significant", de eerste al op 31 januari 2023. Wie toen was
  gestopt, had een effect van +150% vastgelegd dat drie jaar later weg is. Het gevaar is hier niet een vals
  positief, maar een waar effect dat niet blijft.
- *Meervoudig toetsen:* acht segmenttoetsen, gecorrigeerd volgens Holm.
- *Niet-stationaire markt:* de voornaamste vlag. Meer batterijen sturen op hetzelfde signaal; de marge verdwijnt.
- *Simulatie:* de batterij is prijsnemer. Bij een echte proef drukt de eigen handel de onbalansprijs.

## 3. Regressie: wat verklaart de capture rate van zon

207 zone-jaren met gemeten opwek, 2019 tot en met 2025. Doel: capture rate. Kandidaten: eigen zonaandeel, zonaandeel
van de buurlanden (gewogen naar handelscapaciteit), wind, waterkracht, kernenergie, gas, prijsniveau, jaareffecten.

**Verkenning.** Rangcorrelatie met de capture rate: buurlanden −0,68; eigen zonaandeel −0,30; gas +0,18; prijs +0,12.
VIF overal onder 2,4: de kandidaten zijn los genoeg van elkaar.

**Keuze van kenmerken en model.** Lasso houdt alle kandidaten, maar met kleine gewichten. De voorspelfout op landen
die het model niet zag (kruisvalidatie per land) beslist:

| Model | R² | RMSE | MAE |
|---|---|---|---|
| alleen jaareffecten | 0,65 | 0,094 | 0,070 |
| eigen zon + buren + jaareffecten | 0,67 | 0,092 | 0,069 |
| alle kandidaten + jaareffecten | 0,65 | 0,094 | 0,072 |
| bosmodel | 0,68 | 0,090 | 0,068 |

Gekozen: eigen zon + buren + jaareffecten. Het is het beste lineaire model en het bosmodel wint maar 2%.

| Term | Coëfficiënt | 95%-interval | Lezing |
|---|---|---|---|
| Eigen zonaandeel (per procentpunt) | −0,0016 | −0,0053 tot +0,0020 | niet van nul te onderscheiden |
| Zonaandeel buurlanden (per procentpunt) | −0,0106 | −0,0184 tot −0,0028 | vijf punten meer zon bij de buren: capture rate 0,05 lager |
| Jaar 2022 (tegen 2019) | +0,037 | −0,006 tot +0,080 | crisisjaar: marktwaarde hersteld |
| Jaar 2023 | −0,118 | −0,174 tot −0,062 | |
| Jaar 2024 | −0,225 | −0,323 tot −0,127 | |
| Jaar 2025 | −0,247 | −0,350 tot −0,144 | de daling vlakt af: −0,02 in een jaar |

Binnen de steekproef: R² 0,73; aangepast 0,72; RMSE 0,083; MAE 0,062. Standaardfouten geclusterd per land.

**Aannames.** Residuen niet normaal en met ongelijke spreiding (beide afgewezen); vandaar geclusterde standaardfouten
en voorzichtigheid met de voorspelintervallen. Lineariteit: geen duidelijke kromming. Residuen binnen een zone hangen
samen (Durbin-Watson 1,2): een zone die boven de lijn ligt, blijft daar. Grootste residuen: Estland en Litouwen 2020,
Noord-Zweden 2021 en 2022, Noord-Italië 2024 en Finland 2025 (houden meer waarde dan het model verwacht).

**Voorbeelden met 95%-voorspelinterval.**

| Geval | Voorspeld | Interval | Werkelijk |
|---|---|---|---|
| Nederland 2025 | 0,60 | 0,43 tot 0,77 | 0,62 |
| Duitsland 2025 | 0,62 | 0,44 tot 0,79 | 0,52 |
| Spanje 2025 | 0,62 | 0,45 tot 0,80 | 0,55 |
| Noord-Italië 2025 | 0,66 | 0,49 tot 0,83 | 0,84 |
| Polen 2025 | 0,64 | 0,48 tot 0,81 | 0,65 |
| Nederland, eigen zonaandeel +5 punten | 0,59 | 0,42 tot 0,77 | |
| Nederland, zonaandeel buren +5 punten | 0,55 | 0,38 tot 0,72 | |

Het interval is ±0,17 breed: het model verklaart het patroon, niet één zone in één jaar.

## 4. Cohorten

Cohort: het jaar waarin zon in het land 5% van de opwek haalde (Ember, alle jaren). Maten: capture rate (prijs
relatief), capture-prijs in euro (prijs absoluut), zonaandeel (vermogen) en het aandeel zones waar de capture-prijs
de kosten dekt (LCOE €67 voor Noordwest-Europa, €51 voor Zuid-Europa). Periode: jaren sinds de drempel, en
kalenderjaar. `fact_cohort_maand_SA` geeft het maandbeeld (voortschrijdend gemiddelde van twaalf maandwaarden).

**Capture rate per cohort en kalenderjaar**

| Cohort | Zones | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | Capture-prijs 2025 | Dekt €67 in 2025 |
|---|---|---|---|---|---|---|---|---|---|
| tot en met 2015 (IT, GR, DE, ES) | 7 | 0,96 | 0,87 | 0,97 | 0,83 | 0,79 | 0,70 | €74 | 57% |
| 2016-2019 (BE) | 1 | 0,92 | 0,74 | 0,92 | 0,78 | 0,56 | 0,51 | €42 | 0% |
| 2020-2021 (NL, HU) | 2 | 1,01 | 0,84 | 0,97 | 0,77 | 0,62 | 0,60 | €58 | 0% |
| 2022-2023 | 10 | 1,01 | 0,90 | 1,01 | 0,82 | 0,69 | 0,60 | €55 | 10% |
| 2024-2025 | 5 | 1,01 | 0,88 | 1,01 | 0,82 | 0,70 | 0,61 | €56 | 20% |
| nog onder de drempel | 11 | 0,99 | 1,07 | 1,02 | 0,83 | 0,66 | 0,69 | €30 | 0% |

**Tijd tot de gebeurtenis** (capture rate voor het eerst onder 0,70, gerekend vanaf het drempeljaar):

| Cohort | Zones | Gezakt | Jaren tot de helft is gezakt |
|---|---|---|---|
| tot en met 2015 | 7 | 3 | niet bereikt: 57% zit na 13 jaar nog boven 0,70 (Italië) |
| 2016-2019 | 1 | 1 | 6 |
| 2020-2021 | 2 | 2 | 4 |
| 2022-2023 | 10 | 10 | 2 |
| 2024-2025 | 5 | 5 | 0 |
| alle zones | 25 | 21 | 2 |

**Inzichten.**
1. *Het is een kalendereffect, geen leeftijdseffect.* Latere cohorten zakken sneller (rangcorrelatie −0,96), maar
   dat komt doordat vrijwel elke zone in 2024 of 2025 zakte, ongeacht haar startjaar. In 2025 verschillen de
   cohorten onderling niet aantoonbaar. Wie later instapt, krijgt geen aanloopjaren meer.
2. *Vroege instappers staan er niet slechter voor.* Het oudste cohort heeft in 2025 de hoogste capture rate (0,70) en
   capture-prijs (€74), dankzij Italië en Griekenland met hoge avondprijzen.
3. *Weinig zon is geen schuilplaats.* De elf zones onder de drempel hebben de laagste capture-prijs (€30): het zijn
   waterkrachtzones met lage prijzen.
4. *Kostendekking is in twee jaar omgeslagen.* In 2023 dekte de capture-prijs €67 in vrijwel elke zone; in 2025 in
   geen enkele zone van de cohorten 2016 tot 2021.

Handelen: beoordeel een project op het verwachte kalenderpad van de regio, niet op hoe "jong" de markt is; reken met
een capture-prijs in euro en niet alleen met de capture rate; zoek zon met contract in zones met hoge avondprijzen.

## 5. Prognose

**Reeksen en modelkeuze.** Maandreeksen van Nederland sinds 2019: prijs, zonprijs (wat zon ontvangt), dagspreiding en
negatieve uren. Vier modellen zijn getoetst door vanaf elk eerder moment twaalf maanden vooruit te voorspellen
(35 momenten). De intervallen zijn de fouten die het gekozen model in die toets werkelijk maakte.

| Reeks | Gekozen model | MAPE (1 tot 12 maanden) | RMSE | Seizoensnaief ter vergelijking | Controlejaar nov 2025 tot okt 2026 |
|---|---|---|---|---|---|
| Prijs | terugkeer naar het gemiddelde | 27% | €31 | 58% | MAPE 27%, RMSE €39 |
| Zonprijs | terugkeer naar het gemiddelde | 37% | €31 | 69% | MAPE 16%, RMSE €22 |
| Dagspreiding | gemiddelde van twee modellen | 34% | €42 | 45% | MAPE 40%, RMSE €59 |
| Negatieve uren | Holt-Winters gedempt | n.v.t. (nullen) | 31 uur per maand | 34 uur | RMSE 32 uur |

**Ontleding van de prijs.** Trend (gecentreerd jaargemiddelde): €107 in april 2026 en stijgend. Seizoen: mei −€27,
april −€20, augustus +€25, december +€22. De schokken van 2022 en 2026 zitten in trend en rest, niet in het seizoen. Een schok
slijt langzaam: een afwijking halveert in ongeveer veertien maanden, in elke deelperiode opnieuw geschat op 0,95.

**Eind 2026 en 2027.**

| Maat | 2026 (tien maanden gemeten, twee geschat) | 2027 model | 2027 gecorrigeerd voor eerdere missers | 80%-interval | 95%-interval |
|---|---|---|---|---|---|
| Prijs (€/MWh) | 135 | 158 | 148 | 106 tot 190 | 95 tot 214 |
| Zonprijs (€/MWh) | 100 | 109 | 98 | 68 tot 139 | 60 tot 153 |
| Capture rate zon | 0,56 | 0,61 | 0,52 | 0,45 tot 0,63 | 0,41 tot 0,66 |
| Dagspreiding (€/MWh) | 157 | 168 | 170 | 137 tot 262 | 121 tot 306 |
| Negatieve uren | 400 | 408 | 527 | 362 tot 676 | 205 tot 682 |

November 2026 is geschat op €241 en december op €228. Ter vergelijking uit de markt: de Duitse termijnprijs voor
levering in 2027 (Cal-27 basislast) stond op 6 november op €144,71, na een jaarpiek van €164,27 op 30 oktober
([Tacto, 9 november 2026](https://www.tacto.ai/en/energy/electricity-price)). Dat ligt op de gecorrigeerde middenwaarde
van het model.

**Scenario's tot 2030, met 2050 als eindpunt.** Geen statistiek meer: acht jaar data draagt geen voorspelling over
een kwart eeuw. Elk scenario is een benoemde set aannames. De capture rate volgt de regressie (eigen zon +2,8 punten
per jaar, buren +1,4, zoals in 2019 tot 2025); kosten komen uit het eigen model (LCOE €67 in 2025, €51 in 2030, €34
in 2050). Na 2030 is de capture rate vastgehouden; alleen de kosten dalen.

| Scenario | Prijs 2030 | Capture rate 2030 | Capture-prijs | Vereiste capture rate 2030 | Marge zon 2030 | Marge zon 2050 | Batterij dagmarkt €/MW |
|---|---|---|---|---|---|---|---|
| Basis | €87 | 0,52 | €45 | 0,58 | −€6 | +€11 | 54.000 |
| Flexibiliteit haalt zon in (gunstig voor zon) | €87 | 0,62 | €53 | 0,58 | +€3 | +€20 | 27.000 |
| Zon loopt uit op flexibiliteit (ongunstig voor zon) | €87 | 0,37 | €32 | 0,58 | −€19 | −€2 | 82.000 |
| Gas blijft duur | €135 | 0,52 | €70 | 0,38 | +€19 | +€36 | 82.000 |
| Gas wordt goedkoop | €77 | 0,52 | €40 | 0,65 | −€11 | +€6 | 48.000 |

**Aannames die de uitkomst bepalen.** (1) De schok van 2026 slijt zo traag als die van 2022. (2) De prijs keert terug
naar het niveau van 2023 tot 2025, tenzij gas duur blijft. (3) Zon groeit door in het tempo van de afgelopen zes
jaar. (4) De overige druk op de capture rate (het jaareffect) blijft gelijk, herstelt met 0,01 per jaar of loopt door
met 0,03 per jaar; dat getal is de grootste onzekerheid en is niet uit de data af te leiden. (5) Batterij-omzet
halveert bij verzadiging, zoals in Californië en Texas. Twee dingen vallen op: in de basis dekt zon zonder contract
zijn kosten in 2030 niet en in 2050 wel, puur door dalende kosten. En zon en opslag bewegen tegengesteld: wat het ene
schaadt, helpt het andere.

## 6. De bevindingen voor zes lezers

Zonder p-waarden, intervallen of coëfficiënten.

**Energiespecialisten**
- *Samenvatting.* De marktwaarde van zon is sinds 2019 in elke Europese zone gedaald, gemiddeld met ruim een derde.
  Het zonaandeel van de buurlanden verklaart dat beter dan het eigen zonaandeel. De opbrengst van bijsturen op
  onbalans is in drie jaar vrijwel verdwenen.
- *En dus.* Reken een project door op regioniveau en met de interconnectie erbij, niet per land.
- *Zekerheid.* De daling: zeer zeker. De rol van de buurlanden: waarschijnlijk. De omvang per zone: onzeker.
- *Beeld.* Zon is als het openen van alle sluizen tegelijk: het maakt weinig uit hoe breed je eigen sluis is als het
  hele stroomgebied op hetzelfde uur loost.
- *Kanttekening.* De opwekmix is per land gemeten, niet per biedzone.
- *Grafiek.* Capture rate per zone, 2019 naast 2025, met een lijn per zone: alle lijnen dalen.

**Beleggingsspecialisten**
- *Samenvatting.* Wind verdient zonder contract zijn kapitaalkosten in driekwart van de zones; zon in een kwart; een
  batterij op dagmarkthandel alleen in geen enkele. Het kalenderjaar verklaart meer van de uitkomst dan het land. In
  jaren met een gasschok keert het beeld om en is alles rendabel.
- *En dus.* Landenspreiding binnen Europa spreidt weinig; spreid over techniek en contractvorm. Zon en opslag dekken
  elkaar af.
- *Zekerheid.* De rangorde wind, zon, batterij: zeker. De hoogte van de rendementen: indicatief, want elk jaar is
  doorgerekend alsof het dertig jaar zo blijft.
- *Beeld.* Een portefeuille van tien strandtenten aan dezelfde kust: tien adressen, één weerbericht.
- *Kanttekening.* Geen balanceringsmarkten, netkosten of contractprijzen in deze rendementen.
- *Grafiek.* Per techniek het aandeel zones boven de kapitaalkosten, gewone jaren naast schokjaren.

**Directie en raad van commissarissen**
- *Samenvatting.* Zon zonder vaste afnameprijs verdient in gewone jaren de kapitaalkosten niet terug. Opslag heeft
  meer inkomstenbronnen nodig dan prijsverschillen alleen. In 2026 zijn de prijzen door gas ruim anderhalf keer zo
  hoog; dat helpt nu, maar is geen basis voor een investeringsbesluit.
- *En dus.* Keur nieuwe zonprojecten alleen goed met een contract of met opslag erbij, en toets elk voorstel op een
  jaar als 2024.
- *Zekerheid.* Hoog voor de richting, matig voor de bedragen na 2027.
- *Beeld.* Een winkel die alleen winst maakt in de week dat de concurrent dicht is.
- *Kanttekening.* De vooruitblik na 2027 bestaat uit scenario's, geen voorspelling.
- *Grafiek.* Marge van zon per MWh in 2030 in vijf scenario's: drie onder nul, twee erboven.

**HR en recruitment in finance en energie**
- *Samenvatting.* Het werk verschuift van "projecten bouwen" naar "projecten laten renderen in een grillige markt".
  Gevraagd zijn mensen die prijsdata, contracten en opslag in samenhang kunnen doorrekenen. Deze analyse laat zien
  dat de kandidaat dat kan, van ruwe data tot toets en prognose.
- *En dus.* Zoek profielen die financiële modellen, statistiek en marktkennis combineren.
- *Zekerheid.* De conclusies steunen op openbare data van 37 marktgebieden over zeven jaar.
- *Beeld.* Van aannemer naar beheerder: het huis staat er, nu moet de exploitatie kloppen.
- *Kanttekening.* Het is een portfolioproject, geen beleggingsadvies.
- *Grafiek.* Eén dia: wind, zon en batterij tegen de kapitaalkosten.

**Eerstejaars studenten**
- *Samenvatting.* Als iedereen op hetzelfde moment hetzelfde verkoopt, daalt de prijs. Zonnepanelen leveren allemaal
  rond het middaguur, dus de middagprijs is gehalveerd ten opzichte van 2019. Wie stroom kan bewaren tot de avond,
  verdient aan het verschil, tot te veel anderen hetzelfde doen.
- *En dus.* Een goed idee wordt minder waard naarmate meer mensen het uitvoeren; kijk naar wat schaars blijft.
- *Zekerheid.* Het patroon is in alle 37 gebieden gemeten.
- *Beeld.* Een festival waar iedereen om twaalf uur tegelijk naar de frietkraam gaat.
- *Kanttekening.* Prijzen hangen ook van gas af; in een duur gasjaar ziet alles er beter uit.
- *Grafiek.* De prijs per uur van de dag in 2019 en in 2025: een vlakke lijn tegenover een diep dal rond het middaguur.

**Groep 7 en 8**
- *Samenvatting.* Als de zon schijnt, maken alle zonnepanelen tegelijk stroom. Dan is er zoveel dat stroom bijna
  niets meer kost. 's Avonds is het donker en is stroom duur.
- *En dus.* Het is slim om stroom van de middag te bewaren voor de avond, in een grote batterij.
- *Zekerheid.* Dat zien we elk jaar en in elk land waar we keken.
- *Beeld.* Als de hele klas op dezelfde dag trakteert, wil niemand nog een traktatie. Bewaar je hem tot morgen, dan is
  iedereen er blij mee.
- *Kanttekening.* Batterijen zijn duur, dus het lukt niet altijd.
- *Grafiek.* Een zon boven een berg stroom om twaalf uur, en een lampje dat 's avonds uit de batterij brandt.

## Beperkingen

- De IRR per jaar veronderstelt dat dat ene jaar de hele levensduur aanhoudt.
- Zones zijn niet onafhankelijk; de werkelijke onzekerheid is groter dan de intervallen aangeven.
- De A/B-test is een simulatie op historische prijzen met een batterij die de prijs niet beïnvloedt.
- De prognose kent alleen het eigen verleden van de reeks: geen gasprijs, weer of termijnmarkt als invoer.
- De scenario's na 2027 zijn aannames. Het jaareffect, de grootste post, is gekozen en niet geschat.
