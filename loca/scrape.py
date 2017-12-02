"""

2100-12-31T12%3A00%3A00Z

loca
https://cida.usgs.gov/thredds/ncss/loca/dataset.html
"""
import os
import requests
import tqdm

FUTURE = """ACCESS1-0_r1i1p1_rcp45
ACCESS1-0_r1i1p1_rcp85
ACCESS1-3_r1i1p1_rcp45
ACCESS1-3_r1i1p1_rcp85
CCSM4_r6i1p1_rcp45
CCSM4_r6i1p1_rcp85
CESM1-BGC_r1i1p1_rcp45
CESM1-BGC_r1i1p1_rcp85
CESM1-CAM5_r1i1p1_rcp45
CESM1-CAM5_r1i1p1_rcp85
CMCC-CMS_r1i1p1_rcp45
CMCC-CMS_r1i1p1_rcp85
CMCC-CM_r1i1p1_rcp45
CMCC-CM_r1i1p1_rcp85
CNRM-CM5_r1i1p1_rcp45
CNRM-CM5_r1i1p1_rcp85
CSIRO-Mk3-6-0_r1i1p1_rcp45
CSIRO-Mk3-6-0_r1i1p1_rcp85
CanESM2_r1i1p1_rcp45
CanESM2_r1i1p1_rcp85
EC-EARTH_r2i1p1_rcp85
EC-EARTH_r8i1p1_rcp45
FGOALS-g2_r1i1p1_rcp45
FGOALS-g2_r1i1p1_rcp85
GFDL-CM3_r1i1p1_rcp45
GFDL-CM3_r1i1p1_rcp85
GFDL-ESM2G_r1i1p1_rcp45
GFDL-ESM2G_r1i1p1_rcp85
GFDL-ESM2M_r1i1p1_rcp45
GFDL-ESM2M_r1i1p1_rcp85
GISS-E2-H_r2i1p1_rcp85
GISS-E2-H_r6i1p3_rcp45
GISS-E2-R_r2i1p1_rcp85
GISS-E2-R_r6i1p1_rcp45
HadGEM2-AO_r1i1p1_rcp45
HadGEM2-AO_r1i1p1_rcp85
HadGEM2-CC_r1i1p1_rcp45
HadGEM2-CC_r1i1p1_rcp85
HadGEM2-ES_r1i1p1_rcp45
HadGEM2-ES_r1i1p1_rcp85
IPSL-CM5A-LR_r1i1p1_rcp45
IPSL-CM5A-LR_r1i1p1_rcp85
IPSL-CM5A-MR_r1i1p1_rcp45
IPSL-CM5A-MR_r1i1p1_rcp85
MIROC-ESM-CHEM_r1i1p1_rcp45
MIROC-ESM-CHEM_r1i1p1_rcp85
MIROC-ESM_r1i1p1_rcp45
MIROC-ESM_r1i1p1_rcp85
MIROC5_r1i1p1_rcp45
MIROC5_r1i1p1_rcp85
MPI-ESM-LR_r1i1p1_rcp45
MPI-ESM-LR_r1i1p1_rcp85
MPI-ESM-MR_r1i1p1_rcp45
MPI-ESM-MR_r1i1p1_rcp85
MRI-CGCM3_r1i1p1_rcp45
MRI-CGCM3_r1i1p1_rcp85
NorESM1-M_r1i1p1_rcp45
NorESM1-M_r1i1p1_rcp85
bcc-csm1-1-m_r1i1p1_rcp45
bcc-csm1-1-m_r1i1p1_rcp85"""

HIST = """ACCESS1-0_r1i1p1_historical
ACCESS1-3_r1i1p1_historical
CCSM4_r6i1p1_historical
CESM1-BGC_r1i1p1_historical
CESM1-CAM5_r1i1p1_historical
CMCC-CMS_r1i1p1_historical
CMCC-CM_r1i1p1_historical
CNRM-CM5_r1i1p1_historical
CSIRO-Mk3-6-0_r1i1p1_historical
CanESM2_r1i1p1_historical
EC-EARTH_r1i1p1_historical
FGOALS-g2_r1i1p1_historical
GFDL-CM3_r1i1p1_historical
GFDL-ESM2G_r1i1p1_historical
GFDL-ESM2M_r1i1p1_historical
GISS-E2-H_r6i1p1_historical
GISS-E2-R_r6i1p1_historical
HadGEM2-AO_r1i1p1_historical
HadGEM2-CC_r1i1p1_historical
HadGEM2-ES_r1i1p1_historical
IPSL-CM5A-LR_r1i1p1_historical
IPSL-CM5A-MR_r1i1p1_historical
MIROC-ESM-CHEM_r1i1p1_historical
MIROC-ESM_r1i1p1_historical
MIROC5_r1i1p1_historical
MPI-ESM-LR_r1i1p1_historical
MPI-ESM-MR_r1i1p1_historical
MRI-CGCM3_r1i1p1_historical
NorESM1-M_r1i1p1_historical
bcc-csm1-1-m_r1i1p1_historical"""


def downloader(varname, model, syear, eyear):
    """Go Main Go"""
    url = ("https://cida.usgs.gov/thredds/ncss/loca_future?"
           "var="+varname+"_"+model+"&north=44&west=-98.1&"
           "east=-90.0&south=41.0&disableProjSubset=on&horizStride=1"
           "&time_start="+syear+"-01-01T12%3A00%3A00Z&"
           "time_end="+eyear+"-01-01T12%3A00%3A00Z&"
           "timeStride=1&addLatLon=true")
    filename = "%s_%s.nc" % (varname, model)
    if os.path.isfile(filename):
        return
    req = requests.get(url, stream=True)
    with open('test.nc', 'wb') as fh:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                fh.write(chunk)


def main():
    """Go Main Go"""
    for varname in ['pr', 'tasmin', 'tasmax']:
        for line in tqdm.tqdm(HIST.split("\n")):
            model = line.strip()
            downloader(varname, model, 1970, 2006)
        for line in tqdm.tqdm(FUTURE.split("\n")):
            model = line.strip()
            downloader(varname, model, 2006, 2071)


if __name__ == '__main__':
    main()
