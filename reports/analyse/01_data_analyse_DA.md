# Data-analyse (_DA)

> Stand van dit verslag: 17 november 2026, middag. Daarna zijn data gerepareerd en analyses toegevoegd; wat daardoor verschoof staat in `07_vervolg.md` (hoofdstuk 9).

Stand: 17 november 2026. Code: `src/eti/da.py`. Draaien: `PYTHONPATH=src python3 -m eti.da` (ongeveer 30 seconden).
Uitvoer: dertien tabellen met `_DA` in de naam in `powerbi/data`.

**Gekozen lezing.** "De datasets" zijn alle 73 tabellen in `powerbi/data`. Het profiel (statistieken, ontbrekende
waarden, verdelingen, waardetellingen) loopt over alle 493 kolommen. De verdieping (verbanden, segmenten, uitschieters,
drijfveren) gebruikt een paneel van 37 Europese biedzones over 2019 tot en met 2026, waaraan de batterij van twee uur
en de opwekmix van het land (Ember) zijn gekoppeld. De tijdpatronen komen uit de Nederlandse uurprijzen.
Het jaar 2026 loopt tot 15 november en doet in de verbanden en modellen niet mee.

| Tabel | Inhoud |
|---|---|
| `fact_profiel_DA` | per tabel en kolom: aantal, ontbrekend, gemiddelde, mediaan, spreiding, kwartielen, scheefheid, verdeling |
| `fact_waarden_DA` | per tekstkolom de tien meest voorkomende waarden plus "overig" |
| `fact_correlatie_DA` | Pearson, Spearman, Spearman binnen jaren, VIF, eta-kwadraat, vertraagde verbanden |
| `fact_segmentprofiel_DA`, `fact_gedragssegment_DA`, `fact_clusterkeuze_DA` | drie indelingen met profiel per segment |
| `fact_tijd_DA` | trend, seizoen, weekdag, uur van de dag, breekpunten, groeicijfers |
| `fact_uitschieters_DA`, `fact_uitschieters_effect_DA` | elke uitschieter met context en advies; effect op gemiddelde en mediaan |
| `fact_zonejaar_DA`, `fact_zonejaar_schoon_DA` | het paneel met vlaggen; de schone versie voor modellen |
| `fact_drijfveren_DA`, `fact_tweelingen_DA` | belang van kenmerken volgens vier methoden; kenmerken die hetzelfde meten |

## 1. Verkenning

**Verdelingen.** Van de 350 numerieke kolommen is er 25 ongeveer normaal verdeeld. 128 zijn sterk scheef naar rechts
en 61 mogelijk tweetoppig. Voor deze data zegt een gemiddelde dus weinig; gebruik medianen en rangordes.

| Kolom (zone-jaren) | Gemiddelde | Mediaan | Min | Max | Verdeling |
|---|---|---|---|---|---|
| Gemiddelde prijs (€/MWh) | 93 | 87 | 9 | 308 | sterk scheef naar rechts |
| Capture rate zon | 0,84 | 0,85 | 0,47 | 3,51 | sterk scheef (twee rekenfouten) |
| Capture rate wind | 0,92 | 0,94 | 0,55 | 1,12 | licht scheef naar links |
| Negatieve uren | 124 | 36 | 0 | 725 | sterk scheef naar rechts |
| Uren boven €200 | 808 | 135 | 0 | 7.097 | sterk scheef naar rechts |
| Dagspreiding (€/MWh) | 88 | 80 | 3 | 251 | licht scheef naar rechts |
| Batterij 2 uur (€/MW/jaar) | 35.265 | 30.374 | 597 | 100.085 | scheef naar rechts |
| Onbalansprijs tekort NL (€/MWh) | 106 | 90 | −3.895 | 5.500 | scheefheid 7,3: zware staarten |

