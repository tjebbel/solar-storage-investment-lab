# Analysepakketten: wat eruit kwam en wat nu

> Stand van dit verslag: 17 november 2026, middag. Daarna zijn data gerepareerd en analyses toegevoegd; wat daardoor verschoof staat in `07_vervolg.md` (hoofdstuk 9).

Stand: 17 november 2026. Zes pakketten zijn uitgevoerd op de 73 tabellen in `powerbi/data`. Dit overzicht legt de
uitkomsten naast elkaar en zet de vervolgstappen op volgorde.

## Wat er ligt

| # | Pakket | Verslag | Code | Uitvoer |
|---|---|---|---|---|
| 1 | Data-analyse | `01_data_analyse_DA.md` | `eti.da` | 13 tabellen `*_DA.csv` |
| 2 | Statistiek en prognose | `02_statistische_analyse_SA.md` | `eti.sa`, `eti.prognose` | 15 tabellen `*_SA.csv` |
| 3 | Visualisatie | `03_visualisatie.md` | `eti.vis`, `eti.rapport_grafieken`, `eti.verken_app` | 10 grafieken, 9 rapportgrafieken, Power BI-thema |
| 4 | Rapportage | `04_rapportage.md` | `eti.woordenboek` | KPI-sjabloon, datawoordenboek, JSON-schema |
| 5 | SQL | `05_sql.md` | `sql/*.sql`, `eti.sql_run` | 27 stappen, gemeten tijden |
| 6 | Python en R | `06_python.md` | `eti.analyse_script`, `eti.rapport_auto`, `eti.ml_pijplijn`, `eti.kwaliteit`, notebook | dag-, week- en maandrapport, model, kwaliteitslog |

Alles in één keer draaien: `bash run_analyse.sh`. Tests: 155 (was 92).

## Wat de uitkomsten samen zeggen

1. **Eén gemeenschappelijke factor stuurt bijna alles.** Vijf verschillende methoden komen op hetzelfde uit. Het
   kalenderjaar verklaart 59% van de variatie in dagspreiding en het land 29% (pakket 1). In de regressie dragen de
   jaareffecten 65% en voegen de zonaandelen 2 punten toe (pakket 2). In de cohortanalyse zakken alle cohorten in
   2024 of 2025, ongeacht hun startjaar. In het verklarende model weegt het prijsniveau het zwaarst (pakket 6). En
   het ML-model kan de rangorde van zones niet beter voorspellen dan "zelfde als dit jaar". Voor een belegger:
   landenspreiding binnen Europa is geen risicospreiding.
2. **Zon is overal minder waard, en het eigen zonaandeel is niet de oorzaak.** −0,35 in alle 37 zones. Het
   zonaandeel van de buurlanden telt (−0,0106 per procentpunt), het eigen aandeel niet aantoonbaar.
3. **Rendement volgt techniek en contract, niet de sector.** Wind boven de kapitaalkosten in 73% van de zones, zon
   in 25%, batterij op dagmarkthandel in 8%. In schokjaren haalt zon 86%.
4. **Opslag is het spiegelbeeld van zon, maar voordeel slijt.** Rangcorrelatie −0,40 tussen de capture rate van zon
   en de batterij-omzet; in alle 37 zones daalde zon terwijl de batterij steeg. Tegelijk ging de opbrengst van
   bijsturen van €73.000 naar €6.000 per MW in drie jaar.
5. **2026 is een schokjaar, en vier losse instrumenten zagen het.** De anomaliecontrole (5,4 standaardafwijkingen),
   de kwaliteitsbewaking (verschuiving van de prijsverdeling), de scorekaart (prijs geel, capture rate rood) en de
   prognose (2027: €148 tot €158). De oorzaak ligt buiten de data: gas en een windstille week.
6. **De data heeft vier bekende gebreken.** De Nederlandse zonreeks dekt 2% van de opwek; SE3 en SE4 hebben in 2021
   een onmogelijke capture rate; twee tabellen tellen uren van 1 tot 24 in plaats van 0 tot 23; en een lege IRR
   betekent "komt nooit terug", niet "onbekend". Alle vier staan nu in het datawoordenboek en in de controles.

## Waar de pakketten elkaar tegenspreken of schuren

