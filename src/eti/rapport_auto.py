"""Automatische rapporten: dag, week en maand.

Wat het doet: (1) verse data ophalen als daar een opdracht voor is ingesteld, (2) kerncijfers uitrekenen met de
vergelijking met de vorige periode, (3) grafieken maken, (4) een opgemaakt rapport schrijven, (5) versturen als er
mailinstellingen zijn. Randgevallen: een dag zonder 24 uren telt niet mee in vergelijkingen; een feestdag wordt
vergeleken met de laatste zondag; een lopende week of maand wordt overgeslagen; ontbreekt alles, dan staat dat in
het rapport en in het logboek in plaats van een foutmelding.

Gebruik:  PYTHONPATH=src python3 -m eti.rapport_auto [dag|week|maand|alles] [JJJJ-MM-DD]
Cron:     15 7 * * *   cd <repo> && PYTHONPATH=src <python> -m eti.rapport_auto dag
          30 7 * * 1   cd <repo> && PYTHONPATH=src <python> -m eti.rapport_auto week
          45 7 1 * *   cd <repo> && PYTHONPATH=src <python> -m eti.rapport_auto maand
          <python> is het volledige pad van de Python met de bibliotheken, bijvoorbeeld <repo>/.venv/bin/python3.
          Cron kent je PATH niet: een kaal `python3` is daar de systeem-Python zonder pandas. Op macOS mag cron
          bovendien niet in Bureaublad, Documenten of Downloads lezen; zet de map elders of gebruik een LaunchAgent
          (zie reports/analyse/06_python.md). Getest in tests/test_mail_cron.py met een lege omgeving (env -i).
"""
import logging
import os
import re
import smtplib
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage

import numpy as np
import pandas as pd

from . import battery, rapport_grafieken as rg

# ------------------------------------------------------------------------------------------------ instellingen
DATA = "powerbi/data"
UIT = "reports/analyse/periodiek"
SJABLOON = "reports/analyse/sjablonen/kpi_rapport_sjabloon.md"
LOGBOEK = "resultaten/rapport_auto.log"
VERVERSEN = []                    # opdrachten die vooraf verse data ophalen, bijvoorbeeld [["python3", "-m", "eti.live"]]
AUTEUR = os.environ.get("RAPPORT_AUTEUR", "eti.rapport_auto")
MAIL = {"host": os.environ.get("SMTP_HOST", ""), "poort": int(os.environ.get("SMTP_PORT", "587")), "gebruiker": os.environ.get("SMTP_USER", ""),
        "wachtwoord": os.environ.get("SMTP_PASSWORD", ""), "van": os.environ.get("RAPPORT_VAN", ""),
        "aan": [a.strip() for a in os.environ.get("RAPPORT_AAN", "").split(",") if a.strip()]}     # nooit in de code: alleen uit de omgeving
LOKAAL = ("localhost", "127.0.0.1", "::1")     # alleen hier mag inloggen zonder versleuteling (proefserver op de eigen machine)
GROEN, GEEL, ROOD = "🟢 op koers", "🟡 let op", "🔴 actie nodig"
ACTIES = {"prijs": "Lopende waarderingen herzien met de huidige prijs als schok, niet als nieuw normaal",
          "capture": "Marktwaarde van zon in de modellen bijstellen naar de laatste twaalf maanden",
          "marge": "Geen zon zonder contract goedkeuren; afnamecontract of opslag toevoegen",
          "batterij": "Batterijcase toetsen op de inkomsten naast de dagmarkt en op netkosten",
          "negatief": "Contractbepalingen over negatieve prijzen nalopen", "zonneg": "Sturen op opwek buiten de overschoturen; afschakelen bij negatieve prijs regelen",
          "co2": "Impact per uur rapporteren en de daling toelichten", "vers": "Ophaalscripts controleren; de data loopt achter"}
log = logging.getLogger("rapport_auto")


def eur(x):
    return "n.b." if x is None or x != x else f"{x:,.0f}".replace(",", ".")


def komma(x, n=2):
    return "n.b." if x is None or x != x else f"{x:.{n}f}".replace(".", ",")


