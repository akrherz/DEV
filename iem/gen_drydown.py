"""Generate an example JSON to iterate on."""
import json

from pyiem.util import get_dbconn
from pandas.io.sql import read_sql


def main():
    """Go Main Go."""
    pgconn = get_dbconn('iem')
    df = read_sql("""
        SELECT day, max_tmpf, min_tmpf, avg_rh from
        summary s JOIN stations t ON (s.iemid = t.iemid) WHERE
        t.id = 'DSM' and t.network = 'IA_ASOS' and
        day > '1980-01-01' and
        to_char(day, 'mmdd') between '0901' and '1101'
        ORDER by day ASC
    """, pgconn, index_col=None, parse_dates='day')
    df['year'] = df['day'].dt.year
    res = {'data': {}}
    for year, df2 in df.groupby('year'):
        res['data'][year] = {
            'dates': df2['day'].dt.strftime("%Y-%m-%d").values.tolist(),
            'high': df2['max_tmpf'].values.tolist(),
            'low': df2['min_tmpf'].values.tolist(),
            'rh': df2['avg_rh'].values.tolist()}
    fp = open('example.json', 'w')
    json.dump(res, fp)
    fp.close()


if __name__ == '__main__':
    main()
