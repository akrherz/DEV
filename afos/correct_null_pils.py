"""Find afos database entries that have null PIL values"""
from __future__ import print_function
import psycopg2
from pyiem.util import noaaport_text
from pyiem.nws.product import TextProduct


def dotable(table):
    """Go main go"""
    pgconn = psycopg2.connect(database='afos', host='localhost', port=5555,
                              user='mesonet')
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    cursor.execute("""SELECT entered, data, source, wmo from """ + table + """
    WHERE pil is null""")
    failures = 0
    updated = 0
    noupdates = 0
    for row in cursor:
        product = noaaport_text(row[1])
        try:
            tp = TextProduct(product, utcnow=row[0],
                             parse_segments=False)
        except Exception as exp:
            failures += 1
            if str(exp).find('Could not parse WMO header!') == -1:
                print(exp)
            continue
        if tp.afos is None:
            failures += 1
            continue
        cursor2.execute("""UPDATE """ + table + """
        SET data = %s, pil = %s WHERE pil is null and entered = %s and
        source = %s and wmo = %s
        """, (product, tp.afos, row[0], row[2], row[3]))
        if cursor2.rowcount == 0:
            print("Hmmmm")
            noupdates = 0
        else:
            updated += 1
    print(("%s rows: %s updated: %s failures: %s noupdates: %s"
           ) % (table, cursor.rowcount, updated, failures, noupdates))
    cursor2.close()
    pgconn.commit()


def main():
    """Do Main"""
    for year in range(2000, 2018):
        for col in ['0106', '0712']:
            table = "products_%s_%s" % (year, col)
            dotable(table)


if __name__ == '__main__':
    main()