| Spanning | Wat het is | Wat te doen |
|---|---|---|
| Memo tegenover regressie | het memo toont een lijn "capture = 0,97 − 0,016 × zonaandeel"; met jaareffecten is het eigen aandeel niet meer aantoonbaar | de figuur en de zin in het memo vervangen door de regressie met buurlanden en jaareffecten |
| Prognose tegenover scenario's | de prognose geeft €148 tot €158 voor 2027; de scenario's gaan vanaf 2029 uit van €87 | de overgang is een aanname (2028 halverwege); toetsen aan de termijnprijzen voor 2028 en 2029 |
| Nederland tegenover Californië en Texas | de Nederlandse batterij-omzet stijgt (€82.000), de Amerikaanse halveerde | Nederland is nog niet verzadigd; de curve per GW batterijvermogen laat zien hoe ver het nog is |
| Negatieve uren | het memo schrijft ze aan zon toe; binnen jaren hangen ze samen met kernenergie (0,38) en wind (0,29), niet met het eigen zonaandeel | in het kernenergiehoofdstuk uitwerken |
| A/B-test | over vier jaar een overtuigend effect, in 2026 niets | altijd per jaar rapporteren; het gemiddelde niet gebruiken |
| ML tegenover verwachting | geen model verslaat de eenvoudige lat | zo rapporteren; pas opnieuw proberen met maanddata of meer jaren |

## Wat niet is getest

- De DAX-maten en de T-SQL-varianten (geen Power BI of SQL Server beschikbaar).
- De verkenner in een echte browser (streamlit en plotly ontbreken in mijn werkomgeving); de rekenfuncties en de
  schermcode met nagemaakte widgets wel.
- Het R-script (geen R).
- Het werkelijk versturen van mail en het inplannen met cron.
- Het notebook in Jupyter zelf; de cellen zijn wel in volgorde uitgevoerd.

## Vervolgstappen, op volgorde

**Eerst: wat nog openstond en nu meer waard is geworden**

1. *Documentronde.* Kernenergie in memo en naslagwerk, Texas over heel 2023 tot en met 2026, FCR en aFRR in het
   batterijhoofdstuk, testaantal 155. Neem daarin drie nieuwe punten mee: het jaar weegt zwaarder dan het land, het
   eigen zonaandeel is niet de drijver, en 2026 is een schokjaar.
2. *Figuren vervangen.* `europa37.png` paneel b (regressielijn) en d (twee assen) door `fig/01`, `fig/02` en
   `fig/10`; `verzadiging.png` opnieuw met de volledige Texas-reeks.
3. *Verzadigingscurve per GW.* De data ligt klaar (batterij-output per uur uit EIA). Dit beantwoordt de vraag hoe
   lang de Nederlandse batterij-omzet nog kan stijgen.

**Dan: de modellen sterker maken**

4. *Balanceringsinkomsten zelf modelleren.* Zonder dit steunt de volledige batterijcase op cijfers van anderen. Het
   ontbrekende stuk is de prijs van aFRR-vermogen.
5. *Gasprijs en CO2-prijs toevoegen.* Als verklaring van het jaareffect en als invoer voor de prognose, samen met
   de termijnprijs. Dat maakt van "het jaar" een oorzaak in plaats van een etiket.
6. *Regressie met vaste zone-effecten en buurlanden*, om het effect binnen zones te scheiden van dat tussen zones.
7. *Maandpaneel voor het ML-model.* Twaalf keer zoveel waarnemingen; pas dan is een model boven de lat te verwachten.

**Data repareren**

8. De capture rate van SE3 en SE4 voor 2021 herberekenen of op leeg zetten in de bron.
9. Een beter Nederlands zonprofiel zoeken (een bron die zon achter de meter meetelt).
10. Urentelling gelijktrekken (0 tot 23) en een datumtabel toevoegen voor Power BI.

**In gebruik nemen**

11. `pip install -r requirements-analyse.txt` en `bash run_analyse.sh` op de iMac; daarna de verkenner starten.
12. Kwaliteitscontrole en dagrapport inplannen met cron (regels staan bovenaan de scripts).
13. Power BI: thema laden, de alarmmaten toevoegen en testen, de pagina "Vandaag" bouwen.
14. De analysetests toevoegen aan de CI op GitHub (bibliotheken uit `requirements-analyse.txt`).
15. Het R-script draaien en de uitkomst naast de Python-tabel leggen.

**Voor het portfolio**

16. Een pagina die per vaardigheid (SQL, Python, statistiek, ML, visualisatie, rapportage) naar één bestand en één
    uitkomst wijst, en de recruitermemo daarop aanpassen. De eerlijke ML-uitkomst ("de lat wint") en de A/B-test met
    slijtend effect zijn daarin sterker dan een hoog R².
