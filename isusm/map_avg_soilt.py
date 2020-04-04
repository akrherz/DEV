"""Make something pretty."""
import datetime

from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    df = read_sql(
        """
        with avgs as (
            select station, extract(doy from valid) as doy, avg(c30)
            from daily GROUP By station, doy ORDER by doy ASC
        )
        select station, min(doy) as doy
        from avgs where avg >= 38 and station != 'A136949' GROUP by station
    """,
        pgconn,
        index_col="station",
    )
    nt = NetworkTable("ISUAG", only_online=False)
    lons = []
    lats = []
    vals = []
    jan1 = datetime.date(2000, 1, 1)
    for sid, row in df.iterrows():
        if sid not in nt.sts:
            continue
        lons.append(nt.sts[sid]["lon"])
        lats.append(nt.sts[sid]["lat"])
        date = jan1 + datetime.timedelta(days=row["doy"] - 1)
        print(f"{sid} {nt.sts[sid]['name']} {date}")
        vals.append(date.strftime("%b %-d"))

    mp = MapPlot(
        title=(
            "ISU Soil Moisture Network :: "
            r"Date of Avg 4inch Soil Temp >= 38$^\circ$F"
        ),
        nocaption=True,
    )
    mp.plot_values(lons, lats, vals, textsize=18, labelbuffer=0)
    mp.postprocess(filename="map.png")


if __name__ == "__main__":
    main()
