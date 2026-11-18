-- Vraag: in welke biedzones is opslag in het laatste hele jaar het aantrekkelijkst, en hoe staat zon er daar voor?
-- Draait op de ruwe tabellen, zodat de query ook zonder pijplijn werkt.

-- STAP: analyse_zones | hangt af van: raw_land_jaar, raw_flex_land, raw_dim_zone | soort: query
WITH
laatste AS (                 -- het laatste hele jaar: minstens 8.700 uren met een prijs
    SELECT MAX(jaar) AS jaar FROM raw_land_jaar WHERE uren >= 8700
),
zon AS (                     -- een capture rate buiten 0..2 is een rekenfout en wordt leeg
    SELECT biedzone, land, jaar, gem_prijs, negatieve_uren, dagspreiding,
           CASE WHEN capture_zon BETWEEN 0 AND 2 THEN capture_zon END AS capture_zon
    FROM raw_land_jaar
    WHERE biedzone IS NOT NULL
),
batterij AS (                -- batterij van 2 uur; een lege IRR betekent dat de investering nooit terugkomt
    SELECT land, jaar, omzet_realistisch_per_mw AS omzet, irr_realistisch AS irr
    FROM raw_flex_land
    WHERE uren_opslag = 2
),
nu AS (
    SELECT z.*, b.omzet, b.irr
    FROM zon z
    JOIN laatste t ON z.jaar = t.jaar
    LEFT JOIN batterij b ON b.land = z.land AND b.jaar = z.jaar
),
vorig AS (
    SELECT z.biedzone, b.omzet
    FROM zon z
    JOIN laatste t ON z.jaar = t.jaar - 1
    LEFT JOIN batterij b ON b.land = z.land AND b.jaar = z.jaar
),
basis AS (                   -- 2019 als ijkpunt voor de daling van de marktwaarde van zon
    SELECT biedzone, capture_zon FROM zon WHERE jaar = 2019
)
SELECT
    COALESCE(d.regio, 'Onbekend')                                  AS "Regio",
    n.land                                                         AS "Land of zone",
    n.jaar                                                         AS "Jaar",
    CAST(ROUND(n.omzet) AS INTEGER)                                AS "Batterij-omzet (euro per MW)",
    ROUND(100.0 * (n.omzet - v.omzet) / NULLIF(v.omzet, 0), 1)     AS "Verandering batterij-omzet (%)",
    CASE WHEN n.omzet IS NULL THEN 'geen cijfer'
         WHEN n.irr IS NULL THEN 'verdient zich niet terug'
         ELSE printf('%.1f%%', 100 * n.irr) END                    AS "IRR batterij op de dagmarkt",
    ROUND(n.capture_zon, 2)                                        AS "Capture rate zon",
    ROUND(n.capture_zon - b.capture_zon, 2)                        AS "Verandering sinds 2019",
    CAST(n.negatieve_uren AS INTEGER)                              AS "Negatieve uren",
    CAST(ROUND(n.dagspreiding) AS INTEGER)                         AS "Dagspreiding (euro per MWh)",
    CASE WHEN n.capture_zon < 0.60 AND n.negatieve_uren >= 300 THEN 'Zonverzadigd'
         WHEN n.dagspreiding >= 120 THEN 'Batterijmarkt'
         WHEN n.dagspreiding < 60 THEN 'Vlakke prijzen'
         WHEN n.capture_zon >= 0.75 THEN 'Zon houdt waarde'
         ELSE 'Middenveld' END                                     AS "Segment",
    RANK() OVER (PARTITION BY COALESCE(d.regio, 'Onbekend') ORDER BY n.omzet DESC) AS "Rang in de regio"
FROM nu n
LEFT JOIN vorig v        ON v.biedzone = n.biedzone
LEFT JOIN basis b        ON b.biedzone = n.biedzone
LEFT JOIN raw_dim_zone d ON d.biedzone = n.biedzone
ORDER BY n.omzet DESC NULLS LAST;
