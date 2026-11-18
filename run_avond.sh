#!/bin/bash
# Avondrun: alle NL-jaren opnieuw (met herstelde 2020/2026), daarna extra datasets voor Power BI.
cd "$(dirname "$0")"
source .venv/bin/activate
mkdir -p resultaten
LOG=resultaten/avond_log.txt
echo "=== Start $(date) ===" | tee $LOG
for YEAR in $(seq 2019 2026); do
  echo "== NL $YEAR" | tee -a $LOG
  PYTHONPATH=src python3 -m eti --source live --year $YEAR --db data/eti_live_$YEAR.db --out reports/live_$YEAR >> $LOG 2>&1 \
    && echo "   klaar" | tee -a $LOG || echo "   MISLUKT" | tee -a $LOG
done
PYTHONPATH=src python3 -m eti.extra 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.powerbi >> $LOG 2>&1
echo "=== Alles klaar $(date) ===" | tee -a $LOG
