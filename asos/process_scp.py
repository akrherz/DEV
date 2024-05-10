"""Ingest the NESDIS SCP Product."""

from tqdm import tqdm

from pyiem.database import get_dbconn
from pyiem.nws.products.scp import parser
from pyiem.util import noaaport_text


def do(table):
    """Go!"""
    afos = get_dbconn("afos")
    asos = get_dbconn("asos")
    fcursor = afos.cursor()
    fcursor.execute("SET TIME ZONE 'UTC'")
    fcursor.execute(
        f"SELECT entered, data, pil from {table} WHERE "
        "substr(pil, 1, 3) = 'SCP' "
        "and source in ('KNES', 'KWBC') ORDER by entered ASC"
    )
    for row in fcursor:
        text = row[1].encode("ascii", "ignore").decode("ascii", "ignore")
        try:
            prod = parser(noaaport_text(text), utcnow=row[0])
            if prod.afos is None:
                prod.afos = row[2]
        except Exception as exp:
            print(exp)
            continue
        cursor = asos.cursor()
        prod.sql(cursor)
        cursor.close()
        asos.commit()


def main():
    """Go Main Go."""
    progress = tqdm(range(1993, 2021))
    for year in progress:
        progress.set_description(str(year))
        for suffix in ["0106", "0712"]:
            do(f"products_{year}_{suffix}")


if __name__ == "__main__":
    main()
