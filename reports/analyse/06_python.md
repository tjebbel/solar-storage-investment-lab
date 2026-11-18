# Python en R

> Stand van dit verslag: 17 november 2026, middag. Daarna zijn data gerepareerd en analyses toegevoegd; wat daardoor verschoof staat in `07_vervolg.md` (hoofdstuk 9).

Stand: 17 november 2026. Vijf opdrachten, elk een eigen module. Alles is uitgevoerd op de eigen data, behalve waar
dat hieronder staat.

```
pip install -r requirements-analyse.txt
bash run_analyse.sh                                   # alle pakketten in volgorde, daarna de tests
```

| Opdracht | Bestand | Draaien | Uitvoer |
|---|---|---|---|
| Volledig analysescript | `src/eti/analyse_script.py` | `python3 src/eti/analyse_script.py` | `resultaten/analyse_script/` |
| Automatische rapporten | `src/eti/rapport_auto.py` | `PYTHONPATH=src python3 -m eti.rapport_auto alles` | `reports/analyse/periodiek/` |
| ML-pijplijn | `src/eti/ml_pijplijn.py` | `PYTHONPATH=src python3 -m eti.ml_pijplijn` | `resultaten/ml/` |
| Kwaliteitsbewaking | `src/eti/kwaliteit.py` | `PYTHONPATH=src python3 -m eti.kwaliteit` | `resultaten/kwaliteit/` |
| Notebook-sjabloon | `notebooks/analyse_sjabloon.ipynb` | openen in VS Code of Jupyter | |
| R (extra) | `r/hypothesetoets.R` | `Rscript r/hypothesetoets.R` | `resultaten/r_hypothesetoets_webr.txt` (uitgevoerd op 18 november) |

## 1. Volledig analysescript

