#!/bin/bash
# Test op de Mac zelf: bibliotheken in .venv, ontbrekende capture rates aanvullen, alle pakketten en tests draaien,
# het R-script proberen en de verkenner starten.
# Gebruik: bash test_op_mac.sh        (of in VS Code: Terminal > Run Task > "Analyse: test op de Mac")
# Verslag: resultaten/mac_test.txt. De verkenner blijft daarna draaien op http://localhost:8501 tot je de terminal sluit.
cd "$(dirname "$0")" || exit 1
mkdir -p resultaten
L=resultaten/mac_test.txt
{
  echo "== start $(date '+%F %T') op $(uname -sm) =="
  if [ -x .venv/bin/python3 ]; then source .venv/bin/activate; else echo "geen werkende .venv gevonden: de standaard-Python wordt gebruikt"; fi
  export PYTHONPATH=src
  python3 --version
  echo "== 1. bibliotheken =="
  if python3 -m pip install -q -r requirements-analyse.txt; then echo "installatie: ok"; else echo "installatie: MISLUKT"; fi
  python3 -c "import pandas, numpy, scipy, sklearn, seaborn, streamlit, plotly; print('pandas', pandas.__version__, '| numpy', numpy.__version__, '| scipy', scipy.__version__, '| scikit-learn', sklearn.__version__, '| seaborn', seaborn.__version__, '| streamlit', streamlit.__version__, '| plotly', plotly.__version__)"
  echo "== 2. afgekeurde capture rates aanvullen met instraling (Open-Meteo) =="
  python3 -m eti.herstel zon_proxy 2>&1 | tail -12
  for m in kernenergie verbanden ruimtelijk regio_indeling; do python3 -W ignore -m eti.$m > /dev/null 2>&1 && echo "   $m: bijgewerkt" || echo "   $m: MISLUKT"; done
  echo "== 3. alle pakketten en tests =="
  bash run_analyse.sh > resultaten/mac_run.txt 2>&1
  grep -n "^Ran \|^OK\|^FAILED\|Traceback\|Error:" resultaten/mac_run.txt | tail -12
  echo "== 4. verkenner onder Streamlit, zonder browser =="
  python3 -m unittest tests.test_verken_streamlit 2>&1 | tail -6
  echo "== 5. R =="
  if command -v Rscript > /dev/null; then Rscript r/hypothesetoets.R 2>&1 | tail -40; else echo "Rscript niet gevonden: R staat niet op deze Mac"; fi
  echo "== klaar $(date '+%F %T') =="
} > "$L" 2>&1
echo "Verslag: $L. De verkenner start nu op http://localhost:8501 (stoppen: ctrl+C)."
python3 -m streamlit run src/eti/verken_app.py --server.headless true --server.address localhost --server.port 8501 --browser.gatherUsageStats false > resultaten/mac_verkenner.txt 2>&1
