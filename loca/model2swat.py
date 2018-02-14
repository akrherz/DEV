"""Dump regcm4 data to SWAT files

We had a discussion on using the 0z to 0z summary data or computing 6z to 6z
totals from the 3-hourly or hourly files.  We appear to be going with the
6z to 6z option

The SRF files contain the following. For most runs they are written every 3
hours but recently I have been specifying 1 hour frequency:

surface (10 m) u wind (uas), instantaneous
surface (10 m) v wind (vas), instantaneous
surface (2 m) specific humidity (qas), instantaneous
surface (2 m) temperature (tas), instantaneous
time mean precipitation rate (pr)
time mean incident SW (rsds)
time mean net SW, i.e. incident minus reflected (rsns)

/opt/miniconda2/bin/ncrcat -v uas regcm4_erai_12km_SRF.*.nc
    ../singlevar/regcm4_erai_12km_uas.nc

tasmax and tasmin
-----------------
/opt/miniconda2/bin/ncra -O --mro -d time,6,,24,24 -v tas -y min
    regcm4_erai_12km_tas.????.nc ../daily6z/regcm4_erai_12km_tasmin.nc
/opt/miniconda2/bin/ncra -O --mro -d time,6,,24,24 -v tas -y max
    regcm4_erai_12km_tas.????.nc ../daily6z/regcm4_erai_12km_tasmax.nc

precip
------
/opt/miniconda2/bin/ncra -O --mro -d time,6,,24,24 -v pr -y avg
    regcm4_erai_12km_pr.????.nc ../daily6z/regcm4_erai_12km_pr.nc


wind
----
/opt/miniconda2/bin/ncks -A regcm4_erai_12km_uas.1989.nc
    regcm4_erai_12km_vas.1989.nc
mv regcm4_erai_12km_vas.1989.nc regcm4_erai_12km_uas_vas.1989.nc
rm regcm4_erai_12km_uas.1989.nc
# the -6 appears to allow it to even work
/opt/miniconda2/bin/ncap2 -6 -O -s 'sped=sqrt(pow(uas,2)+pow(vas,2))'
    regcm4_erai_12km_uas_vas.1989.nc regcm4_erai_12km_sped.1989.nc

"""
from __future__ import print_function
import sys
import datetime

from tqdm import tqdm
import netCDF4

BASEDIR = "/mnt/nrel/akrherz/DEV/loca"


def get_basedate(ncfile):
    """Compute the dates that we have"""
    nctime = ncfile.variables['time']
    basets = datetime.datetime.strptime(nctime.units,
                                        "days since %Y-%m-%d 00:00:00")
    ts = basets + datetime.timedelta(days=float(nctime[0]))
    return datetime.date(ts.year, ts.month, ts.day), len(nctime[:])


def main(argv):
    """Go Main Go"""
    model = "bcc-csm1-1-m_r1i1p1_rcp85"
    tasmax_nc = netCDF4.Dataset("%s/tasmax_%s.nc" % (BASEDIR, model))
    tasmin_nc = netCDF4.Dataset("%s/tasmin_%s.nc" % (BASEDIR, model))
    pr_nc = netCDF4.Dataset("%s/pr_%s.nc" % (BASEDIR, model))

    basedate, timesz = get_basedate(pr_nc)
    for i, lon in enumerate(tqdm(pr_nc.variables['lon'][:])):
        for j, lat in enumerate(pr_nc.variables['lat'][:]):
            pcpfp = open('swatfiles/%.4f_%.4f.pcp' % (lon - 360., lat), 'wb')
            tmpfp = open('swatfiles/%.4f_%.4f.tmp' % (lon - 360., lat), 'wb')
            pcpfp.write("""model %s



""" % (model, ))
            tmpfp.write("""model %s



""" % (model, ))
            tasmax = tasmax_nc.variables['tasmax_%s' % (model, )][:, j, i]
            tasmin = tasmin_nc.variables['tasmin_%s' % (model, )][:, j, i]
            pr = pr_nc.variables['pr_%s' % (model, )][:, j, i]
            for k in range(timesz):
                date = basedate + datetime.timedelta(days=k)
                pcpfp.write(("%s%03i%5.1f\n"
                             ) % (date.year, float(date.strftime("%j")),
                                  pr[k]))
                tmpfp.write(("%s%03i%5.1f%5.1f\n"
                             ) % (date.year, float(date.strftime("%j")),
                                  tasmax[k], tasmin[k]))

            pcpfp.close()
            tmpfp.close()


if __name__ == '__main__':
    main(sys.argv)