Eén bestand dat van boven naar beneden te lezen is en niet op de andere modules leunt. Stappen, elk een functie:
`laad` (kolommen, typen, lege sleutels en bereik controleren; stopt met een eigen fout `DataFout` als de invoer niet
deugt), `schoon` (dubbele zone-jaren eruit, waarden buiten bereik leeg, onvolledige jaren gemarkeerd), `verken`
(kengetallen, toets op normaliteit, rangcorrelaties), `analyseer`, `teken` (drie PNG's) en `samenvatting`. Logboek in
`analyse.log`; eindcode 0, 1 (invoer niet bruikbaar) of 2 (onverwachte fout).

Uitkomst van de laatste run (296 zone-jaren, 37 zones):

1. De capture rate van zon daalde tussen 2019 en 2025 met gemiddeld 0,35 (95%-interval 0,31 tot 0,39), in 37 van
   de 37 zones.
2. Zon en opslag bewegen tegengesteld: in 2025 is de rangcorrelatie tussen de capture rate van zon en de
   batterij-omzet −0,40 over 37 zones. In alle 37 zones ging zon sinds 2019 omlaag terwijl de batterij-omzet steeg.
3. Een model op prijsniveau, opwekmix en jaar verklaart 82% van de batterij-omzet in zones die het niet zag
   (gemiddelde fout €7.192 per MW). Het prijsniveau weegt het zwaarst, dan het jaar.

## 2. Automatische rapporten

Instellingen bovenaan het bestand: mappen, het sjabloon, een lijst ophaalopdrachten (`VERVERSEN`, standaard leeg:
het script leest dan de bestaande csv's) en de mailinstellingen, die alleen uit de omgeving komen (`SMTP_HOST`,
`SMTP_USER`, `SMTP_PASSWORD`, `RAPPORT_VAN`, `RAPPORT_AAN`). Zonder die variabelen wordt niets verstuurd en staat
dat in het logboek.

| Rapport | Vergelijking | Laatste run |
|---|---|---|
| Dag | zeven dagen ervoor en dezelfde weekdag een week eerder; op een feestdag de laatste zondag | 14 november: €207 per MWh, 24% onder het weekgemiddelde van €272 |
| Week | de week ervoor en dezelfde week een jaar eerder | week 45: €253, +8% op de week ervoor en +182% op vorig jaar |
| Maand | dezelfde maand een jaar eerder; vult het KPI-sjabloon en maakt drie grafieken | oktober 2026: 4 groen, 2 geel, 2 rood |

Scorekaart oktober 2026: prijs €172 (geel: buiten de band van de twaalf maanden ervoor), capture rate 0,78 tegen
0,91 een jaar eerder (rood), marge zon €70 per MWh (groen), batterij €5.814 per MW tegen €7.124 nodig (rood),
negatieve uren 16 tegen 46 (groen), versheid 2,5 dagen (geel).

**Randgevallen.** Een dag zonder 24 uren telt niet mee en wordt genoemd. Een lopende week of maand wordt
overgeslagen. Feestdagen (met Pasen, Hemelvaart en Pinksteren uitgerekend) worden met een zondag vergeleken. Een
sjabloonveld zonder waarde wordt "n.b." en komt in het logboek. Mislukt het verversen, dan draait het rapport door
op de bestaande data. Ontbreekt de brondata, dan eindigt het script met een melding in plaats van een fout.

**Inplannen.** De cron-regels staan bovenaan het bestand (dagelijks 07:15, maandag 07:30, eerste van de maand 07:45).

**Niet getest:** het werkelijk versturen van mail. De code is getest tegen een nagemaakte mailserver.

## 3. ML-pijplijn

Vraag: welke biedzones verdienen volgend jaar meer dan de Europese mediaan met een batterij? Het niveau van volgend
jaar hangt aan de gasprijs en is niet te voorspellen; de plaats in de rangorde is dat mogelijk wel. Doel: omzet in
jaar t+1 gedeeld door de mediaan van dat jaar. Het model leert de verandering ten opzichte van dit jaar.

| Onderdeel | Keuze |
|---|---|
| Splitsing | op tijd: trainen op doeljaren 2021 tot 2024 (148 rijen), toetsen op 2025 (37 rijen), 2026 als blik vooruit |
| Kenmerken | 13 getallen (verhouding nu, groei, dagspreiding ten opzichte van de prijs, prijs ten opzichte van de mediaan, capture rate, negatieve uren, opwekmix, vraag) en de regio |
| Voorbewerking | lege waarden op de mediaan, schalen, regio als losse kolommen; alles in één scikit-learn-pijplijn |
| Keuze van kenmerken | `SelectKBest`, aantal als instelling in het zoekrooster |
| Modellen | ridge, bosmodel, gradient boosting, naaste buren |
| Afstellen en kruisvalidatie | zoekrooster per model; elke plooi laat een heel doeljaar weg |
| Lat | "volgend jaar is gelijk aan dit jaar" |
| Bewaren | `batterij_verhouding.joblib` (hele pijplijn) en `.json` (kenmerken, instelling, versie, uitkomsten) |
| Toepassen | `voorspel(rijen)` controleert de kolommen en geeft de verhouding voor volgend jaar |

| Model | Fout in kruisvalidatie (RMSE) | Fout op 2025 | Tegenover de lat |
|---|---|---|---|
| Lat: gelijk aan dit jaar | 0,219 | 0,266 | |
| Ridge (gekozen op kruisvalidatie) | 0,231 | 0,330 | 6% slechter |
| Naaste buren | 0,233 | 0,382 | 7% slechter |
| Bosmodel | 0,240 | 0,536 | 10% slechter |
| Gradient boosting | 0,244 | 0,352 | 12% slechter |

**Uitkomst: geen model haalt de lat.** De rangorde van zones van dit jaar is de beste voorspeller van die van
volgend jaar. De pijplijn heeft daar een regel voor: een model wordt alleen aanbevolen als het in de kruisvalidatie
minstens 5% onder de lat komt. Dat gebeurde niet, dus `vooruitblik.csv` geeft als aanbeveling de stand van dit
jaar, met de modelvoorspelling ernaast. De grootste missers zitten in Midden- en Zuidoost-Europa: die zones stonden
in 2024 ver boven de mediaan en zakten in 2025 terug. Op het onvolledige jaar 2026 zit het model er net onder
(0,179 tegen 0,189), te weinig om iets aan te verbinden. Met 148 rijen over vier doeljaren is dit geen verrassing;
meer jaren of maanddata zijn nodig voordat een model hier iets toevoegt.

## 4. Kwaliteitsbewaking

Zeven soorten controles, elk met ernst (kritiek, waarschuwing, info), status en context:

| Controle | Wat ze toetst | Kritiek als |
|---|---|---|
| Versheid | leeftijd van de laatste meting | ouder dan 4 dagen |
| Volume | aantal rijen tegenover de vorige run | rijen verdwenen, tabel leeg of bestand weg |
| Verschuiving | verdeling van de laatste 30 dagen tegenover alles daarvoor (PSI) | nooit: hooguit een waarschuwing |
| Lege waarden | aandeel leeg per kolom tegenover de vorige run | nooit: waarschuwing bij een sprong van 5 punten |
| Schema | kolommen en typen tegenover het datawoordenboek | kolom weg of verkeerd type |
| Bereik | grenzen en toegestane waarden uit het datawoordenboek | nooit: waarschuwing |
| Sleutel en verwijzing | unieke, gevulde sleutels; waarden die in de oudertabel moeten bestaan | lege of dubbele sleutel |

Een verschuiving is bewust geen reden om te stoppen: een echte marktschok ziet er hetzelfde uit als een fout in de
bron. Het logboek (`kwaliteit_log.csv`) groeit per run; `stand.json` bewaart aantallen voor de volgende vergelijking.
Bij een kritieke bevinding eindigt het script met code 2, zodat cron of een pijplijn de publicatie tegenhoudt.

Laatste run: 47 controles, 43 geslaagd, geen kritiek, vier waarschuwingen. Twee daarvan zijn de prijsschok
(dagmarktprijs: mediaan van de laatste 30 dagen €221 tegen €80 daarvoor; onbalansprijs €223 tegen €89), één de
versheid (2,5 dagen) en één de bekende rekenfout in de capture rate van SE3 en SE4.

## 5. Notebook-sjabloon

`notebooks/analyse_sjabloon.ipynb`, gemaakt door `src/eti/maak_notebook.py`. Zes delen: instellen, overzicht van de
data, opschonen, verkennen, kernanalyse, bevindingen en aanbevelingen. Elk deel begint met een uitleg in markdown;
elke codecel doet één ding (26 cellen, waarvan 19 code). Alleen de cel "Instellingen" hoeft aangepast om het op een
andere tabel te gebruiken. Zoals geleverd draait het op `fact_land_jaar` en komt het uit op dezelfde −0,35.
Getest door alle codecellen in volgorde uit te voeren; niet geopend in Jupyter zelf.

## R

`r/hypothesetoets.R` herhaalt vier van de toetsen in basis-R (zon, wind en batterij tegen de kapitaalkosten; daling
van de capture rate), met Holm-correctie. **Uitgevoerd op 18 november** in R 4.6.0 via webR (R in de browser, op je
Mac), onveranderd; R staat zelf niet op je Mac. Aantallen, schattingen en aandelen zijn gelijk aan Python. De p-waarden
wijken af zoals verwacht (normale benadering in R, exacte verdeling in Python). Eén beslissing verschilt: met Holm over
vier toetsen is wind in R net significant (0,040), in de volledige familie van Python net niet (0,059). Uitvoer en
vergelijking: `resultaten/r_hypothesetoets_webr.txt`.

## Tests

63 nieuwe tests in negen bestanden (`tests/test_da.py`, `test_sa.py`, `test_verken.py`, `test_woordenboek.py`,
`test_sql.py`, `test_kwaliteit.py`, `test_rapport_auto.py`, `test_ml_en_script.py`, `test_notebook.py`); samen met
de bestaande 92 zijn het er 155. Tests die scipy, scikit-learn of seaborn nodig hebben, slaan zichzelf over als die
bibliotheek ontbreekt.
