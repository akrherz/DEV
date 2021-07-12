"""Glean out PTS style points from ancient SWO text products."""
# stdlib
from datetime import timezone
import math
import re
import sys

# third party
from metpy.units import units
import pytz
import pandas as pd
from pyiem.util import get_dbconn, utc

VERSION = "2021JUL08"
CRCRLF = "\r\r\n"
CENTRAL_TZ = pytz.timezone("America/Chicago")
RIGHT_OF_LINE = re.compile(r"(RGT|RIGHT|RT) OF A?\s?(LN|LINE) (FM|FROM)")
VALID_TIME = re.compile(r"^VALID (TIME)?\s*([0-9]{6})Z?\s-\s([0-9]{6})", re.M)
STS = utc(1987, 1, 1)
ETS = utc(2002, 3, 26)
txt2drct = {
    "U": 360,
    "M": 360,
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
    "DW": 225,
    "WSW": 250,
    "W": 270,
    "West": 270,
    "WNW": 295,
    "NW": 315,
    "NWN": 335,
    "NNW": 335,
}
UNKNOWN = {}


def load_stations():
    """Load up the tie points according to ancient GEMPAK."""
    # Personal correspondance, Andy Dean
    rows = []
    entries = []
    for line in open("SPCstn.txt"):
        tokens = line.split()
        sid = tokens[0]
        if sid in entries:
            continue
        entries.append(sid)
        rows.append(
            {
                "sid": sid,
                "lat": float(tokens[1]) / 100.0,
                "lon": 0 - float(tokens[2]) / 100.0,
            }
        )
    # Be so careful of order and synop tbl has naughty entries
    mydir = "/home/gempak/GEMPAK7/gempak/tables/stns/"
    for tbl in ["spcwatch", "synop", "inactive", "pirep_navaids", "vors"]:
        for line in open(f"{mydir}/{tbl}.tbl"):
            if line.startswith("!") or len(line) < 70 or line[0] == " ":
                continue
            sid = line.split()[0]
            if len(sid) != 3 or line[52:54] != "US":
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
    # text.find("TSTMS MAY APCH SVR LIMITS") > -1  is NOT TSTM!
    if text.find("GEN TSTM") > -1 or text.find("GNL TSTM") > -1:
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
    if lon >= 100:
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
        if token in ["CONT", "CONTD", "CONTG", "COTND"]:  # jump!
            pts.append("99999999")
        elif token.isdigit() and (i + 2) < sz:
            miles = float(token)
            drct = txt2drct.get(tokens[i + 1])
            if drct is None:
                print(tokens[i + 1])
                print(text)
                print(tokens)
                sys.exit()
            sid = tokens[i + 2]
            if sid in stns.index:
                row = stns.loc[sid]
                lon, lat = compute_loc(row["lon"], row["lat"], miles, drct)
                pts.append(make_point(lon, lat))
            else:
                UNKNOWN.setdefault(sid, 0)
                UNKNOWN[sid] += 1
            i += 3
            continue
        else:
            if token in stns.index:
                row = stns.loc[token]
                pts.append(make_point(row["lon"], row["lat"]))
            else:
                UNKNOWN.setdefault(token, 0)
                UNKNOWN[token] += 1
        i += 1
    return pts


def process(fh, stns, row):
    """Do work."""
    lines = [
        x.strip()
        for x in (
            row[1]
            .replace("\r", "")
            .replace("\003", "")
            .replace("\n.\n", "\n\n")
            .split("\n")
        )
    ]
    text = "\n".join(lines)
    if text.find("\n\nVALID") == -1:
        text = text.replace("\nVALID", "\n\nVALID")
    paragraphs = text.split("\n\n")
    thresholds = {}
    take_paragraphs = []
    found_valid = False
    for paragraph in paragraphs:
        text = (
            paragraph.replace("\n", " ")
            .replace("...", " ")
            .replace("..", " ")
            .replace(".", " ")
            .replace("AND TO ", ". TO ")
            .replace("ALSO TO ", ". TO ")
            .replace('"', "")
            .strip()
        )
        tokens = VALID_TIME.findall(text)
        if tokens:
            if found_valid:
                print(row[1])
                print("Aborting with double valid?")
                sys.exit()
            _, stime, etime = tokens[0]
            found_valid = True
            # Fix missing Z in the first timestamp.
            fh.write(
                CRCRLF.join(
                    [
                        f"VALID TIME {stime}Z - {etime}Z",
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
                        "",
                    ]
                )
            )
            continue
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
            if len(pts) < 2:
                continue
            if threshold not in thresholds:
                thresholds[threshold] = pts
            else:
                if thresholds[threshold][-1] != "99999999":
                    thresholds[threshold].append("99999999")
                thresholds[threshold].extend(pts)
        if want:
            take_paragraphs.append(paragraph.replace("\n", CRCRLF))
    if not found_valid:
        print("Failed to find VALID LINE.")
        print(paragraphs)
        sys.exit()
    for threshold in thresholds:
        fh.write(f"{threshold:4s}   ")
        sz = len(thresholds[threshold])
        for i, pt in enumerate(thresholds[threshold]):
            if i % 6 == 0 and i > 1:
                fh.write(f"{CRCRLF}       ")
            fh.write(pt)
            if (i + 1) != sz:
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
        "SELECT entered at time zone 'UTC', data, pil from products "
        "WHERE entered > %s and entered < %s "
        "and pil in ('SWODY1', 'SWODY2') "
        "ORDER by entered ASC",
        (STS, ETS),
    )
    for row in cursor:
        valid = row[0].replace(tzinfo=timezone.utc)
        print(valid)
        localtime = valid.astimezone(CENTRAL_TZ)
        day = row[2][-1]
        pil = f"PTSDY{day}"
        with open(f"PTS/{valid.strftime('%Y%m%d%H%M')}_{pil}.txt", "w") as fh:
            fh.write(
                CRCRLF.join(
                    [
                        "\001",
                        "000 ",
                        f"WUUS0{day} KWNS {valid.strftime('%d%H%M')}",
                        pil,
                        "",
                        f"DAY {day} CONVECTIVE OUTLOOK AREAL OUTLINE",
                        f"IOWA MESONET SYNTHETIC PRODUCT FROM SWO V{VERSION}",
                        localtime.strftime("%I%M %p %Z %a %b %d %Y").upper(),
                        "",
                        "",
                    ]
                )
            )
            process(fh, stns, row)


if __name__ == "__main__":
    main()
    print(UNKNOWN)
