# Visualisatie

> Stand van dit verslag: 17 november 2026, middag. Daarna zijn data gerepareerd en analyses toegevoegd; wat daardoor verschoof staat in `07_vervolg.md` (hoofdstuk 9).

Stand: 17 november 2026. Code: `src/eti/vis.py` (tien grafieken bij de bevindingen), `src/eti/rapport_grafieken.py`
(vaste set voor maand-, kwartaal- en jaarrapport), `src/eti/verken_app.py` (interactief prototype),
`powerbi/thema_analyse.json` (kleuren en lettergroottes voor Power BI).

```
PYTHONPATH=src python3 -m eti.vis                      # reports/analyse/fig/*.png en bijschriften.txt
PYTHONPATH=src python3 -m eti.rapport_grafieken        # reports/analyse/periodiek/<soort>_<periode>/
PYTHONPATH=src python3 -m eti.rapport_grafieken 2026-06
pip install streamlit plotly && streamlit run src/eti/verken_app.py
```

**Wat is getest.** De grafieken zijn gemaakt en bekeken; botsende labels zijn hersteld. Het palet is door de
kleurcontrole gehaald (zie onder). Van het prototype zijn de rekenfuncties getest en is de schermcode met nagemaakte
widgets doorlopen; in een echte browser is het niet gestart, want streamlit en plotly ontbreken in mijn werkomgeving.

## 1. Ontwerp van het Power BI-dashboard

**Voor wie en waarvoor.** Energieprofessionals en beleggers die rendement en impact van hernieuwbare energie volgen.
De vraag: waar investeren in de periode tot 2050? Verversen: dagelijks in 2026, wekelijks vanaf 2027.

**De blik van vijf seconden.** Na vijf seconden moet de lezer drie dingen weten: verdient zon zijn kosten, verdient
opslag haar kapitaal, en is de markt normaal of in een schok. Daarom staat bovenaan geen grafiek maar drie
statustegels met pictogram, woord en getal, en daaronder één zin: "Opslag eerst in 13 zones, zon alleen met contract".

