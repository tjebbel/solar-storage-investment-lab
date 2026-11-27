# Planning: alle dashboards met data af voor zondagavond 29 november 2026

Uitgangspunt van Tjebbe: een uur bouwtijd per dashboard, plus een kwartier voor publiceren, live controle en scoren
(`docs/ontwerp_beoordeling.md`, doel 16 van 20 of hoger). Twintig dashboards is ongeveer 25 uur over drie dagen.
Commit pas na opdracht.

Volgorde: wat op LinkedIn het meest aanspreekt eerst (herkenbaar, actueel, een sterk beeld); valt er iets af, dan van onderen.
KPI-tegels (t50) staan klaar voor alle dashboards. Stappen voor de eerste drie: `tableau/STAPPENPLAN_WEEKEND.md`.

| Dag | Dashboard | Onderwerp | Waarom hier | Tabel |
|---|---|---|---|---|
| gedaan do 26 nov | 18 | Storage saturation (18 van 20) | | t55 |
| gedaan vr 27 nov | 36 | Nederland na de salderingsregeling (18 van 20) | raakt elk huishouden met panelen; stopt 1 januari 2027 | t101, t90 |
| gedaan vr 27 nov | 28 | Europa's toekomst in Californie en Zuid-Australie (18 van 20) | een beeld dat in een oogopslag werkt | t68, t69 |
| gedaan vr 27 nov | 23 | Energiearmoede per gemeente (17 van 20) | iedereen zoekt de eigen gemeente op | t88, t97 |
| vr 27 nov | 41 | Netkosten per land | de eigen energierekening; verdubbeld sinds 2019 | t96 |
| vr 27 nov | 42 en 35 | Wachtrijen: Europa en Nederland | netcongestie is dagelijks nieuws | t95, t89 |
| vr 27 nov | 24 | Waterstof: aangekondigd tegenover gebouwd | 4% wordt gebouwd: tegen de verwachting in | t102 |
| vr 27 nov | 21 | Grondstoffen: zilver, koper, aluminium | zilver 3,7 keer januari 2019 | t100 |
| za 28 nov | 6 | Profit pool langs de waardeketen | wie verdient er aan zonnepanelen | t60 |
| za 28 nov | 38 | Zon verliest, batterijen winnen | bevinding 5 van de memo | t78, t79 |
| za 28 nov | 30 | Prognosemodel en de waarde in euro's | vaardigheid als data-analist | t73 tot t75, t80 |
| za 28 nov | 32 | LCOE per land, twee methoden | draagt de memo; vakpubliek | t92, t93 |
| za 28 nov | 39 en 33 | Kapitaalkosten per land | bevinding 3 van de memo; vakpubliek | t82, t85, t87 |
| za 28 nov | 40 | Subsidie per vermeden ton | vakpubliek | t94, t13 |
| za 28 nov | 10 | Verenigde Staten | regio; actueel door het belastingbeleid | t21, t33 tot t36 |
| zo 29 nov | 11 | China | regio | t20, t22 |
| zo 29 nov | 43 | Ervaringscurve per land | aanvulling op dashboard 4 | t11, t93 |
| zo 29 nov | 9 | EU-prijsconvergentie | regio | t18 |
| zo 29 nov | 13 | Netbeheer: flexibiliteit en elektrische auto's | overlapt deels met 42 | t25, t26 |
| zo 29 nov | 22 | Banen in hernieuwbare energie | dunne data (11 rijen) | t91 |
| zo 29 nov | 12 | NGFS-scenario's per werelddeel | geen Europa apart, een model | t99 |
| zo 29 nov | herstel | Dashboards onder 16; onderrand 1, 3 en 4; dashboard 15 live controleren; README en scores | | |

## Niet in het weekend
- 37: staat al als blad `ppa2030` op dashboard 17.
- 44: de kosten per ontlaadduur ontbreken (het PNNL-werkboek is een lege rekenmal); alleen de ervaringscurves (t98) zijn er.
- 34: grensstromen, eerst een controle tegen ENTSO-E.
- 31: wacht op Fabric-toegang.

## Vaste werkwijze per dashboard
1. Bron verbinden via Verbinding bewerken naar `tableau/data_en/<tabel>.csv` (geen Cmd+R op het .twbx).
2. KPI-rij dupliceren; hoofdgrafiek; twee ondersteunende grafieken; onderrand met bronregel.
3. Geen "Next"-regel. Elke titel een ondertitel. Kleurcode met kleurnaam. Nederland oranje `E39A2D`.
4. Publiceren, link sturen, live controle en score.

## Kanttekeningen bij de data
- t94 (PBL): de 23 waarden zijn twee keer uit de pdf gelezen en gelijk. De erratalijst van 10 juli 2026 meldt dat de
  overzichtstabellen 3.2 tot 3.24 opnieuw zijn gepubliceerd vanwege de kolom langetermijnprijs. Gebruik op het dashboard
  alleen de subsidie-intensiteit, niet het basisbedrag of de langetermijnprijs, tot de pdf met de hand is nagelezen.
- t96 (Eurostat): belastingen zijn in 20 rijen negatief door tijdelijke kortingen (Nederland 2021 tot 2025). Gebruik daarom
  `Network share of energy plus network pct` voor vergelijkingen, niet `Network share pct`.
- t95 (wachtrijen): definities verschillen per land; niet optellen en de peildatum tonen.
- t99 (NGFS): vijf werelddelen, een model; staat niet op GitHub. Licentie lezen voor publicatie op Tableau Public.
- t102 (waterstof): 164 Mt per jaar "aangekondigd" telt ook projecten zonder startjaar (71 Mt) en na 2030 (38 Mt). Tot en met 2030 is het 61 Mt; dat is niet tegen het IEA-rapport gecontroleerd.
