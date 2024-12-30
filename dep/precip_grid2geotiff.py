"""We converted from numpy grid to GeoTIFF."""

import gzip
import os

import numpy as np
import pandas as pd
import rasterio
from affine import Affine
from tqdm import tqdm


def main():
    """Go."""
    progress = tqdm(pd.date_range("2007/01/01", "2024/12/29"))
    for dt in progress:
        progress.set_description(dt.strftime("%Y-%m-%d"))
        fn = dt.strftime("/mnt/idep2/data/dailyprecip/%Y/%Y%m%d.npy.gz")
        if not os.path.isfile(fn):
            continue
        with gzip.GzipFile(fn, "r") as src:
            values = np.flipud(np.load(file=src))
        values = (values * 100.0).astype(np.uint16)
        with rasterio.open(
            fn.replace(".npy.gz", ".geotiff"),
            "w",
            driver="GTiff",
            compress="lzw",
            height=values.shape[0],
            width=values.shape[1],
            count=1,
            dtype=values.dtype,
            crs="EPSG:4326",
            # This is not exactly right, but close enough until reprocessing
            transform=Affine(0.01, 0.0, -126.005, 0.0, -0.01, 49.995),
        ) as dst:
            dst._set_all_scales([0.01])
            dst._set_all_offsets([0.0])
            dst.write(values, 1)


if __name__ == "__main__":
    main()
