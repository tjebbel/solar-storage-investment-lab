"""Revisie dashboard 1 "Eerste bevindingen" na de ontwerpbeoordeling van 19 november.

  t47_kpi_nl.csv           per KPI en jaar: waarde NL, vorig jaar, verschil, Europese mediaan (alle zones), positie, lezing
  t48_capture_rangorde.csv per jaar en zone: capture rate zon, rang (1 = hoogst), Top 5 / Bodem 5 / NL / overig
  t3b_batterij_leesbaar.csv  scenario's in gewone taal, haalbaar ja/nee tegen de marktprijs (280 EUR/kWh), volgorde
  t4b_schokjaar_top.csv    tien zones met de grootste prijsstijging, de rest samengevoegd als "Overige (gemiddeld)"
  t49_segmenten.csv        segment, logische volgorde en kleur (zelfde kleur als in tableau/Preferences.tps)
Gebruik:  PYTHONPATH=src python3 -m eti.dashboard1_revisie
"""
from pathlib import Path
import pandas as pd

UIT = Path("tableau/data")
KPI = [  # kolom in t1, naam, eenheid, wat is "beter" voor een investeerder in zon + batterij
    ("Batterij-omzet per MW", "Batterij-omzet", "EUR/MW per jaar", "hoger is beter voor batterijen"),
    ("Capture rate zon", "Capture rate zon", "fractie", "hoger is beter voor zon"),
    ("Gemiddelde prijs", "Gemiddelde prijs", "EUR/MWh", "context"),
    ("Negatieve uren", "Negatieve uren", "uren", "hoger: slechter voor zon, beter voor batterijen"),
    ("Dagspreiding", "Dagspreiding", "EUR/MWh", "hoger is beter voor batterijen"),
]
SEGMENTEN = [("Vlakke prijzen", 1, "#A8A29E"), ("Zon houdt waarde", 2, "#E39A2D"), ("Middenveld", 3, "#1F9E89"),
             ("Batterijmarkt", 4, "#4A5FC1"), ("Zonverzadigd", 5, "#C4457A")]  # gevalideerd: CVD en normaal zicht
LEESBAAR = {
    "dagmarkt, geen netkosten, 1 cyclus per dag": "Alleen dagmarkt, geen netkosten, 1 cyclus",
    "dagmarkt, geen netkosten, 1,5 cyclus per dag": "Alleen dagmarkt, geen netkosten, 1,5 cyclus",
    "dagmarkt, geen netkosten, 2 cyclus per dag": "Alleen dagmarkt, geen netkosten, 2 cycli",
    "dagmarkt, tijdsafhankelijk transportrecht, 1 cyclus per dag": "Alleen dagmarkt, met netkosten, 1 cyclus",
    "dagmarkt, tijdsafhankelijk transportrecht, 1,5 cyclus per dag": "Alleen dagmarkt, met netkosten, 1,5 cyclus",
    "dagmarkt, tijdsafhankelijk transportrecht, 2 cyclus per dag": "Alleen dagmarkt, met netkosten, 2 cycli",
    "stapeling, vast transportrecht": "Dagmarkt + reservemarkten, vast netcontract",
    "stapeling, tijdsafhankelijk transportrecht": "Dagmarkt + reservemarkten, flexibel netcontract",
    "stapeling zonder capaciteitsvergoedingen, tijdsafhankelijk": "Dagmarkt + reservemarkten zonder capaciteitsvergoeding",
}


def kpi(t1="tableau/data/t1_zonejaar.csv"):
    t = pd.read_csv(t1)
    rij = []
    for kol, naam, eenheid, lezing in KPI:
        med = t.groupby("Jaar")[kol].median()
        nl = t[t.Zone == "NL"].set_index("Jaar")[kol]
        for j, w in nl.items():
            v = nl.get(j - 1)
            rij.append({"KPI": naam, "Eenheid": eenheid, "Jaar": j, "Heel jaar": int(t[(t.Zone == "NL") & (t.Jaar == j)]["Heel jaar"].iloc[0]),
                        "Waarde NL": w, "Vorig jaar": v, "Verschil": None if pd.isna(v) else w - v,
                        "Verschil %": None if pd.isna(v) or v == 0 else 100 * (w / v - 1),
                        "EU-mediaan": med.get(j), "Positie": ("op EU-mediaan" if abs(w - med.get(j)) <= 0.01 * abs(med.get(j)) else ("boven EU-mediaan" if w > med.get(j) else "onder EU-mediaan")),
                        "Lezing": lezing,
                        "Pijl": "" if pd.isna(v) else ("▲" if w > v else ("▼" if w < v else "="))})
    k = pd.DataFrame(rij).round(3)
    dec = {"Capture rate zon": 2}
    k["Waarde tekst"] = [nl_getal(w, dec.get(n, 0)) for w, n in zip(k["Waarde NL"], k["KPI"])]
    k["Onderregel"] = [("" if pd.isna(v) else f"{p} vorig jaar {nl_getal(v, dec.get(n, 0))}") + f" · EU {nl_getal(m, dec.get(n, 0))}"
                       for p, v, m, n in zip(k["Pijl"], k["Vorig jaar"], k["EU-mediaan"], k["KPI"])]
    goed_omhoog = {"Batterij-omzet": True, "Capture rate zon": True, "Dagspreiding": True}
    k["Richting"] = [("neutraal" if n not in goed_omhoog or pd.isna(d) or d == 0 else ("goed" if d > 0 else "slecht"))
                     for n, d in zip(k["KPI"], k["Verschil"])]
    return k


