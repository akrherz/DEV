"""I fouled things up, per usual."""

import sys
import traceback

from pyiem.database import get_dbconnc
from pyiem.nws.product import TextProduct
from pyiem.nws.products.taf import parser
from tqdm import tqdm


def main(yr, second):
    """Go Main Go."""
    table = f"products_{yr}_{second}"
    conn, cursor = get_dbconnc("afos")
    cursor2 = conn.cursor()
    cursor.execute(
        f"select ctid, entered, data, source from {table} where pil is null "
        "and substr(source, 1, 1) in ('K', 'P', 'T') and "
        "substr(wmo, 1, 2) = 'FT'"
    )
    progress = tqdm(cursor, total=cursor.rowcount)
    for row in progress:
        taf = None
        if len(row["data"].split("TAF")) > -1:
            try:
                taf = parser(
                    row["data"].replace("TAF AMD ", ""), utcnow=row["entered"]
                )
                if len(taf.data) == 1:
                    pil = f"TAF{taf.data[0].station[1:]}"
                else:
                    pil = f"TAF{row['source'][1:]}"  # collective
            except Exception as exp:
                progress.write(str(exp))
                if "NoneType" in str(exp):
                    traceback.print_exc()
                    progress.write(row["data"])
                    sys.exit()
        if taf is None:
            # Likely multi- or give up
            taf = TextProduct(
                row["data"],
                utcnow=row["entered"],
                ugc_provider={},
                parse_segments=False,
            )
            pil = f"TAF{row['source'][1:]}"
        progress.set_description(f"{table} {pil}")
        cursor2.execute(
            f"UPDATE {table} SET pil = %s, bbb = %s WHERE ctid = %s",
            (pil, taf.bbb, row["ctid"]),
        )
    cursor2.close()
    conn.commit()


def frontend():
    for _yr in range(2012, 2020):
        for _second in ("0106", "0712"):
            main(_yr, _second)


if __name__ == "__main__":
    frontend()
