# Generate a WEPP format cli file from NARR analysis
# Daryl Herzmann 1 Oct 2008

import mx.DateTime, math, sys
from Scientific.IO import NetCDF

sts = mx.DateTime.DateTime(1997, 1, 1)
ets = mx.DateTime.DateTime(2007, 1, 1)
interval = mx.DateTime.RelativeDateTime(days=1)


def k2f(thisk):
    return (9.00 / 5.00 * (float(thisk) - 273.15)) + 32.00


def k2c(thisk):
    return float(thisk) - 273.15


def figureXY(lon, lat):
    """  Figure out the x,y values of our point of interest :) """
    nc = NetCDF.NetCDFFile("/mnt/nrel/cjames/NARR/air.2m.2006.nc")
    xsz = nc.dimensions["x"]
    ysz = nc.dimensions["y"]
    lats = nc.variables["lat"]
    lons = nc.variables["lon"]
    res = 100000
    for i in range(xsz):
        for j in range(ysz):
            delta = math.sqrt(
                (lats[j, i][0] - lat) ** 2 + (lons[j, i][0] - lon) ** 2
            )
            if delta < res:
                res = delta
                minx = i
                miny = j

    return minx, miny


x, y = figureXY(float(sys.argv[2]), float(sys.argv[3]))

o = open("clifiles/%s.dat" % (sys.argv[1],), "w")

now = sts
while now < ets:
    # Load up the netcdf variables we need to do business
    # air:add_offset = 275.5f ;
    # air:scale_factor = 0.003799786f ;
    tmpk = NetCDF.NetCDFFile(
        "/mnt/nrel/cjames/NARR/air.2m.%s.nc" % (now.year,)
    ).variables["air"][:, y, x]

    # dpt:add_offset = 492.66f ;
    # dpt:scale_factor = 0.01f ;
    dwpk = NetCDF.NetCDFFile(
        "/mnt/nrel/cjames/NARR/dpt.2m.%s.nc" % (now.year,)
    ).variables["dpt"][:, y, x]

    #  Watts/per/meter sq
    #  dswrf:add_offset = 3041.6f ;
    #  dswrf:scale_factor = 0.1f ;
    solar = NetCDF.NetCDFFile(
        "/mnt/nrel/cjames/NARR/dswrf.%s.nc" % (now.year,)
    ).variables["dswrf"][:, y, x]

    #  apcp:add_offset = 50.f ;
    #  apcp:scale_factor = 0.001526019f ;
    precip = NetCDF.NetCDFFile(
        "/mnt/nrel/cjames/NARR/apcp.%s.nc" % (now.year,)
    ).variables["apcp"][:, y, x]

    # Loop over each day this year
    nextyear = now + mx.DateTime.RelativeDateTime(years=1)
    sts = now
    while now < nextyear:
        offset = int((now - sts).days)
        floor = offset * 8
        ceil = (offset + 1) * 8
        highc = k2c(max(tmpk[floor:ceil]) * 0.003799786 + 275.5)
        lowc = k2c(min(tmpk[floor:ceil]) * 0.003799786 + 275.5)
        dwpc = k2c(sum(dwpk[floor:ceil]) / 8.0 * 0.01 + 492.66)
        # Close enough for now
        langley = sum(solar[floor:ceil]) / 8.0 * 0.1 + 3041.6
        wmps = 10.0
        drct = 0.0
        # Now, ye lovely precip
        pticks = 0
        ptxt = ""
        rsum = 0
        i = 0
        for v in precip[floor:ceil]:
            if v > -32765:
                rsum += v * 0.00152 + 50
                ptxt += "%02i.75\t%.1f\n" % ((i + 1) * 3 - 1, rsum)
                pticks += 1
            i += 1
        if pticks > 0:
            ptxt = "00.00\t0.00\n" + ptxt
            pticks += 1
        if rsum < 5:
            ptxt = ""
            pticks = 0
        o.write(
            "%s\t%s\t%s\t%s\t%3.1f\t%3.1f\t%4.0f\t%4.1f\t%s\t%4.1f\n%s"
            % (
                now.day,
                now.month,
                now.year,
                pticks,
                highc,
                lowc,
                langley,
                wmps,
                drct,
                dwpc,
                ptxt,
            )
        )
        now += interval

o.close()
