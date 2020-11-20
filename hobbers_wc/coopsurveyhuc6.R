# Various summaries from the Co-op data 
source("coopfns.R")
library(RPostgreSQL)
library(plyr)
library(ggplot2)
library(rgeos)
library(rgdal)

load("FlagPrecip.RData")

drv = dbDriver("PostgreSQL")
con = dbConnect(drv,dbname="cscap")

qstr = paste("SELECT coop_id, huc6_id, longitude, latitude, ",
             "easting, northing FROM coop_station ",
             "WHERE huc6_id IS NOT NULL ORDER BY coop_id",sep="")
dstn = dbGetQuery(con,qstr)


# ------------------------------------------------------------------------#
# Aridity

dapr = dstn
dapr$month = 4
daprard = ddply(dapr,c("coop_id"),.fun=aridity,.progress="text",
                dbcon=con,flagfrm=dflg)
daprard = merge(daprard,dstn)

dmay = dstn
dmay$month = 5
dmayard = ddply(dmay,c("coop_id"),.fun=aridity,.progress="text",
                dbcon=con,flagfrm=dflg)
dmayard = merge(dmayard,dstn)

djun = dstn
djun$month = 6
djunard = ddply(djun,c("coop_id"),.fun=aridity,.progress="text",
                dbcon=con,flagfrm=dflg)
djunard = merge(djunard,dstn)

djul = dstn
djul$month = 7
djulard = ddply(djul,c("coop_id"),.fun=aridity,.progress="text",
                dbcon=con,flagfrm=dflg)
djulard = merge(djulard,dstn)

daug = dstn
daug$month = 8
daugard = ddply(daug,c("coop_id"),.fun=aridity,.progress="text",
                dbcon=con,flagfrm=dflg)
daugard = merge(daugard,dstn)

dsep = dstn
dsep$month = 9
dsepard = ddply(dsep,c("coop_id"),.fun=aridity,.progress="text",
                dbcon=con,flagfrm=dflg)
dsepard = merge(dsepard,dstn)

dcmb = rbind(daprard,dmayard,djunard,djulard,daugard,dsepard)
davgard = ddply(dcmb,c("coop_id","year"),.fun=avgevnt,.progress="text")

d11 = davgard[davgard$year == 2015,]
d07 = davgard[davgard$year >= 2012,]
d07cst = ddply(d07,c("coop_id"),.fun=qsmryext,vrout="avgidx")

names(d11) = c("coop_id","year","Aridity11")
d11 = d11[,c("coop_id","Aridity11")]
d07cst = d07cst[,c("coop_id","mean")]
names(d07cst) = c("coop_id","Aridity07_11")

aridcoop = merge(d11,d07cst)

