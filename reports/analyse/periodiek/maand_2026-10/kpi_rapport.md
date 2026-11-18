# KPI-rapport impactbeleggen in zon en opslag: okt 2026

| | |
|---|---|
| Rapport | maand (maand, kwartaal of jaar) |
| Periode | okt 2026, vergeleken met okt 2025 |
| Data tot en met | 15-11-2026 09:00 UTC |
| Opgesteld door | eti.rapport_auto op 18-11-2026 |
| Bron | `powerbi/data`, gemaakt met `eti.rapport_auto` |

## Scorekaart

Status: 🟢 op koers, 🟡 let op, 🔴 actie nodig. De regels staan in de bijlage.

| # | Kerncijfer | Waarde | Norm | Vorige periode | Verschil | Status |
|---|---|---|---|---|---|---|
| 1 | Dagmarktprijs (euro per MWh) | 172 | 103 (12 maanden ervoor) | 82 | +109% | 🟡 let op |
| 2 | Capture rate zon | 0,78 | 0,91 (vorig jaar) | 0,91 | -14 punten | 🔴 actie nodig |
| 3 | Marge zon (euro per MWh) | 70 | vanaf 5 | 8 | +62 | 🟢 op koers |
| 4 | Batterij, dagmarkt (euro per MW) | 5.814 | 7.124 (8%) | 4.098 | +42% | 🔴 actie nodig |
| 5 | Negatieve uren | 16 | hooguit 46 | 46 | -30 | 🟢 op koers |
| 6 | Zonopwek in negatieve uren (%) | 1,7 | onder 5 | 1,8 | -0,0 punten | 🟢 op koers |
| 7 | Vermeden CO2, modelpark (ton per jaar) | 3.750 (2025) | minstens 3.616 | 3.616 | +4% | 🟢 op koers |
| 8 | Versheid van de data (dagen) | 3,1 | hooguit 2 | | | 🟡 let op |

**Samengevat:** 4 groen, 2 geel, 2 rood.

## Per kerncijfer

### 1. Dagmarktprijs
- Trend: +109% tegenover okt 2025; 3,5 standaardafwijkingen van het gemiddelde van de twaalf maanden ervoor
- Context: een afwijking boven 2 standaardafwijkingen wijst op een schok (gas, weer) en vertekent vergelijkingen met vorig jaar
- Grafiek: `1_markt_prijs.png`

### 2 en 3. Zon: capture rate en marge
- Trend: capture rate 0,78 (-14 punten); zon ontving 134 euro per MWh bij kosten van 64 euro
- Context: de capture rate is seizoensgebonden: vergelijk met dezelfde maand vorig jaar, niet met de vorige maand
- Grafiek: `2_zon.png`

### 4. Opslag
- Trend: 5.814 euro per MW (+42%); dagspreiding 168 euro per MWh
- Context: voor 8% rendement is 7.124 euro per MW per maand nodig, voor 5% 6.118; zonder balanceringsmarkten en netkosten
- Grafiek: `3_opslag.png`

### 5 en 6. Negatieve uren
- Trend: 16 uren (was 46); 1,7% van de zonopwek viel in die uren
- Context: negatieve uren vallen vooral van april tot en met augustus

### 7. Impact
- Trend: 3.750 ton in 2025 (+4% tegenover het jaar ervoor)
- Context: jaarcijfer van het modelpark, per uur berekend; wordt een keer per jaar ververst

### 8. Datakwaliteit
- laatste meting 3,1 dagen oud; maand met 744 uren

## Toelichting

(nog in te vullen door de analist)

*Ruimte voor de analist: wat verklaart de rode en gele kerncijfers, wat is eenmalig, wat is nieuw ten opzichte van het vorige rapport.*

## Acties

| # | Actie | Aanleiding | Eigenaar | Termijn | Stand |
|---|---|---|---|---|---|
| 1 | Marktwaarde van zon in de modellen bijstellen naar de laatste twaalf maanden | kerncijfer capture staat op rood | | | open |
| 2 | Batterijcase toetsen op de inkomsten naast de dagmarkt en op netkosten | kerncijfer batterij staat op rood | | | open |
| 3 | Lopende waarderingen herzien met de huidige prijs als schok, niet als nieuw normaal | kerncijfer prijs staat op geel | | | open |
| 4 | Ophaalscripts controleren; de data loopt achter | kerncijfer vers staat op geel | | | open |

## Bijlage: definities en rekenwijze

| Kerncijfer | Definitie | Berekening | Groen | Geel | Rood |
|---|---|---|---|---|---|
| Dagmarktprijs | Gemiddelde Nederlandse dagmarktprijs over alle uren van de periode | som van de uurprijzen gedeeld door het aantal uren | binnen 2 standaardafwijkingen van de 12 maanden ervoor | 2 tot 4 | meer dan 4 |
| Capture rate zon | Prijs die zon ontvangt gedeeld door de gemiddelde prijs | som (prijs × zonopwek) / som (zonopwek) / gemiddelde prijs | hoger dan of gelijk aan dezelfde periode vorig jaar | tot 5 punten lager | meer dan 5 punten lager |
| Marge zon | Wat zon per MWh ontvangt min de kosten per MWh van een nieuw park | capture-prijs min LCOE uit `fact_regio_jaar` | vanaf 5 euro | 0 tot 5 euro | onder nul |
| Batterij, dagmarkt | Omzet van een batterij van 2 uur per MW, plan op de prijzen van gisteren, verliesdagen overgeslagen | som van de dagwinsten; zonder netkosten en balancering | boven het bedrag voor 8% rendement | tussen 5% en 8% | onder het bedrag voor 5% |
| Negatieve uren | Aantal uren met een prijs onder nul | telling | niet hoger dan vorig jaar | tot 25% hoger | meer dan 25% hoger |
| Zonopwek in negatieve uren | Deel van de zonopwek dat in uren met een negatieve prijs valt | zonopwek in negatieve uren / totale zonopwek | onder 5% | 5 tot 15% | boven 15% |
| Vermeden CO2 | Vermeden uitstoot van het modelpark van 10 MW, per uur berekend | `fact_nl_jaar.co2_vermeden_uur` | gelijk aan of hoger dan vorig jaar | tot 10% lager | meer dan 10% lager |
| Versheid | Dagen tussen de laatste meting en de rapportdatum | rapportdatum min laatste tijdstip | tot 2 dagen | 3 of 4 dagen | meer dan 4 dagen |

Het bedrag voor 8% en 5% rendement volgt uit een investering van 560 euro per kW, 15 jaar, 2% degradatie en 2%
beheerkosten: 85.500 en 73.400 euro per MW per jaar, naar rato voor een maand of kwartaal.