# ------------------------------------------------------------------------------------------------------- data
def ververs(opdrachten=None):
    """Draait de ingestelde ophaalopdrachten. Mislukt er een, dan gaat het rapport door op de bestaande data."""
    for opdracht in (VERVERSEN if opdrachten is None else opdrachten):
        try:
            subprocess.run(opdracht, check=True, timeout=1800, env={**os.environ, "PYTHONPATH": "src"})
            log.info("ververst: %s", " ".join(opdracht))
        except Exception as e:
            log.warning("verversen mislukt (%s): %s; het rapport gebruikt de bestaande data", " ".join(opdracht), e)


def dagtabel(data=DATA):
    """Een rij per dag: prijs, dagspreiding, negatieve uren, batterij-omzet per MW en of de dag volledig is."""
    u = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), parse_dates=["timestamp_utc"]).dropna(subset=["prijs_eur_mwh"])
    u = u.drop_duplicates("timestamp_utc").set_index("timestamp_utc").sort_index()
    g = u.prijs_eur_mwh.groupby(u.index.date)
    d = pd.DataFrame({"uren": g.size(), "prijs": g.mean(), "dagspreiding": g.max() - g.min(), "negatieve_uren": g.apply(lambda s: int((s < 0).sum()))})
    d.index = pd.to_datetime(d.index)
    d["volledig"] = d.uren == 24
    per_dag = {pd.Timestamp(k): v.tolist() for k, v in u.prijs_eur_mwh.groupby(u.index.date) if len(v) == 24}
    vol = sorted(per_dag.items())                                    # alleen volledige dagen doen mee in het batterijplan
    winst = battery.naive_forecast_daily([p for _, p in vol], rg.UREN_OPSLAG, rg.RENDEMENT)
    d["batterij_per_mw"] = pd.Series(winst, index=[dag for dag, _ in vol[1:]]).reindex(d.index)
    return d


def pasen(jaar):
    """Eerste paasdag (algoritme van Gauss voor de gregoriaanse kalender)."""
    a, b, c = jaar % 19, jaar // 100, jaar % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    j, k = c // 4, c % 4
    m = (a + 11 * h) // 319
    r = (2 * e + 2 * j - k - h + m + 32) % 7
    maand = (h - m + r + 90) // 25
    return date(jaar, maand, (h - m + r + maand + 19) % 32)


def feestdagen(jaar):
    """Nederlandse feestdagen waarop de stroomvraag op een zondag lijkt."""
    p = pasen(jaar)
    koningsdag = date(jaar, 4, 26) if date(jaar, 4, 27).weekday() == 6 else date(jaar, 4, 27)
    return {date(jaar, 1, 1), p, p + timedelta(1), koningsdag, date(jaar, 5, 5), p + timedelta(39), p + timedelta(49), p + timedelta(50),
            date(jaar, 12, 25), date(jaar, 12, 26)}


# --------------------------------------------------------------------------------------------------- rapporten
def verschil(nu, toen, procent=True):
    if nu is None or toen is None or nu != nu or toen != toen or (procent and toen == 0):
        return "n.b."
    return f"{nu / toen - 1:+.0%}" if procent else f"{nu - toen:+,.0f}".replace(",", ".")


