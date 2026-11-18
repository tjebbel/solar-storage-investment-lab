# 08 Vervolg 18 november: verbeterpunten en zeven vervolgonderzoeken

Stand: 18 november 2026, middag. Dit verslag hoort bij het verzoek om de verbeterpunten in data en methode door te voeren,
opnieuw te evalueren, het naslagwerk aan te vullen en de zeven vervolgonderzoeken uit te voeren. Alles is opnieuw te
maken met `bash run_analyse.sh` (vijf nieuwe stappen aan het eind). Tests: 203 (was 191), alle geslaagd.

## 1. In het kort

1. **Het verschil tussen de twee zonbronnen is vooral ontbrekende data, niet zon achter de meter.** Zonder de 34
   land-jaren waarin Energy-Charts (bijna) geen zon meet, verdwijnt het gemiddelde verschil met Ember (van -6 tot -12%
   naar -2 tot +5%). Wat overblijft zijn vaste definitieverschillen per land, in beide richtingen; buiten de steekproef
   voorspellen ze zichzelf goed (fout 25% naar 2% voor de zes landen die structureel lager zitten).
2. **De segmenten zijn per jaar robuust, per zone vaak niet.** In 2023-2025 is 16 tot 23 van de 37 zones een grensgeval.
   Nederland 2025 is er een: met de capture rate van een dak in plaats van een park wordt het 'zonverzadigd'.
3. **FCR levert 2,3 tot 4,2 keer de dagmarkt op** in de acht zones van de gezamenlijke FCR-veiling (2025). aFRR-capaciteit
   heeft alleen twee ijkpunten (Nederland 2022 en 2026). De markten zijn klein en de bronnen zijn alternatieven per uur.
4. **Een batterij op de dagmarkt alleen haalt 8% net bij de bouwkosten van nu (280 euro per kWh) en alleen zonder
   netkosten.** Extra cycli helpen niet: de meeropbrengst (+17% bij twee cycli) weegt niet op tegen de kortere levensduur.
   Met volledige stapeling is er ruimte tot 451-586 euro per kWh, zonder capaciteitsvergoedingen niet (206).
5. **Het schokjaar 2026 is voor driekwart gas.** Januari tot en met oktober: +33 euro per MWh; gas 25, zon en wind samen
   -0,2, rest 8 (vooral Noorwegen: waterstanden zitten niet in het model).
6. **Op dezelfde Mac is SQLite bij alle drie de query's sneller dan SQL Server in Docker**; herschrijven wint in beide
   systemen een factor 3.000 of meer. De DAX-toets staat klaar voor Fabric of Windows.

## 2. Herevaluatie: wat eerder niet klopte

- **De 'ontbrekende komma' in `sql/02_optimalisatie.sql` bestond niet.** De regel is langer dan 160 tekens en mijn
  controle (`cut -c1-160`) knipte de komma eraf. Het bestand op de Mac en in de werkomgeving zijn gelijk en kloppen.
- **"56% wijkt af" kwam door de tolerantie van 0,5 procentpunt die ik voor de T-SQL-run koos.** De standaard in
  `sql_run.py` was 2,0. Nu: de ruimste van 0,5 procentpunt en 10% van B, en dekkingsgaten apart. Dan wijkt 45% af van
  de land-jaren zonder gat.
- **Wat in de werkomgeving staat, is niet vanzelf wat op de Mac staat.** Twee keer liep een kopie uiteen. Voor deze
  ronde zijn de bestanden eerst met controlesommen vergeleken: alle code was gelijk, alleen analyse-uitvoer verschilde
  (pandas 2.3 tegen 3.0, afronding).

## 3. Verbeterpunten in data en methode

| Punt | Wat er veranderd is | Bestand |
|---|---|---|
| Tolerantie aansluiting | ruimste van een vaste (0,5 pp) en een relatieve (10% van B) | `sql/05_reconciliatie.sql`, `sql/tsql/05_reconciliatie.sql`, `sql_run.py` |
| Bijna-nul waarden in A | eigen categorie 'dekkingsgat in A' (A < 25% van B), telt niet in het gemiddelde verschil | idem |
| Restgroep 'overig' | opgesplitst in 'structureel lager', 'structureel hoger' (80% van de jaren aan dezelfde kant) en 'wisselend' | idem |
| Segmentgrenzen | gevoeligheidstoets en kolom `grensgeval` per zone-jaar | `eti.segment_gevoeligheid` |
| DISTINCT op kommagetallen | afronding op 6 decimalen in de trage T-SQL-query, met uitleg | `sql/tsql/02_optimalisatie.sql` |
| T-SQL-scripts | gelijk aan wat op de Mac werkte: `-d solar`, `alle` voor geen filter, geen CODEPAGE, tijdmeting | `sql/tsql/*` |
| Ongewogen gemiddelde over zones | niet opgelost: er is geen opwek per zone in de data | onzekerhedenregister |

