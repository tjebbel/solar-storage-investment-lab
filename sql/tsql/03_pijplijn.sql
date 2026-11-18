-- Pijplijn (T-SQL): van ruwe tabellen raw_* naar de tabellen waar analyse en dashboard op draaien (mart_*).
-- Vertaling van sql/03_pijplijn.sql (SQLite). Dezelfde stappen, dezelfde uitkomsten; de verschillen staan bij de stap.
-- Uitvoeren na 00_laden.sql, in database solar:  sqlcmd -d solar -i 03_pijplijn.sql
--
-- Verschillen met SQLite:
--  * datetime(x) -> TRY_CAST(x AS datetime2); strftime -> YEAR/MONTH/DATEPART; julianday -> DATEDIFF
--  * typeof(x) IN ('real','integer') -> TRY_CAST(x AS float) IS NOT NULL (tekst in een getalkolom valt af)
--  * GROUP_CONCAT -> STRING_AGG; CREATE TABLE AS -> SELECT ... INTO
--  * stg_batterij: SQLite kiest bij dubbele rijen een willekeurige rij; hier MAX per kolom (zelfde uitkomst bij een dubbele)

-- STAP: stg_nl_uur | hangt af van: raw_nl_uur | soort: tabel
DROP TABLE IF EXISTS dbo.stg_nl_uur;
WITH getypeerd AS (
    SELECT TRY_CAST(timestamp_utc AS datetime2)    AS tijdstip_utc,   -- NULL als de tekst geen geldig tijdstip is
           TRY_CAST(prijs_eur_mwh AS float)        AS prijs,          -- NULL bij tekst ("n/a", "12,5")
           TRY_CAST(solar_mw AS float)             AS zon_mw,
           TRY_CAST(wind_mw AS float)              AS wind_mw
    FROM dbo.raw_nl_uur
),
genummerd AS (                                                    -- dubbele tijdstippen: de rij met een prijs wint
    SELECT *, ROW_NUMBER() OVER (PARTITION BY tijdstip_utc ORDER BY CASE WHEN prijs IS NULL THEN 1 ELSE 0 END, prijs DESC) AS n
    FROM getypeerd
)
SELECT tijdstip_utc,
       CAST(tijdstip_utc AS date)     AS dag,
       YEAR(tijdstip_utc)             AS jaar,
       MONTH(tijdstip_utc)            AS maand,
       DATEPART(hour, tijdstip_utc)   AS uur,
       prijs, zon_mw, wind_mw
INTO dbo.stg_nl_uur
FROM genummerd
WHERE n = 1 AND tijdstip_utc IS NOT NULL AND prijs IS NOT NULL;
CREATE UNIQUE INDEX ux_stg_nl_uur ON dbo.stg_nl_uur (tijdstip_utc);
CREATE INDEX ix_stg_nl_uur_dag ON dbo.stg_nl_uur (dag);
CREATE INDEX ix_stg_nl_uur_jaar_maand ON dbo.stg_nl_uur (jaar, maand, uur);
GO

-- STAP: afgekeurd_nl_uur | hangt af van: raw_nl_uur | soort: tabel
-- Rijen die de staging niet haalden, met de reden. Niets verdwijnt stil.
DROP TABLE IF EXISTS dbo.afgekeurd_nl_uur;
SELECT timestamp_utc, prijs_eur_mwh,
       CASE WHEN TRY_CAST(timestamp_utc AS datetime2) IS NULL THEN 'ongeldig tijdstip'
            WHEN prijs_eur_mwh IS NULL THEN 'prijs ontbreekt'
            WHEN TRY_CAST(prijs_eur_mwh AS float) IS NULL THEN 'prijs is geen getal'
            ELSE 'dubbel tijdstip' END AS reden
INTO dbo.afgekeurd_nl_uur
FROM (SELECT r.*,
             ROW_NUMBER() OVER (PARTITION BY r.timestamp_utc
                                ORDER BY CASE WHEN TRY_CAST(r.prijs_eur_mwh AS float) IS NULL THEN 1 ELSE 0 END,
                                         TRY_CAST(r.prijs_eur_mwh AS float) DESC) AS n
      FROM dbo.raw_nl_uur r) x
