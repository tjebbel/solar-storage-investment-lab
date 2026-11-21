"""Dashboard 28 "Europe's future is in California and South Australia": de duck curve buiten Europa naast NL en DE.

Alleen lokale bestanden (data/raw, eerder opgehaald door eti.wereld), dus geen netwerk nodig:
  Californie   EIA-archief SP-15 (eia_caiso_lmp_da_hr_zones_<jaar>.csv, tot 2024) + CAISO OASIS SP15 (CAISO_<jaar>_<mm>.csv, vanaf 2023)
  Texas        gridstatus.io ERCOT hub average (gridstatus_ercot_hubavg_<jaar>_1*.json)
  Zuid-Australie AEMO SA1, 5 minuten, marktklok NEM (UTC+10, geen zomertijd), interval-einde (aemo_SA1_<jjjjmm>.csv)
  Japan        JEPX systeemprijs, halfuur (jepx_<fiscaal jaar>.csv)
  VK           Elexon Market Index (APX), halfuur (elexon_mi_<datum>.json)
  NL, DE       Energy-Charts via de cache van eti.uurdata
Om munten en prijsniveaus vergelijkbaar te maken rekenen we met een index: prijs in dat uur / gemiddelde prijs van het jaar.
Tabellen (Engels): t68_world_duck_profile (markt x jaar x uur: index), t69_world_duck_depth (markt x jaar: middag- en avondindex,
negatieve uren). Gebruik: PYTHONPATH=src python3 -m eti.wereld_duck
"""
import glob
import json
from pathlib import Path

import pandas as pd

from eti import uurdata as u
from eti import wereld as w

RAW = Path("data/raw")
UIT = [Path("tableau/data"), Path("tableau/data_en")]


def _uurreeks(pts, tz):
    """[(UTC 'YYYY-MM-DD HH:MM', prijs)] -> uurgemiddelden in lokale tijd (index zonder tijdzone)."""
    if not pts:
        return pd.Series(dtype=float)
    s = pd.Series([float(p) for _, p in pts], index=pd.to_datetime([t for t, _ in pts], utc=True))
    s = s[~s.index.duplicated()].sort_index().tz_convert(tz).resample("h").mean().dropna()
    s.index = s.index.tz_localize(None)
    return s


def californie():
    eia = []
    for f in sorted(glob.glob(str(RAW / "eia_caiso_lmp_da_hr_zones_*.csv"))):
        try:
            eia += w.parse_eia_lmp(open(f, encoding="utf-8", errors="replace").read(), "SP-15 LMP")
        except Exception:
            pass
    return _uurreeks(w.voeg_samen(eia, w._oasis_punten()), "America/Los_Angeles")


def texas():
    pts = []
    for f in sorted(glob.glob(str(RAW / "gridstatus_ercot_hubavg_*.json"))):
        pts += w.parse_gridstatus(json.load(open(f)))
    return _uurreeks(pts, "America/Chicago")


def zuid_australie():
    delen = []
    for f in sorted(glob.glob(str(RAW / "aemo_SA1_*.csv"))):
        d = pd.read_csv(f, usecols=["SETTLEMENTDATE", "RRP"])
        delen.append(d)
    d = pd.concat(delen)
    t = pd.to_datetime(d.SETTLEMENTDATE, format="%Y/%m/%d %H:%M:%S") - pd.Timedelta(minutes=5)   # interval-einde -> begin
    s = pd.Series(d.RRP.to_numpy(), index=t)
    s = s[~s.index.duplicated()].sort_index().resample("h").mean().dropna()
    return s


def japan():
    pts = []
    for f in sorted(glob.glob(str(RAW / "jepx_*.csv"))):
        pts += w.parse_jepx(open(f, "rb").read().decode("shift_jis", "replace"))
    return _uurreeks(pts, "Asia/Tokyo")


def vk():
    pts = []
    for f in sorted(glob.glob(str(RAW / "elexon_mi_*.json"))):
        for r in json.load(open(f)).get("data", []):
            if r.get("dataProvider") == "APXMIDP" and r.get("volume"):
                pts.append((r["startTime"][:16].replace("T", " "), r["price"]))
    return _uurreeks(pts, "Europe/London")


def europa(zone):
    delen = [u.uren(zone, j).Price for j in range(2019, 2027)]
    s = pd.concat([d for d in delen if len(d)])
    s.index = pd.to_datetime(s.index)
    return s.dropna()


MARKTEN = {"California (CAISO SP15)": californie, "Texas (ERCOT)": texas, "South Australia (AEMO)": zuid_australie,
           "Japan (JEPX system)": japan, "United Kingdom (APX)": vk,
           "Netherlands": lambda: europa("NL"), "Germany": lambda: europa("DE-LU")}


def maten(naam, s):
    prof, diep = [], []
    for jaar, g in s.groupby(s.index.year):
        if len(g) < 24 * 200:
            continue
        gem = g.mean()
        h = g.groupby(g.index.hour).mean()
        for uur, p in h.items():
            prof.append({"Market": naam, "Year": jaar, "Hour": uur, "Average price (local currency)": p,
                         "Price index (1 = year average)": p / gem if gem > 0 else None})
        mid, av = g[(g.index.hour >= 11) & (g.index.hour < 15)].mean(), g[(g.index.hour >= 18) & (g.index.hour < 21)].mean()
        diep.append({"Market": naam, "Year": jaar, "Hours": len(g), "Average price (local currency)": gem,
                     "Midday index 11-15h": mid / gem if gem > 0 else None, "Evening index 18-21h": av / gem if gem > 0 else None,
                     "Evening to midday ratio": av / mid if mid > 0.1 * gem else None,   # middag bijna 0: verhouding zinloos
                     "Negative hours": int((g < 0).sum()), "Negative hours %": 100 * (g < 0).mean(),
                     "Partial year": len(g) < 24 * 360})
    return prof, diep


def main():
    prof, diep = [], []
    for naam, f in MARKTEN.items():
        try:
            a, b = maten(naam, f())
            prof += a; diep += b
            print(f"{naam}: {len(b)} jaren")
        except Exception as e:
            print(f"{naam} OVERGESLAGEN: {e}")
    t68, t69 = pd.DataFrame(prof), pd.DataFrame(diep)
    for uit in UIT:
        t68.round(4).to_csv(uit / "t68_world_duck_profile.csv", index=False)
        t69.round(4).to_csv(uit / "t69_world_duck_depth.csv", index=False)
    return t68, t69


if __name__ == "__main__":
    a, b = main()
    pd.set_option("display.width", 250)
    print(b[b.Year.isin([2019, 2023, 2025])].round(2).to_string())
