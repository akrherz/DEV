"""Send the raw archived data back through IEMAccess for reprocessing."""

from zoneinfo import ZoneInfo

import click
from pandas.io.sql import read_sql
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.models.shef import SHEFElement


def get_tzname(station):
    """Figure out the timezone."""
    pgconn, cursor = get_dbconnc("mesosite")
    cursor.execute(
        "SELECT tzname from stations where id = %s",
        (station,),
    )
    try:
        return cursor.fetchone()["tzname"]
    finally:
        cursor.close()
        pgconn.close()


@click.command()
@click.option("--station", help="Station to process")
def main(station):
    """Go Main."""
    tz = ZoneInfo(get_tzname(station))
    with get_sqlalchemy_conn("hads") as pgconn:
        df = read_sql(
            "SELECT *, valid at time zone 'UTC' as utc_valid from raw "
            "WHERE station = %s ORDER by valid ASC LIMIT 10000",
            pgconn,
            params=(station,),
        )
    df["valid"] = df["utc_valid"].dt.tz_localize("UTC").dt.tz_convert(tz)
    if len(df.index) == 10_000:
        print("Aborting, as there is too much data in database.")
        return
    for valid, obs in df.groupby("valid"):
        elements = []
        for row in obs.itertuples(index=False):
            elements.append(
                SHEFElement(
                    station=station,
                    basevalid=valid,
                    valid=valid,
                    num_value=row.value,
                    physical_element=row.key[:2],
                    duration=row.key[2],
                    source=row.key[3:5],
                    extremum=row.key[5],
                )
            )
        print(valid, elements)


if __name__ == "__main__":
    main()
