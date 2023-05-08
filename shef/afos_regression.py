"""Feed some AFOS data through for regression testing."""

from pyiem.nws.products.shef import parser
from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main."""
    cursor = get_dbconn("afos").cursor()
    cursor.execute(
        "SELECT data, source, pil from products where entered > '2021-09-21 20:03' and "
        "substr(pil, 1, 3) in ('RR1', 'RR2', 'RR3', 'RR5', 'RRM', 'RRS', 'RR6', 'RR4') "
        "ORDER by entered",
    )
    for row in cursor:
        prod = parser(row[0])
        if prod.warnings:
            print("\n".join(prod.warnings))
            print(prod.get_product_id())
            print("-" * 80)


if __name__ == "__main__":
    main()
