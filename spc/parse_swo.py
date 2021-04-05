"""Glean out geometries from ancient SWO text products."""
# stdlib
from datetime import timezone
import math
import re

# third party
from metpy.units import units
import pytz
import pandas as pd
from pyiem.util import get_dbconn

CRCRLF = "\r\r\n"
CENTRAL_TZ = pytz.timezone("America/Chicago")
RIGHT_OF_LINE = re.compile("(RGT|RIGHT|RT) OF A (LN|LINE) (FM|FROM)")
txt2drct = {
    "N": 360,
    "North": 360,
    "NNE": 25,
    "NE": 45,
    "ENE": 70,
    "E": 90,
    "East": 90,
    "ESE": 115,
    "SE": 135,
    "SSE": 155,
    "S": 180,
    "South": 180,
    "SSW": 205,
    "SW": 225,
    "WSW": 250,
    "W": 270,
    "West": 270,
    "WNW": 295,
    "NW": 315,
    "NNW": 335,
}


def load_stations():
    """Load up the tie points according to ancient GEMPAK."""
    mydir = "/home/gempak/GEMPAK7/gempak/tables/stns/"
    rows = []
    entries = []
    for tbl in ["synop.tbl", "inactive.tbl"]:
        for line in open(f"{mydir}/{tbl}"):
            if line.startswith("!") or len(line) < 70 or line[0] == " ":
                continue
            sid = line.split()[0]
            if len(sid) != 3:
                continue
            if sid in entries:
                continue
            entries.append(sid)
            lat = float(line[56:60]) / 100.0
            lon = float(line[61:67]) / 100.0
            rows.append(dict(sid=sid, lat=lat, lon=lon))
    return pd.DataFrame(rows).set_index("sid")


def get_threshold(text):
    """Convert things we need."""
    # Order here matters as some funky things could happen in the text
    if text.find("GEN TSTMS") > -1:
        return "TSTM"
    if text.find("SLGT RISK") > -1:
        return "SLGT"
    if text.find("MDT RISK") > -1:
        return "MDT"
    if text.find("HIGH RISK") > -1:
        return "HIGH"


def compute_loc(lon, lat, dist, bearing):
    """Estimate a lat/lon"""
    meters = (units("mile") * dist).to(units("meter")).m
    northing = meters * math.cos(math.radians(bearing)) / 111111.0
    easting = (
        meters
        * math.sin(math.radians(bearing))
        / math.cos(math.radians(lat))
        / 111111.0
    )
    return lon + easting, lat + northing


def make_point(lon, lat):
    """Make a point."""
    lon = lon * -1
    if lon > 100:
        lon -= 100
    return "%.0f%04.0f" % (
        lat * 100,
        lon * 100,
    )


def compute(stns, text):
    """Turn the text into something or another."""
    tokens = text.split()
    sz = len(tokens)
    i = 0
    pts = []
    while i < sz:
        token = tokens[i]
        if token in ["CONT", "CONTD"]:  # jump!
            pts.append("99999999")
        elif token.isdigit():
            miles = float(token)
            drct = txt2drct[tokens[i + 1]]
            sid = tokens[i + 2]
            row = stns.loc[sid]
            lon, lat = compute_loc(row["lon"], row["lat"], miles, drct)
            pts.append(make_point(lon, lat))
            i += 3
            continue
        else:
            row = stns.loc[token]
            pts.append(make_point(row["lon"], row["lat"]))
        i += 1
    return pts


def process(fh, stns, row):
    """Do work."""
    lines = [x.strip() for x in row[1].replace("\r", "").split("\n")]
    paragraphs = ("\n".join(lines)).split("\n\n")
    thresholds = {}
    take_paragraphs = []
    for paragraph in paragraphs:
        text = (
            paragraph.replace("\n", " ").replace("...", " ").replace("..", " ")
        )
        if text.startswith("VALID "):
            fh.write(
                CRCRLF.join(
                    [
                        f"VALID TIME {text.replace('VALID ', '')}",
                        "",
                        "PROBABILISTIC OUTLOOK POINTS DAY 1",
                        "",
                        "... TORNADO ..." "",
                        "&&",
                        "",
                        "... HAIL ..." "",
                        "&&",
                        "",
                        "... WIND ...",
                        "",
                        "&&",
                        "",
                        "CATEGORICAL OUTLOOK POINTS DAY 1",
                        "",
                        "... CATEGORICAL ...",
                        "",
                    ]
                )
            )
        threshold = get_threshold(text)
        if threshold is None:
            continue
        want = False
        for token in text.split("."):
            s = RIGHT_OF_LINE.search(token)
            if not s:
                continue
            want = True
            pts = compute(stns, token[s.end() :].strip())
            if threshold not in thresholds:
                thresholds[threshold] = pts
            else:
                thresholds[threshold].append("99999999")
                thresholds[threshold].extend(pts)
        if want:
            take_paragraphs.append(paragraph)
    for threshold in thresholds:
        fh.write(f"{threshold:4s}   ")
        for i, pt in enumerate(thresholds[threshold]):
            if i % 6 == 0 and i > 1:
                fh.write("       ")
            fh.write(pt)
            if (i + 1) % 6 == 0 and i > 0:
                fh.write(CRCRLF)
            else:
                fh.write(" ")
        fh.write(CRCRLF)
    fh.write(CRCRLF + "&&" + CRCRLF)
    fh.write((f"{CRCRLF}{CRCRLF}").join(take_paragraphs))
    fh.write(CRCRLF + "\003")


def main():
    """Go Main Go."""
    stns = load_stations()
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT entered at time zone 'UTC', data, pil from products_1996_0106 "
        "WHERE entered > '1996-04-19' and entered < '1996-04-20' "
        "and pil in ('SWODY1', 'SWODY2')"
        "ORDER by entered ASC"
    )
    for row in cursor:
        valid = row[0].replace(tzinfo=timezone.utc)
        localtime = valid.astimezone(CENTRAL_TZ)
        day = row[2][-1]
        pil = f"PTSDY{day}"
        with open(f"{valid.strftime('%Y%m%d%H%M')}_{pil}.txt", "w") as fh:
            fh.write(
                CRCRLF.join(
                    [
                        "\001",
                        "000 ",
                        f"WUUS0{day} KWNS {valid.strftime('%d%H%M')}",
                        pil,
                        "",
                        f"DAY {day} CONVECTIVE OUTLOOK AREAL OUTLINE",
                        "NWS STORM PREDICTION CENTER NORMAN OK",
                        localtime.strftime("%I%M %p %Z %a %b %d %Y").upper(),
                        "",
                    ]
                )
            )
            process(fh, stns, row)


if __name__ == "__main__":
    main()
