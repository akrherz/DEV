;
; Main program found at bottom
;
;---------------------------------------------------------------------------------
; Function to get x gridpoint given earth lat/lon (assuming Polar Stereo projection)
;
function xgrid(earth_lat[*]:float, earth_lon[*]:float, xpole[1]:float, ypole[1]:float, latitude_true[1]:float)
local c1, PI180, YLONX, RADIUS, blat, blon
begin
      c1    = 1.0
      PI180 = asin(c1)/90.0
      YLONX = -15.0
      RADIUS = 6371230.0

      return (xpole+((1.+sin(latitude_true*PI180))/(1.+sin(earth_lat*PI180)))*RADIUS*cos(earth_lat*PI180)*cos(earth_lon*PI180-YLONX*PI180))
end
;---------------------------------------------------------------------------------
; Function to get y gridpoint given earth lat/lon (assuming Polar Stereo projection)
;
function ygrid(earth_lat[*]:float, earth_lon[*]:float, xpole[1]:float, ypole[1]:float, latitude_true[1]:float)
local c1, PI180, YLONX, RADIUS, blat, blon
begin
      c1    = 1.0
      PI180 = asin(c1)/90.0
      YLONX = -15.0
      RADIUS = 6371230.0

      return (ypole+((1.+sin(latitude_true*PI180))/(1.+sin(earth_lat*PI180)))*RADIUS*cos(earth_lat*PI180)*sin(earth_lon*PI180-YLONX*PI180))
end
;
;---------------------------------------------------------------------------------
; Given earth-oriented wind components, compute grid oriented components with a
; lambert conformal grid.  On input wind components are earth oriented, but on
; output they become grid-relative.
;
procedure rotate_lc(earth_u[*]:float, earth_v[*]:float, lat[*]:float, lon[*]:float, grid_u[*]:float, grid_v[*]:float, lat_tan_p[1]:float, lon_xx_p[1]:float, model[1]:string)
local dims1, raddeg, rotcon_p, deltal, sindl, cosdl
begin
      raddeg = 3.14159/180.0
      rotcon_p = 1.0 * sin(lat_tan_p*raddeg)    ; Change to -1.0 for southern Hemi
      dims1  = dimsizes(lat)
      deltal = new(dims1(0),float)
      sindl  = new(dims1(0),float)
      cosdl  = new(dims1(0),float)
      grid_u = new(dims1(0),float)
      grid_v = new(dims1(0),float)

      deltal = rotcon_p*(lon_xx_p-lon)*raddeg
      sindl = sin(deltal)
      cosdl = cos(deltal)
      grid_u = earth_u*cosdl + earth_v*sindl
      grid_v = earth_v*cosdl - earth_u*sindl

end
;
;---------------------------------------------------------------------------------
; Given earth-oriented wind components, compute grid oriented components with a
; polar stereographic grid.  On input wind components are earth oriented, but on
; output they become grid-relative.  ; Adapted from W3FC08 from NCEP Libraries.
;
procedure rotate_ps(earth_u[*]:float, earth_v[*]:float, lat[*]:float, lon[*]:float, grid_u[*]:float, grid_v[*]:float, model[1]:string)
local dims1, spacing, lat_true, pole_i, pole_j, xpole, ypole, dfp
begin
      dims1  = dimsizes(lat)
      dfp    = new(dims1(0),float)
      ffid   = new(dims1(0),float)
      ffjd   = new(dims1(0),float)
      grid_u = new(dims1(0),float)
      grid_v = new(dims1(0),float)

      if (model.eq."RUC") then
          spacing   = 60000.0
          lat_true  = 40.0
          pole_i    = 31.91069
          pole_j    = 112.5311
          xpole     = (pole_i - 1.0)*spacing
          ypole     = (pole_j - 1.0)*spacing
      else
          print ("Cannot handle this grid")
      end if

      ffid = xgrid(lat, lon, xpole, ypole, lat_true)/spacing + 1.
      ffjd = ygrid(lat, lon, xpole, ypole, lat_true)/spacing + 1.
      ffid = pole_i - ffid
      ffjd = pole_j - ffjd

      dfp    = sqrt(ffid*ffid + ffjd*ffjd)
      grid_u = (earth_u*ffjd + earth_v*ffid)/dfp
      grid_v = (earth_v*ffjd - earth_u*ffid)/dfp
;      print ( (/grid_u,grid_v/) )
end
;
;--------------------------------------------------------------------
;
; Main program to change earth-oriented wind components to grid-oriented components
; needed before plotting windbarbs.
;
;begin
;   ind_good = 0         ; this works as expected, replacing orig with new
;   ind_good = (/0,1/)   ; does not replace orig values with newly computed ones
;   earth_lat =  (/39.7500000, 37.9333333/)
;   earth_lon =  (/-104.86667, -75.466667/)
;   u   =  (/8.7, 25.8/)
;   v   =  (/7.3, -6.9/)
;   print ("Earth wind components")
;   print ( (/u(ind_good), v(ind_good)/) )
;   earthwind_to_gridwind(u(ind_good), v(ind_good), earth_lat(ind_good), earth_lon(ind_good), "RUC")
;;   print ("Grid wind components")
;   print ( (/u(ind_good), v(ind_good)/) )
;end
