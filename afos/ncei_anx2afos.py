"""Look through NCEI ANX files and insert into AFOS database.

https://www.ncei.noaa.gov/data/service-records-retention-system/access/anx/

/tank/ncei_srrs is NFS mounted.
"""

import os

import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.nws.product import TextProduct
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()

# 7 May 2025 copied from iem repo :(
PIL3_IGNORE = (
    "RR1 RR2 RR3 RR4 RR5 RR6 RR7 RR8 RR9 RRA RRS RRZ ECM ECS ECX LAV "
    "LEV MAV MET MTR MEX NBE NBH NBP NBS NBX OSO RSD RWR STO HML WRK "
    "SCV LLL RRM ROB"
).split()
PIL_IGNORE = (
    "HPTNCF WTSNCF TSTNCF HD3RSA XF03DY XOBUS ECMNC1 SYNBOU MISWTM MISWTX "
    "MISMA1 MISAM1 BBXX CHECK CMAN SPECI METAR"
).split()
# Another 7 May 2025 copy
FAKE = {
    "URPA15": "AHOPA1",
    "URPN15": "AHOPN1",
    "URNT15": "AHONT1",
    "URNT10": "REPNT0",
    "URNT11": "REPNT1",
    "URNT12": "REPNT2",
    "URNT13": "REPNT3",
    "URNT14": "REPNTS",
    "URPA10": "REPPA0",
    "URPA11": "REPPA1",
    "URPA12": "REPPA2",
    "URPA13": "REPPA3",
    "URPA14": "REPPA4",
    "URPN10": "REPPN0",
    "URPN11": "REPPN1",
    "URPN12": "REPPN2",
    "URPN13": "REPPN3",
    "URPN14": "REPPNS",
    "URNT40": "URNT40",
}


def process(conn: Connection, utcnow, raw):
    """Ingest."""
    raw = f"000 \n{raw}\n"
    try:
        prod = TextProduct(
            raw, utcnow=utcnow, parse_segments=False, ugc_provider={}
        )
    except Exception as exp:
        LOG.warning("Failed to parse %s: %s", raw[:20], exp)
        return
    # Life choices were made here
    if prod.afos is None:
        if prod.wmo.startswith("UB"):
            prod.afos = "PIREP"
        elif prod.wmo not in FAKE:
            return
        else:
            prod.afos = FAKE[prod.wmo]
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
            "data": raw.replace("\r", ""),
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
            # if raw.find("KWBC") > -1:
            process(conn, utcnow, raw)
    conn.commit()


def main():
    """Go Main Go."""
    for dt in pd.date_range("2006/05/28", "2006/05/30", freq="1h", tz="UTC"):
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
