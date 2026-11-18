-- Pijplijn: van ruwe csv-tabellen (raw_*) naar tabellen waar analyse en dashboard op draaien (mart_*).
-- Dialect: SQLite. Elke stap begint met een regel "-- STAP: naam | hangt af van: ... | soort: tabel of query".
-- De stappen zijn herhaalbaar: een tabel wordt eerst weggegooid en dan opnieuw gebouwd.
--
-- Afhankelijkheden (DAG):
--   raw_nl_uur ──► stg_nl_uur ──► mart_nl_dag ──► mart_nl_maand
--        └──────► afgekeurd_nl_uur
--   raw_land_jaar ──► stg_land_jaar ─┐
--   raw_flex_land ──► stg_batterij ──┼──► mart_zonejaar ──► kwaliteit
--   raw_ember_opwek_jaar ► stg_mix ──┤
--   raw_dim_zone ────────────────────┘
--   raw_land_maand + raw_dim_zone ──► mart_zonemaand
-- Staging mag naast elkaar draaien; elke mart wacht op haar staging; kwaliteit draait als laatste.

-- STAP: stg_nl_uur | hangt af van: raw_nl_uur | soort: tabel
DROP TABLE IF EXISTS stg_nl_uur;
CREATE TABLE stg_nl_uur AS
WITH getypeerd AS (
    SELECT datetime(timestamp_utc)        AS tijdstip_utc,     -- NULL als de tekst geen geldig tijdstip is
           CAST(prijs_eur_mwh AS REAL)    AS prijs,
           CAST(solar_mw AS REAL)         AS zon_mw,
           CAST(wind_mw AS REAL)          AS wind_mw,
           typeof(prijs_eur_mwh)          AS type_prijs       -- vangt tekst in een getalkolom ("n/a", "12,5")
    FROM raw_nl_uur
),
genummerd AS (                                                 -- dubbele tijdstippen: de rij met een prijs wint
    SELECT *, ROW_NUMBER() OVER (PARTITION BY tijdstip_utc ORDER BY prijs IS NULL, prijs DESC) AS n
    FROM getypeerd
)
SELECT tijdstip_utc,
       date(tijdstip_utc)                              AS dag,
       CAST(strftime('%Y', tijdstip_utc) AS INTEGER)   AS jaar,
       CAST(strftime('%m', tijdstip_utc) AS INTEGER)   AS maand,
       CAST(strftime('%H', tijdstip_utc) AS INTEGER)   AS uur,
       prijs, zon_mw, wind_mw
FROM genummerd
WHERE n = 1 AND tijdstip_utc IS NOT NULL AND prijs IS NOT NULL AND type_prijs IN ('real', 'integer');
CREATE UNIQUE INDEX ux_stg_nl_uur ON stg_nl_uur (tijdstip_utc);
CREATE INDEX ix_stg_nl_uur_dag ON stg_nl_uur (dag);
CREATE INDEX ix_stg_nl_uur_jaar_maand ON stg_nl_uur (jaar, maand, uur);

-- STAP: afgekeurd_nl_uur | hangt af van: raw_nl_uur | soort: tabel
-- Rijen die de staging niet haalden, met de reden. Niets verdwijnt stil.
DROP TABLE IF EXISTS afgekeurd_nl_uur;
CREATE TABLE afgekeurd_nl_uur AS
SELECT timestamp_utc, prijs_eur_mwh,
       CASE WHEN datetime(timestamp_utc) IS NULL THEN 'ongeldig tijdstip'
            WHEN prijs_eur_mwh IS NULL THEN 'prijs ontbreekt'
            WHEN typeof(prijs_eur_mwh) NOT IN ('real', 'integer') THEN 'prijs is geen getal'
            ELSE 'dubbel tijdstip' END AS reden
FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY timestamp_utc ORDER BY prijs_eur_mwh IS NULL, prijs_eur_mwh DESC) AS n FROM raw_nl_uur)
WHERE datetime(timestamp_utc) IS NULL OR prijs_eur_mwh IS NULL OR typeof(prijs_eur_mwh) NOT IN ('real', 'integer') OR n > 1;

