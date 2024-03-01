"""Fancy bar plot for feature fun
with outlooks as (
    select issue, threshold, expire, geom from spc_outlooks where
    outlook_type = 'C' and day = 1
    and extract(hour from valid at time zone 'UTC') in (19, 20)
    and category = 'TORNADO' and st_isvalid(geom)
    and expire > '2007-01-01'),

warns as (
    select st_union(s.geom), o.expire
    from sbw s JOIN outlooks o on
    (st_overlaps(s.geom, o.geom) and s.issue > o.issue
    and s.issue < o.expire)
    WHERE st_isvalid(s.geom) and s.issue > '2007-01-01' and
    s.status = 'NEW' and s.phenomena = 'TO' and s.significance = 'W'
    GROUP by o.expire),

agg as (
    select o.expire, threshold,
    coalesce(st_area(st_intersection(o.geom, w.st_union)), 0) as inter_area,
    st_area(o.geom) as outlook_area
    from outlooks o LEFT JOIN warns w on (o.expire = w.expire)),

agg2 as (
    select expire, threshold, inter_area / outlook_area * 100. as ratio
    from agg)

select threshold, max(expire), avg(ratio) from agg2
GROUP by threshold ORDER by threshold;

"""

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

DATA = """
 0.02      | 2017-05-19 07:00:00-05 | 0.48018663597178
 0.05      | 2017-05-19 07:00:00-05 | 1.20424012445923
 0.10      | 2017-05-19 07:00:00-05 | 4.04134433281224
 0.15      | 2017-05-19 07:00:00-05 | 5.58442034173105
 0.30      | 2017-05-19 07:00:00-05 | 13.5212030092903
 SIGN      | 2017-05-19 07:00:00-05 | 4.66745197924032
"""
DATA16 = """
 0.02      | 2017-05-19 07:00:00-05 | 0.470031808403787
 0.05      | 2017-05-19 07:00:00-05 |  1.21029277085968
 0.10      | 2017-05-19 07:00:00-05 |  4.04898780771454
 0.15      | 2017-05-19 07:00:00-05 |   5.8938836526862
 0.30      | 2017-05-19 07:00:00-05 |  13.2446672333714
 SIGN      | 2017-05-19 07:00:00-05 |  5.13977284907456
"""
DATA20 = """
 0.02      | 2017-05-19 07:00:00-05 | 0.450738981164547
 0.05      | 2017-05-19 07:00:00-05 |  1.15658587054413
 0.10      | 2017-05-19 07:00:00-05 |  4.01400165216431
 0.15      | 2017-05-19 07:00:00-05 |  4.95264602817491
 0.30      | 2017-05-19 07:00:00-05 |  11.3421031303162
 SIGN      | 2017-05-19 07:00:00-05 |   4.9353610793895
"""

FONT = FontProperties()
FONT.set_weight("bold")


def gett(data):
    """Get"""
    labels = []
    vals = []
    for line in data.split("\n"):
        tokens = line.strip().split("|")
        if len(tokens) != 3:
            continue
        labels.append(tokens[0].strip())
        vals.append(float(tokens[2]))
    return labels, vals


def main():
    """Go"""
    labels, vals = gett(DATA)
    _labels16, vals16 = gett(DATA16)
    _labels20, vals20 = gett(DATA20)
    plt.style.use("ggplot")
    ax = plt.axes([0.15, 0.11, 0.8, 0.76])
    plt.gcf().set_size_inches(8, 6)
    ax.bar(
        np.arange(len(vals)) - 0.25,
        vals,
        width=0.25,
        align="center",
        label="12 UTC",
    )
    ax.bar(
        np.arange(len(vals16)),
        vals16,
        width=0.25,
        align="center",
        label="16 UTC",
    )
    ax.bar(
        np.arange(len(vals20)) + 0.25,
        vals20,
        width=0.25,
        align="center",
        label="20 UTC",
    )
    for x, y in enumerate(vals):
        ax.text(
            x - 0.3,
            y + 0.1,
            "%.1f%%" % (y,),
            va="bottom",
            ha="center",
            color="k",
            fontproperties=FONT,
            rotation=45,
        )
    for x, y in enumerate(vals16):
        ax.text(
            x,
            y + 0.1,
            "%.1f%%" % (y,),
            va="bottom",
            ha="center",
            color="k",
            fontproperties=FONT,
            rotation=45,
        )
    for x, y in enumerate(vals20):
        ax.text(
            x + 0.3,
            y + 0.1,
            "%.1f%%" % (y,),
            va="bottom",
            ha="center",
            color="k",
            fontproperties=FONT,
            rotation=45,
        )
    ax.set_ylim(0, 15)
    # ax.set_xticks(range(0, 101, 25))
    ax.legend(loc=2, ncol=3)
    plt.gcf().text(
        0.5,
        0.93,
        (
            "NWS Storm Prediction Center 2007-2017\n"
            "Percentage of Tornado Day 1 Outlook Area receiving "
            "1+ Tor Warn Polygon\n"
            "Daily events are weighted equally while averaging"
        ),
        fontsize=14,
        ha="center",
        va="center",
    )
    plt.gcf().text(
        0.5,
        0.01,
        "* based on unofficial archives maintained by the IEM, 18 May 2017",
        ha="center",
    )
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels)
    ax.set_xlabel("Tornado Outlook Threshold")
    ax.set_ylabel("Average Areal Coverage by Tor Warn [%]")
    plt.gcf().savefig("test.png")


if __name__ == "__main__":
    main()
