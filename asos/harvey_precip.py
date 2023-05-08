"""Some diagnostics on Harvey precip"""
import datetime

import numpy as np
import pytz

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

NT = NetworkTable("TX_ASOS")
ASOSDB = get_dbconn("asos")
IEMDB = get_dbconn("iem")
BASETIME = datetime.datetime(2017, 8, 25, 12)
BASETIME = BASETIME.replace(tzinfo=pytz.timezone("America/Chicago"))
BASETIME = BASETIME.replace(hour=1)

print("Be sure to check 1 minute total against QC data")


def workflow(sid):
    """Do what we need to do!"""
    cursor = IEMDB.cursor()
    cursor.execute(
        """SELECT sum(pday) from summary_2017 s JOIN stations t
    on (s.iemid = t.iemid) WHERE s.day >= '2017-08-25'
    and s.day < '2017-08-31' and t.id = %s""",
        (sid,),
    )
    dailytotal = cursor.fetchone()[0]

    cursor = ASOSDB.cursor()
    cursor.execute(
        """SELECT valid, precip from t2017_1minute where
    station = %s and valid >= '2017-08-25 01:00' and
    valid < '2017-08-31 01:00'
    and precip > 0 and precip < 0.5""",
        (sid,),
    )
    obs = np.zeros((6 * 1440), "f")
    for row in cursor:
        offset = int((row[0] - BASETIME).total_seconds() / 60)
        obs[offset] = row[1]
    maxes = []
    for interval in [5, 15, 30, 60, 120, 240]:
        maxval = 0
        for i in range(interval, len(obs)):
            thisval = np.sum(obs[i - interval : i])
            if thisval > maxval:
                maxval = thisval
        maxes.append(maxval)

    mps = [12, 4, 2, 1, 0.5, 0.25]
    print(
        ("%s %20.20s %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f")
        % (
            sid,
            NT.sts[sid]["name"],
            dailytotal,
            np.max(obs) * 60.0,
            maxes[0] * mps[0],
            maxes[1] * mps[1],
            maxes[2] * mps[2],
            maxes[3] * mps[3],
            maxes[4] * mps[4],
            maxes[5] * mps[5],
        )
    )


def main():
    """Go!"""
    for sid in [
        "AUS",
        "BPT",
        "CXO",
        "DWH",
        "GLS",
        "HOU",
        "IAH",
        "LBX",
        "LVJ",
        "SGR",
        "UTS",
    ]:
        workflow(sid)


if __name__ == "__main__":
    main()
