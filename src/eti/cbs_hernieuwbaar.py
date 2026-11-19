"""Dashboard 8 (Nederlandse overheid) en controles op dashboards 5 en 14: CBS-cijfers hernieuwbare energie.

Invoer data/extern/cbs/<tabel>.csv (StatLine-selecties, CC BY 4.0, mogen in git):
  82610NED hernieuwbare elektriciteit (productie, vermogen)    84917NED/86329NED eindverbruik hernieuwbaar
  84918NED vermeden fossiel verbruik en CO2                     85004NED vermogen zon en wind per RES-regio
  85005NED zonnestroom per regio (installaties, kWp)            86330NED hernieuwbare warmte en koude
  82003NED zonnewarmte
plus data/extern/referentie_kapitaal_emissie.csv (IEA-kapitaalkosten 2021, RVO-emissiefactoren 2024).
Uitvoer (tableau/data):
  t37_nl_stroom.csv          per bron en jaar: productie, aandeel verbruik, vermogen, vollasturen
  t38_nl_eindverbruik.csv    per bron en jaar: TJ en aandeel in bruto eindverbruik (2023-2025)
  t39_vermeden_co2.csv       per bron: vermeden CO2 en de impliciete factor in t CO2 per MWh (CBS-methode)
  t40_res_regio.csv          per RES-regio: MWp zon (klein, groot) en MW wind op land, 2020-2025, groei
  t41_toetsen.csv            controle van eigen aannames: marginale factor 0,40 en WACC per regio tegen IEA
Gebruik:  PYTHONPATH=src python3 -m eti.cbs_hernieuwbaar
"""
from pathlib import Path
import numpy as np
import pandas as pd

MAP, UIT = Path("data/extern/cbs"), Path("tableau/data")
REF = Path("data/extern/referentie_kapitaal_emissie.csv")
WACC_EIGEN = {"Nederland": ("Europa", 0.05), "Europa (Spanje)": ("Europa", 0.055), "VS (Texas)": ("VS", 0.06),
              "China": ("China", 0.045), "India (RvdW)": ("India", 0.12)}


def lees(tabel):
    d = pd.read_csv(MAP / f"{tabel}.csv", sep=";", dtype=str, encoding="utf-8-sig")
    d.columns = [c.strip() for c in d.columns]
    per = [c for c in d.columns if c.lower() == "perioden"][0]
    d["Voorlopig"] = d[per].str.contains(r"\*", regex=True)
    d["Jaar"] = d[per].str.extract(r"(\d{4})")[0].astype(int)
    d["Deel"] = d[per].str.contains("t/m")
    for c in d.columns:
        if c not in (per, "Voorlopig", "Jaar", "Deel") and d[c].str.strip().str.match(r"^-?[\d.]*$").all():
            d[c] = pd.to_numeric(d[c].str.strip().replace({".": None, "": None}), errors="coerce")
    return d.drop(columns=per)


def stroom():
    d = lees("82610NED").rename(columns={"Bron/Techniek": "Bron"})
    k = {c: n for c, n in zip(d.columns, d.columns)}
    prod = [c for c in d.columns if c.startswith("Elektriciteitsproductie/Niet-genormaliseerde productie/Bruto")][0]
    aand = [c for c in d.columns if "relatief/Niet-genormaliseerde productie/Bruto" in c][0]
    verm = [c for c in d.columns if "vermogen" in c][0]
    t = d[["Bron", "Jaar", "Voorlopig", prod, aand, verm]].rename(columns={prod: "Productie GWh", aand: "Aandeel verbruik %", verm: "Vermogen MW"})
    t["Vollasturen"] = (t["Productie GWh"] * 1000 / t["Vermogen MW"]).round(0)
    return t


def eindverbruik():
    a = lees("84917NED").rename(columns={"Bron/techniek": "Bron"}).drop(columns=["Energietoepassingen"])
    b = lees("86329NED").rename(columns={"Bron/Techniek": "Bron"})
    b["Bron"] = b["Bron"].replace({"Totaal hernieuwbare energie": "Totaal hern. energie exc. stat. overdr."})
    t = pd.concat([a, b], ignore_index=True)
    t.columns = ["Bron" if c == "Bron" else ("TJ" if "(TJ)" in c else ("Aandeel %" if "relatief" in c else c)) for c in t.columns]
    return t[~t["Bron"].str.contains("inc. stat|Statistische", regex=True)][["Bron", "Jaar", "Voorlopig", "TJ", "Aandeel %"]]


def vermeden(s):
    d = lees("84918NED").rename(columns={"Bron/techniek": "Bron"})
    d.columns = ["Bron", "Toepassing"] + ["Vermeden fossiel TJ", "Vermeden CO2 kton"] + list(d.columns[4:])
    p = s.set_index(["Bron", "Jaar"])["Productie GWh"]
    d["Productie GWh"] = [p.get((b, j), np.nan) for b, j in zip(d["Bron"].replace({"Totaal windenergie": "Totaal windenergie"}), d["Jaar"])]
    d["t CO2 per MWh"] = (d["Vermeden CO2 kton"] / d["Productie GWh"]).round(3)
    d["kg CO2 per GJ fossiel"] = (d["Vermeden CO2 kton"] * 1e6 / (d["Vermeden fossiel TJ"] * 1e3)).round(1)
    return d[["Bron", "Jaar", "Voorlopig", "Vermeden fossiel TJ", "Vermeden CO2 kton", "Productie GWh", "t CO2 per MWh", "kg CO2 per GJ fossiel"]]


