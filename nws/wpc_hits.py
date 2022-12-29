"""Map of states with WPC glory."""

from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.util import get_sqlalchemy_conn
import pandas as pd


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
            with data as (
                select distinct state, date from wpc_national_high_low
                where n_x = 'N'
            )
            select state, count(*) from data GROUP by state ORDER by count asc
            """,
            conn,
            index_col="state",
        )

    mp = MapPlot(
        twitter=True,
        sector="conus",
        title="Jul 2008 - 2022 Days Having Coolest WPC Temperature",
        subtitle=(
            "Based on unoffical IEM archives, "
            "ties between states are double counted."
        ),
        axisbg="white",
    )

    cmap = get_cmap("plasma")
    bins = pretty_bins(1, df["count"].max())
    bins[0] = 1
    mp.fill_states(
        df["count"].to_dict(),
        bins=bins,
        spacing="proportional",
        units="days",
        ilabel=True,
        lblformat="%.0f",
        cmap=cmap,
        labelbuffer=0,
    )

    mp.postprocess(filename="wpc_min.png")


if __name__ == "__main__":
    main()
