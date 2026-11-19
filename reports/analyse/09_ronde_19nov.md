# Ronde 18-19 november 2026: publicatie, kernenergie, signalering en data voor dashboards 4-15

Het hoofdstuk "Ronde 18-19 november" in het naslagwerk (`reports/Naslagwerk_Zon_Opslag_Duurzame_Financiering.pdf`) bevat de duiding,
de nieuwe begrippen en de herevaluatie. Hieronder staan de ruwe uitkomsten per module, zoals ze uit de code komen.

## 1. Publicatie
- Dashboard 1 *Eerste bevindingen* staat op Tableau Public; README met afbeelding en link.
- Repo opgeruimd: 870 -> 386 bestanden; logs, oude jaarruns, sessiescripts en tijdelijke Tableau-bestanden uit git (lokaal bewaard).
- Les: Tableau Desktop Professional publiceert pas naar Tableau Public als alle bronnen extracten zijn.

## 2. Kernenergie (`eti.kern_wereld`, t6-t8)
```
Wereld kern: 2540 TWh in 2000, 2533 in 2015, 2805 in 2025; aandeel 16.6% -> 8.8%
Wereld zon: 256 TWh in 2015 -> 2807 in 2025; zon voorbij kern sinds 2025
Europa kern: 1180 TWh in 2000 -> 996 in 2025; zon 444, wind 627 TWh
  zon voorbij kern, Europa: nan
  zon voorbij kern, EU: nan
  zon voorbij kern, Noord-Amerika: nan
  zon voorbij kern, Azie: 2023
  zon voorbij kern, China: 2022
  zon voorbij kern, Verenigde Staten: nan
  zon voorbij kern, Frankrijk: nan
  zon voorbij kern, Duitsland: 2022
  zon voorbij kern, Japan: 2014
  zon voorbij kern, India: 2020
Koers Afbouw: France, Canada, Sweden, United Kingdom, Switzerland, South Africa, Taiwan (China)
Koers Geen gegevens 2025: Ukraine
Koers Gestopt: Germany, Lithuania
Koers Herstart: Japan
Koers Stabiel: United States, Spain, Belgium, Hungary, Brazil, Bulgaria, Romania, Mexico, Slovenia, Iran, Netherlands, Armenia
Koers Uitbouw: China, Russia, South Korea, India, United Arab Emirates, Finland, Czechia, Pakistan, Slovakia, Belarus, Argentina
Grootste groei kern 2015-2025 (TWh): China +314, Japan +90, United Arab Emirates +39, Russia +23, South Korea +20
Grootste krimp kern 2015-2025 (TWh): Germany -92, France -45, United Kingdom -34, Taiwan (China) -33, Canada -16
Laagste CO2-intensiteit onder landen met kern (g/kWh, 2025): Sweden 35, Switzerland 39, France 41, Finland 59, Slovakia 95, Brazil 109
Europese dagmarkt 2026: capture rate kern gemiddeld 1.00, zon in dezelfde landen 0.61
```

## 3. Signalering (`eti.signalering_europa`, t9-t10)
Python geeft voor Nederland 2026 66 van 66 waarden gelijk aan `powerbi/maten_verwacht.csv`.
Aandeel zone-maanden met 'Let op' of 'Schok': 2020 30%, 2021 57%, 2022 22%, 2023 0%, 2024 16%, 2025 9%, 2026 35%.