def dagrapport(d, dag=None):
    """Laatste volledige dag (of de gevraagde dag) tegenover het gemiddelde van de zeven dagen ervoor en dezelfde
    weekdag een week eerder; op een feestdag de laatste zondag."""
    vol = d[d.volledig]
    if dag is not None:
        vol = vol[vol.index <= pd.Timestamp(dag)]
    if vol.empty:
        return "# Dagrapport\n\nGeen volledige dag in de data. Controleer het ophalen.\n", None
    t = vol.index[-1]
    nu = vol.iloc[-1]
    week = vol[(vol.index < t) & (vol.index >= t - pd.Timedelta(days=7))]
    feest = t.date() in feestdagen(t.year)
    if feest:
        kandidaten = vol[(vol.index < t) & (vol.index.dayofweek == 6)]
        maat, maatnaam = (kandidaten.iloc[-1] if len(kandidaten) else None), "de laatste zondag (feestdag)"
    else:
        vorige = t - pd.Timedelta(days=7)
        maat, maatnaam = (vol.loc[vorige] if vorige in vol.index else None), "dezelfde weekdag een week eerder"
    ontbreekt = int((~d[(d.index <= t) & (d.index > t - pd.Timedelta(days=7))].volledig).sum())
    regels = [f"# Dagrapport {t:%d-%m-%Y}" + (" (feestdag)" if feest else ""), "",
              "| Kerncijfer | Waarde | Gemiddelde 7 dagen ervoor | Verschil | " + maatnaam.capitalize() + " | Verschil |", "|---|---|---|---|---|---|"]
    for naam, kol, proc in (("Dagmarktprijs (euro per MWh)", "prijs", True), ("Dagspreiding (euro per MWh)", "dagspreiding", True),
                            ("Negatieve uren", "negatieve_uren", False), ("Batterij 2 uur (euro per MW)", "batterij_per_mw", True)):
        gem = week[kol].mean() if len(week) else np.nan
        m = maat[kol] if maat is not None else np.nan
        regels.append(f"| {naam} | {eur(nu[kol])} | {eur(gem)} | {verschil(nu[kol], gem, proc)} | {eur(m)} | {verschil(nu[kol], m, proc)} |")
    regels += ["", f"Vergelijking over {len(week)} volledige dagen." + (f" In de laatste week ontbreken uren op {ontbreekt} dag(en); die tellen niet mee." if ontbreekt else ""),
               f"Laatste meting in de data: {d.index.max():%d-%m-%Y}."]
    return "\n".join(regels) + "\n", t


def weekrapport(d, tot=None):
    """Laatste volledige week (maandag tot en met zondag, zeven volledige dagen) tegenover de week ervoor en dezelfde
    week een jaar eerder."""
    vol = d[d.volledig]
    if tot is not None:
        vol = vol[vol.index <= pd.Timestamp(tot)]
    weken = vol.groupby(vol.index.to_period("W-SUN")).agg(dagen=("prijs", "size"), prijs=("prijs", "mean"), dagspreiding=("dagspreiding", "mean"),
                                                             negatieve_uren=("negatieve_uren", "sum"), batterij_per_mw=("batterij_per_mw", "sum"))
    heel = weken[weken.dagen == 7]
    if heel.empty:
        return "# Weekrapport\n\nGeen volledige week in de data.\n", None
    w, nu = heel.index[-1], heel.iloc[-1]
    vorig = heel.loc[w - 1] if (w - 1) in heel.index else None
    jaar = heel.loc[w - 52] if (w - 52) in heel.index else None
    regels = [f"# Weekrapport week {w.start_time.isocalendar()[1]} van {w.start_time.year} ({w.start_time:%d-%m} tot en met {w.end_time:%d-%m})", "",
              "| Kerncijfer | Deze week | Week ervoor | Verschil | Zelfde week vorig jaar | Verschil |", "|---|---|---|---|---|---|"]
    for naam, kol, proc in (("Dagmarktprijs (euro per MWh)", "prijs", True), ("Dagspreiding (euro per MWh)", "dagspreiding", True),
                            ("Negatieve uren", "negatieve_uren", False), ("Batterij 2 uur (euro per MW)", "batterij_per_mw", True)):
        a, b = (vorig[kol] if vorig is not None else np.nan), (jaar[kol] if jaar is not None else np.nan)
        regels.append(f"| {naam} | {eur(nu[kol])} | {eur(a)} | {verschil(nu[kol], a, proc)} | {eur(b)} | {verschil(nu[kol], b, proc)} |")
    over = len(weken) - len(heel)
    regels += ["", f"Weken met minder dan zeven volledige dagen zijn overgeslagen ({over} in de hele reeks)."]
    return "\n".join(regels) + "\n", w


def stoplicht(waarde, groen, geel):
    """groen en geel zijn functies die True geven als de waarde in dat vak valt."""
    if waarde is None or waarde != waarde:
        return "n.b."
    return GROEN if groen(waarde) else GEEL if geel(waarde) else ROOD


