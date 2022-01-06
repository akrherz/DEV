"""See what our NLDN data has for a heatmap."""

import geopandas as gpd

from matplotlib.colorbar import ColorbarBase
import matplotlib.colors as mpcolors
from pyiem.reference import Z_FILL
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
    mp = MapPlot(
        sector="iowa",
        continentalcolor="white",
        statebordercolor="white",
        title="15 Dec 2021 Serial Derecho",
        twitter=True,
        caption="@akrherz",
    )
    nldn = nldn.to_crs(mp.panels[0].crs)
    ncmap = get_cmap("copper")
    ncmap.set_under("#EEEEEE")
    ncmap.set_over("red")
    nbins = [2 ** i for i in range(0, 7)]
    scaled = [n * 25 for n in nbins]
    nnorm = mpcolors.BoundaryNorm(scaled, ncmap.N)

    xmin, xmax, ymin, ymax = mp.panels[0].get_extent(crs=mp.panels[0].crs)
    xs = (xmax - xmin) / 5000  # 2km
    ys = (ymax - ymin) / 5000  # 2km
    print(f"{xs:.2f} {ys:.2f}")
    mp.panels[0].ax.hexbin(
        nldn["geom"].x,
        nldn["geom"].y,
        cmap=ncmap,
        norm=nnorm,
        zorder=Z_FILL - 1,
        extent=mp.panels[0].get_extent(),
        gridsize=(int(xs), int(ys)),
    )

    ncax = mp.fig.add_axes(
        [0.92, 0.3, 0.02, 0.6],
        frameon=True,
        facecolor="#EEEEEE",
        yticks=[],
        xticks=[],
    )

    # 2km hack
    nnorm = mpcolors.BoundaryNorm(nbins, ncmap.N)
    ncb = ColorbarBase(
        ncax, norm=nnorm, cmap=ncmap, extend="both", spacing="uniform"
    )
    ncb.set_label(
        "Events per sqkm, courtesy Vaisala NLDN",
        loc="bottom",
    )
    mp.fig.savefig("test.png")


if __name__ == "__main__":
    main()
