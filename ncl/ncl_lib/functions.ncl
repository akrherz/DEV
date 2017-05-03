;
; returns an array of the corners of a 2d array
;
        function corners(a[*][*]:numeric)
        begin
                return((/a(0,0),a(0,dimsizes(a(0,:))-1),a(dimsizes(a(:,0))-1,dimsizes(a(0,:))-1),a(dimsizes(a(:,0))-1,0)/))
        end

; [Greg this will be an important function for you to use]
; Given the corners of an area in lat and longitude this will set 
; the map limit to be these corner values
;  
        procedure fitmap(mp[1]:graphic,lat[*][*]:numeric,lon[*][*]:numeric)
        local tlat,tlon,t,b,l,r
        begin
                tlat =  corners(lat)
                tlon =  corners(lon)
                NhlDataToNDC(mp,tlon,tlat,tlon,tlat)
                print((/tlon,tlat/))
                t = max(tlat)
                b = min(tlat)
                l = min(tlon)
                r = max(tlon)
                print((/t,b,l,r/))
                setvalues mp
                        "mpLimitMode" : "NDC"
                        "mpTopNDCF" : t
                        "mpBottomNDCF" : b
                        "mpLeftNDCF" : l
                        "mpRightNDCF" : r
                end setvalues
        end 


;
; Creates a data object from 1,2 or 3D data
;
	function MakeData(val:numeric,name[1]:string)
	local ndims,dims,data
	begin
		ndims = dimsizes(dimsizes(val));
		dims = dimsizes(val);
		if((ndims .eq. 1).and.(dims.gt.1)) then
			data = create name coordArraysClass noparent
				"caYArray" : val
			end create
			if(isatt(val,"_FillValue")) then
				setvalues data
					"caMissingValueV" :val@_FillValue
				end setvalues
			end if
			return (data)
		end if
		if(ndims .eq. 2) then
			if(any(dims  .eq. 2)) then
				if(dims(0).eq.2) then
					data = create name coordArraysClass noparent
						"caXArray" : val(0,:)
						"caYArray" : val(1,:)
					end create
				else
					data = create name coordArraysClass noparent
						"caXArray" : val(:,0)
						"caYArray" : val(:,1)
					end create
				end if
				if(isatt(val,"_FillValue")) then
					setvalues data
						"caMissingValueV" :val@_FillValue
					end setvalues
				end if
				return(data)
			else
				data = create name scalarFieldClass noparent
					"sfDataArray" : val
				end create
				if(isatt(val,"_FillValue")) then
					setvalues data
						"sfMissingValueV" : val@_FillValue
					end setvalues
				end if
				return(data)
			end if
		end if
		if(ndims .eq. 3) then
			if(dims(0) .eq. 2) then
				data = create name vectorFieldClass  noparent
					"vfUDataArray" : val(0,:,:)
					"vfVDataArray" : val(1,:,:)
				end create
			end if
			if(dims(1) .eq. 2) then
				data = create name vectorFieldClass  noparent
					"vfUDataArray" : val(:,0,:)
					"vfVDataArray" : val(:,1,:)
				end create
			end if
			if(dims(2) .eq. 2) then
				data = create name vectorFieldClass  noparent
					"vfUDataArray" : val(:,:,0)
					"vfVDataArray" : val(:,:,0)
				end create
			end if
			if(isatt(val,"_FillValue")) then
				setvalues data
					"vfMissingUValueV" : val@_FillValue
					"vfMissingVValueV" : val@_FillValue
				end setvalues
			end if
			return(data)
		end if
		data = new(1,graphic)
		return(data)
	end

;
; create proper workspace (X11, NCGM, or PS)
;
	function xwk(name[1]:string,outfilename[1]:string)
	local wk
	begin
		if (name .eq. "ncgm") then
			wk = create name ncgmWorkstationClass noparent
				"wkMetaName" : outfilename
			end create
		else
		  if (name .eq. "x") then
			wk = create name xWorkstationClass noparent
				"wkPause" : True
				"wkColorMap" : "default"
			end create
		  else
		    if (name .eq. "ps") then
			wk = create name psWorkstationClass noparent
				"wkPSFileName" : outfilename
			end create
		    end if
		  end if
		end if


		return(wk)
	end
;
; create a vector plot from a vector field
; create the vector field with makedata
;	
	function vector(wk[1]:graphic,vf[1]:graphic,name[1]:string) 
	local vc
	begin
		vc = create name vectorPlotClass wk
			"vcVectorFieldData" : vf
			"vcRefAnnoOn" : False
			"vcRefLengthF" : 0.017
                        "vcGlyphStyle" : "WindBarb"
                        "tfDoNDCOverlay" : True
                        "vcPositionMode" : "ArrowHead"
                        "vcWindBarbScaleFactorF" : 1.943844
                        "vcWindBarbTickAngleF" : 75.0
                        "vcFillArrowsOn" : False
                        "vcLineArrowColor" : 36
                        "vcWindBarbColor" : 36
		end create
		return(vc)
	end 	
