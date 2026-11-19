"""Dashboard 10 (de VS): EIA-860M maandinventaris van generatoren, 2015-2026.

Twee stappen:
  1. extract (eenmalig, zwaar): leest de ruwe maandbestanden data/raw/eia860m/<maand>_generator<jaar>.xlsx (niet in git,
     ca. 13 MB per stuk) en schrijft per snapshot een compacte optelling naar data/extern/eia860m_snapshot.csv
     (snapshot x staat x techniek: MW, MWh, aantal), plus de toevoegingen naar bedrijfsmaand uit de nieuwste snapshot
     (data/extern/eia860m_toevoeging.csv) en de geplande projecten (data/extern/eia860m_gepland.csv).
     EIA-data is publiek domein, dus deze optellingen mogen in git.
  2. tabellen (licht): maakt van die optellingen
       t33_vs_voorraad.csv     per snapshotmaand: in bedrijf, MW per techniekgroep, en batterij-MWh
       t34_vs_toevoeging.csv   per bedrijfsmaand: nieuw vermogen per techniekgroep (uit de nieuwste snapshot)
       t35_vs_staat.csv        per staat: toevoeging zon en batterij per jaar
       t36_vs_gepland.csv      geplande ingebruikname per maand en techniekgroep, met status
Gebruik:  PYTHONPATH=src python3 -m eti.vs_860m [--extract]
Kanttekening: toevoegingen uit één snapshot missen eenheden die sindsdien buiten bedrijf zijn (overlevingsvertekening);
voor zon en batterijen na 2015 is dat verwaarloosbaar.  Vermogen is nameplate AC (MW); voor zon is dat lager dan de DC-cijfers van Ember/IEA.
"""
import re
import sys
from pathlib import Path
import pandas as pd

RUW, EXT, UIT = Path("data/raw/eia860m"), Path("data/extern"), Path("tableau/data")
MAANDEN = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
GROEP = {"Solar Photovoltaic": "Zon", "Solar Thermal with Energy Storage": "Zon", "Solar Thermal without Energy Storage": "Zon",
         "Batteries": "Batterij", "Onshore Wind Turbine": "Wind", "Offshore Wind Turbine": "Wind",
         "Natural Gas Fired Combined Cycle": "Gas", "Natural Gas Fired Combustion Turbine": "Gas", "Natural Gas Steam Turbine": "Gas",
         "Natural Gas Internal Combustion Engine": "Gas", "Natural Gas with Compressed Air Storage": "Gas", "Other Natural Gas": "Gas",
         "Conventional Steam Coal": "Kolen", "Coal Integrated Gasification Combined Cycle": "Kolen", "Nuclear": "Kern",
         "Conventional Hydroelectric": "Water", "Hydroelectric Pumped Storage": "Pompcentrale"}
KOL = ["Plant State", "Nameplate Capacity (MW)", "Technology", "Operating Month", "Operating Year", "Nameplate Energy Capacity (MWh)"]
KOLP = ["Plant State", "Nameplate Capacity (MW)", "Technology", "Planned Operation Month", "Planned Operation Year", "Status"]


def groep(tech):
    return tech.map(GROEP).fillna("Overig")


def lees_blad(pad, blad, kol):
    import openpyxl
    wb = openpyxl.load_workbook(pad, read_only=True)
    ws = wb[[s for s in wb.sheetnames if s.strip().lower() == blad.lower()][0]]
    it = ws.iter_rows(values_only=True)
    for h in it:
        if h and "Entity ID" in [str(x).strip() if x else "" for x in h]:
            break
    h = [str(x).strip() if x else "" for x in h]
    idx = [h.index(k) if k in h else None for k in kol]
    rijen = [[(r[i] if i is not None else None) for i in idx] for r in it if r[0] is not None and not str(r[0]).startswith("NOTE")]
    d = pd.DataFrame(rijen, columns=kol)
    for c in d.columns:
        if c not in ("Plant State", "Technology", "Status"):
            d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.dropna(subset=["Nameplate Capacity (MW)"])


def snapshot_naam(pad):
    m = re.search(r"([a-z]+)_generator(\d{4})", Path(pad).name)
    return int(m.group(2)), MAANDEN.index(m.group(1)) + 1


def extract(bestanden=None, csvmap=None):
    """bestanden: ruwe xlsx; csvmap: of een map met al uitgepakte op_<jaar>_<maand>.csv (zelfde kolommen)."""
    delen, laatste = [], None
    bronnen = [(snapshot_naam(f), f) for f in (bestanden or sorted(RUW.glob("*_generator*.xlsx")))]
    if csvmap:
        bronnen = [((int(p.stem[3:7]), int(p.stem[8:10])), p) for p in sorted(Path(csvmap).glob("op_*.csv"))]
    for (j, m), f in sorted(bronnen):
        d = pd.read_csv(f) if str(f).endswith(".csv") else lees_blad(f, "Operating", KOL)
        d["Nameplate Energy Capacity (MWh)"] = pd.to_numeric(d.get("Nameplate Energy Capacity (MWh)"), errors="coerce")
        d["Groep"] = groep(d["Technology"])
        s = d.groupby(["Plant State", "Groep"]).agg(MW=("Nameplate Capacity (MW)", "sum"), MWh=("Nameplate Energy Capacity (MWh)", "sum"),
                                                    Eenheden=("Technology", "size")).reset_index()
        s.insert(0, "Snapshot", f"{j}-{m:02d}")
        delen.append(s); laatste = d
    EXT.mkdir(parents=True, exist_ok=True)
    pd.concat(delen).to_csv(EXT / "eia860m_snapshot.csv", index=False)
    t = laatste.groupby(["Operating Year", "Operating Month", "Plant State", "Groep"]).agg(
        MW=("Nameplate Capacity (MW)", "sum"), MWh=("Nameplate Energy Capacity (MWh)", "sum")).reset_index()
    t.to_csv(EXT / "eia860m_toevoeging.csv", index=False)
    return delen[-1]["Snapshot"].iloc[0]


