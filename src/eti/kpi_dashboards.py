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
    t10 = pd.read_csv(D / "t10_dekking_nl.csv"); t10 = t10[t10.Scenario.str.startswith("LCOE 2025")]
    g = t10[t10["Status zon"] == "Gedekt"].set_index("Jaar")["Maanden"]; n = t10.groupby("Jaar")["Maanden"].sum()
    j = int(n.index.max())
    k = pd.read_csv(D / "t47_kpi_nl.csv").set_index(["KPI", "Jaar"])
    cr, pr = k.loc[("Capture rate zon", j)], k.loc[("Gemiddelde prijs", j)]
    s = pd.read_csv(D / "t9_signalering_zones.csv"); laatste = s.Maand.max(); sl = s[s.Maand == laatste]
    nl = sl[sl.Zone == "NL"].iloc[0]
    return [
        _r(2, 1, "Maanden kosten gedekt", g.get(j, 0), f"{g.get(j, 0)} van {n[j]}", f"{j-1}: {g.get(j-1, 0)} van {n[j-1]}",
           "LCOE 2025: 67,39 EUR/MWh", "goed" if g.get(j, 0) / n[j] > g.get(j - 1, 0) / n[j - 1] else "slecht"),
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
           f"95%: {a['Interval laag']:.0%}-{a['Interval hoog']:.0%}", "literatuur ca. 20-25%", "goed"),
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
    best = k.sort_values("Kosten per ton (gemiddelde factor)").iloc[0]
    nl = k[k.Landcode == "NLD"].iloc[0]
    return [
        _e(5, 1, "Countries abating CO2 at a profit", winst, f"{winst} of {len(k)}", "solar capture price above LCOE, 2025",
           "negative cost per tonne", "good"),
        _e(5, 2, "Abatement potential to 2030", pot_m, f"{pot_m:.0f} Mt CO2/yr", f"average grid factor: {pot_g:.0f} Mt",
           "marginal factor (gas) vs average", "neutral"),
        _e(5, 3, "Cheapest abatement", best["Kosten per ton (gemiddelde factor)"], f"{_land(best.Land)}: {best['Kosten per ton (gemiddelde factor)']:.0f} EUR/t",
           f"margin {best['Marge EUR/MWh']:.0f} EUR/MWh", "EU ETS around 70-80 EUR/t", "good"),
        _e(5, 4, "Netherlands", nl["Kosten per ton (gemiddelde factor)"], f"{nl['Kosten per ton (gemiddelde factor)']:.0f} EUR/t",
           f"marginal factor: {nl['Kosten per ton (marginale factor)']:.0f} EUR/t", f"margin {nl['Marge EUR/MWh']:.0f} EUR/MWh",
           "bad" if nl["Marge EUR/MWh"] < 0 else "good"),
    ]


def dashboard8():
    s = pd.read_csv(D / "t37_nl_stroom.csv").set_index(["Bron", "Jaar"])
    z25, z24 = s.loc[("Zonnestroom", 2025)], s.loc[("Zonnestroom", 2024)]
    a = pd.read_csv(D / "t51_congestie_afstemming.csv").set_index("Wachtrij")
    r = pd.read_csv(D / "t40_res_regio.csv").groupby("Jaar")["Zon MWp"].sum()
    g25, g24 = r[2025] / r[2024] - 1, r[2024] / r[2023] - 1
    f = pd.read_csv(D / "t25_flex_nl.csv").set_index("Jaar")["Negatieve uren"]
    return [
        _e(8, 1, "Solar share of Dutch power", z25["Aandeel verbruik %"], f"{z25['Aandeel verbruik %']:.0f}%",
           f"2024: {z24['Aandeel verbruik %']:.0f}%", "CBS, 2025 provisional", "good"),
        _e(8, 2, "Solar capacity growth", g25, f"{g25:+.0%} in 2025", f"2024: {g24:+.0%}", f"{r[2025]/1000:.1f} GWp in RES regions",
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
        _e(14, 2, "Dutch solar margin", nl["Marge zon EUR/MWh"], f"{nl['Marge zon EUR/MWh']:.0f} EUR/MWh", "capture price minus LCOE, 2025",
           "additionality: high", "bad"),
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
        _e(15, 2, "Cost of capital, India", ind.WACC, f"{ind.WACC:.1%}", f"Netherlands: {nl.WACC:.1%}", "IEA Cost of Capital Observatory", "bad"),
        _e(15, 3, "Indian LCOE at Dutch WACC", ind["LCOE bij 5% WACC"], f"{ind['LCOE bij 5% WACC']:.0f} EUR/MWh",
           f"now: {ind['LCOE EUR/MWh']:.0f} EUR/MWh", f"{1 - ind['LCOE bij 5% WACC']/ind['LCOE EUR/MWh']:.0%} cheaper", "good"),
        _e(15, 4, "Sites with 1.5x Dutch sun", (z["Vollasturen tegen Nederland"] >= 1.5).sum(),
           f"{(z['Vollasturen tegen Nederland'] >= 1.5).sum()} of {len(z)}", "PVGIS, 11 years", "same panel, more output", "neutral"),
    ]


ENGELS = (dashboard5, dashboard7, dashboard8, dashboard9, dashboard10, dashboard11, dashboard13, dashboard14, dashboard15)


def main():
    t = pd.DataFrame(dashboard2() + dashboard3() + dashboard4() + [x for f in ENGELS for x in f()])
    t.to_csv(D / "t50_kpi_dashboards.csv", index=False)
    regels = [f"D{x.Dashboard}.{x.Volgorde} {x.KPI}: {x.Tekst} | {x.Vergelijking} | {x.Referentie} | {x.Richting}" for _, x in t.iterrows()]
    Path("resultaten/kpi_dashboards.txt").write_text("\n".join(regels) + "\n")
    print("\n".join(regels))


if __name__ == "__main__":
    main()
