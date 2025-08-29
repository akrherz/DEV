"""We found warnings in 2006 with a status that did not match the VTEC.

Likely a botched SQL command at some point when I attempted to do cheap
updates.  A noticed issue was FW.W with a status of UPG.
"""

from datetime import datetime

import httpx
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.products.vtec import VTECProduct
from pyiem.util import logger
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()


def trim_product_ids(product_ids, needle, utcnow):
    """Oye, a new problem to fix."""
    good = []
    for pid in product_ids:
        resp = httpx.get(
            f"https://mesonet.agron.iastate.edu/api/1/nwstext/{pid}"
        )
        try:
            prod = VTECProduct(resp.text, utcnow=utcnow)
        except Exception as exp:
            LOG.info("Failed to parse %s with %s", pid, exp)
            good.append(pid)
            continue
        found = False
        for seg in prod.segments:
            for vtec in seg.vtec:
                for ugc in seg.ugcs:
                    key = (
                        f"{vtec.phenomena}.{vtec.significance}."
                        f"{vtec.etn}.{ugc}"
                    )
                    if key == needle:
                        found = True
        if found:
            good.append(pid)
        else:
            print(f"Removing {pid} from {needle}")
    return good


def process_day(conn, dt: datetime):
    """Process a day of data."""
    warningdf = pd.read_sql(
        text("""
    select ctid, ugc, phenomena, significance, eventid, status, product_ids
    from warnings
    WHERE vtec_year = :year and updated >= :sts and updated < :ets
    and status = 'UPG' and significance = 'W'
    order by updated asc
        """),
        conn,
        params={"year": dt.year, "sts": dt, "ets": dt + pd.Timedelta(days=1)},
    )
    for _, row in warningdf.iterrows():
        pid = row["product_ids"][-1]
        resp = httpx.get(
            f"https://mesonet.agron.iastate.edu/api/1/nwstext/{pid}"
        )
        try:
            prod = VTECProduct(resp.text, utcnow=dt)
        except Exception as exp:
            LOG.info("Failed to parse %s with %s", pid, exp)
            continue
        needle = (
            f"{row['phenomena']}.{row['significance']}.{row['eventid']}."
            f"{row['ugc']}"
        )
        found = False
        for seg in prod.segments:
            for vtec in seg.vtec:
                # meh
                if vtec.action == "COR":
                    continue
                for ugc in seg.ugcs:
                    key = (
                        f"{vtec.phenomena}.{vtec.significance}.{vtec.etn}."
                        f"{ugc}"
                    )
                    if key == needle:
                        found = True
                        if row["status"] != vtec.action:
                            print(f"Fixing, {row}, {vtec}")
                            conn.execute(
                                text("""
                                UPDATE warnings SET status = :status
                                WHERE ctid = :ctid and vtec_year = :year
                                """),
                                {
                                    "status": vtec.action,
                                    "ctid": row["ctid"],
                                    "year": dt.year,
                                },
                            )
                            conn.commit()
        if not found:
            print(f"Could not find {needle} in {pid}")
            pids = trim_product_ids(row["product_ids"], needle, dt)
            if pids:
                conn.execute(
                    text("""
                    UPDATE warnings SET product_ids = :pids
                    WHERE ctid = :ctid and vtec_year = :year
                    """),
                    {
                        "pids": pids,
                        "ctid": row["ctid"],
                        "year": dt.year,
                    },
                )
                conn.commit()


def main():
    """."""
    progress = tqdm(pd.date_range("2008/01/01", "2008/12/31", tz="UTC"))
    with get_sqlalchemy_conn("postgis") as conn:
        for dt in progress:
            progress.set_description(f"{dt:%Y-%m-%d}")
            process_day(conn, dt)


if __name__ == "__main__":
    main()
