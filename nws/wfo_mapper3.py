"""Generic plotter"""
import datetime
from calendar import month_abbr

from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, drct2text
import numpy as np
from pandas.io.sql import read_sql

data = """ KABQ   | 12768 |  5433
 KABR   |  2848 |  4757
 KAKQ   | 27284 |  3733
 KALY   |  9476 |  2944
 KAMA   | 10154 |  5306
 KAPX   |  2200 |  1604
 KARX   |  6226 |  2778
 KBGM   |  8019 |  3399
 KBIS   |  7249 |  6108
 KBMX   | 15974 |  7248
 KBOI   |  1659 |   688
 KBOU   |  3564 |  4417
 KBOX   |  9146 |  2481
 KBRO   |  4874 |  1426
 KBTV   |  4930 |  1368
 KBUF   |  7099 |  2100
 KBYZ   |  4973 |  3151
 KCAE   |  6252 |  4375
 KCAR   |  4648 |  1267
 KCHS   | 12973 |  3858
 KCLE   |  3205 |  4797
 KCRP   |  6215 |  1947
 KCTP   | 12435 |  4501
 KCYS   | 10741 |  3792
 KDDC   |  5918 |  7105
 KDLH   | 10119 |  3568
 KDMX   |  5906 |  7070
 KDTX   |  7365 |  2433
 KDVN   |  8142 |  3725
 KEAX   |  8914 |  5343
 KEKA   |  1333 |   115
 KEPZ   |  6263 |  1857
 KEWX   |  7345 |  4368
 KEYW   |   765 |    31
 KFFC   | 33854 |  9030
 KFGF   |  2804 |  4631
 KFGZ   |  1951 |  2331
 KFSD   |  1596 |  6552
 KFWD   | 15344 |  8345
 KGGW   |  2301 |  2836
 KGID   |  8289 |  6888
 KGJT   |  2555 |   679
 KGLD   |  8676 |  7040
 KGRB   |  8294 |  2254
 KGRR   |  4629 |  2476
 KGSP   | 20249 |  8349
 KGTF   |   154 |     3
 KGYX   |  7450 |  2392
 KHGX   |  4671 |  3815
 KHNX   |  4211 |   352
 KHUN   | 12906 |  3699
 KICT   | 11424 |  7745
 KILM   |  7691 |  2394
 KILN   | 10969 |  5566
 KILX   |  2742 |  4970
 KIND   |  5074 |  4089
 KIWX   |  7462 |  3644
 KJAN   | 17183 | 13681
 KJAX   | 30132 |  5486
 KJKL   |  8929 |  4240
 KKEY   |  2291 |    47
 KLBF   |  7066 |  7799
 KLCH   |  6158 |  3077
 KLIX   | 12349 |  4101
 KLKN   |  4222 |   743
 KLMK   | 16904 |  7249
 KLOT   |  5196 |  3623
 KLOX   |  2342 |   160
 KLSX   |  4965 |  7033
 KLUB   |  6709 |  5373
 KLWX   |  9209 |  6236
 KLZK   |  8852 | 10546
 KMAF   | 11307 |  6587
 KMEG   | 10731 |  8409
 KMFL   | 13652 |  1889
 KMFR   |  1751 |   359
 KMHX   |  9232 |  1898
 KMKX   |  6018 |  2368
 KMLB   | 10553 |  2182
 KMOB   | 10410 |  4922
 KMPX   |  5485 |  5594
 KMQT   |  4239 |  1494
 KMRX   |  8707 |  6116
 KMSO   |  2223 |   862
 KMTR   |   930 |    66
 KOAX   |  7145 |  7684
 KOHX   |  8648 |  7065
 KOKX   |  9066 |  1774
 KOMA   |   511 |     1
 KOTX   |   762 |   516
 KOUN   | 27778 | 16029
 KPAH   |  7053 |  6327
 KPBZ   | 12612 |  5284
 KPDT   |  1699 |   654
 KPHI   | 13743 |  4786
 KPIH   |  4804 |  1175
 KPQR   |  4315 |   226
 KPSR   |  4072 |  2301
 KPUB   |  9789 |  4466
 KRAH   | 16253 |  5655
 KREV   |  4435 |   575
 KRIW   | 17065 |  1450
 KRLX   | 10803 |  3819
 KRNK   | 18787 |  6009
 KSEW   |  1463 |    44
 KSGF   |  8054 |  8615
 KSGX   |  2063 |   405
 KSHV   |  8030 |  7193
 KSJT   |  9884 |  6022
 KSLC   |  2347 |  1595
 KSPI   |  2241 |     2
 KSTO   |  4534 |   472
 KTAE   | 10513 |  5170
 KTBW   | 10414 |  1924
 KTFX   |  5007 |  2108
 KTOP   |  6379 |  5167
 KTSA   | 15617 |  8816
 KTWC   |  2844 |  2344
 KUNR   |  6263 |  7166
 KVEF   |   427 |  1278
 PAFC   |  1315 |    54
 PAFG   |  1904 |    60
 PAJK   |  1042 |     8
 PAJN   |    36 |     1
 PGUM   |  1527 |     5
 PHFO   |   438 |    74
 TJSJ   |  3082 |   160"""


def main():
    """Go Main"""
    vals = {}
    for line in data.split("\n"):
        wfo, sps, svr = line.strip().split("|")
        wfo = wfo.strip()
        wfo = wfo[1:]
        if wfo == "JSJ":
            wfo = "SJU"
        vals[wfo] = float(sps) / float(svr)
    # bins = [1, 25, 100, 250, 500, 750, 1000, 1500, 2000]
    # bins = np.arange(2011, 2021, 1)
    bins = [0, 0.1, 0.2, 0.5, 0.75, 1, 2, 5, 10]
    cmap = plt.get_cmap("hot")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        figsize=(12.0, 9.0),
        title=(
            "2001-2019 NWS Ratio of SPS to SVR Text Products by Forecast Office"
        ),
        subtitle=("based on IEM archives"),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%.2f",  # , labels=labels,
        cmap=cmap,
        ilabel=True,  # clevlabels=clevlabels,
        units="SPS / SVR",
        spacing="proportional",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
