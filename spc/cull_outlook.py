"""Remove outlooks with in-error PTS."""

import datetime
import sys

from pyiem.util import get_dbconn, logger

LOG = logger()


def main(argv):
    """Go Main Go."""
    product_id = argv[1]
    ts = datetime.datetime.strptime(product_id[:12], "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=datetime.timezone.utc)
    source = product_id[13:17]
    pil = product_id[25:]
    assert pil[:3] == "PTS"
    swo_pil = pil.replace("PTS", "SWO")

    LOG.info("Preparing to cull %s", product_id)
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor.execute(
        "INSERT into bad_products select * from products where "
        "entered = %s and source = %s and pil = %s",
        (ts, source, swo_pil),
    )
    assert cursor.rowcount > 0
    LOG.info("Inserted %s rows into bad_products", cursor.rowcount)
    cursor.execute(
        "DELETE from products where entered = %s and source = %s and pil = %s",
        (ts, source, swo_pil),
    )
    LOG.info("Deleted %s rows", cursor.rowcount)
    cursor.execute(
        "DELETE from products where entered = %s and source = %s and pil = %s",
        (ts, source, pil),
    )
    LOG.info("Deleted %s PTS rows", cursor.rowcount)
    cursor.close()
    pgconn.commit()

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        "select id from spc_outlook WHERE product_id = %s",
        (product_id,),
    )
    outlook_id = cursor.fetchone()[0]
    LOG.info("Found spc_outlook_id = %s", outlook_id)
    cursor.execute(
        "DELETE from spc_outlook_geometries where spc_outlook_id = %s",
        (outlook_id,),
    )
    LOG.info("DELETED %s rows from spc_outlook_geometries", cursor.rowcount)
    cursor.execute(
        "DELETE from spc_outlook where id = %s",
        (outlook_id,),
    )
    LOG.info("DELETED %s rows from spc_outlook", cursor.rowcount)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
