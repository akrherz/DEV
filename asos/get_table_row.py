"""Get data needed for a data table summarizing a ASOS event."""

import click
from pyiem.database import get_sqlalchemy_conn, sql_helper


@click.command()
@click.option("--station", required=True)
def main(station: str):
    """Go main go."""
    with get_sqlalchemy_conn("asos") as conn:
        res = conn.execute(
            sql_helper("""
            select iemid, archive_begin + '1 day'::interval as archive_begin,
            state, name from stations where id = :id
            and network ~* 'ASOS'
            """),
            {"id": station},
        )
        row = res.mappings().fetchone()
        iemid = row["iemid"]
        archive_begin = row["archive_begin"].year
        state = row["state"]
        name = row["name"]

    with get_sqlalchemy_conn("iem") as conn:
        res = conn.execute(
            sql_helper("""
            select day, max_dwpf from summary where iemid = :iemid
            and day in ('2026-07-26', '2026-07-27') ORDER by day asc
            """),
            {"iemid": iemid},
        )
        rows = res.mappings().fetchall()
        jul26 = rows[0]["max_dwpf"]
        jul27 = rows[1]["max_dwpf"]

    with get_sqlalchemy_conn("asos") as conn:
        res = conn.execute(
            sql_helper("""
            select valid, dwpf from alldata where station = :station
            and valid < '2026-07-26' and dwpf > :floor order by valid desc
            limit 5
            """),
            {"station": station, "floor": max(jul26, jul27) - 0.5},
        )
        firstentry = None
        for i, row in enumerate(res.mappings()):
            if i == 0:
                firstentry = row["valid"].strftime("%Y %b %-d")
            print(f"{row['valid']} {row['dwpf']}")

        res = conn.execute(
            sql_helper("""
            select valid, dwpf from alldata where station = :station
            and dwpf > :floor order by dwpf desc, valid desc
            limit 1
            """),
            {"station": station, "floor": max(jul26, jul27) - 0.5},
        )
        row = res.mappings().fetchone()
        maxvalue = row["dwpf"]
        maxdate = row["valid"].strftime("%Y %b %-d")

    print(
        "<tr>\n"
        f"<td>{state}</td>\n"
        f"<td>{station}</td>\n"
        f"<td>{name}</td>\n"
        f"<td>{archive_begin}</td>\n"
        f"<td>{jul26:.0f}</td>\n"
        f"<td>{jul27:.0f}</td>\n"
        f"<td>{'..' if firstentry is None else firstentry}</td>\n"
        f"<td>{maxvalue:.0f}</td>\n"
        f"<td>{maxdate}</td>\n"
        "</tr>\n"
    )


if __name__ == "__main__":
    main()
