"""exercise."""

import numpy as np
import xarray as xr

import matplotlib.colors as mpcolors
from pyiem.plot import MapPlot
from pyiem.plot.colormaps import radar_ptype
from pyiem.reference import Z_FILL


def main(i):
    """Go Main."""
    ds = xr.open_dataset(
        "/mesonet/ARCHIVE/data/2023/01/03/model/hrrr/00/hrrr.t00z.refd.grib2"
    )
    mp = MapPlot(sector="iowa")
    colors = radar_ptype()
    refd = ds["refd"][i]
    norm = mpcolors.BoundaryNorm(np.arange(0, 56, 2.5), len(colors["rain"]))
    for typ in ["rain", "snow", "frzr", "icep"]:
        cmap = mpcolors.ListedColormap(colors[typ])
        ref = np.ma.masked_where(ds[f"c{typ}"][i].values < 0.01, refd)
        mp.panels[0].pcolormesh(
            ds["longitude"],
            ds["latitude"],
            ref,
            norm=norm,
            cmap=cmap,
            zorder=Z_FILL,
        )
    mp.draw_radar_ptype_legend()
    mp.fig.savefig(f"test{i}.png")
    mp.close()


if __name__ == "__main__":
    a = [main(i) for i in range(10)]
