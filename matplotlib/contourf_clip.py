"""One Off."""
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.path import Path
from matplotlib.patches import Polygon, PathPatch
import numpy
from scipy.interpolate import griddata


def mask_outside_polygon(poly_verts, ax=None):
    """
        Plots a mask on the specified axis ("ax", defaults to plt.gca()) such
    that
        all areas outside of the polygon specified by "poly_verts" are masked.

        "poly_verts" must be a list of tuples of the verticies in the polygon in
        counter-clockwise order.

        Returns the matplotlib.patches.PathPatch instance plotted on the figure.
    """
    import matplotlib.patches as mpatches
    import matplotlib.path as mpath

    if ax is None:
        ax = plt.gca()

    # Get current plot limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Verticies of the plot boundaries in clockwise order
    bound_verts = [
        (xlim[0], ylim[0]),
        (xlim[0], ylim[1]),
        (xlim[1], ylim[1]),
        (xlim[1], ylim[0]),
        (xlim[0], ylim[0]),
    ]

    # A series of codes (1 and 2) to tell matplotlib whether to draw a lineor
    # move the "pen" (So that there's no connecting line)
    bound_codes = [mpath.Path.MOVETO] + (len(bound_verts) - 1) * [
        mpath.Path.LINETO
    ]
    poly_codes = [mpath.Path.MOVETO] + (len(poly_verts) - 1) * [
        mpath.Path.LINETO
    ]
    # Plot the masking patch
    path = mpath.Path(bound_verts + poly_verts, bound_codes + poly_codes)
    patch = mpatches.PathPatch(
        path, facecolor="white", edgecolor="b", zorder=3
    )
    patch = ax.add_patch(patch)

    # Reset the plot limits to their original extents
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    return patch


def main():
    """Go Main Go."""
    lats = 39 + (6.0 * numpy.random.random_sample(1000))
    lons = -100 + (10.0 * numpy.random.random_sample(1000))
    vals = 0 + (30.0 * numpy.random.random_sample(1000))

    xi = numpy.linspace(-95, -90, 100)
    yi = numpy.linspace(39, 47, 100)
    xi, yi = numpy.meshgrid(xi, yi)
    vals = griddata(zip(lons, lats), vals, (xi, yi), "cubic")
    lons = xi
    lats = yi

    fig = plt.figure(num=None, figsize=(10.24, 7.68))
    fig.subplots_adjust(bottom=0, left=0, right=1, top=1, wspace=0, hspace=0)

    ax = plt.axes([0.01, 0.05, 0.9, 0.85], axisbg=(0.4471, 0.6235, 0.8117))

    m = Basemap(
        llcrnrlon=-100.0,
        llcrnrlat=38.0,
        urcrnrlon=-90.0,
        urcrnrlat=44.0,
        rsphere=(6378137.00, 6356752.3142),
        resolution="l",
        projection="merc",
        lat_0=40.0,
        lon_0=-20.0,
        lat_ts=20.0,
    )
    m.fillcontinents(color="1.0")

    x = [-95, -92, -92, -95, -95]
    y = [42, 42, 43, 43, 42]
    # x = [-95,-95,-92,-92,-95]
    # y = [42,43,43,42,42]
    xx, yy = m(x, y)
    path = Path(zip(xx, yy))
    patch = PathPatch(path, facecolor="none")
    ax.add_patch(patch)

    x, y = m(lons, lats)
    cs = m.contourf(x, y, vals, numpy.arange(0, 30, 2), zorder=2)

    poly = zip(xx, yy)
    mask_outside_polygon(poly, ax=ax)
    m.drawstates(linewidth=2, zorder=4)
    cbar = m.colorbar(cs, location="right", pad="1%", ticks=cs.levels)
    cbar.set_label("mph")

    plt.savefig("test.png")


if __name__ == "__main__":
    main()
