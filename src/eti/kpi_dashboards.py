"""KPI-tegels voor dashboards 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14 en 15 volgens de ontwerpnorm (bouwgids, sectie "Ontwerpnorm").

Elke tegel: waarde, vergelijking met de vorige periode, een referentie (EU-mediaan, doel of andere bron) en een richting
(goed, slecht, neutraal) die de kleur van de pijl bepaalt. Zo haalt elk dashboard de 5-secondentest zonder nawerk.
  t50_kpi_dashboards.csv   Dashboard, Volgorde, KPI, Waarde, Tekst, Vergelijking, Referentie, Richting
Gebruik:  PYTHONPATH=src python3 -m eti.kpi_dashboards
"""
from pathlib import Path
import pandas as pd

D = Path("tableau/data")


def _r(dash, nr, kpi, waarde, tekst, vergelijking, referentie, richting):
    return dict(Dashboard=dash, Volgorde=nr, KPI=kpi, Waarde=waarde, Tekst=tekst, Vergelijking=vergelijking,
                Referentie=referentie, Richting=richting)


def dashboard2():
    t10 = pd.read_csv(D / "t10_dekking_nl.csv")
    ir = t10[t10.Scenario.str.startswith("LCOE 2024 IRENA")]
    t10 = t10[t10.Scenario.str.startswith("LCOE 2025")]
    g = t10[t10["Status zon"] == "Gedekt"].set_index("Jaar")["Maanden"]; n = t10.groupby("Jaar")["Maanden"].sum()
    j = int(n.index.max())
    k = pd.read_csv(D / "t47_kpi_nl.csv").set_index(["KPI", "Jaar"])
    cr, pr = k.loc[("Capture rate zon", j)], k.loc[("Gemiddelde prijs", j)]
    s = pd.read_csv(D / "t9_signalering_zones.csv"); laatste = s.Maand.max(); sl = s[s.Maand == laatste]
    nl = sl[sl.Zone == "NL"].iloc[0]
    return [
        _r(2, 1, "Maanden kosten gedekt", g.get(j, 0), f"{g.get(j, 0)} van {n[j]}", f"{j-1}: {g.get(j-1, 0)} van {n[j-1]}",
           f"LCOE 2025: 67,39 EUR/MWh; IRENA 2024: {ir[(ir['Status zon'] == 'Gedekt') & (ir.Jaar == j)]['Maanden'].sum()} van {n[j]}", "goed" if g.get(j, 0) / n[j] > g.get(j - 1, 0) / n[j - 1] else "slecht"),
        _r(2, 2, "Capture rate zon NL", cr["Waarde NL"], f"{cr['Waarde NL']:.2f}", f"{j-1}: {cr['Vorig jaar']:.2f}",
           f"EU-mediaan {cr['EU-mediaan']:.2f}", "goed" if cr["Verschil"] > 0 else "slecht"),
        _r(2, 3, "Gemiddelde prijs NL", pr["Waarde NL"], f"{pr['Waarde NL']:.0f} EUR/MWh", f"{j-1}: {pr['Vorig jaar']:.0f}",
           f"EU-mediaan {pr['EU-mediaan']:.0f}", "neutraal"),
        _r(2, 4, "Prijssignaal laatste maand", nl["Prijs z-score"], f"{nl['Prijs signaal']} (z = {nl['Prijs z-score']:.1f})",
           f"maand {laatste[:7]}", f"{(sl['Prijs signaal'] == 'Schok').sum()} van {len(sl)} zones Schok",
           "slecht" if nl["Prijs signaal"] == "Schok" else "neutraal"),
    ]


def dashboard3():
    t6 = pd.read_csv(D / "t6_kern_gebied_jaar.csv").set_index(["Gebied", "Jaar", "Bron"])["Opwek TWh"]
    t7 = pd.read_csv(D / "t7_kern_land.csv"); t8 = pd.read_csv(D / "t8_kern_markt.csv")
    cr = t8[t8.Jaar == 2025].groupby("Bron")["Capture rate"].mean()
    koers = t7["Koers kern"].value_counts()
    return [
        _r(3, 1, "Wereld: kern tegen zon", t6[("Wereld", 2025, "Kernenergie")],
           f"{t6[('Wereld', 2025, 'Kernenergie')]:,.0f} tegen {t6[('Wereld', 2025, 'Zon')]:,.0f} TWh",
           f"2015 zon: {t6[('Wereld', 2015, 'Zon')]:,.0f} TWh", "Ember, 2025", "neutraal"),
        _r(3, 2, "Europa: kern tegen zon", t6[("Europa", 2025, "Kernenergie")],
           f"{t6[('Europa', 2025, 'Kernenergie')]:,.0f} tegen {t6[('Europa', 2025, 'Zon')]:,.0f} TWh",
           f"2015 kern: {t6[('Europa', 2015, 'Kernenergie')]:,.0f} TWh", "Ember, 2025", "neutraal"),
        _r(3, 3, "Marktwaarde kern tegen zon", cr.get("Kernenergie"), f"{cr.get('Kernenergie'):.2f} tegen {cr.get('Zon'):.2f}",
           "capture rate 2025", "1,00 = gemiddeld uur", "neutraal"),
        _r(3, 4, "Landen uitbouw tegen afbouw", koers.get("Uitbouw", 0),
           f"{koers.get('Uitbouw', 0)} uitbouw, {koers.get('Afbouw', 0) + koers.get('Gestopt', 0)} afbouw of gestopt",
           f"{koers.get('Herstart', 0)} herstart, {koers.get('Stabiel', 0)} stabiel", "regel: >=10% en 2 TWh", "neutraal"),
    ]


def dashboard4():
    e = pd.read_csv(D / "t11_ervaringscurve.csv").set_index("Jaar")["Prijs USD per W"]
    lc = pd.read_csv(D / "t45_leercurve.csv").set_index("Variant")
    p = pd.read_csv(D / "t12_portefeuille.csv")
    ster = p[p.Kwadrant == "Ster"].groupby("Moment").Landcode.apply(lambda s: ", ".join(sorted(s)))
    nl = p[p.Landcode == "NLD"].set_index("Moment")["Kwadrant"]
    a = lc.loc["alle jaren"]
    return [
        _r(4, 1, "Leersnelheid", a.Leersnelheid, f"{a.Leersnelheid:.0%} per verdubbeling",
           f"95%: {a['Interval laag']:.0%}-{a['Interval hoog']:.0%}", "ITRPV 1976-2025: 26%", "goed"),
        _r(4, 2, "Paneelprijs", e[2025], f"{e[2025]:.3f} USD/W", f"2024: {e[2024]:.3f} ({e[2025]/e[2024]-1:+.0%})",
           "exportwaarde China", "goed"),
        _r(4, 3, "Sterren 2025", len(ster[2025].split(", ")), ster[2025], f"2022: {ster[2022]}", "groei > 30%/jaar", "neutraal"),
        _r(4, 4, "Nederland", None, nl[2025], f"2022: {nl[2022]}", "verzadiging, netcongestie", "slecht"),
    ]


def dashboard7():
    """Vanaf 19 november alleen Engels (zie _e)."""
    c = pd.read_csv(D / "t15_controles.csv"); r = pd.read_csv(D / "t16_risico.csv")
    from eti.vertaal_en import vertaal
    gesl = c.Status.str.startswith("Geslaagd").sum(); openl = c[c.Status.isin(["Open", "Afwijking open"])]
    live = (c["Opnieuw berekend"] == "ja").sum(); top = r.sort_values("Score", ascending=False).iloc[0]
    return [
        _e(7, 1, "Controls passed", gesl, f"{gesl} of {len(c)}", "18 Nov: 6 of 12", f"target: all {len(c)}", "good"),
        _e(7, 2, "Still open", len(openl), f"{len(openl)}", ", ".join(openl.Controle), "target: 0 before publication",
           "bad" if len(openl) else "good"),
        _e(7, 3, "Recalculated in every run", live, f"{live} of {len(c)}", "automatic in run_analyse.sh", "rest: recorded by hand", "neutral"),
        _e(7, 4, "Largest risk", top.Score, f"score {top.Score} of 9", vertaal(top.Risico) or top.Risico,
           vertaal(top.Maatregel) or top.Maatregel, "bad"),
    ]


