# 07 Vervolg: getest, gerepareerd en uitgebreid

Stand: 18 november 2026, nacht. Dit verslag hoort bij het verzoek "test dat alsnog en voer de vervolgstappen uit".
De cijfers komen uit de tabellen in `powerbi/data`; elke tabel is opnieuw te maken met `bash run_analyse.sh`.

## 1. In het kort

1. **Alle 191 tests slagen, ook op je Mac zelf, zonder overslaan.** De uitkomsten van je Mac (pandas 2.3) en van de
   werkomgeving (pandas 3.0) zijn gelijk op afronding na. Mail is getest tegen een echte SMTP-server op de eigen
   machine, de cron-regels in een lege omgeving. Dat leverde vier echte fouten op, alle hersteld. Het R-script draaide
   onveranderd in R voor de browser en geeft dezelfde schattingen als Python; de verkenner werkt in een echte browser.
2. **Twee klokfouten in de data gevonden en hersteld.** De straling van Open-Meteo en de opwek van EIA staan op het
   eind van het uur, de prijzen op het begin. De capture rate van zon buiten Europa lag daardoor te hoog:
   Californië 2025 0,39 in plaats van 0,45, Texas 0,78 in plaats van 0,88.
3. **Verzadiging per GW:** in het basismodel kost elke GW batterijen erbij 10% van de opbrengst per MW in
   Texas en 8% in Californië. De toets tussen de twee markten bevestigt dat niet; behandel het als bovengrens.
4. **Het jaar is gas, behalve voor zon.** De gasprijs verklaart het jaareffect in de prijs vrijwel geheel en de
   Nederlandse jaarprijs binnen 5%. De capture rate van zon volgt de opbouw van zon en wind, niet het gas.
5. **FCR betaalt meer dan de dagmarkt** (116 tot 202 duizend euro per MW per jaar), maar de markt is klein.
6. **Kernenergie staat in memo en naslagwerk**, met eigen cijfers over marktwaarde en een som voor een nieuwe centrale.

## 2. Wat getest is

| Onderdeel | Hoe | Uitkomst |
|---|---|---|
| Volledige testset | rest van de repo naar de cloud gehaald; daar staan scipy, scikit-learn en seaborn | 191 tests, alle geslaagd; alleen de twee Streamlit-tests slaan over |
| Op je Mac zelf | `bash test_op_mac.sh` in de eigen omgeving van het project (.venv, Python 3.13.1): pandas 2.3.3, numpy 2.5.4, scipy 1.18.1, scikit-learn 1.9.1, seaborn 0.13.2, streamlit 1.67.0, plotly 6.9.0 | 191 tests, alle geslaagd, niets overgeslagen; verkenner onder Streamlit: 2 tests geslaagd; verkenner draaide daarna op `localhost:8501` |
| Mac tegen werkomgeving | dezelfde tabellen vergeleken na een volledige run op beide | gelijk tot op 1e-13; alleen de kruisvalidatie in de regressie wijkt 0,0002 af |
| Dezelfde set via de koppeling met de Mac | Linux-omgeving zonder scipy en scikit-learn | 191 tests, geslaagd, 28 overgeslagen |
| Mail | `tests/test_mail_cron.py`: een SMTP-server op een socket, geen nabootsing | bericht met bijlage komt aan; inloggen werkt; zonder versleuteling gaat het wachtwoord niet naar een andere machine; onbereikbare server geeft een logregel en geen crash |
| Cron | de drie regels uit `rapport_auto.py` in een lege omgeving (`env -i`, alleen `HOME`, `SHELL`, `PATH=/usr/bin:/bin`) | draaien en schrijven de rapporten, mits de regel het volledige pad van Python noemt |
| Hele keten | `bash run_analyse.sh`, nu 18 stappen | loopt door in ruim anderhalve minuut |
| R | het onveranderde `r/hypothesetoets.R` in R 4.6.0 via webR (R in de browser, op je Mac), met de drie invoertabellen ingekort tot de rijen die het script gebruikt | zelfde aantallen, schattingen en aandelen als Python; p-waarden zoals verwacht anders (zie 3a) |
| Verkenner in een echte browser | het browservenster van de Claude-app op je Mac, `localhost:8501` | pagina laadt; kerncijfers, filters en de tabbladen Overzicht, Tijd en Rekenhulp reageren |
| Online dashboard | nieuwe tabellen voor Europa en de wereld geplaatst; de grafieken buiten de app nagetekend met dezelfde code | 37 zones, acht markten buiten de EU met Texas; bekijken vraagt je aanmelding bij claude.ai |

