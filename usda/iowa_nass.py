"""Some fruits for my horror."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot, get_cmap


def main():
    """Go Main."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            select * from nass_iowa where metric = 'days suitable'
            and extract(month from valid) in (4, 5)
            """,
            conn,
            parse_dates=["valid"],
        )
    means = df.mean(numeric_only=True)
    data = {
        "IAC001": means["nw"] / 7.0 * 60.0,
        "IAC002": means["nc"] / 7.0 * 60.0,
        "IAC003": means["ne"] / 7.0 * 60.0,
        "IAC004": means["wc"] / 7.0 * 60.0,
        "IAC005": means["c"] / 7.0 * 60.0,
        "IAC006": means["ec"] / 7.0 * 60.0,
        "IAC007": means["sw"] / 7.0 * 60.0,
        "IAC008": means["sc"] / 7.0 * 60.0,
        "IAC009": means["se"] / 7.0 * 60.0,
    }
    mp = MapPlot(
        sector="iowa",
        title="2009-2023 Iowa NASS Estimated Days Suitable during April/May",
        subtitle=(
            f"Based on {len(df.index)} Weekly Iowa NASS Ag District Reports"
        ),
    )
    cmap = get_cmap("viridis")
    mp.fill_climdiv(
        data, ilabel=True, lblformat="%.1f", cmap=cmap, bins=range(26, 33, 2)
    )
    mp.postprocess(filename="231220.png")


if __name__ == "__main__":
    main()
