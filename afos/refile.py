"""Churn the database.

Turns out we have lots of dup filed products in 2009 due to timestamp
processing pain.  This will re-insert everything and allow other dedup apps
to clean up the mess."""

import pandas as pd
# pylint: disable=wrong-import-order
import pytz
from pyiem.util import noaaport_text, get_dbconn
from pyiem.nws.product import TextProduct


def main():
    """Go Main Go."""
    pgconn = get_dbconn('afos')
    cursor = pgconn.cursor()
    for date in pd.date_range('2009-01-01', '2019-06-30'):
        cursor.execute("""
            SELECT entered, data, source, pil, wmo from products_2009_0106
            WHERE entered >= '%s 00:00+00' and entered <= '%s 23:59+00'
        """ % (date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")))
        cursor2 = pgconn.cursor()
        updates = 0
        for row in cursor:
            utcnow = row[0].astimezone(pytz.UTC)
            try:
                prod = TextProduct(
                    noaaport_text(row[1]), utcnow=utcnow, parse_segments=False)
            except:
                continue
            if prod.valid == row[0]:
                continue
            secs = (prod.valid - row[0]).total_seconds()
            if secs < -3600 or secs > 3600:
                continue
            cursor2.execute("""
                UPDATE products_2009_0106 SET entered = %s WHERE
                entered = %s and source = %s and pil = %s and wmo = %s
            """, (prod.valid, row[0], row[2], row[3], row[4]))
            updates += 1
        cursor2.close()
        pgconn.commit()
        print("date: %s count: %s updates: %s" % (
            date, cursor.rowcount, updates))


if __name__ == '__main__':
    main()