def nl_getal(x, dec=0):
    """Nederlandse notatie: punt voor duizendtallen, komma voor decimalen."""
    if pd.isna(x):
        return ""
    t = f"{x:,.{dec}f}"
    return t.replace(",", "_").replace(".", ",").replace("_", ".")


def rangorde(t1="tableau/data/t1_zonejaar.csv"):
    t = pd.read_csv(t1)[["Zone", "Zonenaam", "Landcode", "Jaar", "Capture rate zon"]].dropna()
    t["Rang"] = t.groupby("Jaar")["Capture rate zon"].rank(ascending=False, method="first").astype(int)
    n = t.groupby("Jaar")["Rang"].transform("max")
    t["Groep"] = "overig"
    t.loc[t.Rang <= 5, "Groep"] = "Top 5"
    t.loc[t.Rang > n - 5, "Groep"] = "Bodem 5"
    t.loc[t.Zone == "NL", "Groep"] = "Nederland"
    t["Toon"] = t.Groep != "overig"
    return t.round(3)


def batterij(t3="tableau/data/t3_batterij.csv"):
    b = pd.read_csv(t3)
    b["Scenario leesbaar"] = b["Scenario"].map(LEESBAAR).fillna(b["Scenario"])
    b["Haalbaar"] = (b["Hoogste bouwkosten per kWh"] >= b["Bouwkosten nu per kWh"]).map({True: "haalbaar", False: "niet haalbaar"})
    b["Volgorde"] = b.groupby("Doelrendement")["Hoogste bouwkosten per kWh"].rank(ascending=False).astype(int)
    # Basisgeval na vergelijking met marktstudies (Modo 2026: aFRR-capaciteitsprijzen op hun bodem):
    # stapelen ZONDER capaciteitsvergoeding; met capaciteitsvergoeding is het hoge scenario.
    def soort(sc):
        if sc.startswith("stapeling zonder"):
            return "Basisgeval"
        if sc.startswith("stapeling"):
            return "Hoog: als capaciteitsprijzen herstellen"
        return "Alleen dagmarkt"
    b["Scenario soort"] = b["Scenario"].map(soort)
    return b


def schok_top(t4="tableau/data/t4_schokjaar.csv", n=10):
    s = pd.read_csv(t4)
    tot = s.groupby("Zone")["Prijsstijging totaal"].first().sort_values(ascending=False)
    top = list(tot.index[:n])
    a = s[s.Zone.isin(top)].copy()
    rest = s[~s.Zone.isin(top)]
    r = rest.groupby("Oorzaak", as_index=False)["Euro per MWh"].mean()
    r["Zone"] = f"Overige {rest.Zone.nunique()} (gemiddeld)"
    r["Prijsstijging totaal"] = rest.groupby("Zone")["Prijsstijging totaal"].first().mean()
    a = pd.concat([a, r[a.columns]], ignore_index=True)
    volg = {z: i for i, z in enumerate(top + [r.Zone.iloc[0]], 1)}
    a["Volgorde"] = a.Zone.map(volg)
    a["Toelichting"] = a.Zone.str.startswith("NO").map({True: "Noorwegen: 'niet verklaard' is vooral de lage waterstand", False: ""})
    return a.round(3)


def segmenten():
    return pd.DataFrame(SEGMENTEN, columns=["Segment", "Volgorde", "Kleur"])


def main():
    k, r, b, s, g = kpi(), rangorde(), batterij(), schok_top(), segmenten()
    for n, d in [("t47_kpi_nl", k), ("t48_capture_rangorde", r), ("t3b_batterij_leesbaar", b), ("t4b_schokjaar_top", s), ("t49_segmenten", g)]:
        d.to_csv(UIT / f"{n}.csv", index=False)
    j = k[k["Heel jaar"] == 1].Jaar.max()
    regels = [f"KPI's Nederland {j} (tegen {j-1}, EU-mediaan):"] + [
        f"  {x.KPI}: {x['Waarde NL']:,.3g} {x.Pijl} (vorig jaar {x['Vorig jaar']:,.3g}; EU-mediaan {x['EU-mediaan']:,.3g}; {x.Positie})"
        for _, x in k[k.Jaar == j].iterrows()]
    regels.append(f"Rangorde capture rate {j}: top 5 " + ", ".join(r[(r.Jaar == j) & (r.Groep == 'Top 5')].sort_values('Rang').Zone) +
                  "; bodem 5 " + ", ".join(r[(r.Jaar == j) & (r.Groep == 'Bodem 5')].sort_values('Rang').Zone) +
                  f"; NL rang {int(r[(r.Jaar == j) & (r.Zone == 'NL')].Rang.iloc[0])} van {int(r[r.Jaar == j].Rang.max())}")
    regels.append("Prijsstijging 2026 top 10: " + ", ".join(s.drop_duplicates("Zone").sort_values("Volgorde").Zone))
    Path("resultaten/dashboard1_revisie.txt").write_text("\n".join(regels) + "\n")
    print("\n".join(regels))


if __name__ == "__main__":
    main()
