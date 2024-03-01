"""Tool shared with NWS to flip CCW polygons"""

import re
import sys

from shapely.geometry import Polygon

LAT_LON = re.compile(r"([0-9]{4,8})\s+")

FILENAME = sys.argv[1]


def checker(lon, lat, strdata):
    """make sure our values are within physical bounds"""
    if lat >= 90 or lat <= -90:
        raise Exception(f"invalid latitude {lat} from {strdata}")
    if lon > 180 or lon < -180:
        raise Exception(f"invalid longitude {lon} from {strdata}")
    return (lon, lat)


def str2polygon(strdata):
    """Borrowed from pyiem."""
    pts = []
    partial = None

    # We have two potential formats, one with 4 or 5 places and one
    # with eight!
    vals = re.findall(LAT_LON, strdata)
    for val in vals:
        if len(val) == 8:
            lat = float(val[:4]) / 100.00
            lon = float(val[4:]) / 100.00
            if lon < 40:
                lon += 100.0
            lon = 0 - lon
            pts.append(checker(lon, lat, strdata))
        else:
            s = float(val) / 100.00
            if partial is None:  # we have lat
                partial = s
                continue
            # we have a lon
            if s < 40:
                s += 100.0
            s = 0 - s
            pts.append(checker(s, partial, strdata))
            partial = None

    if len(pts) == 0:
        return None
    if pts[0][0] != pts[-1][0] and pts[0][1] != pts[-1][1]:
        pts.append(pts[0])
    return Polygon(pts)


def main():
    """Go Main Go."""
    for line in open(FILENAME):
        tokens = line.replace("||", "").replace('"', "").split(";")
        if len(tokens) != 2:
            continue
        (nwsli, pairs) = tokens
        pairs = " ".join(pairs.split())
        poly = str2polygon(pairs)
        if poly is None:
            continue
        if poly.exterior.is_ccw:
            tokens = pairs.strip().split()
            grouped = []
            for i in range(0, len(tokens), 2):
                grouped.append("%s %s" % (tokens[i], tokens[i + 1]))
            print(
                ("\nNWSLI: %s should be flipped!\nOLD: %s\nNEW: %s\n")
                % (nwsli, pairs, " ".join(grouped[::-1]))
            )


if __name__ == "__main__":
    main()
