"""Tests voor de verkenner: de rekenfuncties, en een rooktest van het scherm met nagemaakte widgets."""
import sys
import types
import unittest

import numpy as np
import pandas as pd

from eti import verken_app as va


def voorbeeld():
    rijen = []
    for zone, regio, seg in (("NL", "Noordwest-Europa", "Batterijmarkt"), ("ES", "Iberie", "Zonverzadigd"), ("NO1", "Scandinavie", "Vlakke prijzen")):
        for jaar in (2024, 2025, 2026):
            rijen.append({"biedzone": zone, "land": zone, "regio": regio, "regelsegment": seg, "jaar": jaar, "deeljaar": jaar == 2026,
                          "capture_zon": 0.6 + 0.01 * (jaar - 2024), "batterij_per_mw": 50_000 + 1000 * (jaar - 2024), "dagspreiding": 100.0 + jaar - 2024,
                          "negatieve_uren": 400, "gem_prijs": 80.0, "aandeel_zon_pct": 20.0, "aandeel_wind_pct": 25.0})
    return pd.DataFrame(rijen)


class Rekenfuncties(unittest.TestCase):
    def test_leeg_filter_is_alles(self):
        d = voorbeeld()
        self.assertEqual(len(va.filter_zonejaar(d, hele_jaren=False)), 9)
        self.assertEqual(len(va.filter_zonejaar(d)), 6)                                  # zonder het onvolledige jaar
        self.assertEqual(len(va.filter_zonejaar(d, jaren=(2025, 2025), regios=["Iberie"])), 1)
        self.assertEqual(len(va.filter_zonejaar(d, zones=[], segmenten=None)), 6)

    def test_kerncijfers_en_marge(self):
        k = va.kerncijfers(voorbeeld(), 2025)
        self.assertAlmostEqual(k["capture_zon"][0], 0.61)
        self.assertAlmostEqual(k["capture_zon"][1], 0.01)
        marge, nodig = va.marge_zon(87, 0.52, 51)
        self.assertAlmostEqual(marge, -5.76)
        self.assertAlmostEqual(nodig, 51 / 87)

    def test_lijn_en_rangorde(self):
        d = voorbeeld()
        a, b = va.lijn_batterij(d)
        self.assertAlmostEqual(b, 1000.0, places=3)
        self.assertEqual(va.lijn_batterij(d.head(2)), (0.0, 0.0))
        self.assertEqual(list(va.rangorde(d, 2025, "capture_zon").columns)[-1], "capture_zon")


class Scherm(unittest.TestCase):
    def test_main_loopt_door_met_nagemaakte_widgets(self):
        class Alles:                                              # staat voor elk widget, elke kolom en elke figuur
            def __getattr__(self, naam): return self
            def __call__(self, *a, **k): return self
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def get(self, *a): return {}
            def slider(self, label, lo, hi, value=None, *a, **k): return value

        st = types.ModuleType("streamlit")
        alles = Alles()
        for naam in ("set_page_config", "warning", "title", "caption", "subheader", "dataframe", "download_button", "metric", "info", "stop"):
            setattr(st, naam, alles)
        st.cache_data = lambda f: f
        st.session_state = {}
        st.columns = lambda n: [alles] * (n if isinstance(n, int) else len(n))
        st.tabs = lambda namen: [alles] * len(namen)
        st.slider = lambda label, lo, hi, value=None, *a, **k: value
        st.multiselect = lambda label, opties, default=None, **k: list(default or [])
        st.plotly_chart = lambda *a, **k: {"selection": {"points": []}}
        st.sidebar = types.SimpleNamespace(header=alles, caption=alles, slider=st.slider, multiselect=st.multiselect,
                                           checkbox=lambda label, value=False: value, selectbox=lambda label, opties, **k: opties[0])
        px = types.ModuleType("plotly.express")
        px.scatter = px.line = px.bar = alles
        plotly = types.ModuleType("plotly")
        plotly.express = px
        oud = {k: sys.modules.get(k) for k in ("streamlit", "plotly", "plotly.express")}
        sys.modules.update({"streamlit": st, "plotly": plotly, "plotly.express": px})
        laad = va.laad
        va.laad = lambda data=None: ({"zonejaar": voorbeeld(), "maand": pd.DataFrame(), "scenario": pd.DataFrame()}, [])
        try:
            va.main()
        finally:
            va.laad = laad
            for k, v in oud.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        self.assertIn("zones", st.session_state)


if __name__ == "__main__":
    unittest.main()