def res_regio():
    d = lees("85004NED")
    w = d.pivot_table(index=["Regio's", "Jaar"], columns="Bron en techniek", values=d.columns[2], aggfunc="sum").reset_index()
    w = w.rename(columns={"Regio's": "RES-regio", "Zonnestroom, totaal": "Zon MWp", "Zonnestroom, klein vermogen": "Zon klein MWp",
                          "Zonnestroom, groot vermogen": "Zon groot MWp", "Windenergie op land": "Wind land MW"})
    w["RES-regio"] = w["RES-regio"].str.replace(" (ES)", "", regex=False)
    w = w.sort_values(["RES-regio", "Jaar"])
    w["Groei zon %"] = (w.groupby("RES-regio")["Zon MWp"].pct_change() * 100).round(1)
    w["Aandeel groot %"] = (100 * w["Zon groot MWp"] / w["Zon MWp"]).round(1)
    return w


def toetsen(v, impact="tableau/data/t27_impact.csv"):
    ref = pd.read_csv(REF)
    ef = ref[ref.soort == "emissiefactor"].set_index("sleutel")["waarde"]
    rij = []
    for rend in (0.50, 0.55, 0.58):
        rij.append({"Toets": "Marginale factor gascentrale", "Onderwerp": f"STEG rendement {rend:.0%}",
                    "Eigen aanname": 0.40, "Referentie": round(ef["aardgas"] * 3.6 / rend / 1000, 3), "Eenheid": "t CO2/MWh",
                    "Bron": "RVO 56,2 kg/GJ"})
    z = v[(v.Bron == "Zonnestroom")].sort_values("Jaar").iloc[-1]
    rij.append({"Toets": "Marginale factor gascentrale", "Onderwerp": f"CBS vermeden emissie zonnestroom {z.Jaar}",
                "Eigen aanname": 0.40, "Referentie": z["t CO2 per MWh"], "Eenheid": "t CO2/MWh", "Bron": "CBS 84918NED / 82610NED"})
    kap = ref[ref.soort == "kapitaalkosten_nominaal"].set_index("sleutel")["waarde"]
    if Path(impact).exists():
        from eti.impact_zuiden import lcoe_bij
        t = pd.read_csv(impact); t = t[t.Jaar == 2025]
        for _, r in t.iterrows():
            if r.Regio not in WACC_EIGEN: continue
            iea = kap[WACC_EIGEN[r.Regio][0]]
            rij.append({"Toets": "WACC tegen IEA 2021", "Onderwerp": r.Regio, "Eigen aanname": r.WACC, "Referentie": iea,
                        "Eenheid": "fractie", "Bron": "IEA Cost of Capital Observatory",
                        "LCOE eigen": r["LCOE EUR/MWh"], "LCOE bij IEA-WACC": round(lcoe_bij(r["LCOE EUR/MWh"], r.WACC, iea), 2)})
    t = pd.DataFrame(rij)
    t["Verschil"] = (t["Eigen aanname"] - t["Referentie"]).round(3)
    return t


def main():
    UIT.mkdir(parents=True, exist_ok=True)
    s, e = stroom(), eindverbruik(); v = vermeden(s); r = res_regio(); k = toetsen(v)
    for naam, df in [("t37_nl_stroom", s), ("t38_nl_eindverbruik", e), ("t39_vermeden_co2", v), ("t40_res_regio", r), ("t41_toetsen", k)]:
        df.to_csv(UIT / f"{naam}.csv", index=False)
    tot = e[e.Bron.str.startswith("Totaal hern")].set_index("Jaar")["Aandeel %"]
    zs = s[s.Bron == "Zonnestroom"].set_index("Jaar")
    nl = r[r["RES-regio"] == "Nederland"].set_index("Jaar")
    top = r[(r.Jaar == r.Jaar.max()) & (r["RES-regio"] != "Nederland")].nlargest(3, "Zon MWp")
    regels = [f"Hernieuwbaar aandeel bruto eindverbruik: " + ", ".join(f"{j} {a:.1f}%" for j, a in tot.items()) + " (2025 voorlopig).",
              f"Zonnestroom: {zs.loc[2024,'Productie GWh']:.0f} GWh in 2024, {zs.loc[2025,'Productie GWh']:.0f} GWh in 2025 ({zs.loc[2025,'Aandeel verbruik %']:.1f}% van verbruik); vollasturen {zs.loc[2025,'Vollasturen']:.0f}.",
              f"RES-regio's: zon NL {nl.loc[2020,'Zon MWp']:.0f} MWp (2020) naar {nl.loc[nl.index.max(),'Zon MWp']:.0f} MWp ({nl.index.max()}), groei laatste jaar {nl.loc[nl.index.max(),'Groei zon %']:.1f}%; grootste: " + ", ".join(f"{x['RES-regio']} {x['Zon MWp']:.0f}" for _, x in top.iterrows()) + ".",
              "Toetsen:"] + [f"  {x.Toets} | {x.Onderwerp}: eigen {x['Eigen aanname']}, referentie {x.Referentie}" + (f", LCOE {x['LCOE eigen']:.1f} -> {x['LCOE bij IEA-WACC']:.1f}" if pd.notna(x.get('LCOE eigen', np.nan)) else "") for _, x in k.iterrows()]
    Path("resultaten").mkdir(exist_ok=True); Path("resultaten/cbs_hernieuwbaar.txt").write_text("\n".join(regels) + "\n")
    print("\n".join(regels))


if __name__ == "__main__":
    main()
