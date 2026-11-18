"""Verkenner: interactief prototype (Streamlit met Plotly) om de zone-jaren, tijdreeksen en scenario's te doorzoeken.

Starten:  pip install streamlit plotly
          streamlit run src/eti/verken_app.py --server.address localhost      (alleen op deze machine, niet op het netwerk)
De rekenfuncties bovenaan gebruiken alleen pandas en numpy en zijn los te testen; alles wat het scherm tekent staat
in main(). Brontabellen: fact_zonejaar_DA, fact_land_maand, fact_scenario_SA (eerst eti.da en eti.prognose draaien).
"""
import os

import numpy as np
import pandas as pd

DATA = "powerbi/data"
MATEN = {"capture_zon": "Capture rate zon", "batterij_per_mw": "Batterij 2 uur (euro per MW per jaar)", "dagspreiding": "Dagspreiding (euro per MWh)",
         "negatieve_uren": "Negatieve uren", "gem_prijs": "Gemiddelde prijs (euro per MWh)", "aandeel_zon_pct": "Aandeel zon in de opwek (%)",
         "aandeel_wind_pct": "Aandeel wind in de opwek (%)"}
KLEUREN = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEGMENTKLEUR = {"Batterijmarkt": "#2a78d6", "Zonverzadigd": "#eb6834", "Vlakke prijzen": "#1baf7a", "Zon houdt waarde": "#eda100", "Middenveld": "#898781"}


# ----------------------------------------------------------------------------------------------- rekenfuncties
def laad(data=DATA):
    """Leest de drie tabellen. Geeft een dict; ontbrekende tabellen worden lege DataFrames met een melding."""
    uit, meldingen = {}, []
    for sleutel, bestand in (("zonejaar", "fact_zonejaar_DA.csv"), ("maand", "fact_land_maand.csv"), ("scenario", "fact_scenario_SA.csv")):
        pad = os.path.join(data, bestand)
        if os.path.exists(pad):
            uit[sleutel] = pd.read_csv(pad)
        else:
            uit[sleutel] = pd.DataFrame()
            meldingen.append(f"{bestand} ontbreekt: draai eerst eti.da en eti.prognose.")
    return uit, meldingen


def filter_zonejaar(df, jaren=None, regios=None, segmenten=None, zones=None, hele_jaren=True):
    """Past de filters toe. Een leeg filter (None of lege lijst) betekent: alles."""
    d = df
    if hele_jaren and "deeljaar" in d:
        d = d[~d.deeljaar]
    if jaren:
        d = d[d.jaar.between(min(jaren), max(jaren))]
    for kolom, keuze in (("regio", regios), ("regelsegment", segmenten), ("biedzone", zones)):
        if keuze:
            d = d[d[kolom].isin(keuze)]
    return d


def kerncijfers(d, jaar):
    """Vier kopcijfers voor het gekozen jaar, met het verschil tegenover het jaar ervoor (mediaan over de zones)."""
    nu, vorig = d[d.jaar == jaar], d[d.jaar == jaar - 1]
    uit = {}
    for kolom in ("capture_zon", "batterij_per_mw", "dagspreiding", "negatieve_uren"):
        a = nu[kolom].median() if len(nu) else np.nan
        b = vorig[kolom].median() if len(vorig) else np.nan
        uit[kolom] = (a, a - b if b == b else np.nan)
    return uit


def lijn_batterij(d):
    """Rechte lijn batterij-omzet = a + b * dagspreiding over de gekozen zone-jaren (voor de rekenhulp)."""
    x = d[["dagspreiding", "batterij_per_mw"]].dropna()
    if len(x) < 3:
        return 0.0, 0.0
    b, a = np.polyfit(x.dagspreiding, x.batterij_per_mw, 1)
    return float(a), float(b)


def marge_zon(prijs, capture_rate, lcoe):
    """Marge per MWh van zon zonder contract en de capture rate die nodig is om de kosten te dekken."""
    return prijs * capture_rate - lcoe, (lcoe / prijs if prijs else np.nan)