# Vanaf dashboard 5 verschijnen de dashboards alleen in het Engels (besluit 19 november): deze tegels zijn direct Engels
# en worden door eti.vertaal_en ongewijzigd overgenomen. Richting: good / bad / neutral.
def _e(dash, nr, kpi, waarde, tekst, vergelijking, referentie, richting):
    return _r(dash, nr, kpi, waarde, tekst, vergelijking, referentie, {"good": "goed", "bad": "slecht", "neutral": "neutraal"}[richting])


def _land(naam):
    """Nederlandse land- of locatienaam naar Engels, met het woordenboek van eti.vertaal_en."""
    from eti.vertaal_en import vertaal
    return vertaal(naam) or naam


def dashboard5():
    k = pd.read_csv(D / "t13_kostencurve.csv")
    winst = (k["Marge EUR/MWh"] > 0).sum()
    pot_m, pot_g = k["Potentieel Mt (marginale factor)"].sum(), k["Potentieel Mt (gemiddelde factor)"].sum()
    # standaard = marginale factor (zon verdringt gas); zelfde keuze als de parameter in Tableau en dashboard 25
    best = k.sort_values("Kosten per ton (marginale factor)").iloc[0]
    nl = k[k.Landcode == "NLD"].iloc[0]
    return [
        _e(5, 1, "Countries abating CO2 at a profit", winst, f"{winst} of {len(k)}", "solar capture price above LCOE (IRENA 2024), 2025",
           "negative cost per tonne", "good"),
        _e(5, 2, "Abatement potential to 2030", pot_m, f"{pot_m:.0f} Mt CO2/yr", f"average grid factor: {pot_g:.0f} Mt",
           "marginal factor (gas)", "neutral"),
        _e(5, 3, "Cheapest abatement", best["Kosten per ton (marginale factor)"], f"{_land(best.Land)}: {best['Kosten per ton (marginale factor)']:.0f} EUR/t",
           f"average factor: {best['Kosten per ton (gemiddelde factor)']:.0f} EUR/t", "EU ETS: 74 avg 2025, about 90 in Nov 2026", "good"),
        _e(5, 4, "Netherlands", nl["Kosten per ton (marginale factor)"], f"{nl['Kosten per ton (marginale factor)']:.0f} EUR/t",
           f"average factor: {nl['Kosten per ton (gemiddelde factor)']:.0f} EUR/t", f"margin {nl['Marge EUR/MWh']:.0f} EUR/MWh",
           "bad" if nl["Marge EUR/MWh"] < 0 else "good"),
    ]


def dashboard8():
    s = pd.read_csv(D / "t37_nl_stroom.csv").set_index(["Bron", "Jaar"])
    z25, z24 = s.loc[("Zonnestroom", 2025)], s.loc[("Zonnestroom", 2024)]
    a = pd.read_csv(D / "t51_congestie_afstemming.csv").set_index("Wachtrij")
    r = pd.read_csv(D / "t40_res_regio.csv")
    r = r[r["RES-regio"] == "Nederland"].set_index("Jaar")["Zon MWp"]  # totaalregel; niet optellen (dubbel)
    g25, g24 = r[2025] / r[2024] - 1, r[2024] / r[2023] - 1
    f = pd.read_csv(D / "t25_flex_nl.csv").set_index("Jaar")["Negatieve uren"]
    return [
        _e(8, 1, "Solar share of Dutch power", z25["Aandeel verbruik %"], f"{z25['Aandeel verbruik %']:.0f}%",
           f"2024: {z24['Aandeel verbruik %']:.0f}%", "CBS, 2025 provisional", "good"),
        _e(8, 2, "Solar capacity growth", g25, f"{g25:+.0%} in 2025", f"2024: {g24:+.0%}", f"{r[2025]/1000:.1f} GWp (RES monitor)",
           "bad" if g25 < g24 else "good"),
        _e(8, 3, "Regional queue, offtake", a.loc["Regionaal, afname", "Ons project GW"],
           f"{a.loc['Regionaal, afname', 'Ons project GW']:.1f} GW", f"official: {a.loc['Regionaal, afname', 'Officieel GW']:.1f} GW",
           "capacity map 2026 vs queue July 2025", "bad"),
        _e(8, 4, "Negative-price hours", f[2025], f"{f[2025]:.0f} h", f"2024: {f[2024]:.0f} h", f"2026 to 15 Nov: {f[2026]:.0f} h",
           "bad"),
    ]


def dashboard9():
    c = pd.read_csv(D / "t18_convergentie.csv"); c["Jaar"] = c.Maand.str[:4].astype(int)
    l = c.iloc[-1]; vj = c[c.Maand == f"{int(l.Maand[:4]) - 1}{l.Maand[4:]}"].iloc[0]
    j19 = c[c.Jaar == 2019]["Relatieve spreiding"].mean(); jl = c[c.Jaar == int(l.Maand[:4])]["Relatieve spreiding"].mean()
    return [
        _e(9, 1, "Median zone price", l.Mediaan, f"{l.Mediaan:.0f} EUR/MWh", f"{vj.Maand[:7]}: {vj.Mediaan:.0f}",
           f"{int(l.Zones)} zones, {l.Maand[:7]}", "neutral"),
        _e(9, 2, "Spread P90-P10", l["Spreiding P90-P10"], f"{l['Spreiding P90-P10']:.0f} EUR/MWh",
           f"{vj.Maand[:7]}: {vj['Spreiding P90-P10']:.0f}", "gap between expensive and cheap zones",
           "bad" if l["Spreiding P90-P10"] > vj["Spreiding P90-P10"] else "good"),
        _e(9, 3, "Relative spread, year average", jl, f"{jl:.2f}", f"2019: {j19:.2f}", "(P90-P10) / median",
           "bad" if jl > j19 else "good"),
        _e(9, 4, "Months more divergent than 2019", (c[c.Jaar > 2019]["Relatieve spreiding"] > j19).sum(),
           f"{(c[c.Jaar > 2019]['Relatieve spreiding'] > j19).sum()} of {(c.Jaar > 2019).sum()}", "relative spread above 2019 average",
           "2020-2026", "neutral"),
    ]


def dashboard10():
    v = pd.read_csv(D / "t33_vs_voorraad.csv").set_index("Snapshot"); l = v.index[-1]; vj = f"{int(l[:4]) - 1}{l[4:]}"
    g = pd.read_csv(D / "t36_vs_gepland.csv"); bouw = g[(g.Groep == "Batterij") & g.Status.isin(["U", "V", "TS"])]["Nameplate Capacity (MW)"].sum() / 1000
    st = pd.read_csv(D / "t21_vs_staten.csv").query("Staat != 'Washington, D.C.'").sort_values("Aandeel zon %", ascending=False).iloc[0]
    return [
        _e(10, 1, "Utility solar", v.loc[l, "Zon GW"], f"{v.loc[l, 'Zon GW']:.0f} GW", f"{vj}: {v.loc[vj, 'Zon GW']:.0f} GW",
           f"EIA-860M, {l}", "good"),
        _e(10, 2, "Utility batteries", v.loc[l, "Batterij GW"], f"{v.loc[l, 'Batterij GW']:.0f} GW", f"{vj}: {v.loc[vj, 'Batterij GW']:.0f} GW",
           f"{v.loc[l, 'Batterij uren']:.1f} hours of storage", "good"),
        _e(10, 3, "Batteries under construction", bouw, f"{bouw:.0f} GW", "status U, V or TS", "EIA-860M planned units", "good"),
        _e(10, 4, "Highest solar share", st["Aandeel zon %"], f"{st.Staat}: {st['Aandeel zon %']:.0f}%",
           f"solar and wind: {st['Aandeel zon en wind %']:.0f}%", f"state level, {int(st.Jaar)}", "neutral"),
    ]


