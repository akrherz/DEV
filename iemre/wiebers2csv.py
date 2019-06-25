"""A util script to dump IEMRE json service to csv files"""

import requests
import pandas as pd
import geopandas as gpd


def main():
    """Go Main Go"""
    df = gpd.read_file('/tmp/AFREC_2018_centroid_id.shp')
    for _i, row in df.iterrows():
        uri = ("http://mesonet.agron.iastate.edu/iemre/multiday/"
               "2018-01-01/2018-12-31/%s/%s/json"
               ) % (row['geometry'].y, row['geometry'].x)
        req = requests.get(uri)
        res = []
        for row2 in req.json()['data']:
            res.append(row2)
        df2 = pd.DataFrame(res)
        df2['ID'] = row['ID']
        df2.to_csv("%s.csv" % (row['ID'],), index=False)


if __name__ == '__main__':
    main()
