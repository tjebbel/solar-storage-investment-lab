# Voortgang analysepakketten (18 november 2026)

Volgorde zoals gevraagd. Elk pakket levert code in `src/eti`, tabellen in `powerbi/data` en een verslag in `reports/analyse`.

| # | Pakket | Status | Code | Verslag |
|---|---|---|---|---|
| 1 | Data-analyse (_DA) | klaar | `src/eti/da.py`, `tests/test_da.py` | `01_data_analyse_DA.md` |
| 2 | Statistische analyse (_SA) | klaar | `src/eti/sa.py`, `src/eti/prognose.py`, `tests/test_sa.py` | `02_statistische_analyse_SA.md` |
| 3 | Visualisatie | klaar | `src/eti/vis.py`, `rapport_grafieken.py`, `verken_app.py`, `tests/test_verken.py`, `powerbi/thema_analyse.json` | `03_visualisatie.md` |
| 4 | Rapportage | klaar | `src/eti/woordenboek.py`, `tests/test_woordenboek.py`, `sjablonen/kpi_rapport_sjabloon.md` | `04_rapportage.md`, `datawoordenboek.md`, `datawoordenboek.schema.json` |
| 5 | SQL | klaar | `sql/*.sql`, `src/eti/sql_run.py`, `tests/test_sql.py` | `05_sql.md` |
| 6 | Python en R | klaar | `src/eti/analyse_script.py`, `rapport_auto.py`, `ml_pijplijn.py`, `kwaliteit.py`, `maak_notebook.py`, `notebooks/`, `r/` | `06_python.md` |
| 7 | Alles analyseren, vervolgstappen | klaar | | `00_overzicht.md` |
| 8 | Testen wat niet getest was | klaar: op je Mac 191 tests zonder overslaan; R gedraaid in de browser (webR) en de verkenner in een echte browser nagekeken; DAX en T-SQL vragen software of je account | `tests/test_mail_cron.py`, `test_verken_streamlit.py`, `test_op_mac.sh`, `.vscode/tasks.json`, `resultaten/r_hypothesetoets_webr.txt` | `07_vervolg.md` (2, 3, 3a) |
| 9 | Data repareren | klaar; de tien capture rates zijn op je Mac aangevuld | `herstel.py`, `nacht2.py`, `wereld.py`, `interconnectie.py`, `zonprofiel.py` | `07_vervolg.md` (4) |
| 10 | Verzadigingscurve per GW | klaar | `vs_dag.py`, `verzadiging_gw.py`, `tests/test_verzadiging.py` | `07_vervolg.md` (5) |
| 11 | Gasprijs en termijnprijs | klaar | `gas.py`, `data/extern/gasprijs_fred.csv`, `tests/test_gas.py` | `07_vervolg.md` (6) |
| 12 | Balanceringsinkomsten | klaar zonder aFRR-capaciteit | `stapel.py`, `tests/test_stapel_powerbi.py` | `07_vervolg.md` (7) |
| 13 | DAX toetsbaar maken | klaar; uitvoeren in Power BI is aan jou | `powerbi_toets.py`, `powerbi/maten_analyse.dax`, `powerbi/maten_verwacht.csv`, `dim_datum.csv` | `07_vervolg.md` (3) |
| 14 | Documentronde | klaar: memo 31 pagina's, naslagwerk 283, recruitermemo 1 | LaTeX-bron in `reports/` | hoofdstukken 17 en 18 van de memo |
| 15 | T-SQL in SQL Server (Docker op de Mac) | klaar: 00-05 gelijk aan SQLite | `sql/tsql/*`, `run_tsql.sh` | naslagwerk hoofdstuk 20 |
| 16 | Verbeterpunten data en methode | klaar: aansluiting met relatieve tolerantie, dekkingsgaten en vaste definities | `sql/05_reconciliatie.sql`, `sql_run.py` | `08_vervolg_18nov.md` (3) |
| 17 | Zon achter de meter | klaar: verschil komt door dekkingsgaten; definities per land, buiten de steekproef bevestigd | `bronnen_toets.py` | `08` (4.1) |
| 18 | Segmentgevoeligheid | klaar: kolom grensgeval | `segment_gevoeligheid.py` | `08` (4.2) |
| 19 | Batterij: bronnen, bouwkosten, cycli | klaar; aFRR alleen ijkpunten | `batterij_bronnen.py`, `batterij_irr.py` | `08` (4.3, 4.4) |
| 20 | Schokjaar 2026 | klaar: gas 76% | `schokjaar.py` | `08` (4.5) |
| 21 | Benchmark en DAX | klaar om te draaien op de Mac en in Fabric | `sql_benchmark.py`, `benchmark_tsql.sh`, `powerbi_toets vergelijk` | `08` (4.6, 4.7) |
| 22 | Tableau-dashboard 1 en GitHub | gepubliceerd op Tableau Public; repo opgeruimd (870 -> 386 bestanden) | `tableau/NL_solar.twbx`, README | `09_ronde_19nov.md` (1) |
| 23 | Kernenergie Europa en wereld (dashboard 3) | klaar | `kern_wereld.py` (t6-t8) | `09` (2) |
| 24 | Signalering alle zones, dekking NL (dashboard 2) | klaar; Python 66 van 66 | `signalering_europa.py` (t9-t10) | `09` (3) |
| 25 | Ervaringscurve en portefeuille (dashboard 4) | klaar | `bcg_portefeuille.py` (t11-t12) | `09` (4) |
| 26 | Kostencurve CO2 (dashboard 5) | klaar; LCOE noord/zuid als stand-in | `mck_kostencurve.py` (t13) | `09` (4) |
| 27 | Controlematrix en risicokaart (dashboard 7) | klaar; 3 controles open | `assurance_overzicht.py` (t15-t16) | `09` (4) |
| 28 | Overheden EU, VS, China (dashboards 9-11) | klaar; NL (t17), EU-doelpad (t19), provincies (t23) open | `overheden.py` (t18, t20-t22) | `09` (4) |
| 29 | Netbeheerder en EV (dashboard 13) | klaar; grensstromen nog te controleren | `net_flex.py` (t25-t26) | `09` (4) |
| 30 | Impact en Mondiale Zuiden (dashboards 14-15) | klaar; WACC Afrika open | `impact_zuiden.py` (t27-t28) | `09` (4) |

Ronde 8 tot en met 14: 17 en 18 november 2026. Tests: 191, op je Mac en in de werkomgeving met dezelfde uitkomsten. Het R-script geeft dezelfde schattingen als Python; het online dashboard heeft de nieuwe tabellen met Texas.

Nog open: DAX en T-SQL uitvoeren (Power BI of Fabric met je account), de aFRR-capaciteitsprijs, mail en cron op de Mac zelf.

Ronde 15 tot en met 21: 18 november 2026. Tests: 203. Nog open: DAX uitvoeren in Fabric of op Windows, de snelheidsmeting op de Mac, een aFRR-reeks.

Ronde 22 tot en met 30: 18 en 19 november 2026. Tests: 213 (28 overgeslagen in de Mac-VM zonder Streamlit). Open: Tableau-toets dashboard 2, DAX in Fabric, saldering (t17), NGFS (t24), netcongestie, grensstromen, aFRR-reeks.
