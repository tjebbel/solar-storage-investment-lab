#!/bin/bash
# Draait het model op echte Energy-Charts-data voor elk jaar en bewaart de uitkomst per jaar.
source .venv/bin/activate
mkdir -p resultaten
for YEAR in $(seq 2015 2026); do
  echo "=== $YEAR gestart $(date) ===" | tee -a resultaten/log.txt
  rm -f data/eti.db
  if make run-live YEAR=$YEAR >> resultaten/log.txt 2>&1; then
    mkdir -p resultaten/$YEAR
    cp -r reports/* resultaten/$YEAR/
    echo "$YEAR klaar" | tee -a resultaten/log.txt
  else
    echo "$YEAR MISLUKT, zie log" | tee -a resultaten/log.txt
  fi
  sleep 30
done
echo "=== Alles klaar $(date) ===" | tee -a resultaten/log.txt
