"""map of dates."""
import datetime
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    nt = NetworkTable(["IA_ASOS", "AWOS"])
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    lats = []
    lons = []
    vals = []

    cursor.execute(
        """WITH today as (
        SELECT id, max_tmpf from summary_2020 s JOIN stations t
        ON (s.iemid = t.iemid) WHERE t.network in ('IA_ASOS', 'AWOS')
        and day = '2020-11-03'),
        agg as (
        SELECT t.id, max(day) from summary s, stations t, today t2
        WHERE s.iemid = t.iemid and t.id = t2.id and
        t.network in ('IA_ASOS', 'AWOS') and to_char(day, 'mmdd') >= '1103'
        and day < '2020-11-03' and s.max_tmpf >= t2.max_tmpf
        GROUP by t.id)
        SELECT id, max from agg ORDER by max DESC
        """
    )

    colors = []
    for row in cursor:
        lats.append(nt.sts[row[0]]["lat"])
        lons.append(nt.sts[row[0]]["lon"])
        vals.append(row[1].strftime("%-m/%-d\n%Y"))
        colors.append("r" if row[1] == datetime.date(2016, 12, 25) else "k")

    m = MapPlot(
        continentalcolor="white",
        title=(
            "Iowa ASOS/AWOS Last Nov 3 - Dec 31 Date as Warm as " "3 Nov 2020"
        ),
    )
    m.plot_values(lons, lats, vals, fmt="%s", color=colors, labelbuffer=5)
    m.drawcounties()
    m.postprocess(filename="201104.png")


if __name__ == "__main__":
    main()
