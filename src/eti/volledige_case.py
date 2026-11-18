"""Batterijcase met de posten die de dagmarktberekening weglaat: netkosten en de overige inkomsten.

De invoer zijn bronwaarden, geen eigen berekening. De uitkomst is een bandbreedte, geen voorspelling: de inkomsten
uit regelvermogen dalen terwijl de vloot groeit, en het tijdsafhankelijke transportrecht beperkt de inzet.

Bronnen (stand november 2026):
- Bouwkosten 560 euro per kW voor 2 uur: TenneT, Monitor Voorzieningszekerheid 2026.
- Netkosten 150.000 euro per MW per jaar op hoogspanning, 116.000 op extra hoogspanning, en 57.000 met het
  tijdsafhankelijke transportrecht (korting tot 62 procent): Modo Energy, op basis van de TenneT-tarieven.
- Het transportrecht levert op hoogspanning per saldo 23.000 tot 38.000 euro per MW per jaar op: Modo Energy.
- Volledige stapeling 305.000 euro per MW per jaar (2 uur, januari tot en met september 2026), waarvan 62 procent
  overblijft zonder de capaciteitsvergoedingen voor FCR en aFRR: Modo Energy, Dutch BESS benchmark.
- Ter controle, omzet en netkosten in dezelfde meting: over het jaar tot en met september 2026 verdiende dezelfde
  batterij met een vast recht op hoogspanning 279.000 euro per MW en betaalde zij daarvan 140.000 aan TenneT: Modo Energy.
- Dagmarkt met bijsturen op onbalans: eigen model (eti.onbalansregel), zonder kennis vooraf.

Schrijft powerbi/data/fact_batterij_volledige_case.csv.  Gebruik:  PYTHONPATH=src python3 -m eti.volledige_case
"""
import os
import sys

import pandas as pd

from . import finance, herijk

OUT = "powerbi/data"
CAPEX_KW = 560.0
NET_VAST, NET_TDTR = 150_000.0, 57_000.0
TDTR_SALDO = (23_000.0, 38_000.0)
STAPEL, AANDEEL_ZONDER_CAPACITEIT = 305_000.0, 0.62
STAPEL_JAAR, NET_JAAR = 279_000.0, 140_000.0       # jaar tot en met september 2026, omzet en netkosten samen gemeten


def kasstromen(omzet, netkosten, capex_kw=CAPEX_KW, daling=0.0, jaren_daling=5):
    """Kasstromen van het project van 10 MW en 2 uur. `daling` is een extra jaarlijkse daling van de omzet in de eerste
    `jaren_daling` jaren, bovenop de degradatie; netkosten en beheerkosten blijven gelijk."""
    capex = capex_kw * 1000 * herijk.MW
    kosten = capex * herijk.OPEX_SH + netkosten * herijk.MW
    return [-capex] + [omzet * herijk.MW * (1 - daling) ** min(t - 1, jaren_daling) * (1 - herijk.DEG) ** (t - 1) - kosten
                       for t in range(1, herijk.LIFE + 1)]


def irr(omzet, netkosten, capex_kw=CAPEX_KW, daling=0.0):
    v = finance.irr_safe(kasstromen(omzet, netkosten, capex_kw, daling))
    return None if v is None or v != v else float(v)


def eigen_model(data=OUT, jaar=2026):
    """Omzet per MW van 'dagmarkt met bijsturen' (vooraf gekozen drempels, informatie een kwartier oud)."""
    r = pd.read_csv(os.path.join(data, "fact_onbalans_regel.csv"))
    x = r[(r.regel == "Dagmarkt met bijsturen") & (r.vertraging_kwartieren == 1) & (r.jaar == jaar) & r.vooraf_gekozen.astype(bool)]
    return float(x.omzet_per_mw.iloc[0])


def met_transportrecht(omzet):
    """Omzet onder het tijdsafhankelijke transportrecht: de korting op de netkosten min het saldo dat de bron noemt
    is de omzet die de batterij mist doordat zij op piekuren niet mag laden of leveren."""
    return omzet - (NET_VAST - NET_TDTR) + sum(TDTR_SALDO) / 2


def gevallen(eigen):
    zonder = STAPEL * AANDEEL_ZONDER_CAPACITEIT
    daling = "Volledige stapeling, omzet daalt 10 procent per jaar in vijf jaar"
    return [
        ("Dagmarkt met bijsturen (eigen model)", "geen netkosten, zoals in de memo", eigen, 0.0, 0.0),
        ("Dagmarkt met bijsturen (eigen model)", "tijdsafhankelijk transportrecht, zonder omzetverlies", eigen, NET_TDTR, 0.0),
        ("Dagmarkt met bijsturen (eigen model)", "vast transportrecht", eigen, NET_VAST, 0.0),
        ("Volledige stapeling (benchmark)", "vast transportrecht", STAPEL, NET_VAST, 0.0),
        ("Volledige stapeling (benchmark)", "tijdsafhankelijk transportrecht", met_transportrecht(STAPEL), NET_TDTR, 0.0),
        ("Volledige stapeling, jaar tot en met september 2026", "vast transportrecht, netkosten uit dezelfde meting", STAPEL_JAAR, NET_JAAR, 0.0),
        (daling, "vast transportrecht", STAPEL, NET_VAST, 0.10),
        (daling, "tijdsafhankelijk transportrecht", met_transportrecht(STAPEL), NET_TDTR, 0.10),
        ("Stapeling zonder capaciteitsvergoedingen", "vast transportrecht", zonder, NET_VAST, 0.0),
        ("Stapeling zonder capaciteitsvergoedingen", "tijdsafhankelijk transportrecht", met_transportrecht(zonder), NET_TDTR, 0.0),
    ]


def tabel(eigen):
    rijen = []
    for inkomsten, net, omzet, netkosten, daling in gevallen(eigen):
        rijen.append({"inkomsten": inkomsten, "netaansluiting": net, "omzet_per_mw": omzet, "netkosten_per_mw": netkosten,
                      "na_netkosten_per_mw": omzet - netkosten, "capex_per_kw": CAPEX_KW, "daling_per_jaar": daling,
                      "irr": irr(omzet, netkosten, CAPEX_KW, daling)})
    return pd.DataFrame(rijen)


def main(data=OUT, uit=OUT):
    t = tabel(eigen_model(data))
    os.makedirs(uit, exist_ok=True)
    t.to_csv(os.path.join(uit, "fact_batterij_volledige_case.csv"), index=False)
    print(t.round(3).to_string(index=False))
    return t


if __name__ == "__main__":
    main(*sys.argv[1:3])