**Ontbrekende waarden.** Zeventien kolommen zijn voor meer dan 20% leeg, geen enkele helemaal. De belangrijkste leegte
is geen slordigheid maar informatie: `irr_realistisch` in `fact_flex_land` is in 34% van de rijen leeg omdat de
batterij daar haar investering nooit terugverdient. Zie patroon 2.

**Vijf patronen die een CFO, COO, datawetenschapper, beleggingsmanager, investor relations of hoofd impact moeten kennen**

1. **Het jaar weegt zwaarder dan het land.** Het kalenderjaar verklaart 59% van de variatie in dagspreiding, 49% in
   batterij-omzet en 42% in negatieve uren; het land 29%, 35% en 25%. Spreiden over Europese landen spreidt het
   risico dus minder dan een landenlijst suggereert: alle zones bewegen samen.
2. **Een gemiddelde IRR telt de slechtste gevallen niet mee.** Bij de batterij van twee uur ontbreekt de IRR in 100
   van de 296 zone-jaren; dat zijn precies de jaren met een omzet onder €15.800 per MW. Wie het gemiddelde van de
   gevulde cellen rapporteert, laat de verliezers weg. In 2025 haalt geen enkele zone 8% op dagmarkthandel alleen;
   de mediaan van de zones mét een IRR is −1,0%.
3. **2026 is geen gewoon jaar.** De Nederlandse dagmarktprijs loopt op van €85 in april naar €172 in oktober en €255
   in de eerste helft van november (5,4 standaardafwijkingen boven de twaalf maanden ervoor). Het is Europees: sinds
   mei stijgen 34 tot 36 van de 37 zones jaar op jaar, in november met een mediaan van 139%. Tegelijk daalt het aantal
   negatieve uren in Nederland voor het eerst (399 tegen 584 in 2025) en stijgt de dagspreiding van €123 naar €156.
4. **De Nederlandse zonreeks dekt 2% van de werkelijke opwek.** `solar_mw` in de uurtabel telt op tot 0,5 TWh in 2025;
   Ember geeft 28,5 TWh. De capture rate gebruikt alleen de vorm van het profiel en blijft bruikbaar, maar elk cijfer
   dat het niveau gebruikt (aandeel zon, vermeden CO2 per uur) moet uit Ember komen.
5. **Negatieve prijzen zijn niet alleen een zonverschijnsel.** Noord-Zweden (SE2) had in 2025 678 negatieve uren bij
   1% zon: wind en waterkracht. Binnen jaren hangt het aantal negatieve uren samen met het aandeel kernenergie
   (0,38) en wind (0,29), en niet met het eigen zonaandeel (−0,05).

Twee bijvangsten: de capture rates van SE3 en SE4 in 2021 (3,51 en 2,97) zijn rekenfouten uit een bijna lege
opwekreeks, en in 2019 en 2020 vielen alle zones in het segment "vlakke prijzen" terwijl "zonverzadigd" pas in 2024
ontstond en in 2025 negen zones telt.

**Tien vragen die de data kan beantwoorden, op volgorde van zakelijke waarde**

1. In welke zones verdient een batterij haar kapitaalkosten terug, en met welke inkomstenstapel?
2. Bij welk zonaandeel (eigen en van de buren) zakt de capture rate onder het niveau dat een PPA nog dekt?
3. Hoeveel van het rendement van een portefeuille hangt aan één gemeenschappelijke factor, het Europese prijsniveau?
4. Wat is een prijsschok zoals in 2022 en 2026 waard voor opslag, en wat kost hij voor zon zonder contract?
5. Hoe snel verdwijnt batterij-omzet als de vloot groeit (Californië, Texas, Zuid-Australië)?
6. Welke maanden en uren dragen de omzet, en hoe verschuift dat (avondpiek, zondag, mei)?
7. Wat levert bijsturen op de onbalansmarkt nog op, nu het effect sinds 2023 krimpt?
8. Hoeveel CO2 vermijdt een extra MWh zon per uur van de dag, en hoe snel daalt dat?
9. Welke zones houden waarde voor zon (Italië, Finland) en waarom?
10. Welke bronnen spreken elkaar tegen (Energy-Charts tegen Ember, EIA tegen gridstatus), en waar raakt dat de cijfers?

