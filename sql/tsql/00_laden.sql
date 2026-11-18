-- Laden: maakt de database 'solar' en de ruwe tabellen raw_*, en laadt de csv's uit de container.
-- Alle ruwe kolommen zijn tekst (NVARCHAR), net als de csv's. Typen komen pas in de pijplijn (TRY_CAST),
-- zodat tekst in een getalkolom (bijvoorbeeld "n/a" of "12,5") gevangen wordt en niet stil verdwijnt.
-- Lege velden worden NULL, net als in de SQLite-versie.
--
-- Uitvoeren (zie handleiding): csv's staan in /var/opt/mssql/import/ in de container.
-- Lees dit bestand met sqlcmd -v, dus zonder variabelen nodig.

IF DB_ID(N'solar') IS NULL CREATE DATABASE solar;
GO
USE solar;
GO
SET NOCOUNT ON;
GO

DROP TABLE IF EXISTS dbo.raw_nl_uur;
CREATE TABLE dbo.raw_nl_uur (timestamp_utc NVARCHAR(40), jaar NVARCHAR(10), maand NVARCHAR(10), uur NVARCHAR(10), prijs_eur_mwh NVARCHAR(40), solar_mw NVARCHAR(40), wind_mw NVARCHAR(40), gas_mw NVARCHAR(40), coal_mw NVARCHAR(40), nuclear_mw NVARCHAR(40), biomass_mw NVARCHAR(40), waste_mw NVARCHAR(40), other_renewable_mw NVARCHAR(40));
DROP TABLE IF EXISTS dbo.raw_land_jaar;
CREATE TABLE dbo.raw_land_jaar (land NVARCHAR(100), biedzone NVARCHAR(100), jaar NVARCHAR(10), gem_prijs NVARCHAR(40), mediaan_prijs NVARCHAR(40), capture_zon NVARCHAR(40), capture_wind NVARCHAR(40), negatieve_uren NVARCHAR(20), uren_boven_200 NVARCHAR(20), dagspreiding NVARCHAR(40), aandeel_zon NVARCHAR(40), aandeel_wind NVARCHAR(40), uren NVARCHAR(20), iso3 NVARCHAR(10), aandeel_zon_energycharts NVARCHAR(40), aandeel_wind_energycharts NVARCHAR(40), capture_bron NVARCHAR(100), zon_dekking NVARCHAR(40), capture_zon_gemeten NVARCHAR(40));
DROP TABLE IF EXISTS dbo.raw_flex_land;
CREATE TABLE dbo.raw_flex_land (land NVARCHAR(100), jaar NVARCHAR(10), uren_opslag NVARCHAR(10), omzet_perfect_per_mw NVARCHAR(40), omzet_realistisch_per_mw NVARCHAR(40), voorspel_ratio NVARCHAR(40), irr_realistisch NVARCHAR(40));
DROP TABLE IF EXISTS dbo.raw_land_maand;
CREATE TABLE dbo.raw_land_maand (land NVARCHAR(100), jaar NVARCHAR(10), maand NVARCHAR(10), gem_prijs NVARCHAR(40), capture_zon NVARCHAR(40), capture_wind NVARCHAR(40), negatieve_uren NVARCHAR(20), dagspreiding NVARCHAR(40));
DROP TABLE IF EXISTS dbo.raw_ember_opwek_jaar;
CREATE TABLE dbo.raw_ember_opwek_jaar (area NVARCHAR(100), iso_3_code NVARCHAR(10), year NVARCHAR(10), area_type NVARCHAR(50), electricity_source NVARCHAR(100), generation_twh NVARCHAR(40), share_of_generation NVARCHAR(40), capacity_gw NVARCHAR(40), emissions_mtco2e NVARCHAR(40));
DROP TABLE IF EXISTS dbo.raw_dim_land;
CREATE TABLE dbo.raw_dim_land (iso3 NVARCHAR(10), land NVARCHAR(100), continent NVARCHAR(50), ember_regio NVARCHAR(100), eu NVARCHAR(10), oecd NVARCHAR(10), g20 NVARCHAR(10), studieregio NVARCHAR(100));
DROP TABLE IF EXISTS dbo.raw_dim_zone;
CREATE TABLE dbo.raw_dim_zone (biedzone NVARCHAR(100), regio NVARCHAR(100));
GO

