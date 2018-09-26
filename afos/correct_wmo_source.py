"""Rectify some old WMO source codes used.

Archives of text data have been processed by the IEM.  Products prior to
NWS modernization (early 2000s) used a mixture of WMO source codes.  These
codes are important to various apps.  So this script attempts to fix it.

Attempts to create lookups for one-off CLI products
with data as (
    select distinct source, pil from products_1999_0106),
 agg as (
     select source, count(*), max(pil) from data GROUP by source),
 agg2 as (
     select * from agg where count = 1 and substr(max, 1, 3) = 'CLI')

 select distinct '"'||a.source||'": "'||c.source||'",'
 from products_2018_0712 c, agg2 a WHERE c.pil = a.max;

 with data as (
     select distinct pil from products_2009_0106 where source is null),
 present as (
     select distinct c.source, d.pil from products_2018_0712 c, data d
     where c.pil = d.pil)
 update products_2009_0106 t SET source = p.source
 FROM present p WHERE t.source is null and t.pil = p.pil;
"""
import sys
import json

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
XREF = {
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
}
UNKNOWN = [
    'KABE', 'KABI', 'KACT', 'KACY', 'KADG', 'KAGS',
    'KAPN', 'KARB', 'KAVL', 'KBDL', 'KBDR',
    'KBIX', 'KBKW', 'KBLU', 'KBNO', 'KBTM', 'KBTR', 'KBWI', 'KBZN',
    'KCMH', 'KCNK', 'KCNU', 'KCON', 'KCOU',
    'KCRW', 'KCVG', 'KDAY', 'KDMO', 'KDRT', 'KEAT',
    'KEKN', 'KELY', 'KEVV', 'KEWR', 'KFAR', 'KFMY', 'KFNT',
    'KFOK', 'KFSM', 'KFTW', 'KFWA', 'KGCN', 'KGEG', 'KGLS', 'KGRI', 'KGSO',
    'KGTF', 'KHAF', 'KHFD', 'KHMS', 'KHON', 'KHTS', 'KHUF', 'KHVR',
    'KIAD', 'KILG', 'KINL', 'KINW', 'KIPT', 'KISN', 'KLAF', 'KLEX', 'KLGB',
    'KLMT', 'KLNK', 'KLWS', 'KLYH', 'KMCN', 'KMEI', 'KMGM',
    'KMGW', 'KMHK', 'KMKC', 'KMKE', 'KMKG', 'KMLS', 'KMOD', 'KMRY', 'KMSN',
    'KMYR', 'KNBC', 'KOAK', 'KOFK', 'KOLM', 'KORF', 'KPGA',
    'KPHL', 'KPIA', 'KPVD', 'KPWM', 'KRBL', 'KRDD', 'KRFD', 'KRIC',
    'KRNO', 'KROA', 'KROC', 'KRST', 'KSAV', 'KSBN', 'KSCK', 'KSDF', 'KSEA',
    'KSEZ', 'KSHR', 'KSLE', 'KSMP', 'KSNS', 'KSPI', 'KSPS', 'KSTC', 'KSTJ',
    'KSUX', 'KSXT', 'KTRM', 'KTUP', 'KTYS', 'KUIL',
    'KUKI', 'KVCT', 'KVTN', 'KWAL', 'KXMR', 'KYKM', 'KYUM',
    'PAFA', 'PHLI', 'PHNL', 'PHTO', 'PTKK', 'PTPN', 'PTRO', 'PTYA', 'KCEC',
    'KMHS', 'KRDM', 'KSJC', 'KSMX', 'PADK', 'KAUO', 'KAWO', 'KVBG', 'KEDW',
    'KPRC', 'KVPS', 'KAPG', 'KGBN', 'KNGU', 'PAJN', 'KCQC', 'KGDP', 'KGNT',
    'KGUY', 'KMWT', 'KNMT', 'KOQT', 'KRAM', 'KROW', 'KRTN', 'PKMJ',
    'PKWA', 'PWAK', 'PAVD', 'PGSN', 'KASD', 'KBUO', 'KCHO', 'KCZK', 'KGFL',
    'KHMM', 'KJNW', 'KLVM', 'KMLD', 'KMRB', 'KSJX', 'KSOW', 'PKMR']


def main(argv):
    """Go Main Go."""
    table = argv[1]
    nt = NetworkTable(["WFO", "RFC", "NWS", "NCEP", "CWSU", "WSO"])
    pgconn = get_dbconn('afos', user='mesonet')
    mpgconn = get_dbconn('mesosite')
    cursor = pgconn.cursor()
    mcursor = mpgconn.cursor()
    df = read_sql("""
        SELECT source, count(*) from """ + table + """
        WHERE source is not null GROUP by source ORDER by source
    """, pgconn, index_col='source')
    for source, row in df.iterrows():
        if source[0] not in ['K', 'P']:
            continue
        if source in UNKNOWN:
            continue
        iemsource = source[1:] if source[0] == 'K' else source
        if iemsource in nt.sts:
            continue
        if source in XREF:
            cursor.execute("""
                UPDATE """ + table + """ SET source = %s WHERE source = %s
            """, (XREF[source], source))
            print(("Correcting %s -> %s, %s rows"
                   ) % (source, XREF[source], cursor.rowcount))
        else:
            if row['count'] < 10:
                print("skipping %s as row count is low" % (source, ))
                continue
            mcursor.execute("""
                WITH centers as (
                    select id, geom::geography from stations where network in
                    ('WFO', 'RFC', 'NWS', 'NCEP', 'CWSU', 'WSO')
                ), asos as (
                    SELECT geom::geography from stations where id = %s
                    and network ~* 'ASOS'
                )
                SELECT c.id as center, st_distance(c.geom, a.geom)
                from centers c, asos a ORDER by st_distance ASC
            """, (iemsource, ))
            if mcursor.rowcount < 5:
                print("Source: %s is double unknown" % (source, ))
                continue
            for i, row2 in enumerate(mcursor):
                print("%s %s %.2f" % (source, row2[0], row2[1]))
                if i > 4:
                    break
            newval = input(
                "What do you want to do with %s (count:%s)? " % (
                    source, row['count']))
            if len(newval) == 4:
                XREF[source] = newval
            else:
                UNKNOWN.append(source)

    print(json.dumps(XREF, indent=4))
    print(UNKNOWN)
    cursor.close()
    pgconn.commit()


if __name__ == '__main__':
    main(sys.argv)
