"""See what our NLDN data has for a heatmap."""

import geopandas as gpd

from matplotlib.colorbar import ColorbarBase
import matplotlib.colors as mpcolors
from pyiem.reference import Z_FILL, IA_EAST, IA_NORTH, IA_SOUTH, IA_WEST
from pyiem.util import get_dbconn
from pyiem.plot import MapPlot, get_cmap


def main():
    """Go Main Go."""
    # polygon bounds of Iowa
    wkt = "ST_SETSRID(ST_MakeEnvelope(-96.7, 40.3, -90.1, 43.6, 4326), 4326)"
    nldn = gpd.read_postgis(
        "SELECT geom from nldn_all WHERE "
        f"ST_Contains({wkt}, geom) and "
        "valid >= '2021-01-01' and valid < '2022-01-01'",
        get_dbconn("nldn"),
    )
    nldn = nldn.to_crs(epsg=4326)
    print(nldn)
    mp = MapPlot(
        sector="custom",
        west=IA_WEST,
        east=IA_EAST,
        south=IA_SOUTH,
        north=IA_NORTH,
        continentalcolor="k",
        statebordercolor="white",
        title="15 Dec 2021 Serial Derecho",
        twitter=True,
        caption="@akrherz",
    )
    ncmap = get_cmap("binary_r")
    ncmap.set_under("#000000")
    ncmap.set_over("red")
    nbins = list(range(20, 81, 10))
    nbins[0] = 1
    nnorm = mpcolors.BoundaryNorm(nbins, ncmap.N)

    print(mp.panels[0].get_extent())
    mp.panels[0].ax.hexbin(
        nldn["geom"].x,
        nldn["geom"].y,
        cmap=ncmap,
        norm=nnorm,
        zorder=Z_FILL - 1,
        extent=mp.panels[0].get_extent(),
        gridsize=(600, 370),
    )

    ncax = mp.fig.add_axes(
        [0.92, 0.3, 0.02, 0.2],
        frameon=True,
        facecolor="#EEEEEE",
        yticks=[],
        xticks=[],
    )

    ncb = ColorbarBase(
        ncax, norm=nnorm, cmap=ncmap, extend="max", spacing="proportional"
    )
    ncb.set_label(
        "Strikes per ~24 km cell, courtesy Vaisala NLDN",
        loc="bottom",
    )
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
