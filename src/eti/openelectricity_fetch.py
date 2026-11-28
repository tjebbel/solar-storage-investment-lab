"""Haalt Australische stroomdata op via de Open Electricity API (v4) en bewaart de ruwe antwoorden.

Draaien vanuit de repo-root op je Mac:
    PYTHONPATH=src python3 -m eti.openelectricity_fetch

Sleutel komt uit .env (OPENELECTRICITY_API_KEY). Data is CC BY-NC 4.0: bronvermelding "Open Electricity" en niet-commercieel gebruik.
Ruwe antwoorden komen in data/raw/australie/ (gitignored). Geen komma's in bestandsnamen.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UIT = ROOT / "data" / "raw" / "australie"
BASIS = "https://api.openelectricity.org.au/v4"
NETWERKEN = ["NEM", "WEM"]
START = os.environ.get("OE_START", "2024-01-01T00:00:00")
EIND = os.environ.get("OE_EIND", "2026-11-27T00:00:00")


def sleutel():
    for regel in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if regel.startswith("OPENELECTRICITY_API_KEY="):
            return regel.split("=", 1)[1].strip()
    sys.exit("OPENELECTRICITY_API_KEY niet gevonden in .env")


def ophalen(pad, params, key):
    url = f"{BASIS}/{pad}?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "User-Agent": "solar-storage-investment-lab/1.0 (research; non-commercial)",
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as fout:
        # toon de reden die de server geeft (nooit de sleutel)
        raise RuntimeError(f"HTTP {fout.code}: {fout.read().decode('utf-8', 'replace')[:300]}") from None


def main():
    key = sleutel()
    UIT.mkdir(parents=True, exist_ok=True)
    try:
        ik = ophalen("me", {}, key)
        d = ik.get("data") or {}
        print("sleutel werkt; plan:", d.get("plan"), "| rollen:", d.get("roles"))
    except Exception as fout:
        print("controle van de sleutel (/v4/me) mislukt:", fout)
        return
    taken = [
        # (naam, pad, parameters)
        ("prijs_dag", "market/network/{net}", {"metrics": "price", "interval": "1d",
                                              "date_start": START, "date_end": EIND}),
        ("opwekking_fueltech_dag", "data/network/{net}", {"metrics": "energy", "interval": "1d",
                                                         "date_start": START, "date_end": EIND,
                                                         "primary_grouping": "network_region",
                                                         "secondary_grouping": "fueltech"}),
    ]
    jaren = [("2024-01-01T00:00:00", "2024-12-31T00:00:00"),
             ("2025-01-01T00:00:00", "2025-12-31T00:00:00"),
             ("2026-01-01T00:00:00", EIND)]
    for net in NETWERKEN:
        for naam, pad, params in taken:
            for start, eind in jaren:  # per jaar, om binnen de limiet per aanvraag te blijven
                try:
                    antwoord = ophalen(pad.format(net=net), {**params, "date_start": start, "date_end": eind}, key)
                    bestand = UIT / f"{net}_{naam}_{start[:4]}.json"
                    bestand.write_text(json.dumps(antwoord, indent=1), encoding="utf-8")
                    print(f"{bestand.name}: success={antwoord.get('success')} reeksen={len(antwoord.get('data') or [])}")
                except Exception as fout:
                    print(f"{net} {naam} {start[:4]}: fout {fout}")


if __name__ == "__main__":
    main()