def dashboard11():
    e = pd.read_csv(D / "t22_china_export.csv")
    j = e.groupby("Jaar").agg(GW=("GW", "sum"), USD=("USD miljard", "sum"), Maanden=("Maanden", "max"))
    l = int(j.index.max()); per = j.GW / j.Maanden * 12
    prijs = j.USD / j.GW
    top = e[e.Jaar == l].sort_values("GW", ascending=False).iloc[0]
    return [
        _e(11, 1, "Module exports, annualised", per[l], f"{per[l]:.0f} GW/yr", f"{l-1}: {j.GW[l-1]:.0f} GW",
           f"{l}: {int(j.Maanden[l])} months of data", "good" if per[l] > j.GW[l - 1] else "neutral"),
        _e(11, 2, "Export price", prijs[l], f"{prijs[l]:.3f} USD/W", f"{l-1}: {prijs[l-1]:.3f} ({prijs[l]/prijs[l-1]-1:+.0%})",
           f"2017: {prijs[2017]:.3f}", "good"),
        _e(11, 3, "Largest destination", top.GW, f"{top.Bestemming}", f"{top.GW:.0f} GW in {l}",
           f"{top.GW / j.GW[l]:.0%} of exports", "neutral"),
        _e(11, 4, "Export value", j.USD[l], f"{j.USD[l]:.1f} bn USD", f"{l-1}: {j.USD[l-1]:.1f} bn",
           f"annualised: {j.USD[l] / j.Maanden[l] * 12:.1f} bn", "neutral"),
    ]


def dashboard13():
    f = pd.read_csv(D / "t25_flex_nl.csv").set_index("Jaar")
    ev = pd.read_csv(D / "t26_ev_net.csv").set_index("Land").loc["Netherlands"]
    return [
        _e(13, 1, "Negative-price hours", f.loc[2025, "Negatieve uren"], f"{f.loc[2025, 'Negatieve uren']:.0f} h",
           f"2024: {f.loc[2024, 'Negatieve uren']:.0f} h", f"2026 to 15 Nov: {f.loc[2026, 'Negatieve uren']:.0f} h", "bad"),
        _e(13, 2, "Imbalance price, 99th percentile", f.loc[2025, "Op P99"], f"{f.loc[2025, 'Op P99']:.0f} EUR/MWh",
           f"{f.loc[2025, 'Aandeel op boven 200 %']:.1f}% of quarters above 200", "upward regulation, 2025", "good"),
        _e(13, 3, "Electric cars", ev["EV-vloot"], f"{ev['EV-vloot']/1e6:.2f} million", f"{ev['Vraag GWh per jaar']/1000:.1f} TWh/yr demand",
           f"data to {ev['Latest available date'][:7]}", "good"),
        _e(13, 4, "Smart charging at midday", ev["Middagafname gestuurd GW (aanname)"], f"{ev['Middagafname gestuurd GW (aanname)']:.1f} GW",
           f"unmanaged evening peak: {ev['Piek ongestuurd GW (aanname)']:.1f} GW", "assumption, see method", "neutral"),
    ]


def dashboard14():
    i = pd.read_csv(D / "t27_impact.csv").set_index(["Regio", "Jaar"])
    c = pd.read_csv(D / "t39_vermeden_co2.csv").set_index(["Bron", "Jaar"])["Vermeden CO2 kton"]
    nl, ind = i.loc[("Nederland", 2025)], i.loc[("India (RvdW)", 2025)]
    return [
        _e(14, 1, "CO2 per million EUR, Netherlands", nl["Ton CO2 per M EUR per jaar"], f"{nl['Ton CO2 per M EUR per jaar']:.0f} t/yr",
           f"India: {ind['Ton CO2 per M EUR per jaar']:.0f} t/yr", "solar, 2025", "neutral"),
        _e(14, 2, "Dutch solar margin", nl["Marge zon EUR/MWh"], f"{nl['Marge zon EUR/MWh']:.0f} EUR/MWh",
           f"at IRENA 2024 project cost: {nl['Marge zon bij IRENA EUR/MWh']:+.0f} EUR/MWh", "PBL reference project; additionality depends on the cost basis",
           "neutral"),
        _e(14, 3, "CO2 avoided by Dutch renewables", c[("Totaal energiebronnen", 2025)], f"{c[('Totaal energiebronnen', 2025)]/1000:.1f} Mt",
           f"2024: {c[('Totaal energiebronnen', 2024)]/1000:.1f} Mt", "CBS, provisional", "good"),
        _e(14, 4, "of which solar power", c[("Zonnestroom", 2025)], f"{c[('Zonnestroom', 2025)]/1000:.1f} Mt",
           f"2024: {c[('Zonnestroom', 2024)]/1000:.1f} Mt", "CBS, provisional", "good"),
    ]


def dashboard15():
    z = pd.read_csv(D / "t28_zuiden.csv").sort_values("Vollasturen", ascending=False)
    i = pd.read_csv(D / "t27_impact.csv").set_index(["Regio", "Jaar"])
    ind, nl = i.loc[("India (RvdW)", 2025)], i.loc[("Nederland", 2025)]
    b = z.iloc[0]
    return [
        _e(15, 1, "Best solar site", b.Vollasturen, f"{b.Vollasturen:.0f} full-load hours", f"{_land(b.Locatie)}",
           f"{b['Vollasturen tegen Nederland']:.1f} times the Netherlands", "good"),
        _e(15, 2, "Cost of capital, India", ind.WACC, f"{ind.WACC:.1%}", f"Netherlands: {nl.WACC:.1%}", "model assumption; IEA 2024: 10.0-11.5%", "bad"),
        _e(15, 3, "Indian LCOE at Dutch WACC", ind["LCOE bij 5% WACC"], f"{ind['LCOE bij 5% WACC']:.0f} EUR/MWh",
           f"now: {ind['LCOE EUR/MWh']:.0f} EUR/MWh", f"{1 - ind['LCOE bij 5% WACC']/ind['LCOE EUR/MWh']:.0%} cheaper", "good"),
        _e(15, 4, "Sites with 1.5x Dutch sun", (z["Vollasturen tegen Nederland"] >= 1.5).sum(),
           f"{(z['Vollasturen tegen Nederland'] >= 1.5).sum()} of {len(z)}", "PVGIS, 11 years", "same panel, more output", "neutral"),
    ]


def dashboard6():
    w = pd.read_csv(D / "t60_value_chain.csv")
    china = w[w.Group == "China"]; mod = china[china.Segment == "Modules"]
    verlies = china[china["Net margin %"] < 0]
    fs = w.set_index("Company").loc["First Solar"]; sg = w.set_index("Company").loc["Sungrow"]
    return [
        _e(6, 1, "Chinese manufacturers in loss", len(verlies), f"{len(verlies)} of {len(china)}", "polysilicon, wafers, modules",
           f"combined net loss {-verlies['Net income USD bn'].sum():.1f} bn USD", "bad"),
        _e(6, 2, "Module makers, net margin", mod["Net margin %"].mean(), f"{mod['Net margin %'].mean():.0f}%",
           f"range {mod['Net margin %'].min():.0f}% to {mod['Net margin %'].max():.0f}%", "Trina, JA, Jinko, 2025", "bad"),
        _e(6, 3, "Inverters and storage", sg["Net margin %"], f"{sg['Net margin %']:.0f}% (Sungrow)", "storage is 42% of revenue",
           f"Enphase: {w.set_index('Company').loc['Enphase', 'Net margin %']:.0f}%", "good"),
        _e(6, 4, "Protected market", fs["Net margin %"], f"{fs['Net margin %']:.0f}% (First Solar)", "US tax credits (45X) included",
           "IEA: 10-15% outside China", "neutral"),
    ]