# ------------------------------------------------------------------------#
# Daily Precip 99th percentile
dapr = dstn
dapr$month = 4
dapr$year = 2012
dapr07 = ddply(dapr,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
dapr07 = merge(dapr07,dstn)

dmay = dstn
dmay$month = 5
dmay$year = 2012
dmay07 = ddply(dmay,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
dmay07 = merge(dmay07,dstn)

djun = dstn
djun$month = 6
djun$year = 2012
djun07 = ddply(djun,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
djun07 = merge(djun07,dstn)

djul = dstn
djul$month = 7
djul$year = 2012
djul07 = ddply(djul,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
djul07 = merge(djul07,dstn)

daug = dstn
daug$month = 8
daug$year = 2012
daug07 = ddply(daug,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
daug07 = merge(daug07,dstn)

dsep = dstn
dsep$month = 9
dsep$year = 2012
dsep07 = ddply(dsep,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
dsep07 = merge(dsep07,dstn)

dcmb = rbind(dapr07,dmay07,djun07,djul07,daug07,dsep07)
dtotevt07 = ddply(dcmb,c("coop_id"),.fun=sumevnt)

dapr = dstn
dapr$month = 4
dapr$year = 2015
dapr11 = ddply(dapr,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
dapr11 = merge(dapr11,dstn)

dmay = dstn
dmay$month = 5
dmay$year = 2015
dmay11 = ddply(dmay,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
dmay11 = merge(dmay11,dstn)

djun = dstn
djun$month = 6
djun$year = 2015
djun11 = ddply(djun,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
djun11 = merge(djun11,dstn)

djul = dstn
djul$month = 7
djul$year = 2015
djul11 = ddply(djul,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
djul11 = merge(djul11,dstn)

daug = dstn
daug$month = 8
daug$year = 2015
daug11 = ddply(daug,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
daug11 = merge(daug11,dstn)

dsep = dstn
dsep$month = 9
dsep$year = 2015
dsep11 = ddply(dsep,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q99",flagfrm=dflg,
               vrsmry="obs_precip",extfn=monthprcp)
dsep11 = merge(dsep11,dstn)

dcmb = rbind(dapr11,dmay11,djun11,djul11,daug11,dsep11)
dtotevt11 = ddply(dcmb,c("coop_id"),.fun=sumevnt)

dtotevt07 = dtotevt07[dtotevt07$qday > 0,]
dtotevt07$exprop = dtotevt07$totevt / dtotevt07$qday
dtotevt11 = dtotevt11[dtotevt11$qday > 0,]
dtotevt11$exprop = dtotevt11$totevt / dtotevt11$qday

dtotevt07 = dtotevt07[,c("coop_id","exprop")]
names(dtotevt07) = c("coop_id","DailyPrcp07_11")
dtotevt11 = dtotevt11[,c("coop_id","exprop")]
names(dtotevt11) = c("coop_id","DailyPrcp11")

dprcpcoop = merge(dtotevt11,dtotevt07)

# ------------------------------------------------------------------------#
# Drought Index
d0 = as.POSIXct("2007-01-02 00:00:00",tz="GMT")
wksq = seq(0,52*5,by=1)
dall = d0 + as.difftime(wksq*7,units="days")
dfmt = as.character(format(dall,"%Y-%m-%d"))

for (j in seq(1,length(dfmt))) {
    print(dfmt[j])
    d1 = drtinpoly(dstn,dtstr=dfmt[j],dbcon=con)
    if (j == 1) {
       dfnl = d1
    }
    else {
       dfnl = rbind(dfnl,d1)
    }
}

dfnl$drought_score = 0
dfnl$drought_score[dfnl$drought_id == "D0"] = 1
dfnl$drought_score[dfnl$drought_id == "D1"] = 2
dfnl$drought_score[dfnl$drought_id == "D2"] = 3
dfnl$drought_score[dfnl$drought_id == "D3"] = 4
dfnl$drought_score[dfnl$drought_id == "D4"] = 5

ddrt = ddply(dfnl,c("coop_id"),.fun=qsum,srtvr="drought_score")

dtot07 = merge(dstn,ddrt,all.x=TRUE)
dtot07$totct[is.na(dtot07$totct)] = 0

dfmt11 = dfmt[210:261]

for (j in seq(1,length(dfmt11))) {
    print(dfmt11[j])
    d1 = drtinpoly(dstn,dtstr=dfmt11[j],dbcon=con)
    if (j == 1) {
       dfnl = d1
    }
    else {
       dfnl = rbind(dfnl,d1)
    }
}

dfnl$drought_score = 0
dfnl$drought_score[dfnl$drought_id == "D0"] = 1
dfnl$drought_score[dfnl$drought_id == "D1"] = 2
dfnl$drought_score[dfnl$drought_id == "D2"] = 3
dfnl$drought_score[dfnl$drought_id == "D3"] = 4
dfnl$drought_score[dfnl$drought_id == "D4"] = 5

ddrt = ddply(dfnl,c("coop_id"),.fun=qsum,srtvr="drought_score")

dtot11 = merge(dstn,ddrt,all.x=TRUE)
dtot11$totct[is.na(dtot11$totct)] = 0

dtot07 = dtot07[,c("coop_id","totct")]
names(dtot07) = c("coop_id","Drought07_11")
dtot11 = dtot11[,c("coop_id","totct")]
names(dtot11) = c("coop_id","Drought11")

ddrtcoop = merge(dtot11,dtot07)

# ------------------------------------------------------------------------#
# Seasonal Precip
dssn = dstn
dspr = ddply(dssn,c("coop_id"),.fun=yrcdf,.progress="text",
               dbcon=con,flagfrm=dflg,
               vrsmry="totprcp",yrfn=yrprcp)

ds07 = dspr[dspr$year >= 2012,]
ds07cst = ddply(ds07,c("coop_id"),.fun=qsmryext,vrout="ecdf")
ds07cst = merge(ds07cst,dstn)
ds11 = dspr[dspr$year == 2015,]
ds11 = merge(ds11,dstn)

ds07cst = ds07cst[,c("coop_id","mean")]
names(ds07cst) = c("coop_id","SeasPrcp07_11")
ds11 = ds11[,c("coop_id","ecdf")]
names(ds11) = c("coop_id","SeasPrcp11")

prcpann = ddply(dssn,c("coop_id"),.fun=annsmry,.progress="text",
                dbcon=con,flagfrm=dflg,
                vrsmry="totprcp",yrfn=yrprcp)
prcpann = prcpann[,c("coop_id","median")]
names(prcpann) = c("coop_id","SeasPrcpMedian")

seascoop = merge(ds11,ds07cst)
seascoop = merge(seascoop,prcpann)

# ------------------------------------------------------------------------#
# Heat Stress

dsdd = ddply(dstn,c("coop_id"),.fun=yrstdd,.progress="text",dbcon=con)

dsdd2 = dsdd[dsdd$totobs > 350,]
sddsm = ddply(dsdd2,c("coop_id"),.fun=qsmryext,vrout="sdd_accum")

dsddsb = dsdd2[dsdd2$year >= 2012,]
dmrg = merge(dsddsb,sddsm[,c("coop_id","mean","sd")])
dmrg$ZScore = (dmrg$sdd_accum - dmrg$mean) / dmrg$sd
ds07cst = ddply(dmrg,c("coop_id"),.fun=qsmryext,vrout="ZScore")
ds07cst = merge(ds07cst,dstn)

ds11 = dmrg[dmrg$year == 2015,]
ds11 = merge(ds11,dstn)

ds07cst = ds07cst[,c("coop_id","mean")]
names(ds07cst) = c("coop_id","StressDD07_11")
ds11 = ds11[,c("coop_id","ZScore")]
names(ds11) = c("coop_id","StressDD11")

sddcoop = merge(ds11,ds07cst)

# ------------------------------------------------------------------------#
# Warm Nights
dapr = dstn
dapr$month = 4
dapr$year = 2012
dapr07 = ddply(dapr,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
dapr07 = merge(dapr07,dstn)

dmay = dstn
dmay$month = 5
dmay$year = 2012
dmay07 = ddply(dmay,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
dmay07 = merge(dmay07,dstn)

djun = dstn
djun$month = 6
djun$year = 2012
djun07 = ddply(djun,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
djun07 = merge(djun07,dstn)

djul = dstn
djul$month = 7
djul$year = 2012
djul07 = ddply(djul,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
djul07 = merge(djul07,dstn)

daug = dstn
daug$month = 8
daug$year = 2012
daug07 = ddply(daug,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
daug07 = merge(daug07,dstn)

dsep = dstn
dsep$month = 9
dsep$year = 2012
dsep07 = ddply(dsep,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
dsep07 = merge(dsep07,dstn)

dcmb = rbind(dapr07,dmay07,djun07,djul07,daug07,dsep07)
dtotevt07 = ddply(dcmb,c("coop_id"),.fun=sumevnt)


dapr = dstn
dapr$month = 4
dapr$year = 2015
dapr11 = ddply(dapr,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
dapr11 = merge(dapr11,dstn)

dmay = dstn
dmay$month = 5
dmay$year = 2015
dmay11 = ddply(dmay,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
dmay11 = merge(dmay11,dstn)

djun = dstn
djun$month = 6
djun$year = 2015
djun11 = ddply(djun,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
djun11 = merge(djun11,dstn)

djul = dstn
djul$month = 7
djul$year = 2015
djul11 = ddply(djul,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
djul11 = merge(djul11,dstn)

daug = dstn
daug$month = 8
daug$year = 2015
daug11 = ddply(daug,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
daug11 = merge(daug11,dstn)

dsep = dstn
dsep$month = 9
dsep$year = 2015
dsep11 = ddply(dsep,c("coop_id"),.fun=mnthextct,.progress="text",
               dbcon=con,vrext="q90",flagfrm=dflg,
               vrsmry="obs_low",extfn=monthtmin)
dsep11 = merge(dsep11,dstn)

dcmb = rbind(dapr11,dmay11,djun11,djul11,daug11,dsep11)
dtotevt11 = ddply(dcmb,c("coop_id"),.fun=sumevnt)

dtotevt07 = dtotevt07[dtotevt07$qday > 0,]
dtotevt07$exprop = dtotevt07$totevt / dtotevt07$qday
dtotevt11 = dtotevt11[dtotevt11$qday > 0,]
dtotevt11$exprop = dtotevt11$totevt / dtotevt11$qday

dtotevt07 = dtotevt07[,c("coop_id","exprop")]
names(dtotevt07) = c("coop_id","WarmNight07_11")
dtotevt11 = dtotevt11[,c("coop_id","exprop")]
names(dtotevt11) = c("coop_id","WarmNight11")

warmcoop = merge(dtotevt11,dtotevt07)

dbDisconnect(con)

# Assemble dataset by Coop
aridcoop = merge(aridcoop,dstn[,c("coop_id","huc6_id","longitude","latitude")])
save(aridcoop,dprcpcoop,ddrtcoop,seascoop,
     sddcoop,warmcoop,file="WeatherCoop.RData")

coopdat = aridcoop[,c("coop_id","huc6_id","longitude","latitude","Aridity07_11","Aridity11")]
coopdat = merge(coopdat,dprcpcoop[,c("coop_id","DailyPrcp07_11","DailyPrcp11")])
coopdat = merge(coopdat,ddrtcoop[,c("coop_id","Drought07_11","Drought11")])
coopdat = merge(coopdat,seascoop[,c("coop_id","SeasPrcpMedian","SeasPrcp07_11","SeasPrcp11")])
coopdat = merge(coopdat,sddcoop[,c("coop_id","StressDD07_11","StressDD11")])
coopdat = merge(coopdat,warmcoop[,c("coop_id","WarmNight07_11","WarmNight11")])

coopdat = coopdat[,c("coop_id","longitude","latitude","huc6_id","SeasPrcpMedian","SeasPrcp07_11","SeasPrcp11",
                     "DailyPrcp07_11","DailyPrcp11","Drought07_11","Drought11",
                     "Aridity07_11","Aridity11","StressDD07_11","StressDD11",
                     "WarmNight07_11","WarmNight11")]

write.csv(coopdat,file="WeatherCoopInHUC6.csv",row.names=FALSE,quote=FALSE)

