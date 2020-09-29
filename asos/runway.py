"""
 Look at our METAR archives for notations of runway vis length?
"""
import re
from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    ASOS = get_dbconn("asos")
    acursor = ASOS.cursor()

    acursor.execute(
        """
    select valid, metar from alldata where station = 'DSM' and
    metar ~* ' R' ORDER by valid ASC
    """
    )
    for row in acursor:
        tokens = re.findall("R([0-9]+)/([0-9]+)", row[1])
        if not tokens:
            continue
        rr = tokens[0][0]
        dist = float(tokens[0][1])
        if dist < 1201:
            print("%s,%s,%s" % (row[0], rr, dist))


if __name__ == "__main__":
    main()
