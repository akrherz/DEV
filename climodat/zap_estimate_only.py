"""Remove realtime status for sites that are getting 100% estimates.

We generally do not want to have climodat realtime stations that are purely
estimated for one of the variables.  Some sites only report temp or precip
for example.  This script will remove realtime status for such sites.

Note: This is chunking a year at a time, attm.
"""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.reference import state_names
from sqlalchemy import text


def do(sid: str):
    """Do great things."""
    with get_sqlalchemy_conn("coop") as conn:
        yearly = pd.read_sql(
            text("""
            select year,
            sum(case when temp_estimated then 1 else 0 end) as testimated,
            sum(case when precip_estimated then 1 else 0 end) as pestimated,
            count(*) as obs
            from alldata where station = :sid GROUP by year ORDER by year ASC
            """),
            conn,
            index_col="year",
            params={"sid": sid},
        )
    delete_years = []
    for year, row in yearly.iterrows():
        if row["testimated"] == row["obs"] and row["pestimated"] == row["obs"]:
            delete_years.append(year)
            continue
        break

    if not delete_years:
        return
    if len(delete_years) == len(yearly.index):
        print(f"---------> Refusing to delete all {sid} data...")
        return

    with get_sqlalchemy_conn("coop") as conn:
        res = conn.execute(
            text(
                """
            DELETE from alldata where station = :sid and year = ANY(:years)
            """
            ),
            {
                "sid": sid,
                "years": delete_years,
            },
        )
        print(
            f"Removed {res.rowcount:6.0f} for {sid} "
            f"{delete_years[0]}-{delete_years[-1]}"
        )
        conn.commit()


@click.command()
@click.option("--state", help="Two character state identifier")
def main(state):
    """Workflow."""
    if state:
        states = [state]
    else:
        states = state_names
    for state in states:
        nt = NetworkTable(f"{state}CLIMATE", only_online=False)
        for sid in nt.sts:
            # These sites are always estimated.
            if sid[2:] == "0000" or sid[2] in ["C", "D"]:
                continue
            do(sid)


if __name__ == "__main__":
    main()
