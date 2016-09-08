#!/usr/bin/env python

import datetime, os, shutil, urllib2, json

# Generate series of images between 0z and 12z on the 3rd of August

baseuri = "http://mesonet.agron.iastate.edu/GIS/radmap.php?layers[]=goes&goes_sector=EAST&goes_product=VIS&&layers[]=uscounties&bbox=-96.5,38.5,-90.5,45.5&title=GOES%20East%20Visible&tz=America/Chicago&width=1024&height=768&ts="

sts = datetime.datetime(2015, 7, 24, 11)
ets = datetime.datetime(2015, 7, 25, 2)
interval = datetime.timedelta(minutes=15)
stepi = 0
while sts < ets:
    print sts, stepi
    uri = baseuri + sts.strftime("%Y%m%d%H%M")
    res = urllib2.urlopen( uri )
    image = open('images/%05i.png' % (
                       stepi), 'w')
    image.write( res.read() )
    image.close()
    stepi += 1
    sts += interval

