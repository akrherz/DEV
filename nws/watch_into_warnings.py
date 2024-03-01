"""Conversion of Watches into Warnings"""

import datetime

from tqdm import tqdm

from pyiem.nws.vtec import VTEC_PHENOMENA
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()

    phenomena = "SV"
    startdate = datetime.date(2005, 10, 1)
    enddate = datetime.date(2020, 2, 19)

    cursor.execute(
        """
    SELECT ugc, issue, init_expire, wfo from warnings where phenomena = %s and
    significance = 'A' and issue > %s and issue < %s
    ORDER by issue ASC
    """,
        (phenomena, startdate, enddate),
    )
    total = cursor.rowcount
    print("Events is %s" % (total,))

    hits = {}
    hits2 = {}
    totals = {}
    misses = 0
    for row in tqdm(cursor, total=total):
        wfo = row[3]
        if wfo not in hits:
            hits[wfo] = {}
        if wfo not in totals:
            totals[wfo] = 0
        totals[wfo] += 1
        cursor2.execute(
            """
        SELECT distinct phenomena, significance from warnings
        where ugc = %s and expire > %s and issue < %s and wfo = %s
        """,
            (row[0], row[1], row[2], wfo),
        )
        for row2 in cursor2:
            key = "%s.%s" % (row2[0], row2[1])
            if key not in hits[wfo]:
                hits[wfo][key] = 0
            hits[wfo][key] += 1
            if key not in hits2:
                hits2[key] = 0
            hits2[key] += 1
        if cursor2.rowcount == 0:
            misses += 1

    data = {}
    for wfo in hits:
        data[wfo] = (
            hits[wfo].get("%s.W" % (phenomena,), 0)
            / float(totals[wfo])
            * 100.0
        )

    mp = MapPlot(
        sector="nws",
        axisbg="white",
        title=(
            "Conversion [%%] of %s Watch Counties/Parishes into %s Warnings"
        )
        % (VTEC_PHENOMENA[phenomena], VTEC_PHENOMENA[phenomena]),
        titlefontsize=14,
        subtitle=("%s - %s, Overall %s/%s %.1f%%")
        % (
            startdate.strftime("%-d %b %Y"),
            enddate.strftime("%-d %b %Y"),
            hits2["%s.W" % (phenomena,)],
            total,
            hits2["%s.W" % (phenomena,)] / float(total) * 100.0,
        ),
    )
    mp.fill_cwas(data, ilabel=True, lblformat="%.0f", extend="neither")
    mp.postprocess(filename="test.png")

    print("Misses %s %.1f%%" % (misses, misses / float(total) * 100.0))
    for key in hits2:
        print(
            "%s %s %.1f%%"
            % (key, hits2[key], hits2[key] / float(total) * 100.0)
        )


if __name__ == "__main__":
    main()
