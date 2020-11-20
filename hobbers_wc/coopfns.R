# Summary functions for Co-op data

library(plyr)
library(reshape2)
library(RPostgreSQL)
library(rgeos)

h6spatial = function(dfrm,dbcon) {
    # Get HUC6 polygons and return as a list of spatial polygons
    qr1 = paste("SELECT huc6_id, poly_id, vert_ord, easting, northing ",
                "FROM huc6_poly WHERE huc6_id = '",dfrm$huc6_id,"' ",
                "ORDER BY poly_id, vert_ord",sep="")
    dply = dbGetQuery(dbcon,qr1)
    p2a = as.matrix(dply[,c("easting","northing")])
    plya = Polygon(p2a,hole=FALSE)
    plysa = Polygons(list(plya),"p1")
    dmpca = SpatialPolygons(list(plysa),pO=as.integer(1),
              proj4string=CRS("+proj=utm +lon_0=93w +zone=15 +ellps=GRS80"))
    return(dmpca)
}

h6poly = function(dfrm,dbcon) { 
    # Get HUC6 polygons and return as a list of Polygon
    qr1 = paste("SELECT huc6_id, poly_id, vert_ord, longitude, latitude ",
                "FROM huc6_poly WHERE huc6_id = '",dfrm$huc6_id,"' ",
                "ORDER BY poly_id, vert_ord",sep="")
    dply = dbGetQuery(dbcon,qr1)
    p2a = as.matrix(dply[,c("longitude","latitude")])
    plya = Polygon(p2a,hole=FALSE)
    plysa = Polygons(list(plya),as.character(dfrm$huc6_id))
    return(plysa)
}


monthprcp = function(dfrm,dbcon) {
   # Get Precip for a specific month
   qrst = paste("SELECT coop_id, obs_date, obs_precip, ",
                "date_part('year',obs_date) AS year",
                " FROM coop_data WHERE coop_id = '",
                dfrm$coop_id,"' AND (date_part('month',obs_date) = ",
                dfrm$month,") ORDER BY obs_date",sep="")
   dout = dbGetQuery(dbcon,qrst)
}

monthtprcp = function(dfrm,dbcon) {
    # Get total precip for a specific month
    qrst = paste("SELECT coop_id, SUM(obs_precip) AS tot_precip, ",
                 "date_part('year',obs_date) AS year",
                 " FROM coop_data WHERE coop_id = '",
                dfrm$coop_id,"' AND (date_part('month',obs_date) = ",
                dfrm$month,") GROUP BY year, coop_id ORDER BY year",sep="")
   dout = dbGetQuery(dbcon,qrst)
   if (nrow(dout) > 0) {
       dout$month = dfrm$month[1]
   }
   return(dout)
}

monthmax = function(dfrm,dbcon) {
    # Get max temp for a specific month
    qtst = paste("SELECT coop_id, obs_date, obs_high, ",
                 "date_part('year',obs_date) AS year",
                 " FROM coop_data WHERE coop_id = '",
                 dfrm$coop_id,"' AND (date_part('month',obs_date) = ",
                 dfrm$month,") ORDER BY obs_date",sep="")
    dout = dbGetQuery(dbcon,qtst)
}

monthmaxavg = function(dfrm,dbcon) {
    # Get average max temp for a specific month
    qtst = paste("SELECT coop_id, AVG(obs_high) AS avg_high, ",
                 "date_part('year',obs_date) AS year",
                 " FROM coop_data WHERE coop_id = '",
                dfrm$coop_id,"' AND (date_part('month',obs_date) = ",
                dfrm$month,") GROUP BY year, coop_id ORDER BY year",sep="")
    dout = dbGetQuery(dbcon,qtst)
    if (nrow(dout) > 0) {
        dout$month = dfrm$month[1]
    }
    return(dout)
}

monthtmin = function(dfrm,dbcon) {
   # Get temperature for a specific month
   qrst = paste("SELECT coop_id, obs_date, obs_low, ",
                "date_part('year',obs_date) AS year",
                " FROM coop_data WHERE coop_id = '",
                dfrm$coop_id,"' AND (date_part('month',obs_date) = ",
                dfrm$month,") ORDER BY obs_date",sep="")
   dout = dbGetQuery(dbcon,qrst)
}

yrprcp = function(dfrm,dbcon) {
   # Get Apr-Sep total precip
   qrst = paste("SELECT coop_id, date_part('year',obs_date) AS year, ",
                "COUNT (obs_date) AS totobs, ",
                "SUM(obs_precip) as totprcp FROM coop_data WHERE coop_id = '",
                dfrm$coop_id,"' AND (date_part('month',obs_date) > 3) AND ",
                "(date_part('month',obs_date) < 10) GROUP BY year, coop_id ",
                "ORDER BY year",sep="");
   dout = dbGetQuery(dbcon,qrst)
}