def dashboard17():
    p = pd.read_csv(D / "t61_ppa_prices.csv"); m = pd.read_csv(D / "t62_ppa_vs_merchant.csv").set_index("Country")
    lt = p[p.Index == "P25 continental index"].sort_values("Date"); l, b = lt.iloc[-1], lt.iloc[0]
    es = p[(p.Market == "Spain")].sort_values("Date").iloc[-1]
    return [
        _e(17, 1, "European solar PPA (P25)", l["Price EUR/MWh"], f"{l['Price EUR/MWh']:.0f} EUR/MWh", f"{b.Period}: {b['Price EUR/MWh']:.0f}",
           f"LevelTen, {l.Period}", "bad"),
        _e(17, 2, "Spain solar PPA", es["Price EUR/MWh"], f"{es['Price EUR/MWh']:.0f} EUR/MWh", f"{es.Period}", "lowest LevelTen country", "bad"),
        _e(17, 3, "Germany: PPA vs market", m.loc["Germany", "PPA minus capture price"], f"{m.loc['Germany', 'PPA minus capture price']:+.0f} EUR/MWh",
           f"PPA {m.loc['Germany', 'PPA P25 Q4 2025 EUR/MWh']:.0f} vs capture {m.loc['Germany', 'Solar capture price EUR/MWh']:.0f}",
           "2025; positive = PPA pays more", "good"),
        _e(17, 4, "Hybrid PPA premium", 24, "+24%", "solar plus storage vs solar only", "LevelTen, Q2 2026", "good"),
    ]


def dashboard16():
    d = pd.read_csv(D / "t54_duck_depth.csv"); j = 2025; a = d[d.Year == j]; v = d[d.Year == j - 2]
    top = a.sort_values("Midday dip EUR/MWh", ascending=False).iloc[0]; nl = a.set_index("Zone").loc["NL"]; nlv = v.set_index("Zone").loc["NL"]
    return [
        _e(16, 1, "Deepest midday dip", top["Midday dip EUR/MWh"], f"{top['Zone name']}: {top['Midday dip EUR/MWh']:.0f} EUR/MWh",
           "day average minus 11-15h price", f"{j}", "bad"),
        _e(16, 2, "Netherlands midday dip", nl["Midday dip EUR/MWh"], f"{nl['Midday dip EUR/MWh']:.0f} EUR/MWh", f"{j-2}: {nlv['Midday dip EUR/MWh']:.0f}",
           "evening is " + f"{nl['Evening to midday ratio']:.1f}x midday", "bad"),
        _e(16, 3, "Zones with a deeper dip than 2023", int((a.set_index("Zone")["Midday dip EUR/MWh"] > v.set_index("Zone")["Midday dip EUR/MWh"]).sum()),
           f"{int((a.set_index('Zone')['Midday dip EUR/MWh'] > v.set_index('Zone')['Midday dip EUR/MWh']).sum())} of {len(a)}", "2025 vs 2023", "Energy-Charts, hourly", "neutral"),
        _e(16, 4, "Median negative hours", a["Negative hours"].median(), f"{a['Negative hours'].median():.0f} h", f"2023: {v['Negative hours'].median():.0f} h",
           f"{len(a)} zones, {j}", "bad"),
    ]


def dashboard18():
    b = pd.read_csv(D / "t55_battery_arbitrage.csv"); j = 2025; a = b[b.Year == j].set_index("Zone"); v = b[b.Year == 2023].set_index("Zone")
    top = a.sort_values("Revenue per MW", ascending=False).iloc[0]
    return [
        _e(18, 1, "Median arbitrage revenue", a["Revenue per MW"].median(), f"{a['Revenue per MW'].median()/1000:.0f}k EUR/MW", f"2023: {v['Revenue per MW'].median()/1000:.0f}k",
           "2-hour battery, 1 cycle/day, perfect foresight", "neutral"),
        _e(18, 2, "Best zone", top["Revenue per MW"], f"{top['Zone name']}: {top['Revenue per MW']/1000:.0f}k EUR/MW", f"{j}", "upper bound, no forecast error", "good"),
        _e(18, 3, "Netherlands", a.loc["NL", "Revenue per MW"], f"{a.loc['NL', 'Revenue per MW']/1000:.0f}k EUR/MW", f"2023: {v.loc['NL', 'Revenue per MW']/1000:.0f}k",
           "t1 (realistic): 61k", "good"),
        _e(18, 4, "Days worth more than 100 EUR/MW", a["Days with margin above 100"].median(), f"{a['Days with margin above 100'].median():.0f} days",
           "median zone", f"{j}", "neutral"),
    ]


def dashboard19():
    h = pd.read_csv(D / "t56_hirth.csv"); r = h[h.Reliable]
    de = h.set_index("Zone").loc["DE-LU"]
    return [
        _e(19, 1, "Median slope", r["Slope per percentage point"].median(), f"{r['Slope per percentage point'].median():.3f}", "capture rate per percentage point solar",
           f"{len(r)} reliable zones", "bad"),
        _e(19, 2, "Germany", de["Slope per percentage point"], f"{de['Slope per percentage point']:.3f}",
           f"95%: {de['Interval low']:.3f} to {de['Interval high']:.3f}", "Hirth (2013): value falls with share", "bad"),
        _e(19, 3, "Capture rate at 30% share", r["Capture rate at 30% share"].median(), f"{r['Capture rate at 30% share'].median():.2f}",
           f"at 10%: {r['Capture rate at 10% share'].median():.2f}", "median of reliable zones", "bad"),
        _e(19, 4, "Zones left out", (~h.Reliable).sum(), f"{(~h.Reliable).sum()} of {len(h)}", "too little solar or poor fit", "rule: share >= 10%, R2 >= 0.4", "neutral"),
    ]


def dashboard20():
    k = pd.read_csv(D / "t57_carbon_free.csv"); a = k[(k.Year == 2025) & k["Solar coverage ok"]].set_index("Zone")
    v = k[(k.Year == 2019) & k["Solar coverage ok"]].set_index("Zone")
    beste = a.sort_values("Carbon-free share %", ascending=False).iloc[0]
    return [
        _e(20, 1, "Most carbon-free", beste["Carbon-free share %"], f"{beste['Zone name']}: {beste['Carbon-free share %']:.0f}%",
           f"{beste['Hours above 90% %']:.0f}% of hours above 90%", "nuclear and hydro", "good"),
        _e(20, 2, "Germany", a.loc["DE-LU", "Carbon-free share %"], f"{a.loc['DE-LU', 'Carbon-free share %']:.0f}%",
           f"2019: {v.loc['DE-LU', 'Carbon-free share %']:.0f}%", f"hours above 90%: {a.loc['DE-LU', 'Hours above 90% %']:.0f}%", "neutral"),
        _e(20, 3, "Median zone", a["Carbon-free share %"].median(), f"{a['Carbon-free share %'].median():.0f}%", f"2019: {v['Carbon-free share %'].median():.0f}%",
           f"{len(a)} zones with reliable data", "good"),
        _e(20, 4, "Hours below 50% carbon-free", a["Hours below 50% %"].median(), f"{a['Hours below 50% %'].median():.0f}% of hours",
           f"2019: {v['Hours below 50% %'].median():.0f}%", "median zone; the 24/7 challenge", "good"),
    ]