**Indeling (vier pagina's, elk 16:9).**

| Pagina | Bovenste rij | Midden | Onder |
|---|---|---|---|
| 1. Vandaag | drie statustegels: marge zon (€/MWh), batterij-omzet tegen break-even, prijs tegen normaal | lijn: dagprijs laatste 30 dagen met band van het 12-maandsgemiddelde ± 2 standaardafwijkingen | lijst met actieve waarschuwingen; datum laatste meting |
| 2. Waar | filter regio, segment, jaar | links: gerangschikte staven per zone voor de gekozen maat; rechts: spreiding capture rate tegen batterij-omzet, kleur = segment | tabel segment, aantal zones, aanbeveling |
| 3. Wanneer | filter zone, maat | lijn per maand met prognose en band; matrix maand × uur | scenario's 2030 en 2050 met drie schuiven (prijs, capture rate, kosten) |
| 4. Impact | tegels: vermeden CO2, zonopwek in negatieve uren | kolommen vermeden CO2 per jaar; lijn aandeel opwek in negatieve uren | staven ton CO2 per miljoen euro per regio |

Extra: een doorklikpagina "Zone" (alle maten van één biedzone per jaar en maand) en een tooltip-pagina met de
laatste twaalf maanden als minigrafiek.

**Grafiektype per maat.**

| Maat | Vorm | Waarom |
|---|---|---|
| Marge zon, batterij tegen break-even, prijs tegen normaal | statustegel (getal, verschil, pictogram) | één actuele waarde; een grafiek met één staaf voegt niets toe |
| Maat per zone | gerangschikte horizontale staven, één kleur, gekozen zone in accent | grootte vergelijken over 37 namen; lange namen passen horizontaal |
| Zon tegen opslag | spreidingsdiagram, hooguit vijf segmentkleuren | laat de afruil zien: waar zon zwak is, is opslag sterk |
| Verloop met prognose | lijn met band | trend; de band toont onzekerheid zonder tweede as |
| Maand × uur | matrix met voorwaardelijke opmaak, blauw-grijs-rood rond 1 | twee dimensies en een afwijking van een midden |
| Voor en na per zone (2019 tegen 2025) | halterdiagram | twee meetmomenten per item |
| Scenario's | staven rond nul, kleur naar teken | boven of onder kostendekking is het hele verhaal |
| Segmentverdeling | tabel met aantallen | vijf klassen met tekst erbij; een taart vergelijkt slecht |

**Filters en doorklikken.** Eén rij filters boven de grafieken: periode (voorkeuzes: laatste 30 dagen, lopend jaar,
laatste 12 maanden, alles), regio, segment, techniek. Hiërarchie: regio → land → biedzone → maand → dag. Klikken op
een staaf filtert de pagina; rechtsklik opent de doorklikpagina "Zone". Een leeg filter betekent alles. Het
onvolledige jaar staat standaard uit in vergelijkingen tussen jaren.

**Kleur en codering.** `powerbi/thema_analyse.json`. Regels:
- Kleur volgt het ding, niet de rangorde: Nederland houdt zijn kleur als het filter verandert.
- Reeksen: blauw, oranje, groenblauw, geel, in die volgorde; boven de vier reeksen kleine veelvouden of "overig".
- Eén reeks is het verhaal: die in blauw, de rest grijs.
- Boven of onder een grens: blauw tegenover rood met grijs in het midden. Geen regenboog.
- Statuskleuren (groen, geel, rood) alleen voor status en altijd met pictogram en woord.
- Nooit twee y-assen. Twee maten met verschillende schaal: twee grafieken onder elkaar.
- Tekst in zwart of grijs, nooit in de reekskleur.

Het palet is getoetst met de controle voor kleurenblindheid: de vier reekskleuren slagen op alle harde eisen
(kleinste verschil tussen buren 9,1 bij rood-groenzwakte, eis 8). Groenblauw en geel hebben te weinig contrast met
de achtergrond voor losse lijnen; die krijgen daarom altijd een label bij de lijn.

**Waarschuwingsdrempels** (als maten in DAX; drempels uit de eigen analyse):

| Signaal | Geel | Rood | Herkomst |
|---|---|---|---|
| Marge zon (capture-prijs min LCOE) | onder €5 per MWh | onder nul | scenario's: basis 2030 is −€6 |
| Batterij dagmarkt, voortschrijdend jaar | onder €85.500 per MW (8%) | onder €73.400 (5%) | break-even bij €560 per kW |
| Prijs, maandgemiddelde | meer dan 2 standaardafwijkingen van de 12 maanden ervoor | meer dan 4 | november 2026 scoorde 5,4 |
| Negatieve uren in de maand | 25% boven dezelfde maand vorig jaar | 50% | seizoenspatroon |
| Opbrengst van bijsturen, laatste 90 dagen | interval omvat nul | gemiddelde onder nul | A/B-test |
| Versheid van de data | ouder dan 2 dagen (2026) of 8 dagen (2027) | ouder dan 4 of 15 dagen | verversritme |

```dax
Marge zon = [Capture-prijs zon] - [LCOE]
Status zon = SWITCH(TRUE(), [Marge zon] < 0, "Kosten niet gedekt", [Marge zon] < 5, "Krap", "Gedekt")
Prijs z-score =
VAR gem = CALCULATE(AVERAGE(fact_land_maand[gem_prijs]), DATESINPERIOD(dim_datum[datum], EOMONTH(MAX(dim_datum[datum]), -1), -12, MONTH))
VAR sd  = CALCULATE(STDEV.S(fact_land_maand[gem_prijs]), DATESINPERIOD(dim_datum[datum], EOMONTH(MAX(dim_datum[datum]), -1), -12, MONTH))
RETURN DIVIDE([Gem prijs] - gem, sd)
Data vers = DATEDIFF(MAX(fact_nl_uur_alle_jaren[timestamp_utc]), NOW(), DAY)
```
De DAX is geschreven en niet in Power BI getest. `dim_datum` bestaat nog niet en moet als datumtabel worden toegevoegd.

**Verversen.** 2026: de ophaalscripts draaien elke ochtend op de iMac (cron), de csv's gaan naar het lakehouse, het
model ververst een half uur later. 2027: hetzelfde op maandag. De tegel "datum laatste meting" maakt zichtbaar als
een stap is overgeslagen.

**Mobiel.** Aparte telefoonindeling in Power BI: de drie statustegels onder elkaar, dan één grafiek per scherm.
De matrix maand × uur vervalt op de telefoon en wordt een lijst "vijf goedkoopste en vijf duurste uren". Filters in
een uitklapbaar paneel. Tikdoelen minstens 44 punten; geen zweefteksten als enige bron van een getal.

## 2. Zeven bevindingen en hun grafiek

Publiek: energieprofessionals, duurzaamheidsexperts, impactbeleggers, recruiters, investor relations,
vermogensbeheer, CFO en COO. Gereedschap: Python (uitgevoerd) en Power BI (zelfde vorm).

| # | Bevinding | Vorm en waarom | Assen en codering | Titel | Aantekening | Veelgemaakte fout | Alternatief |
|---|---|---|---|---|---|---|---|
| 1 | Capture rate daalde overal | halter: twee momenten per zone | x capture rate, y zone gesorteerd op 2025; open punt 2019, dicht punt 2025 | In alle 37 zones is zon minder waard dan in 2019 | Nederland in oranje; lijn bij 1,0 | 37 lijnen door elkaar; staven die niet bij nul beginnen | hellinggrafiek voor tien zones |
| 2 | Het jaar weegt zwaarder dan het land | gegroepeerde staven, twee reeksen | x aandeel verklaard (%), y vier maten | Het jaar verklaart meer dan het land | getal aan elke staaf (acht stuks) | taartdiagrammen per maat | puntdiagram met twee punten per rij |
| 3 | Middagprijs gehalveerd | lijn, twee jaren | x uur, y prijs ten opzichte van het jaargemiddelde | De middagprijs is gehalveerd, de avondpiek gegroeid | dal om 13 uur en piek om 19 uur | prijzen in euro, waardoor het crisisjaar alles overstemt | matrix maand × uur |
| 4 | Alleen wind verdient zijn kapitaalkosten | gegroepeerde staven | x aandeel zones boven 5%, y techniek; blauw gewone jaren, oranje schokjaren | Alleen wind verdient in gewone jaren zijn kapitaalkosten | lijn bij de helft | gemiddelde IRR tonen terwijl een derde leeg is | verdeling per techniek als strookdiagram |
| 5 | Opbrengst van bijsturen slijt | punt met interval per jaar | x jaar, y extra omzet (duizend € per MW) | Bijsturen: van +73.000 euro per MW in 2023 naar vrijwel niets in 2026 | nullijn; 2026 loopt tot 15 november | alleen het gemiddelde over vier jaar tonen | cumulatieve lijn per dag |
| 6 | Prijs terug op crisisniveau | lijn met band | x maand, y €/MWh; band 80% en 95% | Prijs weer op crisisniveau; voor 2027 verwacht het model 148 tot 158 euro | piek augustus 2022; gemiddelde 2023-2025 | een prognoselijn zonder band | waaier per kwartaal |
| 7 | Zon dekt kosten in 2030 in drie van vijf scenario's niet | staven rond nul | x marge (€/MWh), y scenario; blauw boven, rood onder nul; rondje = 2050 | In drie van de vijf scenario's dekt zon zonder contract zijn kosten in 2030 niet | 2050 als open punt | scenario's als lijnen die een voorspelling suggereren | tabel met vereiste capture rate |

Daarbij drie hulpgrafieken: de matrix maand × uur (het gat zit in de zomermiddag: van april tot augustus tussen 11
en 15 uur 14% van de jaarprijs), de capture rate per maand, en Nederland in twee panelen.

## 3. De code

`vis.py` gebruikt matplotlib en seaborn. `stijl()` zet één thema (seaborn `set_theme`), `kop()` plaatst titel,
ondertitel en bron op vaste afstand, `punt()` tekent markers met een ring in de achtergrondkleur, en elke grafiek is
een functie die uit de `_DA`- en `_SA`-tabellen leest. De titels en bijschriften worden uit de data opgebouwd: draai
je de analyse opnieuw, dan veranderen de getallen in de titel mee.

## 4. Interactieve verkenner

**Doel.** Zelf door de 296 zone-jaren kunnen lopen: welke zones, welk jaar, welke maat.

**Indeling.** Zijbalk met filters (jaren, regio, segment, alleen hele jaren, maat). Bovenaan vier kerncijfers met
het verschil tegenover het jaar ervoor. Vier tabbladen: Overzicht, Tijd, Rekenhulp, Data.

**Interactie.**
- *Zweven:* naam van het land, zone, negatieve uren en dagspreiding bij elk punt; bij lijnen één gezamenlijke
  aanwijzer voor alle zones op dat jaar.
- *Selecteren:* een lasso of rechthoek in de spreiding beperkt de rangorde ernaast en vult de zonekeuze op het
  tabblad Tijd.
- *Filteren:* alles in de zijbalk werkt op alle tabbladen; een leeg filter betekent alles.
- *Rekenhulp:* drie schuiven (prijs, capture rate, kosten) geven de marge van zon en de capture rate die nodig is;
  een vierde schuif vertaalt dagspreiding naar batterij-omzet via een rechte lijn door de gekozen zone-jaren.

**Overgangen.** Streamlit tekent de pagina opnieuw bij elke wijziging. Plotly houdt de assen vast bij een nieuwe
selectie als de sleutel van de grafiek gelijk blijft, zodat punten verspringen in plaats van dat de hele grafiek
knippert. Voor vloeiende animatie (een jaarschuif die punten laat bewegen) is `animation_frame="jaar"` in Plotly de
volgende stap.

**Standaardbeeld.** Laatste hele jaar, alle zones, maat capture rate: de spreiding zon tegen opslag met de
segmentkleuren. Dat beeld beantwoordt de hoofdvraag zonder klik.

**Bouwplan.** (1) Rekenfuncties los van het scherm, getest (`tests/test_verken.py`). (2) Scherm in Streamlit met
Plotly Express. (3) Lokaal draaien; daarna desgewenst op Streamlit Community Cloud met de csv's in de repo.
(4) Uitbreiden met uurdata per zone zodra die als parquet beschikbaar is.

**Snelheid.** De tabellen zijn klein (296 en 3.516 rijen) en worden met `st.cache_data` één keer gelezen. Uurdata
(69.000 rijen per zone) hoort vooraf te worden samengevat per maand en uur; teken nooit meer dan een paar duizend
punten tegelijk en gebruik voor grotere reeksen `scattergl`.

## 5. Kritiek op de bestaande grafieken

| Grafiek | Wat goed is | Wat beter kan | Vervangen door |
|---|---|---|---|
| `capture_rate.png` | de vorm (dal in de zomer) is direct zichtbaar | Engelse titel en assen in een Nederlands rapport; titel beschrijft in plaats van te concluderen; maanden als getal; as begint bij 0,7 en overdrijft; geen jaar, geen bron | `fig/09_capture_per_maand.png`: kolommen vanaf nul, maandnamen, de drie maanden rond 1,0 in kleur, conclusie als titel |
| `europa37.png` a | gerangschikte staven, Nederland in accent, break-evenlijn | tekst van de lijn valt buiten het vlak; 36 namen in klein lettertype; alleen 2025 | `fig/01_capture_daling.png`: toont ook waar elke zone vandaan komt |
| `europa37.png` b | pad van Nederland door de puntenwolk | één uitschieter (2,2) rekt de as en drukt alle andere punten samen; een regressielijn door alle jaren suggereert een effect van het eigen zonaandeel dat met jaareffecten verdwijnt; kleurschaal met veel tinten voor zeven jaren; de titel is een formule | `fig/02_jaar_tegen_land.png` en de regressietabel; of dezelfde spreiding per jaar in kleine veelvouden |
| `europa37.png` c | 2025 tegen 2026 naast elkaar | de legenda staat over de staven; dubbele staven voor achttien landen is veel inkt; 2026 is geannualiseerd zonder dat de staaf dat toont | halterdiagram 2025 → 2026 met open punt voor het onvolledige jaar |
| `europa37.png` d | onzekerheidsbanden | twee y-assen: het kruispunt van de lijnen in 2022 en 2023 is een gevolg van de schaalkeuze, niet van de data; de as noemt een kleur ("groen") om de reeks aan te wijzen | `fig/10_nederland_twee.png`: twee panelen onder elkaar, elk met een eigen as |
| `wereld.png` a en b | Nederland gestreept als referentie | vijf kruisende lijnen; geel op wit heeft te weinig contrast; het verhaal (Australië liep voor en zakte) moet de lezer zelf zoeken | Nederland en Zuid-Australië in kleur, de rest grijs; of kleine veelvouden |
| `wereld.png` c | Nederland in accent; staven vanaf nul | as zonder eenheid (uren per jaar); brede gele vlakken | één ingetogen kleur, eenheid op de as, getal aan de bovenste en onderste staaf |
| `verzadiging.png` a | gestippeld verlengstuk voor Texas met open punt | Texas is inmiddels compleet tot en met 2026: de stippellijn is achterhaald | opnieuw draaien met de nieuwe Texas-reeks |
| `verzadiging.png` b | zelfde periode vergelijken is de juiste keuze | geel naast oranje is het zwakste kleurpaar voor kleurenblinden; Texas 2026 ontbreekt; brede staven | blauw en oranje, smallere staven, Texas 2026 erbij (€20.500) |

Algemeen: titels die de bevinding noemen, één taal, één palet, geen tweede as, legenda nooit over de data, en een
onvolledig jaar altijd zichtbaar anders (open punt of stippellijn).

**Vijf seconden.** `10_nederland_twee` haalt de proef (twee lijnen, tegengestelde richting). `europa37.png` haalt
hem niet: vier panelen met vier boodschappen. Splits het in losse figuren met elk één titel.

## 6. Vaste set voor maand-, kwartaal- en jaarrapport

`rapport_grafieken.py` bouwt één tabel (`maandtabel()`: een rij per maand) en maakt daaruit per rapport drie
grafieken, een bestand met bijschriften en een samenvatting. Stijl en kleur komen uit `vis.py`.

| Rapport | Onderdeel | Grafiek | Kolommen | Codering | Titel (voorbeeld uit de laatste run) |
|---|---|---|---|---|---|
| Maand | Markt | kolommen, 13 maanden | `prijs` | laatste maand blauw, rest grijs | Markt: 172 euro per MWh in okt 2026, +109% tegenover okt 2025 |
| Maand | Zon | lijn, 13 maanden, met een jaar eerder | `capture_rate` | blauw nu, grijs vorig jaar, lijn bij 1 | Zon: capture rate 0,78 in okt 2026, −14 punten tegenover okt 2025 |
| Maand | Opslag | kolommen met grenslijn | `batterij_per_mw` | laatste maand blauw; lijn = nodig voor 8% | Opslag: 5.814 euro per MW in okt 2026, onder de 7.124 die nodig is |
| Kwartaal | Markt, Zon, Opslag | als maand, negen kwartalen | idem | idem | Markt: 128 euro per MWh in K3 2026, +60% tegenover K3 2025 |
| Jaar | Markt | kolommen, zeven jaren | `prijs` | laatste jaar blauw | Markt: 87 euro per MWh in 2025, +12% tegenover 2024 |
| Jaar | Zon | lijn capture-prijs met kostenlijn | `zonprijs`, `lcoe` | blauw tegenover grijze lijn | Zon: capture-prijs 53 euro, 14 euro onder de kosten in 2025 |
| Jaar | Impact | twee panelen: kolommen en lijn | `co2_vermeden_ton_jaar`, `aandeel_zon_in_negatieve_uren` | blauw en oranje, elk een eigen as | Impact: 3.750 ton vermeden CO2 in 2025, −37% sinds 2019 |

Bijschrift, vaste vorm: "Deze grafiek laat zien dat [inzicht]. De belangrijkste conclusie is [actie]." De actie
hangt af van de uitkomst: bij een prijsverandering boven 25% luidt ze "herzie de prijsaanname in lopende
waarderingen", anders "de prijsaanname hoeft niet te worden aangepast".
