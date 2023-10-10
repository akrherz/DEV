################################################################################
# SVN: $Rev: 5048 $  $Date: 2015-06-04 20:32:09 +0000 (Thu, 04 Jun 2015) $
#
#       NWS Local_NAM12 SmartInit
#
################################################################################


import NWS_NAM12
from Init import *
from numpy import *

#############################################
# Add locally needed imports here
##import time

# *******************************************************************************
#  Make no changes in this section, unless changing name of GFE database


def main():
    Local_NAM12Forecaster().run()


class Local_NAM12Forecaster(NWS_NAM12.NAM12):
    def __init__(self):
        """Local_NAM12Forecaster.__init__"""

        #  Each database can be renamed, if desired. The first name is the
        #  used to get the source data. The optional second name will be used
        #  as the database name in GFE, if it is defined.
        #
        #  Examples:
        #       Will use "A" as the name of the source data and within GFE
        #       NWS_A.NWS_A.__init__(self, "A")
        #
        #       Will use "A" as the name of the source data, but use the name
        #       "B" within GFE
        #       NWS_A.NWS_A.__init__(self, "A", "B")
        NWS_NAM12.NAM12.__init__(self, "NAM12")

        # Optional settings. These are preset for your region, only change
        # if really needed.

    ##        self.BI_optionsDict['topoSite']=True
    ##        self.BI_optionsDict['prismSite']=True
    ##        self.BI_optionsDict['GreatLakeSite']=True
    ##        self.BI_optionsDict['HainesLevel']='HIGH'
    ##        self.BI_optionsDict['windLapseRate']=2.5/304.8

    #  End - Make no changes in this section
    # *******************************************************************************

    ############################################################################
    # Add site additions/overrides to the NAM12 SmartInit Here.
    # Methods must be indented to be inside class statement.
    # Example:

    ##    def calcWindGust(self, Wind, TransWind):
    ##        """Calculates WindGust from Wind and TransWind"""
    ##        # rest of method code

    #    def calcMaxTAloft(self, t_c, gh_c, topo):
    #    	gridShape = (t_c.shape[1], t_c.shape[2])
    #    	MaxTAloft = zeros(gridShape, dtype=float)
    #    	MaxTAloft = MaxTAloft - 50
    #    	prevTemp = zeros(gridShape, dtype=float)
    #    	prevTemp = 10000
    #    	timesThruLoop = 0
    #    	for i in xrange(len(t_c) - 1):   #for each pressure level
    #        	maskAboveGround = greater(gh_c[i], topo)
    #        	mask1500FTAboveGround = greater(gh_c[i], topo + 460)
    #        	temp = t_c[i] - 273.15 # Convert to C
    #        	lapseRate = t_c[i] - prevTemp
    #        	if timesThruLoop == 0:
    #           	   startMaxTAloftMask = greater(lapseRate, 0)
    #        	else:
    #                   startMaxTAloftMask = logical_or(greater(lapseRate, 0), startMaxTAloftMask)
    #        	MaxTAloft = where(logical_and(maskAboveGround, startMaxTAloftMask), where(greater(temp, MaxTAloft), temp, MaxTAloft), MaxTAloft)
    #        	MaxTAloft = where(mask1500FTAboveGround, where(greater(temp, MaxTAloft), temp, MaxTAloft), MaxTAloft)
    #        	prevTemp = t_c[i]
    #        	timesThruLoop = timesThruLoop + 1

    #    	MaxTAloft = self.BI_smoothpm(MaxTAloft, 3)
    #    	return MaxTAloft

    def calcSfcWarmLayer(self, t_BL030, t_BL3060, rh_BL030, rh_BL3060, p_SFC):
        #   calculate dewpoint for the lower 30 mb layer
        rhBL030 = clip(rh_BL030, 0.5, 99.5)
        tCBL030 = t_BL030 - 273.15
        esBL030 = 6.112 * exp((17.67 * tCBL030) / (tCBL030 + 243.5))
        eBL030 = (rhBL030 / 100.0) * esBL030
        tdBL030 = (243.5 * log(eBL030 / 6.112)) / (17.67 - log(eBL030 / 6.112))
        BL030_dewpt = tdBL030 + 273.15

        #   calculate dewpoint for the 30-60mb layer

        rhBL3060 = clip(rh_BL3060, 0.5, 99.5)
        tCBL3060 = t_BL3060 - 273.15
        esBL3060 = 6.112 * exp((17.67 * tCBL3060) / (tCBL3060 + 243.5))
        eBL3060 = (rhBL3060 / 100.0) * esBL3060
        tdBL3060 = (243.5 * log(eBL3060 / 6.112)) / (
            17.67 - log(eBL3060 / 6.112)
        )
        BL3060_dewpt = tdBL3060 + 273.15

        p_SFC - 15.0
        p_SFC - 45.0

        #   calculate model wetbulb for lower 30 mb
        pSFC = (p_SFC - 15.0) / 100.0
        tK030 = t_BL030
        tdK030 = BL030_dewpt
        #   set constants
        c1 = 0.0091379024
        c2 = 6106.396
        f = 0.0006355
        #   convert T and Td to degrees C
        tC030 = tK030 - 273.15
        tdC030 = tdK030 - 273.15
        #   calculate saturation vapor pressures using the
        #   Bolton (1980) form of the Clausius-Clapeyron Equation
        es030 = 6.112 * exp((17.67 * tC030) / (tC030 + 243.5))
        #   calculate dewpoint vapor pressures
        ed030 = 6.112 * exp((17.67 * tdC030) / (tdC030 + 243.5))
        #   compute dewpoint depression
        dewptDep030 = tK030 - tdK030
        #   clip to avoid divide-by-zero
        ##            dewptDep = where(less_equal(dewptDep, 0.0), 0.00001, dewptDep)
        dewptDep030 = where(less_equal(dewptDep030, 0.0), 0.1, dewptDep030)

        #   s is an intermediate in the Tw calculation
        s030 = (es030 - ed030) / (dewptDep030)
        #   calculate first guess Tw
        tW030 = ((tK030 * f * pSFC) + (tdK030 * s030)) / ((f * pSFC) + s030)
        #    Solve for tW iteratively by attempting an energy balance
        #    Ten steps should be sufficient

        for i in xrange(0, 10, 1):
            #       convert to deg C
            tWC030 = tW030 - 273.15
            #       calculate wet bulb vapor pressures
            ew030 = 6.112 * exp((17.67 * tWC030) / (tWC030 + 243.5))
            #       calculate difference values (after Iribarne and Godson (1981))
            de030 = (f * pSFC * (tK030 - tW030)) - (ew030 - ed030)
            #       take derivative of difference value w.r.t. Tw to find zero value of function
            der030 = (ew030 * (c1 - (c2 / tW030**2))) - (f * pSFC)
            #       calculate next guess of tW
            tW030 = tW030 - (de030 / der030)

        #   calculate model wetbulb for 30 to 60 mb
        pSFC = (p_SFC - 45.0) / 100.0
        tK3060 = t_BL3060
        tdK3060 = BL3060_dewpt
        #   set constants
        #   convert T and Td to degrees C
        tC3060 = tK3060 - 273.15
        tdC3060 = tdK3060 - 273.15
        #   calculate saturation vapor pressures using the
        #   Bolton (1980) form of the Clausius-Clapeyron Equation
        es3060 = 6.112 * exp((17.67 * tC3060) / (tC3060 + 243.5))
        #   calculate dewpoint vapor pressures
        ed3060 = 6.112 * exp((17.67 * tdC3060) / (tdC3060 + 243.5))
        #   compute dewpoint depression
        dewptDep3060 = tK3060 - tdK3060
        #   clip to avoid divide-by-zero
        ##            dewptDep = where(less_equal(dewptDep, 0.0), 0.00001, dewptDep)
        dewptDep3060 = where(less_equal(dewptDep3060, 0.0), 0.1, dewptDep3060)

        #   s is an intermediate in the Tw calculation
        s3060 = (es3060 - ed3060) / (dewptDep3060)
        #   calculate first guess Tw
        tW3060 = ((tK3060 * f * pSFC) + (tdK3060 * s3060)) / (
            (f * pSFC) + s3060
        )
        #    Solve for tW iteratively by attempting an energy balance
        #    Ten steps should be sufficient

        for i in xrange(0, 10, 1):
            #       convert to deg C
            tWC3060 = tW3060 - 273.15
            #       calculate wet bulb vapor pressures
            ew3060 = 6.112 * exp((17.67 * tWC3060) / (tWC3060 + 243.5))
            #       calculate difference values (after Iribarne and Godson (1981))
            de3060 = (f * pSFC * (tK3060 - tW3060)) - (ew3060 - ed3060)
            #       take derivative of difference value w.r.t. Tw to find zero value of function
            der3060 = (ew3060 * (c1 - (c2 / tW3060**2))) - (f * pSFC)
            #       calculate next guess of tW
            tW3060 = tW3060 - (de3060 / der3060)

        BL030_mask = greater(tW030, 273.55)
        BL3060_mask = greater(tW3060, 273.55)
        logical_and(BL030_mask, BL3060_mask)
        tW030 = self.convertKtoF(tW030)
        tW3060 = self.convertKtoF(tW3060)

        SfcWarmLayer = (tW3060 + tW030) / 2

        # SfcWarmLayer = where(melting, 1.0, 0)
        return SfcWarmLayer

    #    def calcMinTwAloft(self, t_c, gh_c, rh_c, p_SFC, topo):
    #    	gridShape = (t_c.shape[1], t_c.shape[2])
    #    	MinTwAloft = zeros(gridShape, dtype=float)

    # Calculate the MaxTAloft and what height level the MaxTAloft occurs
    #    	MaxTAloft = zeros(gridShape, dtype=float)
    #    	MaxTAloft = MaxTAloft - 50
    #    	HeightMaxTAloft = zeros(gridShape, dtype=float)
    #    	HeightFreezingLevel = zeros(gridShape, dtype=float)
    #    	prevTemp = zeros(gridShape, dtype=float)
    #    	prevHeight = zeros(gridShape, dtype=float)
    # p_SFC = p_SFC/100.0
    #    	for i in xrange(len(t_c) - 1):   #for each pressure level
    # maskAboveGround = greater(gh_c[i], topo)
    # 		maskAboveGround = greater(gh_c[i], topo + 460)
    #        	temp = t_c[i] - 273.15 # Convert to C
    #        	tempMaxTAloftCheck = greater(temp, MaxTAloft)
    #        	MaxTAloft = where(maskAboveGround, where(tempMaxTAloftCheck, temp, MaxTAloft), MaxTAloft)
    #        	HeightMaxTAloft = where(maskAboveGround, where(tempMaxTAloftCheck, gh_c[i], HeightMaxTAloft), HeightMaxTAloft)

    #    	for i in xrange(len(t_c) - 1):   #for each pressure level
    #        	maskAboveGround = greater(gh_c[i], topo)
    #        	temp = t_c[i] - 273.15 # Convert to C

    # if prevHeight != zeros(gridShape, dtype=float):
    #                if not array_equal(prevHeight, zeros(gridShape, dtype = float)):
    # linear interpolate to determine the Height at 0C
    # convert temps to K just for this calculation
    #            	    tempK = t_c[i]
    #            	    prevTempK = prevTemp + 273.15
    #            	    slope = (gh_c[i] - prevHeight) / (tempK - prevTempK)
    #            	    intercept = gh_c[i] - slope * tempK
    #            	    heightZeroC = slope * 273.15 + intercept

    # HeightFreezingLevel = where(maskAboveGround, where(logical_and(less(prevTemp, 0), greater(temp, 0)), where(less(heightZeroC, HeightMaxTAloft), heightZeroC, HeightFreezingLevel), HeightFreezingLevel), HeightFreezingLevel)
    # HeightFreezingLevel = where(maskAboveGround, where(logical_and(greater(prevTemp, 0), less(temp, 0)), where(less(heightZeroC, HeightMaxTAloft), heightZeroC, HeightFreezingLevel), HeightFreezingLevel), HeightFreezingLevel)

    #        	else:
    #            	    HeightFreezingLevel = where(maskAboveGround, where(equal(temp, 0), gh_c[i], HeightFreezingLevel), HeightFreezingLevel)

    #    	MinTwAloft = zeros(gridShape, dtype=float)
    #    	MinTwAloft = MaxTAloft
    # MinTwAloft = tempT #- 273.15
    # for i in xrange(len(gh_c) - 1):
    #    	for i in xrange(len(t_c)-1):
    #        	maskAboveGround = greater(gh_c[i], topo)
    # temp = t_c[i] - 273.15 # Convert to C

    # MinTAloft = where(maskAboveGround, where(less(gh_c[i], HeightFreezingLevel), where(less(temp, MinTAloft), temp, #MinTAloft), MinTAloft), MinTAloft)
    ##   set constants
    #    		c1  = 0.0091379024
    #    		c2  = 6106.396
    #    		f   = 0.0006355
    ##   calculate model wetbulb
    #    		pSFC = (p_SFC - 100.0) / 100.0
    #    		tK = t_c[i]
    # tdK = BL_dewpt
    ##   set constants
    ##   convert T and Td to degrees C
    # tC = tK - 273.15
    # tdC = tdK - 273.15

    #        	tC = tK-273.15
    #        	es = 6.112*exp((17.67*tC)/(tC+243.5))
    #        	rh = rh_c[i]/100.0 #i
    #        	e = rh*es
    #        	e = where(less_equal(e,0),0.1,e)
    #        	a = log(e/6.112)
    #        	tdC = ((-243.5*a)/(a-17.67))
    # tdC = tdK - 273.15
    ##        print tdC
    #        	tdK = tdC+273.15
    #    		es = 6.112 * exp((17.67 * tC) / (tC + 243.5))
    #    		ed = 6.112 * exp((17.67 * tdC) / (tdC + 243.5))
    #        	dewptDep = (tC - tdC)
    #    		dewptDep = where(less_equal(dewptDep, 0.0), 0.1, dewptDep)
    #    		s = (es - ed) / (dewptDep)
    # 		tW = zeros(gridShape, dtype=float)
    #    		tW = ((tK * f * pSFC) + (tdK * s)) / ((f * pSFC) + s)
    # 		count = 0
    #    		for a in xrange(0,10,1):
    ##       convert to deg C
    #        		tWC = tW - 273.15
    # print tWC
    ##       calculate wet bulb vapor pressures
    #        		ew = 6.112 * exp((17.67 * tWC) / (tWC + 243.5))
    ##       calculate difference values (after Iribarne and Godson (1981))
    #        		de = (f * pSFC * (tK - tW)) - (ew - ed)
    ##       take derivative of difference value w.r.t. Tw to find zero value of function
    #        		der = (ew * (c1 - (c2 / tW ** 2))) - (f * pSFC)
    ##       calculate next guess of tW
    #        		LayerWb = tW - (de / der)
    # count = count + 1
    # print count

    # 		LayerWb = LayerWb - 273.15
    #        	count = where(less(LayerWb, MinTwAloft), (count+1), count)
    # print count
    # 		BelowFZL = (less(gh_c[i], HeightMaxTAloft)) #i
    #        	NewMinTw = (less(LayerWb, MinTwAloft))
    # print HeightMaxTAloft

    # 		MinTwAloftMask = logical_and(BelowFZL, NewMinTw)

    # 		MinTwAloft = where(logical_and(MinTwAloftMask,maskAboveGround), LayerWb, MinTwAloft)
    # print MinTwAloft

    # Smooth the Probability of RefreezeSleet grid
    # ProbRefreezeSleet = self.smoothpm(ProbRefreezeSleet, 3)
    #    		MinTwAloft = self.BI_smoothpm(MinTwAloft, 3)
    # MinTwAloft = where(greater(MinTwAloft, MaxTAloft), MaxTAloft, MinTwAloft)
    #    	return MinTwAloft

    def calcColdLayerDepth(self, t_c, gh_c, topo):
        gridShape = (t_c.shape[1], t_c.shape[2])
        ColdLayerDepth = zeros(gridShape, dtype=float)

        # Calculate the MaxTAloft and what height level the MaxTAloft occurs
        MaxTAloft = zeros(gridShape, dtype=float)
        MaxTAloft = MaxTAloft - 50
        HeightMaxTAloft = zeros(gridShape, dtype=float)
        zeros(gridShape, dtype=float)
        zeros(gridShape, dtype=float)
        zeros(gridShape, dtype=float)
        height = zeros(gridShape, dtype=float)

        for i in xrange(len(t_c) - 1):  # for each pressure level
            maskAboveGround = greater(gh_c[i], topo)
            temp = t_c[i] - 273.15  # Convert to C
            tempMaxTAloftCheck = greater(temp, MaxTAloft)
            MaxTAloft = where(
                maskAboveGround,
                where(tempMaxTAloftCheck, temp, MaxTAloft),
                MaxTAloft,
            )
            HeightMaxTAloft = where(
                maskAboveGround,
                where(tempMaxTAloftCheck, gh_c[i], HeightMaxTAloft),
                HeightMaxTAloft,
            )

        for i in xrange(len(t_c) - 1):  # for each pressure level
            # maskAboveGround = greater(gh_c[i], topo)
            # temp = t_c[i] - 273.15 # Convert to C
            # ColdLayerDepth = where(logical_and(greater(gh_c[i], topo), logical_and(less(gh_c[i], HeightMaxTAloft), less(t_c[i], 0.0))), gh_c[i], ColdLayerDepth)
            previousHeight = where(
                logical_and(
                    greater(gh_c[i], 0.0),
                    logical_and(
                        less(gh_c[i], HeightMaxTAloft), less(t_c[i], 273.15)
                    ),
                ),
                gh_c[i - 1],
                0,
            )
            height = where(
                logical_and(
                    greater(gh_c[i], 0.0),
                    logical_and(
                        less(gh_c[i], HeightMaxTAloft), less(t_c[i], 273.15)
                    ),
                ),
                gh_c[i],
                0,
            )
            ColdLayerDepth = ColdLayerDepth + (height - previousHeight)

        ColdLayerDepth = where(less(MaxTAloft, 0), 0, ColdLayerDepth)

        ColdLayerDepth = ColdLayerDepth * 3.2808
        ColdLayerDepth = self.BI_smoothpm(ColdLayerDepth, 3)
        return ColdLayerDepth

    def calcNPoP(self, PoP, QPF, ctime, mtime):
        if QPF is None:
            newPoP = 0
        else:
            thresh = 0.03
            radius = 40
            dx = 2.5
            gp = int(radius / dx)
            newPoP = zeros(QPF.shape)
            yval = 0
            for yy in QPF:
                xval = 0
                for xspot in yy:
                    newPoP[yval][xval] = self._makeSquarePoP(
                        QPF, gp, [yval, xval], thresh
                    )
                    xval += 1
                yval += 1
        return maximum(newPoP, PoP)

    def _makeSquarePoP(self, data, rad, loca, thresh):
        #        '''loca is x,y pair, rad is radius (in grid points) data is actual grid to work on\
        #        returns and average for the entire square which is assigned to the point'''

        maxy = len(data)
        maxx = len(data[0])
        startX = loca[1]
        startY = loca[0]

        y1 = startY - rad
        y2 = startY + rad
        x1 = startX - rad
        x2 = startX + rad
        # Make sure bounds are in domain
        if x1 >= maxx:
            x1 = maxx - 1
        elif x1 <= 0:
            x1 = 0
        if x2 >= maxx:
            x2 = maxx - 1
        elif x2 <= 0:
            x2 = 0

        if y1 >= maxy:
            y1 = maxy - 1
        elif y1 <= 0:
            y1 = 0
        if y2 >= maxy:
            y2 = maxy - 1
        elif y2 <= 0:
            y2 = 0

        # Slice a square out of array
        window = data[y1:y2, x1:x2]
        newData = where(greater_equal(window, thresh), 1, 0)
        numpoints = float(window.shape[0] * window.shape[1])
        summa = add.reduce(add.reduce(newData))

        return (summa / numpoints) * 100.0
