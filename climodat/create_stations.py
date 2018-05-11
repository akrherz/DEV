"""One time bootstrapping of state averaged and climdiv stations"""


from pandas.io.sql import read_sql
from pyiem.reference import state_names
from pyiem.util import get_dbconn


def states():
    """Go Main Go"""
    output = open('insert.sql', 'w')
    pgconn = get_dbconn('postgis')
    df = read_sql("""
        SELECT st_x(st_centroid(the_geom)) as lon,
        st_y(st_centroid(the_geom)) as lat, state_abbr, state_name
        from states ORDER by state_abbr
    """, pgconn, index_col='state_abbr')
    for state, row in df.iterrows():
        if state in ['AK', 'HI', 'PR']:
            continue
        sql = """
        INSERT into stations(id, name, network, country, state,
        plot_name, online, metasite, geom) VALUES
        ('%s0000', '%s Average', '%sCLIMATE',
         'US', '%s', '%s Average', 't', 't', 'SRID=4326;POINT(%s %s)');
        """ % (state, row['state_name'], state, state, row['state_name'],
               row['lon'], row['lat'])
        output.write(sql)
    output.close()


def main():
    """Go Main Go"""
    output = open('insert.sql', 'w')
    pgconn = get_dbconn('postgis')
    df = read_sql("""
        SELECT st_x(st_centroid(geom)) as lon,
        st_y(st_centroid(geom)) as lat, st_abbrv, name, iemid
        from climdiv ORDER by iemid
    """, pgconn, index_col='iemid')
    for station, row in df.iterrows():
        if row['st_abbrv'] in ['AK', 'HI', 'PR']:
            continue
        name = "%s - %s Climate Division" % (state_names[row['st_abbrv']],
                                             row['name'].title())
        sql = """
        INSERT into stations(id, name, network, country, state,
        plot_name, online, metasite, geom) VALUES
        ('%s', '%s', '%sCLIMATE',
         'US', '%s', '%s', 't', 't', 'SRID=4326;POINT(%s %s)');
        """ % (station, name, row['st_abbrv'], row['st_abbrv'],
               name, row['lon'], row['lat'])
        output.write(sql)
    output.close()

if __name__ == '__main__':
    main()