## 2. Verbanden

Vijftien van de 105 paren hebben een correlatie boven 0,5. "Binnen jaren" is de rangcorrelatie per jaar, gemiddeld
over de jaren; die haalt de gezamenlijke beweging van alle zones eruit.

| Paar | Pearson | Spearman | Binnen jaren | Lezing |
|---|---|---|---|---|
| Dagspreiding en batterij-omzet | 0,97 | 0,98 | 0,96 | vrijwel hetzelfde getal: een KPI volstaat |
| Gemiddelde prijs en uren boven €200 | 0,92 | 0,86 | 0,56 | prijsniveau; deels jaareffect |
| Gemiddelde prijs en dagspreiding | 0,80 | 0,82 | 0,48 | halveert binnen jaren: grotendeels het crisisjaar |
| Zonaandeel en waterkrachtaandeel | −0,53 | −0,63 | −0,67 | geografie: waterkrachtlanden hebben weinig zon |
| Zonaandeel en gasaandeel | 0,49 | 0,58 | 0,67 | zonlanden zijn ook gaslanden |
| Capture rate zon en negatieve uren | −0,41 | −0,62 | −0,28 | twee kanten van hetzelfde middagoverschot |
| Capture rate wind en windaandeel | −0,51 | −0,54 | −0,55 | kannibalisatie van wind, stabiel binnen jaren |
| Zonaandeel en batterij-omzet | 0,51 | 0,58 | 0,38 | zie schijnverband hieronder |

**Niet voor de hand liggend, mogelijk oorzakelijk.** Zonlanden zijn gaslanden (0,67 binnen jaren). Dat is het
mechanisme achter de dagspreiding: zon drukt de middag, gas zet de avondprijs. Het maakt ook duidelijk waarom een
gasschok de batterijcase helpt en de capture rate drukt. Tweede punt: het verband tussen wind en zijn eigen marktwaarde
is binnen jaren sterker (−0,55) dan dat van zon met zijn eigen aandeel (−0,13 binnen jaren, −0,31 over alle jaren),
omdat de marktwaarde van zon vooral met het jaar en de buurlanden meebeweegt.

**Multicollineariteit.** VIF: gemiddelde prijs 17,5; uren boven €200 10,5; waterkracht 6,6; dagspreiding 6,2. Zet
prijsniveau, uren boven €200 en dagspreiding niet samen in één regressie.

**Indelingen en getallen.** Eta-kwadraat van het jaar: dagspreiding 0,59, batterij 0,49, negatieve uren 0,42,
capture rate 0,28. Van het land: 0,29, 0,35, 0,25, 0,15. Van de regio: 0,21, 0,26, 0,15, 0,03. De bron van de capture
rate (opwek of instraling) verklaart 1%.

**Tijd.** Verandering op verandering binnen een zone: prijs en batterij-omzet 0,82; prijs en capture rate 0,63; prijs
en negatieve uren −0,50. Het zonaandeel van vorig jaar hangt samen met de capture rate van dit jaar (−0,25), maar de
verandering van het zonaandeel niet met de verandering van de capture rate (−0,06).

**Schijnverbanden.**
- *Meer zon, meer batterij-omzet* (0,58): binnen een zone is de samenhang tussen de veranderingen 0,00. Beide stegen
  in dezelfde jaren; het ene volgt niet uit het andere.
- *Hoge prijs, grote spreiding* (0,82): binnen jaren 0,48. Het crisisjaar 2022 levert de helft van het verband.
- *Zonaandeel en capture rate*: het verband zit tussen landen en jaren, niet in de jaarlijkse verandering binnen een
  land. Dat past bij het ruimtelijke paneel in het memo, waar het effect met land- en jaareffecten verdwijnt.

## 3. Segmenten

