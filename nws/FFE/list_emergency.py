"""Parse what was dumped into more fun"""
from functools import partial

from shapely.ops import transform
import pandas as pd
from pyiem.nws.products.vtec import parser

project = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:4326'),  # source coordinate system
    pyproj.Proj(init='epsg:2163'))


def main():
    """Go Main Go"""
    data = open('flood_emergency_filtered.txt', 'rb').read().decode('ascii')
    rows = []
    etn = 9000
    for report in data.split("\003"):
        if report == "":
            continue
        v = parser(report)
        data = {
            'link': ('http://mesonet.agron.iastate.edu/'
                     'p.php?pid=%s') % (v.get_product_id(), ),
            'utc_valid': v.valid.strftime("%Y-%m-%d %H:%M"),
            'source': v.source,
            'phenomena': 'FF',
            'significance': 'W',
            'eventid': etn,
            'expire': '',
            'size': 0,
            'year': v.valid.year
        }
        if v.segments[0].vtec:
            vt = v.segments[0].vtec[0]
            if vt.action == 'CAN':
                print("False Positive?!")
                pos = report.find("FLASH FLOOD EMERGENCY")
                print(report[pos-50:pos+50])
                continue
            data['eventid'] = vt.etn
            data['expire'] = v.segments[0].vtec[0].endts.strftime(
                "%Y-%m-%d %H:%M")
            data['size'] = transform(project, v.segments[0].sbw).area / 1e6
        else:
            etn += 1
        rows.append(data)
    df = pd.DataFrame(rows)
    df.to_csv('flood_emergencies.csv')


if __name__ == '__main__':
    main()
