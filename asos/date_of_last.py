"""map of dates."""
# stdlib
import datetime

# 3rd Party
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    nt = NetworkTable("IA_ASOS")
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    lats = []
    lons = []
    vals = []

    cursor.execute(
        """WITH today as (
        SELECT id, max_tmpf from summary_2021 s JOIN stations t
        ON (s.iemid = t.iemid) WHERE t.network = 'IA_ASOS'
        and day = '2021-09-27'),
        agg as (
        SELECT t.id, max(day) from summary s, stations t, today t2
        WHERE s.iemid = t.iemid and t.id = t2.id and
        t.network = 'IA_ASOS' and to_char(day, 'mmdd') >= '0927'
        and day < '2021-09-27' and s.max_tmpf >= t2.max_tmpf
        GROUP by t.id)
        SELECT id, max from agg ORDER by max ASC
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
            "Iowa ASOS/AWOS Last Sep 27 - Dec 31 Date as Warm as 27 Sep 2021"
        ),
    )
    m.plot_values(
        lons, lats, vals, fmt="%s", color=colors, textsize=12, labelbuffer=1
    )
    m.drawcounties()
    m.postprocess(filename="210928.png")


if __name__ == "__main__":
    main()
