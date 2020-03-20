"""Something to hit NCEI's HAS API"""
from __future__ import print_function
import datetime
import sys

import requests

FORM = {
    "satdisptype": "N/A",
    "stations": "ALL",
    "station_lst": "KWNS",
    "typeofdata": "ACUS0",
    "dtypelist": "",
    "begdatestring": "2008060100",
    "enddatestring": "2008060600",
    "begyear": "2008",
    "begmonth": "10",
    "begday": "16",
    "beghour": "",
    "begmin": "",
    "endyear": "2008",
    "endmonth": "12",
    "endday": "10",
    "endhour": "",
    "endmin": "",
    "outmed": "FTP",
    "outpath": "",
    "pri": "500",
    "datasetname": "9957ANX",
    "directsub": "Y",
    "emailadd": "akrherz@iastate.edu",
    "outdest": "FILE",
    "applname": "",
    "subqueryby": "STATION",
    "tmeth": "Awaiting-Data-Transfer",
}

URI = "https://www.ncdc.noaa.gov/has/HAS.FileSelect"


def main(year):
    """Go"""
    # We have to request windows of 5 days or less for one month at a time!
    for month in range(1, 13):
        begins = []
        ends = []
        for day in range(1, 26, 5):
            begins.append(datetime.date(year, month, day))
            ends.append(datetime.date(year, month, day + 4))
        # Cleanup the 26th to whatever period
        nextmonth = datetime.date(year, month, 26) + datetime.timedelta(days=8)
        nextmonth = nextmonth.replace(day=1) - datetime.timedelta(days=1)
        begins.append(datetime.date(year, month, 26))
        ends.append(nextmonth)
        for sts, ets in zip(begins, ends):
            FORM["begdatestring"] = sts.strftime("%Y%m%d00")
            FORM["enddatestring"] = ets.strftime("%Y%m%d23")
            FORM["emailadd"] = ("akrherz+%s@iastate.edu") % (
                sts.strftime("%Y%m%d"),
            )
            req = requests.get(URI, FORM)
            if req.content.find("Order Submitted") > -1:
                print("OK %s %s" % (sts, ets))
            else:
                print("FAIL %s %s" % (sts, ets))
                output = open("/tmp/%s.html" % (sts.strftime("%Y%m%d"),), "w")
                output.write(req.content)
                output.close()


if __name__ == "__main__":
    main(int(sys.argv[1]))
