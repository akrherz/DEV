"""Trim back sites that are now offline."""

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger

LOG = logger()
IEM = get_dbconn("iem")
MESOSITE = get_dbconn("mesosite")


def workflow(iemid, row):
    """Do Work."""
    mcursor = MESOSITE.cursor()
    mcursor.execute(
        "UPDATE stations SET online = 'f' where iemid = %s",
        (iemid,),
    )
    mcursor.close()
    MESOSITE.commit()

    icursor = IEM.cursor()
    icursor.execute(
        "DELETE from summary_2021 where iemid = %s",
        (iemid,),
    )
    LOG.info(
        "Trimmed %s summary rows for %s %s",
        icursor.rowcount,
        row["id"],
        row["network"],
    )
    icursor.close()
    IEM.commit()


def main():
    """Go Main Go"""
    df = read_sql(
        """
        SELECT s.iemid, id, network from stations s JOIN current c ON
        (s.iemid = c.iemid) where c.valid < '2019-01-01' and
        s.network ~* 'DCP' ORDER by id
    """,
        IEM,
        index_col="iemid",
    )
    for iemid, row in df.iterrows():
        workflow(iemid, row)


if __name__ == "__main__":
    main()