def extract_gepland(pad):
    p = pd.read_csv(pad) if str(pad).endswith(".csv") else lees_blad(pad, "Planned", KOLP)
    p["Groep"] = groep(p["Technology"])
    p["Status"] = p["Status"].astype(str).str.extract(r"^\((\w+)\)")[0]
    g = p.groupby(["Planned Operation Year", "Planned Operation Month", "Groep", "Status"])["Nameplate Capacity (MW)"].sum().reset_index()
    g.to_csv(EXT / "eia860m_gepland.csv", index=False)


def tabellen():
    s = pd.read_csv(EXT / "eia860m_snapshot.csv")
    v = s.pivot_table(index="Snapshot", columns="Groep", values="MW", aggfunc="sum").div(1000).round(2)
    v.columns = [f"{c} GW" for c in v.columns]
    v["Batterij GWh"] = s[s.Groep == "Batterij"].groupby("Snapshot")["MWh"].sum().div(1000).round(2)
    v["Batterij uren"] = (v["Batterij GWh"] / v["Batterij GW"]).round(2)
    v = v.reset_index()
    t = pd.read_csv(EXT / "eia860m_toevoeging.csv")
    t = t[t["Operating Year"] >= 2010]
    a = t.pivot_table(index=["Operating Year", "Operating Month"], columns="Groep", values="MW", aggfunc="sum", fill_value=0).div(1000).round(3)
    a.columns = [f"{c} GW" for c in a.columns]
    a = a.reset_index().rename(columns={"Operating Year": "Jaar", "Operating Month": "Maand"})
    a["Datum"] = pd.to_datetime(dict(year=a.Jaar, month=a.Maand, day=1)).dt.strftime("%Y-%m-%d")
    st = t[t.Groep.isin(["Zon", "Batterij"]) & (t["Operating Year"] >= 2018)].pivot_table(
        index=["Plant State", "Operating Year"], columns="Groep", values="MW", aggfunc="sum", fill_value=0).round(1)
    st.columns = [f"{c} MW" for c in st.columns]
    st = st.reset_index().rename(columns={"Plant State": "Staat", "Operating Year": "Jaar"})
    UIT.mkdir(parents=True, exist_ok=True)
    v.to_csv(UIT / "t33_vs_voorraad.csv", index=False); a.to_csv(UIT / "t34_vs_toevoeging.csv", index=False)
    st.to_csv(UIT / "t35_vs_staat.csv", index=False)
    gp = None
    if (EXT / "eia860m_gepland.csv").exists():
        gp = pd.read_csv(EXT / "eia860m_gepland.csv"); gp.to_csv(UIT / "t36_vs_gepland.csv", index=False)
    return v, a, st, gp


def samenvatting(v, a, st, gp):
    jr = a.groupby("Jaar")[[c for c in a.columns if c.endswith("GW")]].sum()
    r = [f"EIA-860M: {len(v)} maandsnapshots, {v.Snapshot.iloc[0]} tot {v.Snapshot.iloc[-1]}."]
    r.append("Nieuw vermogen per jaar (GW, uit nieuwste snapshot): " + "; ".join(
        f"{j}: zon {x.get('Zon GW', 0):.1f}, batterij {x.get('Batterij GW', 0):.1f}, wind {x.get('Wind GW', 0):.1f}, gas {x.get('Gas GW', 0):.1f}"
        for j, x in jr.loc[2018:].iterrows()))
    l = v.iloc[-1]
    r.append(f"In bedrijf {l.Snapshot}: zon {l['Zon GW']:.1f} GW, batterij {l['Batterij GW']:.1f} GW / {l['Batterij GWh']:.1f} GWh ({l['Batterij uren']:.2f} uur), kolen {l['Kolen GW']:.1f} GW, kern {l['Kern GW']:.1f} GW.")
    top = st[st.Jaar == st.Jaar.max()].nlargest(5, "Batterij MW")
    r.append(f"Grootste staten batterij {int(st.Jaar.max())}: " + ", ".join(f"{x.Staat} {x._3:.0f} MW" for x in top.itertuples()))
    if gp is not None:
        k = gp.groupby(["Planned Operation Year", "Groep"])["Nameplate Capacity (MW)"].sum().div(1000).unstack().round(1)
        r.append("Gepland (GW): " + "; ".join(f"{int(j)}: zon {x.get('Zon', 0)}, batterij {x.get('Batterij', 0)}, wind {x.get('Wind', 0)}, gas {x.get('Gas', 0)}" for j, x in k.head(3).iterrows()))
    return r


def main():
    if "--extract" in sys.argv:
        extract()
        nieuw = sorted(RUW.glob("*_generator*.xlsx"), key=snapshot_naam)
        if nieuw: extract_gepland(nieuw[-1])
    v, a, st, gp = tabellen()
    r = samenvatting(v, a, st, gp)
    Path("resultaten").mkdir(exist_ok=True); Path("resultaten/vs_860m.txt").write_text("\n".join(r) + "\n")
    print("\n".join(r))


if __name__ == "__main__":
    main()
