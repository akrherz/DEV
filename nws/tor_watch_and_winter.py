"""
with data as (select distinct substr(ugc, 1, 2) as state,
  generate_series(issue, expire, '1 minute'::interval) as ts from warnings
  where phenomena = 'TO' and significance = 'A' and
  (expire - issue) < '1 days'::interval),
data2 as (select distinct substr(ugc, 1, 2) as state,
  generate_series(issue, expire, '1 minute'::interval) as ts from warnings
  where phenomena in('BZ', 'WS') and significance = 'W' and
  (expire - issue) < '3 days'::interval),
data3 as (SELECT o.state, o.ts from data2 o JOIN data t on (o.state = t.state
  and o.ts = t.ts))
select distinct state, date(ts) from data3 ORDER by date ASC;
"""

from io import StringIO

import pandas as pd
from pyiem.plot import MapPlot
from pyiem.plot.use_agg import plt

txt = """ MI    | 2005-11-15
 KS    | 2005-11-27
 MI    | 2006-02-16
 WI    | 2006-03-12
 MI    | 2006-03-12
 IA    | 2006-03-12
 MI    | 2006-03-13
 WI    | 2006-03-13
 IA    | 2006-03-13
 TX    | 2006-03-20
 OK    | 2006-11-29
 AR    | 2006-11-29
 TX    | 2006-11-29
 TX    | 2006-11-30
 IN    | 2006-12-01
 TX    | 2006-12-29
 OK    | 2006-12-29
 TX    | 2006-12-30
 GA    | 2007-02-01
 KS    | 2007-02-24
 MO    | 2007-03-01
 CO    | 2007-03-28
 TX    | 2007-04-13
 TX    | 2007-04-14
 NC    | 2007-04-15
 CO    | 2007-04-24
 CO    | 2007-05-04
 CO    | 2007-05-05
 IL    | 2008-01-29
 IN    | 2008-01-29
 MO    | 2008-01-29
 IL    | 2008-02-05
 MO    | 2008-02-05
 AR    | 2008-03-03
 TX    | 2008-03-06
 VA    | 2008-03-08
 MI    | 2008-04-11
 SD    | 2008-05-01
 CO    | 2008-05-22
 WY    | 2008-05-22
 CO    | 2008-05-23
 MO    | 2008-12-27
 KS    | 2008-12-27
 SD    | 2009-03-23
 NE    | 2009-03-23
 TX    | 2009-03-26
 OK    | 2009-03-27
 TX    | 2009-03-27
 IL    | 2009-03-28
 VA    | 2009-12-09
 TX    | 2009-12-23
 OK    | 2009-12-23
 OK    | 2009-12-24
 AR    | 2009-12-24
 TX    | 2009-12-24
 AZ    | 2010-01-21
 CA    | 2010-01-21
 AZ    | 2010-01-22
 TX    | 2010-01-28
 NC    | 2010-02-05
 CO    | 2010-04-22
 MO    | 2011-02-24
 PA    | 2011-03-23
 CO    | 2011-05-11
 CO    | 2011-10-07
 CO    | 2011-10-08
 KS    | 2011-11-07
 KS    | 2011-11-08
 IL    | 2012-03-02
 KS    | 2012-12-19
 MO    | 2012-12-19
 MO    | 2012-12-20
 TX    | 2012-12-25
 MO    | 2013-01-29
 IL    | 2013-01-30
 MO    | 2013-01-30
 TX    | 2013-02-21
 TX    | 2013-02-25
 NE    | 2013-10-04
 SD    | 2013-10-04
 NC    | 2013-11-26
 NC    | 2013-11-27
 NE    | 2014-05-08
 MT    | 2014-06-17
 GA    | 2015-02-25
 MI    | 2015-04-09
 CO    | 2015-04-17
 CO    | 2015-04-18
 CO    | 2015-05-09
 NE    | 2015-05-09
 SD    | 2015-05-10
 NE    | 2015-05-10
 CO    | 2015-05-15
 NE    | 2015-11-11
 KS    | 2015-11-11
 CO    | 2015-11-16
 NM    | 2015-11-16
 TX    | 2015-12-26
 OK    | 2015-12-26
 TX    | 2015-12-27
 GA    | 2016-01-22
 NE    | 2016-03-23
 IA    | 2016-03-23
 KS    | 2016-03-23"""


def main():
    """Go Main Go."""
    df = pd.read_csv(StringIO(txt.replace(" ", "")), sep="|")
    df.columns = ["states", "date"]
    df2 = df.groupby("states").count()
    data = {}
    for i, row in df2.iterrows():
        data[i] = row["date"]

    mp = MapPlot(
        sector="conus",
        title="Days with Tornado *Watch* & Winter Storm or Blizzard Warning",
        subtitle=(
            "1 Oct 2005 - 24 Mar 2016 :: # of Dates with both alerts "
            "active within the same state at the same time"
        ),
        axisbg="white",
    )

    cmap = plt.get_cmap("jet")
    cmap.set_over("black")
    cmap.set_under("white")
    mp.fill_states(
        data,
        bins=[0, 1, 2, 3, 4, 5, 6, 7, 10, 15, 20],
        units="count",
        ilabel=True,
        cmap=cmap,
    )

    mp.postprocess(filename="states.png")


if __name__ == "__main__":
    main()
