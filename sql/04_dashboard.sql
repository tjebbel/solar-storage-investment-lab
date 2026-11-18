-- Query's voor het dashboard, met parameters in de vorm {{naam}}. Een leeg filter ('') betekent: alles.
-- Parameters: {{jaar}}, {{jaar_van}}, {{jaar_tot}}, {{regio}}, {{segment}}, {{zone}}, {{niveau}} ('regio', 'land' of 'zone').
-- Alle query's lezen de marts (hooguit een paar duizend rijen, met index op de filterkolommen).

-- STAP: kerncijfers | hangt af van: mart_zonejaar | soort: query
-- Vier tegels: mediaan-achtige kengetallen voor het gekozen jaar, met het jaar ervoor als vergelijking.
WITH keuze AS (
    SELECT * FROM mart_zonejaar
    WHERE jaar IN ({{jaar}}, {{jaar}} - 1)
      AND ({{regio}} = '' OR regio = {{regio}})
      AND ({{segment}} = '' OR segment = {{segment}})
      AND ({{zone}} = '' OR biedzone = {{zone}})
)
SELECT jaar                                      AS "Jaar",
       COUNT(*)                                  AS "Zones",
       ROUND(AVG(capture_zon), 3)                AS "Capture rate zon (gemiddeld)",
       CAST(ROUND(AVG(batterij_per_mw)) AS INTEGER) AS "Batterij-omzet (euro per MW)",
       CAST(ROUND(AVG(dagspreiding)) AS INTEGER) AS "Dagspreiding (euro per MWh)",
       CAST(ROUND(AVG(negatieve_uren)) AS INTEGER) AS "Negatieve uren (gemiddeld)",
       CASE WHEN jaar = {{jaar}} THEN 'gekozen jaar' ELSE 'jaar ervoor' END AS "Periode"
FROM keuze
GROUP BY jaar
ORDER BY jaar DESC;

-- STAP: rangorde | hangt af van: mart_zonejaar | soort: query
-- Doorklikken: {{niveau}} bepaalt of de staven regio's, landen of biedzones zijn. Zelfde query voor elk niveau.
SELECT CASE {{niveau}} WHEN 'regio' THEN regio WHEN 'land' THEN land ELSE biedzone END AS "Groep",
       COUNT(*)                                     AS "Zones",
       ROUND(AVG(capture_zon), 3)                   AS "Capture rate zon",
       CAST(ROUND(AVG(batterij_per_mw)) AS INTEGER) AS "Batterij-omzet (euro per MW)",
       CAST(ROUND(AVG(negatieve_uren)) AS INTEGER)  AS "Negatieve uren"
FROM mart_zonejaar
WHERE jaar = {{jaar}}
  AND ({{regio}} = '' OR regio = {{regio}})
  AND ({{segment}} = '' OR segment = {{segment}})
GROUP BY 1
ORDER BY 4 DESC NULLS LAST;

-- STAP: verloop | hangt af van: mart_zonemaand | soort: query
-- Maandreeks voor een zone, met dezelfde maand een jaar eerder ernaast (LAG over 12 maanden zou gaten missen:
-- daarom een koppeling op jaar - 1).
SELECT printf('%04d-%02d', m.jaar, m.maand)   AS "Maand",
       ROUND(m.gem_prijs, 1)                  AS "Prijs (euro per MWh)",
       ROUND(v.gem_prijs, 1)                  AS "Prijs een jaar eerder",
       ROUND(100.0 * (m.gem_prijs - v.gem_prijs) / NULLIF(v.gem_prijs, 0), 1) AS "Verandering (%)",
       ROUND(m.capture_zon, 2)                AS "Capture rate zon",
       m.negatieve_uren                       AS "Negatieve uren"
FROM mart_zonemaand m
LEFT JOIN mart_zonemaand v ON v.biedzone = m.biedzone AND v.jaar = m.jaar - 1 AND v.maand = m.maand
WHERE m.jaar BETWEEN {{jaar_van}} AND {{jaar_tot}}
  AND m.biedzone = CASE WHEN {{zone}} = '' THEN 'NL' ELSE {{zone}} END      -- leeg filter: Nederland als standaard
ORDER BY m.jaar, m.maand;

-- STAP: maand_uur | hangt af van: stg_nl_uur | soort: query
-- Matrix maand x uur voor de heatmap: prijs ten opzichte van het jaargemiddelde. Lange vorm (een rij per cel).
WITH jaar AS (SELECT AVG(prijs) AS gem FROM stg_nl_uur WHERE jaar = {{jaar}})
SELECT maand AS "Maand", uur AS "Uur (UTC)", ROUND(AVG(prijs) / (SELECT gem FROM jaar), 3) AS "Prijs (1 = jaargemiddelde)", COUNT(*) AS "Uren"
FROM stg_nl_uur
WHERE jaar = {{jaar}}
GROUP BY maand, uur
ORDER BY maand, uur;

-- STAP: segmenten | hangt af van: mart_zonejaar | soort: query
-- Verdeling over de segmenten in de gekozen periode, per jaar: laat de verschuiving zien.
SELECT jaar AS "Jaar", segment AS "Segment", COUNT(*) AS "Zones",
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY jaar), 1) AS "Aandeel (%)"
FROM mart_zonejaar
WHERE jaar BETWEEN {{jaar_van}} AND {{jaar_tot}}
  AND ({{regio}} = '' OR regio = {{regio}})
GROUP BY jaar, segment
ORDER BY jaar, 3 DESC;
