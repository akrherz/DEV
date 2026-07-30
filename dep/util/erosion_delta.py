"""Plot."""

import calendar

import numpy as np
import pandas as pd
from dailyerosion.reference import KG_M2_TO_TON_ACRE
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure_axes


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        df = pd.read_sql(
            sql_helper("""
        with two as (
            select to_char(valid, 'mmdd') as sday,
            sum(avg_delivery_kgm2) * :factor as delivery,
            sum(avg_loss_kgm2) * :factor as loss
            from water_results_by_huc12 w JOIN huc12 h
                on (w.huc12_id = h.huc12_id)
            where huc12_code = '102300070305' and valid < '2023-01-01'
            and w.scenario_id = 0 group by sday),
        one as (
            select to_char(valid, 'mmdd') as sday,
            sum(avg_delivery_kgm2) * :factor as delivery,
            sum(avg_loss_kgm2) * :factor as loss
                from water_results_by_huc12_save w JOIN huc12 h
                on (w.huc12_id = h.huc12_id)
            where huc12_code = '102300070305' and valid < '2023-01-01'
            and w.scenario_id = 0 group by sday)
            select t.sday, t.delivery - o.delivery as del_delivery,
            t.loss - o.loss as del_loss
            from two t JOIN one o on (t.sday = o.sday) ORDER by t.sday asc
        """),
            conn,
            params={"factor": KG_M2_TO_TON_ACRE / 16},
            index_col="sday",
        )

    fig, ax = figure_axes(
        title="DEP Change in Daily Soil Delivery HUC12: 102300070305",
        subtitle="2007-2022 Change from Baseline to Dynamic Tillage",
        logo="dep",
        figsize=(8, 6),
    )
    ax.bar(
        np.arange(0, len(df.index)),
        df["del_delivery"],
    )
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylabel("Total Soil Delivery [T/a]")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
