# KPI-rapport impactbeleggen in zon en opslag: {{periode}}

| | |
|---|---|
| Rapport | {{soort}} (maand, kwartaal of jaar) |
| Periode | {{periode}}, vergeleken met {{vergelijkperiode}} |
| Data tot en met | {{data_tot}} |
| Opgesteld door | {{auteur}} op {{datum_opgesteld}} |
| Bron | `powerbi/data`, gemaakt met `eti.rapport_auto` |

## Scorekaart

Status: 🟢 op koers, 🟡 let op, 🔴 actie nodig. De regels staan in de bijlage.

| # | Kerncijfer | Waarde | Norm | Vorige periode | Verschil | Status |
|---|---|---|---|---|---|---|
| 1 | Dagmarktprijs (euro per MWh) | {{prijs}} | {{prijs_norm}} | {{prijs_vorig}} | {{prijs_verschil}} | {{prijs_status}} |
| 2 | Capture rate zon | {{capture}} | {{capture_norm}} | {{capture_vorig}} | {{capture_verschil}} | {{capture_status}} |
| 3 | Marge zon (euro per MWh) | {{marge}} | {{marge_norm}} | {{marge_vorig}} | {{marge_verschil}} | {{marge_status}} |
| 4 | Batterij, dagmarkt (euro per MW) | {{batterij}} | {{batterij_norm}} | {{batterij_vorig}} | {{batterij_verschil}} | {{batterij_status}} |
| 5 | Negatieve uren | {{negatief}} | {{negatief_norm}} | {{negatief_vorig}} | {{negatief_verschil}} | {{negatief_status}} |
| 6 | Zonopwek in negatieve uren (%) | {{zonneg}} | {{zonneg_norm}} | {{zonneg_vorig}} | {{zonneg_verschil}} | {{zonneg_status}} |
| 7 | Vermeden CO2, modelpark (ton per jaar) | {{co2}} | {{co2_norm}} | {{co2_vorig}} | {{co2_verschil}} | {{co2_status}} |
| 8 | Versheid van de data (dagen) | {{vers}} | {{vers_norm}} | | | {{vers_status}} |

**Samengevat:** {{aantal_groen}} groen, {{aantal_geel}} geel, {{aantal_rood}} rood.

## Per kerncijfer

### 1. Dagmarktprijs
- Trend: {{prijs_trend}}
- Context: {{prijs_context}}
- Grafiek: `1_markt_prijs.png`

### 2 en 3. Zon: capture rate en marge
- Trend: {{capture_trend}}
- Context: {{capture_context}}
- Grafiek: `2_zon.png`

### 4. Opslag
- Trend: {{batterij_trend}}
- Context: {{batterij_context}}
- Grafiek: `3_opslag.png`

### 5 en 6. Negatieve uren
- Trend: {{negatief_trend}}
- Context: {{negatief_context}}

### 7. Impact
- Trend: {{co2_trend}}
- Context: {{co2_context}}

### 8. Datakwaliteit
- {{kwaliteit_samenvatting}}

## Toelichting

{{toelichting}}

*Ruimte voor de analist: wat verklaart de rode en gele kerncijfers, wat is eenmalig, wat is nieuw ten opzichte van het vorige rapport.*

## Acties

| # | Actie | Aanleiding | Eigenaar | Termijn | Stand |
|---|---|---|---|---|---|
{{acties}}

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
