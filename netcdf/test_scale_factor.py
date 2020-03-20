"""Testing scale_factor and ushort type"""
import os
import unittest

import numpy as np
import netCDF4


class TestScaleFactor(unittest.TestCase):
    def setUp(self):
        """Create a test netcdf file"""
        self.testfn = "/tmp/test.nc"  # hack
        nc = netCDF4.Dataset(self.testfn, "w")
        nc.createDimension("x", 10)
        ncvar = nc.createVariable("ncvar", np.ushort, ("x",))
        ncvar.scale_factor = 0.01
        ncvar.add_offset = 0.0
        nc.close()

    def tearDown(self):
        """remove the test file, if it exists"""
        if os.path.isfile(self.testfn):
            os.unlink(self.testfn)

    def test_autoscale_false(self):
        """Does our round trip work with autoscale off"""
        writing = 150.5
        expecting = 150.0

        nc = netCDF4.Dataset(self.testfn, "a")
        nc.set_auto_scale(False)
        nc.variables["ncvar"][5] = writing
        nc.close()

        nc = netCDF4.Dataset(self.testfn, "r")
        nc.set_auto_scale(False)
        self.assertEquals(nc.variables["ncvar"][5], expecting)
        nc.close()

    def test_autoscale_true(self):
        """Does our round trip work with autoscale on"""
        writing = 150
        expecting = 150

        nc = netCDF4.Dataset(self.testfn, "a")
        nc.set_auto_scale(True)
        nc.variables["ncvar"][5] = writing
        nc.close()

        nc = netCDF4.Dataset(self.testfn, "r")
        nc.set_auto_scale(True)
        self.assertAlmostEqual(nc.variables["ncvar"][5], expecting, 1)
        nc.close()
