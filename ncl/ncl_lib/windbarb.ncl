;
; Windbarb Drawing routine
;     rough guideline for setting "scale" on mapped plots
;     scale=min(abs(lat2-lat1),abs(lon2-lon1))*(0.003/8.0)
;
procedure windbarb(drawingarea:graphic, xscreen[*]:float, yscreen[*]:float, u[*]:float, v[*]:float, scale[1]:float, hemi:string)
local x,y,x1,y1,x2,y2,x3,y3,r,wspd,wdir,angle,zx,zy,nz_spd,nz_dir,nz_x,nz_y,z_ind,nz_ind, hfact, flinc,stinc,hsinc,round,iflags,istafs,ihfstafs,iloop,PI,PI180,PI180I,dims1,ii
begin
       ; Set up constants and initialize stuff
       PI      = 3.1415928
       PI180   = PI/180.0
       PI180I   = 180.0/PI
       flinc = 50.0
       stinc = 10.0
       hsinc = 5.0
       round = hsinc*0.5
       iloop = new(1,integer)
       ii = new(1,integer)
       iflags = new(1,integer)
       istafs = new(1,integer)
       ihfstafs = new(1,integer)
       if (hemi .eq. "north" .or. hemi.eq."NORTH") then
          hfact = -1.0
       else
          if (hemi .eq. "south" .or. hemi.eq."SOUTH") then
             hfact = 1.0
          end if
       end if

       marker = create "marker" graphicStyleClass drawingarea
          "gsMarkerColor" : 1
          "gsMarkerThicknessF" : 1
          "gsMarkerIndex" : 4
          "gsMarkerSizeF" : 0.0055
       end create
       solidline = create "solidline" graphicStyleClass drawingarea
          "gsLineThicknessF" : 1
          "gsLineColor" : 1
       end create

       wspd   = sqrt(u^2 + v^2)*1.94
       wdir   = atan2(-u,-v)*PI180I
       angle  = (360.0-floattoint(wdir-90.0)%360)*PI180

       z_ind = ind(wspd.lt.round)
       if (.not.all(ismissing(z_ind))) then
          zx = xscreen(z_ind)
          zy = yscreen(z_ind)
          ; If calm winds plot circle
          NhlNDCPolymarker(drawingarea,marker,zx,zy)
       end if

       nz_ind = ind(wspd.ge.round)
       if (all(ismissing(nz_ind))) then
          return
       end if
       dims1 = dimsizes(nz_ind)
       nz_x = xscreen(nz_ind)
       nz_y = yscreen(nz_ind)
       nz_spd = wspd(nz_ind)
       nz_dir = angle(nz_ind)

       x = new(4, float)
       y = new(4, float)

       do ii = 0,dims1(0)-1

          ; Determine number of flags, staffs, and half-staffs
          iflags   = floattoint( (nz_spd(ii)+round)/flinc )
          istafs   = floattoint( (nz_spd(ii)+round - flinc*iflags)/stinc )
          ihfstafs = floattoint( ( (nz_spd(ii)+round) - (flinc*iflags) - (stinc*istafs) )/hsinc )

          r        = 1.0
          ; Draw the barb (2 points to describe)
          x(0) = nz_x(ii)
          y(0) = nz_y(ii)
          x(1) = nz_x(ii) + (cos(nz_dir(ii))*r)*scale
          y(1) = nz_y(ii) + (sin(nz_dir(ii))*r)*scale
          NhlNDCPolyline(drawingarea,solidline,x(0:1),y(0:1))

          ; Draw each flag individually (filled polygon flag)
          do iloop = 1,iflags
             x1 = r
             y1 = 0.0
             x2 = r+0.05
             y2 = 0.5*hfact
             r  = r-0.15
             x3 = r
             y3 = 0.0
             x(0) = (cos(nz_dir(ii))*x1 - sin(nz_dir(ii))*y1)*scale + nz_x(ii)
             y(0) = (sin(nz_dir(ii))*x1 + cos(nz_dir(ii))*y1)*scale + nz_y(ii)
             x(1) = (cos(nz_dir(ii))*x2 - sin(nz_dir(ii))*y2)*scale + nz_x(ii)
             y(1) = (sin(nz_dir(ii))*x2 + cos(nz_dir(ii))*y2)*scale + nz_y(ii)
             x(2) = (cos(nz_dir(ii))*x3 - sin(nz_dir(ii))*y3)*scale + nz_x(ii)
             y(2) = (sin(nz_dir(ii))*x3 + cos(nz_dir(ii))*y3)*scale + nz_y(ii)
             x(3) = x(0)
             y(3) = y(0)
             NhlNDCPolygon(drawingarea,solidline,x(0:3),y(0:3))
             r  = r-0.15
          end do

          ; Draw each full staff individually
          do iloop = 1,istafs
             x1 = r
             y1 = 0.0
             x2 = r+0.15
             y2 = 0.5*hfact
             x(0) = (cos(nz_dir(ii))*x1 - sin(nz_dir(ii))*y1)*scale + nz_x(ii)
             y(0) = (sin(nz_dir(ii))*x1 + cos(nz_dir(ii))*y1)*scale + nz_y(ii)
             x(1) = (cos(nz_dir(ii))*x2 - sin(nz_dir(ii))*y2)*scale + nz_x(ii)
             y(1) = (sin(nz_dir(ii))*x2 + cos(nz_dir(ii))*y2)*scale + nz_y(ii)
             NhlNDCPolyline(drawingarea,solidline,x(0:1),y(0:1))
             r  = r-0.15
          end do

          ; Draw each half staff individually
          do iloop = 1,ihfstafs
             x1 = r
             y1 = 0.0
             x2 = r+0.075
             y2 = 0.25*hfact
             x(0) = (cos(nz_dir(ii))*x1 - sin(nz_dir(ii))*y1)*scale + nz_x(ii)
             y(0) = (sin(nz_dir(ii))*x1 + cos(nz_dir(ii))*y1)*scale + nz_y(ii)
             x(1) = (cos(nz_dir(ii))*x2 - sin(nz_dir(ii))*y2)*scale + nz_x(ii)
             y(1) = (sin(nz_dir(ii))*x2 + cos(nz_dir(ii))*y2)*scale + nz_y(ii)
             NhlNDCPolyline(drawingarea,solidline,x(0:1),y(0:1))
             r  = r-0.15
          end do

       end do
end