**Regels (zakelijke logica, per zone en jaar).** Zonverzadigd: capture rate onder 0,60 en minstens 300 negatieve
uren. Batterijmarkt: dagspreiding vanaf €120. Vlakke prijzen: dagspreiding onder €60. Zon houdt waarde: capture rate
vanaf 0,75. De rest is middenveld.

| Segment 2025 | Zones | Capture zon | Dagspreiding | Negatieve uren | Batterij €/MW | Leden | Aanbeveling |
|---|---|---|---|---|---|---|---|
| Batterijmarkt | 13 | 0,61 | 154 | 233 | 71.000 | BG, EE, GR, HR, HU, LT, LV, NL, PL, RO, RS, SI, SK | Opslag eerst; toets netkosten en balanceringsmarkten per land |
| Zonverzadigd | 9 | 0,55 | 104 | 431 | 49.000 | AT, BE, CH, CZ, DE-LU, ES, FR, SE3, SE4 | Geen zon zonder contract; PPA met afspraak over negatieve uren, of opslag erbij |
| Vlakke prijzen | 7 | 0,71 | 36 | 221 | 10.000 | NO1 tot NO5, SE1, SE2 | Geen opslag op prijsverschillen; waarde zit in export en langlopende contracten |
| Zon houdt waarde | 5 | 0,83 | 78 | 92 | 30.000 | FI, vier Italiaanse zones | Zon is hier nog te verdedigen; volg het bouwtempo |
| Middenveld | 3 | 0,60 | 110 | 302 | 52.000 | DK1, DK2, PT | Alleen hybride projecten, per geval rekenen |

Verloop: in 2019 en 2020 was vrijwel elke zone "vlakke prijzen"; in 2022 waren 28 zones "batterijmarkt"; "zonverzadigd"
bestaat sinds 2024 (2 zones) en telt in 2025 negen zones.

**K-means.** De silhouetscore is voor elke K laag en vlak (0,34 tot 0,37): de zones vormen geen scherp gescheiden
groepen. Op stabiliteit wint K = 2 (0,72): negen zones met waterkracht (Noorwegen, Noord- en Midden-Zweden, Finland;
dagspreiding €47, batterij €14.000) tegenover 28 zones in de rest van Europa (dagspreiding €125, batterij €57.000).
Fijnere clusters zijn niet stabiel. Voor beslissingen is de regelindeling daarom bruikbaarder dan het algoritme.

**Gedrag (naar het voorbeeld van recency, frequency, monetary).** Recency: jaren sinds de capture rate voor het laatst
0,80 haalde. Frequency: negatieve uren. Monetary: batterij-omzet.

| Segment | Zones | Leden | Aanbeveling |
|---|---|---|---|
| Opslag eerst | 10 | BG, DE-LU, EE, HR, HU, LT, PL, RO, SI, SK | Begin met opslag; de omzet zit in het hoogste derde |
| Zon alleen met contract of opslag | 6 | AT, BE, CZ, DK1, NL, SE3 | Zon haalt al jaren geen 0,80 meer en negatieve uren zijn frequent |
| Zon nog rendabel | 6 | vier Italiaanse zones, NO1, NO2 | Zon kan zonder opslag; in Noorwegen is de capture rate een schatting uit instraling |
| Selectief | 15 | overige | Per project beoordelen |

## 4. Tijdpatronen (Nederland, uurprijs 2019 tot 15 november 2026)