def dashboard25():
    m = pd.read_csv(D / "t64_avoided_per_mwh.csv"); a = m[m.Year == 2025].set_index("Zone")
    lo, hi, gem = ("Marginal factor, solar hours, domestic t/MWh", "Marginal factor, solar hours, fossil response t/MWh",
                   "Average factor, solar hours t/MWh")
    b = a[a.Reliable]
    neg = b[(b["Battery net CO2 t per MW per year, domestic"] < -5)
            & ~(b["Battery net CO2 t per MW per year, fossil response"] > 0)]       # meer dan 5 t per MW per jaar erbij
    landen = ", ".join(sorted(neg["Zone name"].str.replace(r" \(.*\)$", "", regex=True).unique()))
    return [
        _e(25, 1, "Germany: CO2 avoided per MWh solar", a.loc["DE-LU", hi], f"{a.loc['DE-LU', lo]:.2f}-{a.loc['DE-LU', hi]:.2f} t",
           f"average in solar hours: {a.loc['DE-LU', gem]:.2f} t", "marginal: domestic vs fossil response", "neutral"),
        _e(25, 2, "Poland: CO2 avoided per MWh solar", a.loc["PL", hi], f"{a.loc['PL', lo]:.2f}-{a.loc['PL', hi]:.2f} t",
           f"average in solar hours: {a.loc['PL', gem]:.2f} t", "coal sets the margin", "good"),
        _e(25, 3, "Countries where a battery adds CO2", len(set(neg.Country)), f"{len(set(neg.Country))} of {b.Country.nunique()}",
           landen + ": more than 5 t/MW/yr", "both methods agree; 2025, reliable data", "bad"),
        _e(25, 4, "Netherlands", float("nan"), "not measurable", f"Energy-Charts: {a.loc['NL', 'Others share %']:.0f}% unclassified",
           "use CBS/Ember: 0.25 t/MWh", "neutral"),
    ]


def dashboard27():
    t = pd.read_csv(D / "t67_fund_portfolios.csv").set_index("Portfolio")
    se, so, bo = t.loc["South and east"], t.loc["Solar only"], t.loc["Batteries only"]
    lo = so["CO2 per M EUR per year, marginal domestic"] / bo["CO2 per M EUR per year, marginal domestic"]
    hi = so["CO2 per M EUR per year, marginal fossil response"] / bo["CO2 per M EUR per year, marginal fossil response"]
    nw = t.loc["North and west"]
    return [
        _e(27, 1, "Best project return (median)", se["Project IRR P50"], f"{se['Project IRR P50']:.1%}",
           f"P10-P90: {se['Project IRR P10']:.1%} to {se['Project IRR P90']:.1%}", "South and east: solar south + batteries east", "good"),
        _e(27, 2, "Fund net return after fees", se["Fund net IRR (P50)"], f"{se['Fund net IRR (P50)']:.1%}", "hurdle 8%",
           "2% fee, 20% carry, 10-year fund", "bad"),
        _e(27, 3, "CO2 per euro: solar vs batteries", hi, f"{lo:.0f}-{hi:.0f}x", "solar avoids more CO2 per euro",
           "marginal factor, domestic vs fossil response", "neutral"),
        _e(27, 4, "Chance of beating 8%", se["Share of draws above 8%"], f"{se['Share of draws above 8%']:.0%}",
           f"North and west: {nw['Share of draws above 8%']:.0%}", "1,000 Monte Carlo draws", "neutral"),
    ]


def dashboard28():
    t = pd.read_csv(D / "t69_world_duck_depth.csv"); a = t[t.Year == 2025].set_index("Market")
    sa, ca, nl = a.loc["South Australia (AEMO)"], a.loc["California (CAISO SP15)"], a.loc["Netherlands"]
    nl19 = t[(t.Market == "Netherlands") & (t.Year == 2019)].iloc[0]
    return [
        _e(28, 1, "South Australia: midday price", sa["Midday index 11-15h"], f"{sa['Midday index 11-15h']:.0%} of average",
           f"negative {sa['Negative hours %']:.0f}% of hours", "2025, AEMO", "bad"),
        _e(28, 2, "California: midday price", ca["Midday index 11-15h"], f"{ca['Midday index 11-15h']:.0%} of average",
           f"negative {ca['Negative hours %']:.0f}% of hours", "2025, CAISO SP15", "bad"),
        _e(28, 3, "Netherlands: midday price", nl["Midday index 11-15h"], f"{nl['Midday index 11-15h']:.0%} of average",
           f"2019: {nl19['Midday index 11-15h']:.0%}", "2025, Energy-Charts", "bad"),
        _e(28, 4, "Netherlands: negative hours", nl["Negative hours %"], f"{nl['Negative hours %']:.1f}% of hours",
           f"South Australia: {sa['Negative hours %']:.0f}%", "where Europe is heading", "neutral"),
    ]


def dashboard26():
    t = pd.read_csv(D / "t70_revenue_at_risk.csv").set_index("Country")
    top = t.sort_values("Revenue at risk M EUR per year", ascending=False).iloc[0]
    med = t[~t["Target already met"]]["Revenue at risk EUR/MWh"].median()
    return [
        _e(26, 1, "Median revenue at risk", med, f"{med:.0f} EUR/MWh", "if 2030 solar targets are met", "price level of 2025 held constant", "bad"),
        _e(26, 2, "Largest in euros", top["Revenue at risk M EUR per year"], f"{top.name}: {top['Revenue at risk M EUR per year'] / 1000:.1f} bn EUR/yr",
           f"{top['Revenue at risk EUR/MWh']:.0f} EUR/MWh on {top['Solar TWh 2030']:.0f} TWh", "Hirth slope x extra solar share", "bad"),
        _e(26, 3, "Italy keeps the most value", t.at["Italy", "Capture rate 2030"], f"capture rate {t.at['Italy', 'Capture rate 2030']:.2f}",
           f"2025: {t.at['Italy', 'Capture rate 2025']:.2f}",
           f"{(~t['Below own-model LCOE in 2030']).sum()} of {len(t)} stay above country cost in 2030; {(~t['Below LCOE in 2030']).sum()} at IRENA cost", "good"),
        _e(26, 4, "Extrapolated beyond the data", (~t["Within observed range"]).sum(), f"{(~t['Within observed range']).sum()} of {len(t)} countries",
           "2030 share above the highest monthly share seen", "read as a stress test, not a forecast", "neutral"),
    ]


def dashboard29():
    t = pd.read_csv(D / "t71_battery_strategies.csv"); a = t[t.Year == 2025].set_index("Zone")
    y, f = "Yesterday's prices vs perfect", "Fixed schedule vs perfect"
    bal = a[a["Zone name"].isin(["Estonia", "Latvia", "Lithuania"])]
    return [
        _e(29, 1, "No-forecast strategy captures", a[y].median(), f"{a[y].median():.0%} of the ceiling",
           "trade on yesterday's prices (a floor)", "median of 37 zones, 2025", "neutral"),
        _e(29, 2, "Netherlands", a.loc["NL", y], f"{a.loc['NL', y]:.0%}", f"{a.loc['NL', 'Yesterday' + chr(39) + 's prices EUR/MW'] / 1000:.0f}k vs {a.loc['NL', 'Perfect foresight EUR/MW'] / 1000:.0f}k EUR/MW",
           "perfect foresight is the upper bound", "neutral"),
        _e(29, 3, "Baltics: hardest to forecast", bal[y].mean(), f"{bal[y].mean():.0%}", "Estonia, Latvia, Lithuania",
           "highest upper bound, lowest capture", "bad"),
        _e(29, 4, "Fixed duck schedule", a[f].median(), f"{a[f].median():.0%}", "charge 11-13h, discharge 18-20h",
           f"a rule of thumb leaves {1 - a[f].median():.0%} on the table", "neutral"),
    ]


