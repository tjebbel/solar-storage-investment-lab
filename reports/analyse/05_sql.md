# SQL

> Stand van dit verslag: 17 november 2026, middag. Daarna zijn data gerepareerd en analyses toegevoegd; wat daardoor verschoof staat in `07_vervolg.md` (hoofdstuk 9).

Stand: 17 november 2026. Bestanden in `sql/`, loper in `src/eti/sql_run.py`, tests in `tests/test_sql.py`.

```
PYTHONPATH=src python3 -m eti.sql_run                              # alles; verslag in reports/analyse/sql_uitvoer.txt
PYTHONPATH=src python3 -m eti.sql_run maand=2026-10 jaar=2024 regio=Iberie niveau=land
```

**Gekozen lezing.** De sjablonen vroegen om tabellen, kolommen en een "systeem A en B". Ingevuld met de eigen data:
de csv's uit `powerbi/data` worden als `raw_`-tabellen in een SQLite-database gezet (`data/analyse.db`, staat in
`.gitignore`). Dialect: SQLite, omdat het zonder installatie draait en dus getest kon worden. Onderaan staat wat
anders is in Fabric en SQL Server. Alle query's zijn uitgevoerd; de tijden hieronder zijn gemeten.

| Bestand | Opdracht | Stappen |
|---|---|---|
| `01_analyse.sql` | een query voor de analyse | 1 |
| `02_optimalisatie.sql` | een trage query sneller maken | traag, snel, voorberekend |
| `03_pijplijn.sql` | van ruw naar analyseklaar, met controles | 11 |
| `04_dashboard.sql` | query's met parameters voor het dashboard | 5 |
| `05_reconciliatie.sql` | aansluiting tussen twee bronnen | 7 |

Elke stap begint met `-- STAP: naam | hangt af van: ... | soort: tabel of query`. De loper leest die regels, zet de
stappen in de goede volgorde en meet de tijd.

## 1. Analysequery

Vraag: in welke biedzones is opslag in het laatste hele jaar het aantrekkelijkst, en hoe staat zon er daar voor?

- *Lege waarden:* een capture rate buiten 0 tot 2 wordt leeg; een lege IRR wordt de tekst "verdient zich niet terug"
  (en "geen cijfer" als ook de omzet ontbreekt); delen door nul is afgevangen met `NULLIF`; zones zonder regio
  krijgen "Onbekend".
- *Leesbaarheid:* zes CTE's (laatste hele jaar, zon, batterij, nu, vorig, ijkjaar 2019).
- *Niet-vanzelfsprekende logica toegelicht:* waarom 8.700 uren een heel jaar is, waarom de volgorde van de
  segmentregels telt.
- *Uitvoer:* kolomnamen in gewone taal ("Batterij-omzet (euro per MW)", "Verandering sinds 2019").

Uitkomst (37 rijen, 2 ms). Bovenaan: Hongarije €80.919 per MW (−11% tegenover 2024, IRR 5,5%), Bulgarije €80.876,
Griekenland €80.372, Roemenië €80.346; alle vier segment Batterijmarkt.

## 2. Optimalisatie

Vraag: prijs, dagspreiding en negatieve uren per dag voor één maand.

**Waarom de eerste versie traag is.**
1. Drie deelquery's per rij: voor elk van de 720 uren van de maand wordt de hele uurtabel (69.010 rijen) drie keer
   gelezen. Dat zijn ongeveer 150 miljoen rijvergelijkingen.
2. `substr()` en `strftime()` op de kolom: een index op het tijdstip kan niet gebruikt worden.
3. `DISTINCT` ruimt achteraf op: elke dag wordt 24 keer uitgerekend.

**Herschreven.** Eén keer groeperen op een dagkolom die in de staging al bestaat, met een bereikfilter op die kolom.

```sql
CREATE INDEX ix_stg_nl_uur_dag ON stg_nl_uur (dag);
CREATE INDEX ix_stg_nl_uur_jaar_maand ON stg_nl_uur (jaar, maand, uur);
```

