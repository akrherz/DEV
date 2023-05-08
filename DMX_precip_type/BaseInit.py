################################################################################
# SVN: $Rev: 11242 $  $Date: 2016-12-20 15:19:05 +0000 (Tue, 20 Dec 2016) $
# $URL: https://collaborate.nws.noaa.gov/svn/scp/Gfe/Smartinits/NwsInitsConfig/tags/latest_stable/smartinits/BaseInit.py $
################################################################################
# BaseInit version of BaseInit created by BaseInit/make-BaseInit.sh
#
# This file is under NSI configuration management. DO NOT CHANGE
#  Copy methods you wish to change into the Local_BaseInit module and make desired
#  changes there.
#
import calendar
import time

import JSmartUtils
import siteConfig

# From: BaseInit.hdr
from Init import *
from numpy import *


class BaseInit(Forecaster):
    # From: BaseInit.__init__.py
    def __init__(self, srcName, dstName=None):
        Forecaster.__init__(self, srcName, dstName)
        self._siteID = siteConfig.GFESUITE_SITEID
        ## LogStream.logEvent("BaseInit: siteID:", self._siteID)
        # These are defaults. Sites can override via optionsDict
        self._CRtopoSites = ["RIW", "GJT", "PUB", "BOU", "CYS", "UNR"]
        self._WRtopoSites = [
            "BYZ",
            "TFX",
            "MSO",
            "PIH",
            "SLC",
            "FGZ",
            "TWC",
            "PSR",
            "VEF",
            "LKN",
            "BOI",
            "OTX",
            "PDT",
            "SEW",
            "PQR",
            "MFR",
            "REV",
            "EKA",
            "STO",
            "HNX",
            "MTR",
            "LOX",
            "SGX",
        ]
        self._SRtopoSites = ["ABQ", "EPZ", "MAF", "FFC", "MRX", "HUN", "OHX"]
        self._ERtopoSites = [
            "GSP",
            "RNK",
            "RLX",
            "LWX",
            "RLX",
            "PBZ",
            "CTP",
            "BUF",
            "BGM",
            "ALY",
            "BTV",
            "GYX",
            "CAR",
            "BOX",
        ]
        self._ARtopoSites = ["AFG", "AJK", "AFC"]
        self._topoSites = (
            self._CRtopoSites
            + self._WRtopoSites
            + self._SRtopoSites
            + self._ERtopoSites
            + self._ARtopoSites
        )
        ## LogStream.logEvent("self._topoSites:", self._topoSites)

        self._GreatLakeSites = [
            "DLH",
            "MQT",
            "APX",
            "GRB",
            "MKX",
            "LOT",
            "IWX",
            "CLE",
            "BUF",
            "GRR",
            "DTX",
        ]
        self._prismSites = [
            "AKQ",
            "ALY",
            "BGM",
            "BOX",
            "BTV",
            "BUF",
            "CAE",
            "CAR",
            "CHS",
            "CLE",
            "CTP",
            "GSP",
            "GYX",
            "ILM",
            "ILN",
            "LWX",
            "MHX",
            "OKX",
            "PBZ",
            "PHI",
            "RAH",
            "RLX",
            "RNK",
        ]

        # set up default options
        self.BI_optionsDict = {
            "topoSite": False,
            "prismSite": False,
            "GreatLakeSite": False,
            # used in BI_setupBLCube
            "useWetBulb": False,
            "HainesLevel": "MEDIUM",
            # used in BI_getQPFPct, likely to be model specific
            "ClimoQPFSmooth": 8,
            # used in MOS wind and gust computations
            "windLapseRate": 5.0 / 304.8,
            # Threshold used in BI_checkT, min T for snow
            "noSnowThresholdT": 40,
            # Smoothing when filling edit areas
            "SMOOTH_AFTER_FILL": True,
            # Used in BI_setupBLCube to define available BL levels
            "masterPdiff": [0, 30, 60, 90, 120, 150, 180, 210],
            # Used in BI_setupBLCube for how to add BL levels
            "interLeaveBL": False,
            # Used in BI_getSnowLevel to set up which method is used to calculate SnowLevel
            "snowLevelMethod": "BLEND",
            # Used in BI_getSnowLevel to extend the SnowLevel below the freezing level by the specified feet
            "snowLevelBelowFzLevel": 500,
        }

        if "ALL" in self._topoSites or self._siteID in self._topoSites:
            self.BI_optionsDict["topoSite"] = True
        if "ALL" in self._prismSites or self._siteID in self._prismSites:
            self.BI_optionsDict["prismSite"] = True
        if self._siteID in self._GreatLakeSites:
            self.BI_optionsDict["GreatLakeSite"] = True
        if (
            self._siteID in self._WRtopoSites
            or self._siteID in self._SRtopoSites
        ):
            self.BI_optionsDict["HainesLevel"] = "HIGH"
            self.BI_optionsDict["windLapseRate"] = 2.5 / 304.8

        # Note these were from ER
        #  Get ready to track time of boundary layer cube
        self.BLcubeTime = (None, None)

        if self.BI_optionsDict["prismSite"] or self.BI_optionsDict["topoSite"]:
            self.BI_setupClimoQPF()

    # From: ../../methods/alterArea/BaseInit.alterArea.py
    # ===============================================================
    #  Expands or contracts area of array. Area must be ones and
    #  zeros with the operation performed on the area of ones.
    #
    def alterArea(self, array, k):
        negative = 0

        if k < 0:
            k = abs(k)
            negative = 1
            # Invert mask
            array = where(greater(array, 0), 0, 1)

        if k > 0:
            a = array * 0.0
            n = array * 0.0
            for x in range(-k, k + 1):
                for y in range(-k, k + 1):
                    array1 = self.BI_offset(array, x, y)
                    ok = greater(array1, -9000)
                    a = where(ok, a + array1, a)
                    n = where(ok, n + 1, n)
            a = where(less(n, 1), array, a)
            n = where(less(n, 1), 1, n)
            arraysmooth = greater((a / n), 0)
        else:
            arraysmooth = array

        if negative == 1:
            arraysmooth = where(greater(arraysmooth, 0), 0, 1)

        return arraysmooth

    # From: ../../methods/BI_appendBoundaryLayers/BI_appendBoundaryLayers.py
    def BI_appendBoundaryLayers(
        self,
        blTemps,
        blRH,
        blWinds,
        p_SFC,
        stopo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        pdiff,
    ):
        """Create boundary layer cube - cube of values above model surface.
        Adds in pressure level data above the boundary layer fields
           creates:
              BLT - temperatures (K)
              BLR - relative humidity (% 0-100)
              BLH - height (m)
              BLP - pressure (mb)
              BLW - wind (magnitude kts, direction)
              BLD - dewpoint (K)
              BLE - wetbulb (K) [if desired]
        """
        #
        #  split pressure level wind cube into magnitude and direction
        #
        mag_c = wind_c[0]
        dir_c = wind_c[1]
        dew_c = self.RHDP(t_c - 273.15, rh_c) + 273.15
        # Initilialize lists of grids going up with lowest (first) BL grid.
        pSFCmb = p_SFC / 100.0
        pSFCmb = where(less(pSFCmb, 500.0), 1013.0, pSFCmb)
        p_list = [pSFCmb]
        hbot = stopo
        h_list = [hbot]
        t_list = [blTemps[0]]
        r_list = [clip(blRH[0], 0.0001, 99.999)]
        m_list = [blWinds[0][0]]
        d_list = [blWinds[0][1]]
        w_list = [self.RHDP(blTemps[0] - 273.15, r_list[0]) + 273.15]

        for i in range(1, len(blTemps)):
            tavg = blTemps[i]
            tavgc = tavg - 273.15
            ravg = clip(blRH[i], 0.0001, 99.999)
            davgc = self.RHDP(tavgc, ravg)
            ptop = clip(pSFCmb - pdiff[i], 1.0, 1050.0)
            pbot = clip(pSFCmb - pdiff[i - 1], 1.0, 1050.0)
            htop = self.BI_MHGT(tavgc, davgc, ptop, pbot, hbot)

            t_list.append(tavg)
            h_list.append((hbot + htop) / 2.0)
            wind = blWinds[i]
            m_list.append(wind[0])
            d_list.append(wind[1])
            p_list.append((pbot + ptop) / 2.0)
            r_list.append(ravg)
            w_list.append(davgc + 273.15)

            hbot = htop
        #
        #  above the boundary layer...add levels in pressure
        #  cube
        #
        numplevs = gh_c.shape[0]
        levstoadd = self.empty()
        for i in range(numplevs):
            levstoadd = where(greater(gh_c[i], hbot), levstoadd + 1, levstoadd)
        maxtoadd = maximum.reduce(maximum.reduce(levstoadd))
        for j in range(int(maxtoadd)):
            found = self.empty()
            hlev = found
            tlev = found
            mlev = found
            dlev = found
            plev = found
            rlev = found
            wlev = found
            for i in range(numplevs):
                usethislev = logical_and(
                    less(found, 0.5), greater(gh_c[i], hbot)
                )
                hlev = where(usethislev, gh_c[i], hlev)
                plev = where(usethislev, self.pres[i], plev)
                tlev = where(usethislev, t_c[i], tlev)
                mlev = where(usethislev, mag_c[i], mlev)
                dlev = where(usethislev, dir_c[i], dlev)
                rlev = where(usethislev, rh_c[i], rlev)
                wlev = where(usethislev, dew_c[i], wlev)
                found = where(usethislev, 1.0, found)
                numNotFound = add.reduce(add.reduce(less(found, 0.5)))
                if numNotFound < 1:
                    break
            if numNotFound > 0:
                hlev = where(less(found, 0.5), gh_c[numplevs - 1], hlev)
                plev = where(less(found, 0.5), self.pres[numplevs - 1], plev)
                tlev = where(less(found, 0.5), t_c[numplevs - 1], tlev)
                mlev = where(less(found, 0.5), mag_c[numplevs - 1], mlev)
                dlev = where(less(found, 0.5), dir_c[numplevs - 1], dlev)
                rlev = where(less(found, 0.5), rh_c[numplevs - 1], rlev)
                wlev = where(less(found, 0.5), dew_c[numplevs - 1], wlev)
            h_list.append(hlev)
            t_list.append(tlev)
            p_list.append(plev)
            m_list.append(mlev)
            d_list.append(dlev)
            r_list.append(rlev)
            w_list.append(wlev)
            hbot = hlev

        self.BI_BLH = array(h_list)
        self.BI_BLP = array(p_list)
        self.BI_BLT = array(t_list)
        self.BI_BLR = array(r_list)
        mags = array(m_list)
        dirs = array(d_list)
        self.BI_BLW = (mags, dirs)
        self.BI_BLD = array(w_list)
        if self.BI_optionsDict.get("useWetBulb", False):
            self.BI_BLE = self.Wetbulb(
                self.BI_BLT - 273.15, self.BI_BLR, self.BI_BLP
            )
        self.BLcubeTime = ctime
        return

    # From: ../../methods/BI_adjustIsobaricCubes/BI_adjustIsobaricCubes.py
    def BI_adjustIsobaricCubes(
        self,
        BLP,
        BLT,
        BLD,
        BLH,
        blLevel,
        modelP_c,
        t_c,
        modelTd_c,
        rh_c,
        gh_c,
        isobaric,
        intersect,
    ):
        # -----------------------------------------------------------------------
        #  Adjust the height of this isobaric level

        gh_c[isobaric][intersect] = (
            BLH[blLevel]
            + self.BI_calcDeltaZ(
                BLT[blLevel],
                BLD[blLevel],
                BLP[blLevel],
                modelP_c[isobaric] - BLP[blLevel],
            )
        )[intersect]

        # -----------------------------------------------------------------------
        #  Now adjust the temperature of this isobaric level

        #  See if there are any points we need to correct at this isobaric level
        #  which are above the boundary layer
        aboveBLcube = (modelP_c[isobaric] < BLP[-1]) & intersect

        #  Interpolate the temperatures within the boundary layer cube first
        t_c[isobaric][intersect] = self.linear(
            BLH[blLevel - 1],
            BLH[blLevel],
            BLT[blLevel - 1],
            BLT[blLevel],
            gh_c[isobaric],
        )[intersect]

        #  If there are any points which need to be corrected above the boundary
        #  layer cube, interpolate between the top of the BL and the isobaric
        #  level above this one
        if aboveBLcube.any():
            t_c[isobaric][aboveBLcube] = self.linear(
                BLH[blLevel],
                gh_c[isobaric + 1],
                BLT[blLevel],
                t_c[isobaric + 1],
                gh_c[isobaric],
            )[aboveBLcube]

        # -----------------------------------------------------------------------
        #  Adjust the isobaric dewpoint temperature at these points

        #  Interpolate the dewpoints within the boundary layer cube first
        modelTd_c[isobaric][intersect] = self.linear(
            self.BI_BLH[blLevel - 1],
            self.BI_BLH[blLevel],
            self.BI_BLD[blLevel - 1],
            self.BI_BLD[blLevel],
            gh_c[isobaric],
        )[intersect]

        #  If there are any points which need to be corrected above the boundary
        #  layer cube, interpolate between the top of the BL and the isobaric
        #  level above this one
        if aboveBLcube.any():
            modelTd_c[isobaric][aboveBLcube] = self.linear(
                BLH[blLevel],
                gh_c[isobaric + 1],
                BLD[blLevel],
                modelTd_c[isobaric + 1],
                gh_c[isobaric],
            )[aboveBLcube]

        # -----------------------------------------------------------------------
        #  Adjust the relative humidity at these points

        rh_c[isobaric][intersect] = (
            100.0 * self.esat(modelTd_c[isobaric]) / self.esat(t_c[isobaric])
        )[intersect]

        #  Return adjusted cubes
        return t_c, modelTd_c, rh_c, gh_c

    # From: ../../methods/BI_applyTopoT/BI_applyTopoT.py
    # ===========================================================================
    #  BI_applyTopoT - compute temperature at MOS time step.  Can optionally apply
    #  a topographic adjustment developed by Eric Thaler (SOO BOU).
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #  a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_applyTopoT(self, grid, stopo, topo):
        #  Define lapse rate of temperature per thousand feet (304.8 m)
        t_lapse_rate = 2.0 / 304.8

        #  Try to determine the difference between model topography and
        #  the real topography
        topoDiff = self.BI_getMosTopoDiff(stopo, topo)

        #  Apply lapse rate correction where real topo is above model topo
        mask = topoDiff > 0.0
        grid[mask] = (grid + (t_lapse_rate * topoDiff))[mask]

        #  Return completed temperature
        return grid

    # From: ../../methods/BI_baseSnowRatio/BI_baseSnowRatio.py
    ################################################################################
    #  Methods dealing with snow accumulation
    ################################################################################

    # ===========================================================================
    #  BI_baseSnowRatio - Method to compute snow:liquid ratio based on a spline
    #  curve defined at temperature (deg C) anchor points.
    # ===========================================================================
    def BI_baseSnowRatio(self, tGrid):
        #  Define temperature thresholds
        tThresh = [
            -30.0,
            -21.0,
            -18.0,
            -15.0,
            -12.0,
            -10.0,
            -8.0,
            -5.0,
            -3.0,
            2.0,
        ]

        #  Define polynomial coefficients for each temperature threshold
        a = [9.0, 21.0, 31.0, 35.0, 26.0, 15.0, 9.0, 5.0, 4.0]
        b = [
            0.4441,
            3.1119,
            2.8870,
            -0.6599,
            -5.2475,
            -4.5685,
            -1.9786,
            -0.7544,
            -0.3329,
        ]
        c = [
            0.0,
            0.2964,
            -0.3714,
            -0.8109,
            -0.7183,
            1.0578,
            0.2372,
            0.1709,
            0.0399,
        ]
        d = [
            0.0110,
            -0.0742,
            -0.0488,
            0.0103,
            0.2960,
            -0.1368,
            -0.0074,
            -0.0218,
            -0.0027,
        ]

        #  Initialize a grid to track which temperature threshold to use
        tDiff = self.empty()

        #  Initialize each coefficient grid with the last possible value
        aGrid = tDiff.copy() + a[-1]  #  last value in list
        bGrid = tDiff.copy() + b[-1]
        cGrid = tDiff.copy() + c[-1]
        dGrid = tDiff.copy() + d[-1]

        #  Determine which coefficients to use at each point
        for i in range(len(tThresh) - 1):
            mask1 = greater_equal(tGrid, tThresh[i])
            mask2 = less(tGrid, tThresh[i + 1])
            mask = logical_and(mask1, mask2)  # area b/w threshold
            tDiff = where(mask, tGrid - tThresh[i], tDiff)
            aGrid = where(mask, a[i], aGrid)
            bGrid = where(mask, b[i], bGrid)
            cGrid = where(mask, c[i], cGrid)
            dGrid = where(mask, d[i], dGrid)

        #  Compute final snow ratio based upon temperature
        baseRatio = (
            aGrid
            + (bGrid * tDiff)
            + (cGrid * tDiff * tDiff)
            + (dGrid * pow(tDiff, 3))
        )

        #  Ensure snow ratio is zero at temperatures above 4.5C
        baseRatio = where(greater_equal(tGrid, 4.5), 0.0, baseRatio)

        return baseRatio

    # From: ../../methods/BI_baseSnowRatioWR/BI_baseSnowRatioWR.py
    # ====================================================================
    ### Given a grid of temperature in Celcius, this method computes
    ### the base snowRatio based on research done in WR by Trevor Alcott.
    def BI_baseSnowRatioWR(self, tGrid, wGrid):
        #  set up the spline coefficients
        tThresh = [-25.0, -20.0, -15.0, -10.0, -5.0, 0.0]
        SLR = [15, 19, -25, -15, -8, 5]
        slope = [0.8, 1.2, 2, 1.4, 0.6, 0]

        # Initialize the grid
        sRatio = self.newGrid(15.0)
        sRatio = where(greater_equal(tGrid, 0), 5, sRatio)

        # define grids based on tGrid
        for i in range(len(tThresh) - 1):
            mask1 = greater(tGrid, tThresh[i])
            mask2 = less_equal(tGrid, tThresh[i + 1])
            mask = logical_and(mask1, mask2)  # area b/w threshold
            calcT = abs(SLR[i] + (tGrid - tThresh[i]) * slope[i])
            sRatio = where(mask, calcT, sRatio)

        wThresh = [12, 17, 25]
        wMult = [0.05, 0.03]
        # If wind is greater than 25 meters/sec cut the snow ratio in half.
        sRatio = where(greater(wGrid, 25), sRatio * 0.5, sRatio)

        # decrease snow ratio due to wind speed
        for i in range(len(wThresh) - 1):
            mask1 = greater(wGrid, wThresh[i])
            mask2 = less_equal(wGrid, wThresh[i + 1])
            mask = logical_and(mask1, mask2)  # area b/w threshold
            calcW = sRatio * (wThresh[i] - wGrid) * wMult[i]
            sRatio = where(mask, calcW, sRatio)
        return sRatio

    # From: ../../methods/BI_calcDeltaZ/BI_calcDeltaZ.py
    def BI_calcDeltaZ(self, temp, dewPoint, pressure, deltaP):
        #  Ensure temperature inputs are in Kelvin
        temp[temp < 100] += 273.15
        dewPoint[dewPoint < 100] += 273.15

        Rdry = 287.058  #  gas constant for dry air (J/kg)
        gravity = 9.80665  #  m / s^2

        #  First, compute the virtual temperature of the air at this level
        Tv = self.BI_TVRT(temp - 273.15, dewPoint - 273.15, pressure)

        #  Ensure the virtual temperature is in Kelvin before we use it
        Tv[Tv < 100] += 273.15

        #  Now, compute the expected change in height moving this air to a new
        #  pressure level using the hypsometric and ideal gas law equations
        return -1.0 * (deltaP * Rdry * Tv) / (pressure * gravity)

    # From: ../../methods/BI_calcMarineScalar/BI_calcMarineScalar.py
    ################################################################################
    #  Methods dealing with marine parameters
    ################################################################################

    # ===========================================================================
    #  Method to calculate marine scalar fields - fill in missing data and
    #  mask as needed
    # ===========================================================================
    def BI_calcMarineScalar(
        self,
        grid,
        fillMasks=[],
        mask=None,
        maskValue=0.0,
        minValue=0.0,
        filterValue=50.0,
    ):
        #  Filter out everything above filter value
        grid = where(greater(grid, filterValue), minValue, grid)

        #  Fill in any data void areas
        grid = self.BI_fillScalar(grid, fillMasks)

        #  If a mask was supplied
        if mask is not None:
            #  Apply it to data
            return where(mask, grid, maskValue)

        #  Otherwise, just return what we have
        else:
            return grid

    # From: ../../methods/BI_calcMarineVector/BI_calcMarineVector.py
    # ===========================================================================
    #  Method to calculate marine vector fields - fill in missing data and
    #  mask as needed
    # ===========================================================================
    def BI_calcMarineVector(
        self,
        gridMag,
        gridDir,
        fillMasks=[],
        mask=None,
        maskValue=0.0,
        minValue=0.0,
        filterValue=50.0,
    ):
        #  Convert magnitude from m to ft - filtering out everything above
        #  filter value
        gridMag = where(greater(gridMag, filterValue), minValue, gridMag)

        #  Fill in any data void areas
        self.BI_fillVector((gridMag, gridDir), fillMasks)

        #  If a mask was supplied
        if mask is not None:
            #  Apply it to data
            gridMag = where(mask, gridMag, maskValue)
            gridDir = where(mask, gridDir, 0)

        #  Ensure the direction is valid
        gridDir = clip(gridDir, 0.0, 359.5)

        #  Return the completed marine vector
        return (gridMag, gridDir)

    # From: ../../methods/BI_calcMaxT/BI_calcMaxT.py
    # ===========================================================================
    #  MaxT and MinT - max and min of hourly Ts, optionally can apply an offset
    #  to hourly T (higher for MaxT and lower for MinT)
    # ===========================================================================
    def BI_calcMaxT(
        self, T, MaxT, mtime, modelSfcT=None, modelMaxT=None, offset=0
    ):
        #  If we have raw model temperatures
        if modelSfcT is not None and modelMaxT is not None:
            #  Compute a difference between the temperatures we can apply
            #  to the previously downscaled temperature
            #  (don't forget we need to account for differences between
            #   degrees C and degrees F)
            diff = 0.5 + (modelMaxT - modelSfcT) * 9.0 / 5.0

        #  otherwise, do nothing
        else:
            diff = self.empty()

        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids(
                "MaxT", T + diff + offset, "T", mtime, None
            )
        except:
            pass

        #  If the MaxT grid is missing so far
        if MaxT is None:
            #  Use the current hourly T after applying any offset
            return T + diff + offset

        #  Otherwise, keep the highest temperature (after applying offset)
        return maximum(MaxT, T + diff + offset)

    # From: ../../methods/BI_calcMinT/BI_calcMinT.py
    def BI_calcMinT(
        self, T, MinT, mtime, modelSfcT=None, modelMinT=None, offset=0
    ):
        #  If we have raw model temperatures
        if modelSfcT is not None and modelMinT is not None:
            #  Compute a difference between the temperatures we can apply
            #  to the previously downscaled temperature
            #  (don't forget we need to account for differences between
            #   degrees C and degrees F)
            diff = 0.5 + (modelSfcT - modelMinT) * 9.0 / 5.0

        #  otherwise, do nothing
        else:
            diff = self.empty()
        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids(
                "MinT", T + diff - offset, "T", mtime, None
            )
        except:
            pass

        #  If the MinT grid is missing so far
        if MinT is None:
            #  Use the current hourly T after applying any offset
            return T + diff - offset

        #  Otherwise, keep the lowest temperature (after applying offset)
        return minimum(MinT, T + diff - offset)

    # From: ../../methods/BI_calcMixHgt/BI_calcMixHgt.py
    ################################################################################
    #  Methods dealing with fire weather parameters
    ################################################################################

    # ===========================================================================
    #  BI_calcMixHgt - calculate the mixing height
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcMixHgt(self, T, t_FHAG2, p_SFC, topo, fillMasks=[], MSLP=0):
        #  Convert surface pressure to mb (100 hPa = 1 mb)
        sfcPressure = p_SFC / 100.0

        #  If the pressure passed in is a MSL pressure
        if MSLP == 1:
            #  Compute the station pressure instead
            sfcPressure = self.BI_stnPres(sfcPressure, t_FHAG2, topo)

        # Make copies of the boundary layer data
        BLT = self.BI_BLT
        BLH = self.BI_BLH
        BLP = self.BI_BLP

        BLTheta = self.ptemp(BLT, BLP)

        ##        topoDiff = topo - stopo
        ##        thetaToFind = (t_FHAG2 + 2.0) - ( t_FHAG2 + (0.00976 * topoDiff) )
        ##        thetaToFind = where(logical_and(greater_equal(topoDiff, 250 * 0.3048),
        ##                                        greater_equal(thetaToFind, 0.0)),
        ##                             thetaToFind, 0.0)
        #
        #  Potential temp of fire 2 degrees warmer than surface parcel
        #
        fireHeat = 1.5
        fireTheta = self.ptemp(t_FHAG2 + fireHeat, sfcPressure)
        #
        #  Find height the fireTheta crosses the sounding theta
        #
        mixhgt = self.newGrid(-1.0)
        for i in range(1, BLH.shape[0]):
            hcross = self.linear(
                BLTheta[i], BLTheta[i - 1], BLH[i], BLH[i - 1], fireTheta
            )
            cross = logical_and(
                greater(BLTheta[i], fireTheta), less(mixhgt, 0.0)
            )

            #  Check the resulting computed mixing height, it cannot be greater
            #  than the height of the top of the current layer AGL
            hcross = where(greater(hcross, BLH[i]), BLH[i], hcross)

            #  Assign the mixing height, where it is ready to be set
            mixhgt = where(cross, hcross, mixhgt)

        #  Set any remaining points in the domain which need to be set, to the
        #  height of the heighest height in the cube
        mixhgt = where(less(mixhgt, 0.0), BLH[-1], mixhgt)
        #
        #  Change to height above the model topo (in feet)
        #  and smooth a little
        #
        final = (mixhgt - topo) * 3.2808
        final = where(less(sfcPressure, 500.0), -9999.0, final)
        final = self.BI_smoothpm(final, 2)
        final = clip(final, 0.0, 50000.0)
        return final

    # From: ../../methods/BI_calcMosWind/BI_calcMosWind.py
    # ===========================================================================
    #  BI_calcMosWind - compute wind at MOS time step.  Can optionally apply a
    #  topographic adjustment developed by Eric Thaler (SOO BOU).
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #  a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcMosWind(self, swind, stopo, topo, applyTopo=0, fillMasks=[]):
        #  Separate the surface wind into its polar coordinates
        (wmag, wdir) = swind

        #  Convert wind speed from m/s to knots
        wmag = self.convertMsecToKts(wmag)

        # -----------------------------------------------------------------------
        #  If we are going to apply a topographic correction to the MOS

        if applyTopo:
            #  Define lapse rate of wind speed (KT) per thousand feet (304.8 m)
            spd_lapse_rate = self.BI_optionsDict["windLapseRate"]

            #  Try to determine the differrence between model topography and
            #  the real topography
            topoDiff = self.BI_getMosTopoDiff(stopo, topo)

            #  Apply lapse rate correction where real topo is above model topo
            wmag = where(
                greater(topoDiff, 0.0),
                wmag + (spd_lapse_rate * topoDiff),
                wmag,
            )

        #  Smooth this grid a little
        ##        wmag = self.BI_smoothpm(wmag, 1)
        ##        wdir = self.BI_smoothpm(wdir, 1)

        #  Return completed wind, after filling in any data void areas
        #  (as needed)
        return self.BI_fillVector((wmag, wdir), fillMasks)

    # From: ../../methods/BI_calcMosWindGust/BI_calcMosWindGust.py
    # ===========================================================================
    #  BI_calcWindGust - compute wind gust speed at MOS time step
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcMosWindGust(
        self, gust, wmag, stopo, topo, applyTopo=0, fillMasks=[]
    ):
        #  Convert speed from m/s to to knots
        gust = self.convertMsecToKts(gust)

        # -----------------------------------------------------------------------
        #  If we are going to apply a topographic correction to the MOS

        if applyTopo:
            #  Define lapse rate of wind speed (KT) per thousand feet (304.8 m)
            spd_lapse_rate = self.BI_optionsDict["windLapseRate"]

            #  Try to determine the differrence between model topography and
            #  the real topography
            topoDiff = self.BI_getMosTopoDiff(stopo, topo)

            #  Apply lapse rate correction where real topo is above model topo
            gust = where(
                greater(topoDiff, 0.0),
                gust + (spd_lapse_rate * topoDiff),
                gust,
            )

        #  Fill in any data void areas
        gust = self.BI_fillScalar(gust, fillMasks)

        #  Ensure wind gust is at least 1 kt higher than sustained wind speed
        gust = where(less_equal(gust, wmag), wmag + 1.0, gust)

        #  Return the completed wind gust
        return gust

    # From: ../../methods/BI_calcPredHgtRH/BI_calcPredHgtRH.py
    # ===========================================================================
    #  BI_calcPredHgtRH -
    # ===========================================================================
    def BI_calcPredHgtRH(self, gh_c, rh_c, topo):
        #  Define RH threhold which indicates a cloud for each level
        cloudRH = [
            98.0,
            96.0,
            94.0,
            92.0,
            90.0,  #  1000-900 mb (25 mb)
            88.0,
            85.0,
            83.0,
            80.0,
            78.0,  #  875-775 mb  (25 mb)
            75.0,
            73.0,
            70.0,
            68.0,
            65.0,  #  750-650 mb  (25 mb)
            63.0,
            60.0,
            58.0,
            55.0,
            53.0,  #  625-525 mb  (25 mb)
            50.0,
            45.0,
            40.0,
            35.0,
            30.0,  #  500-300 mb  (50 mb)
        ]
        #  Define the maximum cloud base in hundreds of feet
        MaxCloudBase = 250

        #  Convert geopotential heights at all levels to be AGL
        gh_c - topo

        #  Mask the RH cube where it is below ground level
        where(less_equal(gh_c, 0), 0, rh_c)

        #  Get ready to find the cloud heights - start with max cloud level
        #  (in 100s of feet)
        cloudBaseHgt = self.newGrid(MaxCloudBase)

        # -----------------------------------------------------------------------
        #  Look through all the vertical levels (from bottom up)
        for index in xrange(gh_c.shape[0]):
            #  Get the height in feet and RH for this level
            height = gh_c[index] / self.convertFtToM(1)
            rh = rh_c[index]

            #  Where the RH exceeds the threshold for clouds at this level,
            #  assign the current height as the cloud base in 100s of feet
            cloudBaseHgt = where(
                logical_and(
                    equal(cloudBaseHgt, MaxCloudBase),
                    greater_equal(rh, cloudRH[index]),
                ),
                height / 100,
                cloudBaseHgt,
            )

        #  Smooth this data before we categorize
        cloudBaseHgt = self.BI_SmoothGrid(cloudBaseHgt)

        #  Categorize these cloud heights
        cloudBaseHgt = self.BI_categorizeCloudHeight(cloudBaseHgt)

        #  Ensure final cloud base heights are valid
        cloudBaseHgt = clip(cloudBaseHgt, 1, MaxCloudBase)

        return cloudBaseHgt

    # From: ../../methods/BI_calcQPF/BI_calcQPF.py
    ################################################################################
    #  Methods dealing with liquid precipitation accumulation
    ################################################################################

    # ===========================================================================
    #  BI_calcQPF - simply take model QPF and change units to inches
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcQPF(self, qpf, fillMasks=[]):
        #  Remove really bad data
        qpf[qpf >= 1000.0] = 0.0

        #  Fill in any data void areas
        qpf = self.BI_fillScalar(qpf, fillMasks)

        #  Convert from millimeters to inches
        qpf = qpf / 25.4

        return qpf

    # From: ../../methods/BI_calcRH/BI_calcRH.py
    ################################################################################
    #  Methods to derive various RH fields
    ################################################################################

    # ===========================================================================
    #  BI_calcRH - simply calculate RH based on Temp and Dewpoint
    #  (both in K)
    # ===========================================================================
    def BI_calcRH(self, t, dpt, ctime):
        #  See if we are dealing with a cube, or a grid
        try:
            t[0, 0, 0]
            cube = True
            LogStream.logEvent("Dealing with a RH cube")
        except:
            cube = False
            LogStream.logEvent("Dealing with a RH grid")

        #  If this surface RH was likely already computed
        if (
            not cube
            and self._rh_FHAG2 is not None
            and ctime == self.BLcubeTime
        ):
            #  Keep it as is
            return self._rh_FHAG2

        #  Otherwise, if this RH cube was likely already computed
        elif cube and self._rh_c is not None and ctime == self.BLcubeTime:
            #  Keep it as is
            return self._rh_c

        #  If we made it this far, compute the RH we need (surface or cube)
        #  (temperatures must be in degrees C - so convert from K)
        if not cube:
            #  Surface RH
            self._rh_FHAG2 = 100.0 * (
                self.VAPR(dpt - 273.15) / self.VAPR(t - 273.15)
            )

            #  Store surface RH so we do not have to compute it again for this
            #  time step
            return self._rh_FHAG2
        else:
            #  RH cube
            self._rh_c = 100.0 * (
                self.VAPR(dpt - 273.15) / self.VAPR(t - 273.15)
            )
            #  Store RH cube so we do not have to compute it again for this
            #  time step
            return self._rh_c

    # From: ../../methods/BI_calcSky/BI_calcSky.py
    # ===========================================================================
    #  BI_calcSky - calculates Sky condition (fractional cloud cover) from
    #  model RH at specific pressure levels. Uses reduced equations from
    #  Walcek, MWR June 1994. Adds up the amount of fractional clouds calculated
    #  within each layer based on topography (i.e. no clouds below ground) then
    #  divides by a suggested number of layers to produce an average sky.
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcSky(
        self,
        blTemps,
        blRH,
        blWinds,
        p_SFC,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        MSLP=0,
        fillMasks=[],
    ):
        #  Setup the boundary layer cube for this time - if needed
        self.BI_setupBLCube(
            blTemps,
            blRH,
            blWinds,
            p_SFC,
            stopo,
            topo,
            gh_c,
            t_c,
            rh_c,
            wind_c,
            ctime,
            MSLP,
        )

        #  Make local references to boundary layer data for shorter notation
        BLR = self.BI_BLR
        BLP = self.BI_BLP

        #  Make a copy of surface pressure in millibars v. Pa
        tmpP_SFC = p_SFC.copy() / 100.0  # convert surfp to millibars
        x = 560.0  # delta x (85km - 850km)

        #  If the pressure passed in is a MSL pressure
        if MSLP == 1:
            #  Compute the station pressure instead
            tmpP_SFC = self.BI_stnPres(tmpP_SFC, blTemps[0], topo)

        #  Define a percentage of f100 to use as a filter (0.0 - 1.0)
        #  Remember f100 is an exponential function, so changes will be more
        #  pronounced in the 0.5-1.0 range than the 0.0-0.5 range.
        percent = 0.37

        #  compute the sigma level cube for AWIPS2
        newSigma_c = BLP / tmpP_SFC

        #  Determine maximum possible sky fraction
        fmax = 78.0 + x / 15.5

        #  Compute sky fraction for both pressure cubes
        f100 = where(
            less(newSigma_c, 0.7),
            fmax * (newSigma_c - 0.1) / 0.6,
            30.0 + (1.0 - newSigma_c) * (fmax - 30.0) / 0.3,
        )

        #  Compute RH depression at 37% f100 [ (1-RHe) in Walcek ]
        c = 0.196 + (0.76 - x / 2834.0) * (1.0 - newSigma_c)

        del newSigma_c

        #  Compute critical RH threshold to use as a filter
        #  Note (percent * f100)/f100 = percent
        try:
            rhCrit = log(percent) * c + 1.0
        except:
            rhCrit = self.empty()

        #  Ensure "critical RH" is valid
        rhCrit = clip(rhCrit, 0.0, 1.0)

        #  Compute sky fraction for the model cube
        c = ((BLR / 100.0) - 1.0) / c
        c = exp(c)
        f = minimum(f100 * c, 100.0)

        #  Where RH is less than critical value, assign a negligible
        #  contribution
        f[less(BLR / 100.0, rhCrit)] = 0.0

        #  Determine the number of levels
        numLevels = (f.shape[0] / 5) - 1

        #  Ensure we at least keep 5 levels
        if numLevels < 5:
            numLevels = 5

        #  Compress cube vertically
        ##        LogStream.logEvent("There are %d levels for sky." % (f.shape[0]))
        f = self.squishZ(f, numLevels)  #  was 5
        ##        LogStream.logEvent("Now there are %d levels for sky." % (f.shape[0]))

        #  Convert sky fractions to an actual percentage
        if len(f) >= 5:
            f[4] *= 0.25
        else:
            LogStream.logEvent(
                "WARNING: Sky data is missing some levels - "
                + "calculation will be incomplete"
            )
            ind = len(f) - 1
            f[ind] *= 0.25

        f /= 100.0

        sky = f[0]
        for i in xrange(1, f.shape[0]):
            sky = sky + f[i] - sky * f[i]

        #  Convert the sky from percent to whole integers
        grid = sky * 100.0

        #  Fill in any data void areas (as needed)
        grid = self.BI_fillScalar(grid, fillMasks)

        #  Try to check this sky against PoP
        return self.BI_SmoothGrid(grid)

    # From: ../../methods/BI_calcSnowRatio/BI_calcSnowRatio.py
    # ===========================================================================
    #  BI_calcSnowRatio - Method to compute snow:liquid ratio based on a spline
    #  curve defined at temperature (deg C) anchor points.
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcSnowRatio(
        self,
        gh_c,
        t_c,
        rh_c,
        pvv_c,
        gh_MB925,
        gh_MB800,
        gh_MB850,
        gh_MB750,
        gh_MB700,
        gh_MB650,
        gh_MB600,
        gh_MB550,
        cutBelow=4,
        thickness="925-700",
        fillMasks=[],
    ):
        #  We do not want any levels in the cubes at or below 925 mb - make
        #  copies of data we want to keep so as not to corrupt base cubes
        gh_c = gh_c[cutBelow:, :, :]
        t_c = t_c[cutBelow:, :, :]
        rh_c = rh_c[cutBelow:, :, :]
        pvv_c = pvv_c[cutBelow:, :, :]

        #  Define some parameters to alter algorithm

        #  Make some grids we'll need for calculations later
        cubeShape = (len(t_c), t_c.shape[1], t_c.shape[2])

        layerSR = zeros(cubeShape, dtype=float)
        pvvAvg = zeros(cubeShape, dtype=float)
        pvvSum = self.empty()

        #  Look at each vertical level
        for i in range(len(gh_c) - 1):
            avgTemp = t_c[i] - 273.15  # Convert to C
            avgRH = rh_c[i]

            #  Start with a snow ratio based on average temperature
            layerSR[i] = self.BI_baseSnowRatio(avgTemp)

            #  Now factor in vertical motion
            pvvAvg[i] = -10 * (pvv_c[i])
            pvvAvg[i] = where(less(pvvAvg[i], 0.0), 0.0, pvvAvg[i])
            pvvAvg[i] = where(
                less(avgRH, 80.0),
                pvvAvg[i] * ((avgRH * avgRH) / 6400.0),
                pvvAvg[i],
            )

            #  Add this average vertical velocity to the vertical velocity sum
            pvvSum = pvvSum + pvvAvg[i]

        # -----------------------------------------------------------------------
        #  Compute a total snow ratio from layer snow ratios and

        totalSnowRatio = self.empty()
        thicknessSnowRatio = self.empty()

        pvvSum = where(less_equal(pvvSum, 0.0), 0.0001, pvvSum)
        for i in range(len(layerSR)):
            srGrid = layerSR[i] * pvvAvg[i] / pvvSum
            totalSnowRatio = totalSnowRatio + srGrid

        ### Commented out by Andrew Just on Oct 5, 2016 - will make grid unconditional
        # -----------------------------------------------------------------------
        #  Ensure we have active ice nuclei
        # mask = logical_and(less(t_c, 265.15), greater_equal(rh_c, 50.0))
        # mask = any(mask)

        #  No active ice nuclei - no snow ratio
        # totalSnowRatio = where(equal(mask, 0), 0.0, totalSnowRatio)

        # -----------------------------------------------------------------------
        #  Determine snow ratio based on selected layer

        if thickness == "850-700":
            thicknessSnowRatio = 20.0 - pow(
                ((gh_MB700 - gh_MB850) - 1437.0) / 29.0, 2
            )
        elif thickness == "925-700":
            thicknessSnowRatio = 20.0 - pow(
                ((gh_MB700 - gh_MB925) - 2063.0) / 41.0, 2
            )
        elif thickness == "850-650":
            thicknessSnowRatio = 20.0 - pow(
                ((gh_MB650 - gh_MB850) - 1986.0) / 39.0, 2
            )
        elif thickness == "800-600":
            thicknessSnowRatio = 20.0 - pow(
                ((gh_MB600 - gh_MB800) - 2130.0) / 42.0, 2
            )
        else:  # "750-550"
            thicknessSnowRatio = 20.0 - pow(
                ((gh_MB550 - gh_MB750) - 2296.0) / 45.0, 2
            )

        #  Ensure thickness snow ratio is not less than zero
        thicknessSnowRatio = where(
            less(thicknessSnowRatio, 0.0), 0.0, thicknessSnowRatio
        )

        # -----------------------------------------------------------------------
        #  Alter total snow ratio by thickness snow ratio and vertical velocity

        totalSnowRatio = (totalSnowRatio * 0.50) + (thicknessSnowRatio * 0.50)
        totalSnowRatio = where(
            less_equal(pvvSum, 100.0),
            (
                (totalSnowRatio * 0.01 * pvvSum)
                + (thicknessSnowRatio * (1.0 - pvvSum * 0.01))
            ),
            totalSnowRatio,
        )
        totalSnowRatio = where(
            less(pvvSum, 1.0), thicknessSnowRatio, totalSnowRatio
        )

        ### Commented out by Andy on Oct 5, 2016 - will make grid unconditional
        # -----------------------------------------------------------------------
        #  Mask where temperatures are above freezing

        # mask = any(less_equal(t_c,272.65),axis=0)
        # mask = sum(mask)

        #  Set snow ratio to zero where temperatures are above freezing

        # totalSnowRatio = where(mask,totalSnowRatio,0.0)

        #  Return completed snow ratio after filling in any data void areas
        #  (as needed)
        return self.BI_fillScalar(totalSnowRatio, fillMasks)

    # From: ../../methods/BI_calcT/BI_calcT.py
    def BI_calcT(
        self,
        blTemps,
        blRH,
        blWinds,
        p_SFC,
        t_SFC,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        MSLP=0,
        fillMasks=[],
    ):
        """T - use model sounding to get temperature at real topography instead of
        model topography

        Where the topo is above the model topo - use the boundary layer temperature to
        interpolate a temperature...but in radiational inversions this is typically
        too warm because the free air temperature from the model is warmer than air
        near the ground on a mountain that sticks up higher than the model mountains.
        So...  if there is an inversion (i.e. the boundary layer temp at the desired
        height is warmer than the model surface temp) it only goes 1/2 as warm as the
        raw inversion in the free model atmosphere would be.  Not sure if this is good
        for strong and persistent inversions like marine inversions - but works well
        for persistent radiational inversions in the intermountain west during the
        winter - and works well for nocturnal inversions all times of the year.

        Where the topo is below the model topo - it uses the lapse rate between the
        two lowest boundary layer levels and extrapolates this downward - with the
        restriction that the lapse rate cannot be more than dry adiabatic and
        inversions are extrapolated at only 1/2 that lapse rate and also limited to no
        more than 1.5C decrease per km.  The 1.5C per km restriction is arbirary -
        further research may restrict it more or less.  The dry adiabatic restriction
        seems to work fine.
        """

        #  Setup the boundary layer cube for this time - if needed
        self.BI_setupBLCube(
            blTemps,
            blRH,
            blWinds,
            p_SFC,
            stopo,
            topo,
            gh_c,
            t_c,
            rh_c,
            wind_c,
            ctime,
            MSLP,
        )

        #  Make local references to boundary layer data for shorter notation
        BLT = self.BI_BLT
        # self.printval("temp:",self.BI_BLT,65,65)
        BLH = self.BI_BLH

        st = self.newGrid(-1)
        for i in range(1, BLH.shape[0]):
            tval = self.linear(BLH[i], BLH[i - 1], BLT[i], BLT[i - 1], topo)
            #
            # restrict the increase in areas where inversions present
            #
            tval = where(
                greater(tval, BLT[0]), BLT[0] + ((tval - BLT[0]) / 2.0), tval
            )
            between = logical_and(
                greater_equal(topo, BLH[i - 1]), less(topo, BLH[i])
            )
            st = where(logical_and(less(st, 0.0), between), tval, st)
        #
        #  restrict the lapse rates below the model surface
        #
        lapse = (BLT[1] - BLT[0]) / (BLH[1] - BLH[0])
        lapse = where(greater(lapse, 0.0), lapse / 2.0, lapse)
        maxinvert = 1.5 / 1000.0
        lapse = where(greater(lapse, maxinvert), maxinvert, lapse)
        drylapse = -9.8 / 1000.0
        lapse = where(less(lapse, drylapse), drylapse, lapse)
        ##        tst=BLT[0]+((topo-stopo)*lapse)
        tst = t_SFC + ((topo - stopo) * lapse)
        st = where(less(st, 0.0), (tst + t_SFC) / 2.0, st)
        #
        # diff=t_FHAG2-st
        # maxdiff=maximum.reduce(maximum.reduce(diff))
        # mindiff=minimum.reduce(minimum.reduce(diff))
        # print "max/min temp change: %6.2f %6.2f"%(maxdiff,mindiff)

        #  Fill in any data void areas
        st = self.BI_fillScalar(st, fillMasks)

        #  change to Fahrenheit
        return self.KtoF(st)

    # From: ../../methods/BI_calcTd/BI_calcTd.py
    ################################################################################
    #  Methods used to derive surface dewpoint
    ################################################################################

    # ===========================================================================
    # BI_calcTd - where topo is above the model topo - it interpolates the
    #      dewpoint from the model sounding.  This allows mountains sticking up
    #      into dry air during nighttime inversions to reflect the dry air
    #      aloft.
    #
    #      Where the topo is below the model topo - it uses the model surface
    #      mixing ratio, and assumes that is constant to the real topo - and
    #      uses the temperature at the real topo calculated in BI_calcT.
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    #
    #     modified from baseline NAM12 calcTd method (Tim Barker - WFO BOI)
    # ===========================================================================
    def BI_calcTd(
        self,
        blTemps,
        blRH,
        blWinds,
        p_SFC,
        T,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        MSLP=0,
        fillMasks=[],
    ):
        #  Setup the boundary layer cube for this time - if needed
        self.BI_setupBLCube(
            blTemps,
            blRH,
            blWinds,
            p_SFC,
            stopo,
            topo,
            gh_c,
            t_c,
            rh_c,
            wind_c,
            ctime,
            MSLP,
        )

        #  Make local references to boundary layer data for shorter notation
        BLD = self.BI_BLD
        BLH = self.BI_BLH
        #
        #  for real topo above model topo - interpolate dewpoint from the
        #  model dewpoint sounding
        #
        sd = self.newGrid(-1)
        for i in range(1, BLH.shape[0]):
            dval = self.linear(BLH[i], BLH[i - 1], BLD[i], BLD[i - 1], topo)
            between = logical_and(
                greater_equal(topo, BLH[i - 1]), less(topo, BLH[i])
            )
            sd = where(logical_and(less(sd, 0.0), between), dval, sd)
        #
        #  for real topo below model topo - use model surface mixing ratio
        #  and use that mixing ratio with the surface temperature which
        #  was derived from the low-level lapse rate.
        #
        sfce = blRH[0] / 100 * self.esat(blTemps[0])
        w = (0.622 * sfce) / ((p_SFC + 0.0001) / 100 - sfce)
        tsfce = self.esat(self.FtoK(T))
        dpdz = 287.04 * blTemps[0] / (p_SFC / 100 * 9.8)  # meters / millibar
        newp = p_SFC / 100 + (stopo - topo) / dpdz
        ws = (0.622 * tsfce) / (newp - tsfce)
        rh = w / ws
        tsfcesat = rh * tsfce
        tsfcesat = clip(tsfcesat, 0.00001, tsfcesat)
        b = 26.66082 - log(tsfcesat)
        td = (b - sqrt(b * b - 223.1986)) / 0.0182758048
        sd = where(less(sd, 0.0), td, sd)

        #  Fill in any data void areas
        sd = self.BI_fillScalar(sd, fillMasks)

        #  Change to Fahrenheit and make sure it is less than temp
        td = self.KtoF(sd)
        td = where(greater(td, T), T, td)
        return td

    # From: ../../methods/BI_calcTransWind/BI_calcTransWind.py
    # ===========================================================================
    #  BI_TransWind - the average winds in the layer between the surface
    #                 and the mixing height.
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcTransWind(
        self,
        blTemps,
        blRH,
        blWinds,
        p_SFC,
        MixHgt,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        MSLP=0,
        fillMasks=[],
    ):
        #  Setup the boundary layer cube for this time - if needed
        self.BI_setupBLCube(
            blTemps,
            blRH,
            blWinds,
            p_SFC,
            stopo,
            topo,
            gh_c,
            t_c,
            rh_c,
            wind_c,
            ctime,
            MSLP,
        )

        #  Make local references to boundary layer data for shorter notation
        BLW = self.BI_BLW
        BLH = self.BI_BLH
        BLM = BLW[0]
        BLD = BLW[1]
        nmh = stopo + (MixHgt * 0.3048)  # convert MixHt from feet -> meters

        pSFCmb = p_SFC / 100.0
        (utot, vtot) = self._getUV(BLM[0], BLD[0])
        numl = self.newGrid(1)

        for i in range(1, BLH.shape[0]):
            use = less(BLH[i], nmh)
            (u, v) = self._getUV(BLM[i], BLD[i])
            utot = where(use, utot + u, utot)
            vtot = where(use, vtot + v, vtot)
            numl = where(use, numl + 1, numl)
        #
        #  calculate average
        #
        u = utot / numl
        v = vtot / numl
        #
        #  Smooth a little
        #
        u = where(less(pSFCmb, 500.0), -9999.0, u)
        v = where(less(pSFCmb, 500.0), -9999.0, v)
        u = self.BI_smoothpm(u, 1)
        v = self.BI_smoothpm(v, 1)

        #  Fill in any data void areas
        (u, v) = self.BI_fillVector((u, v), fillMasks)
        #
        # convert u, v to mag, dir
        #
        (tmag, tdir) = self._getMD(u, v)
        tdir = clip(tdir, 0, 359.5)
        tmag = tmag * 1.9438  # convert to knots
        tmag = clip(tmag, 0, 125)  # clip speed to 125 knots

        #  Return computed transport wind
        return (tmag, tdir)

    # From: ../../methods/BI_calcWind/BI_calcWind.py
    ################################################################################
    #  Methods dealing with wind and wind gusts
    ################################################################################

    # ===========================================================================
    #  BI_calcWind - uses boundary layer wind "sounding" to get the wind at the
    #         real elevation rather than the model elevation. When real topo
    #         is below model topo, just uses the lowest boundary layer wind
    #         field.
    #
    #   This typically gives ridgetops a bit too much wind speed - so if speed
    #   is above the model surface wind speed - it only uses 1/2 of the
    #   difference.  Direction is allowed to reflect the direction at the
    #   higher level. This gives the wind a topography-influenced look, with
    #   sharp mountains sticking up into 'stronger' wind speeds and different
    #   wind directions.
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    #
    #   modified from baseline NAM12 calcWind method (Tim Barker - WFO BOI)
    # ===========================================================================
    def BI_calcWind(
        self,
        blTemps,
        blRH,
        blWinds,
        p_SFC,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        MSLP=0,
        fillMasks=[],
    ):
        #  Setup the boundary layer cube for this time - if needed
        self.BI_setupBLCube(
            blTemps,
            blRH,
            blWinds,
            p_SFC,
            stopo,
            topo,
            gh_c,
            t_c,
            rh_c,
            wind_c,
            ctime,
            MSLP,
        )

        #  Make local references to boundary layer data for shorter notation
        BLH = self.BI_BLH
        BLW = self.BI_BLW
        BLMAG = BLW[0]
        BLDIR = BLW[1]

        #  Coding for mountain offices
        if self.BI_optionsDict["topoSite"]:
            #  Initialize wind components
            smag = self.newGrid(-1)
            sdir = smag

            #  Where the real topography is below the model topography,
            #  we will set the wind to the surface wind in the model.
            smag = where(less(topo, BLH[0]), BLMAG[0], smag)
            sdir = where(less(topo, BLH[0]), BLDIR[0], sdir)

            #  For places where the real topography is above model topography,
            #  we go through boundary layer data and interpolate the model
            #  winds to the real topography.
            for i in range(1, BLH.shape[0]):
                #  Find areas which are within this layer
                between = logical_and(
                    greater_equal(topo, BLH[i - 1]), less(topo, BLH[i])
                )

                #  Interpolate model winds to real topography
                mval = self.linear(
                    BLH[i], BLH[i - 1], BLMAG[i], BLMAG[i - 1], topo
                )
                dval = self.BI_dirlinear(
                    BLH[i], BLH[i - 1], BLDIR[i], BLDIR[i - 1], topo
                )

                #  Assign new surface winds where we do not alreaday have one
                smag = where(logical_and(less(smag, 0.0), between), mval, smag)
                sdir = where(logical_and(less(sdir, 0.0), between), dval, sdir)

            #  If new computed wind speed is greater than original model surface
            #  wind speed, that is, if a topographic correction has been made,
            #  limit that change to be the addition of half of the difference
            #  between the "corrected" speed and the original model surface wind
            #  speed.  This keeps things under control on the high ridges.

            smag = where(
                greater(smag, BLMAG[0]),
                BLMAG[0] + ((smag - BLMAG[0]) / 2.0),
                smag,
            )

            #  Convert wind speed from m/s to knots
            wmag = smag * 1.944
            wmag = where(less(p_SFC / 100.0, 500.0), 0.0, wmag)
            wdir = clip(sdir, 0, 359.5)

        #  Coding for non-mountain offices
        else:
            sfcWind = blWinds[0]
            wmag = sfcWind[0] * 1.944
            wdir = clip(sfcWind[1], 0, 359.5)

        #  Smooth this grid a little
        ##        wmag = self.BI_smoothpm(wmag, 1)
        ##        wdir = self.BI_smoothpm(wdir, 1)

        #  Return completed wind, after filling in any data void areas
        #  (as needed)
        return self.BI_fillVector((wmag, wdir), fillMasks)

    # From: ../../methods/BI_categorizeCloudHeight/BI_categorizeCloudHeight.py
    # ===========================================================================
    #  BI_categorizeCloudHeight - this method is used to categorize cloud
    #  heights to the closest reportable value in 100s of feet.
    # ===========================================================================
    def BI_categorizeCloudHeight(self, height, convert=0):
        #  Convert visibility from meters to statue miles - if needed
        if convert:
            height = height * (3.28084 / 100.0)

        #  D2D displays -3.28m in clear areas outside the fog areas, so we can
        #  take advantage of this information to distinguish clear areas from
        #  the dense fog associated with "0" values.
        height[height <= 0] = 250

        #  Categorize IFR cigs - we're just not that good
        mask = (height >= 5) & (height < 10)
        height[mask] = 8
        mask = (height >= 2) & (height < 5)
        height[mask] = 3
        height[height < 2] = 1

        #  Categorize MVFR cigs - we're just not that good
        mask = (height >= 10) & (height < 13)
        height[mask] = 10
        mask = (height >= 13) & (height < 18)
        height[mask] = 15
        mask = (height >= 18) & (height < 23)
        height[mask] = 20
        mask = (height >= 23) & (height < 28)
        height[mask] = 25

        #  Ensure cloud heights are reportable
        mask = (height >= 28) & (height < 33)
        height[mask] = 30
        mask = (height >= 33) & (height < 37)
        height[mask] = 35
        mask = (height >= 37) & (height < 43)
        height[mask] = 40
        mask = (height >= 43) & (height < 47)
        height[mask] = 45
        mask = (height >= 47) & (height < 55)
        height[mask] = 50

        #  Switch to 1000 ft values
        mask = (height >= 55) & (height < 65)
        height[mask] = 60
        mask = (height >= 65) & (height < 75)
        height[mask] = 70
        mask = (height >= 75) & (height < 85)
        height[mask] = 80
        mask = (height >= 85) & (height < 95)
        height[mask] = 90
        mask = (height >= 95) & (height < 105)
        height[mask] = 100
        mask = (height >= 105) & (height < 115)
        height[mask] = 110
        mask = (height >= 115) & (height < 125)
        height[mask] = 120
        mask = (height >= 125) & (height < 135)
        height[mask] = 130
        mask = (height >= 135) & (height < 145)
        height[mask] = 140
        mask = (height >= 145) & (height < 175)
        height[mask] = 150

        #  Shorten up the cirrus groups
        mask = (height >= 175) & (height < 225)
        height[mask] = 200
        height[height >= 225] = 250

        #  Return categorized cloud height
        return height

    # From: ../../methods/BI_categorizeVsby/BI_categorizeVsby.py
    # ===========================================================================
    #  BI_categorizeVsby - this method is used to categorize visibility to the
    #  closest reportable value in statute miles.
    # ===========================================================================
    def BI_categorizeVsby(self, vsby, convert=0):
        #  Convert visibility from meters to statue miles - if needed
        if convert == 1:
            vsby = where(greater(vsby, 10.0), vsby / 1609.3, vsby)

        #  10 SM
        vsby = where(greater_equal(vsby, 6.5), 10.0, vsby)
        #  6 SM
        vsby = where(
            logical_and(greater(vsby, 5.45), less(vsby, 6.5)), 6.0, vsby
        )
        #  5 SM
        vsby = where(
            logical_and(greater(vsby, 4.45), less(vsby, 5.46)), 5.0, vsby
        )
        #  3 SM
        vsby = where(
            logical_and(greater(vsby, 2.45), less(vsby, 4.46)), 3.0, vsby
        )
        #  2 SM
        vsby = where(
            logical_and(greater(vsby, 1.45), less(vsby, 2.46)), 2.0, vsby
        )
        #  1 SM
        vsby = where(
            logical_and(greater(vsby, 0.85), less(vsby, 1.46)), 1.0, vsby
        )
        #  3/4 SM
        vsby = where(
            logical_and(greater(vsby, 0.65), less(vsby, 0.86)), 0.75, vsby
        )
        #  1/2 SM
        vsby = where(
            logical_and(greater(vsby, 0.30), less(vsby, 0.66)), 0.50, vsby
        )
        #  1/4 SM
        vsby = where(less_equal(vsby, 0.30), 0.25, vsby)

        return vsby

    # From: ../../methods/BI_checkT/BI_checkT.py
    def BI_checkT(self, T):
        """Check if the minimum temperature is greater than a threshold in
        order to determine if snow calculations need to be made.
        """
        if (
            T is not None
            and T.min() >= self.BI_optionsDict["noSnowThresholdT"]
        ):
            return False
        return True

    # From: ../../methods/BI_computeSkyLayer/BI_computeSkyLayer.py
    # ===========================================================================
    #   BI_computeSkyLayer - compute sky cover fraction using RH over a layer,
    #   rather than at single levels lke the baseline cloud-from-RH technique.
    #   Based on the DSM_Sky_Inits (2005).
    #
    #  This method can attempt to fill in data void regions.  To do so, include
    #    a list of Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_computeSkyLayer(
        self,
        pressureLevel,
        rhLayer,
        ghLayer,
        startPressureLevel,
        topo,
        fillMasks=[],
    ):
        skyLayer = 0
        pressureDiff = pressureLevel - startPressureLevel
        skyLayer = where(
            equal(pressureDiff, 0),
            where(rhLayer < 64, 0, rhLayer * 1.13 - 71.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 2),
            where(rhLayer < 51, 0, rhLayer * 1.33 - 66.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 4),
            where(rhLayer < 59, 0, rhLayer * 1.65 - 95.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 6),
            where(rhLayer < 46, 0, rhLayer * 1.63 - 73.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 10),
            where(rhLayer < 35, 0, rhLayer * 1.79 - 61.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 14),
            where(rhLayer < 20, 0, rhLayer * 1.20 - 24.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 18),
            where(rhLayer < 10, 0, rhLayer * 0.86 - 7.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 20),
            where(rhLayer < 0, 0, rhLayer * 0.55 + 3.0),
            skyLayer,
        )
        skyLayer = where(
            equal(pressureDiff, 22),
            where(rhLayer < 0, 0, rhLayer * 0.33 + 5.0),
            skyLayer,
        )

        #  Return completed sky cover, after filling in any data void areas
        #  (as needed)
        return self.BI_fillScalar(skyLayer, fillMasks)

    # From: ../../methods/BI_dewFromTandRH/BI_dewFromTandRH.py
    # ===========================================================================
    #  BI_dewFromTandRH - computes dewpoint at model time step from T and RH.
    # ===========================================================================
    def BI_dewFromTandRH(self, T, RH):
        tc = (T - 32.0) * (5.0 / 9.0)
        rh = clip(RH, 0.001, 99.999) / 100.0
        x = (log(rh) / 17.67) + (tc / (tc + 243.5))
        tdc = (243.5 * x) / (1.0 - x)
        td = (tdc * 9.0 / 5.0) + 32.0
        return td

    # From: ../../methods/BI_dirlinear/BI_dirlinear.py
    ################################################################################
    #  Utility methods
    ################################################################################

    # ===========================================================================
    #   BI_dirlinear - for mountain offices when computing wind
    #
    #   A linear interpolation that can be used for directions, where values
    #   should never get higher than 360 degrees.  We want interpolations that
    #   cross this 360 degree barrier to "go the right way" rather than flip
    #   back in the opposite direction
    # ===========================================================================
    def BI_dirlinear(self, xmax, xmin, ymax, ymin, we):
        ydif = ymax - ymin
        ydif = where(less(ydif, 0.0), -ydif, ydif)
        rotate = greater(ydif, 180.0)
        upper = greater(ymin, 180.0)
        lower = less(ymin, 180.0)
        ymax = where(logical_and(rotate, upper), ymax + 360.0, ymax)
        ymax = where(logical_and(rotate, lower), ymax - 360.0, ymax)
        slope = (ymax - ymin) / (xmax - xmin + 0.0000001)
        intercept = ymin - (slope * xmin)
        value = (slope * we) + intercept
        value = where(greater(value, 360), value - 360, value)
        value = where(less(value, 0.0), value + 360, value)
        return value

    # From: ../../methods/BI_EnhanceTopoPoP/BI_EnhanceTopoPoP.py
    # ===========================================================================
    #  BI_EnhanceTopoPoP - technique which uses natural logarithm to enhance
    #  chances of measurable precipitation along topographic features.
    # ===========================================================================
    def BI_EnhanceTopoPoP(self, PoP, topo):
        #  Ensure topo can be passed through logarithm
        topo = where(less(topo, 1), 1, topo)

        #  Add topography enhancement which starts at 6000 ft. Applies a
        #  multiplier approach, where 6000 ft is 1 * PoP, 12000 ft or higher
        #  is 1.5 * PoP, and the multiplier increases logarithmically
        #  between the two elevations
        multiplier = where(
            greater(topo, 10.0), 0.7213 * log(topo) - 4.4141, 1.0
        )

        PoP = where(
            logical_and(greater(topo, 1818), less(topo, 3636)),
            PoP * multiplier,
            PoP,
        )
        PoP = where(greater_equal(topo, 3636), 1.5 * PoP, PoP)
        PoP = self.BI_smoothpm(PoP, 2)

        #  Ensure returned PoP is valid
        return clip(PoP, 0.0, 100.0)

    # From: ../../methods/BI_fillEditArea/BI_fillEditArea.py
    # ===========================================================================
    #  BI_fillEditArea - used to compute new values within an edit area based on
    #  data outside edit area - taken from FillTool SmartTool (Tom LeFebvre,
    #  GSD).  AWIPS1 version will run on AWIPS2, but is extremely slow.  Use
    #  the JSmartUtils equivalent on AWIPS2 instead
    # ===========================================================================
    def BI_fillEditArea(self, grid, fillMask):
        #  Get the coordinates of the "edge" points of the area to fill
        borderMask = self.BI_getMaskBorder(fillMask)

        #  "Fill" the values on this grid where necessary
        # Workaround for DR 18576
        try:
            grid = JSmartUtils.fillEditArea(grid, fillMask, borderMask)
        except:
            grid = fillEditArea(grid, fillMask, borderMask)

        #  Return the completed grid
        return grid

    # From: ../../methods/BI_fillMissingClimo/BI_fillMissingClimo.py
    def BI_fillMissingClimo(self, grid, zeroMask=None):
        """fills in climoQPF where PRISM provided no data"""

        # If a mask is not passed then fill areas that are zero
        if zeroMask is None:
            zeroMask = where(equal(grid, 0.0), 0, 1)

        grid = where(zeroMask, grid, 0)

        newGrid = self.empty()

        smoothMask = self.BI_smoothpm(zeroMask, 1)
        smoothQPFC = self.BI_smoothpm(grid, 1, zeroMask)
        newGrid = where(
            logical_and(equal(zeroMask, 0.0), greater_equal(smoothMask, 0.5)),
            smoothQPFC,
            grid,
        )

        for i in range(2, 200, 1):
            zeroMask = where(equal(newGrid, 0.0), 0, 1)
            noPoints = minimum.reduce(minimum.reduce(zeroMask))
            if noPoints == 1:
                break
            smoothMask = self.BI_smoothpm(zeroMask, i)
            smoothQPFC = self.BI_smoothpm(newGrid, i, zeroMask)

            newGrid = where(
                logical_and(
                    equal(newGrid, 0.0), greater_equal(smoothMask, 0.2)
                ),
                smoothQPFC,
                newGrid,
            )

        return newGrid

    # From: ../../methods/BI_fillScalar/BI_fillScalar.py
    # ===========================================================================
    #  BI_fillScalar - This method will attempt to fill in data void regions.
    #    To do so, include a list of Numeric/numpy masks through the fillMasks
    #    argument.
    # ===========================================================================
    def BI_fillScalar(self, scalar, fillMasks=[]):
        # -----------------------------------------------------------------------
        #  Fill in any data void areas

        for fillMask in fillMasks:
            scalar = self.BI_fillEditArea(scalar, fillMask)

            if self.BI_optionsDict["SMOOTH_AFTER_FILL"]:
                scalar = self.BI_Smooth(scalar, fillMask=fillMask)

        return scalar

    # From: ../../methods/BI_fillVector/BI_fillVector.py
    # ===========================================================================
    #  BI_fillVector - This method will attempt to fill in data void regions.
    #    To do so, include a list of Numeric/numpy masks through the fillMasks
    #    argument.
    # ===========================================================================
    def BI_fillVector(self, vector, fillMasks=[]):
        #  Separate this vector into its coordinates
        (coord1, coord2) = vector  #  could be either u-v or mag-dir

        # -----------------------------------------------------------------------
        #  Fill in any data void areas

        for fillMask in fillMasks:
            #  Fix each coordinate
            coord1 = self.BI_fillEditArea(coord1, fillMask)
            coord2 = self.BI_fillEditArea(coord2, fillMask)

            if self.BI_optionsDict["SMOOTH_AFTER_FILL"]:
                coord1 = self.BI_Smooth(coord1, fillMask=fillMask)
                coord2 = self.BI_Smooth(coord2, fillMask=fillMask)

        #  Return the completed GFE vector grid
        return (coord1, coord2)

    # From: ../../methods/BI_FixLowCloudHeights/BI_FixLowCloudHeights.py
    # ===========================================================================
    #   BI_FixLowCloudHeights - this method is used to remove "bad" pixel data
    #   from ceiling heights.  Since it is essentially point-based, it is slow.
    #   Algorithm provided by Harry Gerapetritis (WFO GSP).
    # ===========================================================================
    def BI_FixLowCloudHeights(self, PredHgt):
        # New routine to remove erronous low clouds
        gridsize = PredHgt.shape
        ##        mygrid = PredHgt
        i = 1
        j = 1
        while i < (gridsize[0] - 1):
            j = 1
            while j < (gridsize[1] - 1):
                currentPredHgt = PredHgt[i][j]
                if currentPredHgt < 3:
                    lowFlag = 0
                    gridAvg = 0
                    PredHgt1 = PredHgt[i - 1][j - 1]
                    if PredHgt1 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt1
                    PredHgt2 = PredHgt[i - 1][j]
                    if PredHgt2 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt2
                    PredHgt3 = PredHgt[i - 1][j + 1]
                    if PredHgt3 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt3
                    PredHgt4 = PredHgt[i][j - 1]
                    if PredHgt4 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt4
                    PredHgt5 = PredHgt[i][j + 1]
                    if PredHgt5 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt5
                    PredHgt6 = PredHgt[i + 1][j - 1]
                    if PredHgt6 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt6
                    PredHgt7 = PredHgt[i + 1][j]
                    if PredHgt7 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt7
                    PredHgt8 = PredHgt[i + 1][j + 1]
                    if PredHgt8 < 3:
                        lowFlag = lowFlag + 1
                    else:
                        gridAvg = gridAvg + PredHgt8
                    if lowFlag < 3:
                        PredHgt[i][j] = gridAvg / (8 - lowFlag)
                j = j + 1
            i = i + 1

        #  Ensure any leftover invalid cloud heights are fixed
        PredHgt[PredHgt <= 0.0] = 250

        return PredHgt

    # From: ../../methods/BI_gemRH/BI_gemRH.py
    def BI_gemRH(self, temp, dptd, ctime):
        # first find the dew point
        dwpt = temp - dptd

        # now calc the rh
        Tc = temp - 273.15
        Tdc = dwpt - 273.15
        Vt = 6.11 * pow(10, (Tc * 7.5 / (Tc + 237.3)))
        Vd = 6.11 * pow(10, (Tdc * 7.5 / (Tdc + 237.3)))
        rh = (Vd / Vt) * 100.0

        return rh

    # From: ../../methods/BI_GeneralPoP1hr/BI_GeneralPoP1hr.py
    # ===========================================================================
    #  BI_GeneralPoP - technique which uses a base 10 logarithm versus baseline
    #  linear equation. (0.01" = 71% PoP, 0.05" = 85% PoP, 0.50" = 100% PoP)
    #  Adjust max and min levels based on forecast hour.  Further adjustments
    #  can be made using topography.
    # ===========================================================================
    def BI_GeneralPoP1hr(self, QPF, topo, ctime):
        #  Use the PRISM data to downscale QPF at topography sites
        if self.BI_optionsDict["prismSite"] and len(self.climoQPFGrids) > 0:
            QPFPct = self.BI_getQPFPct(QPF, ctime)
            QPFDS = self.BI_getQPFDS(QPF, QPFPct, ctime)

            #  Adjust QPF where PRISM data is available - this test guarantees
            #  the QPF cannot be zero because of missing PRISM data
            QPF = where(greater(QPFDS, 0.0), QPFDS, QPF)

        #  Start PoP computation
        PoP = self.empty()
        qpf = clip(QPF, 0.001, 1000.0)
        PoP = 19.668 * log10(qpf) + 110.55
        PoP = where(less(QPF, 0.003), 0, PoP)
        PoP = where(greater_equal(QPF, 0.5), 100, PoP)

        #  If we should enhance PoP using topography
        if self.BI_optionsDict["topoSite"]:
            PoP = self.BI_EnhanceTopoPoP(PoP, topo)

        #  Ensure returned PoP is valid
        return clip(PoP, 0.0, 100.0)

    # From: ../../methods/BI_GeneralPoP/BI_GeneralPoP.py
    # ===========================================================================
    #  BI_GeneralPoP - technique which uses natural logarithm versus baseline
    #  linear equation (0.01" = 20% PoP, 0.05" = 50% PoP, 0.50" = 100% PoP).
    #  Adjust max and min levels based on forecast hour.  Further adjustments
    #  can be made using topography.
    # ===========================================================================
    def BI_GeneralPoP(self, QPF, topo, ctime):
        #  Use the PRISM data to downscale QPF at topography sites
        if self.BI_optionsDict["prismSite"] and len(self.climoQPFGrids) > 0:
            QPFPct = self.BI_getQPFPct(QPF, ctime)
            QPFDS = self.BI_getQPFDS(QPF, QPFPct, ctime)

            #  Adjust QPF where PRISM data is available - this test guarantees
            #  the QPF cannot be zero because of missing PRISM data
            QPF = where(greater(QPFDS, 0.0), QPFDS, QPF)

        #  Start PoP computation
        PoP = self.empty()
        qpf = clip(QPF, 0.001, 1000.0)
        PoP = 19.668 * log(qpf) + 110.55
        PoP = where(less(QPF, 0.003), 0, PoP)
        PoP = where(greater_equal(QPF, 0.5), 100, PoP)

        #  If we should enhance PoP using topography
        if self.BI_optionsDict["topoSite"]:
            PoP = self.BI_EnhanceTopoPoP(PoP, topo)

        #  Ensure returned PoP is valid
        return clip(PoP, 0.0, 100.0)

    # From: ../../methods/BI_GeneralPoPBL/BI_GeneralPoPBL.py
    def BI_GeneralPoPBL(
        self,
        t_FHAG2,
        t_BL030,
        t_BL3060,
        t_BL6090,
        t_BL90120,
        t_BL120150,
        rh_FHAG2,
        rh_BL030,
        rh_BL3060,
        rh_BL6090,
        rh_BL90120,
        rh_BL120150,
        wind_FHAG10,
        wind_BL030,
        wind_BL3060,
        wind_BL6090,
        wind_BL90120,
        wind_BL120150,
        p_SFC,
        QPF,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        stime,
        gridLengthFactor=1,
    ):
        """general PoP PBL -  based strongly on QPF (since when model has one inch of
        precip the chance of getting 0.01 is pretty high).  However, there is a big
        difference between a place that model has 0.00 precip and is very close to
        precipitating - and those where model has 0.00 and is a thousand miles from
        the nearest cloud.  Thus, uses the average BL to 500mb RH to make an
        adjustment on the low end - adding to PoP where RH is high.  Ignores surface
        RH to try to ignore fog cases. Would also like to consider omega.

        Uses hyperbolic tangent of QPF, so that it rises quickly as model QPF
        increases - but tapers out to nearly 100% as QPF gets high.  Also uses
        hyperbolic tangent of QPF to reduce the impact of high RH as QPF gets higher
        (since avg RH will always be high when QPF is high)

        Adjustable parameters:
            topQPF is QPF amount that would give 75% PoP if nothing else considered
                at half this amount, PoP is 45%, at double this amount PoP is 96%
                Default set at 0.40.
            RHexcess is amount of average BL to 500mb RH above which PoP is
                adjusted upward
                Default set to 70%
            adjAmount is maximum amount of adjustment if BL to 500mb RH is
                totally saturated
                Default set to 15%
        """
        # Make sure this is set to the version of setupBLCube in this Init file.
        # If you wish to override this than override all of GeneralPoPBL and put a local version of
        # setupBLCube in your Local override without self as the first variable.

        self.BI_setupBLCube(
            [t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120, t_BL120150],
            [
                rh_FHAG2,
                rh_BL030,
                rh_BL3060,
                rh_BL6090,
                rh_BL90120,
                rh_BL120150,
            ],
            [
                wind_FHAG10,
                wind_BL030,
                wind_BL3060,
                wind_BL6090,
                wind_BL90120,
                wind_BL120150,
            ],
            p_SFC,
            stopo,
            topo,
            gh_c,
            t_c,
            rh_c,
            wind_c,
            ctime,
        )
        BLR = self.BI_BLR
        BLP = self.BI_BLP

        topQPF = 0.10  # QPF value where raw PoP would be 75%
        RHexcess = 70.0  # RH above this can add to PoP and below will subtract
        adjAmount = 15.0  # amount of adjustment allowed
        #
        # code added by RJM to modify the PoP based on the forecast hour.
        # for Day 1 grids, the topQPF value should be fairly low in order
        # to have a 75 PoP.  But as we go out in the forecast, it should
        # take more QPF to get the same PoP, due to more model uncertainty.
        # So we use the forecast hour to compute a multiplication factor
        # which will increase the topQPF value.
        # As a first approximation, we'll use a simple formula that will
        # give us a factor of 1 for the 6 hour forecast, and linerally
        # increase to a factor of 3 for the 192 hour forecast.

        forecastHR = stime / 3600
        forecastHR_factor = ((float(forecastHR / 6.0) - 1.0) / 15.0) + 1.0
        topQPF = topQPF * forecastHR_factor
        #
        factor = tanh(gridLengthFactor * QPF * (1.0 / topQPF))
        factor2 = tanh(gridLengthFactor * QPF * (2.0 / topQPF))
        #
        #
        useRH = where(greater(BLP, 500.0), 1, 0)
        useRH[0] = 0
        rhcube = where(useRH, BLR, 0.0)
        div = add.reduce(useRH)
        div = where(less(div, 0.5), 1.0, div)
        rhavg = add.reduce(rhcube) / div
        # rhcube=BLR[1:14]
        # rhavg=add.reduce(rhcube)/13.0
        maxchg = min(100 - RHexcess, RHexcess)
        dpct = (rhavg - RHexcess) / maxchg
        dpct = clip(dpct, -1.0, 1.0)
        dpop = dpct * (1.0 - factor2) * adjAmount
        #
        pop = (factor * (100.0 - adjAmount)) + adjAmount + dpop
        pop = self.BI_smoothpm(pop, 2)
        pop = clip(pop, 0, 100)

        return pop

    # From: ../../methods/BI_getClimoQPF/BI_getClimoQPF.py
    # ===========================================================================
    #  BI_getClimoQPF - get a monthly climo QPF grid for a particular date.
    #  Interpolates between the monthly QPF values - which are assumed
    #  to be valid at 00Z on the 16th of each month.
    # ===========================================================================
    def BI_getClimoQPF(self, ctime):
        #  First try to get it from the cache
        try:
            return self.climoQPF[ctime]
        except:
            LogStream.logEvent("Interpolating climoQPF for a date")

        (ctime1, ctime2) = ctime
        (cyea, cmon, cday, chou, cmin, csec, cwda, cyda, cdst) = time.gmtime(
            ctime1
        )
        if cday < 16:
            pyea = cyea
            pmon = cmon - 1
            if pmon < 1:
                pyea = pyea - 1
                pmon = 12
            nyea = cyea
            nmon = cmon
        else:
            pyea = cyea
            pmon = cmon
            nyea = cyea
            nmon = cmon + 1
            if nmon > 12:
                nyea = nyea + 1
                nmon = 1
        ptime = calendar.timegm((pyea, pmon, 16, 0, 0, 0, 0, 0, 0))
        ntime = calendar.timegm((nyea, nmon, 16, 0, 0, 0, 0, 0, 0))
        diff = float(ntime - ptime)
        nwgt = float(ctime1 - ptime) / diff
        pwgt = float(ntime - ctime1) / diff
        pval = self.climoQPFGrids[pmon - 1] * pwgt
        nval = self.climoQPFGrids[nmon - 1] * nwgt
        finalVal = pval + nval

        cmin = minimum.reduce(minimum.reduce(finalVal))

        #  If we need to fill in missing PRISM data
        if (self.fillMaskPrism is not None) or (cmin < 0.01):
            if self.fillMaskPrism is not None:
                climoMask = self.fillMaskPrism
                finalVal = self.BI_fillMissingClimo(finalVal, climoMask)
            else:
                climoMask = where(less(finalVal, 0.01), 1, 0)
                climoMask = self.alterArea(climoMask, 1)
                finalVal = where(equal(climoMask, 1), 0.0, finalVal)
                finalVal = self.BI_fillMissingClimo(finalVal)

        #  Cache this for later
        self.climoQPF[ctime] = finalVal

        #  Return the interpolated total climatological QPF
        return finalVal

    # From: ../../methods/BI_getFhr/BI_getFhr.py
    def BI_getFhr(self):
        """Gets the current forecast hour as float hours. This would typically
        be used in the levels method to accomodate data changes with forecast hour.
        """
        validTime = SmartInitParams.params["validTime"]
        return (validTime.getTime() / 1000 - self.sourceBaseTime()) / 3600.0

    # From: ../../methods/BI_getindicies/BI_getindicies.py
    # ===========================================================================
    #  BI_getindicies - used in slicing arrays - taken from baseline NAM12
    #  SmartInit (Tim Barker, WFO BOI)
    # ===========================================================================
    def BI_getindicies(self, o, l):
        if o > 0:
            a = slice(o, l)
            b = slice(0, l - o)
        elif o < 0:
            a = slice(0, l + o)
            b = slice(-o, l)
        else:
            a = slice(0, l)
            b = slice(0, l)
        return a, b

    # From: ../../methods/BI_getMaskBorder/BI_getMaskBorder.py
    # ===========================================================================
    #  BI_getMaskBorder - used to find edges of an edit area - taken from
    #  FillTool SmartTool (Tom LeFebvre, GSD)
    # ===========================================================================
    def BI_getMaskBorder(self, mask):
        border = self.empty()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                border = logical_or(border, self.BI_offset(mask, i, j))
        return logical_xor(border, mask)

    # From: ../../methods/BI_getMosTopoDiff/BI_getMosTopoDiff.py
    # ===========================================================================
    #  BI_getMosTopoDiff - gets GFS model topography (if needed), and
    #  computes a topo difference from the real topography
    # ===========================================================================
    def BI_getMosTopoDiff(self, stopo, topo):
        #  If we already have the model topography
        if stopo is not None:
            #  Return topography difference
            return topo - stopo

        # -----------------------------------------------------------------------
        #  If we made it this far, use a model topography as a substitute.
        #  Since just about all of the MOS products we would want to use this
        #  technique for are GFS-based, we will use the GFS model topography

        #  Define location of topography data
        fileName = (
            "/awips2/edex/data/utility/edex_static/site/%s/config/gfe/GFS_topo.dat"
            % (self._siteID)
        )

        #  Try to open and process this file
        try:
            f = open(fileName, "r")  #  open a file, keep the pointer
            p = cPickle.Unpickler(f)  #  make an Unpickler object
            model_topo = p.load()  #  get the model topo data
            f.close()

            #  Compute difference between actual topo and model topo
            diff = topo - model_topo

        except:
            LogStream.logEvent(
                "  %s does not exist! " % (fileName)
                + "Continuing without topo."
            )

            #  Do not make any correction
            diff = 0.0

        #  Return the topography difference we found
        return diff

    # From: ../../methods/BI_getMosT/BI_getMosT.py
    # ===========================================================================
    #  BI_calcMosT - compute temperature at MOS time step. This method can
    #  attempt to fill in data void regions.  To do so, include a list of
    #  Numeric/numpy masks through the fillMasks argument.
    # ===========================================================================
    def BI_calcMosT(self, grid, stopo, topo, applyTopo=0, fillMasks=[]):
        #  Fill in any data void areas
        grid = self.BI_fillScalar(grid, fillMasks)

        #  Coding for mountain offices
        if applyTopo:
            #  Apply topographic correction to MOS
            grid = self.BI_applyTopoT(grid, stopo, topo)

        #  Return completed temperature
        return self.KtoF(grid)

    # From: ../../methods/BI_getNumpyData/BI_getNumpyData.py
    # ====================================================
    #  get a numpy grid from a JEP gridslice
    #     up through 15.x this is done with the __numpy__
    #     attribute.  As of 16.1 and beyond this is done
    #     with a getNDArray call.
    #
    #     After 15.x is no longer supported - the try
    #        test can be deleted
    #
    #     Returns a numpy array for a Scalar.  Returns a
    #     list of numpy arrays for a Vector
    #
    def BI_getNumpyData(self, gridslice):
        try:
            result = gridslice.__numpy__
            if len(result) == 1:
                return result[0]
            else:
                return result
        except AttributeError:
            return gridslice.getNDArray()

    # From: ../../methods/BI_getPoPfromRadar/BI_getPoPfromRadar.py
    #
    # Alternative from QPF PoP Deriviation.
    #
    def BI_getPoPfromRadar(self, radar, ctime, Low=-15):
        fuzzVal = 10.0
        StartPoP = 15.0
        dbz1 = 5.0
        dbz2 = 45.0
        MaxPoP = 100.0

        dx = fuzzVal
        dy = float(StartPoP) - float(Low)
        slope = dy / dx
        b = float(StartPoP) - slope * dbz1
        interPoP1 = (slope * radar) + b
        # Ensure interPops are btween 0 and 100
        interPoP1 = where(greater(interPoP1, 100.0), 100.0, interPoP1)
        interPoP1 = where(less(interPoP1, 0.0), 0.0, interPoP1)
        # Now create a 2nd interpolated field for the 2 user defined pops
        dx = dbz2 - dbz1
        dy = float(MaxPoP) - float(StartPoP)
        slope = dy / dx
        b = float(MaxPoP) - slope * dbz2
        interPoP2 = (slope * radar) + b
        # Ensure interPops are btween 0 and 100
        interPoP2 = where(greater(interPoP2, 100.0), 100.0, interPoP2)
        interPoP2 = where(less(interPoP2, 0.0), 0.0, interPoP2)

        # Create new pop field
        PoP = where(greater(radar, dbz1), StartPoP, Low)
        PoP = where(
            less(radar, dbz1 - fuzzVal), Low, PoP
        )  # all values min pop
        PoP = where(
            logical_and(
                greater_equal(radar, dbz1 - fuzzVal), less_equal(radar, dbz1)
            ),
            interPoP1,
            PoP,
        )  # interpolated values in between
        PoP = where(
            logical_and(greater_equal(radar, dbz1), less(radar, dbz2)),
            interPoP2,
            PoP,
        )  # interpolated values in between
        PoP = where(greater_equal(radar, dbz2), MaxPoP, PoP)
        return self.BI_smoothpm(PoP, 3)

    # From: ../../methods/BI_getQPFDS/BI_getQPFDS.py
    def BI_getQPFDS(self, QPF, QPFPct, ctime):
        """downscaled QPF - by multiplying the model's percentage of its
        monthly QPF climatology (which is smoothed to the models
        resolution) times the REAL hires climatology
        Where no Prism data exists the raw QPF grid will be used.
        """
        sratio = QPFPct / 100.0
        qpfclim = (self.BI_getClimoQPF(ctime)) / 25.4
        if 0 in qpfclim:
            # Make mask of area where there is PRISM data.
            # Then shrink that area slightly to get rid of the most
            # outer pixels which appear to have been blended with zero.
            qpfMask = where(less(qpfclim, 0.01), 0, 1)
            qpfMask = self.alterArea(qpfMask, -1)
            qpfclim = where(qpfMask, qpfclim, 0)
        return where(less(qpfclim, 0.01), QPF, (sratio * qpfclim))

    # From: ../../methods/BI_getQPFPct/BI_getQPFPct.py
    def BI_getQPFPct(self, QPF, ctime):
        """get percentage of a model's smoothed monthly QPF climatology"""

        SCALEFACTOR = 0.5
        #
        #  Get monthly QPF climo, and smooth it over +/- NUMSMOOTH gridpoints
        #
        qpfclim = (self.BI_getClimoQPF(ctime)) / 25.4
        cmax = maximum.reduce(maximum.reduce(qpfclim))
        cmin = minimum.reduce(minimum.reduce(qpfclim))
        crange = cmax - cmin
        climoSmooth = self.BI_smoothpm(
            qpfclim, self.BI_optionsDict["ClimoQPFSmooth"]
        )
        climoSmooth = clip(climoSmooth, 0.001, 100)
        #
        #  Stretch the range of smoothed climo QPF back closer to original
        #  range.  This keeps it from being "easier" for forecasts to be
        #  a larger percentage of the climo.
        #
        smax = maximum.reduce(maximum.reduce(climoSmooth))
        smin = minimum.reduce(minimum.reduce(climoSmooth))
        srange = smax - smin
        pct = (climoSmooth - smin) / (smax - smin)
        newSmooth = (pct * (srange + ((crange - srange) * SCALEFACTOR))) + cmin
        newSmooth = where(less(newSmooth, 0.01), 0.01, newSmooth)
        #
        #  Get model ratio of QPF to monthly QPF
        #
        ratio = (QPF / newSmooth) * 100.0
        return clip(ratio, 0.0, 300.0)

    # From: ../../methods/BI_getSnowLevel/BI_getSnowLevel.py
    # ==========================================================================
    #  T Barker/R Miller/M Hirsch
    #  getSnowLevel - Uses the Freezing Level, the Wet-Bulb height, or a blend
    #                  of the two to determine Snow Level. Configurable variables
    #                  should be placed at the top of the smartInit.
    #                  Defaults:
    #                   METHOD='BLEND'
    #                   BELOW_FREEZING_LEVEL = 500
    #
    #

    def BI_getSnowLevel(self, gh_c, t_c, rh_c, topo):
        METHOD = self.BI_optionsDict["snowLevelMethod"]
        BELOW_FREEZING_LEVEL = self.BI_optionsDict["snowLevelBelowFzLevel"]
        #
        if METHOD == "FREEZING_LEVEL":
            snow = self.BI_getTempCross(gh_c, t_c)
            # subtract BELOW_FREEZING_LEVEL
            snow = snow - (BELOW_FREEZING_LEVEL / 3.28)
        elif METHOD == "WETBULB":
            snow = self.BI_getWetbulbCross(gh_c, t_c, rh_c, topo)
        else:
            # MH - Build weighted blend of wet-bulb height and freezing level height
            snow = self.BI_getWetbulbCross(gh_c, t_c, rh_c, topo)

            fzlvl_snow = self.BI_getTempCross(gh_c, t_c)
            # subtract BELOW_FREEZING_LEVEL
            fzlvl_snow = fzlvl_snow - (BELOW_FREEZING_LEVEL / 3.28)

            # print "fzlvl_snow", 3.28 * fzlvl_snow[0][0]
            # print "wbz", 3.28 * snow[0][0]

            # compute the weight based on column avg RH
            weight = self.BI_weightSnowLevel(gh_c, rh_c, topo)

            # now combine freezing and wet bulb snow levels
            # based on weight.
            blend = (1 - weight) * fzlvl_snow + weight * snow
            # print "weight", weight[0][0]

            snow = blend
        #
        #  Change to feet.
        #  Finally, smooth a bit
        #
        snow = snow * 3.28
        snow = self.BI_smoothpm(snow, 3)
        # print "snow", snow[0][0]
        #
        return snow

    # From: ../../methods/BI_getSoundingArea/BI_getSoundingArea.py
    # ===========================================================================
    #  calculate area above/below freezing in J/kg (m2/s2)
    # ===========================================================================
    def BI_getSoundingArea(self, hbot, tbot, htop, ttop):
        (ttop + tbot) / 2.0
        e1 = (ttop - 273.15) / 273.15
        e2 = (tbot - 273.15) / 273.15
        area = 9.8 * ((e1 + e2) / 2.0) * (htop - hbot)
        return area

    # From: ../../methods/BI_getTempCross/BI_getTempCross.py
    # ==========================================================================
    # getTempCross - Search downward through vertical profiles for the height
    #                when the temperature first crosses zero.  Return the
    #                height (in meters).
    #
    def BI_getTempCross(self, gh_c, t_c):
        #
        #  Starting at the top of the atmosphere, search downward until at
        #  least one gridpoint is above freezing. Then start the detailed
        #  search at the level above this.
        #
        startIndex = 2
        for i in xrange(t_c.shape[0] - 1, -1, -1):
            if maximum.reduce(maximum.reduce(t_c[i])) >= 273.15:
                startIndex = i + 1
                break
        #
        #  setup for detailed search
        #
        height = self.newGrid(-10000)
        ghlast = gh_c[startIndex]
        tclast = t_c[startIndex] - 273.15
        #
        numLeft = add.reduce(add.reduce(less(height, -5000)))
        index = startIndex - 1
        #
        #  Working downward, at each level, calculate the crossing height - but
        #  only use it at gridpoints where the level has not yet been found,
        #  and where the temp at the lower level is above (or equal) to 0.0.
        #  Stop when all gridpoints have been found.
        #
        while (index >= 0) and (numLeft > 0):
            gh = gh_c[index]
            tc = t_c[index] - 273.15
            tDiff = tclast - tc
            tDiff = where(equal(tDiff, 0.0), 1.0, tDiff)
            val = gh + (((ghlast - gh) / tDiff) * (0.0 - tc))
            cross = logical_and(less(height, -5000), greater_equal(tc, 0.0))
            height = where(cross, val, height)
            # numfound=add.reduce(add.reduce(cross))
            # self.logtime("   crossings at level %d (%d): %d"%(index,self.pres[index],numfound))
            #
            #  Move down to next level, but stop when all gridpoints have
            #  been found.
            #
            ghlast = gh
            tclast = tc
            index = index - 1
            numLeft = add.reduce(add.reduce(less(height, -5000)))
        #
        #  Handle case of even lowest pressure level has temp below zero.
        #  Set the height to the height of the lowest model level.
        #
        if numLeft > 0:
            height = where(less(height, -5000), ghlast, height)
        #
        return height

    # From: ../../methods/BI_getWetbulbCross/BI_getWetbulbCross.py
    def BI_getWetbulbCross(self, gh_c, t_c, rh_c, topo):
        #
        #  Setup threshold
        #
        threshk = 0.5 + 273.15
        #
        #  Starting at the top of the atmosphere, search downward until at
        #  least one gridpoint is above threshold. Then start the detailed
        #  search at the level above this.  Since wetbulb is always less than
        #  temp, just do this search in temperature - to save time.
        #
        startIndex = 2
        for i in xrange(t_c.shape[0] - 1, -1, -1):
            if maximum.reduce(maximum.reduce(t_c[i])) >= threshk:
                startIndex = i + 1
                break
        #
        #  setup for detailed search
        #
        height = self.newGrid(-10000)
        pmb = clip(self.newGrid(self.pres[startIndex] - 2.0), 1, 1050)
        ghlast = gh_c[startIndex]
        tc = clip(t_c[startIndex] - 273.15, -120, 60)
        rhc = clip(rh_c[startIndex], 0.5, 99.5)
        wetlast = self.BI_WetbulbLev(tc, rhc, pmb)
        #
        numLeft = add.reduce(add.reduce(less(height, -5000)))
        index = startIndex - 1
        #
        #  Working downward, at each level, calculate the crossing height - but
        #  only use it at gridpoints where the level has not yet been found,
        #  and where the temp at the lower level is above (or equal) to 0.0.
        #  Stop when all gridpoints have been found.
        #
        while (index >= 0) and (numLeft > 0):
            pmb = clip(self.newGrid(self.pres[index] - 2.0), 1, 1050)
            gh = gh_c[index]
            tc = clip(t_c[index] - 273.15, -120, 60)
            rhc = clip(rh_c[index], 0.5, 99.5)
            wet = self.BI_WetbulbLev(tc, rhc, pmb)
            wetDiff = wetlast - wet
            wetDiff = where(equal(wetDiff, 0.0), 1.0, wetDiff)
            val = gh + (((ghlast - gh) / wetDiff) * (threshk - wet))
            cross = logical_and(
                less(height, -5000), greater_equal(wet, threshk)
            )
            height = where(cross, val, height)
            # numfound=add.reduce(add.reduce(cross))
            # self.logtime("   crossings at level %d (%d): %d"%(index,self.pres[index],numfound))
            #
            #  Move down to next level, but stop when all gridpoints have
            #  been found.
            #
            ghlast = gh
            wetlast = wet
            index = index - 1
            numLeft = add.reduce(add.reduce(less(height, -5000)))
        #
        #  Handle case of even lowest pressure level has wetbulb below threshold
        #  Set the height to the height of the lowest model level.
        #
        #  RJM 2Dec2010 changed this to 0 instead of ghlast.  otherwise
        #  there were situations where the entire model is below freezing,
        #  but some gridpoints are below the 1000 gh and would get assigned
        #  rain
        #
        if numLeft > 0:
            height = where(less(height, -5000), 0.0, height)
        return height

    # From: ../../methods/BI_hainesIndex/BI_hainesIndex.py
    # ===========================================================================
    #  BI_hainesIndex - Calculate Haines index based on temperature and RH cubes
    # ===========================================================================
    def BI_hainesIndex(self, hainesLevel, t_c, rh_c):
        dict = {}
        dict["LOW"] = {
            "t1Level": 950,
            "t2Level": 850,
            "mLevel": 850,
            "stabThresh": [4, 8],
            "moiThresh": [6, 10],
        }
        dict["MEDIUM"] = {
            "t1Level": 850,
            "t2Level": 700,
            "mLevel": 850,
            "stabThresh": [6, 11],
            "moiThresh": [6, 13],
        }
        dict["HIGH"] = {
            "t1Level": 700,
            "t2Level": 500,
            "mLevel": 700,
            "stabThresh": [18, 22],
            "moiThresh": [15, 21],
        }

        dd = dict[hainesLevel.upper()]  # dictionary for this Haines type

        # get the needed data, calc dewpoint
        pres = self.pres

        #  Handle case where LOW Haines index cannot be computed
        try:
            t1 = t_c[pres.index(dd["t1Level"])]  #  t1 level
            t2 = t_c[pres.index(dd["t2Level"])]  #  t2 level
        except:
            if hainesLevel.upper() == "LOW":
                #  Use the medium instead - next best thing
                dd = dict["MEDIUM"]
                t1 = t_c[pres.index(dd["t1Level"])]  #  t1 level
                t2 = t_c[pres.index(dd["t2Level"])]  #  t2 level

        tMois = t_c[pres.index(dd["mLevel"])] - 273.15  #  mLevel t , in C.
        rhMois = rh_c[pres.index(dd["mLevel"])] / 100.0  # mLevel rh
        rhMois = where(less_equal(rhMois, 0), 0.00001, rhMois)
        a = log10(rhMois) / 7.5 + (tMois / (tMois + 237.3))
        dpMois = (a * 237.3) / (1.0 - a)

        hainesT = t1 - t2
        hainesM = tMois - dpMois

        # now make the categories
        mask3 = greater_equal(hainesT, dd["stabThresh"][1])
        mask1 = less(hainesT, dd["stabThresh"][0])
        hainesT = where(mask3, 3, where(mask1, 1, 2))

        mask3 = greater_equal(hainesM, dd["moiThresh"][1])
        mask1 = less(hainesM, dd["moiThresh"][0])
        hainesM = where(mask3, 3, where(mask1, 1, 2))

        return hainesT + hainesM

    # From: ../../methods/BI_handleDerivedGrids/BI_handleDerivedGrids.py
    # =============================================================================
    def BI_handleDerivedGrids(
        self, varName, inputGrid, gridType, mtime, minGrids
    ):
        """
        This method ensures that there are enough component grids available to
        calculate a derived grid. For example, we don't want a MaxT to be
        created when we only have the component T grids through 9am.

        Arguments: varName is the derived parameter to be created (usually
                   MaxT/MinT/MaxRH/MinRH/TdMrn/TdAft/PoP[3/6/12]/QPF[3/6/12]),
                   inputGrid is the component grid that the init is currently
                   operating on, gridType is the name of the component grid
                   (generally T/Td/RH/PoP*/QPF*), mtime is the grid time range,
                   minGrids is the minimum number of component grids
                   required to compute a derived grid (this will vary by model
                   temporal resolution and situation), can be an integer OR None;
                   if None, the program will attempt to use the built in dictionary
                   to grab the correct minGrid value (an error is raised if the
                   model name is not present in the dictionary).

        Returns:   None if the required # of component grids is unavailable or
                   the grid type is unsupported, otherwise returns the derived
                   grid.
        """
        #
        #  Test if dictionary lookup method is needed
        #
        if minGrids is None:
            #
            #  Dictionary of temporal resolution and required grids by model & parm.
            #  These entries are selected to elimate grids at "bad" times as much as
            #  possible, while still allowing for differences in time zone. The entries
            #  for hourly temporaal resolution models are slightly relaxed to allow a
            #  few more grids to be created.
            #
            requiredGridsDict = {
                #   Name            Res   MaxT   MinT  MaxRH  MinRH
                "DGEX": [6, 2, 2, 3, 3],
                "ECMWF": [6, 2, 2, 3, 3],
                "CMC": [6, 2, 2, 3, 3],
                "CMCnh": [6, 2, 2, 3, 3],
                "CMCreg": [3, 4, 4, 6, 6],
                "GFS": [6, 2, 2, 3, 3],
                "GLAMP25": [1, 11, 12, 15, 15],
                "HIRESWarw": [3, 4, 4, 6, 6],
                # Leave East/West versions in case a site needs them
                "HIRESWarwEast": [3, 4, 4, 6, 6],
                "HIRESWarwWest": [3, 4, 4, 6, 6],
                "HIRESWnmm": [3, 4, 4, 6, 6],
                "HIRESWnmmEast": [3, 4, 4, 6, 6],
                "HIRESWnmmWest": [3, 4, 4, 6, 6],
                "HRRR": [1, 11, 12, 15, 15],
                "HRRREXP": [1, 11, 12, 15, 15],
                "LAMP25": [1, 11, 12, 15, 15],
                "NAM12": [3, 4, 4, 6, 6],
                "NAMNest": [1, 11, 12, 15, 15],
                "RAP13": [1, 11, 12, 15, 15],
                "SREF": [3, 4, 4, 6, 6],
                "WPCGuide": [6, 2, 2, 3, 3],
                "GFS1hr": [1, 11, 12, 15, 15],
            }
            #
            # Grab model database name
            #
            dbID = self.newdb().getModelIdentifier()
            modelName = dbID[10 : dbID.find("_", 10, len(dbID))]
            #
            #  Check if current model is available in dict, otherwise raise error
            #
            if modelName not in requiredGridsDict:
                raise ValueError
            #
            #  Grab requirements for current situation
            #
            if varName == "MaxT":
                minGrids = requiredGridsDict[modelName][1]
            elif varName == "MinT":
                minGrids = requiredGridsDict[modelName][2]
            elif varName == "MaxRH":
                minGrids = requiredGridsDict[modelName][3]
            else:
                minGrids = requiredGridsDict[modelName][4]
            #
            #  For QPF & PoP, just use the model resolution to determine the
            #  number of required component grids
            #
            if "QPF" or "PoP" in varName:
                if "3" in varName:
                    minGrids = 3 / (requiredGridsDict[modelName][0])
                elif "6" in varName:
                    minGrids = 6 / (requiredGridsDict[modelName][0])
                elif "12" in varName:
                    minGrids = 12 / (requiredGridsDict[modelName][0])
                if minGrids < 1:
                    raise ValueError
        #
        #  For additive grids, we'll start with zero, otherwise the starting
        #  point is just the original input
        #
        if varName in ["QPF12", "QPF6", "QPF3"]:
            finalGrid = zeros_like(inputGrid)
        else:
            finalGrid = inputGrid
        #
        #  Get Object with all component grids
        #
        tempobj = self._Forecaster__getNewWE(gridType + "_SFC")
        if tempobj is None:
            return None
        #
        #  Get the time range tuples of the existing T grids
        #
        temptrobj = tempobj.getKeys()
        #
        #  Loop through existing grid time ranges
        #
        numtrs = temptrobj.size()
        count = 0
        for i in range(numtrs):
            #
            #  See if this grid time range is inside mtime
            #
            tr = temptrobj.get(i)
            if mtime.contains(tr):
                count += 1
                #
                #  Grab the grid. Allow for change in OB 16.1.1 with try
                #  statement
                #
                try:
                    temp = tempobj.getItem(tr).getNDArray()
                except NameError:
                    temp = tempobj.getItem(tr).__numpy__[0]
                #
                # Calculate the derived grid according to the type
                #
                if varName in [
                    "MaxT",
                    "MaxRH",
                    "TdAft",
                    "PoP12",
                    "PoP6",
                    "PoP3",
                ]:
                    finalGrid = maximum(finalGrid, temp)
                elif varName in ["QPF12", "QPF6", "QPF3"]:
                    finalGrid = finalGrid + temp
                elif varName in ["MinT", "MinRH", "TdMrn"]:
                    finalGrid = minimum(finalGrid, temp)
                else:
                    return None
        #
        #  If the minimum # of grids are present, return the derived grid
        #
        if count >= minGrids:
            return finalGrid
        return None

    # From: ../../methods/BI_LakeSnowParameter/BI_LakeSnowParameter.py
    def BI_LakeSnowParameter(
        self, T850, rh850, rh700, wind850, wind700, ctime
    ):
        spd850, dir850 = wind850
        spd700, dir700 = wind700

        # find the 850mb T weight

        T850 = T850 - 273.15

        weight850 = T850 * -0.075 + 0.225
        weight850 = where(greater(T850, -5), 0, weight850)
        weight850 = where(less_equal(T850, -13), 1.2, weight850)
        weight850 = where(less_equal(T850, -14), 1.5, weight850)
        weight850 = where(less_equal(T850, -15), 1.6, weight850)
        weight850 = where(less_equal(T850, -18), 1.5, weight850)
        weight850 = where(less_equal(T850, -19), 1.2, weight850)
        weight850 = where(less_equal(T850, -20), 0.9, weight850)
        weight850 = where(less_equal(T850, -21), 0.8, weight850)
        weight850 = where(less_equal(T850, -22), 0.7, weight850)

        # find the 850-700mb RH weight

        layerRH = (rh850 + rh700) / 2.0

        weightRH = (0.01 * layerRH) + (0.35 * 1.0)
        weightRH = pow(weightRH, 3)

        weightRH = where(less_equal(weightRH, 0.0), 0.0, weightRH)
        weightRH = where(greater_equal(weightRH, 1.6), 1.6, weightRH)

        # find the 850-700mb wind speed weight

        avgSpd = ((spd850 + spd700) / 2.0) * 1.96

        weightSpd = (avgSpd * 0.022) + 0.6

        weightSpd = where(greater_equal(weightSpd, 1.1), 1.1, weightSpd)

        # determine the LSP by mult the three weights
        LSP = weight850 * weightRH * weightSpd

        return LSP

    # From: ../../methods/BI_LESPoP/BI_LESPoP.py
    def BI_LESPoP(self, PoP, LSP, wind925, wind850, ctime):
        try:
            import LSPeditAreas

            lesdir = LSPeditAreas.lesAreas
        except:
            LogStream.logEvent("  COULD NOT IMPORT LSPeditAreas")
            lesdir = None

        if lesdir is not None:
            # now determine the average 1000-850mb u and v average grid
            # mag/dir925==mag/dir1000

            mag925, dir925 = wind925
            mag850, dir850 = wind850

            (u925, v925) = self._getUV(mag925, dir925)
            (u850, v850) = self._getUV(mag850, dir850)

            uAvg = (u925 + u850) / 2
            vAvg = (v925 + v850) / 2
            # Grab a grid
            p = self.newdb().getItem("PoP_SFC")
            # now loop through each edit area and determine if the wind direction thresholds are met
            found = 0
            for lesArea, dirs in lesdir.iteritems():
                # Determine Names
                primaryArea = lesArea + "_Flow_Primary"
                secondaryArea = lesArea + "_Flow_Secondary"
                if (
                    primaryArea in self._editAreas
                    and secondaryArea in self._editAreas
                ):
                    found = 1
                    # LogStream.logEvent("  Computing for %s"%primaryArea)
                    # If EditAreas for those names exist create editArea
                    eaSlice = p.getEditArea(primaryArea)
                    primaryAreamask = self.BI_getNumpyData(eaSlice)
                    eaSlice = p.getEditArea(secondaryArea)
                    secondaryAreamask = self.BI_getNumpyData(eaSlice)

                    # now find the average wind dir in that area
                    # will need to once again convert to u,v and go from there

                    uAvg_area = secondaryAreamask * uAvg
                    vAvg_area = secondaryAreamask * vAvg

                    # first find the total number of points in the editArea
                    totalPoints = add.reduce(add.reduce(secondaryAreamask))
                    uAvgTotal = add.reduce(add.reduce(uAvg_area))
                    vAvgTotal = add.reduce(add.reduce(vAvg_area))

                    uAvg_Single = uAvgTotal / totalPoints
                    vAvg_Single = vAvgTotal / totalPoints

                    # now determine the avg direction in the edit area

                    u = uAvg_Single
                    v = vAvg_Single
                    RAD_TO_DEG = 57.296083
                    sqrt(u * u + v * v)
                    dir = arctan2(u, v) * RAD_TO_DEG
                    dir = where(greater_equal(dir, 360), dir - 360, dir)
                    dir = where(less(dir, 0), dir + 360, dir)
                    avgDir = dir
                    # print secondaryArea+`avgDir`

                    # now compare the threshold dir and the actual dir

                    dir1, dir2 = dirs

                    if (
                        dir1 > dir2
                    ):  # for directional bounds surrouding due north
                        if (avgDir >= dir1) or (avgDir <= dir2):
                            # run smart tool on individual edit area to determine PoP
                            PoP = where(
                                secondaryAreamask,
                                self.BI_lsppop(LSP, PoP, 0.75, ctime),
                                PoP,
                            )
                            PoP = where(
                                primaryAreamask,
                                self.BI_lsppop(LSP, PoP, 1.0, ctime),
                                PoP,
                            )
                    else:
                        if (avgDir >= dir1) and (avgDir <= dir2):
                            # run smart tool on individual edit area to determine PoP
                            PoP = where(
                                secondaryAreamask,
                                self.BI_lsppop(LSP, PoP, 0.75, ctime),
                                PoP,
                            )
                            PoP = where(
                                primaryAreamask,
                                self.BI_lsppop(LSP, PoP, 1.0, ctime),
                                PoP,
                            )

                    # smooth the final product

            if found > 0:
                PoP = self.BI_smoothpm(PoP, 3)

        return PoP

    # From: ../../methods/BI_lsppop/BI_lsppop.py
    def BI_lsppop(self, LSP, PoP, multiplier, ctime):
        lespop = (
            40.259 * LSP
        ) + 0.18  # just a simple linear regression to fit PoP to LSP
        lespop = where(
            less_equal(LSP, 0.45), 10, lespop
        )  # LSP <= 0.45 -> PoP = 10
        lespop = where(
            less_equal(LSP, 0.25), 0, lespop
        )  # LSP <= 0.25 -> PoP = 0
        lespop = lespop * multiplier  # multiplier for secondary area

        lespop = where(greater_equal(lespop, PoP), lespop, PoP)

        return lespop

    # From: ../../methods/BI_MHGT/BI_MHGT.py
    # ===========================================================================
    #  Calculate the hydrostatic height (m) at the middle of a layer, given an
    #  average temp (C) and average dewpoint (C) in the layer, the pressure (mb)
    #  at the top and bottom of the layer, and the height (m) at the bottom
    #  of the layer.  Intended to be used in an integration of hydrostatic
    #  heights given a starting surface height and temp/dewpoint values in
    #  pressure levels above
    # ===========================================================================
    def BI_MHGT(self, tmpc, dwpc, ptop, pbot, hbot):
        pavg = (ptop + pbot) / 2.0
        scale = self.BI_SCLH(tmpc, dwpc, pavg)
        mhgt = hbot + (scale * log(pbot / ptop))
        return mhgt

    # From: ../../methods/BI_modelTime/BI_modelTime.py
    def BI_modelTime(self):
        modelTime = self.newdb().getModelTime()
        modelTime = AbsTime.AbsTime(modelTime).unixTime()
        return modelTime

    # From: ../../methods/BI_offset/BI_offset.py
    # ===========================================================================
    #  BI_offset - Gets a copy of array that is shifted x,y gridpoints.  The
    #  edge points that are unknown are set to -9999.0.  Used in smoothing -
    #  originally taken from baseline NAM12 SmartInit (Tim Barker, WFO BOI)
    # ===========================================================================
    def BI_offset(self, a, x, y):
        sy1, sy2 = self.BI_getindicies(y, a.shape[0])
        sx1, sx2 = self.BI_getindicies(x, a.shape[1])
        b = self.newGrid(-9999.0, dtype=a.dtype)
        b[sy1, sx1] = a[sy2, sx2]
        return b

    # From: ../../methods/BI_SCLH/BI_SCLH.py
    # ===========================================================================
    #  Calculate Scale Height (m) given temp(C), dewpoint(C) and pressure(mb)
    # ===========================================================================
    def BI_SCLH(self, tmpc, dwpc, pres):
        rdgas = 287.058  #  J / kg * K - gas constant for dry air
        gravity = 9.80665  #  m / s^2
        sclh = (rdgas / gravity) * (self.BI_TVRT(tmpc, dwpc, pres) + 273.15)
        return sclh

    # From: ../../methods/BI_setupBLCube/BI_setupBLCube.py
    def BI_setupBLCube(
        self,
        blTemps,
        blRH,
        blWinds,
        p_SFC,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
        MSLP=0,
        masterPdiff=None,
    ):
        """Get boundary layer cube - cube of values above model surface.
        Controls adding in boundary layer information with model pressure levels
           creates:
              BI_BLT - temperatures (K)
              BI_BLR - relative humidity (% 0-100)
              BI_BLH - height (m)
              BI_BLP - pressure (mb)
              BI_BLW - wind (magnitude kts, direction)
              BI_BLD - dewpoint (K)
              BI_BLE - wetbulb temperature (K) [if desired]

        Modified to permit the use of model MSL pressure when surface pressure
        is not available.  Set the MSLP flag to 1, and a surface pressure will
        be calculated.
        """
        # masterPdiff defines master pressure differences to top of each model
        # boundary layer level. It is hard coded as:
        # [0,30,60,90,120,150,180,210] to account for layers typically sent to
        # WFOs but can be overriden by the caller or the model's __init__
        # method via self.BI_optionsDict['masterPdiff']

        #
        #  check to see if already set up for this time
        #
        if self.BLcubeTime == ctime:
            return
        #
        #  Initialize BL cube as missing
        #
        self.BI_BLH = None
        self.BI_BLP = None
        self.BI_BLT = None
        self.BI_BLR = None
        self.BI_BLW = None
        self.BI_BLD = None
        self.BI_BLE = None
        #
        #  if we do not have all the boundary layer data
        #
        if (
            len(blTemps) != len(blRH)
            or len(blTemps) != len(blWinds)
            or len(blTemps) == 0
        ):
            #  Missing some data - we cannot continue safely
            LogStream.logEvent("Cannot setup BL cube - missing data")
            return
        #
        #  Define master pressure differences to top of each model layer within
        #  boundary layer typically sent to WFOs
        # **  PJ: Seems bad to hard code this. Should be passed in or set up in the
        #  model's __init__ method?
        if not masterPdiff:
            masterPdiff = self.BI_optionsDict["masterPdiff"]
        #
        #  Use whatever boundary layer levels we need
        pdiff = masterPdiff[: len(blTemps)]

        #  This method interleaves BL and pressure levels. Another option is to
        #  just add pressure levels that are above all the boundary layer levels
        if not self.BI_optionsDict.get("interLeaveBL", False):
            self.BI_appendBoundaryLayers(
                blTemps,
                blRH,
                blWinds,
                p_SFC,
                stopo,
                gh_c,
                t_c,
                rh_c,
                wind_c,
                ctime,
                pdiff,
            )
            return
        #
        #  split pressure level wind cube into magnitude and direction
        #
        mag_c = wind_c[0]
        dir_c = wind_c[1]
        dew_c = self.RHDP(t_c - 273.15, rh_c) + 273.15

        #  Convert surface pressure into hPa
        pSFCmb = p_SFC / 100.0

        #  If the pressure passed in is a MSL pressure
        if MSLP == 1:
            #  Compute the station pressure instead
            pSFCmb = self.BI_stnPres(pSFCmb, blTemps[0], stopo)

        #  Ensure resulting suface pressure is "reasonable"
        #  (default to 1013 mb when computed surface pressure is < 500 mb)
        pSFCmb = where(less(pSFCmb, 500.0), 1013.0, pSFCmb)

        #  Store "final" surface pressure
        self.pSFCmbModel = pSFCmb

        # =======================================================================
        #  Start constructing the new cubes

        p_list = [pSFCmb]
        hbot = stopo
        h_list = [hbot]
        try:
            t_list = [blTemps[0]]
            r_list = [clip(blRH[0], 0.0001, 99.999)]
            m_list = [blWinds[0][0]]
            d_list = [blWinds[0][1]]
            w_list = [self.RHDP(blTemps[0] - 273.15, blRH[0]) + 273.15]
        except:
            t_list = []
            r_list = []
            m_list = []
            d_list = []
            w_list = []

        #  Add all the available boundary layer levels first
        for i in xrange(1, len(blTemps)):
            tavg = blTemps[i]
            tavgc = tavg - 273.15
            ravg = clip(blRH[i], 0.0001, 99.999)
            davgc = self.RHDP(tavgc, ravg)
            ptop = clip(pSFCmb - pdiff[i], 1.0, 1050.0)
            pbot = clip(pSFCmb - pdiff[i - 1], 1.0, 1050.0)
            htop = self.BI_MHGT(tavgc, davgc, ptop, pbot, hbot)

            t_list.append(tavg)
            h_list.append((hbot + htop) / 2.0)
            wind = blWinds[i]
            m_list.append(wind[0])
            d_list.append(wind[1])
            p_list.append((pbot + ptop) / 2.0)
            r_list.append(ravg)
            w_list.append(davgc + 273.15)

            hbot = htop
        #
        #  Now that boundary layer is done, add in "significant" model levels.
        #
        for i in xrange(gh_c.shape[0]):
            h_list.append(gh_c[i])
            t_list.append(t_c[i])
            p_list.append(self.empty() + self.pres[i])
            m_list.append(mag_c[i])
            d_list.append(dir_c[i])
            r_list.append(rh_c[i])
            w_list.append(dew_c[i])

        #  Convert these lists into Python Numeric/numpy arrays
        self.BI_BLH = array(h_list)
        self.BI_BLP = array(p_list)
        self.BI_BLT = array(t_list)
        self.BI_BLR = array(r_list)
        mags = array(m_list)
        dirs = array(d_list)
        self.BI_BLW = (mags, dirs)
        self.BI_BLD = array(w_list)
        if self.BI_optionsDict["useWetBulb"]:
            self.BI_BLE = self.Wetbulb(
                self.BI_BLT - 273.15, self.BI_BLR, self.BI_BLP
            )
        #
        #  Finally sort all these data using pressure as vertical coordinate.
        #  This will interweave the boundary layer data among the isobaric data
        #  properly.  This technique was developed by Tom LeFebvre (GSD), and
        #  only works on AWIPS2.
        #

        ##        LogStream.logEvent(repr(self.BI_BLP.shape))

        #  Get the "correct" order of levels at each individual point
        sortedIndices = argsort(self.BI_BLP, axis=0)
        sortedIndices = sortedIndices[::-1,]
        height, row, col = indices(self.BI_BLP.shape)

        # -------------------------------------------------------------------
        #  Sort each of the final cubes into the "correct" order

        #  Geopotential height
        self.BI_BLH = self.BI_BLH[sortedIndices, row, col]

        #  Pressure
        self.BI_BLP = self.BI_BLP[sortedIndices, row, col]

        #  Temperature
        self.BI_BLT = self.BI_BLT[sortedIndices, row, col]

        #  Relative humidity
        self.BI_BLR = self.BI_BLR[sortedIndices, row, col]

        #  Wind
        mags = mags[sortedIndices, row, col]
        dirs = dirs[sortedIndices, row, col]
        self.BI_BLW = (mags, dirs)

        #  Dew point
        self.BI_BLD = self.BI_BLD[sortedIndices, row, col]

        #  Wet-bulb temperature
        if self.BI_optionsDict["useWetBulb"]:
            self.BI_BLE = self.BI_BLE[sortedIndices, row, col]

        # Left over from original ErInitsConfig. Non of the variable are used
        #        #-------------------------------------------------------------------
        #        #  Locate the real topography in model height data.  Using the
        #        #  Standard Atmosphere, find the surface pressure of the "real"
        #        #  topography.
        #
        #        #  First find the vertical index of first level above the model topo
        #        allIndices = indices(self.BI_BLH.shape)[0] * (self.BI_BLP > pSFCmb)
        #        self.modelSfcIndex = allIndices.max(axis=0) + 1
        #
        #        #  Now find the vertical index of first level above the actual topo
        #        allIndices = indices(self.BI_BLH.shape)[0] * (self.BI_BLH < topo)
        #        self.realSfcIndex = allIndices.max(axis=0) + 1
        #
        #        #  Now "correct" the surface pressure of the actual topo
        #        exponent = (9.80665 * 28.9644 / 8.31432 / 6.50 )
        #        pSfc = 1013.25 * ( 288.15 / (288.15 + (0.0065 * topo))) ** exponent
        #
        #        #  Set aside this pressure for later
        #        self.pSFCmbTopo = pSfc

        #  Set the model time for these cubes
        self.BLcubeTime = ctime
        return

    # From: ../../methods/BI_setupClimoQPF/BI_setupClimoQPF.py
    # ===========================================================================
    #  BI_setupClimoQPF - fills self.climoQPFGrids with the climo QPF grids for
    #  each month so that BI_getClimoQPF can interpolate to any particular date.
    #  Also read in the FillPrism edit area mask if it is available.
    # ===========================================================================
    def BI_setupClimoQPF(self):
        LogStream.logEvent("Loading Climo QPF grids")

        #  Define:climoQPFGrids array to hold monthly climo QPF grids
        #         climoQPF dictionary to hold cache of climo QPF for particular
        #                                     dates already calculated
        #         fillMaskPrism       to hold edit area mask
        self.climoQPFGrids = 12 * [None]
        self.climoQPF = {}
        self.fillMaskPrism = None

        #  Get the PRISM database
        prismdb = self.getDb(
            "%s_GRID_D2D_PRISMClimo_19700101_0000" % (self._siteID)
        )

        if prismdb is None:
            LogStream.logEvent("can't get PRISM db")
        else:
            #  Get the climo QPF
            climoQPFwe = prismdb.getItem("tp_SFC")

            #  Get the timeRanges for each of the 12 monthly grids
            timeranges = climoQPFwe.getKeys()  # Java time ranges
            for i in xrange(timeranges.size()):
                tr = timeranges.get(i)
                gridslice = climoQPFwe.getItem(tr)

                #  Get this data in a numpy format
                npArray = self.BI_getNumpyData(gridslice)

                self.climoQPFGrids[tr.getStart().getMonth()] = npArray

            #  See if there is an area defined to fill in PRISM data
            try:
                ea = climoQPFwe.getEditArea("FillPrism")
                self.fillMaskPrism = self.BI_getNumpyData(ea)
            except:
                LogStream.logEvent("Could not retrieve FillPrism edit area")

        return

    # From: ../../methods/BI_skyFromRH/BI_skyFromRH.py
    def BI_skyFromRH(self, rh_c, gh_c, topo, p_SFC):
        p_SFC = p_SFC / 100  # convert surfp to milibars
        x = 78  # delta x (85km - 850km)

        #  Define a percentage of f100 to use as a filter (0.0 - 1.0)
        #  Remember f100 is an exponential function, so changes will be more
        #  pronounced in the 0.5-1.0 range than the 0.0-0.5 range.
        percent = 0.37

        gh_cube = gh_c[1:-1, :, :]
        rh_cube = rh_c[1:-1, :, :]
        # Make a pressure cube
        pmb = ones(gh_cube.shape)
        for i in xrange(gh_cube.shape[0]):
            pmb[i] = self.pres[i + 1]

        pp = pmb / p_SFC
        pp = clip(pp, 0.1, 1.0)
        fmax = 78.0 + x / 15.5
        f100 = where(
            pp < 0.7,
            fmax * (pp - 0.1) / 0.6,
            30.0 + (1.0 - pp) * (fmax - 30.0) / 0.3,
        )
        c = 0.196 + (0.76 - x / 2834.0) * (1.0 - pp)

        #  Compute critical RH threshold to use as a filter
        #  Note (percent * f100)/f100 = percent
        try:
            rhCrit = log(percent) * c + 1.0
        except:
            rhCrit = 0.0

        #  Ensure "critical RH" is valid
        rhCrit = clip(rhCrit, 0.0, 1.0)

        c = (rh_cube / 100.0 - 1.0) / c
        c = exp(c)
        f = minimum(f100 * c, 100.0)

        #  Where RH is less than the critical value, set it to 0 contribution
        f = where(less(rh_cube / 100.0, rhCrit), 0.0, f)

        f[4] = f[4] * 0.25
        f = f / 100.0
        sky = f[0]
        for i in xrange(1, f.shape[0]):
            sky = sky + f[i] - sky * f[i]
        sky = self.BI_smoothpm(sky, 3)
        return sky * 100.0

    # From: ../../methods/BI_skyPoPCheck/BI_skyPoPCheck.py
    ################################################################################
    #  Methods used to derive Sky cover
    ################################################################################

    # ===========================================================================
    #   BI_skyPoPCheck - Ensures fractional sky cover is a certain amount
    #   when compared to PoP.
    # ===========================================================================
    def BI_skyPoPCheck(self, sky, PoP):
        #  PoP vs Sky check. Equation ensures sky is a certain value depending
        #  on the PoP. Some examples:
        #  PoP: 15, Sky: 40
        #  PoP: 40, Sky: 55
        #  PoP: 55, Sky: 70
        #  PoP: 75, Sky: 85
        #  PoP: 90, Sky: 100
        skycheck = 33.888 * exp(0.0123 * PoP)

        #  Ensure sky cover meets of exceeds minimum value determined by PoP
        newSky = where(less(sky, skycheck), skycheck, sky)

        #  Replace existing sky
        sky = where(greater_equal(PoP, 15), newSky, sky)

        #  Smooth the sky cover a little
        sky = self.BI_smoothpm(sky, 3)

        #  Return the completed sky - make sure it is valid
        return clip(sky, 0, 100)

    # From: ../../methods/BI_Smooth/BI_Smooth.py
    # ===========================================================================
    #  BI_Smooth - used to smooth a 2-D grid.  Can optionally specify a
    #  smoothing factor, the number of times to smooth, as well as an an area
    #  mask where smoothing should be applied.  Original taken from FillTool
    #  (John Roczbicki, WFO BUF).
    # ===========================================================================
    def BI_Smooth(self, grid, factor=3, times=3, fillMask=None):
        # make a copy of the original grid
        a = grid[:][:]

        # Smooth a 3 times in succession to wipe out any noise
        for x in range(times):
            a = self.BI_SmoothGrid(grid, factor)

        # in the "filled-in" area, replace the current data with
        # the smoothed data
        grid = where(fillMask, a, grid)

        return grid

    # From: ../../methods/BI_SmoothGrid/BI_SmoothGrid.py
    # ===========================================================================
    #  BI_SmoothGrid - used to smooth a 2-D grid once.  Can optionally specify
    #  a smoothing factor (less than 3 simply returns unsmoothed grid) -
    #  taken from FillTool (John Roczbicki, WFO BUF)
    # ===========================================================================
    def BI_SmoothGrid(self, grid, factor=3):
        # This code is essentially the NumericSmooth example
        # smart tool customized for our purposes.
        if factor < 3:
            return grid

        half = int(factor) / 2
        sg = zeros(grid.shape, float64)
        count = zeros(grid.shape, float64)
        gridOfOnes = ones(grid.shape, float64)

        for y in range(-half, half + 1):
            for x in range(-half, half + 1):
                if y < 0:
                    yTargetSlice = slice(-y, None, None)
                    ySrcSlice = slice(0, y, None)
                if y == 0:
                    yTargetSlice = slice(0, None, None)
                    ySrcSlice = slice(0, None, None)
                if y > 0:
                    yTargetSlice = slice(0, -y, None)
                    ySrcSlice = slice(y, None, None)
                if x < 0:
                    xTargetSlice = slice(-x, None, None)
                    xSrcSlice = slice(0, x, None)
                if x == 0:
                    xTargetSlice = slice(0, None, None)
                    xSrcSlice = slice(0, None, None)
                if x > 0:
                    xTargetSlice = slice(0, -x, None)
                    xSrcSlice = slice(x, None, None)

                target = [yTargetSlice, xTargetSlice]
                src = [ySrcSlice, xSrcSlice]
                sg[target] = sg[target] + grid[src]
                count[target] = count[target] + gridOfOnes[src]
        return sg / count

    # From: ../../methods/BI_smoothpm/BI_smoothpm.py
    def BI_smoothpm(self, grid, k, mask=None, onlyMaskedData=1):
        """smoothpm - smooths grid by averaging over plus and minus k gridpoints, which
        means an average over a square 2k+1 gridpoints on a side.

        If mask is specified (an integer grid of 1s and 0s), only modify points that
        have mask=1, not any other points.

        If a mask is specified, the default is for only the points inside the mask to
        influence the smoothed points.  this keeps data from outside the mask
        "bleeding" into the area being smoothed.  If, however, you want the data
        outside the mask to impact the smoothed data, set onlyMaskedData=0 (it defaults
        to 1)

        Near the edges of the grid, the average is over fewer points than in the center
        of the grid - because some of the points in the averaging window would be off
        the grid. It just averages over the points that it can.  For example, on the
        edge gridpoint - it can only come inside k points - so the average is over only
        k+1 points in that direction (though over all 2k+1 points in the other
        direction - if possible)

        This is much faster than shifting the grid multiple times and adding them up.
        Instead it uses the cumsum function in numpy - which gives you cumulative sum
        across a row/column.  Total across the 2k+1 points is the cumsum at the last
        point minus the cumsum at the point before the first point. Only edge points
        need special handling - and the cumsum is useful there too.
        """

        k = int(k)  # has to be integer number of gridpoints
        if k < 1:  # has to be a positive number of gridpoints
            return grid
        if len(grid.shape) != 2:  # has to be a 2-d grid
            return grid
        (ny, nx) = grid.shape
        k2 = k * 2
        #
        #  Remove the minimum and divide by the range from the grid so
        #  that when cumsum accumulates the sum over a full row or
        #  column that it doesn't get so big that precision is lost
        #  might be lost.  This makes the 'gridmin' grid have all points
        #  ranging from 0 to 1.
        #
        fullmin = minimum.reduce(minimum.reduce(grid))
        fullmax = maximum.reduce(maximum.reduce(grid))
        fullrange = fullmax - fullmin
        if fullrange < 0.001:
            fullrange = 0.001
        gridmin = (grid - fullmin) / fullrange
        #
        #  When there is no mask the code is much simpler
        #
        if (mask is None) or (onlyMaskedData == 0):
            #
            #  Average over the first (y) dimension - making the 'mid' grid
            #
            mid = grid * 0.0
            c = cumsum(gridmin, 0)
            nym1 = ny - 1
            midy = int((ny - 1.0) / 2.0)
            ymax = min(k + 1, midy + 1)
            #
            #  Handle the edges
            #
            for j in range(ymax):
                jk = min(j + k, nym1)
                jk2 = max(nym1 - j - k - 1, -1)
                mid[j, :] = c[jk, :] / float(jk + 1)
                if jk2 == -1:
                    mid[nym1 - j, :] = c[nym1, :] / float(jk + 1)
                else:
                    mid[nym1 - j, :] = (c[nym1, :] - c[jk2, :]) / float(jk + 1)
            #
            #  The really fast part for the middle of the grid
            #
            if (k + 1) <= (ny - k):
                mid[k + 1 : ny - k, :] = (
                    c[k2 + 1 :, :] - c[: -k2 - 1, :]
                ) / float(k2 + 1)
            #
            #  Average over the second (x) dimension - making the 'out' grid
            #
            c = cumsum(mid, 1)
            out = grid * 0.0
            nxm1 = nx - 1
            midx = int((nx - 1.0) / 2.0)
            xmax = min(k + 1, midx + 1)
            #
            #  Handle the edges
            #
            for j in range(xmax):
                jk = min(j + k, nxm1)
                jk2 = max(nxm1 - j - k - 1, -1)
                out[:, j] = c[:, jk] / float(jk + 1)
                if jk2 == -1:
                    out[:, nxm1 - j] = c[:, nxm1] / float(jk + 1)
                else:
                    out[:, nxm1 - j] = (c[:, nxm1] - c[:, jk2]) / float(jk + 1)
            #
            #  The really fast part for the middle of the grid
            #
            if (k + 1) <= (nx - k):
                out[:, k + 1 : nx - k] = (
                    c[:, k2 + 1 :] - c[:, : -k2 - 1]
                ) / float(k2 + 1)
            #
            #  Multiply by the range and add the minimum back in
            #
            out = (out * fullrange) + fullmin
            if (onlyMaskedData == 0) and (mask is not None):
                out[mask < 1] = grid[mask < 1]
        #
        #  When there is a Mask specified, it makes the code a bit more
        #  difficult. We have to find out how many points were in each
        #  cumsum value - and we have to deal with possible divide-by-zero
        #  errors for points where no masked points were in the average
        #
        else:
            #
            #  Sum over the first (y) dimension - making the 'mid' grid
            #
            mask = clip(mask, 0, 1)
            gridmin1 = where(mask, gridmin, 0)
            mid = grid * 0.0
            midd = grid * 0.0
            c = cumsum(gridmin1, 0)
            d = cumsum(mask, 0)
            nym1 = ny - 1
            midy = int((ny - 1.0) / 2.0)
            ymax = min(k + 1, midy + 1)
            #
            #  Handle the edges
            #
            for j in range(ymax):
                jk = min(j + k, nym1)
                jk2 = max(nym1 - j - k - 1, -1)
                mid[j, :] = c[jk, :]
                midd[j, :] = d[jk, :]
                if jk2 == -1:
                    mid[nym1 - j, :] = c[nym1, :]
                    midd[nym1 - j, :] = d[nym1]
                else:
                    mid[nym1 - j, :] = c[nym1, :] - c[jk2, :]
                    midd[nym1 - j, :] = d[nym1, :] - d[jk2, :]
            #
            #  The really fast part for the middle of the grid
            #
            if (k + 1) <= (ny - k):
                mid[k + 1 : ny - k, :] = c[k2 + 1 :, :] - c[: -k2 - 1, :]
                midd[k + 1 : ny - k, :] = d[k2 + 1 :, :] - d[: -k2 - 1, :]
            #
            #  Sum over the second (x) dimension - and divide by
            #  the number of points (but make sure number of points
            #  is at least 1) - making the 'out' grid
            #
            c = cumsum(mid, 1)
            d = cumsum(midd, 1)
            out = grid * 0.0
            nxm1 = nx - 1
            midx = int((nx - 1.0) / 2.0)
            xmax = min(k + 1, midx + 1)
            #
            #  Handle the edges
            #
            for j in range(xmax):
                jk = min(j + k, nxm1)
                jk2 = max(nxm1 - j - k - 1, -1)
                out[:, j] = c[:, jk] / maximum(d[:, jk], 1)
                if jk2 == -1:
                    out[:, nxm1 - j] = c[:, nxm1] / maximum(d[:, nxm1], 1)
                else:
                    out[:, nxm1 - j] = (c[:, nxm1] - c[:, jk2]) / maximum(
                        (d[:, nxm1] - d[:, jk2]), 1
                    )
            #
            #  The really fast part for the middle of the grid
            #
            if (k + 1) <= (nx - k):
                out[:, k + 1 : nx - k] = (
                    c[:, k2 + 1 :] - c[:, : -k2 - 1]
                ) / maximum((d[:, k2 + 1 :] - d[:, : -k2 - 1]), 1)
            #
            #  Multiply by the range and add the minimum back in
            #
            out = (out * fullrange) + fullmin
            out[mask < 1] = grid[mask < 1]
        return out

    # From: ../../methods/BI_stnPres/BI_stnPres.py
    # ===========================================================================
    #  Calculate station pressure (mb) given temperature(K) and
    #  MSL pressure (mb or Pa)
    # ===========================================================================
    def BI_stnPres(self, pmsl_SFC, t_SFC, topo):
        #  Convert MSL pressure to mb/hPa - if it is not already in those units
        pmsl_SFC = where(greater(pmsl_SFC, 1100.0), pmsl_SFC / 100.0, pmsl_SFC)

        #  Calculate the station pressure
        return pmsl_SFC * exp(-1.0 * topo / (t_SFC * 29.272))  #  was 29.263

    # From: ../../methods/BI_ThickSnowRatio/BI_ThickSnowRatio.py
    # =======================================================================================
    # Craven SnowRatio based off thicknesses
    # =======================================================================================
    def BI_ThickSnowRatio(self, T, MaxTAloft, gh_MB1000, gh_MB500):
        sRatio = self.empty()
        thick = gh_MB500 - gh_MB1000
        #
        sRatio = where(greater(thick, 5490), 0.0, sRatio)
        sRatio = where(
            logical_and(less_equal(thick, 5490), greater(thick, 5460)),
            2.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5460), greater(thick, 5400)),
            5.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5400), greater(thick, 5370)),
            8.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5370), greater(thick, 5340)),
            10.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5340), greater(thick, 5310)),
            12.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5310), greater(thick, 5280)),
            15.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5280), greater(thick, 5220)),
            17.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5220), greater(thick, 5160)),
            20.0,
            sRatio,
        )
        sRatio = where(
            logical_and(less_equal(thick, 5160), greater(thick, 20)),
            25.0,
            sRatio,
        )
        #
        if MaxTAloft is not None:
            sRatio = where(
                logical_or(
                    greater_equal(T, 35.6), greater_equal(MaxTAloft, 0.0)
                ),
                0,
                sRatio,
            )
        else:
            sRatio = where(greater_equal(T, 35.6), 0.0, sRatio)
        #
        sRatio = self.BI_smoothpm(sRatio, 3)
        return sRatio

    # From: ../../methods/BI_TMSTLev/BI_TMSTLev.py
    # ==========================================================================
    #  TMSTLev - Calculate parcel temp (K) given thetae (K) pressure (mb) and
    #            guess temperature (K)  - for a single level only - NOT a cube
    # --------------------------------------------------------------------------
    def BI_TMSTLev(self, thte, pres, tguess):
        tg = ones(thte.shape) * tguess
        teclip = clip(thte - 270.0, 0.0, 5000.0)
        #
        #  if guess temp is 0 - make a more reasonable guess
        #
        tg = where(
            less(tg, 1),
            (thte - 0.5 * teclip**1.05) * (pres / 1000.0) ** 0.2,
            tg,
        )
        epsi = 0.01
        tgnu = tg - 273.15
        #
        #  Correct the temp up to 100 times.  Typically this takes
        #  less than 5 iterations
        #
        for i in range(1, 100):
            tgnup = tgnu + 1.0
            tenu = self.THTE(pres, tgnu, tgnu)
            tenup = self.THTE(pres, tgnup, tgnup)
            cor = (thte - tenu) / (tenup - tenu)
            tgnu = tgnu + cor
            #
            #  get the maximum correction we made this time
            #  and if it is less than epsi - then we are close
            #  enough to stop.
            #
            acor = abs(cor)
            mcor = maximum.reduce(maximum.reduce(acor))
            if mcor < epsi:
                return tgnu + 273.15
        return tgnu + 273.15

    # From: ../../methods/BI_TVRT/BI_TVRT.py
    # ===========================================================================
    #  Calculate Virtual temperature (C) given temp(C), dewpoint (C)
    #  and pressure(mb)
    # ===========================================================================
    def BI_TVRT(self, tmpc, dwpc, pres):
        mixrscale = self.MIXR(dwpc, pres) * 0.001
        tmpk = tmpc + 273.15
        tvrk = tmpk * (1.0 + (mixrscale / 0.62197)) / (1.0 + mixrscale)
        tvrt = tvrk - 273.15
        return tvrt

    # From: ../../methods/BI_vaprtf/BI_vaprtf.py
    def BI_vaprtf(self, tf):
        tc = (tf - 32.0) * 5.0 / 9.0
        vapr = 6.112 * exp((17.67 * tc) / (tc + 243.5))
        return vapr

    # From: ../../methods/BI_weightSnowLevel/BI_weightSnowLevel.py
    # ==========================================================================
    #  weightSnowLevel - compute a weighting for the snowLevel based on
    #                    the average column RH
    #
    def BI_weightSnowLevel(self, gh_c, rh_c, topo):
        #  To handle dry atmospheres, we need to look at the
        #  average RH to determine if we should compute the snow
        #  level from the dry bulb (i.e. freezing level), wet bulb
        #  or a mix of the two.
        #
        #  Compute the average RH in the column at each grid point.
        #  Only consider grid points above ground, and don't worry
        #  about the boundary layer grids.

        # ignore points that are below ground
        rhavg = where(less(gh_c, topo), -1, rh_c)
        # count the points that are above ground
        count = where(not_equal(rhavg, -1), 1, 0)
        rhavg = where(equal(rhavg, -1), 0, rhavg)

        # reduce the columns so that we have a 2-D array
        count = add.reduce(count, 0)
        rhavg = add.reduce(rhavg, 0)
        ## compute the avg RH at each grid point
        rhavg = where(count, rhavg / (count + 0.001), 0)

        # print "rhavg", rhavg[0][0]

        # MH - Convert RH into a %
        rhavg = rhavg / 100.0

        # MH - Coefficients for the polynomial
        C5 = 4.94123
        C4 = -13.17102
        C3 = 10.64039
        C2 = -2.60176
        C1 = 1.19052
        C0 = 0.0

        poly5 = C5 * pow(rhavg, 5)
        poly4 = C4 * pow(rhavg, 4)
        poly3 = C3 * pow(rhavg, 3)
        poly2 = C2 * pow(rhavg, 2)
        poly1 = C1 * pow(rhavg, 1)

        # MH - Build the polynomial
        poly = poly5 + poly4 + poly3 + poly2 + poly1 + C0
        weight = clip(poly, 0.0, 1.0)

        return weight

    # From: ../../methods/BI_WetbulbLev/BI_WetbulbLev.py
    # ==========================================================================
    # WetbulbLev - calculate a grid of Wetbulb temperatures (K) based on
    #              temperature (C),  RH (% 0-100), and pressure (mb). This is
    #              for a single level only - NOT a cube.
    # --------------------------------------------------------------------------
    def BI_WetbulbLev(self, tc, rh, pres):
        dpc = self.RHDP(tc, rh)
        thte = self.THTE(pres, tc, dpc)
        wetbk = self.BI_TMSTLev(thte, pres, 0)
        return wetbk

    # From: DR18576.py


