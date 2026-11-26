# Downloads die je zelf moet doen (bijgewerkt ma 23 november 2026)

Claude kan vanuit deze sessie niets downloaden: de werkomgeving op de iMac heeft geen netwerk en de cloudomgeving mag geen
bestanden van websites halen. Alles wat lokaal kon, staat klaar (dashboards 25-30: t63-t72). Zet elk bestand in de genoemde map
en zeg het; dan zet ik het om naar tabellen, met tests en een stappenplan.

| # | Wat | Waar te vinden | Opslaan als | Voor | Uiterlijk |
|---|---|---|---|---|---|
| 1 | NGFS-scenario's (fase V): elektriciteitsprijs, CO2-prijs, zon/wind-capaciteit per regio | NGFS Scenario Explorer (IIASA), gratis account | `data/extern/ngfs/` (niet op GitHub: licentie) | 12 | 7 dec |
| 2 | World Bank Pink Sheet, maanddata (zilver, koper, aluminium) | worldbank.org → Commodity Markets → "Monthly prices" (Excel) | `data/extern/pink_sheet_monthly.xlsx` | 21 | 8 dec |
| 3 | IRENA Renewable Energy and Jobs, annual review 2025 (tabellen) | irena.org → Publications | `data/extern/irena_jobs_2025.xlsx` of pdf | 22 | 9 dec |
| 4 | CBS/TNO Monitor Energiearmoede 2019-2025 | cbs.nl (StatLine of publicatie) | `data/extern/energiearmoede.csv` | 23 | 10 dec |
| 5 | IEA Global Hydrogen Review 2025, data annex (CC BY 4.0) | iea.org → Data and statistics | `data/extern/iea_hydrogen_2025.xlsx` | 24 | 11 dec |
| 6 | NEDU verbruiks- en opwekprofielen (zon, uur, 2025-2026) | nedu.nl → Verbruiksprofielen | `data/extern/nedu_profielen_2026.xlsx` | 8 v2, post salderen 29 dec | 22 dec |
| 7 | Terugleververgoedingen 2027 van drie grote leveranciers (tabel met bron en datum) | websites leveranciers | `data/extern/terugleververgoeding_2027.csv` | 8 v2 | 22 dec |
| 8 | IEA Cost of Capital Observatory (WACC per land, zon) | iea.org | `data/extern/iea_wacc.xlsx` | 15, 41 (WACC Afrika) | jan |
| 9 | LevelTen PPA Price Index, kwartalen 2022-2026 (persberichten) | leveltenenergy.com → reports | aanvullen in `data/extern/ppa_prijzen.csv` | 17 v2 | jan |
| 10 | TenneT: officiële wachtrij afname per congestiegebied | tennet.eu → capaciteitskaart / Kamerbrief | `data/extern/tennet_wachtrij.csv` | C20 | jan |
| 11 | Synertics: definitie van hun capture rate Spanje (mail of methodenotitie) | synertics.io | notitie in `docs/` | C19 | dec |

Niet nodig voor 25-30: Energy-Charts, CAISO, ERCOT, AEMO, JEPX, Elexon, OWID en de ENTSO-E-bestanden staan al in `data/raw`.

## Dashboards 32-36 (toegevoegd 22 nov)
| Voor | Data | Waar |
|---|---|---|
| 32 | LCOE zon per land | IRENA Renewable Power Generation Costs (xlsx); Lazard LCOE+ |
| 33 | WACC per land/regio | IEA Cost of Capital Observatory (iea.org) |
| 35 | Wachtrij TenneT, officiele reeks | tennet.eu, Netbeheer Nederland capaciteitskaart-archief |
| 36 | Uurprofiel zon op dak; terugleververgoeding en -kosten 2027 | KNMI/PVGIS-profiel; tarieven leveranciers, ACM |
| 31 | Fabric-toegang (trial of werkgever) | app.fabric.microsoft.com |

## Toegevoegd ma 23 nov (audit van alle tabellen)
| Voor | Data | Waar |
|---|---|---|
| 5, 26, 37 | 2030-doel zon voor Duitsland, Bulgarije en Servië (TWh of GW met vollasturen) | NECP's (Europese Commissie), Ember Target Tracker; toevoegen aan de bron van `t13` |
| 5, 26, 27, 37 | LCOE zon per land (nu twee waarden voor alle landen): zelfde bestand als dashboard 32 | IRENA Renewable Power Generation Costs; Lazard LCOE+ |
| 17, 37 | LevelTen P25 per land, meer kwartalen en meer landen (nu vijf landen, één kwartaal) | LevelTen-persberichten per kwartaal; aanvullen in `data/extern/ppa_prijzen.csv` |
| 17 | KYOS PPA Report, nieuwere uitgave dan juni 2025 | kyos.com → PPA Insights; nieuw bestand naast `data/extern/ppa_kyos_2025_06.csv` |