;
; create a contour plot from a scalar field
; create the scalar field with makedata
;	
	function contour(wk[1]:graphic,sf[1]:graphic,name[1]:string)
	local cn
	begin
		cn = create name contourPlotClass wk
			"cnScalarFieldData" : sf
	                "tmXBMode" : "Manual"
	                "tmXBTickSpacingF" : 5
	                "tmXBMinorPerMajor" : 4
	                "tmXTMode" : "Manual"
	                "tmXTTickSpacingF" : 5
	                "tmXTMinorPerMajor" : 4
	                "tmYLMode" : "Manual"
	                "tmYLTickSpacingF" : 5
	                "tmYLMinorPerMajor" : 4
	                "tmYRMode" : "Manual"
	                "tmYRTickSpacingF" : 5
	                "tmYRMinorPerMajor" : 4
	                "tmXBMajorLengthF" : 0.0035
	                "tmXBMinorLengthF" : 0.0020
	                "tmXTMajorLengthF" : 0.0035
	                "tmXTMinorLengthF" : 0.0020
	                "tmYLMajorLengthF" : 0.0035
	                "tmYLMinorLengthF" : 0.0020
	                "tmYRMajorLengthF" : 0.0035
	                "tmYRMinorLengthF" : 0.0020
	                "tmXBLabelsOn" : False
	                "tmXTLabelsOn" : False
	                "tmYLLabelsOn" : False
	                "tmYRLabelsOn" : False
	                "tiMainFontColor" : 1
	                "tiMainPosition" : "Left"
	                "tiMainJust" : "BOTTOMLEFT"
                        "tiMainOffsetYF" : 0.02
	                "tiMainFont" : 21
	                "pmLabelBarDisplayMode" : "ALWAYS"
	                "pmLabelBarZone" : 1
	                "pmLabelBarSide" : "bottom"
	                "lbAutoManage" : "False"
	                "lbJustification" : "TopRight"
	                "lbOrientation" : "horizontal"
	                "lbPerimOn" : "False"
	                "lbRightMarginF" : 0.0
	                "lbLeftMarginF" : 0.0
	                "lbTopMarginF" : 0.0
	                "lbBottomMarginF" : 0.0
	                "lbLabelsOn" : "False"
	                "lbBoxLinesOn" : "False"
		end create
		return(cn)
	end
;
; create an xyplot
;
	function xyplot(wk[1]:graphic,cas[*]:graphic,name[1]:string)
	local xy
	begin
		xy = create name xyPlotClass wk
			"xyCoordData" : cas 
		end create

		return(xy)
	end
;
; when used with ncl.res creates a map from a GRIB grid number
;
	function gribmap(wk[1],name[1]:string)
	local mp
	begin
		mp = create name mapPlotClass wk end create
		return(mp)
	end 

;
; makes a plot smaller by the value of "frac"
;
	procedure smaller(plot[1]:graphic,frac[1]:numeric)
	local vpx,vpy,vpw,vph,cx,cy,rt
	begin
		getvalues plot
			"vpXF" : vpx
			"vpYF" : vpy
			"vpWidthF" : vpw
			"vpHeightF" : vph
		end getvalues
		cx = vpx + vpw/2.0
		cy = vpy - vph/2.0
		rt = 1.0 - frac/100.0
		vpw = vpw * (rt ^ .5)
		vph = vph * (rt ^ .5)
		vpx = cx - vpw/2.0
		vpy = cy + vph/2.0
		setvalues plot
			"vpXF" : vpx
                        "vpYF" : vpy
                        "vpWidthF" : vpw
                        "vpHeightF" : vph
		end setvalues
	end
;
; makes a plot bigger by the value "frac"
;
	procedure bigger(plot[1]:graphic,frac[1]:numeric)
	local vpx,vpy,vpw,vph,cx,cy,rt
	begin
		getvalues plot
			"vpXF" : vpx
			"vpYF" : vpy
			"vpWidthF" : vpw
			"vpHeightF" : vph
		end getvalues
		cx = vpx + vpw/2.0
		cy = vpy - vph/2.0
		rt = 1.0 + frac/100.0
		vpw = vpw * (rt ^ .5)
		vph = vph * (rt ^ .5)
		vpx = cx - vpw/2.0
		vpy = cy + vph/2.0
		setvalues plot
			"vpXF" : vpx
                        "vpYF" : vpy
                        "vpWidthF" : vpw
                        "vpHeightF" : vph
		end setvalues
	end