def dashboard30():
    t = pd.read_csv(D / "t72_forecast_baseline.csv"); a = t[t.Year == 2025].set_index("Zone")
    m = pd.read_csv(D / "t73_forecast_model.csv"); m = m[m.Year == 2025].set_index("Zone")
    nl = m.loc["NL"]; wint = int(m["Model beats yesterday"].sum())
    return [
        _e(30, 1, "Model error (NL)", nl["MAE model EUR/MWh"], f"{nl['MAE model EUR/MWh']:.0f} EUR/MWh",
           f"yesterday's prices: {nl['MAE yesterday EUR/MWh']:.0f} EUR/MWh", "MAE per hour, test year 2025", "good"),
        _e(30, 2, "Zones where the model wins", wint, f"{wint} of {len(m)}", f"median improvement {m['Improvement vs yesterday %'].median():.0f}%",
           "trained on 2019-2024, tested on 2025", "good"),
        _e(30, 3, "Battery revenue captured", m["Battery model vs perfect"].median(), f"{m['Battery model vs perfect'].median():.0%}",
           f"yesterday's prices: {m['Battery yesterday vs perfect'].median():.0%}", "of perfect foresight, median zone", "good"),
        _e(30, 4, "Without weather and load", nl["MAE lags and calendar only EUR/MWh"], f"{nl['MAE lags and calendar only EUR/MWh']:.0f} EUR/MWh",
           "NL, lagged prices and calendar only", "most of the gain is not from weather", "neutral"),
    ]


def _k(x):
    return f"{x / 1000:.0f}k"


def dashboard32():
    t = pd.read_csv(D / "t92_solar_lcoe_country.csv"); n = len(t)
    lo, hi = t.loc[t["LCOE IRENA EUR/MWh"].idxmin()], t.loc[t["LCOE IRENA EUR/MWh"].idxmax()]
    nl = t.set_index("Country").loc["Netherlands"]
    return [
        _e(32, 1, "Solar earns more than it costs", int((t["Margin IRENA EUR/MWh"] > 0).sum()), f"{int((t['Margin IRENA EUR/MWh'] > 0).sum())} of {n}",
           f"own model: {int((t['Margin own model EUR/MWh'] > 0).sum())}; previous assumption: {int((t['Margin previous assumption EUR/MWh'] > 0).sum())}", "IRENA 2024 cost vs 2025 capture price", "neutral"),
        _e(32, 2, "Cheapest country", lo["LCOE IRENA EUR/MWh"], f"{lo['Country']}: {lo['LCOE IRENA EUR/MWh']:.0f} EUR/MWh",
           f"most expensive: {hi['Country']} {hi['LCOE IRENA EUR/MWh']:.0f}", "IRENA 2024", "good"),
        _e(32, 3, "Netherlands", nl["LCOE IRENA EUR/MWh"], f"{nl['LCOE IRENA EUR/MWh']:.0f} EUR/MWh", f"own model: {nl['LCOE own model EUR/MWh']:.0f}; PBL reference: {nl['LCOE previous assumption EUR/MWh']:.0f}",
           "three cost levels, one country", "neutral"),
        _e(32, 4, "Measured by IRENA", int((t["IRENA basis"] == "IRENA 2024 country data").sum()), f"{int((t['IRENA basis'] == 'IRENA 2024 country data').sum())} of {n}",
           "others: European average 55 EUR/MWh", "country data only for the large markets", "neutral"),
    ]


def dashboard38():
    t = pd.read_csv(D / "t78_solar_battery_hedge.csv"); h = t[t["Reading"].str.startswith("hedge")]
    nl = t.set_index("Zone").loc["NL"]; m = t["Battery MW per solar MW to offset"].median()
    return [
        _e(38, 1, "Zones where the battery hedges solar", len(h), f"{len(h)} of {len(t)}", "solar down, battery up, 2023 to 2025", "day-ahead arbitrage only", "good"),
        _e(38, 2, "Battery needed per MW of solar", m, f"{m:.1f} MW", "median zone", f"at {int(t['Full-load hours assumed'].iloc[0])} full-load hours of solar", "neutral"),
        _e(38, 3, "Netherlands: solar capture price", nl["Solar capture price change"], f"{nl['Solar capture price change']:+.0f} EUR/MWh",
           f"battery revenue {nl['Battery revenue per MW change'] / 1000:+.0f}k EUR/MW", "2023 to 2025", "bad" if nl["Solar capture price change"] < 0 else "good"),
        _e(38, 4, "Correlation capture rate and battery revenue", t["Correlation capture rate vs battery revenue 2019-2025"].median(),
           f"{t['Correlation capture rate vs battery revenue 2019-2025'].median():.2f}", "median zone, 2019-2025", "negative = natural hedge", "neutral"),
    ]


def dashboard39():
    w = pd.read_csv(D / "t85_wacc_by_country.csv"); w = w[w["Technology"] == "Solar PV"]
    c = pd.read_csv(D / "t82_cost_of_capital.csv").set_index("Country")
    lo, hi = w.loc[w["WACC %"].idxmin()], w.loc[w["WACC %"].idxmax()]; ig = w[w["Investment grade"]]; nig = w[~w["Investment grade"]]
    return [
        _e(39, 1, "Cost of capital for solar", w["WACC %"].median(), f"{w['WACC %'].median():.1f}%", f"{lo['Country']} {lo['WACC %']:.1f}% to {hi['Country']} {hi['WACC %']:.1f}%", f"median of {len(w)} countries, IRENA 2024", "neutral"),
        _e(39, 2, "Below investment grade", nig["WACC %"].median(), f"{nig['WACC %'].median():.1f}%", f"investment grade: {ig['WACC %'].median():.1f}%", f"{len(nig)} of {len(w)} countries", "bad"),
        _e(39, 3, "Financing share of solar cost", nig["Financing share of LCOE %"].median(), f"{nig['Financing share of LCOE %'].median():.0f}%",
           f"investment grade: {ig['Financing share of LCOE %'].median():.0f}%", "share of LCOE that pays for capital", "bad"),
        _e(39, 4, "India at European financing", c.loc["India", "Cheaper at European financing %"], f"{c.loc['India', 'Cheaper at European financing %']:.0f}% cheaper",
           f"WACC {c.loc['India', 'WACC %']:.1f}% vs Europe {c.loc['Europe', 'WACC %']:.1f}%", "IEA Cost of Capital Observatory", "good"),
    ]


def dashboard43():
    t = pd.read_csv(D / "t93_irena_solar_country.csv").dropna(subset=["LCOE USD/MWh"]).sort_values("Year"); v = "LCOE USD/MWh"
    g = t.groupby("Country"); a, b = g.first(), g.last(); d = (1 - b[v] / a[v]) * 100; j = int(t.Year.max())
    nu = t[t.Year == j].set_index("Country")[v]; lo, hi = nu.idxmin(), nu.idxmax(); eerst = t[t.Year == t.Year.min()].set_index("Country")[v]
    return [
        _e(43, 1, "Fall in solar cost", d.median(), f"-{d.median():.0f}%", f"first to last year per country, to {j}", f"median of {len(d)} countries, IRENA", "good"),
        _e(43, 2, f"Cheapest in {j}", nu[lo], f"{lo}: {nu[lo]:.0f} USD/MWh", f"most expensive: {hi} {nu[hi]:.0f}", "2024 USD", "good"),
        _e(43, 3, "Netherlands", d["Netherlands"], f"-{d['Netherlands']:.0f}%", f"{a.loc['Netherlands', v]:.0f} ({int(a.loc['Netherlands', 'Year'])}) to {b.loc['Netherlands', v]:.0f} USD/MWh ({int(b.loc['Netherlands', 'Year'])})", "IRENA project data", "good"),
        _e(43, 4, "Spread between countries", nu.max() / nu.min(), f"{nu.max() / nu.min():.1f}x", f"{int(t.Year.min())}: {eerst.max() / eerst.min():.1f}x ({len(eerst)} countries)", "most expensive divided by cheapest", "neutral"),
    ]


