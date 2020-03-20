from __future__ import print_function
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

ax = plt.axes(projection=ccrs.Mercator())
ax.set_extent([-120, -60, 10, 60], crs=ccrs.PlateCarree())
print(ax.get_extent())
# ax.background_patch.set_facecolor('k')
ax.coastlines(color="k")
polycollect = ax.hexbin(
    range(-120, -80, 1),
    range(10, 50, 1),
    range(40),
    bins=range(40),
    transform=ccrs.PlateCarree(),
)
transform, transOffset, offsets, paths = polycollect._prepare_points()
for poly in paths:
    print(poly)

plt.savefig("test.png")