| Bevinding | Periode | Omvang | Blijvend of eenmalig |
|---|---|---|---|
| Prijsniveau | 2019 tot 2026 | €41, 32, 103, 242, 96, 77, 87, 121 per MWh | twee schokken (2022, 2026) op een basis van €80 tot €95 |
| Grootste stijging van het 12-maandsgemiddelde | half jaar tot augustus 2022 | +€100 | eenmalig (gascrisis) |
| Grootste daling | half jaar tot december 2023 | −€97 | eenmalig (herstel) |
| Afwijkende maanden | nov 2026, sep 2021, aug 2022, sep 2026, mrt 2020 | z = 5,4; 4,9; 4,4; 4,1; −4,0 | schokken |
| Jaar op jaar, laatste maanden | mei tot november 2026 | +48%, +63%, +21%, +68%, +96%, +109%, +172% | loopt nog |
| Negatieve uren | 2019 tot 2026 | 3, 97, 70, 85, 316, 458, 584, 399 | stijgend tot 2025; eerste daling in 2026 |
| Dagspreiding | 2019 tot 2026 | €27, 31, 83, 205, 108, 113, 123, 156 | blijvend hoger dan voor 2021 |
| Capture rate zon | 2019 tot 2026 | 0,94; 0,79; 0,77; 0,93; 0,74; 0,60; 0,62; 0,59 | blijvend dalend; 2022 is de uitzondering |
| Seizoen (index, mediaan over hele jaren) | mei 0,75; april 0,81; januari 1,15 | mei en juni lagen in geen enkel jaar boven het jaargemiddelde | blijvend |
| Capture rate zon per maand (2023 en later) | mei 0,59; december 1,06 | zon verdient alleen van november tot januari het jaargemiddelde | blijvend |
| Weekdag | zondag 0,77; zaterdag 0,88; dinsdag tot donderdag 1,08 | zondag 23% onder het jaargemiddelde | blijvend |
| Uur van de dag | 13 uur: 0,97 in 2019, 0,49 in 2025; 19 uur: 1,22 en 1,51 | de middagprijs is gehalveerd ten opzichte van het gemiddelde | blijvend en toenemend |

De prijsstijging van 2026 valt samen met een gasprijs die volgens de prijsvergelijkers van ongeveer €30 per MWh begin
2026 naar ongeveer €85 in november ging (piek €103,94 op 30 oktober) en met een windstilte rond 9 november waarin de
Nederlandse dagprijs €342 haalde. Bronnen staan in `04_rapportage.md`, onderdeel anomalierapport.

## 5. Uitschieters

Drie methoden per kolom: IQR (1,5 maal de kwartielafstand), z-score (boven 3) en isolation forest over alle
kernkolommen samen (5% vervuiling). 182 vlaggen op 296 zone-jaren.

| Categorie | Aantal | Voorbeeld | Behandeling |
|---|---|---|---|
| Invoer- of rekenfout | 2 | capture rate zon SE3 2021 = 3,51 en SE4 2021 = 2,97 (opwekreeks vrijwel leeg) | verwijderen; bron nalopen |
| Systemisch: energiecrisis 2022 | 54 | gemiddelde prijs, uren boven €200, dagspreiding | houden; jaareffect in modellen |
| Systemisch: onvolledig jaar 2026 | 7 | uren, negatieve uren | houden met vlag; niet naast hele jaren zetten |
| Systemisch: capture rate uit instraling | 1 | zones zonder opwekdata | houden met vlag |
| Echte uiterste waarde | 118 | vraag van Duitsland en Frankrijk, kolen in Polen, wind in Denemarken, 678 negatieve uren in SE2 | houden; voor modellen begrenzen op het 1e en 99e percentiel |

Isolation forest wijst dertien zone-jaren aan: twaalf uit 2022 en SE2 in 2025. Meerdimensionaal bekeken is "afwijkend"
dus vrijwel hetzelfde als "crisisjaar".

| Kolom | Uitschieters | Gemiddelde met / zonder | Mediaan met / zonder |
|---|---|---|---|
| Uren boven €200 | 32 | 808 / 328 (−59%) | 135 / 107 |
| Aandeel kolen | 30 | 9,8 / 4,5 (−54%) | 2,0 / 1,0 |
| Vraag (TWh) | 42 | 134 / 85 (−36%) | 89 / 70 |
| Negatieve uren | 16 | 124 / 97 (−22%) | 36 / 29 |
| Gemiddelde prijs | 22 | 93 / 79 (−15%) | 87 / 81 |
| Capture rate zon | 2 | 0,843 / 0,827 (−1,9%) | 0,846 / 0,844 |

