"""Line Collection Troubles."""

from pyiem.plot.use_agg import plt
from shapely.geometry import LineString
import geopandas as gpd


def main():
    """Go Main Go."""
    ls1 = LineString([(0, 0), (1, 1)])
    ls2 = LineString([(0, 1), (1, 0)])
    df1 = gpd.GeoDataFrame({"geometry": [ls1]})
    df2 = gpd.GeoDataFrame({"geometry": [ls2]})

    ax = df1.plot(zorder=2, color="r", lw=5)
    ax = df2.plot(ax=ax, zorder=1, color="b", lw=5)
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
