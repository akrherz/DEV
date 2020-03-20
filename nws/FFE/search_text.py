"""Send products from AFOS database to pyWWA"""

from tqdm import tqdm
from pyiem.util import noaaport_text, get_dbconn

AFOS = get_dbconn("afos")
acursor = AFOS.cursor()


for year in tqdm(range(2019, 2020)):
    for suffix in ["0106", "0712"]:
        table = "products_%s_%s" % (year, suffix)
        acursor.execute(
            (
                f"SELECT data, source, entered from {table} "
                "WHERE entered > '2018-09-14 12:00' and "
                "substr(pil, 1, 3) in ('FFW', 'FFS') "
                "and data ~* 'EMERGENCY' ORDER by entered ASC "
            )
        )
        with open("flood_emergency_2019.txt", "a") as fh:
            for row in acursor:
                raw = " ".join(
                    row[0].upper().replace("\r", "").replace("\n", " ").split()
                )
                if raw.find("FLASH FLOOD EMERGENCY") == -1:
                    continue
                fh.write(noaaport_text(row[0]))
                print(" Hit %s %s" % (row[1], row[2]))
