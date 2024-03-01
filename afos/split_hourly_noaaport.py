"""Merge in hourly noaaport files found here:

http://idd.ssec.wisc.edu/native/nwstg/text/
"""

from pyiem.nws.products import TextProduct
from pyiem.util import utc


def main():
    """Go Main Go."""
    utcnow = utc(2019, 9, 26, 9)
    data = open("/mesonet/tmp/SURFACE_DDPLUS_20190926_0900.txt", "rb").read()
    with open("parsed.txt", "w") as fp:
        found = 0
        for token in data.decode("ascii", "ignore").split("\003"):
            try:
                tp = TextProduct(token, utcnow=utcnow, parse_segments=False)
            except Exception as exp:
                print(exp)
                continue
            if tp.wmo[:2] not in ["SA", "SP"]:
                continue
            fp.write(token.encode("ascii").decode("ascii", "ignore") + "\003")
            found += 1
        print(found)


if __name__ == "__main__":
    main()
