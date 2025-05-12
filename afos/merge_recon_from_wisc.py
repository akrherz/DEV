"""Consume some old Wisconsin DDPLUS files."""

import os
import tarfile
import tempfile

import httpx
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import TextProductException
from pyiem.util import logger, noaaport_text, utc
from pyiem.wmo import WMOProduct
from sqlalchemy.engine import Connection

LOG = logger()
NHC = {
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


def dbsave(conn: Connection, prod: WMOProduct, force: bool) -> bool:
    """Saveme."""
    if not force:
        res = conn.execute(
            sql_helper("""
        select entered from products where pil = :pil and entered = :valid and
        bbb is not distinct from :bbb and wmo = :wmo
        """),
            {
                "pil": NHC[prod.wmo],
                "valid": prod.valid,
                "bbb": prod.bbb,
                "wmo": prod.wmo,
            },
        )
        if res.rowcount > 0:
            LOG.info("Already in DB: %s %s", prod.wmo, prod.valid)
            return False
    # Insert the product into the database
    LOG.info("Adding DB: %s %s", prod.wmo, prod.valid)
    conn.execute(
        sql_helper("""
    INSERT into products (data, pil, entered, source, wmo, bbb) values(
                   :data, :pil, :valid, :source, :wmo, :bbb)
                   """),
        {
            "data": (
                prod.text.replace("\r", "")
                .replace("\001", "")
                .replace("\000", "")
                .strip()
            ),
            "pil": NHC[prod.wmo],
            "valid": prod.valid,
            "source": prod.source,
            "wmo": prod.wmo,
            "bbb": prod.bbb,
        },
    )
    return True


@with_sqlalchemy_conn("afos")
def main(conn: Connection = None) -> None:
    """Go Main Go."""
    for dt in pd.date_range("2004/01/26", "2004/12/31"):
        utcnow = utc(dt.year, dt.month, dt.day, 23, 59)
        LOG.info("Processing %s", dt)
        url = (
            f"https://mtarchive.geol.iastate.edu/{dt:%Y/%m/%d}/noaaport/"
            f"{dt:%y%m%d}.DDPLUS.tar.gz"
        )
        try:
            with httpx.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(f"{dt:%Y%m%d}.DDPLUS.tar.gz", "wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                else:
                    print(f"Failed to download {url}: {response.status_code}")
                    continue
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            continue
        # Unpack the tar.gz file looking for any files ending with .RECON
        # and then parse them
        taken = []
        with tarfile.open(f"{dt:%Y%m%d}.DDPLUS.tar.gz", "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith(".RECON"):
                    LOG.info("Found %s", member.name)
                    f = tar.extractfile(member)
                    if f is None:
                        continue
                    tokens = f.read().split(b"\003")
                    for token in tokens:
                        text = token.decode("ascii", errors="replace")
                        if len(text) < 10:
                            continue
                        try:
                            prod = WMOProduct(
                                noaaport_text(text), utcnow=utcnow
                            )
                        except TextProductException as exp:
                            LOG.warning("Failed to parse %s: %s", text, exp)
                            continue
                        if prod.wmo not in NHC:
                            print(
                                "FATAL Not in NHC: %s %s",
                                prod.wmo,
                                prod.valid,
                            )
                            return
                        key = f"{prod.wmo}{prod.valid}"
                        status = dbsave(conn, prod, key in taken)
                        if status:
                            taken.append(key)
                        # Lame dedup here, but if we took a previous version
                        # with a given id, we will take the next one as well
        conn.commit()


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        main()
