"""
We have database entries with a double dollar sign ($$) as the forecaster.
Let us try to do better.
"""

import time

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from sqlalchemy import text


@click.command()
@click.option("--year", type=int, default=2021, help="Year to process")
@click.option("--chunksize", type=int, default=10, help="Chunksize")
def main(year: int, chunksize: int):
    """Go."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                "select vtec_year, ctid, product_ids[1] as product_id "
                "from warnings where vtec_year = :year and fcster = '$$' "
                "ORDER by product_issue asc LIMIT :chunksize"
            ),
            conn,
            params={"year": year, "chunksize": chunksize},
        )
    conn, cursor = get_dbconnc("postgis")
    for _, row in df.iterrows():
        req = httpx.get(
            "http://mesonet.agron.iastate.edu/api/1/nwstext/"
            f"{row['product_id']}"
        )
        if req.status_code != 200:
            print(f"Failed to fetch {row['product_id']}")
            continue
        raw = req.text.strip().replace("\003", "").replace("\001", "")
        lines = [x.strip() for x in raw.split("\n") if x.strip() != ""]
        # Look backwards at most 3 non-b
        newval = None
        for line in lines[::-1][:3]:
            # OK, keep looking
            if line in ["&&", "$$", "NNNN", "&", "$"]:
                continue
            # Phrase, DQ
            if line.find(" ") > -1 or line.find(".") > -1:
                break
            if 0 < len(line) < 25:
                newval = line
                break
        print(f"Updating to {row['product_id']} -> {repr(newval)}")
        cursor.execute(
            "UPDATE warnings SET fcster = %s "
            "WHERE vtec_year = %s and ctid = %s",
            (newval, row["vtec_year"], row["ctid"]),
        )
    cursor.close()
    conn.commit()

    if len(df.index) != chunksize:
        print("Ran dry")
        time.sleep(3000)


if __name__ == "__main__":
    main()
