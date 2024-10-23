import psycopg2
import pytz
from pandas.io.sql import read_sql

pgconn = psycopg2.connect(database="asos", host="iemdb", user="nobody")

df = read_sql(
    """SELECT
    timezone('UTC', date_trunc('hour', valid at time zone 'UTC')) as valid,
    sknt, drct from t2017 where station = 'DSM'
    LImit 1
    """,
    pgconn,
    index_col=None,
)

print(df["valid"].apply(lambda x: x.tz_convert(pytz.utc)))
