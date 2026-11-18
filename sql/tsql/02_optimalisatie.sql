SET STATISTICS TIME ON;
GO
-- Een trage query en haar snelle versie. Vraag: prijs, dagspreiding en negatieve uren per dag voor een maand.
-- T-SQL-vertaling van sql/02_optimalisatie.sql. Parameter: sqlcmd -v maand="2025-11" (formaat JJJJ-MM).
-- Uitvoeren:  sqlcmd -d solar -v maand="2025-11" -i 02_optimalisatie.sql
-- Let op: de gemeten tijden voor SQLite staan in reports/analyse/05_sql.md; de T-SQL-tijden meet je zelf met SET STATISTICS TIME ON.

-- STAP: traag | hangt af van: raw_nl_uur | soort: query
-- Waarom traag:
--  1. drie deelquery's per rij: voor elk van de 744 uren wordt de hele uurtabel drie keer gelezen;
--  2. LEFT() en tekstfilters op de kolom: een index op timestamp_utc kan niet gebruikt worden;
--  3. DISTINCT ruimt achteraf op: elke dag wordt 24 keer uitgerekend en 23 keer weggegooid.
-- Let op (gevonden 18 november 2026): SQL Server rekent de deelquery's parallel uit. Het gemiddelde van dezelfde dag kan
-- dan in de laatste decimaal verschillen, en DISTINCT ziet die rijen als verschillend (85 rijen in plaats van 30).
-- Daarom afronden op 6 decimalen voor het DISTINCT. SQLite rekent in een vaste volgorde en heeft dit niet.
SELECT DISTINCT
    LEFT(u.timestamp_utc, 10) AS dag,
    ROUND((SELECT AVG(TRY_CAST(x.prijs_eur_mwh AS float)) FROM dbo.raw_nl_uur x
     WHERE LEFT(x.timestamp_utc, 10) = LEFT(u.timestamp_utc, 10)), 6) AS gem_prijs,
    ROUND((SELECT MAX(TRY_CAST(x.prijs_eur_mwh AS float)) - MIN(TRY_CAST(x.prijs_eur_mwh AS float)) FROM dbo.raw_nl_uur x
     WHERE LEFT(x.timestamp_utc, 10) = LEFT(u.timestamp_utc, 10)), 6) AS dagspreiding,
    (SELECT COUNT(*) FROM dbo.raw_nl_uur x
     WHERE LEFT(x.timestamp_utc, 10) = LEFT(u.timestamp_utc, 10) AND TRY_CAST(x.prijs_eur_mwh AS float) < 0) AS negatieve_uren
FROM dbo.raw_nl_uur u
WHERE LEFT(u.timestamp_utc, 7) = '$(maand)'
ORDER BY dag;
GO

-- STAP: snel | hangt af van: stg_nl_uur | soort: query
-- Herschreven:
--  1. een keer groeperen in plaats van drie deelquery's per rij;
--  2. de dag is in de staging een echte datumkolom met een index (ix_stg_nl_uur_dag), en het filter is een bereik
--     op die kolom, zodat alleen de rijen van de maand gelezen worden;
--  3. geen DISTINCT nodig.
-- Indexen (staan in 03_pijplijn.sql):
--     CREATE INDEX ix_stg_nl_uur_dag ON dbo.stg_nl_uur (dag);
--     CREATE INDEX ix_stg_nl_uur_jaar_maand ON dbo.stg_nl_uur (jaar, maand, uur);
SELECT dag,
       AVG(prijs)              AS gem_prijs,
       MAX(prijs) - MIN(prijs) AS dagspreiding,
       SUM(CASE WHEN prijs < 0 THEN 1 ELSE 0 END) AS negatieve_uren
FROM dbo.stg_nl_uur
WHERE dag >= CAST('$(maand)-01' AS date)
  AND dag <  DATEADD(month, 1, CAST('$(maand)-01' AS date))
GROUP BY dag
ORDER BY dag;
GO

-- STAP: voorberekend | hangt af van: mart_nl_dag | soort: query
-- Alternatief: de dagcijfers staan al in mart_nl_dag (een rij per dag, ververst door de pijplijn). Het dashboard
-- leest dan 30 rijen in plaats van 720. In SQL Server of Fabric is dit een geindexeerde view of een goudtabel.
SELECT dag, gem_prijs, dagspreiding, negatieve_uren
FROM dbo.mart_nl_dag
WHERE dag >= CAST('$(maand)-01' AS date)
  AND dag <  DATEADD(month, 1, CAST('$(maand)-01' AS date))
ORDER BY dag;
GO

GO
SET STATISTICS TIME OFF;
GO
