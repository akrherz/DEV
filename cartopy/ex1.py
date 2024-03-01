"""Unsure what this was."""

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

projection = ccrs.GOOGLE_MERCATOR
fig = plt.figure(figsize=(12, 6))
ax = fig.add_axes(
    [0.01, 0.01, 0.98, 0.98],
    aspect="equal",
    # autoscale_on=True,
    adjustable="datalim",
    projection=projection,
)
ax.set_extent([-1e6, 1e6, -1e6, 1e6], crs=projection)
ax.plot([-1e6, 1e6], [-1e6, 1e6], lw=3)
print(ax.get_extent())
print(ax.dataLim)
print(ax.viewLim)
fig.savefig("test.png")
