#!/bin/bash
# Grote nachtrun: 4 extra landen, kwartierwaarde batterij, vermogen, grensstromen, weer, prijsmodel, onzekerheid.
cd "$(dirname "$0")"; source .venv/bin/activate
LOG=resultaten/nacht2_log.txt; echo "=== Start $(date) ===" | tee $LOG
PYTHONPATH=src python3 -m eti.nacht2 2>&1 | tee -a $LOG
# tweede ronde: wat door een haperende verbinding mislukte, wordt nu uit de cache aangevuld
PYTHONPATH=src python3 -m eti.nacht2 meer_landen vermogen grensstromen weer prijsmodel 2>&1 | tee -a $LOG
echo "=== Alles klaar $(date) ===" | tee -a $LOG
# Wereld: overige Europese zones, Tasmanie, NASA, World Bank, OWID CO2, VK, Japan, VS (+ sleutelbronnen als gezet)
pip install -q gridstatus >> $LOG 2>&1 || echo "gridstatus niet geinstalleerd, VS wordt overgeslagen" | tee -a $LOG
PYTHONPATH=src python3 -m eti.wereld 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m eti.nacht2 onzekerheid 2>&1 | tee -a $LOG
echo "=== Wereld klaar $(date) ===" | tee -a $LOG
