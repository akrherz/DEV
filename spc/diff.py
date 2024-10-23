"""Some raster difference."""

from datetime import date

import numpy as np
from affine import Affine
from geopandas import read_postgis
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap
from rasterstats import zonal_stats
from sqlalchemy import text
from tqdm import tqdm

GRIDDELTA = 0.2
GRIDWEST = -139.2
GRIDEAST = -55.1
GRIDNORTH = 54.51
GRIDSOUTH = 19.47


def dump(year=None):
    """Create the grid file of interest."""
    params = {
        "sts": date(2000, 1, 1),
        "ets": date(2024, 1, 1),
    }
    if year is not None:
        params["sts"] = date(year, 1, 1)
        params["ets"] = date(year, 12, 31)
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = read_postgis(
            text("""
            SELECT geom, num from watches where
            to_char(issued, 'mmdd') <= to_char(now(), 'mmdd')
            and type = 'TOR' and issued > :sts
            and issued < :ets
            """),
            pgconn,
            geom_col="geom",
            params=params,
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
    np.save(f"counts{year if year is not None else ''}.npy", counts)


def plot_diff(climo, c2020, lons, lats):
    mp = MapPlot(
        sector="conus",
        title=(
            "1 Jan - 28 May 2024 SPC Tornado Watch Count Departure from "
            "2000-2023 Average"
        ),
        subtitle=(
            "based on unofficial watch polygon "
            "archives maintained by the IEM, "
            f"{GRIDDELTA}x{GRIDDELTA} analysis grid"
        ),
    )
    cmap = get_cmap("RdBu_r")
    cmap.set_under("black")
    cmap.set_over("yellow")
    cmap.set_bad("white")
    lons, lats = np.meshgrid(lons, lats)
    rng = np.array([-6, -4, -2, -1, 1, 2, 4, 6])
    vals = np.ma.array(c2020 - climo)
    vals.mask = np.logical_and(c2020 < 0.1, climo < 0.1)

    res = mp.pcolormesh(lons, lats, vals, rng, cmap=cmap, units="count")
    res.set_rasterized(True)
    mp.panels[0].ax.text(
        0.01,
        0.04,
        (
            "Postive values mean more watches than average\n"
            "for 2024 vs 2000-2023 climatology."
        ),
        bbox=dict(color="white"),
        zorder=100,
        transform=mp.panels[0].ax.transAxes,
    )
    mp.postprocess(filename="diff.png")
    mp.close()


def plot_thisyear(climo, lons, lats):
    """Plot the climatology."""
    mp = MapPlot(
        sector="conus",
        title=("1 Jan - 28 May 2024 SPC Tornado Watch Count"),
        subtitle=(
            "based on unofficial watch polygon "
            "archives maintained by the IEM, "
            f"{GRIDDELTA}x{GRIDDELTA} analysis grid"
        ),
    )
    cmap = get_cmap("plasma")
    cmap.set_under("white")
    lons, lats = np.meshgrid(lons, lats)
    rng = list(np.arange(0, 13, 2))
    rng[0] = 1
    vals = np.ma.array(climo)
    vals.mask = climo < 1

    res = mp.pcolormesh(
        lons, lats, vals, rng, cmap=cmap, units="count", extend="max"
    )
    res.set_rasterized(True)
    mp.postprocess(filename="2024.png")
    mp.close()


def plot_climo(climo, lons, lats):
    """Plot the climatology."""
    mp = MapPlot(
        sector="conus",
        title=(
            "1 Jan - 28 May SPC Tornado Watch Count Climatology " "2000-2023"
        ),
        subtitle=(
            "based on unofficial watch polygon "
            "archives maintained by the IEM, "
            f"{GRIDDELTA}x{GRIDDELTA} analysis grid"
        ),
    )
    cmap = get_cmap("plasma")
    cmap.set_under("white")
    lons, lats = np.meshgrid(lons, lats)
    rng = list(np.arange(0, 13, 2))
    rng[0] = 0.1
    vals = np.ma.array(climo)

    res = mp.pcolormesh(lons, lats, vals, rng, cmap=cmap, units="count")
    res.set_rasterized(True)
    mp.postprocess(filename="climo.png")
    mp.close()


def main():
    """Go Main Go."""
    dump()
    dump(2024)

    climo = np.load("counts.npy") / 24.0  # 2000 thru 2023
    c2020 = np.load("counts2024.npy")
    lons = np.arange(GRIDWEST, GRIDEAST, GRIDDELTA)
    lats = np.arange(GRIDSOUTH, GRIDNORTH, GRIDDELTA)

    plot_diff(climo, c2020, lons, lats)
    plot_climo(climo, lons, lats)
    plot_thisyear(c2020, lons, lats)


if __name__ == "__main__":
    main()
