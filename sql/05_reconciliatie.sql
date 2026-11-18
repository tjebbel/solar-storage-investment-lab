-- Aansluiting tussen twee bronnen voor hetzelfde gegeven: het aandeel van zon in de opwek per land en jaar.
--   Systeem A: gemeten opwek per biedzone (Energy-Charts, kolom aandeel_zon_energycharts), hier gemiddeld per land.
--   Systeem B: Ember, per land (jaarstatistiek, met een schatting van zon achter de meter).
-- Parameters: {{tolerantie_pp}} = toegestaan verschil in procentpunten; {{tolerantie_rel}} = toegestaan verschil als
-- fractie van B. Een verschil telt als 'sluit aan' als het binnen de ruimste van de twee valt. Alleen een vaste
-- tolerantie is te streng voor landen met weinig zon en te ruim voor landen met veel zon.
--
-- Herzien 18 november 2026. De indeling van verschillen is nu toetsbaar in plaats van een gok:
--   * dekkingsgat in A: A telt minder dan een kwart van B. De bron van A meet dan (bijna) geen zon in dat land
--     (Nederland, Noorwegen, Servie, en de eerste jaren van Finland, Zweden, Letland, Polen, Estland, Hongarije).
--     Dit is geen methodeverschil maar ontbrekende data, en het hoort niet in het gemiddelde verschil.
--   * structureel lager of hoger in A: in minstens 80% van de bruikbare jaren ligt A aan dezelfde kant van B.
--     Dan verschilt de definitie tussen de bronnen (bijvoorbeeld zon achter de meter wel of niet geschat).
--   * wisselend: geen vaste kant; herzieningen of het ongewogen gemiddelde over zones.

-- STAP: rec_bronnen | hangt af van: stg_land_jaar, stg_mix, raw_dim_land | soort: tabel
DROP TABLE IF EXISTS rec_a;
CREATE TABLE rec_a AS
SELECT iso3, jaar, ROUND(100.0 * AVG(aandeel_zon_energycharts), 3) AS zon_pct, COUNT(*) AS zones
FROM stg_land_jaar
WHERE iso3 IS NOT NULL AND aandeel_zon_energycharts IS NOT NULL
GROUP BY iso3, jaar;
DROP TABLE IF EXISTS rec_b;
CREATE TABLE rec_b AS
SELECT m.iso3, m.jaar, ROUND(m.aandeel_zon_pct, 3) AS zon_pct
FROM stg_mix m
JOIN raw_dim_land d ON d.iso3 = m.iso3
WHERE d.continent = 'Europe' AND m.jaar >= (SELECT MIN(jaar) FROM rec_a) AND m.aandeel_zon_pct IS NOT NULL;
CREATE UNIQUE INDEX ux_rec_a ON rec_a (iso3, jaar);
CREATE UNIQUE INDEX ux_rec_b ON rec_b (iso3, jaar);

-- STAP: rec_vergelijk | hangt af van: rec_bronnen | soort: tabel
-- Een rij per land en jaar in beide bronnen, met de verhouding A/B en de indeling.
DROP TABLE IF EXISTS rec_land;
CREATE TABLE rec_land AS
SELECT a.iso3,
       SUM(CASE WHEN a.zon_pct >= 0.25 * b.zon_pct THEN 1 ELSE 0 END)                               AS bruikbare_jaren,
       SUM(CASE WHEN a.zon_pct >= 0.25 * b.zon_pct AND a.zon_pct < b.zon_pct THEN 1 ELSE 0 END)     AS jaren_lager,
       SUM(CASE WHEN a.zon_pct >= 0.25 * b.zon_pct AND a.zon_pct > b.zon_pct THEN 1 ELSE 0 END)     AS jaren_hoger
