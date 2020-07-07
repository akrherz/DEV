"""Move mostly SHEF data to file for archived AFOS data."""
import datetime
import subprocess

from tqdm import tqdm
from pyiem.util import get_dbconn, noaaport_text
import pandas as pd


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor.execute("SET TIME ZONE 'UTC'")
    cursor.execute(
        "SELECT min(date(entered)), max(date(entered)) from archived_save"
    )
    mindate, maxdate = cursor.fetchone()
    progress = tqdm(pd.date_range(mindate, maxdate, freq="D"))
    for date in progress:
        progress.set_description(date.strftime("%Y%m%d"))
        cursor.execute(
            "SELECT data from archived_save WHERE "
            "entered >= %s and entered < %s",
            (date, date + datetime.timedelta(days=1)),
        )
        fn = "/mesonet/tmp/off%s.txt" % (date.strftime("%Y%m%d"),)
        with open(fn, "a") as fp:
            for row in cursor:
                fp.write(noaaport_text(row[0]))
        subprocess.call("gzip %s" % (fn,), shell=True)


if __name__ == "__main__":
    main()
