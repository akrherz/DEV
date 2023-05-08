"""See what ACIS thinks about a series of stations."""
from io import StringIO

import requests

from pyiem.reference import ncei_state_codes

SERVICE = "http://data.rcc-acis.org/StnData"


def main():
    """Go Main Go."""
    sids = ["IA0200", "IA0203", "IA0205", "IA0209", "IA0210"]
    print("MAXT PCPN")
    print(f"YEAR {'    '.join(sids)}")
    for year in range(1850, 2022):
        sio = StringIO()
        sio.write(f"{year} ")
        for sid in sids:
            payload = {
                "sid": ncei_state_codes[sid[:2]] + sid[2:],
                "sdate": f"{year}-04-01",
                "edate": f"{year}-04-01",
                "elems": [
                    {"name": "maxt", "add": "t"},
                    {"name": "pcpn", "add": "t"},
                ],
            }
            req = requests.post(SERVICE, json=payload, timeout=60)
            j = req.json()
            maxt = j["data"][0][1]
            maxtv = "X" if maxt[0] != "M" else " "
            maxth = f"{maxt[1]:2d}" if maxt[0] != "M" else "  "
            pcpn = j["data"][0][2]
            pcpnv = "X" if pcpn[0] != "M" else " "
            pcpnh = f"{pcpn[1]:2d}" if pcpn[0] != "M" else "  "
            sio.write(f"{maxtv}{maxth} {pcpnv}{pcpnh}   ")
        print(sio.getvalue())


if __name__ == "__main__":
    main()
