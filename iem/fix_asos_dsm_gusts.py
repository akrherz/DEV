"""Use archive of DSM data to correct stored gusts."""
import sys

import pytz
from pyiem.nws.products.dsm import process, parser
from pyiem.util import get_dbconn


def load_stations():
    """Get xref"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        """
    SELECT id, tzname from stations where network ~* 'ASOS' or network = 'AWOS'
    and tzname is not null
    """
    )
    res = {}
    for row in cursor:
        station = row[0] if len(row[0]) == 4 else "K" + row[0]
        tzname = row[1]
        try:
            res[station] = pytz.timezone(tzname)
        except Exception as exp:
            print("pytz does not like %s" % (exp,))
            res[station] = pytz.UTC
    print("loaded %s stations" % (len(res),))
    return res


def main(argv):
    """Go Main Go."""
    afostable = argv[1]
    stations = load_stations()
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT entered, data from """
        + afostable
        + """
        WHERE substr(pil, 1, 3) = 'DSM'
        ORDER by entered
    """
    )
    updates = 0
    for row in cursor:
        if row[1].startswith("\001"):
            try:
                dsm = parser(row[1], utcnow=row[0])
                dsm.tzlocalize(stations)
            except Exception as exp:
                print(exp)
                print(row[1])
                continue
            dsm.sql(icursor)
        else:
            try:
                dsm = process(row[1])
                if dsm is None:
                    continue
                dsm.compute_times(row[0])
                dsm.tzlocalize(stations[dsm.station])
            except Exception as exp:
                print(exp)
                print(row[1])
                continue
            # print(row[1])
            dsm.sql(icursor)
            # print("%s %s %s/%s %s\n\n" % (
            #    dsm.station, dsm.date, dsm.groupdict['high'],
            #    dsm.groupdict['low'], dsm.groupdict['pday']))
        updates += 1
        if updates % 1000 == 0:
            icursor.close()
            iem_pgconn.commit()
            icursor = iem_pgconn.cursor()

    icursor.close()
    iem_pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
