function nint(x:float)
begin
       return(floor(x + .5))
end
;
procedure station_plot(drawingarea:graphic, xpos[*]:float, ypos[*]:float, temp[*]:float, dewp[*]:float, hght[*]:float, uwnd[*]:float, vwnd[*]:float)
local dims1, dims2, dims3, dims4, temp_string, dewp_string, hght_string, temp_anno, dewp_anno, hght_anno, marker, ind_xtemp, ind_temp, ind_xdewp, ind_dewp, ind_xhght, ind_hght, ind_dewp_gt_30, ind_wind, it, id, ih
begin
 
       dims1 = dimsizes(xpos)
       temp_string = new(dims1(0), string)
       dewp_string = new(dims1(0), string)
       hght_string = new(dims1(0), string)

;  Create all annotations - "+" for station markers, temp, dewp, hght string items

       temp_anno = create "temp_anno" textItemClass drawingarea
          "txFont" : 4
          "txFontHeightF" : 0.010
          "txFontColor" : 1
          "txJust" : "BOTTOMRIGHT"
       end create

       dewp_anno = create "dewp_anno" textItemClass drawingarea
          "txFont" : 4
          "txFontHeightF" : 0.010
          "txFontColor" : 1
          "txJust" : "TOPRIGHT"
       end create

       hght_anno = create "hght_anno" textItemClass drawingarea
          "txFont" : 4
          "txFontHeightF" : 0.010
          "txFontColor" : 1
          "txJust" : "BOTTOMLEFT"
       end create

       marker = create "marker" graphicStyleClass drawingarea
          "gsMarkerColor" : 1
          "gsMarkerThicknessF" : 1
          "gsMarkerIndex" : 2
          "gsMarkerSizeF" : 0.0080
       end create
       NhlNDCPolymarker(drawingarea,marker,xpos,ypos)
 
;  Fill temp, dewpoint depression, and height strings

       temp_string(:) = " :V20:"
       ind_xtemp = ind(temp.eq.temp@_FillValue)
       if (.not.all(ismissing(ind_xtemp))) then
           temp_string(ind_xtemp) = temp_string(ind_xtemp) + "X "
       end if
       ind_temp = ind(.not.(temp.eq.temp@_FillValue))
       if (.not.all(ismissing(ind_temp))) then
           temp_string(ind_temp) = temp_string(ind_temp) + nint(temp(ind_temp)) + " "
       end if

       dewp@_FillValue = 30.0
       dewp = dewp < 30
       dewp@_FillValue = 999.0
       dewp_string(:) = " :V-20:"
       ind_xdewp = ind(dewp.eq.dewp@_FillValue)
       if (.not.all(ismissing(ind_xdewp))) then
           dewp_string(ind_xdewp) = dewp_string(ind_xdewp) + "X "
       end if
       ind_dewp = ind(.not.(dewp.eq.dewp@_FillValue))
       if (.not.all(ismissing(ind_dewp))) then
           dewp_string(ind_dewp) = dewp_string(ind_dewp) + nint(dewp(ind_dewp)) + " "
       end if

       hght_string(:) = " "
       ind_xhght = ind(hght.eq.hght@_FillValue)
       if (.not.all(ismissing(ind_xhght))) then
           hght_string(ind_xhght) = hght_string(ind_xhght) + "X "
       end if
       ind_hght = ind(.not.(hght.eq.hght@_FillValue))
       if (.not.all(ismissing(ind_hght))) then
           hght_string(ind_hght) = hght_string(ind_hght) + nint(hght(ind_hght)/10.0) + " "
       end if

;  Plot temp string

       print ("          Plotting temperature strings")
       dims2 = dimsizes(ind_temp)
       do it = 0, dims2(0)-1
          setvalues temp_anno
              "txString" : temp_string(it)
              "txPosXF" : xpos(it)
              "txPosYF" : ypos(it)
          end setvalues
          draw (temp_anno)
       end do

;  Plot dewp string

       print ("          Plotting dewpoint depression strings")
       dims3 = dimsizes(ind_dewp)
       do id = 0, dims3(0)-1
          setvalues dewp_anno
              "txString" : dewp_string(id)
              "txPosXF" : xpos(id)
              "txPosYF" : ypos(id)
          end setvalues
          draw (dewp_anno)
       end do

;  Plot hght string

       print ("          Plotting height strings")
       dims4 = dimsizes(ind_hght)
       do ih = 0, dims4(0)-1
          setvalues hght_anno
              "txString" : hght_string(ih)
              "txPosXF" : xpos(ih)
              "txPosYF" : ypos(ih)
          end setvalues
          draw (hght_anno)
       end do

;  Plot wind barbs
       print ("          Plotting wind barbs")
       ind_wind = ind(.not.(uwnd.eq.uwnd@_FillValue))
       if (.not.all(ismissing(ind_wind))) then
           windbarb(drawingarea,xpos(ind_wind),ypos(ind_wind),uwnd(ind_wind),vwnd(ind_wind),0.029,"north")
       end if
 
end
