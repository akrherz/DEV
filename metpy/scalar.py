from metpy.units import units
from metpy.calc import wind_direction, wind_components

wdir = wind_direction(5.0 * units("m/s"), 0.0 * units("m/s"))
print("wdir.m type is: %s" % (type(wdir.m),))

u, v = wind_components(5.0 * units("m/s"), 0.0 * units("degree"))
print("u.m type is: %s" % (type(u.m),))