WHERE TRY_CAST(timestamp_utc AS datetime2) IS NULL
   OR TRY_CAST(prijs_eur_mwh AS float) IS NULL
   OR n > 1;
GO

-- STAP: stg_land_jaar | hangt af van: raw_land_jaar | soort: tabel
DROP TABLE IF EXISTS dbo.stg_land_jaar;
WITH schoon AS (
    SELECT LTRIM(RTRIM(land))                       AS land,
           LTRIM(RTRIM(biedzone))                   AS biedzone,
           UPPER(LTRIM(RTRIM(iso3)))                AS iso3,
           TRY_CAST(jaar AS int)                    AS jaar,
           TRY_CAST(uren AS int)                    AS uren,
           TRY_CAST(gem_prijs AS float)             AS gem_prijs,
           TRY_CAST(negatieve_uren AS int)          AS negatieve_uren,
           TRY_CAST(dagspreiding AS float)          AS dagspreiding,
           -- een capture rate buiten 0..2 is een rekenfout (te weinig opwekdata): leeg maken en tellen
           CASE WHEN TRY_CAST(capture_zon AS float) BETWEEN 0 AND 2 THEN TRY_CAST(capture_zon AS float) END AS capture_zon,
           CASE WHEN TRY_CAST(capture_zon AS float) IS NOT NULL AND TRY_CAST(capture_zon AS float) NOT BETWEEN 0 AND 2 THEN 1 ELSE 0 END AS capture_zon_afgekeurd,
           CASE WHEN TRY_CAST(capture_wind AS float) BETWEEN 0 AND 2 THEN TRY_CAST(capture_wind AS float) END AS capture_wind,
           TRY_CAST(aandeel_zon AS float)                  AS aandeel_zon,                 -- aandeel volgens Ember (fractie)
           TRY_CAST(aandeel_zon_energycharts AS float)     AS aandeel_zon_energycharts,    -- aandeel volgens de gemeten opwek (fractie)
           CASE WHEN capture_bron LIKE 'opwek%' THEN 1 ELSE 0 END AS capture_gemeten,
           ROW_NUMBER() OVER (PARTITION BY LTRIM(RTRIM(biedzone)), TRY_CAST(jaar AS int)
                              ORDER BY TRY_CAST(uren AS int) DESC) AS n                    -- dubbel: meeste uren wint
    FROM dbo.raw_land_jaar
    WHERE biedzone IS NOT NULL AND LTRIM(RTRIM(biedzone)) <> '' AND TRY_CAST(jaar AS int) IS NOT NULL
)
SELECT land, biedzone, iso3, jaar, uren,
       CASE WHEN uren >= 8700 THEN 1 ELSE 0 END AS heel_jaar,
       gem_prijs, negatieve_uren, dagspreiding,
       capture_zon, capture_zon_afgekeurd, capture_wind, aandeel_zon, aandeel_zon_energycharts, capture_gemeten
INTO dbo.stg_land_jaar
FROM schoon
WHERE n = 1;
CREATE UNIQUE INDEX ux_stg_land_jaar ON dbo.stg_land_jaar (biedzone, jaar);
GO

-- STAP: stg_batterij | hangt af van: raw_flex_land | soort: tabel
DROP TABLE IF EXISTS dbo.stg_batterij;
SELECT LTRIM(RTRIM(land))                       AS land,
       TRY_CAST(jaar AS int)                    AS jaar,
       MAX(TRY_CAST(omzet_realistisch_per_mw AS float)) AS omzet_per_mw,
       MAX(TRY_CAST(omzet_perfect_per_mw AS float))     AS omzet_perfect_per_mw,
       MAX(TRY_CAST(irr_realistisch AS float))          AS irr          -- leeg betekent: de investering komt nooit terug
INTO dbo.stg_batterij
FROM dbo.raw_flex_land
WHERE TRY_CAST(uren_opslag AS int) = 2 AND land IS NOT NULL AND TRY_CAST(jaar AS int) IS NOT NULL
GROUP BY LTRIM(RTRIM(land)), TRY_CAST(jaar AS int);                  -- beschermt tegen dubbele rijen
CREATE UNIQUE INDEX ux_stg_batterij ON dbo.stg_batterij (land, jaar);
GO