;
; moves a plot by (dx,dy)	
;
	procedure move(plot[1]:graphic,dx[1]:numeric,dy[1]:numeric)
	local vpx,vpy
	begin
		getvalues plot
			"vpXF" : vpx
			"vpYF" : vpy
		end getvalues
		setvalues plot
			"vpXF" : vpx + dx
			"vpYF" : vpy + dy
		end setvalues
	end
;
; centers a plot at (x,y)
;
	procedure centerat(plot[1]:graphic,x[1]:numeric,y[1]:numeric)
	local vpx,vpy,vpw,vph,cx,cy,dx,dy
	begin
		getvalues plot
			"vpXF" : vpx
			"vpYF" : vpy
			"vpWidthF" : vpw
			"vpHeightF" : vph
		end getvalues
		cx = vpx + vpw/2.0
		cy = vpy - vph/2.0
		dx =  x - cx
		dy =  y - cy
		setvalues plot
			"vpXF" : vpx + dx
			"vpYF" : vpy + dy
		end setvalues
	end
	
;
; moves the upper left corner to (vpx,vpy)	
;
	procedure moveto(plot[1]:graphic,vpx[1]:numeric,vpy[1]:numeric)
	begin
		getvalues plot
			"vpXF" : vpx
			"vpYF" : vpy
		end getvalues
	end

	procedure PlotColors(wks:graphic)
	local
		clen,
		labels,
		i,
		lb,
		size
	begin
		getvalues wks
		"wkColorMapLen" : clen
		end getvalues
		labels = new(clen,integer)
		do i = 0,dimsizes(labels)-1
			labels(i) = i + 1
		end do
		size = clen/3
		lb = new(3,graphic)
		do i = 0,2
			lb(i) = create "lb" + i labelBarClass wks
				"vpXF" : .05 + i * .3
				"vpWidthF" : .3
				"lbBoxCount" : size 
				"lbFillColors" : labels(i*size:i*size + size - 1)
				"lbLabelStrings" : labels(i*size:i*size + size - 1 )
				"lbLabelStride" : 1
				"lbMonoFillPattern" : 1
				"lbFillPatterns" : 0
				"lbFillPattern" : 0
			end create
		end do
		NhlDraw(lb)
	end 

	
	procedure PlotPatterns(wks:graphic)
	local clen, labels, i, lb, size
	begin
		getvalues wks
			".wkFillTableLength" : clen
		end getvalues
		labels = new(clen,integer)
		do i = 0,dimsizes(labels)-1
			labels(i) = i + 1
		end do
		size = clen/3
		lb = new(3,graphic)
		do i = 0,2
			lb(i) = create "lb" + i labelBarClass wks
				"vpXF" : .05 + i * .3
				"vpWidthF" : .3
				"lbBoxCount" : size 
				"lbFillPatterns" : labels(i*size:i*size + size - 1)
				"lbLabelStrings" : labels(i*size:i*size + size - 1 )
				"lbLabelStride" : 1
				"lbMonoFillColor" : 1
				"lbFillColors" : 1
			end create
			end do
			NhlDraw(lb)
	end 

	procedure setaspect(plot[1]:graphic)
	local xmin,xmax,ymax,ymin,asp,vph,vpw,cx,cy
	begin
		getvalues plot
			"trXMinF" : xmin
			"trXMaxF" : xmax
			"trYMaxF" : ymax
			"trYMinF" : ymin
			"vpXF" : vpx
			"vpYF" : vpy
			"vpWidthF" : vpw
			"vpHeightF" : vph
		end getvalues
		cx = vpx + vpw/2.0
		cy = vpy - vph/2.0
		asp = (xmax - xmin)/(ymax - ymin)
		print("asp " + asp)
		if(asp .gt. 1.0) then
			vph = vph/asp
		else
			vpw = vpw * asp
		end if
		
		setvalues plot
			"vpWidthF" : vpw
			"vpHeightF" : vph
		end setvalues

		centerat(plot,cx,cy)
	end 
	
	
	procedure saveps(wk[1]:graphic,name[1]:string,plots:graphic)
	local ps,cmap
	begin
		getvalues wk
			"wkColorMap" : cmap
		end getvalues
		ps = create name psWorkstationClass noparent
			"wkPSFileName" : name
			"wkColorMap" : cmap
		end create
		NhlChangeWorkstation(plots,ps)
		draw(plots)
		frame(ps)
		NhlChangeWorkstation(plots,wk)
		NhlDestroy(ps)
	end

	procedure savecgm(wk[1]:graphic,name[1]:string,plots:graphic)
	local ncgm,cmap
	begin
		getvalues wk
			"wkColorMap" : cmap
		end getvalues
		ncgm = create name ncgmWorkstationClass noparent
			"wkMetaName" : name
			"wkColorMap" : cmap
		end create
		NhlChangeWorkstation(plots,ncgm)
		draw(plots)
		frame(ncgm)
		NhlChangeWorkstation(plots,wk)
		NhlDestroy(ncgm)
	end
