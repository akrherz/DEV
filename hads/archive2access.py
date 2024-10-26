"""Send the raw archived data back through IEMAccess for reprocessing."""

from zoneinfo import ZoneInfo

import click
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.models.shef import SHEFElement
from pyiem.util import logger
from pywwa.workflows.shef import (
    ACCESSDB_QUEUE,
    load_stations,
    process_site_time,
    write_access_record,
)
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()


def get_tzname(station):
    """Figure out the timezone."""
    pgconn, cursor = get_dbconnc("mesosite")
    load_stations(cursor)
    cursor.execute(
        "SELECT tzname from stations where id = %s",
        (station,),
    )
    row = cursor.fetchone()
    cursor.close()
    pgconn.close()
    tzname = row["tzname"]
    return tzname


class FakeProd:
    afos = None

    def get_product_id(self):
        return None


@click.command()
@click.option("--station", help="Station to process")
def main(station):
    """Go Main."""
    tz = ZoneInfo(get_tzname(station))
    with get_sqlalchemy_conn("hads") as pgconn:
        df = pd.read_sql(
            text(
                "SELECT *, valid at time zone 'UTC' as utc_valid from raw "
                "WHERE station = :sid and value > -990 "
                "ORDER by valid ASC LIMIT 10000"
            ),
            pgconn,
            params={"sid": station},
        )
    df["valid"] = df["utc_valid"].dt.tz_localize("UTC").dt.tz_convert(tz)
    if len(df.index) == 10_000:
        print("Aborting, as there is too much data in database.")
        return
    prod = FakeProd()
    for valid, obs in df.groupby("valid"):
        elements = []
        for row in obs.itertuples(index=False):
            elem = SHEFElement(  # type: ignore
                station=station,
                basevalid=valid,
                valid=valid,
                num_value=row.value,
            )
            elem.consume_code(row.key)
            elements.append(elem)
        process_site_time(prod, station, valid, elements)
    conn, cursor = get_dbconnc("iem")
    cursor.close()
    for iemid, entry in ACCESSDB_QUEUE.items():
        progress = tqdm(entry.records.items())
        for localts, record in progress:
            progress.set_description(f"{localts:%Y-%m-%d %H:%M}")
            # Get a reference and delete it from the dict
            cursor = conn.cursor()
            write_access_record(cursor, record, iemid, localts, entry)
            cursor.close()
            conn.commit()


if __name__ == "__main__":
    main()
