"""Fix sky_coverage field."""

import datetime

import httpx
from pyiem.database import get_dbconn
from pyiem.nws.products.cli import parser
from pyiem.util import noaaport_text

COLS = [
    "snowdepth",
]


def do(valid):
    """Process."""
    dbconn = get_dbconn("iem")
    cursor = dbconn.cursor()
    cursor2 = dbconn.cursor()
    cursor.execute(
        "select station, product from cli_data WHERE valid = %s "
        "and snowdepth is null",
        (valid,),
    )
    for row in cursor:
        uri = f"http://iem.local/api/1/nwstext/{row[1]}"
        try:
            resp = httpx.get(uri, timeout=30)
            resp.raise_for_status()
            cli = parser(noaaport_text(resp.content.decode("ascii", "ignore")))
        except Exception as exp:
            print(f"missing {row[1]} {exp}")
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
            "UPDATE cli_data SET snowdepth = %s WHERE "
            "station = %s and valid = %s",
            (*vals, row[0], valid),
        )

    cursor2.close()
    dbconn.commit()


def main():
    """Go Main."""
    sts = datetime.date(2020, 10, 1)
    ets = datetime.date(2022, 4, 24)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        do(now)
        now += interval


if __name__ == "__main__":
    main()
