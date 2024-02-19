"""
Review website_telemetry for errors.
"""

import requests

import pandas as pd
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            """
            select distinct request_uri from website_telemetry
            where status_code = 500
            and valid > now() - '1 day'::interval
            """,
            conn,
        )
    for uri in df["request_uri"]:
        print("-------------------------------------------------")
        print(uri)
        waiting = True
        while waiting:
            req = requests.get("http://iem.local" + uri, timeout=600)
            # Rumfields Known Knowns
            if req.status_code in [200, 422, 503]:
                waiting = False
                continue
            # /api/ can emit 500 for a variety of reasons, ensure that we
            # get a JSON response in this case and move along
            if uri.startswith("/api/"):
                try:
                    req.json()
                    waiting = False
                    continue
                except Exception:
                    pass
            res = input(f"Got {req.status_code} Try again?([y]/n) ")
            if res == "n":
                waiting = False


if __name__ == "__main__":
    main()