-- STAP: stg_land_jaar | hangt af van: raw_land_jaar | soort: tabel
DROP TABLE IF EXISTS stg_land_jaar;
CREATE TABLE stg_land_jaar AS
WITH schoon AS (
    SELECT TRIM(land)                 AS land,
           TRIM(biedzone)             AS biedzone,
           UPPER(TRIM(iso3))          AS iso3,
           CAST(jaar AS INTEGER)      AS jaar,
           CAST(uren AS INTEGER)      AS uren,
           CAST(gem_prijs AS REAL)    AS gem_prijs,
           CAST(negatieve_uren AS INTEGER) AS negatieve_uren,
           CAST(dagspreiding AS REAL) AS dagspreiding,
           -- een capture rate buiten 0..2 is een rekenfout (te weinig opwekdata): leeg maken en tellen
           CASE WHEN capture_zon BETWEEN 0 AND 2 THEN CAST(capture_zon AS REAL) END    AS capture_zon,
           CASE WHEN capture_zon IS NOT NULL AND capture_zon NOT BETWEEN 0 AND 2 THEN 1 ELSE 0 END AS capture_zon_afgekeurd,
           CASE WHEN capture_wind BETWEEN 0 AND 2 THEN CAST(capture_wind AS REAL) END  AS capture_wind,
           CAST(aandeel_zon AS REAL)  AS aandeel_zon,                          -- aandeel volgens Ember (fractie)
           CAST(aandeel_zon_energycharts AS REAL) AS aandeel_zon_energycharts, -- aandeel volgens de gemeten opwek (fractie)
           COALESCE(capture_bron LIKE 'opwek%', 0) AS capture_gemeten,
           ROW_NUMBER() OVER (PARTITION BY TRIM(biedzone), CAST(jaar AS INTEGER) ORDER BY uren DESC) AS n   -- dubbel: meeste uren wint
    FROM raw_land_jaar
    WHERE biedzone IS NOT NULL AND TRIM(biedzone) <> '' AND jaar IS NOT NULL                                -- geen lege sleutels
)
SELECT land, biedzone, iso3, jaar, uren, uren >= 8700 AS heel_jaar, gem_prijs, negatieve_uren, dagspreiding,
       capture_zon, capture_zon_afgekeurd, capture_wind, aandeel_zon, aandeel_zon_energycharts, capture_gemeten
FROM schoon
WHERE n = 1;
CREATE UNIQUE INDEX ux_stg_land_jaar ON stg_land_jaar (biedzone, jaar);

-- STAP: stg_batterij | hangt af van: raw_flex_land | soort: tabel
DROP TABLE IF EXISTS stg_batterij;
CREATE TABLE stg_batterij AS
SELECT TRIM(land) AS land, CAST(jaar AS INTEGER) AS jaar,
       CAST(omzet_realistisch_per_mw AS REAL) AS omzet_per_mw,
       CAST(omzet_perfect_per_mw AS REAL)     AS omzet_perfect_per_mw,
       CAST(irr_realistisch AS REAL)          AS irr          -- leeg betekent: de investering komt nooit terug
FROM raw_flex_land
WHERE uren_opslag = 2 AND land IS NOT NULL AND jaar IS NOT NULL
GROUP BY TRIM(land), CAST(jaar AS INTEGER);                    -- beschermt tegen dubbele rijen
CREATE UNIQUE INDEX ux_stg_batterij ON stg_batterij (land, jaar);

-- STAP: stg_mix | hangt af van: raw_ember_opwek_jaar | soort: tabel
-- Ember is 'lang' (een rij per bron); hier 'breed' gemaakt met een kolom per bron.
DROP TABLE IF EXISTS stg_mix;
CREATE TABLE stg_mix AS
SELECT UPPER(TRIM(iso_3_code)) AS iso3, CAST(year AS INTEGER) AS jaar,
       MAX(CASE WHEN electricity_source = 'Solar'   THEN share_of_generation END) AS aandeel_zon_pct,
       MAX(CASE WHEN electricity_source = 'Wind'    THEN share_of_generation END) AS aandeel_wind_pct,
       MAX(CASE WHEN electricity_source = 'Nuclear' THEN share_of_generation END) AS aandeel_kern_pct,
       MAX(CASE WHEN electricity_source = 'Gas'     THEN share_of_generation END) AS aandeel_gas_pct,
       MAX(CASE WHEN electricity_source = 'Demand'  THEN generation_twh END)      AS vraag_twh
FROM raw_ember_opwek_jaar
WHERE iso_3_code IS NOT NULL AND TRIM(iso_3_code) <> ''        -- regio's zonder landcode tellen niet mee
GROUP BY 1, 2;
CREATE UNIQUE INDEX ux_stg_mix ON stg_mix (iso3, jaar);

