-- Een trage query en haar snelle versie. Vraag: prijs, dagspreiding en negatieve uren per dag voor een maand.
-- Parameter: {{maand}} als 'JJJJ-MM'. De gemeten tijden staan in reports/analyse/05_sql.md.

-- STAP: traag | hangt af van: raw_nl_uur | soort: query
-- Waarom traag:
--  1. drie deelquery's per rij: voor elk van de 744 uren wordt de hele uurtabel drie keer gelezen;
--  2. substr() en strftime() op de kolom: een index op timestamp_utc kan niet gebruikt worden;
--  3. DISTINCT ruimt achteraf op: elke dag wordt 24 keer uitgerekend en 23 keer weggegooid.
SELECT DISTINCT
    substr(u.timestamp_utc, 1, 10) AS dag,
    (SELECT AVG(x.prijs_eur_mwh) FROM raw_nl_uur x WHERE substr(x.timestamp_utc, 1, 10) = substr(u.timestamp_utc, 1, 10)) AS gem_prijs,
    (SELECT MAX(x.prijs_eur_mwh) - MIN(x.prijs_eur_mwh) FROM raw_nl_uur x WHERE substr(x.timestamp_utc, 1, 10) = substr(u.timestamp_utc, 1, 10)) AS dagspreiding,
    (SELECT COUNT(*) FROM raw_nl_uur x WHERE substr(x.timestamp_utc, 1, 10) = substr(u.timestamp_utc, 1, 10) AND x.prijs_eur_mwh < 0) AS negatieve_uren
FROM raw_nl_uur u
WHERE strftime('%Y-%m', u.timestamp_utc) = {{maand}}
ORDER BY dag;

-- STAP: snel | hangt af van: stg_nl_uur | soort: query
-- Herschreven:
--  1. een keer groeperen in plaats van drie deelquery's per rij;
--  2. de dag is in de staging een eigen kolom met een index (ix_stg_nl_uur_dag), en het filter is een bereik
--     op die kolom, zodat alleen de rijen van de maand gelezen worden;
--  3. geen DISTINCT nodig.
-- Indexen (staan in 03_pijplijn.sql):
--     CREATE INDEX ix_stg_nl_uur_dag ON stg_nl_uur (dag);
--     CREATE INDEX ix_stg_nl_uur_jaar_maand ON stg_nl_uur (jaar, maand, uur);
SELECT dag,
       AVG(prijs)              AS gem_prijs,
       MAX(prijs) - MIN(prijs) AS dagspreiding,
       SUM(prijs < 0)          AS negatieve_uren
FROM stg_nl_uur
WHERE dag >= {{maand}} || '-01' AND dag < date({{maand}} || '-01', '+1 month')
GROUP BY dag
ORDER BY dag;

-- STAP: voorberekend | hangt af van: mart_nl_dag | soort: query
-- Alternatief: de dagcijfers staan al in mart_nl_dag (een rij per dag, ververst door de pijplijn). Het dashboard
-- leest dan 30 rijen in plaats van 720. In SQL Server of Fabric is dit een geindexeerde view of een goudtabel.
SELECT dag, gem_prijs, dagspreiding, negatieve_uren
FROM mart_nl_dag
WHERE dag >= {{maand}} || '-01' AND dag < date({{maand}} || '-01', '+1 month')
ORDER BY dag;
