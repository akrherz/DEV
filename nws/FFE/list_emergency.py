"""Parse what was dumped into more fun"""

import pandas as pd
from pyiem.nws.products.vtec import parser


def main():
    """Go Main Go"""
    data = open('flood_emergency_filtered.txt', 'rb').read().decode('ascii')
    rows = []
    etn = 9000
    for report in data.split("\003"):
        if report == "":
            continue
        v = parser(report)
        data = {'link': ('http://mesonet.agron.iastate.edu/'
                         'p.php?pid=%s') % (v.get_product_id(), ),
                'utc_valid': v.valid.strftime("%Y-%m-%d %H:%M"),
                'source': v.source,
                'phenomena': 'FF', 'significance': 'W', 'eventid': etn,
                'year': v.valid.year}
        if v.segments[0].vtec:
            vt = v.segments[0].vtec[0]
            if vt.action == 'CAN':
                print("False Positive?!")
                pos = report.find("FLASH FLOOD EMERGENCY")
                print(report[pos-50:pos+50])
                continue
            data['eventid'] = vt.etn
            # data['phenomena'] = vt.phenomena
            # data['significance'] = vt.significance
        else:
            etn += 1
        rows.append(data)
    df = pd.DataFrame(rows)
    df.to_csv('flood_emergencies.csv')


if __name__ == '__main__':
    main()