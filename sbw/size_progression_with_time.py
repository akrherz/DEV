"""How are the sizes of the polygons changing with time"""
from itertools import cycle

from psycopg2.extras import DictCursor
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from pyiem.util import get_dbconn


def do_year(pgconn, year):
    """Process a year's worth of data"""
    cursor = pgconn.cursor(cursor_factory=DictCursor)
    sbwtable = "sbw_%s" % (year,)
    sums = np.zeros((120), np.float)
    counts = np.zeros((120), np.float)
    cursor.execute(
        f"""
    WITH issuance as (
        SELECT wfo, eventid, polygon_begin, phenomena, significance,
        ST_Area(ST_Transform(geom, 2163)) as area from {sbwtable}
        WHERE status = 'NEW' and phenomena = 'TO' and significance = 'W')

    SELECT i.polygon_begin, s.polygon_begin as s_pb, s.polygon_end as s_pe,
    i.area as i_area, ST_Area(ST_Transform(s.geom, 2163)) as s_area from
    {sbwtable} s JOIN issuance i on (s.wfo = i.wfo and
    s.eventid = i.eventid and s.phenomena = i.phenomena and
    s.significance = i.significance) WHERE status != 'CAN'
    ORDER by s.issue ASC
    """
    )
    for row in cursor:
        idx0 = int((row["s_pb"] - row["polygon_begin"]).total_seconds() / 60.0)
        idx1 = idx0 + int((row["s_pe"] - row["s_pb"]).total_seconds() / 60.0)
        ratio = row["s_area"] / row["i_area"]
        if idx0 < 0 or idx0 > 119 or idx1 > 119 or ratio > 1.1 or ratio < 0:
            print("idx0: %s idx1: %s ratio: %s" % (idx0, idx1, ratio))
            print(row)
            print("----------------------------------------------------")
            continue
        sums[idx0:idx1] += ratio
        counts[idx0:idx1] += 1

    return sums / counts


def main():
    """Go Main Go"""
    lines = ["-", "--", "-.", ":"]
    linecycler = cycle(lines)
    pgconn = get_dbconn("postgis", user="nobody")
    fig = plt.figure(figsize=(12.80, 7.68))
    ax = fig.add_axes([0.06, 0.1, 0.43, 0.8])
    ax2 = fig.add_axes([0.56, 0.1, 0.43, 0.8])
    fig.text(
        0.5,
        0.92,
        (
            "NWS Storm-Based Tornado Warning Size Progression\n"
            "All Warnings Equally Weighted"
        ),
        ha="center",
        fontsize=16,
    )
    ax.set_xlabel("Minutes After Issuance")
    ax.set_ylabel("Polygon Size Relative to Issuance")
    ax.grid(True)
    ax.set_xlim(0, 80)
    ax.set_xticks(range(0, 81, 15))
    ax.set_yticks(np.arange(0, 1.1, 0.1))
    ax.set_ylim(0, 1.1)
    v30 = []
    v45 = []
    for year in tqdm(range(2008, 2018)):
        res = do_year(pgconn, year)
        v30.append(res[30])
        v45.append(res[45])
        ax.plot(
            np.arange(120), res, next(linecycler), label="%s" % (year,), lw=2
        )
    ax.legend(ncol=5)

    ax2.bar(np.arange(2008, 2018) - 0.2, v30, width=0.4, label="@30 Minutes")
    ax2.bar(np.arange(2008, 2018) + 0.2, v45, width=0.4, label="@45 Minutes")
    ax2.grid(True)
    ax2.set_xlabel("Yearly Values for Selected Times")
    ax2.legend()
    ax2.set_yticks(np.arange(0, 1.1, 0.1))
    ax2.set_ylim(*ax.get_ylim())
    fig.text(0.02, 0.01, "@akrherz Iowa Environmental Mesonet 15 Nov 2017")
    fig.savefig("test.png")


if __name__ == "__main__":
    main()
