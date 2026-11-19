"""Dashboard 7, in de traditie van de Big Four: controlematrix en risicokaart van het project.

Een readiness-beoordeling, geen accountantsverklaring. Elke controle heeft een doel, twee kanten die vergeleken worden,
een uitkomst en een status. Waar het kan wordt de uitkomst nu opnieuw berekend (live); anders staat de bron erbij.
  t15_controles.csv   controle-id, domein, doel, kant A, kant B, uitkomst, status, bron, opnieuw berekend (ja/nee)
  t16_risico.csv      risico, kans (1-3), impact (1-3), score, maatregel, dashboard  (uit het onzekerhedenregister)
Gebruik:  PYTHONPATH=src python3 -m eti.assurance_overzicht [--tests]   (--tests draait ook de hele testsuite)
"""
import os
import re
import subprocess
import sys

import pandas as pd

from . import signalering_europa

EMBER = "powerbi/data/fact_ember_opwek_jaar.csv"
EMBER_CAP = "powerbi/data/fact_ember_capaciteit_maand.csv"


def live_cbs_ember():
    s = pd.read_csv("tableau/data/t37_nl_stroom.csv")
    cbs = s[(s.Bron == "Zonnestroom") & (s.Jaar == 2025)]["Productie GWh"].iloc[0] / 1000
    o = pd.read_csv(EMBER)
    e = o[(o["ISO 3 code"] == "NLD") & (o["Electricity source"] == "Solar") & (o.Year == 2025)]["Generation (TWh)"].iloc[0]
    v = e / cbs - 1
    return (f"zonnestroom 2025: CBS {cbs:.1f} TWh (voorlopig), Ember {e:.1f} TWh, verschil {v:+.0%}; vermogen sluit wel aan (25,9 GW)",
            "Geslaagd" if abs(v) < 0.05 else "Afwijking open")


def live_eia_ember():
    v = pd.read_csv("tableau/data/t33_vs_voorraad.csv").set_index("Snapshot")
    c = pd.read_csv(EMBER_CAP)
    c = c[(c["ISO 3 Code"] == "USA") & (c.Source == "Solar")]
    c["Snapshot"] = c.Year.astype(str) + "-" + c.Month.astype(int).map("{:02d}".format)
    c = c.groupby("Snapshot")["Installed Capacity"].max()
    m = sorted(set(v.index) & set(c.index))[-1]
    return (f"zon VS {m}: EIA-860M {v.loc[m, 'Zon GW']:.0f} GW (AC, installaties vanaf 1 MW), Ember {c.loc[m]:.0f} GW "
            f"(DC, inclusief kleinschalig); verhouding {c.loc[m] / v.loc[m, 'Zon GW']:.2f}", "Afwijking verklaard")


def live_voorlopig():
    fout = []
    for t in ("t37_nl_stroom", "t38_nl_eindverbruik", "t39_vermeden_co2"):
        d = pd.read_csv(f"tableau/data/{t}.csv")
        if "Voorlopig" not in d or not d.loc[d.Jaar == 2025, "Voorlopig"].all():
            fout.append(t)
    return ("vlag Voorlopig aanwezig en 2025 overal gemarkeerd" if not fout else "ontbreekt in " + ", ".join(fout)), \
        ("Geslaagd" if not fout else "Afwijking")


def live_extern():
    v = pd.read_csv("tableau/data/t52_validatie_extern.csv")
    cr = v[v.Onderwerp.str.startswith("Capture rate") & ~v.Onderwerp.str.contains("Spanje")]
    es = v[v.Onderwerp.str.contains("Spanje")].iloc[0]
    c21 = (f"{(cr.Oordeel == 'sluit aan').sum()} van {len(cr)} capture rates binnen 0,03 van Modo/Enervis "
           f"(Duitsland 2022/2024/2025: {', '.join(f'{x:.2f}' for x in cr['Ons project'].head(3))})",
           "Geslaagd" if (cr.Oordeel == "sluit aan").all() else "Afwijking")
    c19 = (f"Spanje 2025: wij {es['Ons project']:.2f}, Synertics {es.Extern:.2f}; Modo noemt Duitsland en Spanje gelijk; definitie navragen",
           "Afwijking open")
    return c19, c21


