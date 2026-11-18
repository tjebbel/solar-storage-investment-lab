#!/bin/bash
# Nachtrun 4 (17 november 2026). Duurt naar schatting 30 tot 60 minuten; elke stap slaat zichzelf over bij een fout.
#  1. vs_eia       Texas en Californie uit het EIA-archief (rekent de rijen na die op 17 november in de browser zijn berekend)
#  2. eia_opwek    uurlijkse opwek per brandstof in Texas en Californie: echt zonprofiel, kernenergie, batterijvermogen
#  3. balans_probe welke balanceringsreeksen ENTSO-E voor Nederland geeft (aFRR, FCR); ruwe bestanden voor het stapelmodel
#  4. kernenergie  capture rate, negatieve uren en modulatie van kernenergie in 13 biedzones (uit bestanden die er al zijn)
cd "$(dirname "$0")"; source .venv/bin/activate
set -a; [ -f .env ] && source .env; set +a
mkdir -p resultaten
LOG=resultaten/nacht4_log.txt; echo "=== Start $(date) ===" | tee $LOG
PYTHONPATH=src python3 -m eti.wereld vs_eia eia_opwek balans_probe 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -W ignore -m eti.kernenergie 2>&1 | tee -a $LOG
PYTHONPATH=src python3 -m unittest discover -s tests 2>&1 | tail -3 | tee -a $LOG
echo "=== Klaar $(date) ===" | tee -a $LOG
