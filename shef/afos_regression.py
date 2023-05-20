"""Feed some AFOS data through for regression testing."""
import re

from pyiem.util import get_dbconn, logger

LOG = logger()

NWSLI_RE = re.compile("^[A-Z]{4}[0-9]")


def main():
    """Go Main."""
    cursor = get_dbconn("afos").cursor()
    cursor.execute(
        """
        SELECT data, source, pil from products where entered > '2023-05-16'
        and substr(pil, 1, 3) = 'RTP'
        and extract(hour from entered) between 3 and 12
        ORDER by entered
        """,
    )
    for row in cursor:
        has_dh = None
        for line in row[0].replace("\r", "").split("\n"):
            if line.startswith(".B"):
                has_dh = line.find(" DH") > -1
            if line.startswith(".END"):
                has_dh = None
            if has_dh is not None:
                if NWSLI_RE.match(line) and line.find("DH") == -1:
                    print(row[1], row[2])
                    has_dh = None


if __name__ == "__main__":
    main()