Uitkomst van de nieuwe aansluiting (SQLite, 182 land-jaren in beide bronnen): sluit aan 82, dekkingsgat 34,
structureel hoger 32, structureel lager 24, wisselend 10; tijdsverschil 26, alleen in B 106.

## 4. De zeven vervolgonderzoeken

### 4.1 Zon achter de meter (`eti.bronnen_toets`)

| Verschil A tegen B (%) | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Alle 26 landen | -9,3 | -6,9 | -8,0 | -11,7 | -10,3 | -5,9 | -6,3 |
| Zonder dekkingsgaten | +4,6 | +1,4 | +1,6 | -1,9 | -1,2 | +0,8 | +0,5 |

Dekkingsgaten: Nederland (alle jaren, A telt 3-5%), Noorwegen, Servie, en de eerste jaren van Finland, Zweden, Letland,
Polen, Estland en Hongarije. Structureel lager in A (geschatte ontbrekende zon 2025): Oostenrijk 4,6 TWh, Hongarije 2,8,
Roemenie 1,2, Portugal 0,8, Slovenie 0,6, Slowakije 0,1; samen 10,2 TWh. Structureel hoger: Zwitserland, Finland,
Estland, Griekenland, Polen, Tsjechie, Italie, Frankrijk, Spanje. Duitsland als ijkpunt: 67 van 100 GW op daken
(BSW-Solar, eind 2024), A/B toch ongeveer 1.

Toets buiten de steekproef (verhouding uit 2019-2022 als correctie op 2023-2025, mediane fout |A-B|/B):

| Groep | Land-jaren | Zonder correctie | Met correctie | Beter |
|---|---|---|---|---|
| Alle landen | 65 | 12,8% | 7,4% | 60% |
| Structureel lager in A | 18 | 24,6% | 2,1% | 89% |
| Structureel hoger in A | 24 | 14,7% | 7,0% | 83% |
| Wisselend of gelijk | 23 | 6,4% | 8,9% | 13% |

Conclusie: Ember voor het niveau, de gemeten reeks voor de vorm. Dat het om zon achter de meter gaat is aannemelijk voor
de zes 'lager'-landen, maar de data tonen alleen dat het verschil vast is, niet waar het vandaan komt.

### 4.2 Segmenten (`eti.segment_gevoeligheid`)

Grootste verschuiving per drempel (20% omhoog of omlaag, aandeel zone-jaren dat wisselt): capture rate vanaf 0,75
('zon houdt waarde') 19,6%; dagspreiding vanaf 120: 6,8%; capture rate onder 0,60: 5,7%; dagspreiding onder 60: 5,4%;
negatieve uren vanaf 300: 2,0%. Grensgevallen (minder dan 80% van 2.000 trekkingen hetzelfde segment): 0, 0, 9, 4, 23,
16, 17, 11 in 2019-2026. Per segment (2023 en later): vlakke prijzen 11%, batterijmarkt 27%, zon houdt waarde 64%,
zonverzadigd 67%, middenveld 88%. Nederland 2025: 31% (dagspreiding 124 tegen drempel 120; capture rate 0,615 tegen 0,60).

### 4.3 Bronnen van batterij-opbrengst (`eti.batterij_bronnen`)

| Nederland, euro per MW per jaar | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Dagmarkt (plan op gisteren) | 47.320 | 52.710 | 61.041 | 81.874 |
| FCR, alle blokken | 116.179 | 152.283 | 159.651 | 201.977 |
| aFRR-capaciteit 27 euro/MW/u, 50% toegewezen | | | | 118.260 |
| aFRR-capaciteit, alle uren | | | | 236.520 |

FCR-leden 2025, FCR gedeeld door dagmarkt: Slovenie 2,3, Duitsland 2,6, Nederland 2,6, Oostenrijk 2,8, Belgie 2,9,
Denemarken-West 3,0, Frankrijk 3,8, Zwitserland 4,2. Kanttekeningen: Nederlandse FCR-prijs als benadering voor de leden;
prijs voor 1 MW erbij; veiling ca. 1.700 MW; aFRR alleen ijkpunten (Modo Energy); bronnen niet optelbaar.

### 4.4 Bouwkosten en cycli (`eti.batterij_irr`)

Meeropbrengst op de dagmarkt bij meer cycli (volledige kennis, Nederland 2025-2026): 1,5 cyclus +9,8%, 2 cycli +16,6%.
Levensduur bij 6.000 cycli: 15, 10 en 8 jaar.

| Inkomsten en netkosten | Cycli | Max. euro/kWh voor 8% | voor 5% |
|---|---|---|---|
| Dagmarkt met bijsturen, geen netkosten | 1 | 286 | 333 |
| idem | 1,5 | 262 | 295 |
| idem | 2 | 246 | 273 |
| Dagmarkt met bijsturen, tijdsafhankelijk transportrecht | 1 | 77 | 88 |
| Volledige stapeling, vast transportrecht | 1 | 451 | 518 |
| Volledige stapeling, tijdsafhankelijk transportrecht | 1 | 586 | 680 |
| Stapeling zonder capaciteitsvergoedingen, tijdsafhankelijk | 1 | 206 | 238 |