-- STAP: stg_mix | hangt af van: raw_ember_opwek_jaar | soort: tabel
-- Ember is 'lang' (een rij per bron); hier 'breed' gemaakt met een kolom per bron.
DROP TABLE IF EXISTS dbo.stg_mix;
SELECT UPPER(LTRIM(RTRIM(iso_3_code)))  AS iso3,
       TRY_CAST(year AS int)            AS jaar,
       MAX(CASE WHEN electricity_source = 'Solar'   THEN TRY_CAST(share_of_generation AS float) END) AS aandeel_zon_pct,
       MAX(CASE WHEN electricity_source = 'Wind'    THEN TRY_CAST(share_of_generation AS float) END) AS aandeel_wind_pct,
       MAX(CASE WHEN electricity_source = 'Nuclear' THEN TRY_CAST(share_of_generation AS float) END) AS aandeel_kern_pct,
       MAX(CASE WHEN electricity_source = 'Gas'     THEN TRY_CAST(share_of_generation AS float) END) AS aandeel_gas_pct,
       MAX(CASE WHEN electricity_source = 'Demand'  THEN TRY_CAST(generation_twh AS float) END)      AS vraag_twh
INTO dbo.stg_mix
FROM dbo.raw_ember_opwek_jaar
WHERE iso_3_code IS NOT NULL AND LTRIM(RTRIM(iso_3_code)) <> ''    -- regio's zonder landcode tellen niet mee
GROUP BY UPPER(LTRIM(RTRIM(iso_3_code))), TRY_CAST(year AS int);
CREATE UNIQUE INDEX ux_stg_mix ON dbo.stg_mix (iso3, jaar);
GO

-- STAP: mart_zonejaar | hangt af van: stg_land_jaar, stg_batterij, stg_mix, raw_dim_zone | soort: tabel
DROP TABLE IF EXISTS dbo.mart_zonejaar;
SELECT l.biedzone, l.land, COALESCE(d.regio, 'Onbekend') AS regio, l.iso3, l.jaar, l.heel_jaar,
       l.gem_prijs, l.capture_zon, l.capture_wind, l.capture_gemeten, l.negatieve_uren, l.dagspreiding,
       b.omzet_per_mw AS batterij_per_mw, b.irr AS irr_batterij,
       m.aandeel_zon_pct, m.aandeel_wind_pct, m.aandeel_kern_pct, m.vraag_twh,
       CASE WHEN l.capture_zon < 0.60 AND l.negatieve_uren >= 300 THEN 'Zonverzadigd'     -- volgorde telt: verzadiging gaat voor
            WHEN l.dagspreiding >= 120 THEN 'Batterijmarkt'
            WHEN l.dagspreiding < 60 THEN 'Vlakke prijzen'
            WHEN l.capture_zon >= 0.75 THEN 'Zon houdt waarde'
            ELSE 'Middenveld' END AS segment
INTO dbo.mart_zonejaar
FROM dbo.stg_land_jaar l
LEFT JOIN dbo.stg_batterij b ON b.land = l.land AND b.jaar = l.jaar
LEFT JOIN dbo.stg_mix m      ON m.iso3 = l.iso3 AND m.jaar = l.jaar
LEFT JOIN dbo.raw_dim_zone d ON d.biedzone = l.biedzone;
CREATE UNIQUE INDEX ux_mart_zonejaar ON dbo.mart_zonejaar (biedzone, jaar);
CREATE INDEX ix_mart_zonejaar_filter ON dbo.mart_zonejaar (jaar, regio, segment);
GO

-- STAP: mart_nl_dag | hangt af van: stg_nl_uur | soort: tabel
-- Vooraf berekend: het dashboard hoeft de uurtabel niet meer te lezen.
DROP TABLE IF EXISTS dbo.mart_nl_dag;
SELECT dag, jaar, maand, COUNT(*) AS uren, AVG(prijs) AS gem_prijs, MAX(prijs) - MIN(prijs) AS dagspreiding,
       SUM(CASE WHEN prijs < 0 THEN 1 ELSE 0 END) AS negatieve_uren,
       SUM(zon_mw) AS zon_mwh, SUM(prijs * zon_mw) AS zon_omzet
