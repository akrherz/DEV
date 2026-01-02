"""
Dave provided a HUC12 shapefile used by ACPF in EPSG:5070, I did not need that
resolution, so I

    ogr2ogr -simplify 500 huc12.shp US48_HUC12_Oct2024.shp

"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyiem.grid.nav import get_nav
from pyiem.util import ncopen
from tqdm import tqdm

CSV = Path("acpf_huc12_climate.csv")


def create_baseline():
    """Create the basic csv that gets added to later."""
    prism_nav = get_nav("prism")
    gdf = gpd.read_file("huc12.shp")
    gdf["centroid"] = gdf.geometry.centroid.to_crs(4326)
    ij = gdf.apply(
        lambda row: prism_nav.find_ij(row["centroid"].x, row["centroid"].y),
        axis=1,
    )
    with open(CSV, "w") as fh:
        fh.write("huc12,prism_grid_i,prism_grid_j\n")
        for huc12, _ij in zip(gdf["huc12"].values, ij, strict=True):
            fh.write(f"{huc12},{_ij[0]},{_ij[1]}\n")


def main():
    """Go Main Go."""
    if not CSV.exists():
        create_baseline()
    statsdf = pd.read_csv(CSV, dtype={"huc12": str})

    with ncopen("/mesonet/data/prism/prism_monthlyc.nc") as nc:
        for month in tqdm(range(1, 13)):
            ppt = nc.variables["ppt"][month - 1]
            tmin = nc.variables["tmin"][month - 1]
            tmax = nc.variables["tmax"][month - 1]
            for idx, row in statsdf.iterrows():
                i = row["prism_grid_i"]
                j = row["prism_grid_j"]
                statsdf.at[idx, f"precip_{month:02.0f}_sum_mm"] = ppt[j, i]
                statsdf.at[idx, f"tmin_{month:02.0f}_avg_c"] = tmin[j, i]
                statsdf.at[idx, f"tmax_{month:02.0f}_avg_c"] = tmax[j, i]

    with ncopen("/mesonet/data/prism/prism_yearlyc.nc") as nc:
        ppt = nc.variables["ppt"]
        tmin = nc.variables["tmin"]
        tmax = nc.variables["tmax"]
        for idx, row in statsdf.iterrows():
            i = row["prism_grid_i"]
            j = row["prism_grid_j"]
            statsdf.at[idx, "precip_year_sum_mm"] = ppt[j, i]
            statsdf.at[idx, "tmin_year_avg_c"] = tmin[j, i]
            statsdf.at[idx, "tmax_year_avg_c"] = tmax[j, i]

    statsdf.to_csv(CSV, index=False, float_format="%.2f")


if __name__ == "__main__":
    main()
