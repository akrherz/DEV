"""Send products from AFOS database to pyWWA"""

from pyiem.database import get_dbconn
from pyiem.util import noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    acursor = pgconn.cursor("streamer")

    acursor.execute(
        """
        SELECT pil, entered at time zone 'UTC', data
        from products
        WHERE source = 'TJSJ' and entered >= '2017-08-26'
        and entered < '2017-09-13'
    """
    )
    for row in acursor:
        with open(f"TJSJ/{row[0].strip()}_{row[1]:%Y%m%d%H%M}.txt", "a") as fp:
            fp.write(noaaport_text(row[2]))


if __name__ == "__main__":
    main()
