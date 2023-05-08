"""Review ACIS threads_dict.json"""
import sys

import requests

from pyiem.reference import ncei_state_codes
from pyiem.util import get_dbconn

code2state = dict((v, k) for k, v in ncei_state_codes.items())
URL = "https://threadex.rcc-acis.org/data/threads_dict.json"


def main(argv):
    """Go Main Go."""
    lookfor = argv[1]
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    req = requests.get(URL, timeout=60)
    data = req.json()
    for sid in data:
        if sid != lookfor:
            continue
        cursor.execute(
            "SELECT id, state from stations where network ~* 'CLIMATE' and "
            "substr(id, 4, 3) = %s",
            (sid,),
        )
        if cursor.rowcount == 0:
            print(f"sid: {sid} is unknown by threading id")
        for entry in data[sid]:
            print(entry)


if __name__ == "__main__":
    main(sys.argv)
