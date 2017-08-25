"""we get an excel file with station locations, so we merge"""
from __future__ import print_function
import pandas as pd
import psycopg2

PGCONN = psycopg2.connect(database='mesosite', host='localhost', port=5555,
                          user='mesonet')

def main():
    """Go!"""
    cursor = PGCONN.cursor()
    df = pd.read_excel("/tmp/YCFCD.xlsx", skiprows=[0, 1])
    df2 = df[pd.notnull(df['NWS HB5 Name'])]
    print(df2.columns)
    for _, row in df2[['NWS HB5 Name',
                    'LATITUDE (DD)', 'LONGITUDE (DD)']].iterrows():
        sql = ("UPDATE stations SET geom='SRID=4326;POINT(-%s %s)'"
               " , county = null, elevation = -999, ugc_zone = null "
               " WHERE network = 'AZ_DCP' and id = '%s';\n"
               ) % (row['LONGITUDE (DD)'], row['LATITUDE (DD)'],
                    row['NWS HB5 Name'])
        if row['NWS HB5 Name'][-2:] == 'A3' and isinstance(row['LATITUDE (DD)'], float):
            print(sql)
            cursor.execute(sql)

    cursor.close()
    PGCONN.commit()
    PGCONN.close()


if __name__ == '__main__':
    main()
