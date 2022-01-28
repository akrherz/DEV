"""Mine the GPW data away.

https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11/data-download

Notes
=====
- Eight files are in 90x90 degree chunks.
- count is supposed to be people per pixel, but floating point values exist?
- input says ll corner of grid, we want to store centroid points.
- lazyly only storing the NW quadrant (1, 2) of the globe and Guam (4)

"""
from functools import partial
import sys

import rasterio
from tqdm import tqdm
from pyiem.util import get_dbconn


def filter1(_x, _y):
    """take it all."""
    return True


def filter2(_x, y):
    """take nothing south of PR."""
    return y > 17


def filter4(x, y):
    """Just Guam area."""
    return 140 < x < 150 and 12 < y < 18


def main(year, sector):
    """Go!"""
    print(f"Processing sector {sector}, year {year}")
    ffdict = {1: filter1, 2: filter2, 4: filter4}
    ff = ffdict[sector]
    pgconn = get_dbconn("postgis")
    updated = 0
    # Load the ascii grid file with rasterio
    fn = f"gpw_v4_population_count_rev11_{year}_30_sec_{sector}.asc"
    with rasterio.open(fn) as src:
        # Get the data
        data = src.read()
        # Get the affine transform
        affine = src.transform
        # Get the shape
        shape = src.shape
        x0 = affine.c
        y0 = affine.f
        dx = affine.a
        dy = affine.e
    # A looping we will go
    for row in tqdm(range(shape[0])):
        cursor = pgconn.cursor()
        for col in range(shape[1]):
            # Get the centroid values
            x = x0 + col * dx + dx / 2.0
            y = y0 + row * dy - dy / 2.0
            # Get the value
            value = data[0, row, col]
            if value >= 1 and ff(x, y):
                cursor.execute(
                    f"INSERT into gpw{year} (geom, population) "
                    "VALUES ('SRID=4326;POINT(%s %s)', %s)",
                    (x, y, float(value)),
                )
                updated += 1
        cursor.close()
        pgconn.commit()
    print(f"Inserted {updated} records")


if __name__ == "__main__":
    # need to actually exec the iterable
    list(map(partial(main, sys.argv[1]), [1, 2, 4]))
