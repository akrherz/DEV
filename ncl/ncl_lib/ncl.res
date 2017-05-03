!*Font                           : Helvetica
*cnLineLabelPlacementMode       : computed
*cnLineLabelAngleF              : 0.0
*cnLineLabelBackgroundColor     : -1
*cnInfoLabelOn                  : False
*cnConstFLabelOn                : False
!
*solidline*gsLineThicknessF : 1.
*solidline*gsLineColor : 1
!
*dashedline*gsLineThicknessF : 2.
*dashedline*gsLineColor : 12
*dashedline*gsLineLabelString : dashedline
*dashedline*gsLineDashPattern : 5
*dashedline*gsLineDashSegLenF : .3
!
*marker*gsMarkerColor : 1
*marker*gsMarkerThicknessF : 1.
*marker*gsMarkerIndex : 4
*marker*gsMarkerSizeF : 0.80
!
! Vector plots
!
*vect*vfXCStride		: 2
*vect*vfYCStride		: 2
*vect*vcWindBarbColor		: 36
*vect2*vfXCStride               : 2
*vect2*vfYCStride               : 2
*vect2*vcWindBarbColor          : 36
*vect3*vfXCStride               : 3
*vect3*vfYCStride               : 3
*vect3*vcWindBarbColor          : 36
*vect4*vfXCStride               : 4
*vect4*vfYCStride               : 4
*vect4*vcWindBarbColor          : 36
*vect5*vfXCStride               : 5
*vect5*vfYCStride               : 5
*vect5*vcWindBarbColor          : 36
!
! Default for RUC 40 km Grid
!
*ruc40*mpProjection             : LAMBERTCONFORMAL
*ruc40*mpLambertParallel1F      : 25.0
*ruc40*mpLambertParallel2F      : 25.0
*ruc40*mpLambertMeridianF       : -95.0
*ruc40*mpLimitMode              : points
*ruc40*mpLeftPointLatF          : 54.1733
*ruc40*mpLeftPointLonF          : -139.8567
*ruc40*mpRightPointLatF         : 17.3400
*ruc40*mpRightPointLonF         : -69.03647
*ruc40*mpTopPointLatF           : 55.4818
*ruc40*mpTopPointLonF           : -57.3794
*ruc40*mpBottomPointLatF        : 16.2810
*ruc40*mpBottomPointLonF        : -126.1378
*ruc40*mpGridAndLimbOn          : False
*ruc40*mpLabelsOn               : False
*ruc40*mpPerimOn                : False
*ruc40*mpOutlineBoundarySets    : allBoundaries
!
! Default for GRIB Grid 211
!
*211*mpProjection               : LAMBERTCONFORMAL
*211*mpLambertParallel1F        : 25.0
*211*mpLambertParallel2F        : 25.0
*211*mpLambertMeridianF         : -95.0
*211*mpLimitMode                : points
*211*mpLeftPointLatF            : 54.5364
*211*mpLeftPointLonF            : -152.856
*211*mpRightPointLatF           : 14.3344
*211*mpRightPointLonF           : -65.0903
*211*mpTopPointLatF             : 57.2897
*211*mpTopPointLonF             : -49.3833
*211*mpBottomPointLatF          : 12.19
*211*mpBottomPointLonF          : -133.459
*211*mpGridAndLimbOn            : False
*211*mpLabelsOn                 : False
*211*mpPerimOn                  : False
*211*mpOutlineBoundarySets      : allBoundaries
!
! Default for GRIB Grid 87
!
*87*mpProjection		: STEREOGRAPHIC
*87*mpCenterLatF		: 90.0
*87*mpCenterLonF		: -105.0
*87*mpLimitMode			: Corners
*87*mpLeftCornerLatF		: 22.8755
*87*mpLeftCornerLonF		: -120.4911
*87*mpRightCornerLatF		: 46.0172
*87*mpRightCornerLonF		: -60.8279
*87*mpGridAndLimbOn             : False
*87*mpLabelsOn			: False
*87*mpPerimOn			: False
*87*mpOutlineBoundarySets	: allBoundaries
!
! Default for GRIB Grid 202
!
*202*mpProjection		: STEREOGRAPHIC
*202*mpCenterLatF		: 90.0
*202*mpCenterLonF		: -105.0
*202*mpLimitMode		: Corners
*202*mpLeftCornerLatF		: 7.830
*202*mpLeftCornerLonF		: -141.030
*202*mpRightCornerLatF		: 35.620
*202*mpRightCornerLonF		: -18.570
*202*mpGridAndLimbOn            : False
*202*mpLabelsOn			: False
*202*mpPerimOn			: False
*202*mpOutlineBoundarySets	: allBoundaries
!
! Default for GRIB Grid 212
!
*212*mpProjection		: LAMBERTCONFORMAL
*212*mpLambertParallel1F 	: 25.0
*212*mpLambertParallel2F 	: 25.0
*212*mpLambertMeridianF 	: -95.0
*212*mpLimitMode		: points
*212*mpLeftPointLatF 		: 54.5364
*212*mpLeftPointLonF 		: -152.856
*212*mpRightPointLatF 		: 14.3344
*212*mpRightPointLonF 		: -65.0903
*212*mpTopPointLatF 		: 57.2897
*212*mpTopPointLonF 		: -49.3833
*212*mpBottomPointLatF 		: 12.19
*212*mpBottomPointLonF 		: -133.459
*212*mpGridAndLimbOn            : False
*212*mpLabelsOn			: False
*212*mpPerimOn			: False
*212*mpOutlineBoundarySets	: allBoundaries
!
! Default for GRIB Grid 241
!
*241*mpProjection               : STEREOGRAPHIC
*241*mpCenterLatF               : 90.0
*241*mpCenterLonF               : -105.0
*241*mpLimitMode                : Corners
*241*mpLeftCornerLatF           : 22.813
*241*mpLeftCornerLonF           : -120.351
*241*mpRightCornerLatF          : 45.6454
*241*mpRightCornerLonF          : -60.2738
*241*mpGridAndLimbOn            : False
*241*mpLabelsOn                 : False
*241*mpPerimOn                  : False
*241*mpOutlineBoundarySets      : allBoundaries
!
! Default for Air Force and NESDIS Snow analysis Grid
!
*snowgrid*mpProjection          : STEREOGRAPHIC
*snowgrid*mpCenterLatF          : 90.0
*snowgrid*mpCenterLonF          : -80.0
*snowgrid*mpLimitMode           : points
*snowgrid*mpLeftPointLatF       : -20.77300
*snowgrid*mpLeftPointLonF       : -125.05516
*snowgrid*mpRightPointLatF      : -20.77357
*snowgrid*mpRightPointLonF      : 55.05538
*snowgrid*mpTopPointLatF        : -20.82510
*snowgrid*mpTopPointLonF        : 144.99939
*snowgrid*mpBottomPointLatF     : -20.72136
*snowgrid*mpBottomPointLonF     : -34.99960
*snowgrid*mpGridAndLimbOn       : True
*snowgrid*mpLabelsOn            : True
*snowgrid*mpPerimOn             : True
*snowgrid*mpOutlineBoundarySets : allBoundaries
!
*DEN*mpLeftCornerLatF         : 33.0411
*DEN*mpLeftCornerLonF         : -111.874
*DEN*mpRightCornerLatF        : 45.86345
*DEN*mpRightCornerLonF        : -97.44046
!
*ICT*mpLeftCornerLatF         : 31.10922
*ICT*mpLeftCornerLonF         : -104.3431
*ICT*mpRightCornerLatF        : 43.39226
*ICT*mpRightCornerLonF        : -89.28943
!
*LIT*mpLeftCornerLatF         : 28.39211
*LIT*mpLeftCornerLonF         : -99.97708
*LIT*mpRightCornerLatF        : 40.40219
*LIT*mpRightCornerLonF        : -84.8299
!
*EVV*mpLeftCornerLatF         : 32.83491
*EVV*mpLeftCornerLonF         : -95.0000
*EVV*mpRightCornerLatF        : 44.15139
*EVV*mpRightCornerLonF        : -78.65948
!
*DTW*mpLeftCornerLatF         : 37.11278
*DTW*mpLeftCornerLonF         : -91.41803
*DTW*mpRightCornerLatF        : 47.81417
*DTW*mpRightCornerLonF        : -73.98065
!
*ALB*mpLeftCornerLatF         : 37.49389
*ALB*mpLeftCornerLonF         : -83.75522
*ALB*mpRightCornerLatF        : 47.41682
*ALB*mpRightCornerLonF        : -65.48599
!
*TPA*mpLeftCornerLatF         : 21.794
*TPA*mpLeftCornerLonF         : -89.497
*TPA*mpRightCornerLatF        : 32.948
*TPA*mpRightCornerLonF        : -74.222
!
*MGM*mpLeftCornerLatF         : 26.645
*MGM*mpLeftCornerLonF         : -94.183
*MGM*mpRightCornerLatF        : 38.159
*MGM*mpRightCornerLonF        : -78.687
!
*BWI*mpLeftCornerLatF         : 33.2788
*BWI*mpLeftCornerLonF         : -85.47809
*BWI*mpRightCornerLatF        : 43.62811
*BWI*mpRightCornerLonF        : -68.11899
!
*CLT*mpLeftCornerLatF         : 29.42208
*CLT*mpLeftCornerLonF         : -88.30469
*CLT*mpRightCornerLatF        : 40.24131
*CLT*mpRightCornerLonF        : -71.83115
!
*AUS*mpLeftCornerLatF         : 24.55791
*AUS*mpLeftCornerLonF         : -103.8451
*AUS*mpRightCornerLatF        : 37.06563
*AUS*mpRightCornerLonF        : -89.62863
!
*ABQ*mpLeftCornerLatF         : 27.75788
*ABQ*mpLeftCornerLonF         : -113.2035
*ABQ*mpRightCornerLatF        : 40.98315
*ABQ*mpRightCornerLonF        : -99.64545
!
*COD*mpLeftCornerLatF         : 38.37666
*COD*mpLeftCornerLonF         : -115.9208
*COD*mpRightCornerLatF        : 51.10908
*COD*mpRightCornerLonF        : -101.2116
!
*LWS*mpLeftCornerLatF         : 37.47775
*LWS*mpLeftCornerLonF         : -124.429
*LWS*mpRightCornerLatF        : 50.92648
*LWS*mpRightCornerLonF        : -111.0443
!
*WMC*mpLeftCornerLatF         : 33.97141
*WMC*mpLeftCornerLonF         : -123.4918
*WMC*mpRightCornerLatF        : 47.64445
*WMC*mpRightCornerLonF        : -110.4568
!
*LAS*mpLeftCornerLatF         : 29.2081
*LAS*mpLeftCornerLonF         : -120.6371
*LAS*mpRightCornerLatF        : 43.03768
*LAS*mpRightCornerLonF        : -107.8179
!
*MSP*mpLeftCornerLatF         : 38.843
*MSP*mpLeftCornerLonF         : -100.4614
*MSP*mpRightCornerLatF        : 50.24743
*MSP*mpRightCornerLonF        : -83.71646
!
*PIR*mpLeftCornerLatF         : 38.42895
*PIR*mpLeftCornerLonF         : -108.164
*PIR*mpRightCornerLatF        : 50.53161
*PIR*mpRightCornerLonF        : -92.4299
!
! Mean Sea Level Pressure plots
!
*mslp*cnLevelSelectionMode      : ManualLevels
*mslp*cnLevelSpacingF           : 2.0
*mslp*cnMinLevelValF            : 972
*mslp*cnMaxLevelValF            : 1044
*mslp*cnHighLabelsOn            : True
*mslp*cnHighLabelFont           : 22
*mslp*cnHighLabelFontHeightF    : 0.020
*mslp*cnHighLabelFontThicknessF : 3.0
*mslp*cnHighLabelBackgroundColor        : Transparent
*mslp*cnHighLabelFontColor      : 8
*mslp*cnLowLabelsOn             : True
*mslp*cnLowLabelFont            : 22
*mslp*cnLowLabelFontHeightF     : 0.020
*mslp*cnLowLabelFontThicknessF  : 3.0
*mslp*cnLowLabelBackgroundColor : Transparent
*mslp*cnLowLabelFontColor       : 28
*mslp*cnLineLabelFontHeightF    : 0.009
*mslp*cnFillOn			: True
*mslp*cnFillColors              : (/31,31,31,31,31,31,31,31,31,31,30,30,28,28,26,26,25,25,24,24,23,23,23,23,13,13,12,12,11,11,10,10, 8, 8, 6, 6, 5, 5/)
*mslp*cnMonoFillPattern         : False
*mslp*cnFillPatterns            : (/11,11,11,11,11,11,11,11,11,11,10,10, 9, 9, 8, 8, 7, 7, 4, 4, 3, 3, 3, 3, 4, 4,12,12,13,13,14,14,15,15,16,16,16,16/)
*mslp*cnMonoFillScale           : False
*mslp*cnFillScales              : (/.1,.1,.2,.2,.3,.3,.3,.3,.3,.3,.3,.3,.4,.4,.4,.4,.4,.4,.5,.5,.7,.7,.3,.3,.5,.5,.5,.5,.5,.5,.4,.4,.4,.4,.3,.3,.2,.2/)
!
! Speed (kts) plots  (LOW-LEVEL)
!
*speed1*cnLevelSelectionMode     : ExplicitLevels
*speed1*cnLevels                 : (/15.,20.,30.,40.,50.,60.,70./)
*speed1*cnHighLabelsOn           : False
*speed1*cnLowLabelsOn            : False
*speed1*cnLineLabelsOn           : False
*speed1*cnLinesOn                : True
*speed1*cnLineColor              : 3
*speed1*cnLineDashPattern        : 5
*speed1*cnLineDashSegLenF        : .12
*speed1*cnFillOn                 : True
*speed1*cnFillColors             : (/-1,13,13,23,23,24,24,26,28,30/)
*speed1*cnMonoFillPattern        : False
*speed1*cnFillPatterns           :  (/0, 3, 4, 3, 4, 3, 4, 3, 4, 3/)
*speed1*cnMonoFillScale          : False
*speed1*cnFillScales             : (/1.,.5,.2,.4,.2,.4,.2,.2,.2,.2/)
!
! Speed (kts) plots  (UPPER-LEVEL)
!
*speed2*cnLevelSelectionMode     : ExplicitLevels
*speed2*cnLevels                 : (/30.,50.,70.,90.,110.,130.,150.,170.,190./)
*speed2*cnHighLabelsOn           : False
*speed2*cnLowLabelsOn            : False
*speed2*cnLineLabelsOn           : False
*speed2*cnLinesOn                : True
*speed2*cnLineColor              : 3
*speed2*cnLineDashPattern        : 5
*speed2*cnLineDashSegLenF        : .11
*speed2*cnFillOn                 : True
*speed2*cnFillColors             : (/-1,13,13,23,23,24,26,28,30,30/)
*speed2*cnMonoFillPattern        : False
*speed2*cnFillPatterns           :  (/0, 3, 4, 3, 4, 4, 3, 4, 3, 0/)
*speed2*cnMonoFillScale          : False
*speed2*cnFillScales             : (/1.,.5,.2,.4,.2,.2,.2,.2,.2,1./)
!
! Geo_Height 200 mb plots
!
*geoz200*cnLevelSelectionMode   : ManualLevels
*geoz200*cnLevelSpacingF        : 12.0
*geoz200*cnMinLevelValF         : 918.0
*geoz200*cnHighLabelsOn         : False
*geoz200*cnLowLabelsOn          : False
*geoz200*cnLineLabelInterval    : 1
*geoz200*cnLineLabelFontHeightF : 0.008
*geoz200*cnLineLabelFontColor   : 36
*geoz200*cnLineColor            : 34
*geoz200*cnFillOn               : False
*geoz200*cnLineThicknessF       : 2.0
!
! Geo_Height 250 mb plots
!
*geoz250*cnLevelSelectionMode   : ManualLevels
*geoz250*cnLevelSpacingF        : 12.0
*geoz250*cnMinLevelValF         : 894.0
*geoz250*cnHighLabelsOn         : False
*geoz250*cnLowLabelsOn          : False
*geoz250*cnLineLabelInterval    : 1
*geoz250*cnLineLabelFontHeightF : 0.008
*geoz250*cnLineLabelFontColor   : 36
*geoz250*cnLineColor            : 34
*geoz250*cnFillOn               : False
*geoz250*cnLineThicknessF       : 2.0
!
! Geo_Height 300 mb plots
!
*geoz300*cnLevelSelectionMode   : ManualLevels
*geoz300*cnLevelSpacingF        : 12.0
*geoz300*cnMinLevelValF         : 870.0
*geoz300*cnHighLabelsOn         : False
*geoz300*cnLowLabelsOn          : False
*geoz300*cnLineLabelInterval    : 1
*geoz300*cnLineLabelFontHeightF : 0.008
*geoz300*cnLineLabelFontColor   : 36
*geoz300*cnLineColor            : 34
*geoz300*cnFillOn               : False
*geoz300*cnLineThicknessF       : 2.0
!
! Geo_Height 500 mb plots
!
*geoz500*cnLevelSelectionMode   : ManualLevels
*geoz500*cnLevelSpacingF        : 6.0
*geoz500*cnMinLevelValF         : 492.0
*geoz500*cnHighLabelsOn         : False
*geoz500*cnLowLabelsOn          : False
*geoz500*cnLineLabelInterval    : 1
*geoz500*cnLineLabelFontHeightF : 0.008
*geoz500*cnLineLabelFontColor   : 36
*geoz500*cnLineColor            : 34
*geoz500*cnFillOn               : False
*geoz500*cnLineThicknessF       : 2.0
!
! Geo_Height 700 mb plots
!
*geoz700*cnLevelSelectionMode   : ManualLevels
*geoz700*cnLevelSpacingF        : 3.0
*geoz700*cnMinLevelValF         : 240.0
*geoz700*cnHighLabelsOn         : False
*geoz700*cnLowLabelsOn          : False
*geoz700*cnLineLabelInterval    : 1
*geoz700*cnLineLabelFontHeightF : 0.008
*geoz700*cnLineLabelFontColor   : 36
*geoz700*cnLineColor            : 34
*geoz700*cnFillOn               : False
*geoz700*cnLineThicknessF       : 2.0
!
! Geo_Height 850 mb plots
!
*geoz850*cnLevelSelectionMode   : ManualLevels
*geoz850*cnLevelSpacingF        : 3.0
*geoz850*cnMinLevelValF         : 120.0
*geoz850*cnHighLabelsOn         : False
*geoz850*cnLowLabelsOn          : False
*geoz850*cnLineLabelInterval    : 1
*geoz850*cnLineLabelFontHeightF : 0.008
*geoz850*cnLineLabelFontColor   : 36
*geoz850*cnLineColor            : 34
*geoz850*cnFillOn               : False
*geoz850*cnLineThicknessF       : 2.0
!
! Temperature (F) plots
!
*tempF*cnLevelSelectionMode 	: ManualLevels
*tempF*cnLevelSpacingF	 	:  5.0
*tempF*cnMinLevelValF 		: -30.0
*tempF*cnMaxLevelValF 		: 95.0
*tempF*cnHighLabelsOn		: False
*tempF*cnLowLabelsOn		: False
*tempF*cnLineLabelFontHeightF	: 0.011
*tempF*cnFillOn			: True
*tempF*cnFillColors		: (/-1,-1,-1,2,3,4,5,6,8,10,11,12,13,14,15,18,21,22,23,24,25,26,28,30,31,-1,-1/)
!
! Temps (C) line contours
!
*tempC*cnLevelSelectionMode     : ManualLevels
*tempC*cnLevelSpacingF          :  5.0
*tempC*cnMinLevelValF           : -60.0
*tempC*cnMaxLevelValF           : 40.0
*tempC*cnHighLabelsOn           : False
*tempC*cnLowLabelsOn            : False
*tempC*cnMonoLineLabelFontColor : False
*tempC*cnLineLabelFontColors    : (/ 2, 2, 2, 2, 2, 2, 3, 4, 5, 6, 8,10,11, 1,25,26,27,28,29,30,31,31/)
*tempC*cnLineLabelFontHeightF   : 0.008
*tempC*cnFillOn                 : False
*tempC*cnLineLabelInterval      : 1
*tempC*cnLineLabelBackgroundColor       : 0
*tempC*cnMonoLineColor          : False
*tempC*cnLineColors             : (/ 2, 2, 2, 2, 2, 2, 3, 4, 5, 6, 8,10,11,25,26,27,28,29,30,31,31/)
*tempC*cnMonoLineThickness      : False
*tempC*cnLineThicknesses        : (/2.,2.,2.,2.,2.,2.,2.,2.,2.,2.,2.,2.,3.,2.,2.,2.,2.,2.,2.,2.,2./)
*tempC*cnMonoLineDashPattern    : False
*tempC*cnLineDashPatterns       : (/ 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0/)
*tempC*cnLineDashSegLenF        : .05
!
! Dewpoint Temperature F plots
!
*dewpF*cnLevelSelectionMode 	: ExplicitLevels
*dewpF*cnLevels 		: (/-40.,-30.,-20.,-10.,0.,10.,20.,30.,35.,40.,45.,50.,55.,60.,65.,70.,75.,80./)
*dewpF*cnHighLabelsOn		: False
*dewpF*cnLowLabelsOn		: False
*dewpF*cnFillOn			: True
*dewpF*cnFillColors		: (/-1,-1,-1,-1,-1,-1,-1,-1,12,13,14,18,22,23,24,25,26,28,30,31,-1/)
*dewpF*cnExplicitLabelBarLabelsOn	: True
*dewpF*cnLineLabelFontHeightF	: 0.011
*dewpF*cnLineLabelInterval	: 1
*dewpF*lbLabelStrings		: (/-40,-30,-20,-10,0,10,20,30,35,40,45,50,55,60,65,70,75,80,85/)
!
! Theta-E (C) plots
!
*thetae*cnLevelSelectionMode 	: ManualLevels
*thetae*cnLevelSpacingF	 	: 5.0
*thetae*cnMinLevelValF 		: -10.0
*thetae*cnMaxLevelValF 		: 95.0
*thetae*cnHighLabelsOn		: False
*thetae*cnLowLabelsOn		: False
*thetae*cnLineLabelFontHeightF	: 0.011
*thetae*cnFillOn		: True
*thetae*cnFillColors		: (/-1,-1,2,3,4,5,6,8,10,11,12,13,14,15,18,21,22,23,24,25,26,28,30,31,-1,-1/)
!
! 3-hour Pressure Tendency plot
!
*ptend*cnLevelSelectionMode     : ManualLevels
*ptend*cnLevelSpacingF          : 0.25
*ptend*cnMinLevelValF           : -2.0
*ptend*cnMaxLevelValF           : 2.0
*ptend*cnHighLabelsOn           : True
*ptend*cnHighLabelFont          : 22
*ptend*cnHighLabelBackgroundColor       : Transparent
*ptend*cnHighLabelFontColor     : 28
*ptend*cnHighLabelFontHeightF   : 0.013
*ptend*cnLowLabelsOn            : True
*ptend*cnLowLabelFont           : 22
*ptend*cnLowLabelBackgroundColor        : Transparent
*ptend*cnLowLabelFontColor      : 8
*ptend*cnLowLabelFontHeightF    : 0.013
*ptend*cnFillOn                 : True
*ptend*cnFillColors             : (/2, 3, 4, 5, 6, 8,10,11,13,23,24,25,26,28,30,31,31,31/)
*ptend*cnMonoFillPattern        : False
*ptend*cnFillPatterns           : (/14,12,12,10,10, 8, 8, 3, 3, 4, 4, 7, 7, 9, 9,11,11,13/)
*ptend*cnMonoFillScale          : False
*ptend*cnFillScales             : (/.2,.2,.2,.2,.2,.2,.2,.2,.4,.4,.2,.2,.2,.2,.2,.2,.2,.2/)
*ptend*cnLineLabelInterval      : 1
*ptend*cnLineLabelBackgroundColor       : 0
*ptend*cnLineLabelFontHeightF   : 0.011
*ptend*cnMonoLineThickness      : False
*ptend*cnLineThicknesses        : (/1.,1.,1.,1.,1.,1.,1.,1.,3.,1.,1.,1.,1.,1.,1.,1.,1.,1./)
*ptend*cnMonoLineDashPattern    : False
*ptend*cnLineDashPatterns       : (/5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0/)
*ptend*cnLineDashSegLenF        : .1
!
! CAPE (J/kg) plots
!
*cape*cnLevelSelectionMode 	: ManualLevels
*cape*cnLevelSpacingF           : 500.0
*cape*cnMinLevelValF            : 500.0
*cape*cnMaxLevelValF            : 6000.0
*cape*cnHighLabelsOn		: False
*cape*cnLowLabelsOn		: False
*cape*cnLineLabelInterval	: 1
*cape*cnLineLabelFontHeightF	: 0.009
*cape*cnFillOn			: True
*cape*cnFillColors		: (/-1,17,18,21,22,23,24,25,26,28,30,31,2/)
!
! CIN (J/kg) plots
!
*cin*cnLevelSelectionMode 	: ExplicitLevels
*cin*cnLevels 			: (/-250.0,-150.0,-75.0,-25.0/)
*cin*cnHighLabelsOn             : False
*cin*cnLowLabelsOn              : False
*cin*cnLineLabelInterval        : 1
*cin*cnLineLabelFontHeightF     : 0.009
*cin*cnLineColor                : 11
*cin*cnLineLabelFontColor       : 10
*cin*cnFillOn                   : True
*cin*cnMonoFillPattern          : False
*cin*cnFillPatterns             : (/ 4, 3, 0, 0, 0/)
*cin*cnMonoFillScale            : False
*cin*cnFillScales               : (/.5,.7,1.,1.,1./)
*cin*cnFillColors               : (/10,11,-1,-1,-1/)
!
! Precip category plots
!
*prcp_cat*cnLevelSelectionMode 	: ManualLevels
*prcp_cat*cnLevelSpacingF	: 1.0
*prcp_cat*cnMinLevelValF 	: 0.0
*prcp_cat*cnMaxLevelValF 	: 4.0
*prcp_cat*cnRasterModeOn        : True
*prcp_cat*cnRasterSmoothingOn   : False
*prcp_cat*cnHighLabelsOn        : False
*prcp_cat*cnLowLabelsOn         : False
*prcp_cat*cnLinesOn             : False
*prcp_cat*cnLineLabelsOn        : False
*prcp_cat*cnExplicitLabelBarLabelsOn    : True
*prcp_cat*lbLabelStrings        : (/0,RA,SN,FZRA,PL,MIX/)
*prcp_cat*lbLabelAlignment      : BoxCenters
*prcp_cat*cnFillOn		: False
*prcp_cat*cnFillColors          : (/0,18,12,23,28, 3/)
!
! Precip (24-hour) plots
!
*totpcp*cnLevelSelectionMode 	: ExplicitLevels
*totpcp*cnLevels 		: (/0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1.0,1.50,2.0,3.0,4.0/)
*totpcp*cnHighLabelsOn		: False
*totpcp*cnLowLabelsOn		: False
*totpcp*cnLinesOn		: False
*totpcp*cnLineLabelsOn		: False
*totpcp*cnFillOn		: True
*totpcp*cnFillColors		: (/-1,14,15,18,21,22,23,24,25,26,28,30,31,28/)
*totpcp*cnMonoFillPattern	: False
*totpcp*cnFillPatterns		:  (/0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4/)
*totpcp*cnMonoFillScale		: False
*totpcp*cnFillScales		: (/1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.,.3/)
!
! Precip (24-hour) plots
!
*pcp24*cnLevelSelectionMode     : ExplicitLevels
*pcp24*cnLevels                 : (/0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1.0,1.25,1.50,1.75,2.0,3.0,4.0/)
!!*pcp24*cnRasterModeOn         : True
!!*pcp24*cnRasterSmoothingOn    : False
*pcp24*cnHighLabelsOn           : False
*pcp24*cnLowLabelsOn            : False
*pcp24*cnLinesOn                : False
*pcp24*cnLineLabelsOn           : False
*pcp24*cnFillOn                 : True
*pcp24*cnFillColors             : (/-1,14,15,18,21,22,23,24,25,26,28,30,31,28,28,28/)
!
! Precipitable Water (cm)
!
*pwat*cnLevelSelectionMode 	: ManualLevels
*pwat*cnLevelSpacingF	 	: 0.5
*pwat*cnMinLevelValF 		: 1.0
*pwat*cnMaxLevelValF 		: 4.5
*pwat*cnHighLabelsOn		: False
*pwat*cnLowLabelsOn		: False
*pwat*cnLinesOn			: False
*pwat*cnLineLabelsOn		: False
*pwat*cnFillOn			: True
*pwat*cnFillColors		: (/-1,13,14,15,18,21,22,23,24/)
!
! Lifted Index (C) plots
!
*lift*cnLevelSelectionMode 	: ManualLevels
*lift*cnLevelSpacingF	 	: 2.0
*lift*cnMinLevelValF 		: -12.0
*lift*cnMaxLevelValF 		: 4.0
*lift*cnHighLabelsOn            : False
*lift*cnLowLabelsOn             : False
*lift*cnLineLabelInterval	: 1
*lift*cnLineLabelFontHeightF	: 0.010
*lift*cnLineColor               : 10
*lift*cnLineLabelFontColor      : 8
!
! SREH (m2/s2) plots
!
*sreh*cnLevelSelectionMode     : ExplicitLevels
*sreh*cnLevels                 : (/50.0,100.0,150.0,200.0,300.0,400.0,500.0/)
!*sreh*cnLevelSelectionMode 	: ManualLevels
!*sreh*cnLevelSpacingF	 	: 50.0
!*sreh*cnMinLevelValF 		: 50.0
!*sreh*cnMaxLevelValF 		: 400.0
*sreh*cnHighLabelsOn		: False
*sreh*cnLowLabelsOn		: False
*sreh*cnLineLabelInterval	: 1
*sreh*cnLineLabelFontHeightF	: 0.008
*sreh*cnFillOn			: True
*sreh*cnFillColors		: (/-1,23,23,24,24,25,25,28,28/)
*sreh*cnMonoFillPattern		: False
*sreh*cnFillPatterns		:  (/0, 3, 4, 3, 4, 3, 4, 3, 0/)
*sreh*cnMonoFillScale		: False
*sreh*cnFillScales		: (/1.,.6,.4,.5,.3,.3,.2,.2,1./)
!
! Cloud water
!
*cloud*cnLevelSelectionMode     : ExplicitLevels
*cloud*cnLevels                 : (/0.0001, 0.010, 0.10/)
*cloud*cnHighLabelsOn           : False
*cloud*cnLowLabelsOn            : False
*cloud*cnFillOn                 : True
*cloud*cnLineColor              : 23
*cloud*cnLineLabelsOn           : False
*cloud*cnFillColors             : (/-1, 22, 20, 18/)
*cloud*cnExplicitLabelBarLabelsOn : True
*cloud*lbLabelStrings           : (/.,.,.,WATER/)
*cloud*lbLabelAlignment         : BoxCenters
!
! Supercooled Liquid Water
!
*slw*cnLevelSelectionMode       : ExplicitLevels
*slw*cnLevels                   : (/0.0001, 0.010, 0.10/)
*slw*cnHighLabelsOn             : False
*slw*cnLowLabelsOn              : False
*slw*cnLinesOn                  : True
*slw*cnLineLabelsOn             : False
*slw*cnLineColor                : 25
*slw*cnLineDashPattern          : 5
*slw*cnLineDashSegLenF          : .10
*slw*cnFillOn                   : True
*slw*cnFillColors               : (/-1,25,26,28/)
*slw*cnMonoFillPattern          : False
*slw*cnFillPatterns             :  (/0, 4, 4, 4/)
*slw*cnMonoFillScale            : False
*slw*cnFillScales               : (/1.,.5,.35,.25/)
*slw*cnExplicitLabelBarLabelsOn : True
*slw*lbLabelStrings             : (/.,.,SUPERCOOLED,./)
*slw*lbLabelAlignment           : BoxCenters
!
! Cloud ice
!
*ice*cnLevelSelectionMode       : ExplicitLevels
*ice*cnLevels                   : (/0.0001, 0.005/)
*ice*cnHighLabelsOn             : False
*ice*cnLowLabelsOn              : False
*ice*cnLinesOn                  : True
*ice*cnLineLabelsOn             : False
*ice*cnLineColor                : 8
*ice*cnLineDashPattern          : 5
*ice*cnLineDashSegLenF          : .10
*ice*cnFillOn                   : True
*ice*cnFillColors               : (/-1,13,12,11/)
*ice*cnMonoFillPattern          : False
*ice*cnFillPatterns             :  (/0, 3, 3, 3/)
*ice*cnMonoFillScale            : False
*ice*cnFillScales               : (/1.,.5,.3,.2/)
*ice*cnExplicitLabelBarLabelsOn : True
*ice*lbLabelStrings             : (/.,.,ICE,./)
*ice*lbLabelAlignment           : BoxCenters
!
! Mixing Ratio (g/kg) plots
!
*Mixr*cnLevelSelectionMode      : ManualLevels
*Mixr*cnLevelSpacingF           : 2.0
*Mixr*cnMinLevelValF            : 8.0
*Mixr*cnMaxLevelValF 		: 16.0
*Mixr*cnHighLabelsOn            : False
*Mixr*cnLowLabelsOn             : False
*Mixr*cnFillOn                  : True
*Mixr*cnLinesOn                 : False
*Mixr*cnLineLabelsOn            : False
*Mixr*cnFillColors              : (/-1,14,14,21,22,23/)
*Mixr*cnMonoFillPattern         : False
*Mixr*cnFillPatterns            :  (/0, 3, 0, 0, 0, 0/)
*Mixr*cnMonoFillScale           : False
*Mixr*cnFillScales              : (/1.,.4,1.,1.,1.,1./)
!
! Vertical Velocity (m/s) plots
!
*Vvel*cnLevelSelectionMode      : ExplicitLevels
*Vvel*cnLevels                  : (/-25.,-10.,-5.,-2.,2.,5.,10.,25.,50./)
*Vvel*cnLinesOn                 : False
*Vvel*cnLineLabelsOn            : False
*Vvel*cnHighLabelsOn            : False
*Vvel*cnLowLabelsOn             : False
*Vvel*cnFillOn                  : True
*Vvel*cnFillColors              : (/23,22,21,14,-1,23,24,25,28,31/)
*Vvel*cnExplicitLabelBarLabelsOn        : True
*Vvel*lbLabelStrings            : (/-25,-10,-5,-2,2,5,10,25,50/)
!
! Radar plots
!
*radar*cnLevelSelectionMode 	: ExplicitLevels
*radar*cnLevels 		: (/0.,.01,1.,2.,4.,6.,8.,10.,13.,16.,20.,25.,30.,35.,40.,45.,50.,55.,60.,65.,90./)
*radar*cnHighLabelsOn		: False
*radar*cnLowLabelsOn		: False
*radar*cnLineLabelFontHeightF	: 0.011
*radar*cnLinesOn		: False
*radar*cnFillOn			: True
*radar*cnFillColors		: (/-1,-1,2,3,4,5,6,8,10,11,13,15,18,21,23,24,26,28,30,31,31,31,-1/)
!
! Relative Humidity (%) plots
!
*relh*cnLevelSelectionMode 	: ExplicitLevels
*relh*cnLevels 			: (/30.,50.,70.,80.,90./)
*relh*cnHighLabelsOn		: False
*relh*cnLowLabelsOn		: False
*relh*cnLinesOn                 : False
*relh*cnLineLabelsOn		: False
*relh*cnFillOn			: True
*relh*cnFillColors		: (/24,-1,-1,23,21,18/)
!
! 1000-500 Thickness plots
!
*thick*cnLevelSelectionMode 	: ManualLevels
*thick*cnLevelSpacingF		: 6.0
*thick*cnMinLevelValF 		: 486.0
*thick*cnMaxLevelValF 		: 582.0
*thick*cnHighLabelsOn		: False
*thick*cnLowLabelsOn		: False
*thick*cnLineLabelFontHeightF	: 0.008
*thick*cnFillOn			: False
*thick*cnLineDashPattern	: 2
*thick*cnLineDashSegLenF	: .10
*thick*cnLineLabelInterval	: 1
*thick*cnMonoLineLabelFontColor	: False
*thick*cnLineLabelFontColors	: (/ 2, 2, 2, 2, 2, 3, 4, 5, 6, 8,10,11,25,26,27,28,29,30,31,31/)
*thick*cnMonoLineColor		: False
*thick*cnLineColors 		: (/ 2, 2, 2, 2, 2, 3, 4, 5, 6, 8,10,11,25,26,27,28,29,30,31,31/)
*thick*cnMonoLineThickness      : False
*thick*cnLineThicknesses        : (/1.,1.,1.,1.,1.,1.,1.,1.,1.,3.,1.,1.,1.,1.,1.,1.,1.,1.,1.,1./)
!
! Vorticity (/s) plots
!
*vort*cnLevelSelectionMode 	: ManualLevels
*vort*cnLevelSpacingF	 	: 3.0
*vort*cnMinLevelValF 		: 0.0
*vort*cnMaxLevelValF 		: 30.0
*vort*cnHighLabelsOn		: True
*vort*cnHighLabelString		: X
*vort*cnHighLabelFontColor	: 1
*vort*cnHighLabelBackgroundColor	: Transparent
*vort*cnLowLabelsOn		: True
*vort*cnLowLabelString		: N
*vort*cnLowLabelFontColor	: 1
*vort*cnLowLabelBackgroundColor	: Transparent
*vort*cnLinesOn			: True
*vort*cnLineColor               : 11
*vort*cnLineLabelsOn		: False
*vort*cnFillOn			: True
*vort*cnFillColors		: (/12,13,-1,-1,15,18,21,23,24,25,26,28/)
!
! Snow Depth plots
!
*snowd*cnLevelSelectionMode     : ExplicitLevels
!*snowd*cnLevels                 : (/-1.0,0.0,1.0,3.0,6.0,12.0,24.0,36.0/)
*snowd*cnLevels                 : (/-1.0,0.0,2.54,7.62,15.24,30.48,60.96,91.44/)
*snowd*cnHighLabelsOn           : False
*snowd*cnLowLabelsOn            : False
*snowd*cnLinesOn                : False
*snowd*cnLineLabelsOn           : False
*snowd*cnFillOn                 : True
*snowd*cnFillColors             : (/-1,13,-1, 3, 3, 3, 4, 5, 0/)
*snowd*cnMonoFillPattern        : False
*snowd*cnFillPatterns           :  (/0, 7, 0, 3, 4, 0, 0, 0, 0/)
*snowd*cnMonoFillScale          : False
*snowd*cnFillScales             : (/1.,.2,1.,.5,.2,1.,1.,1.,1./)
*snowd*cnExplicitLabelBarLabelsOn       : True
*snowd*lbLabelStrings           : (/ice,0, 1, 3, 6,12,24,36/)
!
! Snow Cover plots
!
*snowc*cnLevelSelectionMode     : ExplicitLevels
*snowc*cnLevels                 : (/-1.0,0.0,0.5/)
*snowc*cnHighLabelsOn           : False
*snowc*cnLowLabelsOn            : False
*snowc*cnLinesOn                : False
*snowc*cnLineLabelsOn           : False
*snowc*cnFillOn                 : True
*snowc*cnFillColors             : (/-1,13,-1, 0/)
*snowc*cnMonoFillPattern        : False
*snowc*cnFillPatterns           :  (/0, 7, 0, 0/)
*snowc*cnMonoFillScale          : False
*snowc*cnFillScales             : (/1.,.2,1.,1./)
!
! Flux moisture divergence (g/kg/hr) plots
!
*mcon*cnLevelSelectionMode      : ManualLevels
*mcon*cnLevelSpacingF           : 0.50
*mcon*cnMinLevelValF            : -6.0
*mcon*cnMaxLevelValF            : -1.0
*mcon*cnHighLabelsOn            : False
*mcon*cnLowLabelsOn             : False
*mcon*cnLinesOn                 : False
*mcon*cnLineLabelsOn            : False
*mcon*cnFillOn                  : True
*mcon*cnFillColors              : (/31,28,26,25,24,23,21,18,15,14,13,-1/)
!
! Vorticity Generation Potential ( ) plots
!
*vgp*cnLevelSelectionMode       : ManualLevels
*vgp*cnLevelSpacingF            : 0.10
*vgp*cnMinLevelValF             : 0.10
*vgp*cnMaxLevelValF             : 1.00
*vgp*cnHighLabelsOn             : True
*vgp*cnHighLabelBackgroundColor : Transparent
*vgp*cnHighLabelFontHeightF     : 0.013
*vgp*cnLowLabelsOn              : False
*vgp*cnLineLabelInterval	: 1
*vgp*cnFillOn                   : True
*vgp*cnFillColors               : (/-1,15,18,21,23,24,25,26,28,31/)
!
! Precip Rain plots
!
*pcpra*cnLevelSelectionMode     : ExplicitLevels
*pcpra*cnLevels                 : (/0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1.0/)
*pcpra*cnHighLabelsOn           : False
*pcpra*cnLowLabelsOn            : False
*pcpra*cnLinesOn                : False
*pcpra*cnLineLabelsOn           : False
*pcpra*cnFillOn                 : True
*pcpra*cnFillColors             : (/-1,61,62,63,64,65,66,67,68,69/)
!
! Precip Snow plots
!
*pcpsn*cnLevelSelectionMode     : ExplicitLevels
*pcpsn*cnLevels                 : (/0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1.0/)
*pcpsn*cnHighLabelsOn           : False
*pcpsn*cnLowLabelsOn            : False
*pcpsn*cnLinesOn                : False
*pcpsn*cnLineLabelsOn           : False
*pcpsn*cnFillOn                 : True
*pcpsn*cnFillColors             : (/-1,41,42,43,44,45,46,47,48,49/)
!
! Precip FZRA plots
!
*pcpfz*cnLevelSelectionMode     : ExplicitLevels
*pcpfz*cnLevels                 : (/0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1.0/)
*pcpfz*cnHighLabelsOn           : False
*pcpfz*cnLowLabelsOn            : False
*pcpfz*cnLinesOn                : False
*pcpfz*cnLineLabelsOn           : False
*pcpfz*cnFillOn                 : True
*pcpfz*cnFillColors             : (/-1,51,52,53,54,55,56,57,58,59/)
!
! Precip PL plots
!
*pcpip*cnLevelSelectionMode     : ExplicitLevels
*pcpip*cnLevels                 : (/0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1.0/)
*pcpip*cnHighLabelsOn           : False
*pcpip*cnLowLabelsOn            : False
*pcpip*cnLinesOn                : False
*pcpip*cnLineLabelsOn           : False
*pcpip*cnFillOn                 : True
*pcpip*cnFillColors             : (/-1,71,72,73,74,75,76,77,78,79/)
!
! Precip Mix plots
!
*pcpmx*cnLevelSelectionMode     : ExplicitLevels
*pcpmx*cnLevels                 : (/0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1.0/)
*pcpmx*cnHighLabelsOn           : False
*pcpmx*cnLowLabelsOn            : False
*pcpmx*cnLinesOn                : False
*pcpmx*cnLineLabelsOn           : False
*pcpmx*cnFillOn                 : True
*pcpmx*cnFillColors             : (/-1,81,82,83,84,85,86,87,88,89/)
!
! Type1 text annotation
!
*Type1*amParallelPosF           : .002
*Type1*amOrthogonalPosF         : .998
*Type1*amJust                   : TopLeft
*Type1*amZone                   : 1
*Type1*txFont                   : 21
*Type1*txFontHeightF            : .015
*Type1*txPerimOn                : True
*Type1*txFontColor              : 1
*Type1*txBackgroundFillColor    : 0
!
! Type2 text annotation
!
*Type2*amParallelPosF           : .998
*Type2*amOrthogonalPosF         : .998
*Type2*amJust                   : TopRight
*Type2*amZone                   : 1
*Type2*txFont                   : 21
*Type2*txFontHeightF            : .012
*Type2*txPerimOn                : True
*Type2*txFontColor              : 1
*Type2*txBackgroundFillColor    : 0
