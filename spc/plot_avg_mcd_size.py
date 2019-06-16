"""Plot of Average MCD Size."""

from pyiem.plot.use_agg import plt
from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn('postgis')
    df = read_sql("""
       select extract(year from issue)::int as year,
       avg(ST_Area(geom::geography))
       from text_products where pil = 'SWOMCD'
       and issue > '2003-01-01' GROUP by year ORDER by year
    """, pgconn)
    df['norm'] = df['avg'] / df['avg'].max() * 100.
    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df['year'].values, df['norm'].values)
    for _, row in df.iterrows():
        ax.text(
            row['year'], row['norm'] + 1, "%.0f%%" % (row['norm'], ),
            ha='center')
    ax.set_ylabel("Normalized MCD Size Relative to 2005 Max [%]")
    ax.set_title(
        ("Storm Prediction Center :: Mesoscale Discussion Area Size\n"
         "Relative to year 2005 maximum of 86,000 sq km"))
    ax.grid(True)
    ax.set_ylim(60, 104)
    ax.set_yticks(range(60, 101, 5))
    ax.set_xticks(range(2004, 2020, 4))
    ax.set_xlim(2002.2, 2019.7)
    ax.set_xlabel(
        "@akrherz, based on unofficial IEM archives, 2019 data to 15 June")
    fig.savefig('test.png')


if __name__ == '__main__':
    main()