yrstdd = function(dfrm,dbcon) {
    # Heat stress degree days
    t1 = paste("SUM(CASE WHEN (obs_high <= 86) THEN 0 ",
              "ELSE (obs_high - 86) END) as sdd_accum ",
              sep="")
    qrst = paste("SELECT coop_id, date_part('year',obs_date) AS year, ",
                 "COUNT (obs_date) AS totobs, ",
                 t1," FROM coop_data WHERE coop_id = '",
                 dfrm$coop_id,"'", 
                 "GROUP BY year, coop_id ",
                 "ORDER BY year",sep="")
    dout = dbGetQuery(dbcon,qrst)
}

yrgdd = function(dfrm,dbcon) {
   # Get April-Sept GDDs
   t1 = paste("SUM(CASE WHEN (floor((obs_high + obs_low)/2) < 50) THEN 0 ",
              "WHEN (floor((obs_high + obs_low)/2) > 86) THEN 36 ",
              "ELSE (floor((obs_high + obs_low)/2) - 50) END) as gdd_accum ",
              sep="")
   qrst = paste("SELECT coop_id, date_part('year',obs_date) AS year, ",
                "COUNT (obs_date) AS totobs, ",
                t1," FROM coop_data WHERE coop_id = '",
                dfrm$coop_id,"' AND (date_part('month',obs_date) > 3) AND ",
                "(date_part('month',obs_date) < 10) GROUP BY year, coop_id ",
                "ORDER BY year",sep="")
   dout = dbGetQuery(dbcon,qrst)
}

qsmryext = function(dfrm,vrout) {
    # Quick summary of data set
    q50 = median(dfrm[,vrout])
    q75 = quantile(dfrm[,vrout],0.75)
    q90 = quantile(dfrm[,vrout],0.9)
    q95 = quantile(dfrm[,vrout],0.95)
    q99 = quantile(dfrm[,vrout],0.99)
    qmn = mean(dfrm[,vrout])
    qsd = sd(dfrm[,vrout])
    nobs = length(dfrm[,vrout])
    d2 = data.frame(mean=qmn,sd=qsd,median=q50,q75=q75,q90=q90,q95=q95,q99=q99,nobs=nobs)
    return(d2)
}

mnthsmry = function(dfrm,dbcon,flagfrm,smrvr) {
    d1 = monthprcp(dfrm,dbcon)
    # Check for valid data here - flag bad years
    fsb = flagfrm[flagfrm$coop_id == dfrm$coop_id[1],]
    if (nrow(fsb) > 0) {
        for (i in seq(1,nrow(fsb))) {
            d1 = d1[d1$year != fsb$year[i],]
        }
    }
    dsum = qsmryext(d1,vrout=smrvr)
    return(dsum)
}

mnthchk = function(dfrm) {
    # Quality check
    spotobs = (dfrm$obs_precip * 100) %% 100
    lspt = length(spotobs[spotobs == 0])
    tspt = length(spotobs)
    d2 = data.frame(flag=lspt,totobs=tspt,frq=lspt/tspt,totprcp=sum(dfrm$obs_precip))
    return(d2)
}

# Also make a function to find events in a year
mnthextct = function(dfrm,dbcon,vrext="q95",flagfrm,vrsmry,extfn) {
    d1 = extfn(dfrm,dbcon)
    # Check for valid data here - flag bad years
    fsb = flagfrm[flagfrm$coop_id == dfrm$coop_id[1],]
    if (nrow(fsb) > 0) {
        for (i in seq(1,nrow(fsb))) {
            d1 = d1[d1$year != fsb$year[i],]
        }
    }
    if (nrow(d1) > 0) {
        dsum = qsmryext(d1,vrout=vrsmry)
        dsb = d1[d1$year >= dfrm$year & !is.na(d1[,vrsmry]),]
        dfrm$events = length(dsb[dsb[,vrsmry] >= dsum[1,vrext],vrsmry])
        dfrm$totday = dsum$nobs
        dfrm$qday = nrow(dsb)
    }
    else {
        dfrm = NULL
    }
    return(dfrm)
}

yrcdf = function(dfrm,dbcon,flagfrm,vrsmry,yrfn) {
    # Evaluate empirical CDF of a seasonal variable
    d1 = yrfn(dfrm,dbcon)
    # Check for valid data here - 
    fsb = flagfrm[flagfrm$coop_id == dfrm$coop_id[1],]
    if (nrow(fsb) > 0) {
        for (i in seq(1,nrow(fsb))) {
            d1 = d1[d1$year != fsb$year[i],]
        }
    }
    if (nrow(d1) > 0) {
        d1 = d1[order(d1[,vrsmry]),]
        d1$rank = seq(1,nrow(d1))
        d1$ecdf = d1$rank / nrow(d1)
    }
    else {
        d1 = NULL
    }
    return(d1)
}

