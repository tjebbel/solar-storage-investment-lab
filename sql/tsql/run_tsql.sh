#!/bin/bash
# Draait de T-SQL-scripts in de container sqltest en schrijft het logboek naar de Mac.
# Uitvoeren in Terminal op de Mac (Docker Desktop aan, container sqltest draait):
#   bash ~/projecten/sqlserver_import/run_tsql.sh
# Wacht tot KLAAR verschijnt; typ intussen niets (invoer gaat anders naar het lopende script).
set -u
REPO="$HOME/projecten/tjebbel/set_up/energy_dashboard/solar-storage-investment-lab/sql/tsql"
LOG="$HOME/projecten/sqlserver_import/log_tsql.txt"

docker cp "$REPO/." sqltest:/tmp/tsql/ || { echo "FOUT: kopieren naar container"; exit 1; }
docker exec -u root sqltest chmod -R a+rX /tmp/tsql /var/opt/mssql/import

# -d solar: elke sqlcmd-aanroep is een nieuwe sessie die anders in master begint.
# -W: geen opvulling met spaties, zodat de uitvoer leesbaar blijft.
run() { docker exec sqltest /opt/mssql-tools18/bin/sqlcmd -C -b -d solar -S localhost -U sa -P "$(docker exec sqltest printenv MSSQL_SA_PASSWORD)" -W "$@"; }

{
  echo "== 00_laden"
  docker exec sqltest /opt/mssql-tools18/bin/sqlcmd -C -b -S localhost -U sa -P "$(docker exec sqltest printenv MSSQL_SA_PASSWORD)" -W -i /tmp/tsql/00_laden.sql || { echo "FOUT in 00_laden"; exit 1; }
  for f in 03_pijplijn 01_analyse 02_optimalisatie; do
    echo "== $f"
    run -v maand=2025-06 -i "/tmp/tsql/$f.sql" || { echo "FOUT in $f"; exit 1; }
  done
  echo "== 04_dashboard"
  run -v jaar=2025 jaar_van=2019 jaar_tot=2025 regio=alle segment=alle zone=alle niveau=land -i /tmp/tsql/04_dashboard.sql || echo "FOUT in 04"
  echo "== 05_reconciliatie"
  run -v tolerantie_pp=0.5 tolerantie_rel=0.10 -i /tmp/tsql/05_reconciliatie.sql || echo "FOUT in 05"
  echo "KLAAR"
} 2>&1 | tee "$LOG" | tail -40
