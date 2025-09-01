"""Dump text from database."""

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor.execute(
        "WITH data as ("
        "SELECT wfo, eventid, issue at time zone 'UTC' as issue, report, "
        "expire at time zone 'UTC' as expire, "
        "svs, row_number() OVER (PARTITION by wfo, eventid, "
        "vtec_year ORDER by length(svs) DESC) from "
        "warnings where phenomena = 'FF' and significance = 'W' and "
        "is_emergency) "
        "SELECT * from data WHERE row_number = 1 ORDER by issue, wfo, eventid"
    )
    done = []
    for row in cursor:
        key = f"{row[0]}_{row[1]}_{row[2].year}"
        if key in done:
            continue
        done.append(key)
        i = 0
        with open(f"FFE_Text/{key}_{i}.txt", "w") as fh:
            fh.write(row[3])
        for prod in ("" if row[5] is None else row[5]).split("__"):
            if prod.strip() == "":
                continue
            i += 1
            with open(f"FFE_Text/{key}_{i}.txt", "w") as fh:
                fh.write(prod)


if __name__ == "__main__":
    main()
