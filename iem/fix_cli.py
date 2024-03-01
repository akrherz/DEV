"""Fix sky_coverage field."""

import datetime

import requests

from pyiem.nws.products.cli import parser
from pyiem.util import get_dbconn, noaaport_text

COLS = [
    "resultant_wind_speed",
    "resultant_wind_direction",
    "highest_wind_speed",
    "highest_wind_direction",
    "highest_gust_speed",
    "highest_gust_direction",
    "average_wind_speed",
]


def do(valid):
    """Process."""
    dbconn = get_dbconn("iem")
    cursor = dbconn.cursor()
    cursor2 = dbconn.cursor()
    cursor.execute(
        "select station, product from cli_data WHERE valid = %s "
        "and average_wind_speed is null",
        (valid,),
    )
    for row in cursor:
        uri = f"http://iem.local/api/1/nwstext/{row[1]}"
        req = requests.get(uri)
        if req.status_code != 200:
            print(f"missing {row[1]}")
            continue
        try:
            cli = parser(noaaport_text(req.content.decode("ascii", "ignore")))
        except Exception:
            continue
        if not cli.data:
            continue
        hasdata = False
        vals = []
        for col in COLS:
            val = cli.data[0]["data"].get(col)
            if val is not None:
                hasdata = True
            vals.append(val)
        if not hasdata:
            continue
        print(f"{row[0]} {valid} {vals}")
        cursor2.execute(
            "UPDATE cli_data SET resultant_wind_speed = %s, "
            "resultant_wind_direction = %s, highest_wind_speed = %s, "
            "highest_wind_direction = %s, highest_gust_speed = %s, "
            "highest_gust_direction = %s, average_wind_speed = %s  WHERE "
            "station = %s and valid = %s",
            (*vals, row[0], valid),
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
