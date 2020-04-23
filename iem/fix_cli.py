"""Fix sky_coverage field."""
import datetime
import requests

from pyiem.util import get_dbconn, noaaport_text
from pyiem.nws.products.cli import parser


def do(valid):
    """Process."""
    dbconn = get_dbconn("iem")
    cursor = dbconn.cursor()
    cursor2 = dbconn.cursor()
    cursor.execute(
        "select station, product from cli_data WHERE valid = %s "
        "and average_sky_cover is null",
        (valid,),
    )
    for row in cursor:
        uri = f"http://iem.local/api/1/nwstext/{row[1]}"
        req = requests.get(uri)
        if req.status_code == 404:
            print(f"missing {row[1]}")
            continue
        cli = parser(noaaport_text(req.content.decode("ascii", "ignore")))
        val = cli.data[0]["data"].get("average_sky_cover")
        if val is None:
            continue
        print(f"{row[0]} {valid} {val}")
        cursor2.execute(
            "UPDATE cli_data SET average_sky_cover = %s WHERE "
            "station = %s and valid = %s",
            (val, row[0], valid),
        )

    cursor2.close()
    dbconn.commit()


def main():
    """Go Main."""
    sts = datetime.date(2020, 1, 1)
    ets = datetime.date(2020, 4, 24)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        do(now)
        now += interval


if __name__ == "__main__":
    main()
