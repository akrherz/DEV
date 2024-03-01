"""Demonstration done for some local collegues."""

import netCDF4
from osgeo import gdal


def main():
    """Go Main Go."""
    nc = netCDF4.Dataset("LU_zedx_MSDrainage022317.nc")
    LEVELINDEX = 3
    CROPS = ["corn", "soybean", "natural", "wheat"]

    lunc = nc.variables["LU"][0, 0, LEVELINDEX, :, :]

    drv = gdal.GetDriverByName("HFA")
    # Create a destination dataset
    ds = drv.Create(
        "%s.img" % (CROPS[LEVELINDEX],),
        len(nc.dimensions["longitude"]),
        len(nc.dimensions["latitude"]),
        1,
        gdal.GDT_Float32,
        options=["COMPRESS=YES"],
    )

    # Manual projection hack here, hold yer nose
    srs = (
        'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",'
        '6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
        'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,'
        'AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433'
        ',AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    )
    # Assign projection information to the destination
    ds.SetProjection(srs)
    # Gotcha, need to flip the data up/down
    ds.GetRasterBand(1).WriteArray(lunc)
    ds.GetRasterBand(1).SetDescription("Test BADN")
    # Optional, allows ArcGIS to auto show a legend
    ds.GetRasterBand(1).ComputeStatistics(True)

    lons = nc.variables["longitude"]
    dx = lons[1] - lons[0]
    lats = nc.variables["latitude"]
    dy = lats[0] - lats[1]

    # top left x, w-e pixel resolution, rotation, top left y,
    # rotation, n-s pixel resolution
    ds.SetGeoTransform([lons[0], dx, 0, lats[0], 0, 0 - dy])
    print(
        ("We wrote data with min and max: %s")
        % (ds.GetRasterBand(1).ComputeRasterMinMax(),)
    )
    # Close the files by destroying the objects
    del ds
    del srs


if __name__ == "__main__":
    main()
