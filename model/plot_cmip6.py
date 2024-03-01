"""A quick and dirty CMIP6 plot."""

import datetime
from zoneinfo import ZoneInfo

import numpy as np

from pyiem.plot import MapPlot, get_cmap
from pyiem.util import ncopen, utc


def main():
    """Go Main Go."""
    nc = ncopen(
        "pr_3hr_BCC-CSM2-MR_esm-hist_r1i1p1f1_gn_201001010130-201212312230.nc"
    )
    lats = nc.variables["lat"][:].filled(0)
    lons = (nc.variables["lon"][161:] - 360.0).filled(0)
    lons, lats = np.meshgrid(lons, lats)
    t0 = utc(2010, 1, 1)
    cmap = get_cmap("jet")
    cmap.set_under("white")
    bins = np.arange(0, 91, 10)
    bins[0] = 1.0

    for idx in range(4874, 4888):
        print(idx)
        ts = t0 + datetime.timedelta(hours=nc.variables["time"][idx] * 24.0)
        lts = ts.astimezone(ZoneInfo("America/Chicago"))
        pr = nc.variables["pr"][idx, :, 161:] * 8 * 3600.0
        mp = MapPlot(
            title="CMIP6 BCC-CSM2-MR-ESM-HIST 3 Hour Precipitation [mm]",
            subtitle=f"Valid: {lts:%d %b %Y %H:%M %p}",
            logo="dep",
            sector="custom",
            west=-105,
            east=-85,
            south=36,
            north=45,
        )
        mp.pcolormesh(lons, lats, pr, bins, cmap=cmap, units="mm")

        mp.fig.savefig(f"frame{idx - 4874:04.0f}.png")
        mp.close()


if __name__ == "__main__":
    main()
