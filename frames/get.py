#!/usr/bin/env python

import datetime, os, shutil

# Generate series of images between 0z and 12z on the 3rd of August
now = datetime.datetime(2012,1,1,0,0)
ets = datetime.datetime(2012,1,2,0,0)
interval = datetime.timedelta(minutes=15)

baseuri = "http://mesonet.agron.iastate.edu/GIS/radmap.php?"
#baseuri += "width=720&height=486&layers[]=goes&goes_sector=EAST&goes_product=IR&bbox=-97.75774,17.5,-73.43659,45.445455"
baseuri += "width=720&height=486&layers[]=goes&goes_sector=WEST&goes_product=IR&bbox=-132.05774,41.979636,-109.43659,50.445455"

# Change into a frames folder
os.chdir("frames")
stepi = 0
while (now < ets):
  #testfp = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ridge/DMX/N0U/DMX_N0U_%Y%m%d%H%M.png")
  #if os.path.isfile(testfp):
  url = "%s&ts=%s" % (baseuri, now.strftime("%Y%m%d%H%M"))
  #print url
  cmd = "wget -q -O %05i.png '%s'" % (stepi, url )
  os.system(cmd)
  #shutil.copyfile("%05i.png" % (stepi,), "%s.png" % (now.strftime("%H%M"),))
  stepi += 1
  now += interval

os.system("ffmpeg -y -r 2 -sameq -i %05d.png -b 24 out.mp4")
