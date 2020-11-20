from pandas.io.sql import read_sql
import psycopg2
import pandas as pd

pgconn = psycopg2.connect(database="cscap")

df = read_sql(
    """SELECT huc6_id, huc6_name from huc6""", pgconn, index_col="huc6_id"
)

df2 = pd.read_csv("WeatherCoopInHUC6.csv")

g = df2.groupby("huc6_id").median()

for i, row in g.iterrows():
    huc6 = ("0%s" % (i,))[-6:]
    print(i, df.loc[huc6, "huc6_name"], row["SeasPrcpMedian"])
