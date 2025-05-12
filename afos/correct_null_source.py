"""Find afos database entries that have null source values"""

from pyiem.database import get_dbconn
from pyiem.nws.product import TextProduct
from pyiem.util import logger, noaaport_text

LOG = logger()


def dotable(table):
    """Go main go"""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute(
        f"SELECT entered, data, pil, wmo, ctid from {table} "
        "WHERE source is null"
    )
    failures = 0
    updated = 0
    noupdates = 0
    for row in cursor:
        product = noaaport_text(row[1])
        try:
            tp = TextProduct(
                product, utcnow=row[0], parse_segments=False, ugc_provider={}
            )
        except Exception:
            failures += 1
            LOG.exception("Failed to parse %s %s %s", row[0], row[2], row[3])
            continue
        if tp.source is None:
            failures += 1
            continue
        part = "0106" if tp.valid.month < 7 else "0712"
        table2 = f"products_{tp.valid:%Y}_{part}"
        if table != table2:
            LOG.info("Table mismatch %s %s", table, table2)
            noupdates += 1
            continue
        cursor2.execute(
            f"UPDATE {table} SET data = %s, source = %s, entered = %s, "
            "bbb = %s, wmo = %s WHERE ctid = %s",
            (
                product.replace("\001", "")
                .replace("\003", "")
                .replace("\r", "")
                .strip(),
                tp.source,
                tp.valid,
                tp.bbb,
                tp.wmo,
                row[4],
            ),
        )
        if cursor2.rowcount == 0:
            print("Hmmmm")
            noupdates = 0
        else:
            updated += 1
    LOG.info(
        "%s rows: %s updated: %s failures: %s noupdates: %s",
        table,
        cursor.rowcount,
        updated,
        failures,
        noupdates,
    )
    cursor2.close()
    pgconn.commit()


def main():
    """Do Main"""
    for year in range(2009, 2012):
        for col in ["0106", "0712"]:
            table = f"products_{year}_{col}"
            dotable(table)


if __name__ == "__main__":
    main()
