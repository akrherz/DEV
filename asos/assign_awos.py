"""Quacks like a duck, it must be a duck."""

import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, get_sqlalchemy_conn, logger

LOG = logger()
ATTR = "IS_AWOS"


def compute_is_awos(station):
    """Look at the timestamps."""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            SELECT extract(minute from valid) as minute, count(*) from t2023
            where station = %s and valid > now() - '30 days'::interval
            GROUP by minute
            """,
            conn,
            params=(station,),
        )
    if df.empty:
        return None
    # We have lots of flakey AWOS sites that randomly report at some other time
    df = df[df["count"] > 5]
    # If it isn't 3, then we won't try more
    if len(df.index) != 3 or df["count"].max() < 30:
        return False
    # counts should be within 95% of each other
    if (df["count"].max() / df["count"].min()) > 1.05:
        return False
    return True


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("mesosite") as conn:
        netdf = pd.read_sql(
            "SELECT id from networks where id ~* '_ASOS' and "
            "length(id) = 7",
            conn,
            index_col=None,
        )
    mesosite = get_dbconn("mesosite")
    for network in netdf["id"].values:
        nt = NetworkTable(network, only_online=False)
        cursor = mesosite.cursor()
        for station, meta in nt.sts.items():
            is_awos = compute_is_awos(station)
            ois_awos = meta["attributes"].get(ATTR) == "1"
            if is_awos is None or is_awos == ois_awos or is_awos is False:
                continue
            if ois_awos and not is_awos:
                print(station, meta["name"], ois_awos, is_awos)
                raise ValueError("WTF")
            LOG.info(
                "%s[%s] %s %s -> %s",
                station,
                network,
                meta["name"],
                ois_awos,
                is_awos,
            )
            cursor.execute(
                """
                INSERT into station_attributes (iemid, attr, value)
                VALUES (%s, %s, %s)
                """,
                (meta["iemid"], ATTR, "1"),
            )

        cursor.close()
        mesosite.commit()


if __name__ == "__main__":
    main()
