import psycopg2
import datetime
#import numpy as np
from pyiem.plot import MapPlot
import matplotlib.pyplot as plt

text = """ STO |                0 |       |     1
 OKX |                0 |       |     1
 GJT |                0 |       |     1
 MFR |                0 |       |     2
 BOX |                0 |       |     2
 GYX |                0 |       |     3
 PHI |               25 |     1 |     3
 GGW |               25 |     1 |     3
 BRO |                0 |       |     4
 BUF |                0 |       |     4
 BYZ | 14.2857142857143 |     1 |     6
 EPZ |                0 |       |     7
 TFX | 36.3636363636364 |     4 |     7
 ALY |                0 |       |     8
 RAH | 11.1111111111111 |     1 |     8
 CTP |               10 |     1 |     9
 MQT |               10 |     1 |     9
 LWX |                0 |       |    10
 BGM | 9.09090909090909 |     1 |    10
 GRR |               25 |     4 |    12
 RLX | 6.66666666666667 |     1 |    14
 GRB | 22.2222222222222 |     4 |    14
 CLE | 11.7647058823529 |     2 |    15
 APX | 11.7647058823529 |     2 |    15
 MRX |             6.25 |     1 |    15
 RIW |  19.047619047619 |     4 |    17
 GSP | 5.55555555555556 |     1 |    17
 MHX | 13.0434782608696 |     3 |    20
 DLH |               16 |     4 |    21
 RNK |                0 |       |    26
 DTX | 7.14285714285714 |     2 |    26
 CRP | 10.3448275862069 |     3 |    26
 CAE |                0 |       |    26
 MLB | 3.57142857142857 |     1 |    27
 ILM |                0 |       |    27
 MKX | 6.45161290322581 |     2 |    29
 PBZ |  3.2258064516129 |     1 |    30
 AKQ | 5.71428571428571 |     2 |    33
 TBW |  13.953488372093 |     6 |    37
 CHS |  4.8780487804878 |     2 |    39
 ABQ |  2.4390243902439 |     1 |    40
 MFL |                0 |       |    40
 LUB | 20.7547169811321 |    11 |    42
 ARX | 10.6382978723404 |     5 |    42
 UNR |             12.5 |     6 |    42
 ABR | 29.2307692307692 |    19 |    46
 CYS | 28.3582089552239 |    19 |    48
 HUN | 1.92307692307692 |     1 |    51
 MAF | 18.1818181818182 |    12 |    54
 JKL | 1.78571428571429 |     1 |    55
 LBF | 29.7619047619048 |    25 |    59
 IWX | 16.6666666666667 |    12 |    60
 LOT | 21.5909090909091 |    19 |    69
 PUB | 22.4719101123595 |    20 |    69
 TOP | 28.5714285714286 |    28 |    70
 MEG | 18.1818181818182 |    16 |    72
 OHX | 5.19480519480519 |     4 |    73
 ICT | 21.0526315789474 |    20 |    75
 BIS | 13.6363636363636 |    12 |    76
 BMX | 9.41176470588235 |     8 |    77
 AMA | 20.6185567010309 |    20 |    77
 OAX | 23.3009708737864 |    24 |    79
 EWX | 5.95238095238095 |     5 |    79
 ILN |  3.6144578313253 |     3 |    80
 LCH | 4.70588235294118 |     4 |    81
 MOB | 4.70588235294118 |     4 |    81
 FSD | 24.1071428571429 |    27 |    85
 JAX |                0 |       |    88
 HGX | 1.06382978723404 |     1 |    93
 MPX | 20.5128205128205 |    24 |    93
 FFC |  10.377358490566 |    11 |    95
 EAX | 15.7894736842105 |    18 |    96
 SJT | 13.5135135135135 |    15 |    96
 ILX |  9.1743119266055 |    10 |    99
 GID | 15.8333333333333 |    19 |   101
 DVN | 15.6716417910448 |    21 |   113
 LZK | 4.16666666666667 |     5 |   115
 FGF | 7.14285714285714 |     9 |   117
 IND | 12.3188405797101 |    17 |   121
 LMK |                0 |       |   122
 DMX | 18.4210526315789 |    28 |   124
 TAE | 9.48905109489051 |    13 |   124
 LSX | 9.86842105263158 |    15 |   137
 SGF |  3.8961038961039 |     6 |   148
 TSA | 7.31707317073171 |    12 |   152
 DDC | 15.8974358974359 |    31 |   164
 GLD | 21.8181818181818 |    48 |   172
 LIX | 7.88177339901478 |    16 |   187
 BOU | 12.1076233183857 |    27 |   196
 FWD | 12.6086956521739 |    29 |   201
 SHV | 3.13725490196078 |     8 |   247
 JAN | 9.15750915750916 |    25 |   248
 PAH | 8.69565217391304 |    24 |   252
 OUN | 13.8047138047138 |    41 |   256"""

from pyiem.network import Table

nt = Table("WFO")

data = {}
labels = {}
uniq = []
for line in text.split("\n"):
    tokens = line.split("|")
    wfo = tokens[0].strip()
    data[wfo] = float(tokens[1])

bins = range(0, 37, 4)
cmap = plt.get_cmap('viridis')
p = MapPlot(sector='nws', continental_color='white',
                 title="2013-2017 Percentage of Tornado Warnings with OBSERVED tag",
                 subtitle='based on warning issuance for warnings that included the TORNADO tag')
p.fill_cwas(data, bins=bins, labels=labels, lblformat='%.1f', cmap=cmap, ilabel=True,
            units='Percentage')
p.postprocess(filename='test.png')
#import iemplot
#iemplot.makefeature('test')
