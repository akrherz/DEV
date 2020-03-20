################################################################################
# SVN: $Rev: 11251 $  $Date: 2016-12-20 16:19:45 +0000 (Tue, 20 Dec 2016) $
# $URL: https://collaborate.nws.noaa.gov/svn/scp/Gfe/Smartinits/NwsInitsConfig/branches/4.2/smartinits/NWS_NAM12.py $
################################################################################
# NWS version of NAM12 created by NWS_NAM12/make-NWS_NAM12.sh
#
# This file is under NSI configuration management. DO NOT CHANGE
#  Copy methods you wish to change into the Local_NAM12 module and make desired
#  changes there.
#
from numpy import *

# From: NWS_NAM12.hdr

from Init import *
from siteConfig import *

import time, sys, calendar
import BaseInit


def main():
    NAM12().run()


class NAM12(BaseInit.BaseInit):

    # From: NWS_NAM12.__init__.py
    def __init__(self, srcName="NAM12", dstName=None):
        BaseInit.BaseInit.__init__(self, srcName, dstName)

    """XX_NAM12 SmartInit Methods"""

    # From: ../../methods/levels/NAM12.levels.py
    # ===========================================================================
    #  Define available levels within this model
    # ===========================================================================
    def levels(self):
        return [
            "MB1000",
            "MB975",
            "MB950",
            "MB925",
            "MB900",
            "MB875",
            "MB850",
            "MB825",
            "MB800",
            "MB775",
            "MB750",
            "MB725",
            "MB700",
            "MB675",
            "MB650",
            "MB625",
            "MB600",
            "MB575",
            "MB550",
            "MB525",
            "MB500",
            "MB450",
            "MB400",
            "MB350",
        ]

    # From: ../../methods/rhWaterToIce/rhWaterToIce.py
    def rhWaterToIce(self, rhWaterGrid, temp):
        tempInK = temp + 273.15
        naturalLogTemp = math.log(tempInK)
        vaporPressureWRTwater = math.exp(
            53.67957 - (6743.769 / tempInK) - 4.8451 * naturalLogTemp
        )
        satVaporPressureWRTice = math.exp(
            23.33086 - (6111.72784 / tempInK) + 0.15215 * naturalLogTemp
        )
        rhIceGrid = (
            rhWaterGrid * vaporPressureWRTwater / satVaporPressureWRTice
        )

        return rhIceGrid

    # From: ../../methods/probIceForTemp/probIceForTemp.py
    def probIceForTemp(self, temp):
        probList = [30, 40, 50, 60, 70, 75, 80]
        if temp == 8:
            prob = 30
        elif temp == 9:
            prob = 40
        elif temp == 10:
            prob = 50
        elif temp == 11:
            prob = 60
        elif temp == 12:
            prob = 70
        elif temp == 13:
            prob = 75
        elif temp == 14:
            prob = 85
        elif temp == 15:
            prob = 100
        return prob

    # From: ../../methods/calcFzLevel/XX_NAM12.calcFzLevel.py
    # ==========================================================================
    # Many of the models have had a freezing level in the gh field.
    # ==========================================================================
    def calcFzLevel(self, gh_FRZ):
        return gh_FRZ * 3.28

    # From: ../../methods/calcHaines/calcHaines.py
    # --------------------------------------------------------------------------
    # Haines Index
    # ---------------------------------------- ----------------------------------
    def calcHaines(self, t_c, rh_c):
        return self.BI_hainesIndex(
            self.BI_optionsDict["HainesLevel"], t_c, rh_c
        )

    # From: ../../methods/calcMaxRH/calcMaxRH.py
    # ===========================================================================
    #  MaxRH is simply maximum of all RH grids during period
    # ===========================================================================
    def calcMaxRH(self, RH, MaxRH, mtime):
        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids("MaxRH", RH, "RH", mtime, None)
        except:
            pass

        if MaxRH is None:
            return RH
        return maximum(MaxRH, RH)

    # From: ../../methods/calcMaxTAloft/calcMaxTAloft.py
    def calcMaxTAloft(self, t_c, gh_c, topo):
        MaxTAloft = self.newGrid(-50)
        self.HeightMaxTAloft = self.empty()
        prevTemp = self.empty()
        prevTemp = 10000
        timesThruLoop = 0
        for i in xrange(len(t_c) - 1):  # for each pressure level
            self.maskAboveGround = gh_c[i] > topo
            mask2kFTAboveGround = gh_c[i] > topo + 600
            temp = t_c[i] - 273.15  # Convert to C
            lapseRate = t_c[i] - prevTemp
            if timesThruLoop == 0:
                startMaxTAloftMask = lapseRate > 0
            else:
                startMaxTAloftMask = (lapseRate > 0) | startMaxTAloftMask
            Mask = self.maskAboveGround & (temp > MaxTAloft)
            self.HeightMaxTAloft[Mask] = gh_c[i][Mask]
            Mask = (
                self.maskAboveGround & startMaxTAloftMask & (temp > MaxTAloft)
            )
            MaxTAloft[Mask] = temp[Mask]
            Mask = mask2kFTAboveGround & (temp > MaxTAloft)
            MaxTAloft[Mask] = temp[Mask]
            prevTemp = t_c[i]
            timesThruLoop = timesThruLoop + 1

        MaxTAloft = self.BI_smoothpm(MaxTAloft, 3)
        return MaxTAloft

    # From: ../../methods/calcMaxTwAloft/calcMaxTwAloft.py
    def calcMaxTwAloft(self, t_c, rh_c, gh_c, stopo):
        MaxTwAloft = self.newGrid(-50)
        prevTemp = 10000
        timesThruLoop = 0
        for i in xrange(len(t_c) - 1):  # for each pressure level
            pmb = clip(self.newGrid(self.pres[i] - 2.0), 1, 1050)
            tc = clip(t_c[i] - 273.15, -120, 60)
            rhc = clip(rh_c[i], 0.5, 99.5)
            tw = self.BI_WetbulbLev(tc, rhc, pmb) - 273.15
            maskAboveGround = gh_c[i] > stopo
            mask2kFTAboveGround = gh_c[i] > stopo + 600
            lapseRate = tw - prevTemp
            if timesThruLoop == 0:
                startMaxTwAloftMask = lapseRate > 0
            else:
                startMaxTwAloftMask = (lapseRate > 0) | startMaxTwAloftMask
            Mask = maskAboveGround & startMaxTwAloftMask & (tw > MaxTwAloft)
            MaxTwAloft[Mask] = tw[Mask]
            Mask = mask2kFTAboveGround & (tw > MaxTwAloft)
            MaxTwAloft[Mask] = tw[Mask]
            prevTemp = tw
            timesThruLoop = timesThruLoop + 1

        MaxTwAloft = self.BI_smoothpm(MaxTwAloft, 3)
        return MaxTwAloft

    # From: ../../methods/calcMaxT/calcMaxT.py
    def calcMaxT(self, T, MaxT, mtime):
        """Take the max of the available T grids in the available time range."""
        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids("MaxT", T, "T", mtime, None)
        except:
            pass

        if MaxT is None:
            return T

        return maximum(MaxT, T)

    # From: ../../methods/calcMinRH/calcMinRH.py
    # ===========================================================================
    #  MinRH is simply minimum of all RH grids during period
    # ===========================================================================
    def calcMinRH(self, RH, MinRH, mtime):
        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids("MinRH", RH, "RH", mtime, None)
        except:
            pass

        if MinRH is None:
            return RH
        return minimum(MinRH, RH)

    # From: ../../methods/calcMinT/calcMinT.py
    def calcMinT(self, T, MinT, mtime):
        """Take the min of the available T grids in the available time range."""
        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids("MinT", T, "T", mtime, None)
        except:
            pass

        if MinT is None:
            return T

        return minimum(MinT, T)

    # From: ../../methods/calcMixHgt/lvls.calcMixHgt.py
    def calcMixHgt(
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
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
    ):

        """MixHgt - the height to which a parcel above a 'fire' would rise
        (in height) above ground level (in feet).
    
        Calculated by assuming a parcel above a fire is VERY hot - but the fire
        is very small - so that entrainment quickly makes it only a few degrees
        warmer than the environment.  Ideally would want to consider moisture
        and entrainment - but this is a very simple first guess.
    
        This does NO downscaling - and even smooths the field a little at the
        end.  We have no observations of this - other than at sounding
        locations - so we have no idea what the spatial patterns should look
        like.
        """
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

        BLT = self.BI_BLT
        BLP = self.BI_BLP
        BLTheta = self.ptemp(BLT, BLP)
        BLH = self.BI_BLH
        #
        #  Potential temp of fire 2 degrees warmer than surface parcel
        #
        fireHeat = 2.0
        pSFCmb = p_SFC / 100
        fireTheta = self.ptemp(t_FHAG2 + fireHeat, pSFCmb)
        #
        #  find height the fireTheta crosses the sounding theta
        #
        mixhgt = self.newGrid(-1)
        for i in range(1, BLH.shape[0]):
            hcross = self.linear(
                BLTheta[i], BLTheta[i - 1], BLH[i], BLH[i - 1], fireTheta
            )
            cross = logical_and(
                greater(BLTheta[i], fireTheta), less(mixhgt, 0.0)
            )
            mixhgt = where(cross, hcross, mixhgt)
        mixhgt = where(less(mixhgt, 0.0), BLH[-1], mixhgt)
        #
        #  Change to height above the model topo (in feet)
        #  and smooth a little
        #
        final = (mixhgt - stopo) * 3.28
        final = where(less(pSFCmb, 500), -9999.0, final)
        final = self.BI_smoothpm(final, 2)
        final = clip(final, 0.0, 50000.0)
        return final

    # From: ../../methods/calcPoP12/GeneralPoP.calcPoP12.py
    # --------------------------------------------------------------------------
    # PoP12 - calculated by re-running the PoP algorithm for 12 hour QPF
    # ---------------------------------------------------------------------------
    def calcPoP12(self, PoP, QPF12, topo, ctime):
        if QPF12 is not None:
            PoP12 = self.BI_GeneralPoP(QPF12, topo, ctime)
            PoP12 = self.BI_smoothpm(PoP12, 3)
            return PoP12

    # From: ../../methods/calcPoP6/GeneralPop.calcPoP6.py
    # --------------------------------------------------------------------------
    # PoP6 - calculated by re-running the PoP algorithm for 6 hour QPF
    # ---------------------------------------------------------------------------
    def calcPoP6(self, PoP, QPF6, topo, ctime):
        if QPF6 is not None:
            PoP6 = self.BI_GeneralPoP(QPF6, topo, ctime)
            PoP6 = self.BI_smoothpm(PoP6, 3)
            return PoP6

    # From: ../../methods/calcPoP/GeneralPop.calcPoP.py
    # ===========================================================================
    #  PoP - calculated using a PoP from QPF method, then adjusts the maximum
    #        and minimum levels based on forecast hour
    # ===========================================================================
    def calcPoP(self, QPF, topo, ctime):
        PoP = self.BI_GeneralPoP(QPF, topo, ctime)
        return PoP

    # From: ../../methods/calcPotFreezingRain/calcPotFreezingRain.py
    def calcPotFreezingRain(self, cfrzr_SFC):
        potfreezingrain = cfrzr_SFC * 100
        return potfreezingrain

    # From: ../../methods/calcPotRain/calcPotRain.py
    ### PoWT additions ###
    def calcPotRain(self, crain_SFC):
        potrain = crain_SFC * 100
        return potrain

    # From: ../../methods/calcPotRainShowers/calcPotRainShowers.py
    def calcPotRainShowers(self, crain_SFC):
        potrainshowers = crain_SFC * 100
        return potrainshowers

    # From: ../../methods/calcPotSleet/calcPotSleet.py
    def calcPotSleet(self, cicep_SFC):
        potsleet = cicep_SFC * 100
        return potsleet

    # From: ../../methods/calcPotSnow/calcPotSnow.py
    def calcPotSnow(self, csnow_SFC):
        potsnow = csnow_SFC * 100
        return potsnow

    # From: ../../methods/calcPotSnowShowers/calcPotSnowShowers.py
    def calcPotSnowShowers(self, csnow_SFC):
        potsnowshowers = csnow_SFC * 100
        return potsnowshowers

    # From: ../../methods/calcCloudBasePrimary/calcCloudBasePrimary.py
    def calcCloudBasePrimary(self, topo, rh_c, gh_c):
        self.cloudRH = [
            98.0,
            96.0,
            94.0,
            92.0,
            90.0,
            88.0,
            85.0,
            83.0,
            80.0,
            78.0,
            75.0,
            73.0,
            70.0,
            68.0,
            65.0,
            63.0,
            60.0,
            58.0,
            55.0,
            53.0,
            50.0,
            45.0,
            40.0,
            35.0,
        ]
        MaxCloudBase = 250
        CloudBasePrimary = self.newGrid(MaxCloudBase)
        for i in xrange(rh_c.shape[0]):
            rh = rh_c[i]
            # height = gh_c[i]/0.3048
            height = (gh_c[i] - topo) / 0.3048
            height = where(less(height, 1.0), 0.0, height)
            rh = where(less(height, 1.0), 0.0, rh)
            CloudBasePrimary = where(
                logical_and(
                    equal(CloudBasePrimary, MaxCloudBase),
                    greater_equal(rh, self.cloudRH[i]),
                ),
                height / 100,
                CloudBasePrimary,
            )

        return clip(CloudBasePrimary, 1, 250)

    # From: ../../methods/calcCloudBaseCCL/calcCloudBaseCCL.py
    # Compute Convective Condensation Level for CloudBase estimation.  Used to help with
    # Diurnal CU.  Adopted from GSP's CloudBase_FM_CCL_LCL tool

    def calcCloudBaseCCL(
        self,
        topo,
        T,
        Td,
        t_c,
        rh_c,
        gh_c,
        p_SFC,
        t_BL030,
        t_BL3060,
        rh_BL030,
        rh_BL3060,
    ):
        MaxCloudBase = 250

        dpt_BL030 = self.BI_dewFromTandRH(self.KtoF(t_BL030), rh_BL030)
        dpt_BL3060 = self.BI_dewFromTandRH(self.KtoF(t_BL3060), rh_BL3060)

        # GET vapor pressures
        eT_SFC = self.BI_vaprtf(T)
        eTd_SFC = self.BI_vaprtf(Td)
        e_BL030 = self.BI_vaprtf(dpt_BL030)
        e_BL3060 = self.BI_vaprtf(dpt_BL3060)

        # Mixing Ratios
        wSFC = (0.622 * eTd_SFC) / ((p_SFC / 100.0) - eTd_SFC)
        lastWs = (0.622 * eT_SFC) / ((p_SFC / 100.0) - eT_SFC)
        wBL030 = (0.622 * e_BL030) / ((p_SFC / 100.0) - e_BL030)
        wBL3060 = (0.622 * e_BL3060) / ((p_SFC / 100.0) - e_BL3060)
        #
        #       wBL is the average boundary layer mixing ratio
        wBL = (wSFC + wBL030 + wBL3060) / 3.0
        #
        tempCCL = topo
        lastCCL = topo
        #
        lastHgt = self.newGrid(0)
        #
        for i in xrange(gh_c.shape[0]):
            tK = t_c[i]
            hgt = gh_c[i]
            pres = int(self.levels()[i].split("MB")[1])
            # Due to wBL possibly being about he 925 MIXING RATIO will not
            # start until 925 is hit.
            if pres > 925:
                continue

            maskAboveGround = gh_c[i] > topo
            tC = tK - 273.15
            #           calculate saturation vapor pressure (eS) at this level using the
            #           Bolton (1980) form of the Clausius-Clapeyron Equation
            eS = 6.112 * exp((17.67 * tC) / (tC + 243.5))
            #           Saturation Mixing Ratio
            wS = (0.622 * eS) / (pres - eS)
            #
            #           find all grid boxes where the new Ws is lower than
            #           the boundary layer mixing ratio wBL
            newWsLower = wS < wBL
            #
            #           The CCL is ready to set when the saturation mixing ratio
            #           at the new level is less than the boundary layer mixing
            #           ratio, we are above ground level, and the CCL is still set
            #           at zero.  Set a mask for when this condition is true.
            #
            readyToSet = logical_and(
                newWsLower,
                logical_and(maskAboveGround, less(lastCCL, topo + 1.0)),
            )

            #
            #           perform a linear interpolation between model levels to make an
            #           approximation for the height where the saturation mixing ratio
            #           becomes less than the boundary layer mixing ratio
            #
            hCross = self.linear(wS, lastWs, hgt, lastHgt, wBL)
            #
            #           Find and store the level where temp goes above
            #           freezing, considering only layers above the ground
            #
            tempCCL = where(readyToSet, hCross, tempCCL)
            #
            lastWs = wS
            lastHgt = hgt
            lastCCL = tempCCL
        #
        Mask = tempCCL <= topo
        tempCCL[Mask] = 250
        CCL = ((tempCCL - topo) * 3.2808) / 100.00
        #
        return clip(CCL, 0, 250)

    # From: ../../methods/calcCloudBaseLCL/calcCloudBaseLCL.py

    # Compute Lifted Condensation level for CloudBase estimation.  Used to help with
    # Diurnal CU.  Adopted from GSP's CloudBase_FM_CCL_LCL tool
    def calcCloudBaseLCL(
        self, topo, T, Td, t_BL030, t_BL3060, rh_BL030, rh_BL3060
    ):
        t_SFC = self.FtoK(T)
        td_SFC = self.FtoK(Td)

        dpt_BL030 = self.FtoK(
            self.BI_dewFromTandRH(self.KtoF(t_BL030), rh_BL030)
        )
        dpt_BL3060 = self.FtoK(
            self.BI_dewFromTandRH(self.KtoF(t_BL3060), rh_BL3060)
        )

        #       calculate a boundary layer average temp (in Kelvins)
        tBL = (t_SFC + t_BL030 + t_BL3060) / 3.0
        #
        #       calculate a boundary layer average dewpt (in Kelvins)
        tdBL = (td_SFC + dpt_BL030 + dpt_BL3060) / 3.0

        heightLCL = 125.0 * (tBL - tdBL)
        LCL = (heightLCL * 3.2808) / 100.0
        return clip(LCL, 0, 250)

    # From: ../../methods/calcVisibility/vis.calcVisibility.py
    # ===========================================================================
    #  Visibility - convert from meters to statute miles
    # ===========================================================================
    def calcVisibility(self, vis_SFC):
        return vis_SFC * 0.00062137

    # From: ../../methods/calcProbIcePresent/calcProbIcePresent.py
    def calcProbIcePresent(self, t_c, rh_c, gh_c, topo, MaxTAloft):
        # we do not want the 1000MB level
        gh_c = gh_c[1:, :, :]
        t_c = t_c[1:, :, :]
        rh_c = rh_c[1:, :, :]
        ProbIcePresent = self.empty()

        temperatureList = [-8, -9, -10, -11, -12, -13, -14, -15]
        temperatureListAboveZero = [8, 9, 10, 11, 12, 13, 14, 15]
        probList = [30, 40, 50, 60, 70, 75, 85, 100]
        # initialize the rhGrid array
        rhGrid = []
        for i in [0, 1, 2, 3, 4, 5, 6, 7]:
            rhGrid.append(self.empty())
        for i in temperatureListAboveZero:
            rhGrid.append(self.empty())

        # pre-scan to determine maximum height level where ice in cloud is present
        # i.e. this method purpose is to prevent ice in clouds above a 1500+ meter thick of dry air (rh <75%)
        #     from entering lower clouds
        allowableMaxGH = gh_c[len(gh_c) - 1]
        bottomGH = self.empty()
        bottomGHrhDry = rh_c[1] < 75
        ### Added code for checking if bottom 1 km has mean RH of 85% or higher
        totalAllowedLayers = self.empty()
        layerRH = self.empty()
        ##############

        for i in xrange(len(gh_c) - 1):
            currentLevelGH = gh_c[i]
            currentLevelGHrhDry = rh_c[i] < 75
            if i > 1:
                previousLevelGHrhDry = rh_c[i - 1] < 75
                currentLevelGHrhDry = (
                    currentLevelGHrhDry | previousLevelGHrhDry
                )
                # currentGHrhDry = logical_or(less(rh_c[i], 75), less(rh_c[i-1], 75))
            if i > 2:
                currentLevelGHrhDry = (
                    currentLevelGHrhDry
                    | previousLevelGHrhDry
                    | (rh_c[i - 2] < 75)
                )
                # currentGHrhDry = logical_or(logical_or(less(rh_c[i], 75), less(rh_c[i-1], 75)), less(rh_c[i-2], 75))
            Mask = (
                currentLevelGHrhDry
                & bottomGHrhDry
                & ((currentLevelGH - bottomGH) > 1500)
                & (bottomGH < allowableMaxGH)
            )
            allowableMaxGH[Mask] = bottomGH[Mask]

            bottomGH[~currentLevelGHrhDry] = currentLevelGH[
                ~currentLevelGHrhDry
            ]
            Mask = bottomGH > 0
            bottomGHrhDry[Mask] = currentLevelGHrhDry[Mask]

            ###### Added code to use later which checks to see if bottom 1 km has a mean RH of 85% or higher.
            # Basically for ProbIcePresent to diagnose drizzle / freezing drizzle situation ###
            diffHeightTopo = gh_c[i] - topo
            mask = (diffHeightTopo > 0) & (diffHeightTopo <= 1000)
            totalAllowedLayers[mask] = totalAllowedLayers[mask] + 1
            layerRH[mask] = (layerRH + rh_c[i])[mask]
            #########################

        # get the ProbIce for each temperature
        for requestedTemp in temperatureListAboveZero:
            prevRH = self.empty()
            prevTemp = self.empty()
            # scan the cube for the relative humidity at the requested temperature below the height found in previous section, stored as allowableMaxGH.
            for i in xrange(len(t_c) - 1):
                maskAboveGround = greater(gh_c[i], topo)
                temp = t_c[i] - 273.15  # Convert to C
                prevMaskAboveGround = greater(gh_c[i - 1], topo)
                MaskHeightBelowMax = gh_c[i] < allowableMaxGH
                if not array_equal(prevRH, self.empty()):
                    # linear interpolate to determine the RH at temperature
                    slope = (rh_c[i] - prevRH) / (temp - prevTemp)
                    intercept = rh_c[i] - slope * temp
                    rhRequestedTemp = slope * requestedTemp * -1 + intercept
                    MaskStayingAboveGround = (
                        maskAboveGround & prevMaskAboveGround
                    )
                    MaskRHHigher = rhRequestedTemp > rhGrid[requestedTemp]
                    Mask = (
                        MaskHeightBelowMax
                        & MaskStayingAboveGround
                        & (prevTemp < requestedTemp * -1)
                        & (temp > requestedTemp * -1)
                        & MaskRHHigher
                    )
                    rhGrid[requestedTemp][Mask] = rhRequestedTemp[Mask]
                    Mask = (
                        MaskHeightBelowMax
                        & MaskStayingAboveGround
                        & (prevTemp > requestedTemp * -1)
                        & (temp < requestedTemp * -1)
                        & MaskRHHigher
                    )
                    rhGrid[requestedTemp][Mask] = rhRequestedTemp[Mask]

                else:
                    Mask = (
                        MaskHeightBelowMax
                        & maskAboveGround
                        & equal(temp, requestedTemp * -1)
                        & (rh_c[i] > rhGrid[requestedTemp])
                    )
                    rhGrid[requestedTemp][Mask] = rh_c[i][Mask]

                prevTemp = temp
                prevRH = rh_c[i]
            # Change rhGrid from w.r.t. water to w.r.t. ice
            rhGrid[requestedTemp] = self.rhWaterToIce(
                rhGrid[requestedTemp], requestedTemp * -1
            )
            # Smooth the rhGrid
            rhGrid[requestedTemp] = self.BI_smoothpm(rhGrid[requestedTemp], 3)
            # Create the probability of Ice for the requestedTemp
            probIceForTemp = (
                rhGrid[requestedTemp]
                / 100
                * self.probIceForTemp(requestedTemp)
                / 100
            ) * 100
            # Ensure the probability of ice present is greater than or equal to the probability of Ice for this requested Temp
            Mask = probIceForTemp > ProbIcePresent
            ProbIcePresent[Mask] = probIceForTemp[Mask]

        # apply the MaxTAloft to assign 100 to ProbIcePresent if temperatures are colder than -14C
        ProbIcePresent[MaxTAloft < -14] = 100

        ###### Added code which checks to see if bottom 1 km has mean RH of 85% RH or higher.
        # Basically for ProbIcePresent to diagnose drizzle / freezing drizzle situation ###
        mask = layerRH / totalAllowedLayers < 85
        ProbIcePresent[mask] = float32(100)
        ####################################################

        # Smooth the Probability of Ice Present grid
        ProbIcePresent = self.BI_smoothpm(ProbIcePresent, 3)
        return ProbIcePresent

    # From: ../../methods/calcProbRefreezeSleet/calcProbRefreezeSleet.py
    def calcProbRefreezeSleet(self, t_c, gh_c, topo, MaxTAloft):
        ProbRefreezeSleet = self.empty()

        HeightFreezingLevel = self.empty()
        prevTemp = self.empty()
        prevHeight = self.empty()
        # Determine height of freezing level
        for i in xrange(len(t_c) - 1):  # for each pressure level
            maskAboveGround = gh_c[i] > topo
            temp = t_c[i] - 273.15  # Convert to C

            if not array_equal(prevHeight, self.empty()):
                # linear interpolate to determine the Height at 0C
                # convert temps to K just for this calculation
                tempK = t_c[i]
                prevTempK = prevTemp + 273.15
                slope = (gh_c[i] - prevHeight) / (tempK - prevTempK)
                intercept = gh_c[i] - slope * tempK
                heightZeroC = slope * 273.15 + intercept
                ZeroCHgtBelowMaxTAloft = heightZeroC < self.HeightMaxTAloft
                Mask = (
                    maskAboveGround
                    & (prevTemp < 0)
                    & (temp > 0)
                    & ZeroCHgtBelowMaxTAloft
                )
                HeightFreezingLevel[Mask] = heightZeroC[Mask]
                Mask = (
                    maskAboveGround
                    & (prevTemp > 0)
                    & (temp < 0)
                    & ZeroCHgtBelowMaxTAloft
                )
                HeightFreezingLevel[Mask] = heightZeroC[Mask]

            else:
                Mask = maskAboveGround & equal(temp, 0)
                HeightFreezingLevel[Mask] = gh_c[i][Mask]
                # HeightFreezingLevel = where(maskAboveGround, where(equal(temp, 0), gh_c[i], HeightFreezingLevel), HeightFreezingLevel)
            prevTemp = temp
            prevHeight = gh_c[i]

        # figure out the coldest temperature below the height of the Freezing Level
        MinTAloft = MaxTAloft
        for i in xrange(len(gh_c) - 1):
            maskAboveGround = gh_c[i] > topo
            temp = t_c[i] - 273.15  # Convert to C
            Mask = (
                maskAboveGround
                & (gh_c[i] < HeightFreezingLevel)
                & (temp < MinTAloft)
            )
            MinTAloft[Mask] = temp[Mask]

        # Calculate the probability of refreeze to sleet based off the MinTAloft
        # Ensure most of the melting has taken place
        meltMask = MaxTAloft > 3
        # Ensure the freezing level height is at least 2500 ft (or 762 meters)
        depthCheck = HeightFreezingLevel > 762
        # Ensure the MinTAloft is at least -2C
        tempCheck = MinTAloft < -2
        Mask = meltMask & depthCheck & tempCheck
        ProbRefreezeSleet[Mask] = (
            2.3036 * MinTAloft * MinTAloft + 5.979 * MinTAloft + 0.8295
        )[Mask]

        # Smooth the Probability of RefreezeSleet grid
        # ProbRefreezeSleet = self.BI_smoothpm(ProbRefreezeSleet, 3)

        return ProbRefreezeSleet

    # From: ../../methods/calcQPF12/calcQPF12.py
    # ===========================================================================
    #  QPF12 - sums up all QPF grids within each 12 hour period
    # ===========================================================================
    def calcQPF12(self, QPF, QPF12, ctime, mtime):
        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids("QPF12", QPF, "QPF", mtime, None)
        except:
            pass

        modelhour = time.gmtime(ctime[0])
        forecastHR = modelhour.tm_hour

        #  If this is the start of a 12hr QPF block, or QPF12 is missing
        #  We cannot trust the grids will be processed in sequential order, so
        #  we need to check total before resettting it.  Note, this makes it
        #  impossible to rerun a model SmartInit without wiping the QPF12 grids
        #  first.  Otherwise, the QPF12 will be doubled.
        if (forecastHR in [0, 12] and QPF12 is None) or QPF12 is None:

            #  Reset the value of the 12 hr QPF with the only precip we have
            return QPF

        #  If we made it this far, return the total 12 hour QPF
        return QPF12 + QPF

    # From: ../../methods/calcQPF6/calcQPF6.py
    # ===========================================================================
    #  QPF6 and QPE06 - sums up all QPF grids within each 6 hour period
    # ===========================================================================
    def calcQPF6(self, QPF, QPF6, ctime, mtime):
        #
        # First, try the derived method to ensure enough component grids are available.
        # If that method does not work in this situation, continue to regular method.
        #
        try:
            return self.BI_handleDerivedGrids("QPF6", QPF, "QPF", mtime, None)
        except:
            pass

        modelhour = time.gmtime(ctime[0])
        forecastHR = modelhour.tm_hour

        #  If this is the start of a 6hr QPF block, or QPF6 is missing
        #  We cannot trust the grids will be processed in sequential order, so
        #  we need to check total before resettting it.  Note, this makes it
        #  impossible to rerun a model SmartInit without wiping the QPF6 grids
        #  first.  Otherwise, the QPF6 will be doubled.
        if (forecastHR in [0, 6, 12, 18] and QPF6 is None) or QPF6 is None:

            #  Reset the value of the 6 hr QPF with the only precip we have
            return QPF

        #  If we made it this far, return the total 6 hour QPF - so far
        return QPF6 + QPF

    # From: ../../methods/calcQPF/tp.calcQPF.py
    # ===========================================================================
    #  Calculate model time step precipitation
    # ===========================================================================
    def calcQPF(self, tp_SFC):
        # convert from millimeters to inches
        return self.BI_calcQPF(tp_SFC)

    # From: ../../methods/calcRH/calcRH.py
    # ===========================================================================
    #  RH - simply calculate RH based on Temp and Dewpoint (both in degrees F)
    # ===========================================================================
    def calcRH(self, T, Td):
        Tc = 0.556 * (T - 32.0)
        Tdc = 0.556 * (Td - 32.0)
        Vt = 6.11 * pow(10, (Tc * 7.5 / (Tc + 237.3)))
        Vd = 6.11 * pow(10, (Tdc * 7.5 / (Tdc + 237.3)))
        RH = (Vd / Vt) * 100.0
        return RH

    # From: ../../methods/calcSky/rh_c-gh_c.calcSky.py
    # --------------------------------------------------------------------------
    # Sky
    # ---------------------------------------- ----------------------------------
    def calcSky(self, rh_c, gh_c, topo, PoP):
        sky = self.empty()
        count = self.newGrid(7)
        startPressureLevel = self.empty()

        # coding for mountain offices
        if self.BI_optionsDict["topoSite"]:
            for i in xrange(rh_c.shape[0]):
                rhLayer = rh_c[i]
                ghLayer = gh_c[i]

                # Assign sky for each pressure level. Set sky to 0 where the geopotential height is at or below 50 meters of ground.
                startPressureLevel = where(
                    logical_and(
                        equal(startPressureLevel, 0),
                        greater_equal(ghLayer - 50, topo),
                    ),
                    i,
                    startPressureLevel,
                )
                skylayer = where(
                    greater_equal(ghLayer - 50, topo),
                    self.BI_computeSkyLayer(
                        i, rhLayer, ghLayer, startPressureLevel, topo
                    ),
                    0,
                )
                sky = sky + skylayer

        # coding for non-mountain offices
        else:
            for i in xrange(rh_c.shape[0]):
                rhLayer = rh_c[i]
                skylayer = 0
                if i == 2:
                    skylayer = where(
                        less(rhLayer, 64), 0, rhLayer * 1.13 - 71.0
                    )  # 950mb
                    count = where(greater(rhLayer, 90), count - 1, count)
                    count = where(greater(rhLayer, 95), count - 2, count)
                elif i == 4:
                    skylayer = where(
                        less(rhLayer, 51), 0, rhLayer * 1.33 - 66.0
                    )  # 900mb
                    count = where(greater(rhLayer, 90), count - 1, count)
                    count = where(greater(rhLayer, 95), count - 2, count)
                elif i == 6:
                    skylayer = where(
                        less(rhLayer, 59), 0, rhLayer * 1.65 - 95.0
                    )  # 850mb
                    count = where(greater(rhLayer, 90), count - 1, count)
                    count = where(greater(rhLayer, 95), count - 2, count)
                elif i == 8:
                    skylayer = where(
                        less(rhLayer, 46), 0, rhLayer * 1.63 - 73.0
                    )  # 800mb
                    count = where(greater(rhLayer, 90), count - 1, count)
                    count = where(greater(rhLayer, 95), count - 2, count)
                elif i == 12:
                    skylayer = where(
                        less(rhLayer, 35), 0, rhLayer * 1.79 - 61.0
                    )  # 700mb
                elif i == 16:
                    skylayer = where(
                        less(rhLayer, 20), 0, rhLayer * 1.20 - 24.0
                    )  # 600mb
                elif i == 20:
                    skylayer = where(
                        less(rhLayer, 10), 0, rhLayer * 0.86 - 7.0
                    )  # 500mb
                elif i == 21:
                    skylayer = where(
                        less(rhLayer, 0), 0, rhLayer * 0.55 + 3.0
                    )  # 450mb
                elif i == 22:
                    skylayer = where(
                        less(rhLayer, 0), 0, rhLayer * 0.33 + 5.0
                    )  # 350mb

                sky = where(gh_c[i] >= topo, sky + skylayer, sky)  # topo check

            count = where(less(count, 2), 2, count)
            sky = sky / count  # layer divisor
            sky = self.BI_smoothpm(sky, 3)

        # PoP vs Sky check. Equation ensures sky is a certain value depending on the PoP. Some examples:
        # PoP: 15, Sky: 40
        # PoP: 40, Sky: 55
        # PoP: 55, Sky: 70
        # PoP: 75, Sky: 85
        # PoP: 90, Sky: 100
        skycheck = 33.888 * exp(0.0123 * PoP)
        sky = where(
            greater_equal(PoP, 15),
            where(less(sky, skycheck), skycheck, sky),
            sky,
        )
        sky = self.BI_smoothpm(sky, 3)

        return clip(sky, 0, 100)

    # From: ../../methods/calcSnowAmt/calcSnowAmt.py
    # ===========================================================================
    #  SnowAmt - uses SnowRatio data along with the model QPF to compute SnowAmt
    #            check is also made to reduce SnowAmt as temperature climbs
    #            above zero. The default in BaseInit is if the entire grid is
    #            above 40F then zero is returned for the whole grid.
    # ---------------------------------------------------------------------------
    def calcSnowAmt(self, QPF, T, SnowRatio):
        if not self.BI_checkT(T):
            return where(T, 0, 0)

        SnowAmt = QPF * SnowRatio
        SnowAmt = where(
            greater(T, 32.0), pow(36.0 - T, 2) / 16.0 * SnowAmt, SnowAmt
        )
        SnowAmt = where(greater(T, 35.0), 0.0, SnowAmt)
        return SnowAmt

    # From: ../../methods/calcSnowLevel/calcSnowLevel.py
    # ==========================================================================
    #  calcSnowLevel
    #
    def calcSnowLevel(self, gh_c, t_c, rh_c, topo):
        return self.BI_getSnowLevel(gh_c, t_c, rh_c, topo)

    # From: ../../methods/calcSnowRatio/XX_NAM12.calcSnowRatio.py
    # ===========================================================================
    #  SnowRatio - calculates the snow ratio using the Cobb method (Caribou Tool)
    #
    # ---------------------------------------------------------------------------

    def calcSnowRatio(
        self,
        T,
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
    ):

        if not self.BI_checkT(T):
            return where(T, 0, 0)

        # Cobb method
        return self.BI_calcSnowRatio(
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
        )

    # From: ../../methods/calcT/BI_calcT.calcT.py
    # ===========================================================================
    #  Calculate surface temperature using available BL data
    # ===========================================================================
    def calcT(
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
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
    ):

        #  Construct lists of boundary layer data
        blTemps = [t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120, t_BL120150]
        blRH = [
            rh_FHAG2,
            rh_BL030,
            rh_BL3060,
            rh_BL6090,
            rh_BL90120,
            rh_BL120150,
        ]
        blWinds = [
            wind_FHAG10,
            wind_BL030,
            wind_BL3060,
            wind_BL6090,
            wind_BL90120,
            wind_BL120150,
        ]

        #  Compute the temperature using the available boundary layer data
        return self.BI_calcT(
            blTemps,
            blRH,
            blWinds,
            p_SFC,
            t_FHAG2,
            stopo,
            topo,
            gh_c,
            t_c,
            rh_c,
            wind_c,
            ctime,
        )

    # From: ../../methods/calcTd/BI_calcTd.calcTd.py
    # ===========================================================================
    #  Calculate surface dewpoint using available BL data
    # ===========================================================================
    def calcTd(
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
        T,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
    ):

        #  Construct lists of boundary layer data
        blTemps = [t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120, t_BL120150]
        blRH = [
            rh_FHAG2,
            rh_BL030,
            rh_BL3060,
            rh_BL6090,
            rh_BL90120,
            rh_BL120150,
        ]
        blWinds = [
            wind_FHAG10,
            wind_BL030,
            wind_BL3060,
            wind_BL6090,
            wind_BL90120,
            wind_BL120150,
        ]

        #  Compute the dewpoint using the available boundary layer data
        return self.BI_calcTd(
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
        )

    # From: ../../methods/calcTransWind/BI_calcTransWind.calcTransWind.py
    # ===========================================================================
    #  Calculate transport wind using available BL data
    # ===========================================================================
    def calcTransWind(
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
        MixHgt,
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
    ):

        #  Construct lists of boundary layer data
        blTemps = [t_FHAG2, t_BL030, t_BL3060, t_BL6090, t_BL90120, t_BL120150]
        blRH = [
            rh_FHAG2,
            rh_BL030,
            rh_BL3060,
            rh_BL6090,
            rh_BL90120,
            rh_BL120150,
        ]
        blWinds = [
            wind_FHAG10,
            wind_BL030,
            wind_BL3060,
            wind_BL6090,
            wind_BL90120,
            wind_BL120150,
        ]

        #  Compute the transport wind using the available boundary layer data
        return self.BI_calcTransWind(
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
        )

    # From: ../../methods/calcWindGust/TransWind.calcWindGust.py
    # ==========================================================================
    # WindGust - wind speed of the transport wind (the average wind in the
    #            mixed layer
    #
    #            Does NOT restrict the wind gust to be zero if it is
    #            not above the wind speed.
    # ==========================================================================
    def calcWindGust(self, Wind, TransWind):
        wmag = Wind[0]
        tmag = TransWind[0]
        gmag = wmag * 1.5
        #
        # If tmag is greater than cap set to gmag to cap otherwise
        # set to gmag. High wind gust cases.
        #
        hcap = Wind[0] * 1.8
        gmag = where(greater(tmag, hcap), hcap, gmag)
        #
        # if tmag is less than lcap set to lcap otherwise set to
        # gmag. Low wind gust cases.
        #
        lcap = Wind[0] * 1.3
        gmag = where(less(tmag, lcap), tmag, gmag)
        #
        # Set gmag to wmag if the tmag is less than wmag
        # No Wind Gust cases.
        #
        gmag = where(less(tmag, wmag), wmag, gmag)
        #
        return gmag

    # From: ../../methods/calcWind/XX_NAM12.calcWind.py
    ##-------------------------------------------------------------------------
    ##  Wind - Converts the lowest available wind level from m/s to knots
    ##  Applies a topography adjustment for mountain offices (from
    ##     Eric Thaler SOO BOU)
    ##-------------------------------------------------------------------------
    def calcWind(
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
        stopo,
        topo,
        gh_c,
        t_c,
        rh_c,
        wind_c,
        ctime,
    ):

        # coding for mountain offices
        if self.BI_optionsDict["topoSite"]:
            # Enter some physical constants

            g = 9.80665
            R_d = 287.05
            R_v = 461.50
            c_pd = 1005.7
            eps = R_d / R_v

            # Set up the model parameters

            num_bl = 5
            bl_levs = ["BL030", "BL3060", "BL6090", "BL90120", "BL120150"]
            sfc_wind_parm = "FHAG10"
            sfc_thermo_parm = "FHAG2"
            sfc_pres_parm = "SFC"
            hght_parm = "gh"
            isobaric = "N"

            # Define arrays for the boundary layer variables

            bl_pres = []
            bl_tvrt = []
            bl_hght = []
            bl_wdir = []
            bl_wspd = []
            bl_temp = []
            bl_relh = []

            # Grab the model and real topography (m).  Model topo put in bl_hght[0].

            bl_hght.append(stopo)
            topo_real = topo

            # Grab the surface winds.  Put direction in bl_wdir[0] and speed in bl_wspd[0].

            bl_wdir.append(wind_FHAG10[1])
            bl_wspd.append(wind_FHAG10[0])

            # Grab the surface thermodynamic data and compute the pressures of the various boundary layers.

            pres = p_SFC
            bl_pres.append(pres)
            bl_pres.append(pres - 1500.0)
            bl_pres.append(pres - 4500.0)
            bl_pres.append(pres - 7500.0)
            bl_pres.append(pres - 10500.0)
            bl_pres.append(pres - 13500.0)
            bl_pres.append(pres - 16500.0)
            bl_temp.append(t_FHAG2)
            bl_relh.append(rh_FHAG2)
            ew = (
                6.1094
                * exp(
                    17.625
                    * (bl_temp[0] - 273.15)
                    / (243.04 + (bl_temp[0] - 273.15))
                )
            ) * (bl_relh[0] / 100.0)
            ew = ew * 1.00071 * exp(0.0000045 * bl_pres[0] / 100.0)
            bl_tvrt.append(
                (bl_pres[0] / 100.0)
                / ((bl_pres[0] / 100.0) + (ew * (eps - 1.0)))
                * bl_temp[0]
            )

            # Grab the boundary layer data.

            for bl in [
                wind_BL030,
                wind_BL3060,
                wind_BL6090,
                wind_BL90120,
                wind_BL120150,
            ]:
                bl_wdir.append(bl[1])
                bl_wspd.append(bl[0])

            for bl in [t_BL030, t_BL3060, t_BL6090, t_BL90120, t_BL120150]:
                bl_temp.append(bl)

            for bl in [
                rh_BL030,
                rh_BL3060,
                rh_BL6090,
                rh_BL90120,
                rh_BL120150,
            ]:
                bl_relh.append(bl)

            for lev in range(1, num_bl + 1):
                ew = (
                    6.1094
                    * exp(
                        17.625
                        * (bl_temp[lev] - 273.15)
                        / (243.04 + (bl_temp[lev] - 273.15))
                    )
                ) * (bl_relh[lev] / 100.0)
                ew = ew * 1.00071 * exp(0.0000045 * bl_pres[lev] / 100.0)
                bl_tvrt.append(
                    (bl_pres[lev] / 100.0)
                    / ((bl_pres[lev] / 100.0) + (ew * (eps - 1.0)))
                    * bl_temp[lev]
                )

            # Compute the heights of the middle of each boundary layer by integrating the hypsometric equation

            for lev in range(1, num_bl + 1, 1):
                bl_hght.append(
                    bl_hght[lev - 1]
                    + R_d
                    / g
                    * (bl_tvrt[lev - 1] + bl_tvrt[lev])
                    / 2.0
                    * log(bl_pres[lev - 1] / bl_pres[lev])
                )

            # Initialize some arrays.

            spd = self.newGrid(-1)
            dir = self.newGrid(-1)

            # For places where the real topography is above the model topography we go through
            # the boundary layer data and interpolate the model winds to the real topography.

            for lev in range(1, num_bl + 1):
                between = logical_and(
                    greater_equal(topo_real, bl_hght[lev - 1]),
                    less(topo_real, bl_hght[lev]),
                )
                spd = where(
                    equal(1, between),
                    self.linear(
                        bl_hght[lev - 1],
                        bl_hght[lev],
                        bl_wspd[lev - 1],
                        bl_wspd[lev],
                        topo_real,
                    ),
                    spd,
                )
                dir = where(
                    equal(1, between),
                    self.BI_dirlinear(
                        bl_hght[lev - 1],
                        bl_hght[lev],
                        bl_wdir[lev - 1],
                        bl_wdir[lev],
                        topo_real,
                    ),
                    dir,
                )

            # In places where the real topography is below the model topography,
            # we will set the GFE wind to the surface wind in the model.

            dir = where(less(topo_real, bl_hght[0]), bl_wdir[0], dir)
            spd = where(less(topo_real, bl_hght[0]), bl_wspd[0], spd)

            # If the new computed wind speed is greater than the original model surface wind
            # speed, that is, if a topographic correction has been made, limit that change to
            # be the addition of half of the difference between the corrected speed and the
            # original surface wind speed.  This keeps things under control on the high ridges.

            spd = where(
                greater(spd, bl_wspd[0]),
                bl_wspd[0] + ((spd - bl_wspd[0]) / 2.0),
                spd,
            )
            spd = spd * 3600.0 / 1852.0

        # coding for non-mountain offices
        else:
            spd = wind_FHAG10[0]  # get the wind grids
            dir = wind_FHAG10[1]
            spd = spd * 1.94  # convert m/s to knots

        dir = clip(dir, 0, 359.5)
        return (spd, dir)
