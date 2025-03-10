import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import netCDF4
import numpy as np

nc = netCDF4.Dataset("NoBCNoRR.nc4")
data = nc.variables["SOC030_kgha"][30, 0, 0, :, :]
lons, lats = np.meshgrid(nc.variables["lon"][:], nc.variables["lat"][:])

ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-100, -80, 30, 45], crs=ccrs.PlateCarree())
res = ax.pcolormesh(lons, lats, data.T)
plt.gcf().colorbar(res)
ax.coastlines()
plt.gcf().savefig("test.png")