Volledig rooster in `fact_batterij_irr_grid_BI.csv`.

### 4.5 Schokjaar 2026 (`eti.schokjaar`)

Maandmodel 2019-2025, 2.116 zone-maanden, R2 0,84. Coefficienten (standaardfout geclusterd per maand): gas 1,58 (0,03),
zon 0,42 (0,19), wind -1,00 (0,17). Januari-oktober 2026 tegen 2025, 28 zones met tien maanden: prijsstijging 33,0; door
gas 25,0 (76%); zon 0,7; wind -0,9; rest 8,1. Rest het grootst in NO3 (46), NO5 (41), NO1 (29), NO2 (24) en Italie (7-13);
negatief in Griekenland (-12), Portugal (-11), Spanje (-9). Het positieve teken bij zon is waarschijnlijk geen oorzaak
maar samenloop (zon groeit in dezelfde jaren dat de prijs stijgt); lees het als 'niet te onderscheiden van nul'.

### 4.6 Eerlijke snelheidsmeting (`eti.sql_benchmark`, `sql/tsql/benchmark_tsql.sh`)

Gemeten op de iMac, 18 november 13:25: dezelfde data, juni 2025, opwarmronde plus vijf rondes, mediaan in ms.

| Query | SQLite 3.48 | SQL Server 2022 (Docker, linux/amd64) |
|---|---|---|
| Traag | 14.232 | 35.903 |
| Snel | 0,25 | 12 |
| Voorberekend | 0,09 | 1 |
| Traag / snel | 56.600 | 3.000 |

SQLite is op deze machine bij alle drie sneller. SQL Server draaide de trage query deze keer op een kern (processortijd
gelijk aan verstreken tijd); eerder op de dag parallel (13 s processortijd in 1,8 s). Waarom het plan wisselde is niet
vastgesteld. De les van herschrijven (factor 3.000 tot 56.000) is veel groter dan het verschil tussen de systemen.

### 4.7 Power BI en DAX (`eti.powerbi_toets vergelijk`)

Nieuw: `python3 -m eti.powerbi_toets vergelijk export.csv` legt de uitkomst van de toetsvraag uit Power BI of Fabric
waarde voor waarde naast `powerbi/maten_verwacht.csv` (66 waarden, marge 0,01) en schrijft `resultaten/dax_vergelijking.csv`.
Uitvoeren vraagt Power BI Desktop op Windows of een Fabric-account.

## 5. Nieuwe tabellen in `powerbi/data`

`fact_bronnen_land_RC`, `fact_bronnen_jaar_RC`, `fact_bronnen_toets_RC`, `fact_segment_drempel_SG`, `fact_segment_zone_SG`,
`fact_batterij_bronnen_BB`, `fact_batterij_bronnen_nl_BB`, `fact_batterij_irr_grid_BI`, `fact_batterij_breakeven_BI`,
`fact_schokjaar_zone_SJ`, `fact_schokjaar_model_SJ`.

## 6. Wat nog op de Mac moet

```bash
cd ~/projecten/tjebbel/set_up/energy_dashboard/solar-storage-investment-lab
bash run_analyse.sh                                   # alles opnieuw, met de vijf nieuwe stappen en 203 tests
bash ~/projecten/sqlserver_import/run_tsql.sh         # T-SQL met de nieuwe aansluiting (05)
PYTHONPATH=src .venv/bin/python -m eti.sql_benchmark sqlite
bash sql/tsql/benchmark_tsql.sh
PYTHONPATH=src .venv/bin/python -m eti.sql_benchmark samen
```

## 7. Naslagwerk

Toegevoegd: *De keten op een pagina* (voor deel I), hoofdstuk 20 *De SQL-laag*, hoofdstuk 21 *Ronde 18 november*,
hoofdstuk 22 *Onzekerhedenregister*. Bijgewerkt: de zin dat T-SQL niet is uitgevoerd, de verbeterpunten (nu 15) en de
leesroute. 291 pagina's.

## 8. Na de run op de Mac (13:20)

- `run_analyse.sh` draaide zonder pandas en numpy: `source .venv/bin/activate` wijst na het verplaatsen van de repo nog
  naar de oude map op het Bureaublad. Het script roept nu `.venv/bin/python` rechtstreeks aan. Ook `pip` in de omgeving
  wijst nog naar het Bureaublad; gebruik `.venv/bin/python -m pip`, of maak de omgeving opnieuw.
- De T-SQL-run met de nieuwe aansluiting gaf exact de SQLite-uitkomst (182, 82, 34, 66, 44,6%).