Al gedaan op 23 nov zonder download: Frankrijk en Griekenland (LevelTen via pv magazine) en de KYOS-tabel van juni 2025 (39 zones).

## Stand di 24 nov
- Binnen: Wereldbank Pink Sheet (`data/extern/pink_sheet_monthly.xlsx`, voor 21) en IRENA Renewable Energy Statistics 2026
  (PUBFIN en RESHARE als csv in `data/extern`, voor 15 en 33; t83 en t84).
- IRENA Stats Tool (`.xlsb`, 18 MB) is aangeleverd maar nog niet verwerkt.
- Nog steeds nodig voor 32: IRENA Renewable Power Generation Costs (LCOE per land); dat is een ander bestand, achter een formulier.
- Binnen (24 nov, avond): IRENA Renewable Power Generation Costs in 2024 (t85, t86), IEA Cost of Capital Observatory (t82 opnieuw,
  t87), IEA Hydrogen Production en Infrastructure Projects Database (juni 2026) en Global Hydrogen Review 2025 (pdf); de laatste
  drie zijn nog niet verwerkt (dashboard 24).
- NGFS: alleen het referentiebestand (modellen, scenario's, regio's, variabelen) is binnen; de scenariodata zelf nog niet.

## Stand di 24 nov, laat (openbare bronnen zonder account)
Geen bestand gedownload: de cijfers zijn overgenomen van de bronpagina's en staan als kleine tabellen in `data/extern`.
| Voor | Bestand | Tabel | Bron en peildatum | Wat nog ontbreekt |
|---|---|---|---|---|
| 23 | `energiearmoede.csv` | t88 | CBS/TNO Monitor Energiearmoede 2025 (cbs.nl, 24 juli 2026): aandeel 2019-2025, tekort per huishouden | aantallen per jaar, uitsplitsing naar woningtype en gemeente (tabellenset CBS) |
| 35, 42 | `wachtrij_netbeheer.csv` | t89 | Netbeheer Nederland (1 juli 2025); Solar Magazine 24 okt 2026 (eind 2025, eerste helft 2026) | uitsplitsing per congestiegebied; het halfjaarrapport van Netbeheer Nederland zelf als bron voor 2026 |
| 36, 8 v2 | `terugleververgoeding_2027.csv` | t90 | keuze.nl (24 nov 2026, 13 leveranciers); energievergelijk.nl (31 okt 2025, 9 leveranciers) | contractvorm per rij; controle op de sites van de leveranciers zelf |
| 22 | `irena_jobs_2025.csv` | t91 | IRENA/ILO Annual Review 2025 (11 jan 2026): totaal, per technologie, per land | banen per land voor zon (alleen China bekend), aandeel vrouwen: staat in het rapport zelf |

- 2030-doel zon voor Duitsland, Bulgarije en Servië: **staat al in het Ember-bestand**, maar als vermogen (GW) en niet als opwek (TWh).
  `mck_kostencurve.py` leest alleen `generation_twh`. Omrekenen met de eigen opbrengst van 2025 (TWh per GW) geeft Duitsland
  181 TWh (215 GW), Bulgarije 7,9 TWh (6,75 GW) en Servië 0,3 TWh (0,37 GW). Nog niet doorgevoerd: het verandert t13 en de
  KPI's van dashboards 5, 26, 27 en 37 (potentieel 103 naar 140 Mt per jaar).
- NEDU/MFFBAS-profielen: nog niet opgehaald (bestand, moet via de browser).

## Stand di 24 nov, nacht: wat kan nu gebouwd worden
- **Correctie:** IRENA geeft wél een kostprijs per land voor zeven Europese landen (Frankrijk, Duitsland, Griekenland, Italië,
  Nederland, Polen, Spanje; figuur 3.3 en 3.10). Die staan in `data/extern/irena_solar_country_2024.csv` (t93, 2010-2024).
- **Dashboard 32:** klaar om te bouwen (t92). Twee methoden naast elkaar: eigen model (zelfde installatie, opbrengst en
  kapitaalkosten per land) en IRENA (per land waar bekend, anders Europees gemiddelde).
- **Dashboard 24 (waterstof):** de IEA-projectendatabase (2.942 productieprojecten, status, land, vermogen, jaar) volstaat.
- **NGFS:** wereldtotalen binnen (`data/extern/ngfs/`, niet op GitHub); per regio en de elektriciteitsprijs ontbreken nog.
- **39 en 43:** data aanwezig (t85; t11 en t93). **42:** alleen Nederland (t89). **40, 41, 44:** eerst een literatuurlijst;
  hiervoor bestaat geen kant-en-klaar bestand.

