#!/bin/bash
cd "$(dirname "$0")"; source .venv/bin/activate
LOG=resultaten/nacht_log.txt; echo "=== Start $(date) ===" | tee $LOG
PYTHONPATH=src python3 -m eti.nacht 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.bootstrap 10000 2>&1 | tee -a $LOG
echo "=== Alles klaar $(date) ===" | tee -a $LOG
