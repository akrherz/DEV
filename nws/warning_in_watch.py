"""
with warns as (
    select ugc, issue, expire from warnings
    where phenomena = 'TO' and significance ='W' and issue > '2005-10-01'),
watch as (
    select ugc, phenomena, issue, expire from warnings where
    phenomena in ('SV', 'TO') and significance = 'A'),
agg as (
    SELECT w.ugc, w.issue as w_issue, w.expire, a.ugc as a_ugc,
    a.phenomena,
    a.issue, a.expire from warns w LEFT JOIN watch a on (w.ugc = a.ugc
    and w.issue < a.expire and w.expire > a.issue))

 SELECT count(*), sum(case when phenomena = 'TO' then 1 else 0 end) as tor,
 sum(case when phenomena = 'SV' then 1 else 0 end) as svr,
 sum(case when phenomena is null then 1 else 0 end) as no from agg

 agg2 as (SELECT extract(week from w_issue) as week, count(*),
 sum(case when a_ugc is not null then 1 else 0 end) from agg GROUP by week)
  select week, sum / count::float * 100 from agg2 ORDER by week;

"""

import calendar
from io import StringIO

import pandas as pd
from pyiem.plot import figure_axes


def main():
    """Go Main."""
    tor_data = """1 | 81.52149448570786
     2 | 88.65795724465558
     3 | 89.48130976528542
     4 | 90.17969076473047
     5 |  84.2581554134605
     6 | 78.24982132930994
     7 | 68.69737493808816
     8 |  65.5941794664511
     9 | 71.06366755623333
    10 | 74.43887961417177
    11 | 83.61111111111111
    12 | 83.34429103659873"""

    svr_data = """1 |  74.14081606384349
     2 |   71.6718031627343
     3 |    70.499131351383
     4 |  72.84464647236334
     5 |  63.68342214798908
     6 |  57.50500891927663
     7 |  44.36958483448337
     8 |    37.786470641473
     9 | 40.992843860934244
    10 | 60.481415043177165
    11 |  66.83096315449257
    12 |  69.15300964925716"""

    sio = StringIO()
    sio.write(tor_data)
    sio.seek(0)
    tor = pd.read_csv(sio, sep="|", names=["month", "freq"]).set_index("month")
    sio = StringIO()
    sio.write(svr_data)
    sio.seek(0)
    svr = pd.read_csv(sio, sep="|", names=["month", "freq"]).set_index("month")

    (fig, ax) = figure_axes(
        title=(
            "Percentage of NWS County Warnings Issued "
            "Within a SPC Convective Watch"
        ),
        subtitle="Oct 2005 - 9 May 2023, based on unofficial IEM archives.",
        figsize=(10.24, 7.68),
    )

    ax.bar(
        svr.index - 0.4,
        svr["freq"],
        align="edge",
        width=0.4,
        fc="#fec44f",
        label="Severe TStorm Warning (57.0%)",
    )
    ax.bar(
        tor.index,
        tor["freq"],
        align="edge",
        width=0.4,
        fc="red",
        label="Tornado Warning (81.9%)",
    )
    for i in range(1, 13):
        val = svr.at[i, "freq"]
        ax.text(i - 0.01, val + 2, f"{val:.0f}%", ha="right")
        val = tor.at[i, "freq"]
        ax.text(i + 0.2, val + 2, f"{val:.0f}%", ha="center")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.legend(loc=(0.4, 0.95), ncol=2)

    fig.savefig("230510.png")


if __name__ == "__main__":
    main()
