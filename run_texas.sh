#!/bin/bash
# Texas aanvullen via gridstatus.io (sleutel in .env) en de opwekcijfers opnieuw rekenen. Duurt enkele minuten.
cd "$(dirname "$0")"; source .venv/bin/activate
set -a; [ -f .env ] && source .env; set +a
mkdir -p resultaten
LOG=resultaten/texas_log.txt; echo "=== Start $(date) ===" | tee $LOG
PYTHONPATH=src python3 -m eti.wereld vs_eia eia_opwek 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m unittest discover -s tests 2>&1 | tail -3 | tee -a $LOG
echo "=== Klaar $(date) ===" | tee -a $LOG
