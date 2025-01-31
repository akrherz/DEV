"""Plot NOHRSC snowfall data."""

import numpy as np
from affine import Affine
from pyiem.plot import MapPlot, nwssnow
from pyiem.util import ncopen


def main():
    """Go Main"""
    with ncopen("/tmp/sfav2_CONUS_2024093012_to_2025013012.nc") as nc:
        lats = nc.variables["lat"][:]
        lons = nc.variables["lon"][:]
        data = np.flipud(nc.variables["Data"][:] * 1000.0 / 25.4)
    data = np.ma.masked_where(data < 0.01, data)

    mp = MapPlot(
        sector="spherical_mercator",
        west=-100,
        south=29,
        east=-80,
        north=47,
        continentalcolor="tan",
        title=(
            "National Snowfall Analysis - NOHRSC - "
            "2024-2025 Season Total Snowfall"
        ),
        subtitle="Snowfall up until 6 AM 30 Jan 2025",
    )
    cmap = nwssnow()
    cmap.set_bad("None")
    levs = [0.1, 2, 5, 8, 12, 18, 24, 30, 36, 48, 60]
    mp.imshow(
        data,
        Affine(
            lons[1] - lons[0], 0.0, lons[0], 0.0, lats[0] - lats[1], lats[-1]
        ),
        "EPSG:4326",
        clevs=levs,
        cmap=cmap,
        units="inch",
        clip_on=False,
        spacing="proportional",
    )
    # mp.drawcounties()
    # mp.drawcities()
    mp.postprocess(filename="250131.png")


if __name__ == "__main__":
    main()