annsmry = function(dfrm,dbcon,flagfrm,vrsmry,yrfn) {
    # Give a summary of the annual values of a variable
    d1 = yrfn(dfrm,dbcon)
    # Check for valid data here - 
    fsb = flagfrm[flagfrm$coop_id == dfrm$coop_id[1],]
    if (nrow(fsb) > 0) {
        for (i in seq(1,nrow(fsb))) {
            d1 = d1[d1$year != fsb$year[i],]
        }
    }
    if (nrow(d1) > 0) {
        dout = qsmryext(d1,vrsmry)
    }
    else {
        dout = NULL
    }
    return(dout)
}



sumevnt = function(dfrm) {
    dout = data.frame(coop_id = dfrm$coop_id[1],
#                      easting = dfrm$easting[1],
#                      northing = dfrm$northing[1],
                      month = dfrm$month[1],
                      year = dfrm$year[1],
                      totevt = sum(dfrm$events),
                      totday = sum(dfrm$totday),
                      qday = sum(dfrm$qday))
    return(dout)
}

aridity = function(dfrm,dbcon,flagfrm) {
    # Compute aridity index for a station, and year
    dp = monthtprcp(dfrm,dbcon)
    dt = monthmaxavg(dfrm,dbcon)
    # Check for valid data here - flag bad years
    fsb = flagfrm[flagfrm$coop_id == dfrm$coop_id[1],]
    if (nrow(fsb) > 0) {
        for (i in seq(1,nrow(fsb))) {
            dp = dp[dp$year != fsb$year[i],]
            dt = dt[dt$year != fsb$year[i],]
        }
    }
    if ( (nrow(dp) > 0) && (nrow(dt) > 0)) {
        dpsm = qsmryext(dp,vrout="tot_precip")
        dp$prcp_anom = (dp$tot_precip - dpsm$mean[1]) / dpsm$sd[1]
        dtsm = qsmryext(dt,vrout="avg_high")
        dt$temp_anom = (dt$avg_high - dtsm$mean[1]) / dtsm$sd[1]
        dfnl = merge(dp,dt)
        dfnl$aridity = dfnl$temp_anom - dfnl$prcp_anom
    }
    else {
        dfnl = NULL
    }
    return(dfnl)
}

avgevnt = function(dfrm) {
    dout = data.frame(coop_id = dfrm$coop_id[1],
#                      easting = dfrm$easting[1],
#                      northing = dfrm$northing[1],
                      year = dfrm$year[1],
                      avgidx = mean(dfrm$aridity))
    return(dout)
}

chkply = function(plyfrm,ptfrm) {
    ptout = point.in.polygon(ptfrm$easting,ptfrm$northing,
                             pol.x=plyfrm$easting,pol.y=plyfrm$northing)
    if (length(ptout[ptout ==1]) > 0) {
        frout = ptfrm[ptout ==1,]
        frout$drought_id = plyfrm$drought_id[1]
        return(frout)
    }
    else {
        return(NULL)
    }
}

qsrt = function(dfrm,srtvr) {
    # Return one row with the highest level
    dsrt = dfrm[order(dfrm[,srtvr]),]
    dout = dsrt[nrow(dsrt),]
    return(dout)
}

qsum = function(dfrm,srtvr) {
    dtout = data.frame(coop_id=dfrm$coop_id[1],
#                       easting=dfrm$easting[1],
#                       northing=dfrm$northing[1],
                       totct=sum(dfrm[,srtvr]))
    return(dtout)
}

drtinpoly = function(dfrm,dtstr,dbcon) {
    qdm = paste("SELECT drought_id, obs_date, poly_id, vert_ord, ",
               "easting, northing FROM ",
               "drought_poly WHERE obs_date = '",dtstr,"' ORDER BY ",
               "drought_id, poly_id, vert_ord",sep="")
    ddm = dbGetQuery(con,qdm)
    ddm$cat_poly = factor(paste(ddm$drought_id,"_",ddm$poly_id,sep=""))
    plydrt = ddply(ddm,c("cat_poly"),.fun=chkply,ptfrm=dfrm)
    plystn = ddply(plydrt,c("coop_id"),.fun=qsrt,srtvr="drought_id")
    plystn$obs_date = rep(dtstr,nrow(plystn))
    return(plystn)
}

