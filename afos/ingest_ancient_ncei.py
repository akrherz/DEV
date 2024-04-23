"""Process really old files from NCEI."""

import datetime
import re
import string

from poker2afos import XREF_SOURCE  # noqa

from pyiem.database import get_dbconn
from pyiem.util import noaaport_text, utc

WMO_RE = re.compile(
    "^(?P<ttaaii>[A-Z0-9]{4,6})\s+(?P<cccc>[A-Z]{4})\s+"
    r"(?P<ddhhmm>[0-3][0-9][0-2][0-9][0-5][0-9])",
    re.M,
)


def compute_valid(utcnow, ddhhmm):
    """Figure out the time, sigh."""
    wmo_day = int(ddhhmm[:2])
    wmo_hour = int(ddhhmm[2:4])
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


def main():
    """Go Main Go."""
    content = open("/mesonet/tmp/ncei/9949dec1989-28", "rb").read()
    utcnow = utc(1989, 12, 28)
    dbconn = get_dbconn("afos")
    cursor = dbconn.cursor()
    hits = 0
    for token in content.split(b"\xb0"):
        pos = token.find(b"\x80")
        if pos == -1:
            continue
        pos2 = token.find(b"\x1f")
        if pos2 == -1 or pos2 > 10:
            continue
        afos = token[3:pos2].decode("ascii", "ignore").strip()
        if len(afos) < 4:
            continue
        m = WMO_RE.match(token[pos + 1 : pos + 20].decode("ascii", "ignore"))
        if not m:
            continue
        wmo = m.groupdict()
        cccc = XREF_SOURCE.get(wmo["cccc"], wmo["cccc"])
        ttaaii = clean_ttaaii(wmo["ttaaii"])
        valid = compute_valid(utcnow, wmo["ddhhmm"])
        product = noaaport_text(
            "".join(
                filter(
                    lambda x: x in string.printable,
                    token[pos + 1 :].decode("utf-8", "ignore"),
                )
            )
        )
        print(f"afos: {afos} ttaaii: {ttaaii} source: {cccc} valid: {valid}")
        cursor.execute(
            "INSERT into products (data, pil, entered, source, wmo) VALUES "
            "(%s, %s, %s, %s, %s)",
            (
                product.replace("\0", ""),
                afos.replace("\0", ""),
                valid,
                cccc,
                ttaaii,
            ),
        )
        hits += 1
    print(f"Got {hits} products")
    cursor.close()
    dbconn.commit()


if __name__ == "__main__":
    main()
