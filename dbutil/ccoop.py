"""
We have something new, CCOOP, celluar COOP sites.
"""
import geopandas as gpd
from pyiem.database import get_dbconnc
from pyiem.reference import nwsli2state


def main():
    """Go Main Go."""
    pgconn, cursor = get_dbconnc("mesosite")

    df = gpd.read_file("https://www.weather.gov/source/crh/ccoop/master.json")
    for _, row in df.iterrows():
        sid = row["sid"]
        if len(sid) != 5 or sid in [
            "SFSC1",
        ]:
            print(f"skipping {sid}")
            continue
        cursor.execute("select network from stations where id = %s", (sid,))
        networks = [x["network"] for x in cursor.fetchall()]
        state = nwsli2state.get(sid[3:])
        if len(networks) == 2:
            # The COOP should be deleted
            print(f"python delete_station.py {state}_COOP {sid}")
        if networks == [f"{state}_COOP"]:
            # Switch to DCP
            print(f"Switching {sid} to DCP")
            cursor.execute(
                "UPDATE stations SET network = %s WHERE id = %s and "
                "network = %s",
                (f"{state}_DCP", sid, f"{state}_COOP"),
            )
            continue
        cursor.execute(
            "select iemid from stations where id = %s and network = %s",
            (sid, f"{state}_DCP"),
        )
        iemid = cursor.fetchone()["iemid"]
        cursor.execute(
            "insert into station_attributes(iemid, attr, value) values "
            "(%s, 'IS_CCOOP', '1')",
            (iemid,),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