def kpi_waarden(m, tot, data=DATA, nu_moment=None):
    """Alle invulvelden van het KPI-sjabloon voor de laatste volledige maand tot en met `tot`."""
    t = rg.kengetallen(m, "M")
    t = t[t.volledig & (t.index <= tot)]
    nu, vorig = t.iloc[-1], (t.iloc[-13] if len(t) > 12 else t.iloc[0])
    eerder = t.prijs.iloc[-13:-1]
    z = (nu.prijs - eerder.mean()) / eerder.std() if len(eerder) > 2 else np.nan
    marge, marge_vorig = nu.zonprijs - nu.lcoe, vorig.zonprijs - vorig.lcoe
    b8, b5 = rg.break_even(0.08) / 12, rg.break_even(0.05) / 12
    jaar = pd.read_csv(os.path.join(data, "fact_nl_jaar.csv")).set_index("jaar").co2_vermeden_uur
    heel = [j for j in jaar.index if j < t.index[-1].year] or list(jaar.index)
    co2, co2_vorig = jaar[heel[-1]], (jaar[heel[-2]] if len(heel) > 1 else np.nan)
    laatste = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), usecols=["timestamp_utc"], parse_dates=["timestamp_utc"]).timestamp_utc.max()
    moment = nu_moment or datetime.now(timezone.utc).replace(tzinfo=None)
    vers = (moment - laatste).total_seconds() / 86400
    punten = (nu.capture_rate - vorig.capture_rate) * 100
    w = {"soort": "maand", "periode": rg.naam(t.index[-1], "M"), "vergelijkperiode": rg.naam(vorig.name, "M"), "data_tot": f"{laatste:%d-%m-%Y %H:%M} UTC",
         "auteur": AUTEUR, "datum_opgesteld": f"{moment:%d-%m-%Y}",
         "prijs": eur(nu.prijs), "prijs_norm": f"{eur(eerder.mean())} (12 maanden ervoor)", "prijs_vorig": eur(vorig.prijs), "prijs_verschil": verschil(nu.prijs, vorig.prijs),
         "prijs_status": stoplicht(abs(z), lambda x: x <= 2, lambda x: x <= 4),
         "capture": komma(nu.capture_rate), "capture_norm": f"{komma(vorig.capture_rate)} (vorig jaar)", "capture_vorig": komma(vorig.capture_rate),
         "capture_verschil": f"{punten:+.0f} punten", "capture_status": stoplicht(punten, lambda x: x >= 0, lambda x: x >= -5),
         "marge": eur(marge), "marge_norm": "vanaf 5", "marge_vorig": eur(marge_vorig), "marge_verschil": verschil(marge, marge_vorig, False),
         "marge_status": stoplicht(marge, lambda x: x >= 5, lambda x: x >= 0),
         "batterij": eur(nu.batterij_per_mw), "batterij_norm": f"{eur(b8)} (8%)", "batterij_vorig": eur(vorig.batterij_per_mw),
         "batterij_verschil": verschil(nu.batterij_per_mw, vorig.batterij_per_mw), "batterij_status": stoplicht(nu.batterij_per_mw, lambda x: x >= b8, lambda x: x >= b5),
         "negatief": eur(nu.negatieve_uren), "negatief_norm": f"hooguit {eur(vorig.negatieve_uren)}", "negatief_vorig": eur(vorig.negatieve_uren),
         "negatief_verschil": verschil(nu.negatieve_uren, vorig.negatieve_uren, False),
         "negatief_status": stoplicht(nu.negatieve_uren, lambda x: x <= vorig.negatieve_uren, lambda x: x <= 1.25 * vorig.negatieve_uren),
         "zonneg": komma(nu.aandeel_zon_in_negatieve_uren * 100, 1), "zonneg_norm": "onder 5", "zonneg_vorig": komma(vorig.aandeel_zon_in_negatieve_uren * 100, 1),
         "zonneg_verschil": f"{(nu.aandeel_zon_in_negatieve_uren - vorig.aandeel_zon_in_negatieve_uren) * 100:+.1f} punten".replace(".", ","),
         "zonneg_status": stoplicht(nu.aandeel_zon_in_negatieve_uren, lambda x: x < 0.05, lambda x: x <= 0.15),
         "co2": f"{eur(co2)} ({heel[-1]})", "co2_norm": f"minstens {eur(co2_vorig)}", "co2_vorig": eur(co2_vorig), "co2_verschil": verschil(co2, co2_vorig),
         "co2_status": stoplicht(co2 / co2_vorig - 1 if co2_vorig == co2_vorig else np.nan, lambda x: x >= 0, lambda x: x >= -0.10),
         "vers": komma(vers, 1), "vers_norm": "hooguit 2", "vers_status": stoplicht(vers, lambda x: x <= 2, lambda x: x <= 4),
         "prijs_trend": f"{verschil(nu.prijs, vorig.prijs)} tegenover {rg.naam(vorig.name, 'M')}; {komma(z, 1)} standaardafwijkingen van het gemiddelde van de twaalf maanden ervoor",
         "prijs_context": "een afwijking boven 2 standaardafwijkingen wijst op een schok (gas, weer) en vertekent vergelijkingen met vorig jaar",
         "capture_trend": f"capture rate {komma(nu.capture_rate)} ({punten:+.0f} punten); zon ontving {eur(nu.zonprijs)} euro per MWh bij kosten van {eur(nu.lcoe)} euro",
         "capture_context": "de capture rate is seizoensgebonden: vergelijk met dezelfde maand vorig jaar, niet met de vorige maand",
         "batterij_trend": f"{eur(nu.batterij_per_mw)} euro per MW ({verschil(nu.batterij_per_mw, vorig.batterij_per_mw)}); dagspreiding {eur(nu.dagspreiding)} euro per MWh",
         "batterij_context": f"voor 8% rendement is {eur(b8)} euro per MW per maand nodig, voor 5% {eur(b5)}; zonder balanceringsmarkten en netkosten",
         "negatief_trend": f"{eur(nu.negatieve_uren)} uren (was {eur(vorig.negatieve_uren)}); {komma(nu.aandeel_zon_in_negatieve_uren * 100, 1)}% van de zonopwek viel in die uren",
         "negatief_context": "negatieve uren vallen vooral van april tot en met augustus",
         "co2_trend": f"{eur(co2)} ton in {heel[-1]} ({verschil(co2, co2_vorig)} tegenover het jaar ervoor)", "co2_context": "jaarcijfer van het modelpark, per uur berekend; wordt een keer per jaar ververst",
         "kwaliteit_samenvatting": f"laatste meting {komma(vers, 1)} dagen oud; maand met {int(nu.uren)} uren",
         "toelichting": "(nog in te vullen door de analist)"}
    rood = [k for k in ACTIES if w.get(k + "_status") == ROOD]
    geel = [k for k in ACTIES if w.get(k + "_status") == GEEL]
    w["acties"] = "\n".join(f"| {i} | {ACTIES[k]} | kerncijfer {k} staat op {'rood' if k in rood else 'geel'} | | | open |" for i, k in enumerate(rood + geel, 1)) or "| | geen acties uit de scorekaart | | | | |"
    statussen = [v for k, v in w.items() if k.endswith("_status")]
    w.update({"aantal_groen": statussen.count(GROEN), "aantal_geel": statussen.count(GEEL), "aantal_rood": statussen.count(ROOD)})
    return w


