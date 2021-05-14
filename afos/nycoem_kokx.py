"""Dump products."""
import os

from pyiem.util import get_dbconn

PILS = (
    "MWW|FWW|CFW|TCV|RFW|FFA|SVR|TOR|SVS|SMW|MWS|NPW|WCN|WSW|EWW|FLS|"
    "FLW|FFW|FFS|HLS|TSU|DSW|SQW"
)


def main():
    """Go Main Go."""
    pgconn = get_dbconn("afos")
    acursor = pgconn.cursor("streamer")

    acursor.execute(
        """
        SELECT pil, entered at time zone 'UTC', source, data from products
        WHERE source = 'KOKX' and
        substr(pil, 1, 3) in %s
        and entered between '2017-06-10' and '2018-08-06'
    """,
        (tuple(PILS.split("|")),),
    )
    for row in acursor:
        mydir = "KOKX/%s" % (row[0],)
        if not os.path.isdir(mydir):
            os.makedirs(mydir)
        with open(
            "%s/%s_%s_%s.txt"
            % (mydir, row[1].strftime("%Y%m%d%H%M"), row[2], row[0]),
            "a",
        ) as fh:
            fh.write(row[3])
            fh.write("\r\r\n\003")


if __name__ == "__main__":
    main()
