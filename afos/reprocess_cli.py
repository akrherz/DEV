"""Process CLI."""

from datetime import date

from psycopg2.extras import DictCursor

from pyiem.network import Table as NetworkTable
from pyiem.nws.products import cli
from pyiem.util import get_dbconn, logger

LOG = logger()
FLOOR = date(1999, 12, 15)
CEILING = date(2001, 1, 2)
NT = NetworkTable("NWSCLI", only_online=False)
cli.HARDCODED.update(
    {
        "KANSAS CITY INTERNATIONAL": "KMCI",
        "ORANGEBURG AIRPORT": "KOGB",
        "SCOTTSBLUFF AIRPORT": "KBFF",
        "CHEYENNE": "KCYS",
        "KEARNEY": "KEAR",
        "MINOT": "KMOT",
        "LANDER": "KLND",
        "TWIN CITIES": "KMSP",
        "RAPID CITY AIRPORT": "KUNR",
        "BALTIMORE": "KBWI",
        "TRAVERSE CITY": "KTVC",
        "COLUMBIA METRO AIRPORT": "KCAE",
        "AUGUSTA REGIONAL BUSH FIELD": "KAGS",
        "KEY WEST": "KEYW",
        "TOPEKA": "KTOP",
        "OMAHA EPPLEY": "KOMA",
        "MONTROSE": "KMTJ",
        "DAVENPORT": "KDVN",
        "LITTLE ROCK ADAMS FIELD": "KLIT",
        "ALLIANCE AIRPORT": "KAIA",
        "LARAMIE AIRPORT": "KLAR",
        "CHANHASSEN": "KMPX",
        "COLUMBIA OWENS FIELD": "KCUB",
        "OMAHA VALLEY": "KOAX",
        "DURANGO": "KDRO",
    }
)


def main():
    """Go Main Go."""
    dbconn = get_dbconn("iem")
    cursor = dbconn.cursor(cursor_factory=DictCursor)
    counter = 0
    for text in open("CLI.txt", "rb").read().split(b"\003"):
        try:
            prod = cli.parser(text.decode("ascii"), nwsli_provider=NT.sts)
            if not prod.data:
                continue
        except Exception as exp:
            LOG.exception(exp)
            continue
        # Double check
        bad = False
        for entry in prod.data:
            if entry["cli_valid"] < FLOOR or entry["cli_valid"] > CEILING:
                print(f"Invalid valid {entry['cli_valid']}")
                bad = True
        if not bad:
            counter += 1
            try:
                prod.sql(cursor)
            except Exception as exp:
                print(prod.get_product_id())
                raise Exception() from exp
            if counter % 100 == 0:
                cursor.close()
                dbconn.commit()
                cursor = dbconn.cursor(cursor_factory=DictCursor)
    print(cli.UNKNOWN)
    cursor.close()
    dbconn.commit()


if __name__ == "__main__":
    main()
