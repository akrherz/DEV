"""
Review website_telemetry for errors.
"""

from datetime import timedelta

import click
import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import utc

VHOST_MAPPER = {
    "datateam.agron.iastate.edu": "datateam.local",
    "weather.im": "weatherim.local",
    "mesonet-dep.agron.iastate.edu": "depbackend.local",
    "mesonet.agron.iastate.edu": "iem.local",
    "iem-web-services.agron.iastate.edu": "iem.local",
    "www.mesonet.agron.iastate.edu": "iem.local",
    "mesonet1.agron.iastate.edu": "iem.local",
    "mesonet2.agron.iastate.edu": "iem.local",
    "mesonet3.agron.iastate.edu": "iem.local",
    "mesonet4.agron.iastate.edu": "iem.local",
}


@click.command()
@click.option(
    "--hours", type=int, default=24, help="Number of hours to look back"
)
def main(hours: int):
    """Go Main Go."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            sql_helper("""
            select distinct vhost, request_uri from website_telemetry
            where status_code >= 500
            and valid > :sts
            and vhost not in ('iem.local', '')
            """),
            conn,
            params={"sts": utc() - timedelta(hours=hours)},
        )
    for _, row in df.iterrows():
        vhost = str(row["vhost"])
        uri = row["request_uri"]
        # Unclear how this happens, but alas
        if uri.startswith("http"):
            continue
        print("-------------------------------------------------")
        print(f"[{vhost}] {uri}")
        if uri.find("hads.py") > 0:
            print("Skipping HADS request")
            continue
        waiting = True
        while waiting:
            vhost = VHOST_MAPPER.get(vhost, vhost)
            req = httpx.get(f"http://{vhost}{uri}", timeout=600)
            # Rumfields Known Knowns
            if req.status_code in [200, 400, 404, 422, 503]:
                waiting = False
                continue
            res = input(f"Got {req.status_code} Try again?([y]/n) ")
            if res == "n":
                waiting = False


if __name__ == "__main__":
    main()
