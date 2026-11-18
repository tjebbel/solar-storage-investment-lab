# Power BI-dashboard bouwen (iMac, via Microsoft Fabric in de browser)

Power BI Desktop draait niet op macOS. Op de iMac bouw je het rapport in de browser via Microsoft Fabric
(app.fabric.microsoft.com, gratis proefversie). Alle data staat klaar in `powerbi/data/` en komt uit
hetzelfde model als het memo (`python -m eti.powerbi` maakt de bestanden opnieuw).

## 1. Data laden (15 min)
1. Fabric → nieuwe werkruimte "Energy Investment" → Nieuw → **Lakehouse** `eti_lakehouse`.
2. Files → Uploaden → alle CSV's uit `powerbi/data/`.
3. Per bestand: rechtsklik → **Load to Tables** (nieuwe tabel, zelfde naam).
4. Lakehouse → **New semantic model** → selecteer alle tabellen.

## 2. Model (10 min)
- Relatie: `dim_regio[regio]` 1 → * `fact_regio_jaar[regio]`.
- Overige tabellen staan los (het zijn modeluitkomsten op één project); geen relaties nodig.
- Zet `fact_markt_uur[timestamp_utc]` op type Datum/tijd, percentages (irr, wacc) op Percentage.

## 3. Maten (15 min)
Open het model → Nieuwe meting → plak de maten uit `measures.dax` één voor één.
Maak de what-if-parameter **CO2-prijs** (0–200 €/t).

## 4. Vier rapportpagina's (60–90 min)
| Pagina | Visuals |
|---|---|
| Markt | kaarten Capture rate, Negatieve uren, Gem prijs; matrix maand × uur met Gem prijs (voorwaardelijke opmaak = heatmap); lijn Capture rate per maand |
| Investering | kaarten IRR voor/na belasting, LCOE, Kans onder hurdle; lijn `fact_capture_curve` (capture_rate × irr) met constante lijn 8%; staaf `fact_erosie`; staaf `fact_klimaatscenario` (npv) |
| Fonds en wereldbeelden | lijn `fact_jcurve`; tabel `fact_wereldbeeld` |
| Regio's 2025–2050 | kaartvisual of staaf LCOE regio per jaar; spreiding Impact per € mln (x) tegen LCOE regio (y), legenda regio; slicer jaar; kaart Impactwaarde met CO2-prijs-slider |

## 5. Controle
De kaarten moeten exact deze waarden tonen (zelfde als memo): IRR zon voor belasting 7,2%, na belasting 5,5%,
LCOE 76,5 €/MWh, capture rate 0,79, break-even capture 0,83, negatieve uren 156.

Let op: de maten zijn geschreven maar niet in Power BI zelf getest; wijkt een kaart af, controleer eerst
datatypes (decimaalteken!) en of de visual geen ongewenst filter heeft.

## Pagina "Mondiale context" (Ember)
Laad: fact_ember_prijs_maand, fact_ember_opwek_jaar, fact_ember_zon_import, fact_land_profiel_uur, fact_ntc.
1. **Lijndiagram prijs** – X: fact_ember_prijs_maand[datum], Y: gemiddelde prijs, Legenda: iso3. Filter iso3 = NLD, DEU, ESP, FRA, POL; datum ≥ 2019.
2. **Lijndiagram zonaandeel** – fact_ember_opwek_jaar, filter Electricity source = "Solar", ISO 3 code in NLD/ESP/DEU/CHN/USA/IND. X: Year, Y: Share of generation (%).
3. **Lijndiagram paneelprijs** – fact_ember_zon_import, filter Commodity type = "Panels" en Commodity price tussen 0,03 en 1. X: Date (kwartaal), Y: meting [Paneelprijs mediaan].
4. **Lijndiagram NL netto-positie** – fact_land_profiel_uur, filter land = "Netherlands". X: uur, Y: net_p, Legenda: jaar.
5. **Kaarten (KPI)** – [NTC NL 2024], [NTC NL 2040 Needs], [Zonaandeel NL laatste jaar].
6. Slicer op jaar/scenario; titel: "Waar staat NL mondiaal — en wanneer is het batterijvenster het breedst?"

## Pagina "Europa in 36 zones"
Laad: fact_land_jaar, fact_flex_land, fact_tech_land, fact_onzekerheid_land, fact_kwartier_batterij, dim_markt (koppel dim_markt[markt] aan [land] in elke tabel).
1. **Staafdiagram capture rate** – fact_land_jaar, Y: land, X: capture_zon, slicer op jaar (standaard 2025). Constante lijn op 0,83 (break-even NL).
2. **Spreidingsdiagram** – X: dagspreiding, Y: fact_flex_land[omzet_realistisch_per_mw] (filter uren_opslag = 2), details: land. Laat zien: spreiding bepaalt batterij-omzet.
3. **Gegroepeerde staven batterij** – fact_flex_land, uren_opslag = 2, X: omzet_realistisch_per_mw, Y: land, legenda: jaar (2025, 2026).
4. **Lijn met band** – fact_onzekerheid_land, land = Nederland: capture_p10/p50/p90 per jaar (lijndiagram met foutbalken of drie lijnen).
5. **Tabel zon vs wind** – fact_tech_land: land, technologie, capture_price, irr_merchant (voorwaardelijke opmaak rood < 0, groen > 8%).
6. **Kaart kwartier-uplift** – fact_kwartier_batterij[uplift] per land.
7. **Tabel verbanden** – fact_verbanden (rangcorrelaties per paar) en fact_paneel_kannibalisatie (capture rate op zonaandeel, met land- en jaareffecten). Beide komen uit `python -m eti.verbanden`.
8. **Tabel buurlanden** – fact_ruimtelijk_paneel: capture rate op eigen zonaandeel en het zonaandeel van de buurlanden (gewogen met handelscapaciteit), standaardfouten geclusterd per land. Komt uit `python -m eti.ruimtelijk`.
9. **Tabel kernenergie** – fact_kernenergie_land_jaar: land, jaar, aandeel_kern, capture_kern naast capture_zon, aandeel_in_negatieve_uren, productie_bij_negatieve_prijs (1 = geen terugregelen) en daguitslag_mediaan. fact_kernenergie_verband geeft de rangcorrelaties met dagspreiding, batterij-omzet, capture rate zon en negatieve uren. Beide komen uit `python -m eti.kernenergie`; voor Belgie is benutting_tov_vermogen niet bruikbaar (het opgestelde vermogen in de bron loopt voor op de sluitingen).

