from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from cartopy.util import add_cyclic_point
import cartopy.crs as ccrs

# Read test data
nc_fid = Dataset("test_data.nc", "r")
lat = nc_fid.variables["lat"][:]
lon = nc_fid.variables["lon"][:]
var = nc_fid.variables["LWCF(test - reference)"][:]
cyclic_data, cyclic_lons = add_cyclic_point(var, coord=lon)

# Plot it
fig = plt.figure()
ax = fig.add_axes()

# These contour levels work fine...
# levels =[-35, -30, -25, -20, -15, -10, 0, 10, 15, 20, 25, 30, 35]
# ...but slightly tweaking them results in a failure:
levels = [-35, -30, -25, -20, -15, -10, -5, -2, 2, 5, 10, 15, 20, 25, 30, 35]

proj = ccrs.PlateCarree(central_longitude=180)
ax = plt.axes(projection=proj)
p1 = ax.contourf(
    cyclic_lons,
    lat,
    cyclic_data,
    transform=ccrs.PlateCarree(),
    norm=None,
    levels=levels,
    cmap="bwr",
    extend="both",
)
ax.coastlines(lw=0.3)
ax.set_xticks([-180, -120, -60, 0, 60, 120, 180])
ax.set_yticks([-90, -60, -30, 0, 30, 60, 90])

# Color bar
cbax = fig.add_axes()
cbar = fig.colorbar(p1, cax=cbax)

plt.savefig("test.png", dpi=150)
