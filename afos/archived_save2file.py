"""Move mostly SHEF data to file for archived AFOS data."""
import datetime
import subprocess

import pandas as pd
from pyiem.util import get_dbconn, noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor.execute("SET TIME ZONE 'UTC'")
    cursor.execute(
        """
    SELECT min(date(entered)), max(date(entered)) from archived_save
    """
    )
    mindate, maxdate = cursor.fetchone()
    for date in pd.date_range(mindate, maxdate, freq="D"):
        cursor.execute(
            """
        SELECT data from archived_save WHERE
        entered >= %s and entered < %s
        """,
            (date, date + datetime.timedelta(days=1)),
        )
        fn = "/mesonet/tmp/off%s.txt" % (date.strftime("%Y%m%d"),)
        fp = open(fn, "a")
        for row in cursor:
            fp.write(noaaport_text(row[0]))
        fp.close()
        subprocess.call("gzip %s" % (fn,), shell=True)


if __name__ == "__main__":
    main()
