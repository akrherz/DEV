"""Map of Station counts, maybe."""

from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_dbconn
import pandas as pd


def main():
    """Go Main Go."""
    df = pd.read_sql(
        "SELECT ST_Area(the_geom::geography) / 1000000000. as area, "
        "state_abbr from states where state_abbr != 'DC' ORDER by state_abbr",
        get_dbconn("postgis"),
        index_col="state_abbr",
    )
    stations = pd.read_sql(
        "SELECT state, count(*) from stations where "
        "network ~* 'DCP' and archive_begin is not null "
        "GROUP by state",
        get_dbconn("mesosite"),
        index_col="state",
    )
    df["density"] = stations["count"] / df["area"]

    m = MapPlot(
        twitter=True,
        sector="custom",
        west=-90,
        east=-70,
        south=36,
        north=48,
        title="Number of NWS SHEF Reporting Sites per 1,000 sq km by State",
        subtitle=(
            "Based on IEM archives since 2010, excludes COOP "
            "includes HADS/DCP/LARC,etc sites reporting in SHEF."
        ),
        axisbg="white",
    )

    cmap = get_cmap("plasma")
    m.fill_states(
        df["density"].to_dict(),
        bins=[1, 2, 3, 4, 5, 6, 7, 10, 15],
        spacing="proportional",
        units="stations per 1000 sq km",
        ilabel=True,
        lblformat="%.1f",
        cmap=cmap,
        labelbuffer=1,
    )

    m.postprocess(filename="states.png")


if __name__ == "__main__":
    main()