def vul(sjabloon, waarden):
    """Vult {{velden}} in. Een veld zonder waarde wordt 'n.b.' en komt in het logboek, zodat niets stil leeg blijft."""
    def kies(m):
        if m.group(1) not in waarden:
            log.warning("sjabloonveld zonder waarde: %s", m.group(1))
        return str(waarden.get(m.group(1), "n.b."))
    return re.sub(r"\{\{(\w+)\}\}", kies, sjabloon)


def verstuur(onderwerp, tekst, bijlagen=(), mail=None):
    """Verstuurt het rapport per mail als host, afzender en ontvangers zijn ingesteld; anders alleen een logregel."""
    mail = MAIL if mail is None else mail
    if not (mail["host"] and mail["van"] and mail["aan"]):
        log.info("niet verstuurd: geen mailinstellingen (SMTP_HOST, RAPPORT_VAN, RAPPORT_AAN)")
        return False
    bericht = EmailMessage()
    bericht["Subject"], bericht["From"], bericht["To"] = onderwerp, mail["van"], ", ".join(mail["aan"])
    bericht.set_content(tekst)
    for pad in bijlagen:
        with open(pad, "rb") as fh:
            bericht.add_attachment(fh.read(), maintype="application", subtype="octet-stream", filename=os.path.basename(pad))
    klasse = smtplib.SMTP_SSL if mail["poort"] == 465 else smtplib.SMTP        # 465 = meteen versleuteld, 587 = STARTTLS
    try:
        with klasse(mail["host"], mail["poort"], timeout=30) as server:
            server.ehlo()
            versleuteld = klasse is smtplib.SMTP_SSL
            if not versleuteld and server.has_extn("starttls"):
                server.starttls()
                server.ehlo()
                versleuteld = True
            if mail["gebruiker"]:
                if not versleuteld and mail["host"] not in LOKAAL:
                    log.error("niet verstuurd: %s biedt geen versleuteling; het wachtwoord gaat niet onversleuteld de lijn op", mail["host"])
                    return False
                server.login(mail["gebruiker"], mail["wachtwoord"])
            server.send_message(bericht)
    except (smtplib.SMTPException, OSError) as fout:          # een mailstoring mag het rapport zelf niet tegenhouden
        log.error("niet verstuurd: %s: %s", type(fout).__name__, fout)
        return False
    log.info("verstuurd aan %d ontvanger(s): %s", len(mail["aan"]), onderwerp)
    return True


