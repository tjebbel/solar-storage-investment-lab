# Downloads die je zelf moet doen (bijgewerkt za 21 november 2026)

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
