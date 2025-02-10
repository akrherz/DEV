"""Do Something Fun"""

# third party
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper


def main():
    """Do Something"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper("""SELECT ugc, eventid,
            generate_series(issue, expire, '1 minute'::interval) as ts
            from warnings WHERE phenomena = 'TO' and significance = 'W'
            ORDER by ts ASC
        """),
            conn,
            index_col=None,
        )
    maxrunning = 0
    for ugc, gdf in df.groupby("ugc"):
        lastts = gdf.iloc[0]["ts"]
        running = [0, lastts, None]
        for _, row in gdf.iterrows():
            delta = (row["ts"] - lastts).total_seconds()
            if delta > 61:
                running = [0, row["ts"], None]
            else:
                if (row["ts"] - running[1]).total_seconds() > maxrunning:
                    print(
                        "%s %s %s %s"
                        % (ugc, maxrunning / 3600.0, row["ts"], running[1])
                    )
                    maxrunning = (row["ts"] - running[1]).total_seconds()
            lastts = row["ts"]


if __name__ == "__main__":
    main()
