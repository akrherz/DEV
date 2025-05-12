"""Process really old files from NCEI.

https://www1.ncdc.noaa.gov/pub/data/documentlibrary/tddoc/td9949.pdf

"""

import datetime
import os
import re
import struct
import sys
from io import BytesIO

from pyiem.database import get_dbconn
from pyiem.util import noaaport_text, utc

# Copied from https://github.com/akrherz/iem
sys.path.insert(0, "/opt/iem/scripts/util")
from poker2afos import XREF_SOURCE  # type: ignore

WMO_RE = re.compile(
    r"^(?P<ttaaii>[A-Z0-9]{4,6})\s+(?P<cccc>[A-Z]{4})\s+"
    r"(?P<ddhhmm>[0-3][0-9][0-2][0-9][0-5][0-9])",
    re.M,
)
WMO_EXT_RE = re.compile(
    r"^:.*?:(?P<ttaaii>[A-Z0-9]{4,6})\s+(?P<cccc>[A-Z]{4})\s+"
    r"(?P<ddhhmm>[0-3][0-9][0-2][0-9][0-5][0-9])",
    re.M,
)
AFOS_RE = re.compile(r"^[A-Z0-9]{7,9}\s*$")


def compute_valid(utcnow, ddhhmm):
    """Figure out the time, sigh."""
    wmo_day = int(ddhhmm[:2])
    wmo_hour = int(ddhhmm[2:4])
    if wmo_hour > 23:
        wmo_hour = 0
    wmo_minute = int(ddhhmm[4:])
    res = utcnow.replace(hour=wmo_hour, minute=wmo_minute)
    if wmo_day == utcnow.day:
        return res
    # Tight leash
    for val in [
        res + datetime.timedelta(days=1),
        res - datetime.timedelta(days=1),
    ]:
        if wmo_day == val.day:
            return val
    return res


def clean_ttaaii(val):
    """Add zeros."""
    return "%s%s%s" % (val[:4], "0" if len(val) == 5 else "", val[4:])


def persist(cursor, record, utcnow):
    """Save to the database!"""
    print("_" * 80)
    print(f"cccnnnxxx {record['cccnnnxxx']}")
    print(record["text"])
    if len(record["text"]) < 20:
        print("LEN OF TEXT FAILED")
        return
    text = record["text"].replace("\x00", "")
    if len(text) < 20:
        print("EMPTY PRODUCT")
        return
    # Check 1 we must match the WMO header
    m = WMO_RE.match(text)
    if not m:
        # Check for the strange prefixed products of :blah:WMO
        if text[0] == ":":
            print("Working around :stuff: in WMO header")
            m = WMO_EXT_RE.match(text)
            if not m:
                print("Double failure")
                print(text)
                return
        else:
            print(
                f"WMO_RE FAILED! {ord(record['text'][0])} "
                f"{ord(record['text'][1])}"
            )
            return
    wmo = m.groupdict()
    # Check 2 we have a good AFOS
    m = AFOS_RE.match(record["cccnnnxxx"])
    if not m:
        print("AFOS_RE FAILED!")
        return
    valid = compute_valid(utcnow, wmo["ddhhmm"])
    ttaaii = clean_ttaaii(wmo["ttaaii"])
    cccc = XREF_SOURCE.get(wmo["cccc"], wmo["cccc"])
    afos = record["cccnnnxxx"][3:].strip()
    if not afos.startswith("ROB"):
        return
    print(f"Insert {valid} {cccc} {ttaaii} {afos}")
    cursor.execute(
        "INSERT into products (data, pil, entered, source, wmo) VALUES "
        "(%s, %s, %s, %s, %s)",
        (
            noaaport_text(text),
            afos,
            valid,
            cccc,
            ttaaii,
        ),
    )


def compute_utcnow(fn):
    """Figure out the timestamp."""
    # 9949dec1989-22
    ffn = os.path.basename(fn)
    valid = datetime.datetime.strptime(ffn, "9949%b%Y-%d")
    return utc(valid.year, valid.month, valid.day)


def main(argv):
    """Go Main Go."""
    fn = argv[1]
    utcnow = compute_utcnow(fn)
    # utcnow = utc(1983, 11, 8)
    dbconn = get_dbconn("afos")
    cursor = dbconn.cursor()
    fd = open(fn, "rb")
    current = {}
    while True:
        record = BytesIO(fd.read(284))
        if len(record.getvalue()) != 284:
            print(f"read() resulted in len: {len(record.getvalue())}")
            break
        # Ignore LTH and LAF
        record.read(29)
        meat = record.read(284 - 29)
        # print([chr(a) for a in meat])
        etx = b"\x83" in meat
        # print(etx)
        # Attempt to compute a CCCNNNXXX, maybe unused for some
        cccnnnxxx = (
            b"".join(struct.unpack("9c", record.getvalue()[35:44]))
        ).decode("ascii", "ignore")

        # Record type A (first of multi-block)
        if not etx and not current:
            print("Found A")
            current = {
                "cccnnnxxx": cccnnnxxx,
                "text": meat[24:].decode("ascii", "ignore"),  # +2 ?
            }
        # Record type B (intermediate)
        elif not etx and current:
            print("Found B")
            current["text"] += meat[3:].decode("ascii", "ignore")
        # Record type C (last block)
        elif etx and current:
            print("Found C")
            current["text"] += meat[2:-1].decode("ascii", "ignore")
            persist(cursor, current, utcnow)
            current = {}
        # Record type D (single block)
        elif etx and not current:
            print("Found D")
            current = {
                "cccnnnxxx": cccnnnxxx,
                "text": meat[22:-1].decode("ascii", "ignore"),  # 0
            }
            persist(cursor, current, utcnow)
            current = {}
        # Record type E (unknown, toss it)
        else:
            print("Found E")
            continue
    cursor.close()
    dbconn.commit()


if __name__ == "__main__":
    main(sys.argv)
