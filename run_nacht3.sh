#!/bin/bash
# Leest sleutels uit .env en draait wat ze ontsluiten, plus de interconnectie-export.
cd "$(dirname "$0")"; source .venv/bin/activate
set -a; [ -f .env ] && source .env; set +a
LOG=resultaten/nacht3_log.txt; echo "=== Start $(date) ===" | tee $LOG
PYTHONPATH=src python3 -m eti.interconnectie 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.wereld uk japan vs vs_eia eia_gas onbalans ember 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.ember_global 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.herstel 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.herijk 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.verbanden 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.ruimtelijk 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.onbalansregel 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.volledige_case 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.regio_indeling 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.numbers 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.powerbi 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m unittest discover -s tests 2>&1 | tail -3 | tee -a $LOG
echo "=== Klaar $(date) ===" | tee -a $LOG