-- Laden: eerste regel is de kopregel. Scheidteken is | (zie de export).
BULK INSERT dbo.raw_nl_uur            FROM '/var/opt/mssql/import/raw_nl_uur.csv'            WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', FIRSTROW = 2, TABLOCK);
BULK INSERT dbo.raw_land_jaar         FROM '/var/opt/mssql/import/raw_land_jaar.csv'         WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', FIRSTROW = 2, TABLOCK);
BULK INSERT dbo.raw_flex_land         FROM '/var/opt/mssql/import/raw_flex_land.csv'         WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', FIRSTROW = 2, TABLOCK);
BULK INSERT dbo.raw_land_maand        FROM '/var/opt/mssql/import/raw_land_maand.csv'        WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', FIRSTROW = 2, TABLOCK);
BULK INSERT dbo.raw_ember_opwek_jaar  FROM '/var/opt/mssql/import/raw_ember_opwek_jaar.csv'  WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', FIRSTROW = 2, TABLOCK);
BULK INSERT dbo.raw_dim_land          FROM '/var/opt/mssql/import/raw_dim_land.csv'          WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', FIRSTROW = 2, TABLOCK);
BULK INSERT dbo.raw_dim_zone          FROM '/var/opt/mssql/import/raw_dim_zone.csv'          WITH (FIELDTERMINATOR = '|', ROWTERMINATOR = '0x0a', FIRSTROW = 2, TABLOCK);
GO

-- Lege velden die als lege tekst binnenkomen, worden NULL (zoals in de SQLite-versie).
DECLARE @tabel sysname, @kolom sysname, @sql nvarchar(max);
DECLARE kol CURSOR LOCAL FAST_FORWARD FOR
    SELECT t.name, c.name
    FROM sys.columns c JOIN sys.tables t ON t.object_id = c.object_id
    WHERE t.schema_id = SCHEMA_ID(N'dbo') AND t.name LIKE N'raw[_]%';
OPEN kol;
FETCH NEXT FROM kol INTO @tabel, @kolom;
WHILE @@FETCH_STATUS = 0
BEGIN
    SET @sql = N'UPDATE dbo.' + QUOTENAME(@tabel) + N' SET ' + QUOTENAME(@kolom) + N' = NULL WHERE ' + QUOTENAME(@kolom) + N' = N'''';';
    EXEC sp_executesql @sql;
    FETCH NEXT FROM kol INTO @tabel, @kolom;
END
CLOSE kol;
DEALLOCATE kol;
GO

-- Controle: aantallen moeten gelijk zijn aan de csv's (zie reports/analyse/ voor de SQLite-aantallen).
SELECT 'raw_nl_uur' AS tabel, COUNT(*) AS rijen FROM dbo.raw_nl_uur
UNION ALL SELECT 'raw_land_jaar', COUNT(*) FROM dbo.raw_land_jaar
UNION ALL SELECT 'raw_flex_land', COUNT(*) FROM dbo.raw_flex_land
UNION ALL SELECT 'raw_land_maand', COUNT(*) FROM dbo.raw_land_maand
UNION ALL SELECT 'raw_ember_opwek_jaar', COUNT(*) FROM dbo.raw_ember_opwek_jaar
UNION ALL SELECT 'raw_dim_land', COUNT(*) FROM dbo.raw_dim_land
UNION ALL SELECT 'raw_dim_zone', COUNT(*) FROM dbo.raw_dim_zone;
GO