-- STAP: mart_zonejaar | hangt af van: stg_land_jaar, stg_batterij, stg_mix, raw_dim_zone | soort: tabel
DROP TABLE IF EXISTS mart_zonejaar;
CREATE TABLE mart_zonejaar AS
SELECT l.biedzone, l.land, COALESCE(d.regio, 'Onbekend') AS regio, l.iso3, l.jaar, l.heel_jaar,
       l.gem_prijs, l.capture_zon, l.capture_wind, l.capture_gemeten, l.negatieve_uren, l.dagspreiding,
       b.omzet_per_mw AS batterij_per_mw, b.irr AS irr_batterij,
       m.aandeel_zon_pct, m.aandeel_wind_pct, m.aandeel_kern_pct, m.vraag_twh,
       CASE WHEN l.capture_zon < 0.60 AND l.negatieve_uren >= 300 THEN 'Zonverzadigd'      -- volgorde telt: verzadiging gaat voor
            WHEN l.dagspreiding >= 120 THEN 'Batterijmarkt'
            WHEN l.dagspreiding < 60 THEN 'Vlakke prijzen'
            WHEN l.capture_zon >= 0.75 THEN 'Zon houdt waarde'
            ELSE 'Middenveld' END AS segment
FROM stg_land_jaar l
LEFT JOIN stg_batterij b ON b.land = l.land AND b.jaar = l.jaar
LEFT JOIN stg_mix m      ON m.iso3 = l.iso3 AND m.jaar = l.jaar
LEFT JOIN raw_dim_zone d ON d.biedzone = l.biedzone;
CREATE UNIQUE INDEX ux_mart_zonejaar ON mart_zonejaar (biedzone, jaar);
CREATE INDEX ix_mart_zonejaar_filter ON mart_zonejaar (jaar, regio, segment);

-- STAP: mart_nl_dag | hangt af van: stg_nl_uur | soort: tabel
-- Vooraf berekend: het dashboard hoeft de uurtabel niet meer te lezen.
DROP TABLE IF EXISTS mart_nl_dag;
CREATE TABLE mart_nl_dag AS
SELECT dag, jaar, maand, COUNT(*) AS uren, AVG(prijs) AS gem_prijs, MAX(prijs) - MIN(prijs) AS dagspreiding,
       SUM(prijs < 0) AS negatieve_uren, SUM(zon_mw) AS zon_mwh, SUM(prijs * zon_mw) AS zon_omzet
FROM stg_nl_uur
GROUP BY dag, jaar, maand;
CREATE UNIQUE INDEX ux_mart_nl_dag ON mart_nl_dag (dag);

-- STAP: mart_nl_maand | hangt af van: mart_nl_dag | soort: tabel
DROP TABLE IF EXISTS mart_nl_maand;
CREATE TABLE mart_nl_maand AS
SELECT jaar, maand, SUM(uren) AS uren,
       SUM(gem_prijs * uren) / SUM(uren)                                   AS gem_prijs,          -- gewogen naar uren, niet naar dagen
       SUM(zon_omzet) / NULLIF(SUM(zon_mwh), 0)                            AS zonprijs,
       SUM(zon_omzet) / NULLIF(SUM(zon_mwh), 0) / (SUM(gem_prijs * uren) / SUM(uren)) AS capture_zon,
       SUM(negatieve_uren) AS negatieve_uren, AVG(dagspreiding) AS dagspreiding
FROM mart_nl_dag
GROUP BY jaar, maand;
CREATE UNIQUE INDEX ux_mart_nl_maand ON mart_nl_maand (jaar, maand);

-- STAP: mart_zonemaand | hangt af van: raw_land_maand, stg_land_jaar, raw_dim_zone | soort: tabel
DROP TABLE IF EXISTS mart_zonemaand;
CREATE TABLE mart_zonemaand AS
SELECT z.biedzone, m.land, COALESCE(d.regio, 'Onbekend') AS regio, CAST(m.jaar AS INTEGER) AS jaar, CAST(m.maand AS INTEGER) AS maand,
       CAST(m.gem_prijs AS REAL) AS gem_prijs,
       CASE WHEN m.capture_zon BETWEEN 0 AND 3 THEN m.capture_zon END AS capture_zon,
       CAST(m.negatieve_uren AS INTEGER) AS negatieve_uren, CAST(m.dagspreiding AS REAL) AS dagspreiding
FROM raw_land_maand m
JOIN (SELECT DISTINCT land, biedzone FROM stg_land_jaar) z ON z.land = TRIM(m.land)      -- alleen zones die we kennen
LEFT JOIN raw_dim_zone d ON d.biedzone = z.biedzone
WHERE m.jaar IS NOT NULL AND m.maand BETWEEN 1 AND 12;
CREATE UNIQUE INDEX ux_mart_zonemaand ON mart_zonemaand (biedzone, jaar, maand);
CREATE INDEX ix_mart_zonemaand_tijd ON mart_zonemaand (jaar, maand);

