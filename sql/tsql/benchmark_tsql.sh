#!/bin/bash
# Meet de drie query's uit 02_optimalisatie.sql in SQL Server: een opwarmronde en vijf meetrondes.
# Voorwaarde: run_tsql.sh is een keer gelukt (database solar met stg_nl_uur en mart_nl_dag bestaat).
# Uitvoeren in Terminal op de Mac, vanuit de map van de repo:
#   bash sql/tsql/benchmark_tsql.sh
# Schrijft resultaten/benchmark_tsql.log. Typ niets tot KLAAR verschijnt.
set -u
cd "$(dirname "$0")/../.." || exit 1
mkdir -p resultaten
LOG=resultaten/benchmark_tsql.log
docker cp sql/tsql/02_optimalisatie.sql sqltest:/tmp/tsql/02_optimalisatie.sql >/dev/null
docker exec -u root sqltest chmod a+r /tmp/tsql/02_optimalisatie.sql
PW="$(docker exec sqltest printenv MSSQL_SA_PASSWORD)"
{
  docker exec sqltest /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$PW" -h -1 -Q "SET NOCOUNT ON; SELECT @@VERSION" | head -1
  for i in 0 1 2 3 4 5; do
    echo "== ronde $i"
    docker exec sqltest /opt/mssql-tools18/bin/sqlcmd -C -b -d solar -S localhost -U sa -P "$PW" -W -v maand=2025-06 -i /tmp/tsql/02_optimalisatie.sql \
      | grep -E "rows affected|SQL Server Execution Times|CPU time" | grep -v "parse and compile"
  done
  echo "KLAAR"
} > "$LOG" 2>&1
grep -c "ronde" "$LOG"; tail -3 "$LOG"