def live_congestie():
    a = pd.read_csv("tableau/data/t51_congestie_afstemming.csv")
    tekst = "; ".join(f"{x.Wachtrij} {x['Ons project GW']} tegen {x['Officieel GW']} GW" for _, x in a.iterrows())
    return tekst + " (invoeding na correctie verschoven kolom)", ("Afwijking open" if (a.Status == "Afwijking open").any() else "Afwijking verklaard")


def live_toetsen():
    k = pd.read_csv("tableau/data/t41_toetsen.csv")
    m = k[k.Toets.str.startswith("Marginale")]["Referentie"]
    w = k[k.Toets.str.startswith("WACC")]
    em = (f"0,40 ligt in de band {m.min():.3f}-{m.max():.3f} (RVO 56,2 kg/GJ bij 50-58% rendement; CBS 0,455)",
          "Geslaagd" if m.min() <= 0.40 <= m.max() else "Afwijking")
    wa = ("eigen WACC hoger dan IEA 2021 behalve China; LCOE met IEA-WACC " +
          ", ".join(f"{r.Onderwerp.split(' ')[0]} {r['LCOE bij IEA-WACC']:.0f}" for _, r in w.iterrows()) +
          " EUR/MWh; 2021 was een lagerentejaar", "Afwijking verklaard")
    return em, wa


def live_dax():
    t2 = pd.read_csv("tableau/data/t2_land_maand.csv")
    goed, totaal = signalering_europa.controle(signalering_europa.bereken(t2))
    return f"{goed} van {totaal} waarden gelijk", "Geslaagd" if goed == totaal else "Afwijking"


def live_bronnen():
    b = pd.read_csv("powerbi/data/fact_bronnen_toets_RC.csv").set_index("groep")
    r = b.loc["alle landen"]
    return (f"mediane fout {r['mediane_fout_zonder_correctie']:.0%} -> {r['mediane_fout_met_correctie']:.0%} "
            f"na correctie, {r['aandeel_beter']:.0%} van {int(r['land_jaren'])} land-jaren beter"), "Geslaagd met beperking"


def live_tests():
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": "src"})
    uit = p.stderr + p.stdout
    ran = re.search(r"Ran (\d+) tests", uit)
    skip = re.search(r"skipped=(\d+)", uit)
    ok = p.returncode == 0
    return f"{ran.group(1) if ran else '?'} tests, {skip.group(1) if skip else 0} overgeslagen", "Geslaagd" if ok else "Afwijking"


