"""Process really old stuff."""
import os
import re
import datetime

import pytz
from pyiem.util import noaaport_text
from pyiem.nws.product import TextProduct, TextProductException
from pyiem.util import utc, get_dbconn
from tqdm import tqdm

# Copied from iem/scripts/util/poker2afos.py
XREF_SOURCE = {
    "KDSM": "KDMX",
    "KOKC": "KOUN",
    "KALB": "KALY",
    "KATL": "KFFC",
    "KAUS": "KEWX",
    "KBHM": "KBMX",
    "KBIL": "KBYZ",
    "KBNA": "KOHX",
    "KBOS": "KBOX",
    "KDEN": "KBOU",
    "KDFW": "KFWD",
    "KDTW": "KDTX",
    "KEKO": "KLKN",
    "KELP": "KEPZ",
    "KEYW": "KKEY",
    "KFAT": "KHNX",
    "KFLG": "KFGZ",
    "KHOU": "KHGX",
    "KHSV": "KHUN",
    "KLAS": "KVEF",
    "KLAX": "KLOX",
    "KLBB": "KLUB",
    "KLIT": "KLZK",
    "KLSE": "KARX",
    "KMCI": "KEAX",
    "KMEM": "KMEG",
    "KMIA": "KMFL",
    "KMLI": "KDVN",
    "KMSP": "KMPX",
    "KNEW": "KLIX",
    "KNYC": "KOKX",
    "KOMA": "KOAX",
    "KORD": "KLOT",
    "KPDX": "KPQR",
    "KPHX": "KPSR",
    "KPIT": "KPBZ",
    "KRAP": "KUNR",
    "KRDU": "KRAH",
    "KSAC": "KSTO",
    "KSAN": "KSGX",
    "KSAT": "KEWX",
    "KSFO": "KSTO",
    "KSTL": "KLSX",
    "KTLH": "KTAE",
    "KTUL": "KTSA",
    "KTUS": "KTWC",
    "KALO": "KDMX",
    "KDBQ": "KDVN",
    "KCAK": "KCLE",
    "KHLN": "KTFX",
    "KPNS": "KMOB",
    "KAVP": "KBGM",
    "KCOS": "KPUB",
    "KERI": "KCLE",
    "KTPA": "KTBW",
    "KWMC": "KLKN",
    "KSYR": "KBGM",
    "KPBI": "KMFL",
    "KCPR": "KRIW",
    "KCLT": "KGSP",
    "KBFL": "KHNX",
    "KEUG": "KPQR",
    "KYNG": "KCLE",
    "KCSG": "KFFC",
    "KALS": "KPUB",
    "KBPT": "KLCH",
    "KDCA": "KLWX",
    "KLND": "KRIW",
    "KTOL": "KCLE",
    "KAHN": "KFFC",
    "KMFD": "KCLE",
    "KBFF": "KCYS",
    "KAST": "KPQR",
    "KORH": "KBOX",
    "KSPS": "KOUN",
    "KSMX": "KLOX",
    'KMKC': "KWNS",
}


def save(prod, cursor):
    """Save this to the database!"""
    if prod.valid.year > 1996 or prod.valid.year < 1993:
        return
    utcnow = prod.valid.astimezone(pytz.UTC)
    table = "products_%s_%s" % (
        utcnow.year, "0106" if utcnow.month < 7 else "0712")
    wmo = prod.wmo
    if len(wmo) == 5:
        wmo = "%s0%s" % (wmo[:4], wmo[4])
    cursor.execute("""
        INSERT into """ + table + """ (data, pil, entered, source, wmo)
        VALUES (%s, %s, %s, %s, %s)
    """, (prod.text, prod.afos, prod.valid,
          XREF_SOURCE.get(prod.source, prod.source), wmo))


def main():
    """Go Main Go."""
    os.chdir("/mesonet/tmp/poker")
    dbconn = get_dbconn('afos')
    for dirpath, _dirnames, filenames in tqdm(os.walk(".")):
        cursor = dbconn.cursor()
        for fn in filenames:
            if not fn.endswith(".gdbm"):
                continue
            date = datetime.datetime.strptime(dirpath[:12], "./%Y/%b%d")
            utcnow = utc(date.year, date.month, date.day)
            data = open(
                "%s/%s" % (dirpath, fn), 'rb').read().decode('ascii', 'ignore')
            tokens = re.split("[0-9]{3} \r\r\n", data)
            for token in tokens:
                product = "000 \r\r\n%s" % (token, )
                product = noaaport_text(product).replace("\000", "")
                product = product.split("\003")[0]
                try:
                    prod = TextProduct(
                        product, utcnow=utcnow, parse_segments=False)
                    save(prod, cursor)
                except Exception as _exp:
                    continue
        cursor.close()
        dbconn.commit()


if __name__ == '__main__':
    main()
