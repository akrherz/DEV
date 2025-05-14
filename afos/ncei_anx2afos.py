"""Look through NCEI ANX files and insert into AFOS database.

https://www.ncei.noaa.gov/data/service-records-retention-system/access/anx/

/tank/ncei_srrs is NFS mounted.
"""

import os
import sys
from datetime import datetime, timezone

import click
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.wmo import WMOProduct
from pywwa.workflows.fake_afos_dump import compute_afos
from sqlalchemy.engine import Connection

sys.path.insert(0, "/opt/iem/scripts/dbutil")
from clean_afos import LOG, PIL3_IGNORE, PIL_IGNORE  # type: ignore

# FRH=MOS, RVF=SHEF River, TID=Tide SHEF, BBX is BBXX, CRN is Climate Ref Net
PIL3_IGNORE.extend(["FRH", "RVF", "TID", "BBX", "CRN"])
PIL_IGNORE.extend(["QPSPTR", "QPFPTR"])


def process(conn: Connection, utcnow: datetime, raw: str):
    """Ingest."""
    raw = f"000 \n{raw}\n"
    try:
        prod = WMOProduct(raw, utcnow=utcnow)
    except Exception as exp:
        LOG.warning("Failed to parse %s: %s", raw[:20], exp)
        return
    # Ensure we are decently close in time
    if abs((prod.valid - utcnow).total_seconds()) > 86_400:
        LOG.warning(
            "Product %s is too far from utcnow %s",
            prod.get_product_id(),
            utcnow,
        )
        return
    # Life choices were made here
    if prod.afos is None:
        try:
            compute_afos(prod)
        except Exception:
            return
        if prod.afos is None:
            LOG.warning("Failed to compute afos for %s", prod.get_product_id())
            return
    if prod.afos in PIL_IGNORE or prod.afos[:3] in PIL3_IGNORE:
        return
    res = conn.execute(
        sql_helper(
            "select data from products where pil = :pil and "
            "entered = :valid and bbb is not distinct from :bbb "
            "and source = :source",
        ),
        {
            "pil": prod.afos,
            "valid": prod.valid,
            "bbb": prod.bbb,
            "source": prod.source,
        },
    )
    if res.rowcount > 0:
        return
    LOG.info("Inserting %s", prod.get_product_id())
    conn.execute(
        sql_helper(
            "INSERT into products (data, pil, entered, source, wmo, "
            "bbb) VALUES (:data, :pil, :entered, :source, :wmo, :bbb)"
        ),
        {
            "data": prod.unixtext.replace("\000", ""),
            "pil": prod.afos,
            "entered": prod.valid,
            "source": prod.source,
            "wmo": prod.wmo,
            "bbb": prod.bbb,
        },
    )


@with_sqlalchemy_conn("afos")
def readfile(filename, utcnow, conn: Connection = None):
    """Go Main Go."""
    print(f"Processing {filename}")
    with open(filename, "rb") as fh:
        for token in fh.read().decode("ascii", "ignore").split("****\n"):
            lines = token.split("\n")
            if len(lines) < 4:
                continue
            raw = "\n".join(lines[:-1])
            process(conn, utcnow, raw)
    conn.commit()


@click.command()
@click.option("--sts", type=click.DateTime(), required=True)
@click.option("--ets", type=click.DateTime(), required=True)
def main(sts: datetime, ets: datetime):
    """Go Main Go."""
    sts = sts.replace(tzinfo=timezone.utc)
    ets = ets.replace(tzinfo=timezone.utc)
    for dt in pd.date_range(sts, ets, freq="1h", tz="UTC"):
        ddir = f"/tank/ncei_srrs/anx/{dt:%Y/%m/%d/%H}"
        if not os.path.isdir(ddir):
            LOG.info("Directory %s does not exist, skipping", ddir)
            continue
        utcnow = dt + pd.Timedelta("2 hour")
        for fn in os.listdir(ddir):
            if fn.endswith(".ANX"):
                readfile(f"{ddir}/{fn}", utcnow)


if __name__ == "__main__":
    main()
