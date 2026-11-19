"""Externe validatie: onze cijfers naast vergelijkbare studies (document 'Vergelijkbare studies', 19 november 2026).

  t52_validatie_extern.csv   onderwerp, ons cijfer, extern cijfer, bron, verschil, oordeel, dashboard
De externe waarden zijn overgenomen uit de genoemde publicaties en staan hieronder vast; onze waarden worden bij elke
run opnieuw uit de tabellen gelezen. Oordeel: 'sluit aan' (binnen 0,03 of 15%), 'verklaarbaar' of 'afwijking open'.
Gebruik:  PYTHONPATH=src python3 -m eti.validatie_extern
"""
from pathlib import Path
import pandas as pd

D = Path("tableau/data")
EXTERN = [  # (sleutel, omschrijving, externe waarde, bron, dashboard)
    ("cr_DE-LU_2022", "Capture rate zon Duitsland 2022", 0.94, "Modo Energy (2026), European solar July", "1, 2, 19"),
    ("cr_DE-LU_2024", "Capture rate zon Duitsland 2024", 0.59, "Enervis via pv magazine (28-02-2025)", "1, 2, 19"),
    ("cr_DE-LU_2025", "Capture rate zon Duitsland 2025", 0.51, "Modo Energy (2026): 51% eind 2025", "1, 2, 19"),
    ("cr_AT_2024", "Capture rate zon Oostenrijk 2024", 0.645, "Enervis: AT, CZ, SK, HU, RO 0,63-0,66 (midden)", "1, 2"),
    ("cr_HU_2024", "Capture rate zon Hongarije 2024", 0.645, "Enervis: AT, CZ, SK, HU, RO 0,63-0,66 (midden)", "1, 2"),
    ("cr_RO_2024", "Capture rate zon Roemenie 2024", 0.645, "Enervis: AT, CZ, SK, HU, RO 0,63-0,66 (midden)", "1, 2"),
    ("cr_ES_2025", "Capture rate zon Spanje 2025", 0.97, "Synertics blog (2026)", "1, 2"),
    ("lr", "Leersnelheid zonnepanelen", 0.26, "ITRPV 17e editie: 26,0% over 1976-2025", "4"),
    ("prijs_2025", "Paneelprijs eind 2025 (USD/W)", 0.09, "ITRPV via PV Tech: ongeveer 0,09 USD/Wp", "4"),
]


def eigen():
    t1 = pd.read_csv(D / "t1_zonejaar.csv").set_index(["Zone", "Jaar"])["Capture rate zon"]
    w = {f"cr_{z}_{j}": t1.get((z, j)) for z, j in [("DE-LU", 2022), ("DE-LU", 2024), ("DE-LU", 2025), ("AT", 2024),
                                                     ("HU", 2024), ("RO", 2024), ("ES", 2025)]}
    lc = pd.read_csv(D / "t45_leercurve.csv").set_index("Variant")
    w["lr"] = lc.loc["alle jaren", "Leersnelheid"]
    w["prijs_2025"] = pd.read_csv(D / "t11_ervaringscurve.csv").set_index("Jaar").loc[2025, "Prijs USD per W"]
    return w


def oordeel(sleutel, ons, ext):
    if pd.isna(ons):
        return "geen eigen waarde"
    if sleutel == "lr":
        return "verklaarbaar: korte reeks (2017-2025) en verkoop onder kostprijs 2023-24"
    if abs(ons - ext) <= 0.03 or abs(ons / ext - 1) <= 0.15:
        return "sluit aan"
    return "afwijking open"


def tabel():
    w = eigen()
    r = []
    for k, oms, ext, bron, dash in EXTERN:
        ons = w.get(k)
        r.append({"Onderwerp": oms, "Ons project": round(ons, 3) if pd.notna(ons) else None, "Extern": ext,
                  "Verschil": round(ons - ext, 3) if pd.notna(ons) else None, "Oordeel": oordeel(k, ons, ext),
                  "Bron": bron, "Dashboards": dash})
    af = D / "t51_congestie_afstemming.csv"
    if af.exists():
        for _, x in pd.read_csv(af).iterrows():
            r.append({"Onderwerp": f"Wachtrij {x.Wachtrij} (GW)", "Ons project": x["Ons project GW"], "Extern": x["Officieel GW"],
                      "Verschil": round(x["Ons project GW"] - x["Officieel GW"], 2),
                      "Oordeel": "sluit aan" if x.Status == "Afwijking verklaard" else "afwijking open", "Bron": x.Bron,
                      "Dashboards": "8, 13"})
    return pd.DataFrame(r)


def main():
    t = tabel()
    t.to_csv(D / "t52_validatie_extern.csv", index=False)
    regels = [f"{x.Onderwerp}: ons {x['Ons project']} | extern {x.Extern} | {x.Oordeel}" for _, x in t.iterrows()]
    Path("resultaten/validatie_extern.txt").write_text("\n".join(regels) + "\n")
    print("\n".join(regels))


if __name__ == "__main__":
    main()
