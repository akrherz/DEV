"""Daily IEMAccess database cleanup.

Runs from the database server at 11:08 PM and does some work.
"""
import datetime
import os
import shutil
import subprocess

# don't want to assume pyIEM is isntalled
import psycopg2


def atomic(pgconn, sql):
    """Run something once."""
    # print(sql)
    cursor = pgconn.cursor()
    cursor.execute("SET work_mem='8GB'")
    cursor.execute(sql)
    cursor.close()
    pgconn.commit()


def main():
    """Go Main Go."""
    today = datetime.date.today()
    pgconn = psycopg2.connect("dbname=iem")

    # Create summary table entries for two days from now
    day2 = today + datetime.timedelta(days=2)
    sql = (
        f"INSERT into summary_{day2.year}(iemid, day) "
        f"select iemid, '{day2:%Y-%m-%d}' from current"
    )
    atomic(pgconn, sql)

    # Copy any data older than 12 AM from yesterday
    yest = today - datetime.timedelta(days=1)
    fndate = today - datetime.timedelta(days=2)
    tmpfn = f"{fndate:%Y%m%d}.db"
    sql = (
        "COPY (select * from current_log where "
        f"updated < '{yest:%Y-%m-%d} 00:00') to '/tmp/{tmpfn}' WITH HEADER CSV"
    )
    atomic(pgconn, sql)

    # Delete out any data older than that
    sql = f"DELETE from current_log WHERE updated < '{yest:%Y-%m-%d} 00:00'"
    atomic(pgconn, sql)
    pgconn.close()

    mydir = f"iemaccess/{fndate:%Y_%m}"
    os.makedirs(mydir, exist_ok=True)
    subprocess.call(f"gzip /tmp/{tmpfn}", shell=True)
    shutil.move(f"/tmp/{tmpfn}.gz", mydir)

    # Vacuum
    subprocess.call("vacuumdb -q -z -t current iem", shell=True)
    subprocess.call("vacuumdb -q -z -t current_log iem", shell=True)
    subprocess.call(f"vacuumdb -q -z -t summary_{today.year} iem", shell=True)


if __name__ == "__main__":
    main()
