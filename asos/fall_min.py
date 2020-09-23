"""Minimum Fall Temperature"""
import datetime

from pyiem.plot import MapPlot
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go"""
    pgconn = get_dbconn("iem")

    df = read_sql(
        """
        SELECT id, network, ST_x(geom) as lon,
        ST_y(geom) as lat, min(min_tmpf)
        from summary_2020 s JOIN stations t on (t.iemid = s.iemid)
        WHERE network IN ('IA_ASOS','AWOS') and min_tmpf > -50 and
        day > '2020-08-01' and id not in ('XXX')
        GROUP by id, network, lon, lat ORDER by min ASC
    """,
        pgconn,
        index_col=None,
    )

    mp = MapPlot(
        title=r"2020 Fall Season Minimum Temperature $^\circ$F",
        axisbg="white",
        subtitle=(
            "Automated Weather Stations ASOS/AWOS, Valid Fall 2020 thru %s"
        )
        % (datetime.datetime.now().strftime("%d %b %Y"),),
    )
    # m.contourf(lons, lats, vals, np.arange(-30,1,4))
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["min"].values,
        "%.0f",
        labels=df["id"].values,
        labelbuffer=3,
    )
    mp.drawcounties()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
