"""Create a dump of yearly huc12 results."""

import pandas as pd
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        df = pd.read_sql(
            """
            with data as (
                select huc_12, unnest(string_to_array(states, ',')) as state
                from huc12 where scenario = 0),
            stats as (
                select huc_12, extract(year from valid) as year,
                sum(qc_precip) / 25.4 as precip_inch,
                sum(avg_loss) * 4.463 as detachment_ta,
                sum(avg_delivery) * 4.463 as delivery_ta,
                sum(avg_runoff) / 25.4 as runoff_inch
                from results_by_huc12 WHERE valid < '2023-01-01'
                and scenario = 0 GROUP by huc_12, year)
            select s.*, a.state from stats s, data a WHERE s.huc_12 = a.huc_12
            """,
            conn,
            index_col=None,
        )
    df = df.pivot(
        index=["huc_12", "state"],
        columns="year",
        values=["precip_inch", "detachment_ta", "delivery_ta", "runoff_inch"],
    )
    df.columns = [
        "_".join([a[0], str(int(a[1]))]) for a in df.columns.to_flat_index()
    ]
    df = df.reset_index()
    df.to_csv("huc12_230126.csv", index=False)


if __name__ == "__main__":
    main()
