"""Vaste grafiekenset voor het maand-, kwartaal- en jaarrapport over beleggen in zon en opslag (Nederland).

Alles komt uit een enkele tabel: `maandtabel()` geeft een rij per maand met optelbare kolommen (uren, omzet, opwek,
negatieve uren, batterij-omzet) en de kengetallen die daaruit volgen. Elk rapport heeft drie onderdelen (markt, zon,
opslag of impact) met een grafiek per onderdeel, een titel die de uitkomst noemt en een bijschrift in vaste vorm:
"Deze grafiek laat zien dat [inzicht]. De belangrijkste conclusie is [actie]."

Opnieuw draaien voor een andere periode:
    PYTHONPATH=src python3 -m eti.rapport_grafieken               (laatste volledige maand, kwartaal en jaar)
    PYTHONPATH=src python3 -m eti.rapport_grafieken 2026-06       (stand per juni 2026)
Uitvoer: reports/analyse/periodiek/<soort>_<periode>/*.png, bijschriften.txt en samenvatting.txt.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import battery, vis
from .vis import K, MAAND, kop, punt

DATA, UIT = "powerbi/data", "reports/analyse/periodiek"
UREN_OPSLAG, RENDEMENT = 2, 0.88
STREEF = 0.08
OPTELBAAR = ["uren", "prijs_som", "zon_mwh", "zon_omzet", "zon_mwh_negatief", "negatieve_uren", "dagen", "dagspreiding_som", "batterij_per_mw"]


def maandtabel(data=DATA):
    """De enige brontabel: een rij per maand. Optelbare kolommen eerst, kengetallen via `kengetallen`."""
    u = pd.read_csv(os.path.join(data, "fact_nl_uur_alle_jaren.csv"), parse_dates=["timestamp_utc"]).dropna(subset=["prijs_eur_mwh"])
    u = u.drop_duplicates("timestamp_utc").set_index("timestamp_utc").sort_index()
    u["maand"] = u.index.to_period("M").to_timestamp()
    u["omzet"], u["neg"] = u.prijs_eur_mwh * u.solar_mw, u.prijs_eur_mwh < 0
    m = u.groupby("maand").agg(uren=("prijs_eur_mwh", "size"), prijs_som=("prijs_eur_mwh", "sum"), zon_mwh=("solar_mw", "sum"),
                               zon_omzet=("omzet", "sum"), negatieve_uren=("neg", "sum"))
    m["zon_mwh_negatief"] = u[u.neg].groupby("maand").solar_mw.sum().reindex(m.index).fillna(0.0)
    dagen = [(d, g.prijs_eur_mwh.tolist()) for d, g in u.groupby(u.index.date) if len(g) == 24]
    spreiding = pd.Series({pd.Timestamp(d): max(p) - min(p) for d, p in dagen})
    winst = pd.Series(battery.naive_forecast_daily([p for _, p in dagen], UREN_OPSLAG, RENDEMENT), index=[pd.Timestamp(d) for d, _ in dagen[1:]])
    m["dagen"] = spreiding.groupby(spreiding.index.to_period("M").to_timestamp()).size().reindex(m.index).fillna(0)
    m["dagspreiding_som"] = spreiding.groupby(spreiding.index.to_period("M").to_timestamp()).sum().reindex(m.index).fillna(0.0)
    m["batterij_per_mw"] = winst.groupby(winst.index.to_period("M").to_timestamp()).sum().reindex(m.index).fillna(0.0)
    m["volledig"] = m.uren >= m.index.days_in_month * 24 - 2
    jaar = pd.read_csv(os.path.join(data, "fact_nl_jaar.csv")).set_index("jaar")
    m["co2_vermeden_ton_jaar"] = m.index.year.map(jaar.co2_vermeden_uur)
    lcoe = pd.read_csv(os.path.join(data, "fact_regio_jaar.csv")).query("regio == 'Nederland'").set_index("jaar").lcoe_eur_mwh
    m["lcoe"] = np.interp(m.index.year, lcoe.index, lcoe.values)
    return m.reset_index().rename(columns={"maand": "periode"})


def kengetallen(m, per="M"):
    """Telt de maandtabel op naar maand (M), kwartaal (Q) of jaar (Y) en rekent de kengetallen uit."""
    sleutel = m.periode.dt.to_period(per).dt.to_timestamp()
    t = m.groupby(sleutel)[OPTELBAAR].sum()
    t["volledig"] = m.groupby(sleutel).volledig.all()
    t["prijs"] = t.prijs_som / t.uren
    t["zonprijs"] = t.zon_omzet / t.zon_mwh
    t["capture_rate"] = t.zonprijs / t.prijs
    t["dagspreiding"] = t.dagspreiding_som / t.dagen
    t["aandeel_zon_in_negatieve_uren"] = t.zon_mwh_negatief / t.zon_mwh
    t["lcoe"] = m.groupby(sleutel).lcoe.mean()
    t["co2_vermeden_ton_jaar"] = m.groupby(sleutel).co2_vermeden_ton_jaar.first()
    return t


def break_even(doel=STREEF):
    """Omzet per MW per jaar waarbij de batterij (EUR 560 per kW, 15 jaar) het streefrendement haalt."""
    from . import volledige_case as vc
    laag, hoog = 10_000.0, 400_000.0
    for _ in range(60):
        mid = (laag + hoog) / 2
        laag, hoog = (mid, hoog) if (vc.irr(mid, 0) or -1) < doel else (laag, mid)
    return hoog


def naam(t, per):
    return {"M": f"{MAAND[t.month - 1]} {t.year}", "Q": f"K{(t.month - 1) // 3 + 1} {t.year}", "Y": str(t.year)}[per]


def kolommen(ax, labels, waarden, nadruk=-1, grens=None, grenstekst=""):
    """Kolommen met de laatste (of gekozen) periode in kleur en de rest in grijs; optioneel een grenslijn."""
    kleuren = [K["grijs"]] * len(waarden)
    kleuren[nadruk] = K["blauw"]
    ax.bar(range(len(waarden)), waarden, width=0.55, color=kleuren, edgecolor=K["vlak"], linewidth=1.2)
    ax.set_xticks(range(len(waarden)))
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.text(len(waarden) - 1 if nadruk == -1 else nadruk, waarden[nadruk] + max(waarden) * 0.02, vis.eur(waarden[nadruk]), ha="center", fontsize=9.5, color=K["inkt2"])
    if grens is not None:
        ax.axhline(grens, color=K["gedempt"], lw=0.8)
        ax.text(-0.4, grens + max(max(waarden), grens) * 0.015, grenstekst, fontsize=8.5, color=K["gedempt"])


def figuur(titel, onder, bron, hoogte=3.5):
    fig, ax = plt.subplots(figsize=(7.2, hoogte))
    return fig, ax, (titel, onder, bron)


def rapport(m, per, tot, uit):
    """Maakt de drie grafieken van een rapport. Geeft de lijst (bestandsnaam, bijschrift) en de samenvatting."""
    t = kengetallen(m, per)
    t = t[t.volledig & (t.index <= tot)]
    nu, vorig = t.iloc[-1], t.iloc[-1 - {"M": 12, "Q": 4, "Y": 1}[per]]
    n = {"M": 13, "Q": 9, "Y": 7}[per]
    laatste = t.tail(n)
    labels = [naam(x, per).replace(" ", "\n") if per != "Y" else naam(x, per) for x in laatste.index]
    periode, toen = naam(t.index[-1], per), naam(t.index[-1 - {"M": 12, "Q": 4, "Y": 1}[per]], per)
    schaal = {"M": 12, "Q": 4, "Y": 1}[per]
    grens = break_even() / schaal
    lijst, bron = [], "Bron: Energy-Charts; eigen berekening (eti.rapport_grafieken)."
    map_ = os.path.join(uit, f"{ {'M': 'maand', 'Q': 'kwartaal', 'Y': 'jaar'}[per] }_{t.index[-1].strftime('%Y-%m') if per != 'Y' else t.index[-1].year}")

    # 1 markt: prijs
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    kolommen(ax, labels, laatste.prijs.values)
    ax.set_ylabel("dagmarktprijs (euro per MWh)")
    groei = nu.prijs / vorig.prijs - 1
    kop(fig, f"Markt: {vis.eur(nu.prijs)} euro per MWh in {periode}, {groei:+.0%} tegenover {toen}", f"Gemiddelde Nederlandse dagmarktprijs per {'maand' if per == 'M' else 'kwartaal' if per == 'Q' else 'jaar'}.", bron)
    vis.bewaar(fig, map_, "1_markt_prijs.png", f"Deze grafiek laat zien dat de dagmarktprijs in {periode} {vis.eur(nu.prijs)} euro per MWh was, {groei:+.0%} tegenover {toen}. "
               f"De belangrijkste conclusie is: {'herzie de prijsaanname in lopende waarderingen' if abs(groei) > 0.25 else 'de prijsaanname hoeft niet te worden aangepast'}.", lijst)

    # 2 zon: capture rate dit jaar tegen een jaar eerder, en de capture-prijs tegen de kosten
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    eerder = t.capture_rate.shift({"M": 12, "Q": 4, "Y": 1}[per]).reindex(laatste.index)
    if per == "Y":
        ax.plot(range(len(laatste)), laatste.zonprijs.values, color=K["blauw"], label="capture-prijs van zon")
        ax.plot(range(len(laatste)), laatste.lcoe.values, color=K["gedempt"], lw=1.2, label="kosten per MWh (LCOE)")
        for i, v in enumerate(laatste.zonprijs.values):
            punt(ax, i, v, K["blauw"])
        ax.text(len(laatste) - 1 + 0.12, laatste.zonprijs.iloc[-1], vis.eur(nu.zonprijs), va="center", fontsize=9.5, color=K["inkt2"])
        ax.set_ylabel("euro per MWh"); ax.set_ylim(0, None)
        marge = nu.zonprijs - nu.lcoe
        titel = f"Zon: capture-prijs {vis.eur(nu.zonprijs)} euro, {vis.eur(abs(marge))} euro {'boven' if marge >= 0 else 'onder'} de kosten in {periode}"
        tekst = (f"Deze grafiek laat zien dat zon in {periode} {vis.eur(nu.zonprijs)} euro per MWh ontving bij kosten van {vis.eur(nu.lcoe)} euro (capture rate {nu.capture_rate:.2f}). "
                 f"De belangrijkste conclusie is: {'zonder contract dekt zon de kosten' if marge >= 0 else 'zonder contract dekt zon de kosten niet; sluit een afnamecontract of voeg opslag toe'}.")
    else:
        ax.plot(range(len(laatste)), eerder.values, color=K["grijs"], label="een jaar eerder")
        ax.plot(range(len(laatste)), laatste.capture_rate.values, color=K["blauw"], label="capture rate van zon")
        for i, v in enumerate(laatste.capture_rate.values):
            punt(ax, i, v, K["blauw"])
        ax.axhline(1, color=K["gedempt"], lw=0.8)
        ax.text(len(laatste) - 1 + 0.12, laatste.capture_rate.iloc[-1], f"{nu.capture_rate:.2f}".replace(".", ","), va="center", fontsize=9.5, color=K["inkt2"])
        ax.set_ylabel("capture rate (1 = gemiddelde prijs)"); ax.set_ylim(0, max(1.3, np.nanmax(laatste.capture_rate.values) * 1.1))
        verschil = (nu.capture_rate - vorig.capture_rate) * 100
        titel = f"Zon: capture rate {nu.capture_rate:.2f} in {periode}, {verschil:+.0f} punten tegenover {toen}".replace("0.", "0,")
        tekst = (f"Deze grafiek laat zien dat zon in {periode} {nu.capture_rate:.0%} van de gemiddelde prijs ontving, {verschil:+.0f} punten tegenover {toen}; "
                 f"{nu.aandeel_zon_in_negatieve_uren:.0%} van de zonopwek viel in uren met een negatieve prijs. "
                 f"De belangrijkste conclusie is: {'de marktwaarde van zon staat verder onder druk' if verschil < -2 else 'de marktwaarde van zon is stabiel of herstelt'}.")
    ax.set_xticks(range(len(laatste))); ax.set_xticklabels(labels, fontsize=8.5); ax.set_xlim(-0.5, len(laatste) - 0.2)
    ax.legend(loc="lower left" if per != "Y" else "upper left", ncol=2 if per != "Y" else 1)
    kop(fig, titel, "Wat zon ontvangt ten opzichte van de gemiddelde prijs." if per != "Y" else "Wat zon per MWh ontvangt tegenover de kosten per MWh van een nieuw park.", bron)
    vis.bewaar(fig, map_, "2_zon.png", tekst, lijst)

    # 3 opslag (maand en kwartaal) of impact (jaar)
    if per == "Y":
        fig, (a, b) = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True, gridspec_kw={"hspace": 0.3})
        kolommen(a, labels, laatste.co2_vermeden_ton_jaar.values)
        a.set_ylabel("vermeden CO2 (ton per jaar,\nmodelpark 10 MW)")
        b.plot(range(len(laatste)), laatste.aandeel_zon_in_negatieve_uren.values * 100, color=K["oranje"])
        for i, v in enumerate(laatste.aandeel_zon_in_negatieve_uren.values * 100):
            punt(b, i, v, K["oranje"])
        b.text(len(laatste) - 1 + 0.12, nu.aandeel_zon_in_negatieve_uren * 100, f"{nu.aandeel_zon_in_negatieve_uren:.0%}", va="center", fontsize=9.5, color=K["inkt2"])
        b.set_ylabel("zonopwek in uren met\nnegatieve prijs (%)"); b.set_ylim(0, None); b.set_xlim(-0.5, len(laatste) - 0.2)
        daling = nu.co2_vermeden_ton_jaar / laatste.co2_vermeden_ton_jaar.iloc[0] - 1
        kop(fig, f"Impact: {vis.eur(nu.co2_vermeden_ton_jaar)} ton vermeden CO2 in {periode}, {daling:+.0%} sinds {naam(laatste.index[0], per)}",
            "Boven: vermeden uitstoot volgens de uurmethode. Onder: deel van de opwek dat niets verdringt.", bron)
        vis.bewaar(fig, map_, "3_impact.png", f"Deze grafiek laat zien dat het modelpark in {periode} {vis.eur(nu.co2_vermeden_ton_jaar)} ton CO2 vermeed ({daling:+.0%} sinds {naam(laatste.index[0], per)}) "
                   f"en dat {nu.aandeel_zon_in_negatieve_uren:.0%} van de zonopwek in uren met een negatieve prijs viel. "
                   "De belangrijkste conclusie is: rapporteer impact per uur en niet met een jaargemiddelde, en stuur op opwek buiten de overschoturen.", lijst)
    else:
        fig, ax = plt.subplots(figsize=(7.2, 3.4))
        kolommen(ax, labels, laatste.batterij_per_mw.values, grens=grens, grenstekst=f"nodig voor {STREEF:.0%} rendement: {vis.eur(grens)}")
        ax.set_ylabel(f"omzet per MW per {'maand' if per == 'M' else 'kwartaal'} (euro)")
        haalt = nu.batterij_per_mw >= grens
        kop(fig, f"Opslag: {vis.eur(nu.batterij_per_mw)} euro per MW in {periode}, {'boven' if haalt else 'onder'} de {vis.eur(grens)} die nodig is",
            "Batterij van 2 uur op de dagmarkt, plan op de prijzen van gisteren. Zonder balanceringsmarkten en netkosten.", bron)
        vis.bewaar(fig, map_, "3_opslag.png", f"Deze grafiek laat zien dat een batterij van 2 uur in {periode} {vis.eur(nu.batterij_per_mw)} euro per MW verdiende op de dagmarkt, "
                   f"{'meer' if haalt else 'minder'} dan de {vis.eur(grens)} euro die voor {STREEF:.0%} rendement nodig is; de dagspreiding was {vis.eur(nu.dagspreiding)} euro per MWh. "
                   f"De belangrijkste conclusie is: {'de dagmarkt alleen dekt deze periode de kapitaalkosten' if haalt else 'de batterij heeft naast de dagmarkt andere inkomsten nodig'}.", lijst)

    with open(os.path.join(map_, "bijschriften.txt"), "w", encoding="utf-8") as fh:
        for bestand, tekst in lijst:
            fh.write(f"{bestand}\n{tekst}\n\n")
    regels = [f"Rapport {periode} (vergelijking met {toen})",
              f"Prijs: {vis.eur(nu.prijs)} euro per MWh ({nu.prijs / vorig.prijs - 1:+.0%})",
              f"Capture rate zon: {nu.capture_rate:.2f} (was {vorig.capture_rate:.2f}); capture-prijs {vis.eur(nu.zonprijs)} euro tegenover kosten {vis.eur(nu.lcoe)} euro".replace("0.", "0,"),
              f"Negatieve uren: {int(nu.negatieve_uren)} (was {int(vorig.negatieve_uren)}); zonopwek in negatieve uren: {nu.aandeel_zon_in_negatieve_uren:.0%}",
              f"Dagspreiding: {vis.eur(nu.dagspreiding)} euro per MWh (was {vis.eur(vorig.dagspreiding)})",
              f"Batterij 2 uur, dagmarkt: {vis.eur(nu.batterij_per_mw)} euro per MW (nodig voor {STREEF:.0%}: {vis.eur(grens)})"]
    with open(os.path.join(map_, "samenvatting.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(regels) + "\n")
    return lijst, regels, map_


def main(tot=None, data=DATA, uit=UIT):
    vis.stijl()
    m = maandtabel(data)
    tot = pd.Timestamp(tot) if tot else m[m.volledig].periode.max()
    for per in ("M", "Q", "Y"):
        lijst, regels, map_ = rapport(m, per, tot, uit)
        print(f"  -> {map_}: {len(lijst)} grafieken | {regels[1]}")
    return m


if __name__ == "__main__":
    main(*sys.argv[1:4])