def controles(tests=False):
    dax, dax_s = live_dax()
    br, br_s = live_bronnen()
    ts, ts_s = live_tests() if tests else ("tests niet gedraaid in deze run; gebruik --tests", "Open")
    ce, ce_s = live_cbs_ember()
    ee, ee_s = live_eia_ember()
    vl, vl_s = live_voorlopig()
    (em, em_s), (wa, wa_s) = live_toetsen()
    (c19, c19_s), (c21, c21_s) = live_extern()
    c20, c20_s = live_congestie()
    r = [
        ("C01", "Berekening", "Zelfde uitkomst in twee SQL-dialecten", "SQLite (Python)", "SQL Server 2022 (T-SQL)",
         "stappen 00-05 gelijk in aantallen en waarden", "Geslaagd", "reports/analyse/08_vervolg_18nov.md; log_tsql.txt", "nee"),
        ("C02", "Berekening", "Signaleringsmaten gelijk aan de verwachting", "Python (eti.signalering_europa)",
         "powerbi/maten_verwacht.csv (DAX-ontwerp)", dax, dax_s, "berekend bij deze run", "ja"),
        ("C03", "Berekening", "Tableau rekent hetzelfde als DAX en Python", "Tableau (werkblad Signalering)",
         "powerbi/maten_verwacht.csv", "nog uit te voeren met eti.powerbi_toets vergelijk", "Open", "bouwgids stap 10", "nee"),
        ("C04", "Berekening", "Power BI rekent hetzelfde", "Power BI / Fabric (DAX)", "powerbi/maten_verwacht.csv",
         "wacht op Fabric-toegang", "Open", "VOORTGANG.md", "nee"),
        ("C05", "Bronnen", "Zonaandeel in twee bronnen sluit aan", "Energy-Charts", "Ember",
         "82 sluiten aan, 34 dekkingsgaten, 66 wijken af; het verschil verdwijnt zonder dekkingsgaten",
         "Afwijking verklaard", "sql/05_reconciliatie.sql; t5", "nee"),
        ("C06", "Bronnen", "Correctiefactor werkt buiten de steekproef", "Correctie geschat op 2019-2022", "Ember 2023-2025",
         br, br_s, "fact_bronnen_toets_RC", "ja"),
        ("C07", "Code", "Testsuite slaagt", "tests/", "verwachte uitkomsten", ts, ts_s, "unittest", "ja" if tests else "nee"),
        ("C08", "Code", "Prestaties reproduceerbaar op een tweede machine", "Sandbox", "iMac (SQLite en Docker SQL Server)",
         "patroon gelijk; SQL Server-plan draaide de tweede keer serieel", "Geslaagd met beperking", "resultaten/benchmark_sql.md", "nee"),
        ("C09", "Gegevenskwaliteit", "Volledigheid kerncijfers per land", "Ember 2025", "verwacht: alle landen met kern",
         "Oekraine zonder 2025-cijfer; vermogen Belgie geeft benutting boven 100% (leeg gelaten)", "Afwijking verklaard",
         "eti.kern_wereld", "nee"),
        ("C10", "Gegevenskwaliteit", "Teken en dekking grensstromen", "fact_grensstromen_nl", "ENTSO-E/Ember jaarcijfers",
         "nog niet gecontroleerd; daarom niet gepubliceerd", "Open", "eti.net_flex", "nee"),
        ("C11", "Gegevenskwaliteit", "Twee bronnen voor de Chinese bouwgolf", "Ember capaciteit (mei 2025: 110,9 GW)",
         "NEA via OPIS (mei 2025: 92,9 GW)", "zelfde patroon, ander niveau; bron in subtitel vermelden", "Afwijking verklaard",
         "eti.overheden", "nee"),
        ("C12", "Rapportage", "Gepubliceerde cijfers gelijk aan de bron", "Tableau Public, dashboard 1", "t1-t5",
         "visueel gecontroleerd op 18-11 (kaart 2025: 0,50-0,89; referentielijn 280)", "Geslaagd", "sessie 18-11", "nee"),
        ("C13", "Bronnen", "Zonnestroom NL in twee bronnen", "CBS 82610NED", "Ember jaarcijfers", ce, ce_s,
         "berekend bij deze run", "ja"),
        ("C14", "Bronnen", "Zonvermogen VS in twee bronnen", "EIA-860M (t33)", "Ember maandcapaciteit", ee, ee_s,
         "berekend bij deze run", "ja"),
        ("C15", "Gegevenskwaliteit", "Betekenis statuscodes netcongestie", "congestie_pc6 (codes 0-3)",
         "legenda capaciteitskaart Netbeheer Nederland", "aanname RAGKind-volgorde; nog een postcode op de kaart opzoeken",
         "Open", "eti.netcongestie", "nee"),
        ("C16", "Rapportage", "Voorlopige cijfers zichtbaar", "CBS-tabellen t37-t39", "CBS-markering **", vl, vl_s,
         "berekend bij deze run", "ja"),
        ("C17", "Aannames", "WACC per regio tegen een externe bron", "eigen WACC (t27)", "IEA Cost of Capital Observatory",
         wa, wa_s, "t41", "ja"),
        ("C18", "Aannames", "Marginale emissiefactor tegen een externe bron", "0,40 t/MWh (t13)", "RVO-emissiefactor, CBS",
         em, em_s, "t41", "ja"),
        ("C19", "Bronnen", "Capture rate Spanje tegen een externe bron", "t1 (Energy-Charts)", "Synertics (2026)", c19, c19_s,
         "t52", "ja"),
        ("C20", "Gegevenskwaliteit", "Netcongestie-wachtrij tegen officiele cijfers", "capaciteitskaart 2026 (t29-t31)",
         "Kamerstukken / LAN", c20, c20_s, "t51", "ja"),
        ("C21", "Bronnen", "Capture rates tegen marktanalisten", "t1", "Modo Energy, Enervis", c21, c21_s, "t52", "ja"),
    ]
    return pd.DataFrame(r, columns=["Controle", "Domein", "Doel", "Kant A", "Kant B", "Uitkomst", "Status", "Bron",
                                    "Opnieuw berekend"])