Fouten die het testen opleverde:

- **Cron vond de juiste Python niet.** Cron kent je `PATH` niet; een kaal `python3` is daar de systeem-Python zonder
  pandas. De regels noemen nu `<repo>/.venv/bin/python3`.
- **Het losse analysescript liep vast.** `python3 src/eti/analyse_script.py` zet `src/eti` vooraan in het zoekpad,
  waardoor `eti/numbers.py` de standaardmodule `numbers` verdrong en numpy niet laadde. Hersteld en afgedekt met een test.
- **Een lege groep gaf een deling door nul** in de dagtabel voor Texas en Californië (uur zonder geldige prijs).
- **Dagen waarop EIA uren mist** vertekenden het verzadigingsmodel (één dag in december 2025 trok de helling scheef).
  De dagtabel telt nu de uren met opwek; onvolledige dagen doen niet mee.

## 3. Wat niet getest kon worden

| Onderdeel | Waarom niet | Wat klaarstaat |
|---|---|---|
| DAX | vraagt Power BI of Fabric met jouw aanmelding | `powerbi/maten_analyse.dax` met een toetsvraag en `powerbi/maten_verwacht.csv` met wat die hoort terug te geven; `powerbi/data/dim_datum.csv` is gemaakt |
| T-SQL | geen SQL Server binnen bereik | alleen de vertaaltabel in `05_sql.md`; er zijn geen T-SQL-bestanden geschreven, omdat ongeteste SQL meer schade doet dan geen SQL |
| Echte mailaflevering | vraagt jouw SMTP-gegevens | zet `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `RAPPORT_VAN`, `RAPPORT_AAN` in de omgeving en draai `python3 -m eti.rapport_auto dag` |
| Cron op macOS zelf | een crontab installeren is een blijvende instelling en cron mag op macOS niet in Bureaublad lezen | zet de map buiten Bureaublad, Documenten en Downloads, of gebruik een LaunchAgent; dan `crontab -e` met de regels uit `rapport_auto.py` |

### 3a. Nagekomen

Na de eerste versie van dit verslag (18 november, ochtend) zijn drie dingen alsnog nagekeken.

**R.** R staat niet op je Mac. Het script is daarom gedraaid in webR: R 4.6.0 dat in de browser draait, in het
browservenster van de Claude-app. Het script zelf is niet aangepast; de drie invoertabellen zijn ingekort tot de rijen
en kolommen die het gebruikt (afronding op 12 cijfers verandert de uitkomst met minder dan 1e-13). Uitkomst:

| Toets | n (R en Python) | Schatting (R en Python) | p in R | p in Python | Holm in R (4 toetsen) | Holm in Python (familie) |
|---|---|---|---|---|---|---|
| Zon: IRR boven kapitaalkosten | 36 | 0,0149 | 0,9997 | 0,9997 | 1 | 1 |
| Wind: IRR boven kapitaalkosten | 37 | 0,0858 | 0,0133 | 0,0127 | 0,040 | 0,059 |
| Batterij 2 uur: IRR boven kapitaalkosten | 37 | −0,0635 | 1,0000 | 1,0000 | 1 | 1 |
| Capture rate zon 2025 lager dan 2019 | 37 | −0,351 | 5,9e-08 | 7,3e-12 | 2,4e-07 | 5,1e-11 |

Aantallen, schattingen en aandelen zijn gelijk. De p-waarden van R zijn tot op 2e-15 gelijk aan een naberekening van
de methode van R (normale benadering met continuïteitscorrectie); Python gebruikt de exacte verdeling, vandaar het
verschil. Eén beslissing verschilt: wind is in R net significant en in Python net niet, omdat R over vier toetsen
corrigeert en Python over de hele familie. De conclusie over wind is dus een grensgeval. Uitvoer:
`resultaten/r_hypothesetoets_webr.txt`.

**Verkenner in een echte browser.** De verkenner draaide nog op je Mac (`localhost:8501`, gestart door
`test_op_mac.sh`). In het browservenster van de Claude-app laadt de pagina zonder fouten. De kerncijfers voor 2025
(mediaan over 37 zones: capture rate 0.62, batterij 52,655 euro per MW, dagspreiding 111, negatieve uren 265) kloppen
met de tabellen. De tabbladen Overzicht, Tijd en Rekenhulp reageren; de rekenhulp geeft bij 87 euro, capture rate 0,52
en kosten 51 euro een marge van −6 euro per MWh, gelijk aan het basisscenario in `02_statistische_analyse_SA.md`. Klein
punt: de verkenner schrijft getallen op zijn Engels (0.62, 52,655). Stop de verkenner met Ctrl+C in de terminal als je
hem niet meer gebruikt.

**Online dashboard.** Het dashboard op claude.ai heeft de nieuwe tabellen: 37 Europese zones met de tien aangevulde
capture rates, en acht markten buiten de EU, nu met Texas en met de gecorrigeerde klok van de instraling. Een lijn op
nul is toegevoegd, omdat Victoria in 2023 onder nul kwam (−0,03). Bekijken in de browser lukte niet zonder je
aanmelding bij claude.ai; daarom zijn de grafieken buiten de app nagetekend met dezelfde code en de nieuwe tabellen:
acht lijnen, 37 balken, geen fouten.

## 4. Reparaties in de data

**Klok van de instraling.** Open-Meteo geeft per uur het gemiddelde over het voorgaande uur. Zonder correctie loopt
het zonprofiel een uur achter op de prijs. Bewijs op Nederland: uitgelijnd volgt de gemeten zonreeks de instraling in
elk jaar beter (zie tabel in 4c). Hersteld in `nacht2.straling_per_beginuur` en gebruikt op alle vier de plekken.

**Klok van de Amerikaanse opwek.** EIA publiceert de uurdata per brandstof op het eind van het uur. Hersteld in
`wereld.parse_eia_opwek`. Alle tabellen zijn opnieuw berekend uit de bewaarde bestanden; uren, prijzen en
batterij-omzet bleven gelijk.

| Capture rate zon, 2025 | was | is |
|---|---|---|
| Californië, uit instraling | 0,45 | 0,39 |
| Californië, gemeten opwek | 0,61 | 0,50 |
| Texas, uit instraling | 0,88 | 0,78 |
| Texas, gemeten opwek | 0,93 | 0,80 |
| Verenigd Koninkrijk | 0,85 | 0,84 |
| Japan | 0,81 | 0,78 |
| Zuid-Australië | 0,18 | 0,05 |

De Europese cijfers uit gemeten opwek waren goed en zijn niet veranderd. In Texas liggen schatting en meting nu
dicht bij elkaar; in Californië ligt de meting hoger, wat past bij parken die afschakelen bij negatieve prijzen.

**4a. Afgekeurde capture rates.** Een opwekreeks die pas laat in het jaar begint, weegt alleen die maanden. De
Zweedse zonreeks begint in december 2021; de 3,51 voor Midden-Zweden mat één maand uit de gascrisis. Nieuwe regel
(`herstel.dekking`): een reeks moet driekwart van de maanden dekken. Afgekeurd: vier Zweedse zones in 2021, vijf Noorse
in 2024, Hongarije in 2019. De meting staat nog in `capture_zon_gemeten`. Op je Mac (met netwerk) zijn de tien waarden
aangevuld uit instraling:

| Zone en jaar | Gemeten (afgekeurd) | Dekking | Uit instraling |
|---|---|---|---|
| SE1 2021 | 1,15 | 8% | 1,03 |
| SE2 2021 | 1,15 | 8% | 1,04 |
| SE3 2021 | 3,51 | 8% | 0,90 |
| SE4 2021 | 2,97 | 8% | 0,89 |
| NO1 2024 | 0,57 | 67% | 0,73 |
| NO2 2024 | 0,66 | 67% | 0,76 |
| NO3 2024 | 0,60 | 67% | 0,96 |
| NO4 2024 | 0,70 | 67% | 1,09 |
| NO5 2024 | 0,58 | 67% | 0,79 |
| HU 2019 | 1,08 | 33% | 1,05 |

**4b. Uurtelling.** `fact_land_profiel_uur` en `fact_stromen_uur` tellen nu 0 tot 23 zoals de rest; de bronwaarde 1 tot
24 staat in `uur_bron`.

**4c. De Nederlandse zonreeks.** De vorm klopt, het niveau niet, en de parken schakelen af.

| Jaar | Dekking | Capture gemeten | Capture uit instraling | Idem, oude klok | Correlatie per uur (nieuw / oud) | Negatieve uren met sterke zon | Opbrengst bij negatieve prijs |
|---|---|---|---|---|---|---|---|
| 2019 | 1,2% | 0,94 | 0,95 | 0,95 | 0,93 / 0,90 | 2 | te weinig uren |
| 2020 | 2,5% | 0,79 | 0,79 | 0,80 | 0,97 / 0,93 | 54 | 101% |
| 2021 | 3,6% | 0,77 | 0,76 | 0,76 | 0,96 / 0,92 | 45 | 100% |
| 2022 | 3,0% | 0,93 | 0,91 | 0,92 | 0,96 / 0,92 | 60 | 80% |
| 2023 | 2,8% | 0,74 | 0,71 | 0,72 | 0,95 / 0,91 | 181 | 82% |
| 2024 | 2,2% | 0,60 | 0,56 | 0,59 | 0,93 / 0,89 | 376 | 80% |
| 2025 | 1,8% | 0,62 | 0,52 | 0,56 | 0,86 / 0,82 | 469 | 59% |
| 2026 | n.b.% | 0,59 | 0,55 | 0,59 | 0,89 / 0,85 | 353 | 68% |

Dekking: gemeten opwek gedeeld door het jaartotaal van Ember. Laatste kolom: wat de parken leverden per eenheid
instraling in uren met een negatieve prijs, tegenover alle uren met sterke zon. De capture rate van 0,62 in de
rapporten is dus die van een park dat afschakelt; een dak dat doorlevert haalde in 2025 0,52.

## 5. Verzadigingscurve per GW (`vs_dag.py`, `verzadiging_gw.py`)

| Markt | Vloot 2023 | 2024 | 2025 | 2026 (GW) | Omzet 2023 | 2024 | 2025 | 2026 (duizend euro per MW) | Piekpremie | Daldiepte |
|---|---|---|---|---|---|---|---|---|---|---|
| Texas | 1,2 | 3,2 | 7,0 | 11,8 | 97 | 36 | 25 | 21 | 133 → 30 | 35 → 16 |
| Californië | 3,6 | 6,9 | 9,4 | 11,4 | 41 | 32 | 22 | 18 | 40 → 16 | 29 → 16 |

Vloot: wat de batterijen op hun drukste uren samen leverden. Omzet: twee uur opslag, plan op gisteren, omgerekend
naar een heel jaar. Piekpremie en daldiepte in euro per MWh, 2023 → 2026.

Model: ln(dagopbrengst) = a + b × vloot in GW + zonaandeel, gasprijs, vraag en maand; fouten geclusterd per maand.

| Daling per GW erbij | Texas | Californië |
|---|---|---|
| Basismodel | 10% (p 0,00) | 8% (p 0,00) |
| Zonder schokperiodes | 9% (p 0,00) | 8% (p 0,00) |
| Met tijdtrend | 8% (p 0,01) | 30% (p 0,00) |
| Met jaareffecten | 6% (p 0,27) | 18% (p 0,01) |
| Piekpremie in plaats van omzet | 12% (p 0,00) | 9% (p 0,00) |
| Daldiepte in plaats van omzet | 6% (p 0,00) | 4% (p 0,00) |

Wat dit waard is. De vloot loopt vrijwel gelijk op met de tijd (correlatie 0,90 en 0,98), dus het model
kan hem niet scheiden van iets anders dat geleidelijk verandert. De toets tussen de markten slaagt niet: de Texaanse
vloot groeide van een vijfde van de Californische naar even groot, maar de Texaanse opbrengst daalde niet ten opzichte
van de Californische (coëfficiënt +0,06, p 0,06). Gebruik 8 tot 10% per GW als bovengrens en test een
batterijcase ook op de helft. Figuren: `fig/11_piek_en_dal.png`, `fig/12_verzadiging_per_gw.png`.

## 6. Gasprijs (`gas.py`)

Bron: IMF en Federal Reserve via FRED, per maand, zonder sleutel. `python3 -m eti.gas ververs` haalt de laatste stand
op; zonder netwerk gebruikt het de momentopname in `data/extern/gasprijs_fred.csv`.

- Nederland: een euro meer voor gas is 1,81 euro meer voor stroom, bovenop 19 euro. Mediaan over 37 zones: 1,79.
- Jaareffect verklaard door gas alleen: prijs 86% (losse jaareffecten 86%), dagspreiding 67% (83%),
  batterij 46% (75%), negatieve uren 2% (56%), capture rate zon 4% (65%).
- Capture-model met gas op de plek van het jaar: zon bij de buren -2,3 punt per procentpunt (t -6,6),
  eigen zon -0,6 (p 0,07). Met jaareffecten: -1,0 en -0,2.
- Terugtoets: met de gasprijs van het jaar zelf zit de raming van de Nederlandse jaarprijs er +2,2%, -5,3%, +4,4%, -4,1%, -0,5% naast
  (2022 tot en met 2026); "vorig jaar herhalen" -57%, +151%, +24%, -11%, -25%.
- 2027: 154 euro per MWh op het pad van de termijnmarkt (gas gemiddeld 75), 176 als gas op 87 blijft, 73 als het terugvalt naar 30.
  De Duitse termijnprijs van 145 euro past in dit model bij gas van 70 euro.

De prognose uit pakket 2 (158, na correctie 148) ligt hier dicht bij. Dat zegt ook dat die prognose geen eigen
informatie toevoegt aan wat de gasmarkt al weet. Figuren: `fig/13_gas_en_stroomprijs.png`, `fig/14_jaareffect_is_gas.png`.

## 7. Balanceringsinkomsten (`stapel.py`)

| Bruto omzet, duizend euro per MW per jaar | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Dagmarkt | 48 | 52 | 60 | 84 |
| Dagmarkt met bijsturen op onbalans | 118 | 101 | 75 | 89 |
| Alleen FCR | 116 | 152 | 160 | 202 |
| Half FCR, half dagmarkt met bijsturen | 117 | 127 | 117 | 146 |
| Per dag wisselen op gisteren | 129 | 140 | 157 | 193 |
| Achteraf de beste (bovengrens) | 170 | 190 | 175 | 220 |

Nodig voor 8% rendement: 85 duizend. Correlatie tussen de dagopbrengst van FCR en van de dagmarkt: -0,06 tot 0,17.
Drie kanttekeningen: de prijs is wat 1 MW erbij zou krijgen en de markt is klein (111 MW voor Nederland, ongeveer
1.700 MW in de gezamenlijke veiling); de capaciteitsprijs van aFRR ontbreekt nog steeds in de eigen data (volgens Modo
Energy van 105 euro per MW per uur in 2022 naar 27 in 2026); netkosten en slijtage zijn niet afgetrokken.
Figuur: `fig/15_stapel_fcr_dagmarkt.png`.

## 8. Kernenergie

Het hoofdstuk staat in de memo (hoofdstuk 17) en het naslagwerk. Uit eigen data (`kernenergie.py`): de capture rate
van kernenergie is rond 1,0 en dat is sinds 2015 niet veranderd; binnen een jaar gaat een hoger kernaandeel samen met
meer negatieve uren (correlatie 0,30) en een lagere capture rate van zon (-0,19), niet met de batterij-omzet (0,05).
Uit bronnen: bouwkosten voor twee Nederlandse centrales 20 tot 30 miljard euro, ingebruikname later dan 2035. De
eigen som (aannames in de memo) komt uit op 78 tot 105 euro per MWh bij 5% kapitaalkosten en 135 tot 191 bij 9%.

## 9. Wat verschoof in de eerdere verslagen

| Cijfer | In 01 tot en met 06 | Nu |
|---|---|---|
| Tests | 155 | 191 |
| Tabellen in het datawoordenboek | 73 | 77 |
| Zone-jaren in het capture-model (alleen gemeten opwek) | 207 | 199 |
| Zon bij de buren (met jaareffecten) | -1,06 punt per procentpunt, t -2,8 | -1,04 punt per procentpunt, t -2,5 (het model gebruikt alleen gemeten opwek; het aanvullen veranderde niets) |
| Capture rate lager in 2025 dan in 2019 | 37 van 37 zones | 37 van 37 zones, gemiddeld -0,35 (weer compleet na het aanvullen) |
| SE3 en SE4 in 2021 | 3,51 en 2,97 als bevinding | afgekeurd; uit instraling 0,90 en 0,89 |
| Capture rates buiten Europa | zie tabel in 4 | herrekend |
| Memo, kannibalisatie (155 land-jaren met gemeten opwek) | eigen zonaandeel met land- en jaareffecten: t = 0,1 | t = -2,3: er blijft een klein eigen effect over (-0,5 punt per procentpunt); met buren erbij is geen van beide aantoonbaar |
| Jaareffect in de capture rate, verklaard door gas | 5% | 4% (losse jaareffecten 65%, gas met zon en wind 53%) |
| Kernaandeel tegen capture rate zon, binnen jaren | -0,21 | -0,19 |

Prognose, scenario's, segmenten en de A/B-proef veranderden niet. Rangcorrelaties in `fact_correlatie_DA` schoven
met hooguit 0,07 doordat er tien zone-jaren bij kwamen.

## 10. Wat je zelf nog draait

```bash
python3 -m eti.gas ververs                       # gasprijs van oktober en november zodra FRED die heeft
bash test_op_mac.sh                              # na elke grote wijziging: alles draaien en testen, daarna de verkenner
```

De waarschuwingen in `resultaten/mac_run.txt` over "the 'generic' unit for NumPy timedelta" komen uit pandas 2.3 in
combinatie met numpy 2.5; ze verdwijnen met `pip install -U pandas` (de werkomgeving draait pandas 3.0 en geeft dezelfde
uitkomsten). Twee waarschuwingen uit de eigen code (`da.py`, `ml_pijplijn.py`) zijn hersteld. De verkenner luistert
voortaan alleen op je eigen machine (`--server.address localhost`); bij de run van vannacht was hij ook op je
thuisnetwerk bereikbaar.

In Power BI of Fabric: laad `dim_datum.csv`, plak `powerbi/maten_analyse.dax` in de DAX-queryweergave, voer uit en
leg de uitkomst naast `powerbi/maten_verwacht.csv`. Het thema staat in `powerbi/thema_analyse.json`.
De map `_to_delete/` kan weg.

## 11. Bronnen

- Gasprijs: [FRED, PNGASEUUSDM](https://fred.stlouisfed.org/series/PNGASEUUSDM) en [EXUSEU](https://fred.stlouisfed.org/data/EXUSEU); oktober 2026 via [cbonds](https://cbonds.com/indexes/71489/)
- Termijnpad gas: [Europese Commissie, Autumn 2026 Economic Forecast](https://economy-finance.ec.europa.eu/document/download/e6bb4d2e-5c46-44e6-a716-6624a57494f3_en?filename=ip348_en.pdf); Duitse termijnprijs: [Tacto](https://www.tacto.ai/en/energy/electricity-price)
- Tijdstempels EIA: [About the EIA-930 data](https://www.eia.gov/electricity/930-content/about.html)
- Kosten kernenergie: [Lazard LCOE+ 2026](https://www.lazard.com/research-insights/levelized-cost-of-energyplus-lcoeplus/), [Utility Dive](https://www.utilitydive.com/news/renewables-remain-cheapest-lcoe-rising-lazard/825443/)
- Nederland: [Kamerbrief 16 mei 2025, samenvatting](https://www.overkernenergie.nl/actueel/nieuws/2025/05/16/volgende-stap-bouw-nieuwe-kerncentrales-onderzoeksplan-locaties-bekend-en-studies-in-borssele-afgerond), [Notitie Reikwijdte en Detailniveau](https://www.rvo.nl/sites/default/files/2026-02/Vastgestelde-NRD-30-januari-2026-Nieuwbouw-Kerncentrales.pdf), [gemeente Borsele](https://www.borsele.nl/nieuwbouw-kerncentrales), [Omroep Zeeland](https://www.omroepzeeland.nl/nieuws/17880981/borssele-mag-langer-open-kabinet-wil-zelf-voor-miljarden-nieuwe-kerncentrales-opdraaien)
- Taxonomie: [Gerecht van de EU, perscommuniqué 113/25](https://curia.europa.eu/jcms/jcms/p1_5134860/hu)
- Diablo Canyon: [E&E News](https://www.eenews.net/articles/californias-nuclear-plant-gets-20-year-extension-from-federal-regulators/)
- FCR en aFRR: [TenneT, Dutch Ancillary Services](https://www.tennet.eu/markets/dutch-ancillary-services), [GEM Energy Analytics](https://gemenergyanalytics.substack.com/p/updates-on-fcr-prices), [Modo Energy](https://modoenergy.com/research/fr/nl-netherlands-bess-capacity-market-tennet-afrr-2026)
