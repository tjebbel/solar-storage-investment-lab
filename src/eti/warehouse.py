"""Star schema in SQLite: idempotent loading and analysis views."""
import sqlite3
from .data import TECHNOLOGIES

SCHEMA = """
CREATE TABLE IF NOT EXISTS dim_technology (
    technology TEXT PRIMARY KEY, renewable INTEGER NOT NULL, kg_co2_per_mwh REAL NOT NULL);
CREATE TABLE IF NOT EXISTS fact_price (
    ts_utc TEXT PRIMARY KEY, price_eur_mwh REAL);
CREATE TABLE IF NOT EXISTS fact_generation (
    ts_utc TEXT NOT NULL, technology TEXT NOT NULL REFERENCES dim_technology(technology),
    mwh REAL NOT NULL, PRIMARY KEY (ts_utc, technology));
CREATE VIEW IF NOT EXISTS v_hour AS
SELECT p.ts_utc, p.price_eur_mwh AS price,
       SUM(CASE WHEN g.technology = 'solar' THEN g.mwh END) AS solar_mwh,
       SUM(g.mwh) AS total_mwh,
       SUM(g.mwh * t.kg_co2_per_mwh) / SUM(g.mwh) AS grid_kg_per_mwh
FROM fact_price p
JOIN fact_generation g ON g.ts_utc = p.ts_utc
JOIN dim_technology t ON t.technology = g.technology
GROUP BY p.ts_utc;
"""


def connect(path):
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    return db


def load(db, rows):
    """Upsert rows from data.synthetic_year (or a real loader). Running twice changes nothing."""
    with db:
        db.executemany("INSERT INTO dim_technology VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                       [(k, int(v[0]), v[1]) for k, v in TECHNOLOGIES.items()])
        db.executemany("""INSERT INTO fact_price VALUES (?, ?)
                          ON CONFLICT (ts_utc) DO UPDATE SET price_eur_mwh = excluded.price_eur_mwh""",
                       [(t.strftime("%Y-%m-%dT%H:%MZ"), p) for t, p, _ in rows])
        db.executemany("""INSERT INTO fact_generation VALUES (?, ?, ?)
                          ON CONFLICT (ts_utc, technology) DO UPDATE SET mwh = excluded.mwh""",
                       [(t.strftime("%Y-%m-%dT%H:%MZ"), k, round(v, 1))
                        for t, _, g in rows for k, v in g.items()])
    return db.execute("SELECT COUNT(*) FROM fact_price").fetchone()[0]


def hourly(db):
    """Hourly series ordered by time: (ts_utc, price, solar_mwh, grid_kg_per_mwh)."""
    return db.execute("SELECT ts_utc, price, solar_mwh, grid_kg_per_mwh FROM v_hour ORDER BY ts_utc").fetchall()
