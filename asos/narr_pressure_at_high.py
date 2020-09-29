"""NARR."""
import os

from pyiem.util import get_dbconn
from pyiem.plot import MapPlot, Z_FILL, get_cmap
import numpy as np
import netCDF4
import requests
import cartopy.crs as ccrs
from tqdm import tqdm


def main():
    """Go Main Go."""
    COOP = get_dbconn("coop")
    cursor = COOP.cursor()

    total = None
    lats = None
    lons = None

    cursor.execute(
        "SELECT year, min(day) from alldata_ia "
        "where station = 'IA2203' and low < 32 and month > 7 and "
        "day > '1979-01-01' and day < '2015-01-01' "
        "GROUP by year ORDER by min ASC"
    )
    xs = []
    ys = []
    xx = []
    files = 0
    for row in tqdm(cursor, total=cursor.rowcount):
        uri = row[1].strftime(
            "https://www.ncei.noaa.gov/thredds/ncss/model-narr-a-files/"
            "%Y%m/%Y%m%d/narr-a_221_%Y%m%d_1200_000.grb"
            "?var=Geopotential_height_isobaric&north=89&west=-134&"
            "disableProjSubset=on&horizStride=1&east=-60.5&south=16.0&"
            "time_start=%Y-%m-%dT12%%3A00%%3A00Z&addLatLon=true&"
            "time_end=%Y-%m-%dT18%%3A00%%3A00Z&timeStride=1&vertCoord=500"
        )
        # req = requests.get(uri)
        # if req.status_code != 200:
        #    print(req.content)
        #    continue
        ncfn = f"data/hght12_{row[1].strftime('%Y%m%d')}.nc"
        # with open(ncfn, 'wb') as fh:
        #    fh.write(req.content)
        if not os.path.isfile(ncfn):
            continue
        files += 1
        with netCDF4.Dataset(ncfn, "r") as nc:
            mslp = nc.variables["Geopotential_height_isobaric"][0, 0, :, :]
            mn = np.min(mslp[mslp > 0])
            if total is None:
                total = mslp
                lats = nc.variables["lat"][:]
                lons = nc.variables["lon"][:]
            else:
                total += mslp
            mlons = lons[mslp == mn]
            mlats = lats[mslp == mn]
            if (np.max(mlons) - np.min(mlons)) < 10:
                if (np.min(lats) - np.max(lats)) < 10:
                    xs.append(np.average(mlons))
                    ys.append(np.average(mlats))
                    xx.append("X")

    mp = MapPlot(
        "custom",
        aspect="auto",
        north=46,
        east=-65,
        south=26,
        west=-125,
        title="1979-2014 NCEP NARR Composite 500 hPa Geopotential Heights",
        subtitle=(
            "12 UTC on dates of first fall freezing temp "
            "for Des Moines, X denotes 500 hPa low location"
        ),
    )
    vals = total / float(files)
    mp.pcolormesh(
        lons,
        lats,
        vals,
        np.arange(5460, 5901, 40),
        cmap=get_cmap("jet"),
        extend="neither",
        units="meters",
    )

    # x,y = m.map(xs,ys)
    # print xx
    mp.plot_values(xs, ys, xx, "%s", textsize=16, labelbuffer=0)
    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
