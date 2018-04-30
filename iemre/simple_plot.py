import netCDF4
from pyiem.plot import MapPlot

nc = netCDF4.Dataset('/mesonet/data/iemre/2018_iemre_daily.nc')
mp = MapPlot(sector='conus')

mp.pcolormesh(nc.variables['lon'][:], nc.variables['lat'][:],
              nc.variables['hasdata'][:, :], [0, 1, 2], clip_on=False)
mp.postprocess(filename='test.png')

