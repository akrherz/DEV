#!/usr/bin/env python

import datetime, os, shutil, urllib2, json

# Generate series of images between 0z and 12z on the 3rd of August

baseuri = "http://iem.local/GIS/radmap.php?layers[]=places&layers[]=cities&layers[]=uscounties&bbox=-80.2,41.8,-77.8,43.7&layers[]=ridge&ridge_product=N0Q&ridge_radar=BUF&title=NWS%20Buffalo%20NEXRAD%20Base%20Ref&tz=America/New_York&ts="

stepi = 0
for day in range(17, 22):
    sts = datetime.datetime(2014, 11, day, 0, 0)
    ets = sts + datetime.timedelta(days=1)
    wsurl = (
        "http://mesonet.agron.iastate.edu/json/radar?operation=list&radar=BUF&product=N0Q&start=%s&end=%s"
        % (sts.strftime("%Y-%m-%dT%H:%MZ"), ets.strftime("%Y-%m-%dT%H:%MZ"))
    )
    res = urllib2.urlopen(wsurl)
    j = json.loads(res.read())
    for scan in j["scans"]:
        valid = datetime.datetime.strptime(scan["ts"], "%Y-%m-%dT%H:%MZ")
        uri = baseuri + valid.strftime("%Y%m%d%H%M")
        res = urllib2.urlopen(uri)
        image = open("images/%05i.png" % (stepi), "w")
        image.write(res.read())
        image.close()
        stepi += 1
