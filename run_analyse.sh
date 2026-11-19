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
stap "$PY" -m eti.mck_kostencurve          # dashboard 5: kostencurve CO2-reductie (t13)
stap "$PY" -m eti.bcg_portefeuille         # dashboard 4: ervaringscurve en portefeuille (t11-t12)
stap "$PY" -m eti.overheden                # dashboards 9-11: convergentie, bouwgolf VS/China, staten, export (t18-t22)
stap "$PY" -m eti.net_flex                 # dashboard 13: flexibiliteit NL en elektrisch rijden (t25-t26)
stap "$PY" -m eti.impact_zuiden            # dashboards 14-15: impact en Mondiale Zuiden (t27-t28)
stap "$PY" -m eti.netcongestie            # dashboards 8 en 13: netcongestie capaciteitskaart (t29-t32)
stap "$PY" -m eti.vs_860m                 # dashboard 10: EIA-860M voorraad, toevoeging, staten, gepland (t33-t36)
stap "$PY" -m eti.cbs_hernieuwbaar        # dashboard 8 + toetsen: CBS hernieuwbaar, RES-regio, IEA-WACC, RVO-factor (t37-t41)
stap "$PY" -m eti.dashboard_extra         # dashboards 2-4: gebeurtenissen, kannibalisatie, kern/zon, leercurve, kwadrantuitleg (t42-t46)
stap "$PY" -m eti.dashboard1_revisie      # dashboard 1 revisie: KPI-tegels, rangorde, leesbare scenarios, top 10, segmentkleuren (t47-t49)
stap "$PY" -m eti.validatie_extern        # externe validatie: Modo, Enervis, ITRPV, Kamerstukken (t52); voor assurance
stap "$PY" -m eti.assurance_overzicht --tests  # dashboard 7 (C07 draait de tests mee): controlematrix en risicokaart (t15-t16), als laatste: leest t33, t37, t41
stap "$PY" -m eti.uurdata                 # dashboards 16, 18, 19, 20: uuranalyses uit data/raw (eerste keer ca. 5 min, daarna cache)
stap "$PY" -m eti.kpi_dashboards          # ontwerpnorm: KPI-tegels dashboards 2-5, 7-11, 13-15 (t50), na assurance
stap "$PY" -m eti.vertaal_en              # Engelse tabellen voor de Engelse dashboards (tableau/data_en), als laatste
stap "$PY" -m unittest discover -s tests
echo "Logboek: $LOG"
