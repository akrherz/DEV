"""test scale factor"""
from __future__ import print_function
import netCDF4
import numpy as np


def create_file():
    """Create"""
    nc = netCDF4.Dataset('test.nc', 'w')
    nc.createDimension('x', 10)
    ncvar = nc.createVariable('ncvar', np.ushort, ('x', ))
    ncvar.scale_factor = 100.
    ncvar.add_offset = 0.
    nc.close()


def write_data():
    """Write"""
    nc = netCDF4.Dataset('test.nc', 'a')
    nc.set_auto_maskandscale(True)
    nc.variables['ncvar'][5] = 1.5
    nc.close()

    nc = netCDF4.Dataset('test.nc', 'a')
    nc.set_auto_maskandscale(False)
    nc.variables['ncvar'][6] = 150.5
    nc.close()


def read_file():
    """Read"""
    nc = netCDF4.Dataset('test.nc', 'r')
    nc.set_auto_maskandscale(True)
    print("read[5] resulted in %s" % (nc.variables['ncvar'][5],))
    print("read[6] resulted in %s" % (nc.variables['ncvar'][6],))
    nc.close()

    nc = netCDF4.Dataset('test.nc', 'r')
    nc.set_auto_maskandscale(False)
    print("readv2[5] resulted in %s" % (nc.variables['ncvar'][5],))
    print("readv2[6] resulted in %s" % (nc.variables['ncvar'][6],))
    nc.close()


def main():
    """Go Main"""
    create_file()
    write_data()
    read_file()


if __name__ == '__main__':
    main()
