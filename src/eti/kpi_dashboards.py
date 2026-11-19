"""KPI-tegels voor dashboards 2, 3, 4 en 7 volgens de ontwerpnorm (bouwgids, sectie "Ontwerpnorm").

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
    c = pd.read_csv(D / "t15_controles.csv"); r = pd.read_csv(D / "t16_risico.csv")
    gesl = c.Status.str.startswith("Geslaagd").sum(); open_ = c.Status.isin(["Open", "Afwijking open"]).sum()
    live = (c["Opnieuw berekend"] == "ja").sum(); top = r.sort_values("Score", ascending=False).iloc[0]
    return [
        _r(7, 1, "Controles geslaagd", gesl, f"{gesl} van {len(c)}", "18-11: 6 van 12", "doel: alle 18", "goed"),
        _r(7, 2, "Nog open", open_, f"{open_}", ", ".join(c[c.Status.isin(['Open', 'Afwijking open'])].Controle),
           "doel: 0 voor publicatie", "slecht" if open_ else "goed"),
        _r(7, 3, "Opnieuw berekend bij elke run", live, f"{live} van {len(c)}", "", "rest: handmatig vastgelegd", "neutraal"),
        _r(7, 4, "Grootste risico", top.Score, f"score {top.Score}: {top.Risico}", top.Maatregel, "kans x impact, max 9", "slecht"),
    ]


def main():
    t = pd.DataFrame(dashboard2() + dashboard3() + dashboard4() + dashboard7())
    t.to_csv(D / "t50_kpi_dashboards.csv", index=False)
    regels = [f"D{x.Dashboard}.{x.Volgorde} {x.KPI}: {x.Tekst} | {x.Vergelijking} | {x.Referentie} | {x.Richting}" for _, x in t.iterrows()]
    Path("resultaten/kpi_dashboards.txt").write_text("\n".join(regels) + "\n")
    print("\n".join(regels))


if __name__ == "__main__":
    main()
