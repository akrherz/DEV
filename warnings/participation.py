"""did the UGC have a warning on most active days."""

from pyiem.plot import MapPlot
from pyiem.util import get_dbconn
import numpy as np
import matplotlib.cm as cm


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    pcursor = pgconn.cursor()

    cmap = cm.get_cmap("Accent")
    cmap.set_under("#ffffff")
    cmap.set_over("black")

    m = MapPlot(
        sector="nws",
        axisbg="#EEEEEE",
        title=(
            "1+ Tornado Warn. for 100 most active Tornado Warn. days 1986-2019"
        ),
        subtitle=(
            "A day is defined as 12 to 12 UTC period, did the "
            "county get 1+ warning during those 100 events?"
        ),
        cwas=True,
    )

    bins = np.arange(0, 31, 5)
    bins[0] = 1

    pcursor.execute(
        """
    WITH data as (
        SELECT ugc, date(issue at time zone 'UTC' + '12 hours'::interval)
        from warnings where phenomena in ('TO') and significance = 'W'
        and issue < '2020-01-01'
    ),
    maxdays as (
        SELECT date, count(*) from data
        GROUP by date ORDER by count DESC LIMIT 100
    ),
    events as (
        SELECT distinct ugc, d.date from data d
        JOIN maxdays m on (m.date = d.date)
    )

    SELECT ugc, count(*) from events GROUP by ugc
    """
    )
    data = {}
    for row in pcursor:
        data[row[0]] = float(row[1])

    m.fill_ugcs(data, bins, cmap=cmap, units="Count")
    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
