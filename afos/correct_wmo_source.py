"""Rectify some old WMO source codes used.

Archives of text data have been processed by the IEM.  Products prior to
NWS modernization (early 2000s) used a mixture of WMO source codes.  These
codes are important to various apps.  So this script attempts to fix it.
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
    "KTUS": "KTWC"
}
UNKNOWN = [
    'KABE', 'KABI', 'KACT', 'KACY', 'KADG', 'KAGS', 'KAHN', 'KALO', 'KALS',
    'KAPN', 'KARB', 'KAST', 'KAVL', 'KAVP', 'KBDL', 'KBDR', 'KBFF', 'KBFL',
    'KBIX', 'KBKW', 'KBLU', 'KBNO', 'KBPT', 'KBTM', 'KBTR', 'KBWI', 'KBZN',
    'KCAK', 'KCLT', 'KCMH', 'KCNK', 'KCNU', 'KCON', 'KCOS', 'KCOU', 'KCPR',
    'KCRW', 'KCSG', 'KCVG', 'KDAY', 'KDBQ', 'KDCA', 'KDMO', 'KDRT', 'KEAT',
    'KEKN', 'KELY', 'KERI', 'KEUG', 'KEVV', 'KEWR', 'KFAR', 'KFMY', 'KFNT',
    'KFOK', 'KFSM', 'KFTW', 'KFWA', 'KGCN', 'KGEG', 'KGLS', 'KGRI', 'KGSO',
    'KGTF', 'KHAF', 'KHFD', 'KHLN', 'KHMS', 'KHON', 'KHTS', 'KHUF', 'KHVR',
    'KIAD', 'KILG', 'KINL', 'KINW', 'KIPT', 'KISN', 'KLAF', 'KLEX', 'KLGB',
    'KLMT', 'KLND', 'KLNK', 'KLWS', 'KLYH', 'KMCN', 'KMEI', 'KMFD', 'KMGM',
    'KMGW', 'KMHK', 'KMKC', 'KMKE', 'KMKG', 'KMLS', 'KMOD', 'KMRY', 'KMSN',
    'KMYR', 'KNBC', 'KOAK', 'KOFK', 'KOLM', 'KORF', 'KORH', 'KPBI', 'KPGA',
    'KPHL', 'KPIA', 'KPNS', 'KPVD', 'KPWM', 'KRBL', 'KRDD', 'KRFD', 'KRIC',
    'KRNO', 'KROA', 'KROC', 'KRST', 'KSAV', 'KSBN', 'KSCK', 'KSDF', 'KSEA',
    'KSEZ', 'KSHR', 'KSLE', 'KSMP', 'KSNS', 'KSPI', 'KSPS', 'KSTC', 'KSTJ',
    'KSUX', 'KSXT', 'KSYR', 'KTOL', 'KTPA', 'KTRM', 'KTUP', 'KTYS', 'KUIL',
    'KUKI', 'KVCT', 'KVTN', 'KWAL', 'KWMC', 'KXMR', 'KYKM', 'KYNG', 'KYUM',
    'PAFA', 'PHLI', 'PHNL', 'PHTO', 'PTKK', 'PTPN', 'PTRO', 'PTYA', 'KCEC',
    'KMHS', 'KRDM', 'KSJC', 'KSMX', 'PADK', 'KAUO', 'KAWO', 'KVBG', 'KEDW',
    'KPRC', 'KVPS', 'KAPG', 'KGBN', 'KNGU', 'PAJN']


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
