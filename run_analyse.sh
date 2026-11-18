#!/bin/bash
# Draait alle analysepakketten in de goede volgorde en daarna de tests. Duurt ongeveer drie minuten.
# Gebruik: bash run_analyse.sh      (eerst: pip install -r requirements-analyse.txt)
set -u
# Eigen omgeving van het project, rechtstreeks aangeroepen. Niet via source .venv/bin/activate: na het verplaatsen van de
# repo wijst dat script nog naar de oude map op het Bureaublad, en dan draait alles zonder pandas en numpy.
PY=python3
if [ -x .venv/bin/python ] && .venv/bin/python -c "import pandas, numpy" 2>/dev/null; then PY="$PWD/.venv/bin/python"; fi
echo "Python: $PY"
export PYTHONPATH=src
mkdir -p resultaten
LOG=resultaten/analyse_log.txt
: > "$LOG"
stap() { echo "== $* ==" | tee -a "$LOG"; "$@" 2>&1 | tail -25 | tee -a "$LOG"; echo "   klaar: $(date '+%H:%M:%S')" | tee -a "$LOG"; }
[ -d data/raw ] && stap "$PY" -m eti.vs_dag          # dagtabel Texas en Californie uit de bewaarde uurbestanden (alleen waar data/raw staat)
stap "$PY" -m eti.zonprofiel
stap "$PY" -m eti.da
stap "$PY" -m eti.woordenboek
stap "$PY" -m eti.sa
stap "$PY" -m eti.prognose
stap "$PY" -m eti.vis
stap "$PY" -m eti.rapport_grafieken
stap "$PY" -m eti.sql_run
stap "$PY" -m eti.kwaliteit
stap "$PY" -m eti.ml_pijplijn
stap "$PY" -m eti.rapport_auto alles
stap "$PY" src/eti/analyse_script.py
stap "$PY" -m eti.verzadiging_gw
stap "$PY" -m eti.gas
stap "$PY" -m eti.stapel
stap "$PY" -m eti.powerbi_toets
stap "$PY" -m eti.bronnen_toets             # vervolg 18 november: zon achter de meter en dekkingsgaten
stap "$PY" -m eti.segment_gevoeligheid
stap "$PY" -m eti.batterij_bronnen
stap "$PY" -m eti.batterij_irr
stap "$PY" -m eti.schokjaar
stap "$PY" -m eti.tableau_export          # vijf platte tabellen voor het Tableau-dashboard
stap "$PY" -m eti.kern_wereld              # derde dashboard: kernenergie in Europa en de wereld (t6-t8)
stap "$PY" -m eti.signalering_europa       # tweede dashboard: signalering alle zones, dekking NL (t9-t10)
stap "$PY" -m unittest discover -s tests
echo "Logboek: $LOG"
