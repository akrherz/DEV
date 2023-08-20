"""Shrug."""

from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    nt = NetworkTable("IACLIMATE")

    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()

    cursor.execute(
        """
    with data as (
        select station, max(case when high > 99 then day else null end),
        max(day) as lob from alldata_ia GROUP by station order by max asc)
    select station, max from data where lob > '2023-08-01'::date
    and max is not null
    """
    )

    lats = []
    lons = []
    vals = []
    sites = []
    colors = []
    mp = MapPlot(
        title=r"Most Recent 100$^\circ$F Daily High Temperature",
        subtitle="based on long term climate sites",
        continentalcolor="white",
    )
    mp.ax.set_position([0.02, 0.07, 0.8, 0.8])
    y = 0.87
    mp.fig.text(0.83, y, "Selected Sites")
    y -= 0.04
    for row in cursor:
        station = row[0]
        if station == "IA0000" or station[2] in ["C", "D"]:
            continue
        if station not in nt.sts:
            continue
        sites.append(station)
        lats.append(nt.sts[station]["lat"])
        lons.append(nt.sts[station]["lon"])
        vals.append(row[1].strftime("%-m/%d/%y"))
        color = "k"
        if row[1].year < 1993:
            color = "r"
        elif row[1].year < 2013:
            color = "b"
        colors.append(color)

        def aa(sid):
            return nt.sts[sid]["name"].replace(" Area", "")

        if station[2] == "T" or row[1].year < 2000:
            mp.fig.text(0.83, y, f"{row[1]:%-m/%d/%y} {aa(station)}")
            y -= 0.04

    mp.plot_values(
        lons,
        lats,
        vals,
        labelbuffer=1,
        color=colors,
    )
    mp.drawcounties()
    # m.plot_values(lons, lats, dates, fmt='%s', labels=sites)
    mp.postprocess(filename="230821.png")


if __name__ == "__main__":
    main()
