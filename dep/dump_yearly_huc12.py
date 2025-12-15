"""Create a dump of yearly huc12 results."""

import pandas as pd
from pydep.reference import KG_M2_TO_TON_ACRE
from pyiem.database import get_sqlalchemy_conn, sql_helper


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        df = pd.read_sql(
            sql_helper("""
                with data as (
                select huc_12, extract(year from valid) as year,
                sum(qc_precip) / 25.4 as precip_inch,
                sum(avg_loss) * :factor as detachment_ta,
                sum(avg_delivery) * :factor as delivery_ta,
                sum(avg_runoff) / 25.4 as runoff_inch
                from results_by_huc12 WHERE valid >= '2020-01-01'
                and scenario = 0 GROUP by huc_12, year),
                agg as (
                 select d.*, h.ugc from data d JOIN huc12 h on
                 (d.huc_12 = h.huc_12) where h.scenario = 0
                 )
                select ugc, year,
                avg(precip_inch) as precip_inch,
                avg(detachment_ta) as detachment_ta,
                avg(delivery_ta) as delivery_ta,
                avg(runoff_inch) as runoff_inch
                from agg GROUP by ugc, year
            """),
            conn,
            params={"factor": KG_M2_TO_TON_ACRE},
            index_col=None,
        )

    df = df.pivot(
        index="ugc",
        columns="year",
        values=["precip_inch", "detachment_ta", "delivery_ta", "runoff_inch"],
    )
    df.columns = [
        "_".join([a[0], str(int(a[1]))]) for a in df.columns.to_flat_index()
    ]
    df = df.reset_index()
    df.to_csv("dep_yearly_by_ugc_241011.csv", index=False)


if __name__ == "__main__":
    main()
