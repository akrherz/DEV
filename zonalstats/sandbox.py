"""My first attempt at zonal stats!"""
from rasterstats import zonal_stats
import netCDF4
from affine import Affine
import geopandas as gpd
import pandas as pd
import numpy as np

geodf = gpd.GeoDataFrame.from_file(("/mesonet/data/gis/static/shape/"
                                    "4326/us/huc6_01.shp"))

nc = netCDF4.Dataset("/mesonet/data/iemre/2019_iemre_daily.nc")
# CAREFUL! We need to flip the data
grid = np.flipud(nc.variables['p01d_12z'][100, :, :])

# http://www.perrygeo.com/python-affine-transforms.html
aff = Affine(0.25, 0., -104., 0., -0.25, 50.)

zs = zonal_stats(geodf, grid, affine=aff)
new_geodf = geodf.join(pd.DataFrame(zs))
print(new_geodf[new_geodf['HUC6'] == '070802'])