def rangorde(d, jaar, maat, n=37):
    r = d[d.jaar == jaar][["biedzone", "land", "regio", "regelsegment", maat]].dropna(subset=[maat])
    return r.sort_values(maat, ascending=False).head(n)


# ------------------------------------------------------------------------------------------------------ scherm
def breedte(functie):
    """Het argument waarmee een grafiek de volle breedte krijgt: Streamlit hernoemde use_container_width naar width."""
    import inspect
    try:
        namen = inspect.signature(functie).parameters
    except (TypeError, ValueError):
        return {}
    return {"width": "stretch"} if "width" in namen else ({"use_container_width": True} if "use_container_width" in namen else {})


def main():
    import plotly.express as px
    import streamlit as st
    BREED = breedte(st.plotly_chart)

    st.set_page_config(page_title="Zon en opslag: verkenner", layout="wide")
    data, meldingen = st.cache_data(laad)()
    for m in meldingen:
        st.warning(m)
    z = data["zonejaar"]
    if z.empty:
        st.stop()

    st.sidebar.header("Filters")
    jaren = st.sidebar.slider("Jaren", int(z.jaar.min()), int(z.jaar.max()), (int(z.jaar.min()), int(z[~z.deeljaar].jaar.max())))
    regios = st.sidebar.multiselect("Regio", sorted(z.regio.dropna().unique()))
    segmenten = st.sidebar.multiselect("Segment (regels)", sorted(z.regelsegment.dropna().unique()))
    hele = st.sidebar.checkbox("Alleen hele jaren", value=True)
    maat = st.sidebar.selectbox("Maat", list(MATEN), format_func=MATEN.get)
    d = filter_zonejaar(z, jaren, regios, segmenten, hele_jaren=hele)
    jaar = int(d.jaar.max()) if len(d) else jaren[1]
    st.sidebar.caption(f"{d.biedzone.nunique()} zones, {len(d)} zone-jaren in de selectie. Leeg filter = alles.")

    st.title("Waar verdient zon nog, en waar opslag?")
    st.caption(f"Stand {jaar}; verschil tegenover {jaar - 1}. Mediaan over de gekozen zones.")
    kolommen = st.columns(4)
    for kolom, (sleutel, (waarde, delta)) in zip(kolommen, kerncijfers(d, jaar).items()):
        opmaak = "{:.2f}" if sleutel == "capture_zon" else "{:,.0f}"
        kolom.metric(MATEN[sleutel], opmaak.format(waarde) if waarde == waarde else "geen data",
                     opmaak.format(delta) if delta == delta else None, delta_color="inverse" if sleutel == "negatieve_uren" else "normal")

    overzicht, tijd, scenario, tabel = st.tabs(["Overzicht", "Tijd", "Rekenhulp", "Data"])

    with overzicht:
        links, rechts = st.columns((3, 2))
        nu = d[d.jaar == jaar]
        fig = px.scatter(nu, x="capture_zon", y="batterij_per_mw", color="regelsegment", color_discrete_map=SEGMENTKLEUR, hover_name="land",
                         custom_data=["biedzone"], hover_data={"biedzone": True, "negatieve_uren": True, "dagspreiding": ":.0f", "regelsegment": False},
                         labels={"capture_zon": "capture rate zon", "batterij_per_mw": "batterij 2 uur (euro per MW per jaar)", "regelsegment": "segment"},
                         title=f"Zon tegen opslag per zone, {jaar}")
        fig.update_traces(marker={"size": 11, "line": {"width": 1.5, "color": "white"}})
        fig.update_layout(legend={"orientation": "h", "y": -0.2}, margin={"t": 50, "r": 10})
        gekozen = links.plotly_chart(fig, **BREED, on_select="rerun", selection_mode=("points", "box", "lasso"), key="spreiding")
        punten = gekozen.get("selection", {}).get("points", []) if isinstance(gekozen, dict) else []
        zones = sorted({p.get("customdata", [None])[0] for p in punten if p.get("customdata")}) or None
        r = rangorde(d if not zones else d[d.biedzone.isin(zones)], jaar, maat)
        balk = px.bar(r.sort_values(maat), x=maat, y="biedzone", orientation="h", color_discrete_sequence=[KLEUREN[0]], labels={maat: MATEN[maat], "biedzone": ""},
                      title=f"{MATEN[maat]}, {jaar}" + (" (selectie)" if zones else ""))
        balk.update_layout(height=max(320, 18 * len(r) + 120), margin={"t": 50, "r": 10})
        rechts.plotly_chart(balk, **BREED)
        st.caption("Selecteer punten in de linkergrafiek (lasso of rechthoek) om de rangorde rechts en het tabblad Tijd te beperken.")
        st.session_state["zones"] = zones

    with tijd:
        keuze = st.multiselect("Zones", sorted(d.biedzone.unique()), default=st.session_state.get("zones") or [x for x in ("NL", "DE-LU", "ES", "IT-North") if x in set(d.biedzone)])
        reeks = filter_zonejaar(z, jaren, zones=keuze, hele_jaren=hele)
        fig = px.line(reeks.sort_values("jaar"), x="jaar", y=maat, color="biedzone", markers=True, color_discrete_sequence=KLEUREN, labels={maat: MATEN[maat], "biedzone": "zone"},
                      title=f"{MATEN[maat]} per jaar")
        fig.update_layout(hovermode="x unified", margin={"t": 50, "r": 10})
        st.plotly_chart(fig, **BREED)
        if len(keuze) > 8:
            st.info("Meer dan acht zones: de kleuren herhalen zich. Beperk de keuze of gebruik de rangorde.")
        mnd = data["maand"]
        if not mnd.empty and keuze:
            landen = z[z.biedzone.isin(keuze)].land.unique()
            m = mnd[mnd.land.isin(landen) & mnd.jaar.between(*jaren)].assign(periode=lambda t: pd.to_datetime(t.jaar.astype(str) + "-" + t.maand.astype(str) + "-01"))
            fig = px.line(m.sort_values("periode"), x="periode", y="gem_prijs", color="land", color_discrete_sequence=KLEUREN, labels={"gem_prijs": "prijs (euro per MWh)", "periode": ""},
                          title="Maandprijs")
            fig.update_layout(hovermode="x unified", margin={"t": 50, "r": 10})
            st.plotly_chart(fig, **BREED)

    with scenario:
        st.subheader("Dekt zon zonder contract zijn kosten?")
        a, b, c = st.columns(3)
        prijs = a.slider("Gemiddelde prijs (euro per MWh)", 40, 200, 87)
        capture = b.slider("Capture rate zon", 0.25, 1.00, 0.52, 0.01)
        lcoe = c.slider("Kosten per MWh (LCOE)", 25, 80, 51)
        marge, nodig = marge_zon(prijs, capture, lcoe)
        a.metric("Capture-prijs", f"{prijs * capture:,.0f} euro")
        b.metric("Marge per MWh", f"{marge:+,.0f} euro")
        c.metric("Capture rate nodig", f"{nodig:.2f}")
        st.subheader("Wat verdient een batterij bij deze dagspreiding?")
        snij, helling = lijn_batterij(d)
        spreiding = st.slider("Dagspreiding (euro per MWh)", 20, 300, int(d[d.jaar == jaar].dagspreiding.median()) if len(d) else 120)
        st.metric("Batterij 2 uur op de dagmarkt", f"{snij + helling * spreiding:,.0f} euro per MW per jaar", help="Rechte lijn door de gekozen zone-jaren; zonder balanceringsmarkten en netkosten.")
        sc = data["scenario"]
        if not sc.empty:
            st.dataframe(sc[sc.jaar == 2030][["scenario", "prijs_eur_mwh", "capture_rate_zon", "lcoe_eur_mwh", "marge_eur_mwh", "batterij_dagmarkt_per_mw"]].round(2), hide_index=True)

    with tabel:
        kol = ["land", "biedzone", "regio", "jaar", "regelsegment"] + list(MATEN)
        st.dataframe(d[kol].sort_values(["jaar", "biedzone"]), hide_index=True, height=480)
        st.download_button("Download selectie als csv", d[kol].to_csv(index=False).encode("utf-8"), "selectie.csv", "text/csv")


if __name__ == "__main__":
    main()