## Stand di 24 nov, 23:30: aangeleverd en verwerkt
- **Netbeheer Nederland, Stand van de Uitvoering halfjaar 2026:** `wachtrij_netbeheer.csv` (t89) komt nu uit het rapport zelf
  (p. 15-17): jaareinden 2022-2025 en 30 juni 2026, regionaal en TenneT, afname en invoeding (24 rijen). De cijfers uit het
  vakblad klopten. 2022 is van de grafiek afgelezen. Eind 2025 TenneT afname: 210 (rapport); de Kamerbrief zei 211.
- **MFFBAS/NEDU standaardprofielen 2026 (versie 1.00):** `nedu_profielen_2026_uur.csv`, uurwaarden voor E1A, E1B, E1C, E2A en
  E2B, elk met AZI (zonder invoeding) en AMI (met invoeding), afname (A) en invoeding (I). Voor dashboard 36: `E1A_AMI_A` en
  `E1A_AMI_I` zijn het huishouden met zonnepanelen. Het kwartierbestand zelf (13 MB) staat niet in de repo.
- Nog niet gelezen: het verslag bij de profielen, het jaarverslag profielallocatie 2024 en de infographics 2025.


## Stand do 26 nov: aangeleverd en verwerkt (t94 tot t99)
| Tabel | Voor | Bron | Inhoud |
|---|---|---|---|
| t94_subsidy_per_tonne | 40 | PBL eindadvies SDE++ 2026, hoofdstuk 3 | 23 technieken, subsidie-intensiteit in EUR per ton; nog naslaan in de pdf en de erratalijst |
| t95_grid_queue_europe | 42 | registers van netbeheerders, verzameld door kilovolt.io | 10 landen, GW in de wachtrij en verhouding tot de piekvraag; definities verschillen |
| t96_grid_costs | 41 | Eurostat nrg_pc_204_c en nrg_pc_205_c (bijgewerkt oktober 2026) | 715 rijen: energie, netkosten en belastingen per land en jaar, 2017-2025, huishoudens (2.500-4.999 kWh) en bedrijven (500-1.999 MWh) |
| t97_energy_poverty_region | 23 | CBS Monitor Energiearmoede 2019-2024, tabel 3 | 342 gemeenten, 12 provincies en Nederland, 2019-2024 (wijken en buurten niet overgenomen) |
| t98_storage_experience | 44 | Schmidt en Staffell, dataset 1 december 2022 | 18 reeksen (prijs en cumulatief vermogen) voor 8 opslagtechnieken plus zonnepanelen en omvormers, met de ervaringsgraad per reeks |
| t99_ngfs_regions | 12 | NGFS fase V, REMIND-MAgPIE 3.3-4.8 | 7 scenario's, 5 wereldregio's, stroomprijs en opwek 2020-2100; bron en tabel staan in .gitignore (licentie) |

- Het PNNL-werkboek (LCOS Workbook v2024) is een lege rekenmal: er staan geen kosten per techniek in. Voor dashboard 44
  ontbreken dus nog de invoerwaarden per techniek (PNNL Cost and Performance Database, pagina per techniek).
- NGFS: de regio's zijn vijf werelddelen ("OECD & EU"), geen Europa of Nederland apart, en het is één model.

### Controle 26 nov, 11:30
- t96: drie rijen met netkosten nul verwijderd (Albanie 2017, Oekraine 2020: geen opgave). Extra kolom
  `Network share of energy plus network pct`, omdat het aandeel in de totale prijs vertekent bij negatieve belastingen
  (Nederland 2022: 76%). EU-gemiddelde netkosten huishoudens 6,0 ct (2019) en 8,2 ct (2025): sluit aan op ACER (60 en 84 EUR/MWh).
- t97: gewogen gemiddelde van de 342 gemeenten is 6,0% (2024), gelijk aan het landelijke cijfer. Rozendaal 2023 is leeg (onderdrukt).
- t98: eerste versie voegde twee perioden van dezelfde techniek samen; hersteld, nu 18 reeksen zonder dubbele jaren.
- t99: twee van de zes aangeleverde bestanden waren gelijk; conversie GJ naar MWh (x 3,6) en EJ naar TWh (x 277,8) nagerekend.
- t94: tweede lezing van de pdf geeft dezelfde 23 waarden; zie de kanttekening over de errata in `docs/PLAN_WEEKEND.md`.
- Nieuw: t100 (grondstoffen, Pink Sheet van 3 november 2026), t101 (uurprofiel huishouden per maand, NEDU E1A 2026) en
  t102 (2.934 waterstofprojecten per land, status, techniek en jaar; IEA, juni 2026).