def dashboard40():
    t = pd.read_csv(D / "t94_subsidy_per_tonne.csv"); v = "Subsidy intensity EUR per tonne CO2"; s = t.set_index("Category")[v]
    k = pd.read_csv(D / "t13_kostencurve.csv"); m = k["Kosten per ton (marginale factor)"]
    h2 = t[t.Technology == "Waterstof"][v]; w = t[t.Technology == "Wind"][v]
    return [
        _e(40, 1, "Large solar park, subsidy per tonne", s["Zon-pv groter dan 20 MWp grondgebonden"], f"{s['Zon-pv groter dan 20 MWp grondgebonden']:.0f} EUR/t", f"1 to 20 MWp: {s['Zon-pv 1 tot 20 MWp grondgebonden']:.0f} EUR/t", "PBL advice SDE++ 2026", "good"),
        _e(40, 2, "Onshore wind", w.min(), f"{w.min():.0f} to {w.max():.0f} EUR/t", "by wind speed class", "PBL advice SDE++ 2026", "neutral"),
        _e(40, 3, "Hydrogen from electrolysis", h2.min(), f"{h2.min():.0f} to {h2.max():,.0f} EUR/t", "capped at 400 EUR/t in the scheme", "PBL advice SDE++ 2026", "bad"),
        _e(40, 4, "New solar without subsidy", int((m < 0).sum()), f"{int((m < 0).sum())} of {len(k)} countries", "abate CO2 at a profit in 2025", "own cost curve (dashboard 5), IRENA 2024 cost", "good"),
    ]


def dashboard41():
    t = pd.read_csv(D / "t96_grid_costs.csv"); h = t[t.Group.str.startswith("House")]; b = t[t.Group.str.startswith("Business")]
    j = int(h.Year.max()); f = lambda d, c, y: d[(d.Code == c) & (d.Year == y)].iloc[0]
    nl, nl0, eu, eu0, nb, eb = f(h, "NL", j), f(h, "NL", 2019), f(h, "EU27_2020", j), f(h, "EU27_2020", 2019), f(b, "NL", j), f(b, "EU27_2020", j)
    n, sh = "Network EUR/kWh", "Network share of energy plus network pct"
    stijg = h[h.Year.isin([2019, j]) & ~h.Code.isin(["EU27_2020", "EA"])].pivot(index="Country", columns="Year", values=n).dropna()
    return [
        _e(41, 1, "Dutch household grid cost", nl[n], f"{100 * nl[n]:.1f} ct/kWh", f"2019: {100 * nl0[n]:.1f} ct/kWh", f"EU: {100 * eu[n]:.1f} ct/kWh", "bad"),
        _e(41, 2, "EU household grid cost", eu[n], f"{100 * eu[n]:.1f} ct/kWh", f"2019: {100 * eu0[n]:.1f} ct/kWh ({eu[n] / eu0[n] - 1:+.0%})", f"Eurostat, {j}, 2,500-4,999 kWh", "bad"),
        _e(41, 3, "Grid share of energy plus grid", nl[sh], f"{nl[sh]:.0f}%", f"EU: {eu[sh]:.0f}%", "Netherlands, households, before taxes", "neutral"),
        _e(41, 4, "Countries where grid cost rose", int((stijg[j] > stijg[2019]).sum()), f"{int((stijg[j] > stijg[2019]).sum())} of {len(stijg)}", f"2019 to {j}, households",
           f"Dutch business: {100 * nb[n]:.1f} ct/kWh; EU {100 * eb[n]:.1f}", "bad"),
    ]


def dashboard42():
    t = pd.read_csv(D / "t95_grid_queue_europe.csv").set_index("Country"); x = "Queue as multiple of peak demand"; nl = t.loc["Netherlands"]
    q = pd.read_csv(D / "t89_grid_queue.csv"); l = q[q.Date == q.Date.max()]; r = l[(l["Grid operator"] == "Regional") & (l.Direction == "Offtake")].iloc[0]
    r0 = q[(q.Date == "2025-12-31") & (q["Grid operator"] == "Regional") & (q.Direction == "Offtake")].iloc[0]
    return [
        _e(42, 1, "Largest queue", t["Queue GW"].max(), f"{t['Queue GW'].idxmax()}: {t['Queue GW'].max():.0f} GW", f"{t.loc[t['Queue GW'].idxmax(), x]:.0f} times peak demand", "generation and storage only", "bad"),
        _e(42, 2, "Netherlands", nl["Queue GW"], f"{nl['Queue GW']:.0f} GW", f"{nl[x]:.1f} times peak demand", "offtake and feed-in, 30 June 2026", "bad"),
        _e(42, 3, "Dutch businesses waiting", r["Requests"], f"{r['Requests']:,.0f}", f"end 2025: {r0['Requests']:,.0f}", f"regional grids, offtake, {r['Capacity MW'] / 1000:.1f} GW", "bad"),
        _e(42, 4, "Countries with a public figure", len(t), f"{len(t)}", "Germany and Belgium publish none", "definitions differ: do not add up", "neutral"),
    ]


def dashboard23():
    e = pd.read_csv(D / "t88_energy_poverty.csv").set_index("Year"); r = pd.read_csv(D / "t97_energy_poverty_region.csv"); v = "Energy poverty pct"
    j = int(r.Year.max()); g = r[(r.Level == "Gemeente") & (r.Year == j)].dropna(subset=[v]); hi, lo = g.loc[g[v].idxmax()], g.loc[g[v].idxmin()]
    j2 = int(e.index.max())
    return [
        _e(23, 1, "Households in energy poverty", e.loc[j2, v], f"{e.loc[j2, v]:.1f}%", f"2019: {e.loc[2019, v]:.1f}%; 2023: {e.loc[2023, v]:.1f}%", f"{e.loc[j2, 'Households thousand']:.0f} thousand households, {j2}", "bad"),
        _e(23, 2, "Highest municipality", hi[v], f"{hi['Name']}: {hi[v]:.1f}%", f"lowest: {lo['Name']} {lo[v]:.1f}%", f"CBS, {j}, {len(g)} municipalities", "bad"),
        _e(23, 3, "Municipalities above 8%", int((g[v] > 8).sum()), f"{int((g[v] > 8).sum())} of {len(g)}", f"national: {r[(r.Level == 'Nederland') & (r.Year == j)][v].iloc[0]:.1f}%", f"{j}", "neutral"),
        _e(23, 4, "Affordability gap", e.loc[j2, "Affordability gap EUR"], f"{e.loc[j2, 'Affordability gap EUR']:.0f} EUR/yr", "per household in energy poverty", f"CBS/TNO, {j2}", "bad"),
    ]


