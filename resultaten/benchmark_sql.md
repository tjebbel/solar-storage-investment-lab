# SQLite en SQL Server op dezelfde machine

Maand 2025-06, mediaan van 5 rondes na een opwarmronde.

| systeem                               | query        |   rijen |   mediaan_ms |   min_ms |   max_ms |   herhalingen |   keer_trager_dan_snel |
|:--------------------------------------|:-------------|--------:|-------------:|---------:|---------:|--------------:|-----------------------:|
| SQLite 3.48.0                         | traag        |      30 |     14232.4  | 14150.7  | 18408.4  |             5 |               56571.4  |
| SQLite 3.48.0                         | snel         |      30 |         0.25 |     0.24 |     0.26 |             5 |                   1    |
| SQLite 3.48.0                         | voorberekend |      30 |         0.09 |     0.09 |     0.13 |             5 |                   0.36 |
| SQL Server 2022 (Docker, linux/amd64) | traag        |      30 |     35903    | 34980    | 37863    |             5 |                2991.92 |
| SQL Server 2022 (Docker, linux/amd64) | snel         |      30 |        12    |     8    |    14    |             5 |                   1    |
| SQL Server 2022 (Docker, linux/amd64) | voorberekend |      30 |         1    |     0    |     2    |             5 |                   0.08 |