## 4. Data voor dashboards 4-15
### Dashboard 4: ervaringscurve en portefeuille (`eti.bcg_portefeuille`, t11-t12)
```
Ervaringscurve 2017-2025: leersnelheid 35.0% (95%: 21.5% tot 46.2%), R2 0.81, n=9
Ervaringscurve 2017-2025 zonder 2021,2022: leersnelheid 35.6% (95%: 26.2% tot 43.8%), R2 0.93, n=7
Portefeuille 2022: Ster: HUN, LTU, NLD; Melkkoe: BGR, DEU, GRC, ROU; Vraagteken: DNK, ESP, POL, PRT; Hond: AUT, CZE, FRA
Portefeuille 2025: Ster: BGR, LTU, POL, ROU; Melkkoe: DEU, GRC, HUN; Vraagteken: AUT, DNK, ESP, FIN, PRT; Hond: BEL, CZE, FRA, ITA, NLD
Van ster naar iets anders (2022 -> 2025): HUN (Melkkoe), NLD (Hond)
```
### Dashboard 5: kostencurve (`eti.mck_kostencurve`, t13)
```
Landcode  Capture-prijs zon EUR/MWh  LCOE  Emissiefactor gemiddeld t/MWh  Kosten per ton (gemiddelde factor)  Kosten per ton (marginale factor)  Extra zon TWh  Potentieel Mt (marginale factor)
     ITA                      94.77 51.09                           0.28                             -153.29                            -109.20          52.96                             21.18
     BGR                      73.30 51.09                           0.28                              -80.68                             -55.54            NaN                               NaN
     HRV                      69.42 51.09                           0.16                             -115.64                             -45.83           1.78                              0.71
     SVN                      65.91 51.09                           0.18                              -81.04                             -37.06           2.25                              0.90
     SRB                      64.61 51.09                           0.70                              -19.43                             -33.79            NaN                               NaN
     ROU                      64.42 51.09                           0.26                              -51.58                             -33.33           5.84                              2.34
     GRC                      59.81 51.09                           0.32                              -26.87                             -21.81           9.52                              3.81
     POL                      67.27 67.39                           0.59                                0.20                               0.29           5.26                              2.10
     HUN                      62.56 67.39                           0.16                               29.80                              12.07           2.32                              0.93
     CHE                      60.36 67.39                           0.04                              178.86                              17.56           0.82                              0.33
     SVK                      56.86 67.39                           0.10                              110.50                              26.32           0.75                              0.30
     LVA                      55.40 67.39                           0.13                               88.85                              29.96           1.16                              0.46
     CZE                      54.85 67.39                           0.40                               31.28                              31.34           5.52                              2.21
     NLD                      53.42 67.39                           0.25                               55.08                              34.93           0.00                              0.00
     ESP                      36.10 51.09                           0.15                               97.32                              37.49          75.28                             30.11
     DNK                      51.94 67.39                           0.12                              129.14                              38.63          20.08                              8.03
     PRT                      35.34 51.09                           0.13                              123.23                              39.37          15.62                              6.25
     AUT                      49.32 67.39                           0.12                              154.98                              45.18           8.70                              3.48
     LTU                      48.89 67.39                           0.14                              133.93                              46.25           0.00                              0.00
     EST                      46.87 67.39                           0.32                               64.37                              51.30           0.51                              0.20
     DEU                      46.07 67.39                           0.33                               63.82                              53.31            NaN                               NaN
     BEL                      42.46 67.39                           0.15                              164.81                              62.32           0.74                              0.29
     FIN                      36.05 67.39                           0.06                              533.42                              78.35           4.53                              1.81
     FRA                      35.91 67.39                           0.04                              763.60                              78.70          32.99                             13.19
     NOR                      30.88 67.39                           0.03                             1301.67                              91.28           5.45                              2.18
     SWE                      21.24 67.39                           0.04                             1304.01                             115.37           4.36                              1.74

Landen waar extra zon al geld oplevert (capture-prijs boven LCOE): ITA, BGR, HRV, SVN, SRB, ROU, GRC
Potentieel 2025-2030 met doelen bekend: 102.6 Mt per jaar (marginaal), 45.6 Mt (gemiddeld); landen zonder doel: BGR, SRB, DEU
```
### Dashboard 7: controlematrix en risicokaart (`eti.assurance_overzicht`, t15-t16)
```
Controle                                             Doel                                                                                    Uitkomst                 Status
     C01            Zelfde uitkomst in twee SQL-dialecten                                                stappen 00-05 gelijk in aantallen en waarden               Geslaagd
     C02      Signaleringsmaten gelijk aan de verwachting                                                                    66 van 66 waarden gelijk               Geslaagd
     C03       Tableau rekent hetzelfde als DAX en Python                                           nog uit te voeren met eti.powerbi_toets vergelijk                   Open
     C04                        Power BI rekent hetzelfde                                                                     wacht op Fabric-toegang                   Open
     C05             Zonaandeel in twee bronnen sluit aan 82 sluiten aan, 34 dekkingsgaten, 66 wijken af; het verschil verdwijnt zonder dekkingsgaten    Afwijking verklaard
     C06       Correctiefactor werkt buiten de steekproef                            mediane fout 13% -> 7% na correctie, 60% van 65 land-jaren beter Geslaagd met beperking
     C07                                 Testsuite slaagt                                                                  209 tests, 28 overgeslagen               Geslaagd
     C08 Prestaties reproduceerbaar op een tweede machine                              patroon gelijk; SQL Server-plan draaide de tweede keer serieel Geslaagd met beperking
     C09                Volledigheid kerncijfers per land      Oekraine zonder 2025-cijfer; vermogen Belgie geeft benutting boven 100% (leeg gelaten)    Afwijking verklaard
     C10                    Teken en dekking grensstromen                                            nog niet gecontroleerd; daarom niet gepubliceerd                   Open
     C11            Twee bronnen voor de Chinese bouwgolf                                    zelfde patroon, ander niveau; bron in subtitel vermelden    Afwijking verklaard
     C12         Gepubliceerde cijfers gelijk aan de bron                  visueel gecontroleerd op 18-11 (kaart 2025: 0,50-0,89; referentielijn 280)               Geslaagd

Status: Geslaagd 4, Open 3, Afwijking verklaard 3, Geslaagd met beperking 2

                                                             Risico  Kans  Impact                                   Maatregel Dashboards  Score
                              Gemiddelde of marginale emissiefactor     3       3                       beide varianten tonen   5, 7, 14      9
Segmentgrenzen zijn een keuze; 16-23 zones per jaar zijn grensgeval     3       2                  gevoeligheid tonen (+-20%)       1, 4      6
                  Capture rate Nederland: park (0,62) of dak (0,52)     2       3                beide tonen; keuze per vraag    1, 2, 8      6
                 aFRR-capaciteitsprijs: twee ijkpunten (2022, 2026)     3       2                           tijdreeks ophalen       1, 6      6
                                      LCOE alleen voor vijf regio's     3       2 noord/zuid-aanname in subtitel; bandbreedte  5, 14, 15      6
                                           WACC voor Afrika onzeker     3       2                              als band tonen         15      6
                                     Ember herziet cijfers achteraf     2       2                    downloaddatum vastleggen       alle      4
                Paneelprijs is een exportwaarde, geen fabrieksprijs     2       2             leersnelheid met interval tonen          4      4
                  Grensstromen: teken en dekking niet gecontroleerd     2       2                     eerst controleren (C10)      9, 13      4
                      2026 is een onvolledig jaar (tot 15 november)     3       1                     in elke titel vermelden       alle      3
                      Laadprofiel elektrische auto's is een aanname     3       1                       als scenario markeren         13      3
```
### Dashboards 9-11: EU, VS, China (`eti.overheden`, t18, t20-t22)
```
Prijsspreiding over de zones per jaar (gemiddelde van de maanden):
      Mediaan  Spreiding P90-P10  Relatieve spreiding
Jaar                                                 
2019    42.23              17.28                 0.42
2020    32.93              31.12                 0.96
2021   100.48              66.41                 0.59
2022   243.40             202.92                 0.82
2023    97.81              76.82                 0.79
2024    79.46              78.43                 0.97
2025    88.71              83.15                 0.96
2026   127.73             101.76                 0.79

Gebeurtenisstudie zon:
            Land                                               Gebeurtenis  GW per maand ervoor  GW per maand erna  Maanden erna Piekmaand  Piek GW
Verenigde Staten                              OBBBA getekend (4 juli 2025)                  3.1                3.8            12   2025-01      4.5
Verenigde Staten                 Grens bouwstart zon en wind (4 juli 2026)                  3.1                2.0             2   2026-04      5.3
           China Document 136: nieuwe projecten via de markt (1 juni 2025)                 48.8               18.6            12   2025-05    110.9

Top 5 staten zon en wind:
           Staat  Aandeel zon %  Aandeel wind %  Aandeel zon en wind %  Jaar
Washington, D.C.           69.4             0.0                   69.4  2025
            Iowa            2.5            58.5                   61.0  2025
    South Dakota            2.0            58.0                   60.0  2025
      New Mexico           17.4            35.7                   53.1  2025
          Kansas            1.1            46.9                   48.0  2025

Chinese panelexport (GW) per jaar en bestemming:
Bestemming  Africa  Asia  Europe  Latin America and Caribbean  Middle East  North America  Oceania
Jaar                                                                                              
2017           1.0  19.0     3.0                          4.0          2.0            2.0      2.0
2018           4.0  22.0     8.0                          9.0          3.0            0.0      5.0
2019           3.0  26.0    23.0                         11.0          3.0            1.0      5.0
2020           2.0  33.0    29.0                         10.0          3.0            2.0      4.0
2021           3.0  33.0    43.0                         16.0          4.0            1.0      5.0
2022           4.0  29.0    85.0                         24.0          8.0            0.0      5.0
2023           9.0  47.0   101.0                         29.0         14.0            1.0      7.0
2024          13.0  61.0    97.0                         32.0         27.0            1.0      7.0
2025          19.0  69.0    98.0                         28.0         26.0            2.0      7.0
2026          16.0  47.0    71.0                         16.0         15.0            2.0      7.0
```
### Dashboard 13: netbeheerder en EV (`eti.net_flex`, t25-t26)
```
 Jaar  Kwartieren  Op gemiddeld  Op mediaan  Op P99  Aandeel op boven 200 %  Af gemiddeld  Aandeel af negatief %  Negatieve uren
 2019         NaN           NaN         NaN     NaN                     NaN           NaN                    NaN               3
 2020         NaN           NaN         NaN     NaN                     NaN           NaN                    NaN              97
 2021         NaN           NaN         NaN     NaN                     NaN           NaN                    NaN              70
 2022         NaN           NaN         NaN     NaN                     NaN           NaN                    NaN              86
 2023     34856.0          88.6         0.0  1143.6                     7.7           9.8                   19.7             315
 2024     35103.0          94.5        70.0  1837.6                     5.2           0.1                   25.7             458
 2025     25505.0          94.4        88.6   550.0                     3.5          15.7                   21.0             584
 2026         NaN           NaN         NaN     NaN                     NaN           NaN                    NaN             399

Nederland: 1,415,536 EV's, 3,279 GWh per jaar; ongestuurd laden geeft (aanname) ongeveer 1.12 GW extra avondpiek, gestuurd laden neemt 0.90 GW van het middagoverschot op.
```
### Dashboards 14-15: impact en Mondiale Zuiden (`eti.impact_zuiden`, t27-t28)
```
          Regio  LCOE EUR/MWh  WACC  LCOE bij 5% WACC  Ton CO2 per M EUR per jaar  Marge zon EUR/MWh             Additionaliteit (indicatief)
      Nederland         67.39  0.05             67.39                       246.2             -13.97         hoog: zonder steun niet rendabel
Europa (Spanje)         51.09  0.06             48.99                       121.7             -14.99         hoog: zonder steun niet rendabel
     VS (Texas)         64.56  0.06             59.46                       329.4                NaN onbekend: geen marktprijs in het project
          China         29.83  0.04             31.15                      1090.6                NaN onbekend: geen marktprijs in het project
   India (RvdW)         44.42  0.12             27.67                      1474.5                NaN onbekend: geen marktprijs in het project

          Locatie  Instraling  Vollasturen  Jaren  Vollasturen tegen Nederland
  Egypte (Benban)     2370.03      1896.03     11                         2.12
  Chili (Atacama)     2280.50      1824.40     11                         2.04
    Saoedi-Arabie     2221.40      1777.12     11                         1.99
           Mexico     2147.52      1718.02     11                         1.92
      Zuid-Afrika     2147.05      1717.64     11                         1.92
            Kenia     2113.18      1690.55     11                         1.89
          Marokko     2073.68      1658.94     11                         1.86
         Brazilie     2049.80      1639.84     11                         1.84
       Californie     2034.37      1627.50     11                         1.82
India (Rajasthan)     1994.00      1595.20     11                         1.79
          Nigeria     1923.82      1539.06     11                         1.72
 Australie (Zuid)     1883.75      1507.00     11                         1.69
            Texas     1867.38      1493.91     11                         1.67
          Vietnam     1839.81      1471.84     11                         1.65
        Indonesie     1723.65      1378.92     11                         1.54
           Spanje     1717.50      1374.00     11                         1.54
  China (Qinghai)     1674.40      1339.52     11                         1.50
           Italie     1672.71      1338.17     11                         1.50
            Japan     1439.49      1151.59     11                         1.29
        Nederland     1115.68       892.55     11                         1.00
            Polen     1108.08       886.46     11                         0.99
        Duitsland     1107.31       885.85     11                         0.99
               VK     1075.84       860.67     11                         0.96
           Zweden     1035.25       828.20     11                         0.93
```

## 5. Nog open (verbeterpunten 16-25 in het naslagwerk)
| # | Punt | Wat nodig is |
|---|---|---|
| 16 | Saldering NL (t17) | uurprofiel dak, leveringstarieven 2026-2027 |
| 17 | Netcongestie | capaciteitskaart netbeheerders |
| 18 | NGFS-prijspaden (t24) | download NGFS-scenario's |
| 19 | Grensstromen | teken en dekking controleren (C10) |
| 20 | LCOE per land | IRENA/Lazard per land |
| 21 | Marginale emissiefactor per uur | ENTSO-E opwek per bron + factoren |
| 22 | Tableau-toets 66/66 | 19 november, dashboard 2 |
| 23 | WACC Afrika/ZO-Azie | IEA Cost of Capital Observatory |
| 24 | EU-doelpad, Chinese provincies (t19, t23) | modules schrijven; data lokaal |
| 25 | Paneelprijs als fabrieksprijs | prijsreeks (bijv. InfoLink/PVinsights) |

Tests: 213 (209 + 4 nieuw in `tests/test_dashboards_4_15.py`), alle geslaagd; 28 overgeslagen in de Mac-VM zonder Streamlit.