def dashboard36():
    u = pd.read_csv(D / "t101_household_profile.csv"); f = pd.read_csv(D / "t90_feed_in_tariffs_2027.csv"); f = f[f["As of"] == f["As of"].max()]
    inv = "Feed-in with solar (fraction of year)"; zomer = u[u.Month.isin([4, 5, 6, 7, 8, 9])][inv].sum(); mid = u[u.Hour.isin(range(10, 16))][inv].sum()
    b, w = f.loc[f["Net ct/kWh"].idxmax()], f.loc[f["Net ct/kWh"].idxmin()]
    return [
        _e(36, 1, "Feed-in between 10 and 16h", mid, f"{mid:.0%}", "of all power a solar household feeds in", "NEDU profile E1A 2026", "neutral"),
        _e(36, 2, "Feed-in from April to September", zomer, f"{zomer:.0%}", "six summer months", "when prices are lowest", "bad"),
        _e(36, 3, "Best net feed-in payment", b["Net ct/kWh"], f"{b['Supplier']}: {b['Net ct/kWh']:.1f} ct/kWh", f"lowest: {w['Supplier']} {w['Net ct/kWh']:.1f} ct/kWh", f"{len(f)} suppliers, {b['As of']}", "neutral"),
        _e(36, 4, "Median net payment", f["Net ct/kWh"].median(), f"{f['Net ct/kWh'].median():.1f} ct/kWh", "payment minus feed-in cost", "net metering ends 1 January 2027", "bad"),
    ]


def dashboard21():
    t = pd.read_csv(D / "t100_commodity_prices.csv"); l = t[t.Month == t.Month.max()].set_index("Commodity"); i = "Index (Jan 2019 = 100)"
    y = t[t.Month == str(int(t.Month.max()[:4]) - 1) + t.Month.max()[4:]].set_index("Commodity")
    r = lambda c: f"one year earlier: {y.loc[c, 'Price USD']:,.0f}"
    return [
        _e(21, 1, "Silver", l.loc["Silver", "Price USD"], f"{l.loc['Silver', 'Price USD']:.0f} USD/oz", r("Silver"), f"{l.loc['Silver', i] / 100:.1f} times January 2019", "bad"),
        _e(21, 2, "Copper", l.loc["Copper", "Price USD"], f"{l.loc['Copper', 'Price USD']:,.0f} USD/t", r("Copper"), f"{l.loc['Copper', i] / 100:.1f} times January 2019", "bad"),
        _e(21, 3, "Aluminium", l.loc["Aluminum", "Price USD"], f"{l.loc['Aluminum', 'Price USD']:,.0f} USD/t", r("Aluminum"), f"{l.loc['Aluminum', i] / 100:.1f} times January 2019", "bad"),
        _e(21, 4, "Latest month", 0, t.Month.max()[:7], "World Bank Pink Sheet", "nominal US dollars", "neutral"),
    ]


def dashboard22():
    t = pd.read_csv(D / "t91_renewable_jobs.csv"); g = lambda d, c: t[(t.Dimension == d) & (t.Category == c)]["Jobs million"].iloc[0]
    tot, pv, cn, eu, pvcn = g("Total", "All renewables"), g("Technology", "Solar PV"), g("Country", "China"), g("Country", "European Union"), g("Solar PV by country", "China")
    return [
        _e(22, 1, "Jobs in renewable energy", tot, f"{tot:.1f} million", "world, 2024", "IRENA/ILO annual review 2025", "good"),
        _e(22, 2, "Of which solar PV", pv, f"{pv:.1f} million", f"{pv / tot:.0%} of all renewable jobs", "largest technology", "good"),
        _e(22, 3, "China", cn, f"{cn:.1f} million", f"{cn / tot:.0%} of the world; EU {eu:.1f} million", "all renewables", "neutral"),
        _e(22, 4, "Solar jobs in China", pvcn, f"{pvcn:.1f} million", f"{pvcn / pv:.0%} of all solar jobs", "manufacturing is concentrated", "neutral"),
    ]


def dashboard24():
    t = pd.read_csv(D / "t102_hydrogen_projects.csv"); c = "Capacity kt H2 per year"; s = t.groupby("Status")[c].sum(); n = t.groupby("Status")["Projects"].sum()
    plan = s.get("Concept", 0) + s.get("Feasibility study", 0); bouw = s.get("FID/Construction", 0); op = s.get("Operational", 0); weg = s.get("Cancelled", 0) + s.get("Dormant", 0) + s.get("On hold", 0)
    nl = t[t.ISO3 == "NLD"].groupby("Status")[c].sum()
    return [
        _e(24, 1, "Announced hydrogen capacity", plan, f"{plan / 1000:.0f} Mt/yr", "concept or feasibility study", f"{int(n.get('Concept', 0) + n.get('Feasibility study', 0))} projects, IEA June 2026", "neutral"),
        _e(24, 2, "Operating or under construction", op + bouw, f"{(op + bouw) / 1000:.1f} Mt/yr", f"{(op + bouw) / plan:.0%} of what is announced", "final investment decision taken", "bad"),
        _e(24, 3, "Cancelled, dormant or on hold", weg, f"{weg / 1000:.0f} Mt/yr", f"{int(n.get('Cancelled', 0) + n.get('Dormant', 0) + n.get('On hold', 0))} projects", "larger than what is being built", "bad"),
        _e(24, 4, "Netherlands: being built", nl.get("FID/Construction", 0) + nl.get("Operational", 0), f"{nl.get('FID/Construction', 0) + nl.get('Operational', 0):.0f} kt/yr",
           f"announced: {nl.get('Concept', 0) + nl.get('Feasibility study', 0):,.0f} kt/yr", "low-emission hydrogen projects", "neutral"),
    ]


def dashboard12():
    p = D / "t99_ngfs_regions.csv"
    if not p.exists():
        return []
    t = pd.read_csv(p); o = t[t.Region.str.startswith("OECD")]; g = lambda sc, v, y: o[(o.Scenario == sc) & (o.Variable == v) & (o.Year == y)]["Value"].iloc[0]
    P, G, nz, cp = "Electricity price", "Electricity generation", "Net Zero 2050", "Current Policies"
    return [
        _e(12, 1, "Power price 2030, Net Zero 2050", g(nz, P, 2030), f"{g(nz, P, 2030):.0f} USD/MWh", f"current policies: {g(cp, P, 2030):.0f}", "OECD and EU, 2010 dollars", "bad"),
        _e(12, 2, "Power price 2050, Net Zero 2050", g(nz, P, 2050), f"{g(nz, P, 2050):.0f} USD/MWh", f"current policies: {g(cp, P, 2050):.0f}", "after the transition the price is lower", "good"),
        _e(12, 3, "Power generation 2050", g(nz, G, 2050) / g(nz, G, 2020), f"{g(nz, G, 2050) / g(nz, G, 2020):.1f} times 2020", f"current policies: {g(cp, G, 2050) / g(cp, G, 2020):.1f} times", "Net Zero 2050, OECD and EU", "neutral"),
        _e(12, 4, "Scenarios", t.Scenario.nunique(), f"{t.Scenario.nunique()} scenarios", f"{t.Region.nunique()} world regions, one model", "NGFS phase V, REMIND-MAgPIE", "neutral"),
    ]


ENGELS = (dashboard5, dashboard6, dashboard7, dashboard8, dashboard9, dashboard10, dashboard11, dashboard13, dashboard14, dashboard15, dashboard16, dashboard17, dashboard18, dashboard19, dashboard20, dashboard25, dashboard26, dashboard27, dashboard28, dashboard29, dashboard30, dashboard12, dashboard21, dashboard22, dashboard23, dashboard24, dashboard32, dashboard36, dashboard38, dashboard39, dashboard40, dashboard41, dashboard42, dashboard43)


def main():
    t = pd.DataFrame(dashboard2() + dashboard3() + dashboard4() + [x for f in ENGELS for x in f()])
    t.to_csv(D / "t50_kpi_dashboards.csv", index=False)
    regels = [f"D{x.Dashboard}.{x.Volgorde} {x.KPI}: {x.Tekst} | {x.Vergelijking} | {x.Referentie} | {x.Richting}" for _, x in t.iterrows()]
    Path("resultaten/kpi_dashboards.txt").write_text("\n".join(regels) + "\n")
    print("\n".join(regels))


if __name__ == "__main__":
    main()
