"""Make a GeoTIFF."""

import numpy as np
import rasterio
from rasterio.transform import from_origin

import pandas as pd


def main():
    """Go Main Go."""
    df = pd.read_csv("data.csv")
    img = np.ma.zeros((60, 120))
    for _, row in df.iterrows():
        x = int((row["lon"] + 104.0) / 0.25)
        y = int((row["lat"] - 34.0) / 0.25)
        img[y, x] = row["rfactor_yr_avg"]
    img.mask = np.ma.where(img == 0)
    transform = from_origin(-104, 49, 0.25, 0.25)

    with rasterio.open(
        "rfactor.tif",
        "w",
        driver="GTiff",
        height=img.shape[0],
        width=img.shape[1],
        count=1,
        dtype=str(img.dtype),
        crs="+proj=longlat +datum=WGS84 +no_defs ",
        transform=transform,
    ) as rst:
        rst.write(np.flipud(img), 1)
        rst.write_mask(True)


if __name__ == "__main__":
    main()
