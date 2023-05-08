"""Make something pretty."""

from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot


def main():
    """Go Main Go."""
    nt = NetworkTable("ISUSM")
    counties = {}
    lons = []
    lats = []
    vals = []
    for sid in nt.sts:
        counties[nt.sts[sid]["ugc_county"]] = 1
        lons.append(nt.sts[sid]["lon"])
        lats.append(nt.sts[sid]["lat"])
        vals.append("x")

    mp = MapPlot(
        title="ISU Soil Moisture Station Locations + Counties Covered",
        subtitle="As of 7 Jan 2020, %i stations in %i counties"
        % (len(nt.sts), len(counties)),
        nocaption=True,
    )
    mp.fill_ugcs(counties, bins=[0, 1, 2])
    mp.plot_values(lons, lats, vals, textsize=18, labelbuffer=0)
    mp.postprocess(filename="map.png")


if __name__ == "__main__":
    main()
