"""Dmx."""
import datetime
import json

import urllib2

# Generate series of images between 0z and 12z on the 3rd of August


def main():
    """Go Main Go."""
    baseuri = "http://mesonet.agron.iastate.edu/GIS/radmap.php?layers[]=sbw&layers[]=places&layers[]=cities&layers[]=uscounties&bbox=-94.5,40.5,-92.5,43.5&layers[]=ridge&ridge_product=N0Q&ridge_radar=DMX&title=NWS%20Des%20Moines%20NEXRAD%20Base%20Ref&tz=America/Chicago&width=1024&height=768&ts="

    base = datetime.datetime(2015, 7, 24, 13)
    stepi = 0
    for day in range(24, 25):
        sts = datetime.datetime(2015, 7, day, 0, 0)
        ets = sts + datetime.timedelta(days=1)
        wsurl = (
            "http://mesonet.agron.iastate.edu/json/radar?operation=list&radar=DMX&product=N0Q&start=%s&end=%s"
            % (
                sts.strftime("%Y-%m-%dT%H:%MZ"),
                ets.strftime("%Y-%m-%dT%H:%MZ"),
            )
        )
        res = urllib2.urlopen(wsurl)
        j = json.loads(res.read())
        for scan in j["scans"]:
            valid = datetime.datetime.strptime(scan["ts"], "%Y-%m-%dT%H:%MZ")
            if valid < base:
                continue
            print(valid, stepi)
            uri = baseuri + valid.strftime("%Y%m%d%H%M")
            res = urllib2.urlopen(uri)
            image = open("images/%05i.png" % (stepi), "w")
            image.write(res.read())
            image.close()
            stepi += 1


if __name__ == "__main__":
    main()
