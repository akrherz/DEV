"""Simple script to get the last product."""
import sys

from pyiem.util import noaaport_text
import requests


def main(argv):
    """Go Main Go."""
    pil = argv[1]
    req = requests.get(
        "https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?"
        f"pil={pil}"
    )
    data = noaaport_text(req.content.decode("ascii", "ignore"))
    with open(f"{pil}.txt", "w") as fh:
        fh.write(data)


if __name__ == "__main__":
    main(sys.argv)