De mediaan beweegt nauwelijks, het gemiddelde tot 59%. `fact_zonejaar_schoon_DA` bevat de schone versie: rekenfouten
leeg, uitersten begrensd, 2026 eruit.

## 6. Drijfveren

Vier methoden: rangcorrelatie (een kenmerk tegelijk), wederzijdse informatie (ook niet-lineair), belang in een
bosmodel, en permutatiebelang op een testset van 30%. Twee kenmerksets: *structuur* (opwekmix, vraag, prijsniveau,
jaar) en *markt* (ook marktuitkomsten zoals dagspreiding).

| Doel | Set | R² testset | Top 3 | In de top 3 bij alle vier |
|---|---|---|---|---|
| Capture rate zon | structuur | 0,75 | jaar, prijsniveau, zonaandeel | jaar |
| Capture rate zon | markt | 0,81 | jaar, negatieve uren, voorspelbaarheid | jaar |
| Batterij-omzet | structuur | 0,79 | prijsniveau, jaar, vraag | prijsniveau, jaar |
| Batterij-omzet | markt | 0,97 | dagspreiding, prijsniveau, uren boven €200 | dagspreiding |
| Dagspreiding | structuur | 0,81 | prijsniveau, jaar, vraag | prijsniveau, jaar |
| Negatieve uren | structuur | 0,81 | windaandeel, jaar, prijsniveau | windaandeel |

- **De drie drijfveren van de capture rate van zon zijn het jaar, het prijsniveau en het eigen zonaandeel, in die
  volgorde.** Het jaar staat voor de Europese uitbouw van zon; het eigen aandeel volgt op afstand. Voor de
  onderneming: een land met weinig zon kiezen beschermt niet tegen de waardedaling, want die komt via de grens.
- **De drie drijfveren van batterij-omzet zijn het prijsniveau, het jaar en de omvang van de markt.** De batterijcase
  is een positie op het gasprijsniveau. In rustige jaren zakt de omzet, in schokjaren verdubbelt hij.
- **De drie drijfveren van negatieve uren zijn het windaandeel, het jaar en het prijsniveau.** Wie negatieve uren
  alleen aan zon toeschrijft, mist de helft.

**Waarom de methoden verschillen.** Rangcorrelatie en wederzijdse informatie beoordelen elk kenmerk los en geven
dubbelgangers allebei een hoge score (prijsniveau en uren boven €200 bij batterij-omzet). Het bosmodel en de permutatie
geven het krediet aan één van de dubbelgangers: dagspreiding krijgt 0,97 en de rest vrijwel nul. Bij negatieve uren
staat het windaandeel bij alle vier in de top drie, terwijl het permutatiebelang van het jaar (1,04) veel groter is
dan dat van wind (0,06): wind bepaalt in welke zones de negatieve uren vallen, het jaar hoeveel het er zijn.

**Plaatsvervangers.** Dagspreiding en batterij-omzet (0,98), gemiddelde prijs en uren boven €200 (0,86), gemiddelde
prijs en dagspreiding (0,82), dagspreiding en uren boven €200 (0,82). In een voorspelmodel is dagspreiding geen
oorzaak van batterij-omzet maar dezelfde meting; gebruik de set *structuur* voor uitleg.

## Beperkingen

- 37 zones en 7 hele jaren: 259 waarnemingen die niet onafhankelijk zijn (zelfde jaren, buurlanden).
- De opwekmix komt per land, niet per biedzone: de vijf Noorse en vier Zweedse zones delen één mix.
- Belang van kenmerken is samenhang, geen oorzaak; de set *markt* bevat uitkomsten van hetzelfde mechanisme.
- De capture rate komt in 51 van de 296 zone-jaren uit een instralingsprofiel in plaats van gemeten opwek.
