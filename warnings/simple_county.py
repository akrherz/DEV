"""Map of hour of most common warning."""

import numpy as np
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn

# import matplotlib.colors as mpcolors
import matplotlib.cm as cm


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    pcursor = pgconn.cursor()

    cmap = cm.get_cmap("terrain")

    m = MapPlot(
        sector="conus",
        axisbg="#EEEEEE",
        title="Hour of Day with Most Number of Severe T'Storm Warnings Issued",
        subtitle=(
            "Hours presented are local to the NWS Office "
            "that issued the warning (1986-2019)"
        ),
        cwas=True,
    )

    bins = np.arange(12, 25, 1)
    # norm = mpcolors.BoundaryNorm(bins, cmap.N)

    pcursor.execute(
        """
    WITH data as (
        SELECT ugc, issue at time zone tzname as v
        from warnings w JOIN stations t
        ON (w.wfo =
            (case when length(t.id) = 4 then substr(t.id, 1, 3) else t.id end))
        WHERE t.network = 'WFO' and
        phenomena = 'SV' and significance = 'W' and issue is not null),
    agg as (
        SELECT ugc, extract(hour from v) as hr, count(*) from data
        GROUP by ugc, hr),
    ranks as (
        SELECT ugc, hr, rank() OVER (PARTITION by ugc ORDER by count DESC)
        from agg)

    SELECT ugc, hr from ranks where rank = 1
    """
    )
    data = {}
    for row in pcursor:
        data[row[0]] = float(row[1])

    cl = [
        "Noon",
        "",
        "2 PM",
        "",
        "4 PM",
        "",
        "6 PM",
        "",
        "8 PM",
        "",
        "10 PM",
        "",
    ]
    m.fill_ugcs(
        data,
        bins,
        cmap=cmap,
        units="Hour of Day",
        clevstride=2,
        clevlabels=cl,
        extend="neither",
    )
    m.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