FROM rec_a a JOIN rec_b b ON b.iso3 = a.iso3 AND b.jaar = a.jaar
GROUP BY a.iso3;
DROP TABLE IF EXISTS rec_vergelijk;
CREATE TABLE rec_vergelijk AS
SELECT a.iso3, a.jaar, a.zon_pct AS a_pct, b.zon_pct AS b_pct, a.zones,
       ROUND(a.zon_pct / NULLIF(b.zon_pct, 0), 3) AS verhouding,
       CASE WHEN a.zon_pct < 0.25 * b.zon_pct THEN 'dekkingsgat in A'
            WHEN ABS(a.zon_pct - b.zon_pct) <= MAX({{tolerantie_pp}}, {{tolerantie_rel}} * b.zon_pct) THEN 'sluit aan'
            WHEN l.bruikbare_jaren >= 3 AND l.jaren_lager >= 0.8 * l.bruikbare_jaren THEN 'structureel lager in A'
            WHEN l.bruikbare_jaren >= 3 AND l.jaren_hoger >= 0.8 * l.bruikbare_jaren THEN 'structureel hoger in A'
            ELSE 'wisselend' END AS categorie
FROM rec_a a
JOIN rec_b b ON b.iso3 = a.iso3 AND b.jaar = a.jaar
JOIN rec_land l ON l.iso3 = a.iso3;
CREATE UNIQUE INDEX ux_rec_vergelijk ON rec_vergelijk (iso3, jaar);

-- STAP: a_niet_in_b | hangt af van: rec_bronnen | soort: query
SELECT a.iso3 AS "Land", a.jaar AS "Jaar", a.zon_pct AS "Zon in A (%)",
       CASE WHEN a.jaar > (SELECT MAX(jaar) FROM rec_b) THEN 'tijdsverschil: B publiceert het jaar later'
            ELSE 'land of jaar ontbreekt in B' END AS "Soort verschil"
FROM rec_a a
LEFT JOIN rec_b b ON b.iso3 = a.iso3 AND b.jaar = a.jaar
WHERE b.iso3 IS NULL
ORDER BY a.jaar, a.iso3;

-- STAP: b_niet_in_a | hangt af van: rec_bronnen | soort: query
SELECT b.iso3 AS "Land", COUNT(*) AS "Jaren", MIN(b.jaar) AS "Van", MAX(b.jaar) AS "Tot",
       CASE WHEN NOT EXISTS (SELECT 1 FROM rec_a a WHERE a.iso3 = b.iso3) THEN 'land heeft geen biedzone in A' ELSE 'jaar ontbreekt in A' END AS "Soort verschil"
FROM rec_b b
LEFT JOIN rec_a a ON a.iso3 = b.iso3 AND a.jaar = b.jaar
WHERE a.iso3 IS NULL
GROUP BY b.iso3
ORDER BY 2 DESC, 1;

-- STAP: waardeverschillen | hangt af van: rec_vergelijk | soort: query
-- Zelfde land en jaar, buiten de tolerantie. Het teken laat zien welke bron lager zit.
SELECT iso3 AS "Land", jaar AS "Jaar", a_pct AS "Zon in A (%)", b_pct AS "Zon in B (%)",
       ROUND(a_pct - b_pct, 2) AS "Verschil (procentpunt)", verhouding AS "A gedeeld door B", zones AS "Zones in A",
       categorie AS "Categorie"
FROM rec_vergelijk
WHERE categorie <> 'sluit aan'
ORDER BY ABS(a_pct - b_pct) DESC;

-- STAP: totalen | hangt af van: rec_vergelijk | soort: query
-- Aansluiting op totaalniveau, per jaar: met en zonder de dekkingsgaten. Het tweede getal is het eerlijke verschil.
SELECT jaar AS "Jaar", COUNT(*) AS "Landen in beide",
       ROUND(100.0 * (AVG(a_pct) - AVG(b_pct)) / NULLIF(AVG(b_pct), 0), 1) AS "Verschil alle landen (%)",
       SUM(CASE WHEN categorie <> 'dekkingsgat in A' THEN 1 ELSE 0 END) AS "Landen zonder dekkingsgat",
       ROUND(100.0 * (AVG(CASE WHEN categorie <> 'dekkingsgat in A' THEN a_pct END) - AVG(CASE WHEN categorie <> 'dekkingsgat in A' THEN b_pct END))
             / NULLIF(AVG(CASE WHEN categorie <> 'dekkingsgat in A' THEN b_pct END), 0), 1) AS "Verschil zonder dekkingsgat (%)"
FROM rec_vergelijk
GROUP BY jaar
ORDER BY jaar;

