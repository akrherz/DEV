"""CODSUS needs some cleaning.

https://github.com/Unidata/MetPy/issues/3921
https://github.com/Unidata/MetPy/pull/3922
"""

import sys
import traceback
from io import BytesIO

import httpx
from metpy.io import parse_wpc_surface_bulletin
from tqdm import tqdm


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    resp = httpx.get(
        "https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?"
        f"sdate={year}-01-01&edate={year + 1}-01-01&limit=9999"
        "&pil=CODSUS&fmt=text",
        timeout=60,
    )
    failure = 0
    progress = tqdm(resp.content.split(b"\003"))
    for prod in progress:
        progress.set_description(f"Failures: {failure}")
        bio = BytesIO(prod)
        try:
            parse_wpc_surface_bulletin(bio, year=year)
        except Exception:
            traceback.print_exc()
            with open(f"CODSUS_fail_{failure:04.0f}.txt", "wb") as fh:
                fh.write(prod)
            failure += 1


if __name__ == "__main__":
    main(sys.argv)
