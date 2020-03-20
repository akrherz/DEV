"""Dump IEMRE for counties even

1950 thru 2017
"""
import datetime

import numpy as np
from tqdm import tqdm
import geopandas as gpd
from pyiem.grid.zs import CachingZonalStats
from pyiem import iemre
from pyiem.util import get_dbconn, ncopen
from pyiem.datatypes import temperature, distance


def main():
    """Go Please"""
    pgconn = get_dbconn("nc1018")
    counties = gpd.GeoDataFrame.from_postgis(
        """
    SELECT the_geom, fips from counties
    """,
        pgconn,
        index_col="fips",
        geom_col="the_geom",
    )
    czs = CachingZonalStats(iemre.AFFINE)

    output = open("counties.csv", "w")
    output.write("fips,date,high,low,precip\n")
    for year in tqdm(range(1950, 2018)):
        nc = ncopen(iemre.get_daily_ncname(year), "r", timeout=300)
        for tstep in range(nc.variables["time"].size):
            sdate = (
                datetime.date(year, 1, 1) + datetime.timedelta(days=tstep)
            ).strftime("%Y-%m-%d")
            high = temperature(
                nc.variables["high_tmpk_12z"][tstep, :, :], "K"
            ).value("F")
            low = temperature(
                nc.variables["low_tmpk_12z"][tstep, :, :], "K"
            ).value("F")
            pday = distance(nc.variables["p01d_12z"][tstep, :, :], "MM").value(
                "IN"
            )
            chigh = czs.gen_stats(np.flipud(high), counties["the_geom"])
            clow = czs.gen_stats(np.flipud(low), counties["the_geom"])
            cprecip = czs.gen_stats(np.flipud(pday), counties["the_geom"])
            for i, fips in enumerate(counties.index.values):
                output.write(
                    ("%s,%s,%.2f,%.2f,%.2f\n")
                    % (fips, sdate, chigh[i], clow[i], cprecip[i])
                )
        nc.close()
    output.close()


if __name__ == "__main__":
    main()
