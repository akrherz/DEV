"""Legacy stuff."""

import datetime

import geopandas as gpd
import netCDF4
import numpy as np
from affine import Affine
from pyiem.iemre import daily_offset
from pyiem.util import get_dbconn
from rasterstats import zonal_stats


def main():
    """Go Main Go."""
    AFF = Affine(0.0417, 0.0, -125.0, 0.0, -0.0417, 49.894 + 0.0417)
    pgconn = get_dbconn("postgis")

    fips = gpd.GeoDataFrame.from_postgis(
        """
            SELECT ugc, ST_GeometryN(simple_geom, 1) as geo
            from ugcs WHERE ugc = 'WIC133' and end_ts is null
        """,
        pgconn,
        index_col="ugc",
        geom_col="geo",
    )

    for yr in [2007, 2008, 2009, 2010, 2011]:
        nc = netCDF4.Dataset("/mesonet/data/prism/%s_daily.nc" % (yr,))

        ppt = nc.variables["ppt"]
        sidx = daily_offset(datetime.date(yr, 4, 1))
        eidx = daily_offset(datetime.date(yr, 5, 1))
        vals = []
        for i in range(sidx, eidx):
            # CAREFUL!
            grid = np.flipud(ppt[i, :, :])
            zs = zonal_stats(
                fips["geo"], grid, affine=AFF, nodata=-1, all_touched=True
            )
            vals.append(zs[0]["mean"])
        print("%s %7.2f" % (yr, np.sum(vals)))
        nc.close()


if __name__ == "__main__":
    main()
