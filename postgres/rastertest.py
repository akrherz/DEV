"""Can we deal with rasters?"""

import numpy as np
from rasterio.io import MemoryFile

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        """
    with data as (select
    st_asraster(geom, 0.05::double precision, 0.05::double precision,
    -90, 45, '8BSI'::text) as rast from spc_outlook_geometries LIMIt 3500)
    select st_asGDALRaster(st_union(rast, 'sum'), 'GTiff') from data"""
    )
    row = cursor.fetchone()
    rast = row[0].tobytes()
    with MemoryFile(rast) as memfile:
        with memfile.open() as dataset:
            arr = dataset.read()
            print(arr.shape)
            print(np.max(arr))


if __name__ == "__main__":
    main()