INTO dbo.mart_nl_dag
FROM dbo.stg_nl_uur
GROUP BY dag, jaar, maand;
CREATE UNIQUE INDEX ux_mart_nl_dag ON dbo.mart_nl_dag (dag);
GO

-- STAP: mart_nl_maand | hangt af van: mart_nl_dag | soort: tabel
DROP TABLE IF EXISTS dbo.mart_nl_maand;
SELECT jaar, maand, SUM(uren) AS uren,
       SUM(gem_prijs * uren) / SUM(uren)                                                    AS gem_prijs,       -- gewogen naar uren, niet naar dagen
       SUM(zon_omzet) / NULLIF(SUM(zon_mwh), 0)                                             AS zonprijs,
       SUM(zon_omzet) / NULLIF(SUM(zon_mwh), 0) / (SUM(gem_prijs * uren) / SUM(uren))       AS capture_zon,
       SUM(negatieve_uren) AS negatieve_uren,
       AVG(dagspreiding) AS dagspreiding
INTO dbo.mart_nl_maand
FROM dbo.mart_nl_dag
GROUP BY jaar, maand;
CREATE UNIQUE INDEX ux_mart_nl_maand ON dbo.mart_nl_maand (jaar, maand);
GO

-- STAP: mart_zonemaand | hangt af van: raw_land_maand, stg_land_jaar, raw_dim_zone | soort: tabel
DROP TABLE IF EXISTS dbo.mart_zonemaand;
SELECT z.biedzone, m.land, COALESCE(d.regio, 'Onbekend') AS regio,
       TRY_CAST(m.jaar AS int) AS jaar, TRY_CAST(m.maand AS int) AS maand,
       TRY_CAST(m.gem_prijs AS float) AS gem_prijs,
       CASE WHEN TRY_CAST(m.capture_zon AS float) BETWEEN 0 AND 3 THEN TRY_CAST(m.capture_zon AS float) END AS capture_zon,
       TRY_CAST(m.negatieve_uren AS int) AS negatieve_uren,
       TRY_CAST(m.dagspreiding AS float) AS dagspreiding
INTO dbo.mart_zonemaand
FROM dbo.raw_land_maand m
JOIN (SELECT DISTINCT land, biedzone FROM dbo.stg_land_jaar) z ON z.land = LTRIM(RTRIM(m.land))    -- alleen zones die we kennen
LEFT JOIN dbo.raw_dim_zone d ON d.biedzone = z.biedzone
WHERE TRY_CAST(m.jaar AS int) IS NOT NULL AND TRY_CAST(m.maand AS int) BETWEEN 1 AND 12;
CREATE UNIQUE INDEX ux_mart_zonemaand ON dbo.mart_zonemaand (biedzone, jaar, maand);
CREATE INDEX ix_mart_zonemaand_tijd ON dbo.mart_zonemaand (jaar, maand);
GO

