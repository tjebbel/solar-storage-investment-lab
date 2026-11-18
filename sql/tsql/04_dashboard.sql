-- Query's voor het dashboard (T-SQL-vertaling van sql/04_dashboard.sql).
-- Parameters via sqlcmd -v. Geen filter is het woord alle (sqlcmd accepteert geen lege waarde):
--   jaar, jaar_van, jaar_tot (getallen); regio, segment, zone (tekst); niveau ('regio', 'land' of 'zone').
-- Voorbeeld:
--   sqlcmd -d solar -v jaar=2025 jaar_van=2019 jaar_tot=2025 regio=alle segment=alle zone=alle niveau=land -i 04_dashboard.sql
-- Alle query's lezen de marts (mart_zonejaar en mart_zonemaand), met index op de filterkolommen.
-- Verschil met SQLite: AVG op een int geeft in T-SQL een int; daarom wordt eerst naar float omgezet.

-- STAP: kerncijfers | hangt af van: mart_zonejaar | soort: query
-- Vier tegels: kengetallen voor het gekozen jaar, met het jaar ervoor als vergelijking.
WITH keuze AS (
    SELECT * FROM dbo.mart_zonejaar
    WHERE jaar IN ($(jaar), $(jaar) - 1)
      AND ('$(regio)' = 'alle' OR regio = '$(regio)')
      AND ('$(segment)' = 'alle' OR segment = '$(segment)')
      AND ('$(zone)' = 'alle' OR biedzone = '$(zone)')
)
SELECT jaar AS [Jaar],
       COUNT(*) AS [Zones],
       ROUND(AVG(capture_zon), 3) AS [Capture rate zon (gemiddeld)],
       CAST(ROUND(AVG(batterij_per_mw), 0) AS int) AS [Batterij-omzet (euro per MW)],
       CAST(ROUND(AVG(dagspreiding), 0) AS int) AS [Dagspreiding (euro per MWh)],
       CAST(ROUND(AVG(CAST(negatieve_uren AS float)), 0) AS int) AS [Negatieve uren (gemiddeld)],
       CASE WHEN jaar = $(jaar) THEN 'gekozen jaar' ELSE 'jaar ervoor' END AS [Periode]
FROM keuze
GROUP BY jaar
ORDER BY jaar DESC;
GO

-- STAP: rangorde | hangt af van: mart_zonejaar | soort: query
-- Doorklikken: niveau bepaalt of de staven regio's, landen of biedzones zijn. Zelfde query voor elk niveau.
SELECT CASE '$(niveau)' WHEN 'regio' THEN regio WHEN 'land' THEN land ELSE biedzone END AS [Groep],
       COUNT(*) AS [Zones],
       ROUND(AVG(capture_zon), 3) AS [Capture rate zon],
       CAST(ROUND(AVG(batterij_per_mw), 0) AS int) AS [Batterij-omzet (euro per MW)],
       CAST(ROUND(AVG(CAST(negatieve_uren AS float)), 0) AS int) AS [Negatieve uren]
FROM dbo.mart_zonejaar
WHERE jaar = $(jaar)
  AND ('$(regio)' = 'alle' OR regio = '$(regio)')
  AND ('$(segment)' = 'alle' OR segment = '$(segment)')
GROUP BY CASE '$(niveau)' WHEN 'regio' THEN regio WHEN 'land' THEN land ELSE biedzone END
ORDER BY AVG(batterij_per_mw) DESC;
GO

-- STAP: verloop | hangt af van: mart_zonemaand | soort: query
-- Maandreeks voor een zone, met dezelfde maand een jaar eerder ernaast (koppeling op jaar - 1).
SELECT FORMAT(m.jaar, '0000') + '-' + FORMAT(m.maand, '00') AS [Maand],
       ROUND(m.gem_prijs, 1)                  AS [Prijs (euro per MWh)],
       ROUND(v.gem_prijs, 1)                  AS [Prijs een jaar eerder],
       ROUND(100.0 * (m.gem_prijs - v.gem_prijs) / NULLIF(v.gem_prijs, 0), 1) AS [Verandering (%)],
       ROUND(m.capture_zon, 2)                AS [Capture rate zon],
       m.negatieve_uren                       AS [Negatieve uren]
FROM dbo.mart_zonemaand m
LEFT JOIN dbo.mart_zonemaand v
       ON v.biedzone = m.biedzone AND v.jaar = m.jaar - 1 AND v.maand = m.maand
WHERE m.jaar BETWEEN $(jaar_van) AND $(jaar_tot)
  AND m.biedzone = CASE WHEN '$(zone)' = 'alle' THEN 'NL' ELSE '$(zone)' END    -- leeg filter: Nederland als standaard
ORDER BY m.jaar, m.maand;
GO

-- STAP: maand_uur | hangt af van: stg_nl_uur | soort: query
-- Matrix maand x uur voor de heatmap: prijs ten opzichte van het jaargemiddelde. Lange vorm (een rij per cel).
WITH jaargem AS (SELECT AVG(prijs) AS gem FROM dbo.stg_nl_uur WHERE jaar = $(jaar))
SELECT maand AS [Maand],
       uur AS [Uur (UTC)],
       ROUND(AVG(prijs) / (SELECT gem FROM jaargem), 3) AS [Prijs (1 = jaargemiddelde)],
       COUNT(*) AS [Uren]
FROM dbo.stg_nl_uur
WHERE jaar = $(jaar)
GROUP BY maand, uur
ORDER BY maand, uur;
GO

-- STAP: segmenten | hangt af van: mart_zonejaar | soort: query
-- Verdeling over de segmenten per jaar: laat de verschuiving zien.
SELECT jaar AS [Jaar], segment AS [Segment], COUNT(*) AS [Zones],
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY jaar), 1) AS [Aandeel (%)]
FROM dbo.mart_zonejaar
WHERE jaar BETWEEN $(jaar_van) AND $(jaar_tot)
  AND ('$(regio)' = 'alle' OR regio = '$(regio)')
GROUP BY jaar, segment
ORDER BY jaar, 3 DESC;
GO