-- STAP: kwaliteit | hangt af van: stg_nl_uur, afgekeurd_nl_uur, stg_land_jaar, stg_batterij, mart_zonejaar, mart_nl_dag, mart_zonemaand | soort: tabel
-- Een rij per controle. status: ok, waarschuwing of fout. Een 'fout' hoort de publicatie tegen te houden.
DROP TABLE IF EXISTS kwaliteit;
CREATE TABLE kwaliteit AS
SELECT 'aantal rijen: uurtabel' AS controle,
       CASE WHEN (SELECT COUNT(*) FROM stg_nl_uur) + (SELECT COUNT(*) FROM afgekeurd_nl_uur) = (SELECT COUNT(*) FROM raw_nl_uur) THEN 'ok' ELSE 'fout' END AS status,
       (SELECT COUNT(*) FROM stg_nl_uur) AS aantal,
       'goedgekeurd plus afgekeurd moet gelijk zijn aan ruw (' || (SELECT COUNT(*) FROM raw_nl_uur) || ')' AS toelichting
UNION ALL
SELECT 'afgekeurde uren', CASE WHEN COUNT(*) = 0 THEN 'ok' WHEN COUNT(*) < 0.01 * (SELECT COUNT(*) FROM raw_nl_uur) THEN 'waarschuwing' ELSE 'fout' END, COUNT(*),
       COALESCE((SELECT GROUP_CONCAT(reden || ': ' || n, '; ') FROM (SELECT reden, COUNT(*) AS n FROM afgekeurd_nl_uur GROUP BY reden)), 'geen')
FROM afgekeurd_nl_uur
UNION ALL
SELECT 'lege sleutels: zone-jaren', CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'fout' END, COUNT(*), 'biedzone of jaar leeg in mart_zonejaar'
FROM mart_zonejaar WHERE biedzone IS NULL OR jaar IS NULL
UNION ALL
SELECT 'dubbele sleutels: zone-jaren', CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'fout' END, COUNT(*), 'meer dan een rij per biedzone en jaar'
FROM (SELECT biedzone, jaar FROM mart_zonejaar GROUP BY biedzone, jaar HAVING COUNT(*) > 1)
UNION ALL
SELECT 'verwijzing: zone zonder regio', CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'waarschuwing' END, COUNT(*),
       COALESCE(GROUP_CONCAT(DISTINCT biedzone), 'elke zone heeft een regio')
FROM mart_zonejaar WHERE regio = 'Onbekend'
UNION ALL
SELECT 'verwijzing: batterij zonder zone', CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'waarschuwing' END, COUNT(*), 'land in stg_batterij dat niet in stg_land_jaar staat'
FROM stg_batterij b WHERE NOT EXISTS (SELECT 1 FROM stg_land_jaar l WHERE l.land = b.land AND l.jaar = b.jaar)
UNION ALL
SELECT 'verwijzing: zone-jaar zonder batterij', CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'waarschuwing' END, COUNT(*), 'zone-jaren zonder batterij-omzet'
FROM mart_zonejaar WHERE batterij_per_mw IS NULL
UNION ALL
SELECT 'bereik: capture rate zon', CASE WHEN SUM(capture_zon_afgekeurd) = 0 THEN 'ok' ELSE 'waarschuwing' END, SUM(capture_zon_afgekeurd),
       COALESCE((SELECT GROUP_CONCAT(biedzone || ' ' || jaar, ', ') FROM stg_land_jaar WHERE capture_zon_afgekeurd = 1), 'alles binnen 0 en 2')
FROM stg_land_jaar
UNION ALL
SELECT 'bereik: uurprijs', CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'fout' END, COUNT(*), 'uurprijzen buiten -500 en 5000 euro per MWh'
FROM stg_nl_uur WHERE prijs < -500 OR prijs > 5000
UNION ALL
SELECT 'volledigheid: dagen met 24 uren', CASE WHEN SUM(uren <> 24) <= 10 THEN 'ok' ELSE 'waarschuwing' END, SUM(uren <> 24), 'dagen met een ander aantal uren dan 24'
FROM mart_nl_dag
UNION ALL
SELECT 'versheid: laatste dag', CASE WHEN julianday('now') - julianday(MAX(dag)) <= 4 THEN 'ok' WHEN julianday('now') - julianday(MAX(dag)) <= 15 THEN 'waarschuwing' ELSE 'fout' END,
       CAST(julianday('now') - julianday(MAX(dag)) AS INTEGER), 'dagen sinds ' || MAX(dag)
FROM mart_nl_dag;