-- STAP: samenvatting | hangt af van: rec_vergelijk | soort: query
SELECT (SELECT COUNT(*) FROM rec_a)                                                         AS "Rijen in A",
       (SELECT COUNT(*) FROM rec_b)                                                         AS "Rijen in B",
       (SELECT COUNT(*) FROM rec_vergelijk)                                                 AS "In beide",
       (SELECT COUNT(*) FROM rec_vergelijk WHERE categorie = 'sluit aan')                   AS "Sluit aan",
       (SELECT COUNT(*) FROM rec_vergelijk WHERE categorie = 'dekkingsgat in A')            AS "Dekkingsgat",
       (SELECT COUNT(*) FROM rec_vergelijk WHERE categorie NOT IN ('sluit aan', 'dekkingsgat in A')) AS "Wijkt af",
       (SELECT COUNT(*) FROM rec_a) - (SELECT COUNT(*) FROM rec_vergelijk)                  AS "Alleen in A",
       (SELECT COUNT(*) FROM rec_b) - (SELECT COUNT(*) FROM rec_vergelijk)                  AS "Alleen in B",
       ROUND(100.0 * (SELECT COUNT(*) FROM rec_vergelijk WHERE categorie NOT IN ('sluit aan', 'dekkingsgat in A'))
             / NULLIF((SELECT COUNT(*) FROM rec_vergelijk WHERE categorie <> 'dekkingsgat in A'), 0), 1) AS "Afwijkend zonder dekkingsgat (%)";

-- STAP: oorzaken | hangt af van: rec_vergelijk | soort: query
-- Per soort verschil: hoe vaak, de oorzaak voor zover de data die laat zien, en wat eraan te doen.
WITH alles AS (
    SELECT categorie AS soort FROM rec_vergelijk
    UNION ALL
    SELECT CASE WHEN a.jaar > (SELECT MAX(jaar) FROM rec_b) THEN 'tijdsverschil' ELSE 'alleen in A' END
    FROM rec_a a LEFT JOIN rec_b b ON b.iso3 = a.iso3 AND b.jaar = a.jaar WHERE b.iso3 IS NULL
    UNION ALL
    SELECT 'alleen in B' FROM rec_b b LEFT JOIN rec_a a ON a.iso3 = b.iso3 AND a.jaar = b.jaar WHERE a.iso3 IS NULL
)
SELECT soort AS "Soort", COUNT(*) AS "Aantal",
       CASE soort
            WHEN 'sluit aan' THEN 'geen'
            WHEN 'tijdsverschil' THEN 'Ember publiceert een jaar pas na afloop; A loopt tot vandaag'
            WHEN 'alleen in A' THEN 'landcode of jaar ontbreekt in Ember'
            WHEN 'alleen in B' THEN 'land heeft geen biedzone in de eigen tabel (bijvoorbeeld VK, Ierland)'
            WHEN 'dekkingsgat in A' THEN 'de bron van A meet in dat land en jaar (bijna) geen zon'
            WHEN 'structureel lager in A' THEN 'A telt een deel van de zon niet mee; vaak kleinschalig, achter de meter'
            WHEN 'structureel hoger in A' THEN 'A schat zon achter de meter mee, of rekent met een kleinere noemer'
            ELSE 'herziening, of ongewogen gemiddelde over zones' END AS "Oorzaak",
       CASE soort
            WHEN 'sluit aan' THEN 'geen actie'
            WHEN 'tijdsverschil' THEN 'het lopende jaar niet vergelijken'
            WHEN 'alleen in A' THEN 'koppeltabel met landcodes nalopen'
            WHEN 'alleen in B' THEN 'buiten de vergelijking laten, of de zone toevoegen'
            WHEN 'dekkingsgat in A' THEN 'A niet gebruiken voor het niveau; Ember voor het niveau, A alleen voor de vorm'
            WHEN 'structureel lager in A' THEN 'Ember voor het niveau; de verhouding A/B per land als correctiefactor'
            WHEN 'structureel hoger in A' THEN 'Ember voor het niveau; noemer van A nalopen'
            ELSE 'per geval nalopen; gewogen gemiddelde naar opwek per zone' END AS "Oplossing"
FROM alles
GROUP BY soort
ORDER BY 2 DESC;
