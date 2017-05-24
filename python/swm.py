#!/mesonet/python-2.3/bin/python
# My first go around sucked, lets try again!
# Daryl Herzmann 25 Oct 2004

nx = 361
ny = 64
delt = 120.0
asseln = 0.00
tsteps = 1000
lat0 = 20.0
xbctype = 'PERIODIC'
ybctype = 'RADIATIVE'
HH = 1000.0

import Numeric, math, libs

def main():
  uvect = Numeric.zeros( (nx, ny), 'i4')
  for j in range(ny):
    uvect[:,j] = Numeric.arange(nx)
  h0 = Numeric.zeros( (nx, ny), 'f8')
  h1 = h0.copy()
  h2 = h0.copy()
  u0 = h0.copy()
  u1 = h0.copy()
  u2 = h0.copy()
  v0 = h0.copy()
  v1 = h0.copy()
  v2 = h0.copy()
  dhdt = h0.copy()
  dudt = h0.copy()
  dvdt = h0.copy()

  dx = 360. * 110000.0 / (nx -1)
  dy = dx
  G = 9.8
  tstep = 0

  XGW = math.sqrt(G * HH)
  CG = 1. * XGW
  DHDTLS = 0.
  DUDTLS = 0.
  DVDTLS = 0.

  ICENTX = nx / 2
  ICENTY = ny / 2
  IWID = 8
  AMP = 30.0
  GRAD = 300.0

  RLO = 0.15
  XLO = 0.01
  D2R = 2. * math.pi / 360. 
  OMEGA = 2. * math.pi / 86164.09

  ar = Numeric.arange(ny)
  lats = lat0 + dy * ar / 111000
  f = 2 * OMEGA * Numeric.sin( ar * D2R )

  for j in range(ny):
    HLOGI = 1. / (1. + (1./XLO - 1.)* math.exp(-RLO* (j-1)))
    h0[:,j] = HH + GRAD * (1. - 2. * HLOGI)
    if (j > 2):
      FAVG = f[j]
      for i in range(1, nx-1):
        DELH = h0[i+1,j] - h0[i-1,j]
        DHDY = DELH / (2. * dy)
        u0[i,j] = -(G/FAVG) * DHDY
  """
        IF (IY .EQ. NY) THEN
           U0(IX,NY) = U0(IX,NY-1)
           U0(IX,1) = U0(IX,2)
           PRINT *, 'INIT U ', IY, U0(IX,IY)
        END IF
  """

  for j in range(ny):
    for i in range(nx):
      G1 = (i - ICENTX)**2 + (j - ICENTY)**2
      G2 = IWID ** 2
      h0[i,j] = h0[i,j] - AMP * math.exp(-G1/G2)


  for j in range(1,ny-1):
    for i in range(1,nx-1):
      FAVG = f[j]
      DHDX = (h0[i+1,j] - h0[i-1,j]) / (2. * dx)
      DHDY = (h0[i,j+1] - h0[i,j-1]) / (2. * dy)
      u0[i,j] = -(G/FAVG) * DHDY
      v0[i,j] =  (G/FAVG) * DHDX
    # East and West boundaries
    u0[0,j] = u0[1,j]
    v0[0,j] = v0[1,j]
    u0[nx-1,j] = u0[nx-2,j]
    v0[nx-1,j] = v0[nx-2,j]

  for i in range(nx):
    u0[i,0] = u0[i,1]
    v0[i,0] = v0[i,1]
    u0[i,ny-1] = u0[i,ny-1]
    v0[i,ny-1] = v0[i,ny-1]

  h1 = h0.copy()
  u1 = u0.copy()
  v1 = v0.copy()

      
  if (xbctype == 'PERIODIC'):
    h0 = libs.perbcx(h0, nx, ny)
    u0 = libs.perbcx(u0, nx, ny)
    v0 = libs.perbcx(v0, nx, ny)
    h1 = libs.perbcx(h1, nx, ny)
    u1 = libs.perbcx(u1, nx, ny)
    v1 = libs.perbcx(v1, nx, ny)

  if (ybctype == 'PERIODIC'):
    h0 = libs.perbcy(h0, nx, ny)
    u0 = libs.perbcy(u0, nx, ny)
    v0 = libs.perbcy(v0, nx, ny)
    h1 = libs.perbcy(h1, nx, ny)
    u1 = libs.perbcy(u1, nx, ny)
    v1 = libs.perbcy(v1, nx, ny)


  dhdt = libs.advcx(h0, u0, dhdt, dx, nx, ny)
  dudt = libs.advcx(u0, u0, dudt, dx, nx, ny)
  dvdt = libs.advcx(v0, u0, dvdt, dx, nx, ny)

  dhdt = libs.advcy(h0, v0, dhdt, dy, nx, ny)
  dudt = libs.advcy(u0, v0, dudt, dy, nx, ny)
  dvdt = libs.advcy(v0, v0, dvdt, dy, nx, ny)

  dudt = libs.pgfu(h0, G, dudt, dx, nx, ny)
  dvdt = libs.pgfv(h0, G, dvdt, dy, nx, ny)

  dhdt = libs.divg(h0, u0, v0, dhdt, dx, dy, HH, nx, ny)

  halfdt = delt / 2.  

  if (xbctype == 'RADIATIVE'):
    dhdt = libs.radbcx(h0, u0, dhdt, CG, dx, nx, ny)
    dudt = libs.radbcx(u0, u0, dudt, CG, dx, nx, ny)
    dvdt = libs.radbcx(v0, u0, dvdt, CG, dx, nx, ny)
  elif (xbctype == 'SPONGE'):
    dhdt = libs.spongebcx(dhdt, dhdtls, nx, ny)
    dudt = libs.spongebcx(dudt, dudtls, nx, ny)
    dvdt = libs.spongebcx(dvdt, dvdtls, nx, ny)

  h0, h1, h2 = libs.update(h0, h1, h2, dhdt, halfdt, asseln, nx, ny)
  u0, u1, u2 = libs.update(u0, u1, u2, dudt, halfdt, asseln, nx, ny)
  v0, v1, v2 = libs.update(v0, v1, v2, dvdt, halfdt, asseln, nx, ny)


  if (xbctype == 'PERIODIC'):
    h1 = libs.perbcx(h1, nx, ny)
    u1 = libs.perbcx(u1, nx, ny)


  for tstep in range(tsteps):
    print tstep

    dhdt = Numeric.zeros( (nx,ny), 'f8')
    dudt = Numeric.zeros( (nx,ny), 'f8')
    dvdt = Numeric.zeros( (nx,ny), 'f8')

    dhdt = libs.advcx(h1, u1, dhdt, dx, nx, ny)
    dudt = libs.advcx(u1, u1, dudt, dx, nx, ny)
    dvdt = libs.advcx(v1, u1, dvdt, dx, nx, ny)

    dhdt = libs.advcy(h1, v1, dhdt, dy, nx, ny)
    dudt = libs.advcy(u1, v1, dudt, dy, nx, ny)
    dvdt = libs.advcy(v1, v1, dvdt, dy, nx, ny)

    dudt = libs.pgfu(h1, G, dudt, dx, nx, ny)
    dvdt = libs.pgfv(h1, G, dvdt, dy, nx, ny)

    dudt = libs.coru(v1, dudt, f, nx, ny)
    dvdt = libs.corv(u1, dvdt, f, nx, ny)


    dhdt = libs.divg(h1, u1, v1, dhdt, dx, dy, HH, nx, ny)

    dhdt = libs.diffusx(h0, dhdt, dx, delt, nx, ny)
    dudt = libs.diffusx(u0, dudt, dx, delt, nx, ny)
    dvdt = libs.diffusx(v0, dvdt, dx, delt, nx, ny)

    dhdt = libs.diffusy(h0, dhdt, dy, delt, nx, ny)
    dudt = libs.diffusy(u0, dudt, dy, delt, nx, ny)
    dvdt = libs.diffusy(v0, dvdt, dy, delt, nx, ny)


    if (xbctype == 'RADIATIVE'):
      dhdt = libs.radbcx(h0, u0, dhdt, CG, dx, nx, ny)
      dudt = libs.radbcx(u0, u0, dudt, CG, dx, nx, ny)
    elif (xbctype == 'SPONGE'):
      dhdt = libs.spongebcx(dhdt, dhdtls, nx, ny)
      dudt = libs.spongebcx(dudt, dudtls, nx, ny)
      dvdt = libs.spongebcx(dvdt, dvdtls, nx, ny)

    h0, h1, h2 = libs.update(h0, h1, h2, dhdt, halfdt, asseln, nx, ny)
    u0, u1, u2 = libs.update(u0, u1, u2, dudt, halfdt, asseln, nx, ny)
    v0, v1, v2 = libs.update(v0, v1, v2, dvdt, halfdt, asseln, nx, ny)

    if (xbctype == 'PERIODIC'):
      h1 = libs.perbcx(h1, nx, ny)
      u1 = libs.perbcx(u1, nx, ny)
      v1 = libs.perbcx(v1, nx, ny)

main()
