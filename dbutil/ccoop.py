"""
We have something new, CCOOP, celluar COOP sites.
"""

import geopandas as gpd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.reference import nwsli2state


@with_sqlalchemy_conn("mesosite")
def main(conn=None):
    """Go Main Go."""
    df = gpd.read_file("https://www.weather.gov/source/crh/ccoop/master.json")
    for _, row in df.iterrows():
        sid = row["sid"]
        if len(sid) != 5 or sid in [
            "SFSC1",
        ]:
            print(f"skipping {sid}")
            continue
        res = conn.execute(
            sql_helper("select network from stations where id = :sid"),
            {"sid": sid},
        )
        networks = [x[0] for x in res.fetchall()]
        state = nwsli2state.get(sid[3:])
        if len(networks) == 2:
            # The COOP should be deleted
            print(
                f"python delete_station.py --network={state}_COOP "
                f"--station{sid}"
            )
        if networks == [f"{state}_COOP"]:
            # Switch to DCP
            print(f"Switching {sid} to DCP")
            conn.execute(
                sql_helper(
                    "UPDATE stations SET network = :network WHERE id = :sid "
                    "and network = :network2"
                ),
                {
                    "network": f"{state}_DCP",
                    "sid": sid,
                    "network2": f"{state}_COOP",
                },
            )
            continue
        res = conn.execute(
            sql_helper(
                "select iemid from stations where id = :sid "
                "and network = :network"
            ),
            {"sid": sid, "network": f"{state}_DCP"},
        )
        iemid = res.fetchone()[0]
        res = conn.execute(
            sql_helper(
                "select value from station_attributes where iemid = :iemid "
                "and attr = 'IS_CCOOP'"
            ),
            {"iemid": iemid},
        )
        if res.rowcount > 0:
            print(f"Already marked {sid} as CCOOP")
            continue
        conn.execute(
            sql_helper(
                "insert into station_attributes(iemid, attr, value) values "
                "(:iemid, 'IS_CCOOP', '1')"
            ),
            {"iemid": iemid},
        )
    conn.commit()


if __name__ == "__main__":
    main()
