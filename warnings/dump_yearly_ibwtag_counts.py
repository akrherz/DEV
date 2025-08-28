"""I write things for folks."""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper


@click.command()
@click.option("--phenomena", required=True)
@click.option("--column", required=True)
def main(phenomena: str, column: str):
    """Go Main Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        tags = pd.read_sql(
            sql_helper(
                """
    select vtec_year, {column}, count(*) from sbw
    where phenomena = :ph and significance = 'W' and status = 'NEW'
    GROUP by vtec_year, {column}
    """,
                column=column,
            ),
            conn,
            params={"ph": phenomena},
        )
    tags = tags.pivot(index="vtec_year", columns=column, values="count")
    tags["total"] = tags.sum(axis=1)
    print(tags)
    tags.to_excel(f"{phenomena}_{column}_counts.xlsx")


if __name__ == "__main__":
    main()
