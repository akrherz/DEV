"""Go Fishing."""

from pyiem.util import get_dbconn
from pyiem.nws.products.vtec import parser


def main():
    """Go Main Go."""
    afos = get_dbconn("afos")
    cursor = afos.cursor()
    cursor.execute(
        "SELECT data from products where entered > '2019-07-01' and "
        "substr(pil, 1, 3) in ('FLS', 'FFS', 'FLW', 'FFW') ORDER by entered "
        "ASC"
    )
    samples = {}
    for row in cursor:
        try:
            prod = parser(row[0])
        except Exception as exp:
            print(f"ERROR, exp: {exp}")
            continue
        for seg in prod.segments:
            for hvtec in seg.hvtec:
                for col in ["beginTS", "crestTS", "endTS"]:
                    val = getattr(hvtec, col, None)
                    if val is None:
                        continue
                    if val.year in [2019, 2020]:
                        continue
                    if prod.source in samples:
                        continue
                    samples[prod.source] = 1
                    print(
                        f"{prod.get_product_id()} vtec:{seg.vtec[0]} "
                        f"hvtec:{hvtec}"
                    )


if __name__ == "__main__":
    main()