def risico():
    r = [
        ("Segmentgrenzen zijn een keuze; 16-23 zones per jaar zijn grensgeval", 3, 2, "gevoeligheid tonen (+-20%)", "1, 4"),
        ("Capture rate Nederland: park (0,62) of dak (0,52)", 2, 3, "beide tonen; keuze per vraag", "1, 2, 8"),
        ("aFRR-capaciteitsprijs: twee ijkpunten (2022, 2026)", 3, 2, "tijdreeks ophalen", "1, 6"),
        ("LCOE alleen voor vijf regio's", 3, 2, "noord/zuid-aanname in subtitel; bandbreedte", "5, 14, 15"),
        ("Gemiddelde of marginale emissiefactor", 3, 3, "beide varianten tonen", "5, 7, 14"),
        ("Ember herziet cijfers achteraf", 2, 2, "downloaddatum vastleggen", "alle"),
        ("2026 is een onvolledig jaar (tot 15 november)", 3, 1, "in elke titel vermelden", "alle"),
        ("Paneelprijs is een exportwaarde, geen fabrieksprijs", 2, 2, "leersnelheid met interval tonen", "4"),
        ("Laadprofiel elektrische auto's is een aanname", 3, 1, "als scenario markeren", "13"),
        ("WACC voor Afrika onzeker", 3, 2, "als band tonen", "15"),
        ("Grensstromen: teken en dekking niet gecontroleerd", 2, 2, "eerst controleren (C10)", "9, 13"),
        ("Statuscodes netcongestie verkeerd gelezen", 2, 3, "een postcode op de kaart controleren (C15)", "8, 13"),
        ("AC en DC door elkaar (EIA tegenover Ember/CBS)", 3, 2, "eenheid in elke as en tooltip", "4, 10"),
        ("Vermeden CO2 (CBS) gelezen als emissiereductie", 2, 3, "apart tonen, niet verrekenen (GHG Protocol)", "5, 7, 14"),
        ("Zonnestroom NL: CBS en Ember verschillen ~10%", 2, 2, "bron per grafiek vermelden (C13)", "1, 2, 8"),
    ]
    t = pd.DataFrame(r, columns=["Risico", "Kans", "Impact", "Maatregel", "Dashboards"])
    t["Score"] = t["Kans"] * t["Impact"]
    return t.sort_values("Score", ascending=False)


def main():
    c, r = controles(tests="--tests" in sys.argv), risico()
    c.to_csv("tableau/data/t15_controles.csv", index=False)
    r.to_csv("tableau/data/t16_risico.csv", index=False)
    tekst = c[["Controle", "Doel", "Uitkomst", "Status"]].to_string(index=False) + "\n\nStatus: " + \
        ", ".join(f"{k} {v}" for k, v in c["Status"].value_counts().items()) + "\n\n" + r.to_string(index=False)
    print(tekst)
    open("resultaten/assurance.txt", "w", encoding="utf-8").write(tekst + "\n")


if __name__ == "__main__":
    main()