| Versie | Tijd | Gelezen rijen |
|---|---|---|
| Traag (deelquery's op de ruwe tabel) | 11.900 ms | ongeveer 150 miljoen |
| Herschreven (groeperen met index op dag) | 0,5 ms | 720 |
| Voorberekend (`mart_nl_dag`) | 0,2 ms | 30 |

De herschreven query is ruim twintigduizend keer sneller en geeft dezelfde 30 rijen. **Alternatief:** de dagcijfers
vooraf berekenen in `mart_nl_dag` (in SQLite een tabel die de pijplijn ververst; in SQL Server een geïndexeerde
view, in Fabric een goudtabel of materialized lake view). Dat loont zodra meer dan één rapport dezelfde dagcijfers
vraagt.

## 3. Pijplijn

```
raw_nl_uur ──► stg_nl_uur ──► mart_nl_dag ──► mart_nl_maand
     └──────► afgekeurd_nl_uur
raw_land_jaar ──► stg_land_jaar ─┐
raw_flex_land ──► stg_batterij ──┼──► mart_zonejaar ──► kwaliteit
raw_ember_opwek_jaar ► stg_mix ──┤
raw_dim_zone ────────────────────┘
raw_land_maand + raw_dim_zone ──► mart_zonemaand
```

Staging kan naast elkaar draaien; elke mart wacht op haar staging; `kwaliteit` draait als laatste. Elke stap gooit
haar tabel weg en bouwt haar opnieuw, dus opnieuw draaien is veilig.

| Soort | Stap | Wat ze doet | Rijen | Tijd |
|---|---|---|---|---|
| Staging | `stg_nl_uur` | tijdstip en getallen typeren, dag, jaar, maand en uur afleiden, dubbele tijdstippen eruit | 69.010 | 189 ms |
| Staging | `afgekeurd_nl_uur` | wat de staging niet haalde, met reden | 0 | 96 ms |
| Staging | `stg_land_jaar` | namen opschonen, typeren, capture rate buiten 0 tot 2 leeg maken en tellen, dubbel op zone en jaar eruit | 296 | 3 ms |
| Staging | `stg_batterij` | batterij van 2 uur, een rij per land en jaar | 296 | 3 ms |
| Staging | `stg_mix` | Ember van lang naar breed (kolom per bron) | 5.916 | 59 ms |
| Transformatie | `mart_zonejaar` | koppelt zon, batterij, opwekmix en regio; kent het segment toe | 296 | 4 ms |
| Transformatie | `mart_nl_dag`, `mart_nl_maand` | dag- en maandcijfers, capture rate gewogen naar opwek | 2.876 en 95 | 34 ms |
| Transformatie | `mart_zonemaand` | maandcijfers per zone met regio | 3.515 | 7 ms |
| Controle | `kwaliteit` | elf controles, elk met status ok, waarschuwing of fout | 11 | 9 ms |

**Foutafhandeling.**
- *Lege sleutels:* rijen zonder biedzone of jaar komen de staging niet in; de controle telt ze in de mart.
- *Dubbele rijen:* `ROW_NUMBER()` per sleutel; de rij met de meeste uren (of met een prijs) wint. Een unieke index
  op elke mart laat de stap falen als er toch een dubbele doorheen komt.
- *Verkeerd type:* `typeof()` vangt tekst in een getalkolom; `datetime()` geeft leeg bij een ongeldig tijdstip. Die
  rijen gaan met een reden naar `afgekeurd_nl_uur` in plaats van stil te verdwijnen.
- *Buiten bereik:* een capture rate boven 2 wordt leeg en geteld.

**Uitkomst van de controles:** tien keer ok, één waarschuwing (capture rate van zon afgekeurd voor SE3 2021 en SE4
2021). Aantallen sluiten: 69.010 goedgekeurd plus 0 afgekeurd is 69.010 ruw. Laatste dag in de data: 15 november.

## 4. Dashboardquery's

Parameters in de vorm `{{naam}}`: `jaar`, `jaar_van`, `jaar_tot`, `regio`, `segment`, `zone`, `niveau`. De loper
bindt ze als waarden; ze worden nooit in de tekst van de query geplakt (een test probeert een injectie en die
mislukt).

| Query | Wat ze levert | Vorm | Tijd |
|---|---|---|---|
| `kerncijfers` | vier kengetallen voor het gekozen jaar en het jaar ervoor | 2 rijen | 0,5 ms |
| `rangorde` | staven per regio, land of zone; `niveau` kiest de laag, dezelfde query voor elk niveau | een rij per groep | 0,4 ms |
| `verloop` | maandreeks voor een zone met dezelfde maand een jaar eerder en het verschil | een rij per maand | 0,5 ms |
| `maand_uur` | matrix maand × uur ten opzichte van het jaargemiddelde, lange vorm | 288 rijen | 4 ms |
| `segmenten` | aantal zones per segment per jaar, met aandeel | een rij per jaar en segment | 0,5 ms |

**Randgevallen.** Een leeg filter betekent alles: `({{regio}} = '' OR regio = {{regio}})`. Een lege zone in
`verloop` valt terug op Nederland. Delen door nul is afgevangen. De vergelijking met een jaar eerder gebruikt een
koppeling op jaar − 1 in plaats van `LAG(…, 12)`, zodat een ontbrekende maand de reeks niet verschuift. Alle query's
lezen de marts en blijven ver onder een seconde.

## 5. Aansluiting tussen twee bronnen

Gegeven: het aandeel van zon in de opwek per land en jaar. Systeem A: de gemeten opwek per biedzone
(Energy-Charts), gemiddeld per land. Systeem B: Ember. Tolerantie: 2 procentpunt.

| | Aantal |
|---|---|
| Rijen in A | 208 |
| Rijen in B (Europa, vanaf 2019) | 288 |
| In beide | 182 |
| Sluit aan (binnen 2 punten) | 144 |
| Wijkt af | 38 (20,9%) |
| Alleen in A | 26 |
| Alleen in B | 106 |

| Soort verschil | Aantal | Waarschijnlijke oorzaak | Oplossing |
|---|---|---|---|
| Tijdsverschil | 26 | Ember publiceert een jaar na afloop; A loopt tot vandaag (alle 26 zijn 2026) | het lopende jaar niet vergelijken |
| Alleen in B | 106 | zestien landen zonder biedzone in de eigen tabel (VK, Ierland, Luxemburg en andere) | buiten de vergelijking laten of de zone toevoegen |
| A veel lager | 16 | de gemeten opwek mist zon achter de meter | Ember voor het niveau, A alleen voor het uurprofiel |
| Overig waardeverschil | 22 | gemiddelde over meerdere zones per land, of een herziening | per geval nalopen; wegen naar opwek |

Grootste afwijking: Nederland 2025, 0,6% in A tegen 21,1% in B. Op totaalniveau zit A elk jaar 6% tot 12% onder B
(2025: gemiddeld 11,7% tegen 12,5% over 26 landen).

## Wat anders is in Fabric en SQL Server (T-SQL)

| SQLite | T-SQL |
|---|---|
| `CREATE TABLE x AS SELECT …` | `SELECT … INTO x` of `CREATE TABLE x AS SELECT` (Fabric Warehouse) |
| `strftime('%Y', t)`, `date(t)` | `YEAR(t)`, `CAST(t AS date)` |
| `substr()`, `\|\|`, `printf()` | `SUBSTRING()`, `CONCAT()` of `+`, `FORMAT()` |
| `SUM(prijs < 0)` | `SUM(CASE WHEN prijs < 0 THEN 1 ELSE 0 END)` |
| `GROUP_CONCAT(x, ', ')` | `STRING_AGG(x, ', ')` |
| `typeof(x)` en `datetime(x)` als typecontrole | `TRY_CAST(x AS float)`, `TRY_CONVERT(datetime2, x)` |
| `ORDER BY … NULLS LAST` | `ORDER BY CASE WHEN x IS NULL THEN 1 ELSE 0 END, x` |
| `{{naam}}` gebonden door de loper | `@naam` in een opgeslagen procedure of een parameter in Power BI |
| tabel die de pijplijn ververst | geïndexeerde view (SQL Server) of materialized lake view (Fabric) |

De T-SQL-varianten zijn niet uitgevoerd.