## Pagina "Wereld"
Laad: fact_australie, fact_instraling_wereld, fact_studieregio_jaar, dim_land, fact_worldbank, fact_owid_co2.
1. **Lijndiagram Australië** – capture_zon_instraling per jaar, legenda: regio.
2. **Lijndiagram batterij Australië** – batterij_2u_realistisch_eur_per_mw per jaar (lokale dagen; toont de halvering in 2026).
   Ernaast uit fact_australie_dagprofiel (januari–oktober per jaar): mediaan_avondprijs_eur_mwh en mediaan_middagprijs_eur_mwh, legenda regio. De avondpiek zakt, het middagdal niet.
3. **Staafdiagram vollasturen** – fact_instraling_wereld: gemiddelde vollasturen_schatting per locatie.
4. **Lijndiagram CO2-intensiteit** – fact_studieregio_jaar: intensiteit_g_kwh per Year, legenda: studieregio.
5. Slicer studieregio (uit dim_land) die op alle Ember-tabellen werkt.

## Pagina "Herijking en batterij" (november 2026)
Laad: fact_batterij_stapeling, fact_herijking, fact_onbalans_nl, fact_wereld_markten, fact_gas_henryhub.
1. **Gegroepeerde kolommen** – fact_batterij_stapeling: X jaar, Y omzet_per_mw, legenda strategie. Toon standaard vier strategieen: Dagmarkt, Onbalans op dagmarktplan, Gestapeld vooraf (onbalans op dagmarktplan) en Onbalans perfect. De IRR per bouwkostenniveau staat in fact_batterij_irr; kwartierprijzen voor tekort en overschot staan in fact_onbalans_nl.
2. **Lijndiagram zon** – fact_herijking: X jaar, Y irr_voor_belasting, legenda vollasturen; constante lijn op 8%.
3. **What-if-parameter "Capex per MWh"** (200.000–350.000, stap 25.000) en meting [IRR batterij indicatief] = (omzet − 2% × capex) / capex als eenvoudige cash yield; de exacte IRR staat in het memo (hoofdstuk Herijkt basismodel).
4. **Tabel wereldmarkten** – fact_wereld_markten: markt, jaar, gem_prijs_eur, capture_zon_instraling, negatieve_uren.
5. **Lijndiagram gas** – fact_gas_henryhub: datum (maand), gemiddelde usd_mmbtu.
6. **Tabel onbalansregel** – fact_onbalans_regel: filter regel = "Dagmarkt met bijsturen", vertraging_kwartieren = 1 en vooraf_gekozen = waar. Kolommen jaar, omzet_per_mw, dagmarkt_per_mw, waarvan_onbalans_per_mw. Toont dat bijsturen op onbalans zonder kennis vooraf steeds minder toevoegt. Komt uit `python -m eti.onbalansregel`.
7. **Tabel volledige case** – fact_batterij_volledige_case: inkomsten, netaansluiting, omzet_per_mw, netkosten_per_mw, irr (leeg = geen terugverdientijd). Bronwaarden voor bouwkosten, netkosten en stapeling; komt uit `python -m eti.volledige_case`.
8. **Lijndiagram verzadiging** – fact_wereld_markten: batterij_2u_realistisch_eur_per_mw per jaar, legenda markt (Californie en Texas vanaf 2020; Texas 2025 loopt tot 24 juni). Vergelijk gelijke perioden met fact_vs_halfjaar (1 januari tot en met 24 juni). Herkomst: reports/vs_eia_herkomst.json.
9. **Tabel balancering** – fact_balans_nl_jaar: per jaar de FCR-prijs (mediaan en gemiddelde, euro per MW per uur), de omzet van 1 MW bij volledige inzet in FCR en de aFRR-energieprijzen op en af. Detail: fact_fcr_nl (prijs per blok) en fact_afrr_energie_nl (per kwartier, tot en met september 2025). De capaciteitsprijs van aFRR ontbreekt. Komt uit `python -m eti.balans`.
10. **Tabel opwek VS** – fact_vs_opwek_jaar: markt, jaar, brandstof, twh, aandeel_opwek, capture_rate, aandeel_in_negatieve_uren, hoogste_uur_mw. De hoogste uurwaarde van BAT (Texas) en OTH (Californie) is een maat voor het batterijvermogen. Komt uit de stap eia_opwek.
