import unittest
from eti import wereld


class TestWereld(unittest.TestCase):
    def test_nasa(self):
        d = {"properties": {"parameter": {"ALLSKY_SFC_SW_DWN": {"20250102": 2.0, "20250101": 1.0}, "WS50M": {"20250101": 5}}}}
        self.assertEqual(wereld.parse_nasa(d), [("20250101", 1.0, 5), ("20250102", 2.0, None)])

    def test_worldbank(self):
        p = [{"page": 1}, [{"country": {"value": "Netherlands"}, "countryiso3code": "NLD", "date": "2023", "value": 100},
                           {"country": {"value": "X"}, "countryiso3code": "XXX", "date": "2023", "value": None}]]
        self.assertEqual(wereld.parse_wb(p, "a"), [("Netherlands", "NLD", 2023, "a", 100)])
        self.assertEqual(wereld.parse_wb([{"message": "error"}], "a"), [])

    def test_jepx_jst_to_utc(self):
        txt = "date,slot,a,b,c,system\n2025/04/01,1,0,0,0,10.5\n2025/04/01,20,0,0,0,0.01\n"
        self.assertEqual(wereld.parse_jepx(txt), [("2025-03-31 15:00", 10500.0), ("2025-04-01 00:30", 10.0)])
