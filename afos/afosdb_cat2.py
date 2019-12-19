"""Send products from AFOS database to pyWWA."""

from pyiem.util import get_dbconn, noaaport_text


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor("streamer")

    cursor.execute(
        """
        SELECT data, entered at time zone 'UTC', pil from products
        WHERE pil in ('PFMBIS', 'PFMARX', 'PFMMPX', 'PFMDLH', 'PFMFGF')
        and entered > '2016-01-01 00:00+00'
    """
    )
    for _i, row in enumerate(cursor):
        with open(
            "PFM/%s/%s_%s.txt"
            % (row[1].year, row[2], row[1].strftime("%Y%m%d%H%M")),
            "a",
        ) as fh:
            fh.write(noaaport_text(row[0]))


if __name__ == "__main__":
    main()
