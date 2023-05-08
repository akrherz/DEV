"""Plot WPC"""

import netCDF4

from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt


def main():
    """Go Main"""
    nc = netCDF4.Dataset("/tmp/sfav2_CONUS_2019093012_to_2020063012.nc")
    lats = nc.variables["lat"][:]
    lons = nc.variables["lon"][:]
    data = nc.variables["Data"][:] * 1000.0 / 25.4
    nc.close()

    mp = MapPlot(
        sector="midwest",
        continentalcolor="tan",
        title=(
            "National Snowfall Analysis - NOHRSC - "
            "2019-2020 Season Total Snowfall"
        ),
        subtitle="Snowfall up until 7 PM 30 Jun 2020",
    )
    cmap = plt.get_cmap("terrain_r")
    levs = [0.1, 2, 5, 8, 12, 18, 24, 30, 36, 42, 48, 60]
    mp.pcolormesh(
        lons,
        lats,
        data,
        levs,
        cmap=cmap,
        units="inch",
        clip_on=False,
        spacing="proportional",
    )
    # mp.drawcounties()
    # mp.drawcities()
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
