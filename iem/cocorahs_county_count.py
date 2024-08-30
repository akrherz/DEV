"""CoCoRaHS county count map."""

from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    iemdb = get_dbconn("iem")
    icursor = iemdb.cursor()

    postgis = get_dbconn("postgis")
    pcursor = postgis.cursor()

    icursor.execute(
        """
    WITH data as (
    SELECT distinct s.iemid
    from summary s JOIN stations t on (t.iemid = s.iemid)
    WHERE t.network = 'IACOCORAHS' and s.day >= '2023-09-01' and pday > 0)

    SELECT ugc_county, count(*)
    from stations t JOIN data d on (d.iemid = t.iemid)
    GROUP by ugc_county ORDER by count DESC
    """
    )

    data = {}
    total = 0
    for row in icursor:
        data[row[0]] = row[1]
        total += row[1]

    # Query out centroids of counties...
    pcursor.execute(
        """
        SELECT ugc, ST_x(ST_centroid(geom)) as lon,
        ST_y(ST_centroid(geom)) as lat
        from ugcs WHERE state = 'IA' and end_ts is null and
        substr(ugc,3,1) = 'C'
        """
    )
    clons = []
    clats = []
    cvals = []
    for row in pcursor:
        cvals.append(data.get(row[0], 0))
        clats.append(row[2])
        clons.append(row[1])

    mp = MapPlot(
        axisbg="white",
        title=f"Iowa CoCoRaHS Observers Per County ({total} Total)",
        subtitle=(
            "Sites with at least one report in past year (Sep 2023- Aug 2024)"
        ),
    )
    cmap = plt.get_cmap("YlGnBu")
    mp.fill_ugcs(
        data,
        bins=[1, 2, 3, 4, 5, 7, 10, 15, 20],
        cmap=cmap,
        spacing="proportional",
        extend="max",
    )
    mp.plot_values(clons, clats, cvals, labelbuffer=0)
    mp.drawcounties()
    mp.postprocess(filename="240830.png")


if __name__ == "__main__":
    main()
