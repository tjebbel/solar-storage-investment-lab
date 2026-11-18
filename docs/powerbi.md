# Using the outputs in Power BI / Microsoft Fabric

1. Run `make run`. The folder `reports/` contains `results.json` and `monthly_capture_rate.csv`.
2. Power BI (web or Desktop): Get data → Text/CSV → `monthly_capture_rate.csv`.
3. In Fabric: upload the CSV files to a Lakehouse (Files), load them as Delta tables, and build
   a semantic model in Direct Lake mode.
4. Suggested report page: title as conclusion, KPI cards (capture rate, solar IRR, portfolio IRR,
   probability below hurdle), line chart of monthly capture rate with a reference line at 1.0.