-- STAP: kwaliteit | hangt af van: stg_nl_uur, afgekeurd_nl_uur, stg_land_jaar, stg_batterij, mart_zonejaar, mart_nl_dag, mart_zonemaand | soort: tabel
-- Een rij per controle. status: ok, waarschuwing of fout. Een 'fout' hoort de publicatie tegen te houden.
DROP TABLE IF EXISTS dbo.kwaliteit;
SELECT * INTO dbo.kwaliteit FROM (
    SELECT 'aantal rijen: uurtabel' AS controle,
           CASE WHEN (SELECT COUNT(*) FROM dbo.stg_nl_uur) + (SELECT COUNT(*) FROM dbo.afgekeurd_nl_uur) = (SELECT COUNT(*) FROM dbo.raw_nl_uur) THEN 'ok' ELSE 'fout' END AS status,
           (SELECT COUNT(*) FROM dbo.stg_nl_uur) AS aantal,
           CONCAT('goedgekeurd plus afgekeurd moet gelijk zijn aan ruw (', (SELECT COUNT(*) FROM dbo.raw_nl_uur), ')') AS toelichting
    UNION ALL
    SELECT 'afgekeurde uren',
           CASE WHEN COUNT(*) = 0 THEN 'ok' WHEN COUNT(*) < 0.01 * (SELECT COUNT(*) FROM dbo.raw_nl_uur) THEN 'waarschuwing' ELSE 'fout' END,
           COUNT(*),
           COALESCE((SELECT STRING_AGG(CONCAT(reden, ': ', n), '; ')
                     FROM (SELECT reden, COUNT(*) AS n FROM dbo.afgekeurd_nl_uur GROUP BY reden) g), 'geen')
    FROM dbo.afgekeurd_nl_uur
    UNION ALL
    SELECT 'lege sleutels: zone-jaren',
           CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'fout' END, COUNT(*), 'biedzone of jaar leeg in mart_zonejaar'
    FROM dbo.mart_zonejaar WHERE biedzone IS NULL OR jaar IS NULL
    UNION ALL
    SELECT 'dubbele sleutels: zone-jaren',
           CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'fout' END, COUNT(*), 'meer dan een rij per biedzone en jaar'
    FROM (SELECT biedzone, jaar FROM dbo.mart_zonejaar GROUP BY biedzone, jaar HAVING COUNT(*) > 1) d
    UNION ALL
    SELECT 'verwijzing: zone zonder regio',
           CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'waarschuwing' END, COUNT(*),
           COALESCE((SELECT STRING_AGG(biedzone, ', ') FROM (SELECT DISTINCT biedzone FROM dbo.mart_zonejaar WHERE regio = 'Onbekend') g),
                    'elke zone heeft een regio')
    FROM dbo.mart_zonejaar WHERE regio = 'Onbekend'
    UNION ALL
    SELECT 'verwijzing: batterij zonder zone',
           CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'waarschuwing' END, COUNT(*), 'land in stg_batterij dat niet in stg_land_jaar staat'
    FROM dbo.stg_batterij b
    WHERE NOT EXISTS (SELECT 1 FROM dbo.stg_land_jaar l WHERE l.land = b.land AND l.jaar = b.jaar)
    UNION ALL
    SELECT 'verwijzing: zone-jaar zonder batterij',
           CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'waarschuwing' END, COUNT(*), 'zone-jaren zonder batterij-omzet'
    FROM dbo.mart_zonejaar WHERE batterij_per_mw IS NULL
    UNION ALL
    SELECT 'bereik: capture rate zon',
           CASE WHEN SUM(capture_zon_afgekeurd) = 0 THEN 'ok' ELSE 'waarschuwing' END, SUM(capture_zon_afgekeurd),
           COALESCE((SELECT STRING_AGG(CONCAT(biedzone, ' ', jaar), ', ') FROM dbo.stg_land_jaar WHERE capture_zon_afgekeurd = 1),
                    'alles binnen 0 en 2')
    FROM dbo.stg_land_jaar
    UNION ALL
    SELECT 'bereik: uurprijs',
           CASE WHEN COUNT(*) = 0 THEN 'ok' ELSE 'fout' END, COUNT(*), 'uurprijzen buiten -500 en 5000 euro per MWh'
    FROM dbo.stg_nl_uur WHERE prijs < -500 OR prijs > 5000
    UNION ALL
    SELECT 'volledigheid: dagen met 24 uren',
           CASE WHEN SUM(CASE WHEN uren <> 24 THEN 1 ELSE 0 END) <= 10 THEN 'ok' ELSE 'waarschuwing' END,
           SUM(CASE WHEN uren <> 24 THEN 1 ELSE 0 END), 'dagen met een ander aantal uren dan 24'
    FROM dbo.mart_nl_dag
    UNION ALL
    SELECT 'versheid: laatste dag',
           CASE WHEN DATEDIFF(day, MAX(dag), GETDATE()) <= 4 THEN 'ok'
                WHEN DATEDIFF(day, MAX(dag), GETDATE()) <= 15 THEN 'waarschuwing' ELSE 'fout' END,
           DATEDIFF(day, MAX(dag), GETDATE()),
           CONCAT('dagen sinds ', CONVERT(varchar(10), MAX(dag), 23))
    FROM dbo.mart_nl_dag
) k;
GO
