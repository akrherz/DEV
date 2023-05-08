import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString


def main():
    ls1 = LineString([(0, 0), (1, 1)])
    ls2 = LineString([(0, 1), (1, 0)])
    df1 = gpd.GeoDataFrame({"geometry": [ls1]})
    df2 = gpd.GeoDataFrame({"geometry": [ls2]})

    fig = plt.figure()
    ax = fig.add_axes(
        [0.1, 0.1, 0.7, 0.8], aspect="equal", adjustable="datalim"
    )
    ax.autoscale(False)
    ax.set_xlim(0.25, 1)
    ax.set_ylim(0.25, 0.75)

    df1.plot(ax=ax, zorder=2, color="r", lw=5)
    df2.plot(ax=ax, zorder=1, color="b", lw=5)
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
