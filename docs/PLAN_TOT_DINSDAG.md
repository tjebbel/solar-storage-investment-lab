# Planning: alle openstaande dashboards af uiterlijk dinsdag 1 december 2026

Uitgangspunt: één uur bouwtijd per dashboard, plus 15 minuten voor publiceren, live controle en scoren
in `docs/ontwerp_beoordeling.md`. Doel: 16 van 20 of hoger. Commit pas na opdracht van Tjebbe.

## Wat erin zit

Alleen dashboards waarvan de data al klaarstaat (status "data ready" in de README):

| Volgorde | Dag | Dashboard | Titel (werktitel) | Bron |
|---|---|---|---|---|
| 1 | do 26 nov (middag) | 18 | Storage saturation: batterijen verzadigen | t71 / arbitrage |
| 2 | vr 27 nov | 32 | LCOE per country: wat zon echt kost | t92, t93 |
| 3 | vr 27 nov | 6 | Profit pool along the value chain | Bain, fabrikanten 2025 |
| 4 | za 28 nov | 28 | Europe's future is in California and South Australia | t68, t69 |
| 5 | za 28 nov | 30 | Forecasting showcase: eenvoudig model vs. gisteren | t73 to t75 |
| 6 | zo 29 nov | 9 | EU: price convergence | EU-data |
| 7 | zo 29 nov | 13 | Grid operator: flexibility and EVs | TSO/DSO |
| 8 | ma 30 nov | 10 | United States: tax credits and the build-out | US-data |
| 9 | ma 30 nov | 11 | China: market prices and the build wave | China-data |
| Buffer | di 1 dec | Footers 1, 3, 4; dashboard 15 live controleren; README, PLAN en scores bijwerken; memo eindcheck | | |

## Buiten deze planning (data of literatuur ontbreekt)

- 12 NGFS: wacht op regio- en prijsreeksen.
- 21 t/m 24: bronnen nog niet gedownload.
- 33 t/m 36: nog geen data (IEA, ENTSO-E, TenneT, rooftop-profiel).
- 40, 41, 44: literatuur, zie `docs/literatuur_en_keuzes.md`.
- 31: wacht op Fabric-toegang (laatste).

## Werkwijze per dashboard (1 uur)

1. Bronbestand controleren en `tableau/data_en/` verversen (Verbinding bewerken, geen Cmd+R op het .twbx).
2. KPI-rij dupliceren van het dichtstbijzijnde gepubliceerde dashboard; hoofdgrafiek; onderrand met bronnen.
3. Geen "Next"-regel. Elke titel krijgt een ondertitel. Kleurcodes met kleurnaam. Nederland oranje `E39A2D`.
4. Publiceren; link naar Claude voor live controle in de ingebouwde browser; score loggen.

## Risico's

- Eén uur per dashboard is krap. Dashboards die onder 16 scoren, krijgen een korte herstelronde op di 1 dec.
- Dashboards 6 en 9 en 10 hebben de meeste bronwerk; als dat uitloopt, schuift 11 naar di 1 dec.
