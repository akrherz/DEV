"""Daily IEMAccess database cleanup.

Runs from the database server at 11:08 PM and does some work.
"""
import datetime
import os
import subprocess
import shutil

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
    sql = """
        INSERT into summary_%s(iemid, day) select iemid, '%s' from current
    """ % (
        day2.year,
        day2.strftime("%Y-%m-%d"),
    )
    atomic(pgconn, sql)

    # Copy any data older than 12 AM from yesterday
    yest = today - datetime.timedelta(days=1)
    fndate = today - datetime.timedelta(days=2)
    tmpfn = "%s.db" % (fndate.strftime("%Y%m%d"),)
    sql = """
        COPY (select * from current_log where valid < '%s 00:00')
        to '/tmp/%s' WITH HEADER CSV
    """ % (
        yest.strftime("%Y-%m-%d"),
        tmpfn,
    )
    atomic(pgconn, sql)

    # Delete out any data older than that
    sql = """
        DELETE from current_log WHERE valid < '%s 00:00'
    """ % (
        yest.strftime("%Y-%m-%d"),
    )
    atomic(pgconn, sql)
    pgconn.close()

    mydir = "iemaccess/%s" % (fndate.strftime("%Y_%m"),)
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    subprocess.call("gzip /tmp/%s" % (tmpfn,), shell=True)
    shutil.move("/tmp/%s.gz" % (tmpfn,), mydir)

    # Vacuum
    subprocess.call("vacuumdb -q -z -t current iem", shell=True)
    subprocess.call("vacuumdb -q -z -t current_log iem", shell=True)
    subprocess.call(
        "vacuumdb -q -z -t summary_%s iem" % (today.year,), shell=True
    )


if __name__ == "__main__":
    main()
