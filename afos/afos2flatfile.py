"""Dump what I have stored in the AFOS database to flat files."""
import datetime
import subprocess

from pyiem.util import get_dbconn, logger, noaaport_text, utc

LOG = logger()
pgconn = get_dbconn("afos")
cursor = pgconn.cursor()

# ldmconfig/pqact.d/pqact_filer_iemarchive.conf
pils = (
    "LSR|FWW|CFW|TCV|RFW|FFA|SVR|TOR|SVS|SMW|MWS|NPW|WCN|WSW|EWW|FLS|FLW|"
    "SPS|SEL|SWO|FFW|DSW|SQW"
)


def workflow(date):
    """Process a given UTC date"""
    sts = utc(date.year, date.month, date.day)
    ets = sts + datetime.timedelta(hours=24)
    for pil in pils.split("|"):
        cursor.execute(
            "SELECT data from products WHERE entered >= %s and entered < %s "
            "and substr(pil,1,3) = %s ORDER by entered ASC",
            (sts, ets, pil),
        )
        if cursor.rowcount == 0:
            continue
        LOG.info("%s %s %s", date, pil, cursor.rowcount)
        with open("/tmp/afos.tmp", "w", encoding="utf-8") as fh:
            for row in cursor:
                fh.write(noaaport_text(row[0]))

        pqstr = (
            f"data a {date:%Y%m%d}0000 bogus "
            f"text/noaaport/{pil}_{date:%Y%m%d}.txt txt"
        )
        cmd = f"pqinsert -p '{pqstr}' /tmp/afos.tmp"
        subprocess.call(cmd, shell=True)


def main():
    """Go Main"""
    sts = datetime.datetime(2018, 1, 1)
    ets = datetime.datetime(2020, 1, 28)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        workflow(now)
        now += interval


if __name__ == "__main__":
    # go
    main()
