"""Search the warnings database for potential FFEs."""

from pyiem.util import get_dbconn
from tqdm import tqdm


def main():
    """Go Main Go."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    wcursor = pgconn.cursor()

    for year in tqdm(range(2003, 2008)):
        cursor.execute(
            (
                "SELECT wfo, eventid, ctid, report, svs "
                f"from warnings_{year} "
                "WHERE phenomena = 'FF' and significance = 'W' and "
                "(report ~* 'EMERGENCY' or svs ~* 'EMERGENCY') "
            )
        )
        for row in cursor:
            for text in [row[3], row[4]]:
                if text is None or text.strip() == "":
                    continue
                raw = " ".join(
                    text.upper().replace("\r", "").replace("\n", " ").split()
                )
                if raw.find("FLASH FLOOD EMERGENCY") > -1:
                    print(f"Hit {year} {row[0]} {row[1]}")
                    wcursor.execute(
                        f"UPDATE warnings_{year} SET is_emergency = 't' "
                        "WHERE ctid = %s",
                        (row[2],),
                    )
    wcursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
