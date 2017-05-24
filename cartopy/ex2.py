from pyiem.plot import MapPlot

m = MapPlot(sector='nws')
#m.drawcounties()
#m.drawcities()
m.postprocess(filename='test.png')