def main(soort="alles", tot=None, data=DATA, uit=UIT):
    os.makedirs(os.path.dirname(LOGBOEK), exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler(LOGBOEK, encoding="utf-8"), logging.StreamHandler()])
    ververs()
    paden = []
    try:
        d = dagtabel(data)
    except FileNotFoundError as e:
        log.error("brondata ontbreekt: %s", e)
        return paden
    if soort in ("dag", "alles"):
        tekst, t = dagrapport(d, tot)
        map_ = os.path.join(uit, f"dag_{t:%Y-%m-%d}" if t is not None else "dag_onbekend")
        os.makedirs(map_, exist_ok=True)
        paden.append(os.path.join(map_, "dagrapport.md"))
        open(paden[-1], "w", encoding="utf-8").write(tekst)
        verstuur(tekst.splitlines()[0].lstrip("# "), tekst)
    if soort in ("week", "alles"):
        tekst, w = weekrapport(d, tot)
        map_ = os.path.join(uit, f"week_{w.start_time:%G-W%V}" if w is not None else "week_onbekend")
        os.makedirs(map_, exist_ok=True)
        paden.append(os.path.join(map_, "weekrapport.md"))
        open(paden[-1], "w", encoding="utf-8").write(tekst)
        verstuur(tekst.splitlines()[0].lstrip("# "), tekst)
    if soort in ("maand", "alles"):
        from . import vis
        vis.stijl()
        m = rg.maandtabel(data)
        grens = pd.Timestamp(tot) if tot else m[m.volledig].periode.max()
        lijst, regels, map_ = rg.rapport(m, "M", grens, uit)
        tekst = vul(open(SJABLOON, encoding="utf-8").read(), kpi_waarden(m, grens, data))
        paden.append(os.path.join(map_, "kpi_rapport.md"))
        open(paden[-1], "w", encoding="utf-8").write(tekst)
        verstuur(tekst.splitlines()[0].lstrip("# "), "\n".join(regels), [os.path.join(map_, n) for n, _ in lijst] + [paden[-1]])
    for p in paden:
        log.info("geschreven: %s", p)
    return paden


if __name__ == "__main__":
    main(*sys.argv[1:3])
