"""Some raster difference."""

from geopandas import read_postgis
from affine import Affine
from rasterstats import zonal_stats
import numpy as np
from tqdm import tqdm
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_dbconn

GRIDDELTA = 0.05
GRIDWEST = -139.2
GRIDEAST = -55.1
GRIDNORTH = 54.51
GRIDSOUTH = 19.47


def dump():
    """Create the grid file of interest."""
    pgconn = get_dbconn("postgis")
    df = read_postgis(
        "SELECT geom, num from watches where extract(month from issued) < 9 "
        "and type = 'TOR' and issued > '2000-01-01' and issued < '2020-01-01'",
        pgconn,
        geom_col="geom",
        index_col=None,
    )
    lons = np.arange(GRIDWEST, GRIDEAST, GRIDDELTA)
    lats = np.arange(GRIDSOUTH, GRIDNORTH, GRIDDELTA)
    ysz = len(lats)
    xsz = len(lons)
    ones = np.ones((int(ysz), int(xsz)))
    counts = np.zeros((int(ysz), int(xsz)))
    affine = Affine(GRIDDELTA, 0.0, GRIDWEST, 0.0, 0 - GRIDDELTA, GRIDNORTH)
    zs = zonal_stats(
        df["geom"],
        ones,
        affine=affine,
        nodata=-1,
        all_touched=True,
        raster_out=True,
    )
    for _i, z in tqdm(enumerate(zs)):
        aff = z["mini_raster_affine"]
        mywest = aff.c
        mynorth = aff.f
        raster = np.flipud(z["mini_raster_array"])
        x0 = int((mywest - GRIDWEST) / GRIDDELTA)
        y1 = int((mynorth - GRIDSOUTH) / GRIDDELTA)
        dy, dx = np.shape(raster)
        x1 = x0 + dx
        y0 = y1 - dy
        if x0 < 0 or x1 >= xsz or y0 < 0 or y1 >= ysz:
            continue
        counts[y0:y1, x0:x1] += np.where(raster.mask, 0, 1)
    np.save("counts.npy", counts)


def main():
    """Go Main Go."""

    climo = np.load("counts.npy") / 20.0  # 2000 thru 2019
    c2020 = np.load("counts2020.npy")
    lons = np.arange(GRIDWEST, GRIDEAST, GRIDDELTA)
    lats = np.arange(GRIDSOUTH, GRIDNORTH, GRIDDELTA)

    m = MapPlot(
        sector="conus",
        title=(
            "1 Jan - 31 Aug 2020 SPC Tornado Watch Count Departure from "
            "2000-2019 Average"
        ),
        subtitle=(
            "based on unofficial watch polygon "
            "archives maintained by the IEM, %sx%s analysis grid"
        )
        % (GRIDDELTA, GRIDDELTA),
    )
    cmap = get_cmap("seismic")
    cmap.set_under("black")
    cmap.set_over("yellow")
    cmap.set_bad("white")
    lons, lats = np.meshgrid(lons, lats)
    rng = np.arange(-6, 7, 2.0)
    vals = np.ma.array(c2020 - climo)
    vals.mask = climo < 0.1

    res = m.pcolormesh(lons, lats, vals, rng, cmap=cmap, units="count")
    res.set_rasterized(True)
    m.ax.text(
        0.01,
        0.04,
        (
            "Postive values mean more watches than average\n"
            "for 2020 vs 2000-2019 climatology."
        ),
        bbox=dict(color="white"),
        zorder=100,
        transform=m.ax.transAxes,
    )
    m.postprocess(filename="diff.png")


if __name__ == "__main__":
    # dump()
    main()
