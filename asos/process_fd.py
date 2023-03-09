"""Ingest the KWNO FD Product."""

from tqdm import tqdm
from pyiem.nws.products.fd import parser
from pyiem.util import get_dbconn


def do(table):
    """Go!"""
    afos = get_dbconn("afos")
    asos = get_dbconn("asos", host="localhost")
    fcursor = afos.cursor()
    fcursor.execute("SET TIME ZONE 'UTC'")
    fcursor.execute(
        f"SELECT entered, data, pil from {table} WHERE "
        "substr(pil, 1, 2) = 'FD' "
        "and source = 'KWNO' ORDER by entered ASC"
    )
    for row in fcursor:
        text = row[1].encode("ascii", "ignore").decode("ascii", "ignore")
        cursor = asos.cursor()
        prod = parser(text, utcnow=row[0])
        prod.sql(cursor)
        cursor.close()
        asos.commit()


def main():
    """Go Main Go."""
    progress = tqdm(range(2004, 2024))
    for year in progress:
        progress.set_description(str(year))
        for suffix in ["0106", "0712"]:
            do(f"products_{year}_{suffix}")


if __name__ == "__main__":
    main()
