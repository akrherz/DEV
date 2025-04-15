"""Delete data we do not need."""

import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger

LOG = logger()
IEM = get_dbconn("iem")
MESOSITE = get_dbconn("mesosite")


def workflow(iemid, row):
    """Do Work."""
    for year in range(2023, 1980, -1):
        with get_sqlalchemy_conn("iem") as conn:
            df = pd.read_sql(
                f"SELECT * from summary_{year} WHERE iemid = %s",
                conn,
                params=(iemid,),
            )
        if df.empty:
            continue
        # drop two columns that have data
        df = df.drop(columns=["iemid", "day"])
        # Is this entire data frame null?
        if not df.isnull().values.all():
            print(f"Found data at year {year}, aborting")
            return
        print("All null, culling", year, iemid, row["id"])

        icursor = IEM.cursor()
        icursor.execute(
            f"DELETE from summary_{year} where iemid = %s",
            (iemid,),
        )
        icursor.close()
        IEM.commit()


def main():
    """Go Main Go"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
            SELECT s.iemid, id, network from stations s JOIN current c ON
            (s.iemid = c.iemid) where c.valid < '2021-01-01' and
            (s.network ~* 'COOP' or s.network ~* 'DCP')
            and not online ORDER by id ASC
        """,
            conn,
            index_col="iemid",
        )
    for iemid, row in df.iterrows():
        workflow(iemid, row)


if __name__ == "__main__":
    main()