# NIC version of JSmartUtils for DR 18576
#
# Provides Java implementations of common smart utility functions
# to boost performance.
#
#
#     SOFTWARE HISTORY
#
#    Date            Ticket#       Engineer       Description
#    ------------    ----------    -----------    --------------------------
#    01/14/2013       #1497        njensen        Initial Creation.
#    10/12/2015       #4967        randerso       Updated for new JEP API
#
#

import jep
import numpy
from com.raytheon.uf.common.dataplugin.gfe.util import (
    SmartUtils as JavaSmartUtils,
)


def __getMaskIndiciesForJava(mask):
    flatMask = mask.flat  # flatten the array
    flatIndicies = numpy.nonzero(flatMask)  # get the indicies of the set cells
    ysize = mask.shape[1]
    indexes = []
    # convert the flat incicies to the x, y indicies
    for i in flatIndicies:
        indexes.append((i / ysize, i % ysize))

    #  Make two new jarrays to hold the final coordinate tuples
    size = len(indexes[0][0])
    xcoords = jep.jarray(size, jep.JINT_ID)
    ycoords = jep.jarray(size, jep.JINT_ID)

    # ===================================================================
    #  Convert the coordinates from a tuple of numpy arrays to a list of
    #  coordinate tuples

    for index in xrange(size):
        try:
            x = indexes[0][0][index]
            y = indexes[0][1][index]
            xcoords[index] = int(x)
            ycoords[index] = int(y)
        except Exception as e:
            print(e)

    return xcoords, ycoords


# Originally added for use by BOX SmartInitUtils.SIU_fillEditArea() to speed up their smartInits
# Should be used by other smartInits that need similar functionality
def fillEditArea(grid, fillMask, borderMask):
    editPointsX, editPointsY = __getMaskIndiciesForJava(fillMask)
    borderPointsX, borderPointsY = __getMaskIndiciesForJava(borderMask)

    gridObj = JavaSmartUtils.fillEditArea(
        grid,
        grid.shape[1],
        grid.shape[0],
        editPointsY,
        editPointsX,
        borderPointsY,
        borderPointsX,
    )

    # DR18576    retObj = gridObj.getNDArray()
    # DR18576    return retObj
    return gridObj
