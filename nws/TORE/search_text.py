"""Send products from AFOS database to pyWWA"""

from tqdm import tqdm
from pyiem.util import noaaport_text, get_dbconn
AFOS = get_dbconn('afos')
acursor = AFOS.cursor()


o = open('tornado_emergency_2019.txt', 'a')
for year in tqdm(range(2019, 2020)):
    for suffix in ['0106', '0712']:
        table = "products_%s_%s" % (year, suffix)
        acursor.execute("""
            SELECT data, source, entered from """ + table + """
            WHERE entered > '2018-09-14 12:00' and
            substr(pil, 1, 3) in ('TOR', 'SVS')
            and data ~* 'EMERGENCY' ORDER by entered ASC
        """)
        for row in acursor:
            raw = " ".join(
                row[0].upper().replace("\r", "").replace("\n", " ").split())
            if raw.find("TORNADO EMERGENCY") == -1:
                continue
            o.write(noaaport_text(row[0]))
            print(" Hit %s %s" % (row[1], row[2]))
o.close()
