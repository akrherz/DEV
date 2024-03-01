"""Example using rasterio."""

import numpy as np
import rasterio
from PIL import Image
from rasterio import Affine
from rasterio.warp import Resampling, reproject

import cartopy.crs as ccrs
import matplotlib.colors as mpcolors
import matplotlib.pyplot as plt

# EPSG 5070
ax = plt.axes(
    [0.1, 0.1, 0.8, 0.8],
    projection=ccrs.AlbersEqualArea(
        central_longitude=-96,
        central_latitude=23,
        standard_parallels=[29.5, 45.5],
    ),
    aspect="auto",
)
ax.set_extent([-120, -60, 22, 53], crs=ccrs.PlateCarree())

im = np.asarray(Image.open("n0q_202102100000.png"))
with rasterio.Env():
    src_aff = Affine(0.005, 0, -126, 0, -0.005, 50)
    (px0, px1, py0, py1) = ax.get_extent()
    pixel_bbox = ax.get_window_extent()
    dx = (px1 - px0) / pixel_bbox.width
    dy = (py1 - py0) / pixel_bbox.height
    dest_aff = Affine(dx, 0, px0, 0, dy, py0)
    src_crs = {"init": "EPSG:4326"}

    res = np.zeros((int(pixel_bbox.height), int(pixel_bbox.width)))
    reproject(
        im,
        res,
        src_transform=src_aff,
        src_crs=src_crs,
        dst_transform=dest_aff,
        dst_crs=ax.projection.proj4_params,
        resampling=Resampling.nearest,
    )

# Use jet to upset the cartographers on twitter
cmap = plt.get_cmap("jet")
cmap.set_under((0, 0, 0, 0))
norm = mpcolors.BoundaryNorm(np.arange(1, 256), cmap.N)
ax.imshow(
    res,
    extent=(px0, px1, py0, py1),
    zorder=20,
    cmap=cmap,
    norm=norm,
    origin="lower",
)

plt.savefig("test.png")
