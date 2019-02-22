"""Request for maps and data of products without SVS updates."""

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.plot.geoplot import MapPlot


def main():
    """Go Main Go."""
    dbconn = get_dbconn("postgis")
    df = read_sql("""
    WITH data as (
        SELECT wfo, eventid, extract(year from issue) as year,
        max(case when svs is not null then 1 else 0 end) as hit from
        warnings where product_issue > '2014-04-01' and
        product_issue < '2019-02-22' and phenomena = 'FF'
        and significance = 'W' GROUP by wfo, eventid, year
    )
    SELECT wfo, sum(hit) as got_update, count(*) as total_events from data
    GROUP by wfo ORDER by total_events DESC
    """, dbconn, index_col='wfo')
    if 'JSJ' in df.index and 'SJU' not in df.index:
        df.loc['SJU'] = df.loc['JSJ']

    df['no_update_percent'] = (
        100. - df['got_update'] / df['total_events'] * 100.
    )
    df.to_csv("140401_190221_ffw_nofls.csv")

    # NOTE: FFW followup is FFS
    mp = MapPlot(
        sector='nws',
        title='Percentage of Flash Flood Warnings without a FFS Update Issued',
        subtitle='1 April 2014 - 21 February 2019, based on unofficial data'
    )
    cmap = plt.get_cmap("copper_r")
    cmap.set_under('white')
    cmap.set_over('black')
    ramp = range(0, 101, 5)
    mp.fill_cwas(
        df['no_update_percent'], bins=ramp, cmap=cmap, units='%', ilabel=True,
        lblformat='%.1f'
    )
    mp.postprocess(filename='140401_190221_ffw_nosvs.png')


if __name__ == '__main__':
    main()
