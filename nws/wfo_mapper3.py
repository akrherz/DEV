"""Generic plotter"""
import datetime
from calendar import month_abbr

from pyiem.plot.use_agg import plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, drct2text
import numpy as np
from pandas.io.sql import read_sql

data = """ KABQ   | 12768 |  367
 KABR   |  2848 |  474
 KAKQ   | 27284 |  886
 KALY   |  9476 |  102
 KAMA   | 10154 |  675
 KAPX   |  2200 |  108
 KARX   |  6226 |  437
 KBGM   |  8019 |  220
 KBIS   |  7249 |  836
 KBMX   | 15974 | 2419
 KBOI   |  1659 |   14
 KBOU   |  3564 | 1099
 KBOX   |  9146 |  101
 KBRO   |  4874 |  298
 KBTV   |  4930 |   34
 KBUF   |  7099 |   80
 KBYZ   |  4973 |  162
 KCAE   |  6252 |  437
 KCAR   |  4648 |   52
 KCHS   | 12973 |  577
 KCLE   |  3205 |  504
 KCRP   |  6215 |  505
 KCTP   | 12435 |  348
 KCYS   | 10741 |  487
 KDDC   |  5918 |  998
 KDLH   | 10119 |  369
 KDMX   |  5906 | 1201
 KDTX   |  7365 |  280
 KDVN   |  8142 |  763
 KEAX   |  8914 |  821
 KEKA   |  1333 |    2
 KEPZ   |  6263 |   54
 KEWX   |  7345 |  686
 KEYW   |   765 |   34
 KFFC   | 33854 | 1254
 KFGF   |  2804 | 1055
 KFGZ   |  1951 |  115
 KFSD   |  1596 | 1021
 KFWD   | 15344 |  984
 KGGW   |  2301 |  187
 KGID   |  8289 |  999
 KGJT   |  2555 |   16
 KGLD   |  8676 | 1093
 KGRB   |  8294 |  268
 KGRR   |  4629 |  284
 KGSP   | 20249 |  547
 KGYX   |  7450 |   57
 KHGX   |  4671 | 1192
 KHNX   |  4211 |   34
 KHUN   | 12906 |  877
 KICT   | 11424 | 1033
 KILM   |  7691 |  400
 KILN   | 10969 |  652
 KILX   |  2742 | 1283
 KIND   |  5074 |  966
 KIWX   |  7462 |  563
 KJAN   | 17183 | 3466
 KJAX   | 30132 |  932
 KJKL   |  8929 |  477
 KKEY   |  2291 |   67
 KLBF   |  7066 | 1093
 KLCH   |  6158 | 1010
 KLIX   | 12349 | 1952
 KLKN   |  4222 |   17
 KLMK   | 16904 | 1034
 KLOT   |  5196 |  670
 KLOX   |  2342 |   21
 KLSX   |  4965 | 1327
 KLUB   |  6709 |  489
 KLWX   |  9209 |  680
 KLZK   |  8852 | 1386
 KMAF   | 11307 |  568
 KMEG   | 10731 | 1866
 KMFL   | 13652 |  522
 KMFR   |  1751 |    3
 KMHX   |  9232 |  547
 KMKX   |  6018 |  423
 KMLB   | 10553 |  598
 KMOB   | 10410 | 1518
 KMPX   |  5485 | 1077
 KMQT   |  4239 |   71
 KMRX   |  8707 |  556
 KMSO   |  2223 |    5
 KMTR   |   930 |    4
 KOAX   |  7145 |  911
 KOHX   |  8648 | 1349
 KOKX   |  9066 |   97
 KOTX   |   762 |   11
 KOUN   | 27778 | 1702
 KPAH   |  7053 | 1672
 KPBZ   | 12612 |  253
 KPDT   |  1699 |   15
 KPHI   | 13743 |  264
 KPIH   |  4804 |  105
 KPQR   |  4315 |   24
 KPSR   |  4072 |   26
 KPUB   |  9789 |  481
 KRAH   | 16253 |  631
 KREV   |  4435 |   19
 KRIW   | 17065 |  152
 KRLX   | 10803 |  174
 KRNK   | 18787 |  381
 KSEW   |  1463 |    7
 KSGF   |  8054 | 1575
 KSGX   |  2063 |   26
 KSHV   |  8030 | 1330
 KSJT   |  9884 |  979
 KSLC   |  2347 |   32
 KSTO   |  4534 |   95
 KTAE   | 10513 | 1411
 KTBW   | 10414 |  554
 KTFX   |  5007 |   89
 KTOP   |  6379 |  660
 KTSA   | 15617 | 1321
 KTWC   |  2844 |    8
 KUNR   |  6263 |  431
 KVEF   |   427 |   17
 PAJK   |  1042 |    2
 PHFO   |   438 |    3
 TJSJ   |  3082 |   13"""


def main():
    """Go Main"""
    vals = {}
    for line in data.split("\n"):
        wfo, sps, svr = line.strip().split("|")
        wfo = wfo.strip()
        wfo = wfo[1:]
        if wfo == "JSJ":
            wfo = "SJU"
        vals[wfo] = float(sps) / 19.0
    bins = [1, 25, 100, 250, 500, 750, 1000, 1500, 2000]
    # bins = np.arange(2011, 2021, 1)
    # bins = [0, 0.1, 0.2, 0.5, 0.75, 1, 2, 5, 10]
    # bins = [1, 5, 10, 25, 50, 75, 100, 300]
    cmap = plt.get_cmap("hot")
    mp = MapPlot(
        sector="nws",
        continentalcolor="white",
        figsize=(12.0, 9.0),
        title=(
            "2001-2019 NWS SPS Text Products Issued per Year by Forecast Office"
        ),
        subtitle=("based on IEM archives"),
    )
    mp.fill_cwas(
        vals,
        bins=bins,
        lblformat="%.0f",  # , labels=labels,
        cmap=cmap,
        ilabel=True,  # clevlabels=clevlabels,
        units="count",
        spacing="proportional",
    )

    mp.postprocess(filename="test.png")


if __name__ == "__main__":
    main()
