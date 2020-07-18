"""Plot an IEM NEXRAD Composite RASTER on a cartopy map"""

import matplotlib.pyplot as plt
from matplotlib.image import imread
import cartopy.crs as ccrs

# wget https://mesonet.agron.iastate.edu/
# archive/data/2017/08/19/GIS/uscomp/n0q_201708190300.png
# wget https://mesonet.agron.iastate.edu/
# archive/data/2017/08/19/GIS/uscomp/n0q_201708190300.wld


def main():
    """Go Main!"""
    img = imread("n0q_201708190300.png")
    # The color index to dbz conversion is as such
    # https://mesonet.agron.iastate.edu/GIS/rasters.php?rid=2
    # n0q_dbz = (colorindex - 65.) * 0.5
    (rows, cols, _bands) = img.shape
    (dx, _, _, dy, west, north) = [
        float(line) for line in open("n0q_201708190300.wld").readlines()
    ]
    east = west + dx * cols
    south = north + dy * rows  # dy is negative
    ax = plt.axes(
        projection=ccrs.NearsidePerspective(
            satellite_height=10000000.0,
            central_longitude=-92.0,
            central_latitude=42.0,
        )
    )
    # Note that plotting the entire array made my laptop have kittens
    ax.imshow(
        img[::25, ::25, :],
        origin="upper",
        transform=ccrs.PlateCarree(),
        extent=[west, east, south, north],
    )

    ax.coastlines()

    plt.gcf().savefig("example.png")


if __name__ == "__main__":
    main()
