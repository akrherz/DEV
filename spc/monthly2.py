"""See SQL.txt"""

import calendar
from io import StringIO

import pandas as pd
from pyiem.plot import figure

data = """month|word|count
 200011 |   0 |  115
 200011 |   1 |   49
 200012 |   0 |  455
 200012 |   1 |   69
 200101 |   0 |  498
 200101 |   1 |   88
 200102 |   0 |  728
 200102 |   1 |  160
 200103 |   0 |  839
 200103 |   1 |  225
 200104 |   0 | 1055
 200104 |   1 |  262
 200105 |   0 | 1531
 200105 |   1 |  347
 200106 |   0 | 1240
 200106 |   1 |  368
 200107 |   0 | 1877
 200107 |   1 |  505
 200108 |   0 | 2103
 200108 |   1 |  614
 200109 |   0 | 1640
 200109 |   1 |  515
 200110 |   0 | 1295
 200110 |   1 |  308
 200111 |   0 |  895
 200111 |   1 |  229
 200112 |   0 |  408
 200112 |   1 |  114
 200201 |   0 |  559
 200201 |   1 |  134
 200202 |   0 |  446
 200202 |   1 |   92
 200203 |   0 |  871
 200203 |   1 |  159
 200204 |   0 | 1010
 200204 |   1 |  292
 200205 |   0 |  966
 200205 |   1 |  272
 200206 |   0 |  255
 200206 |   1 |   49
 200207 |   0 |  448
 200207 |   1 |  113
 200208 |   0 |  829
 200208 |   1 |  232
 200209 |   0 |  775
 200209 |   1 |  215
 200210 |   0 |  779
 200210 |   1 |  186
 200211 |   0 |  509
 200211 |   1 |  141
 200212 |   0 |  366
 200212 |   1 |   93
 200301 |   0 |  323
 200301 |   1 |   57
 200302 |   0 |  610
 200302 |   1 |  120
 200303 |   0 |  659
 200303 |   1 |  147
 200304 |   0 | 1064
 200304 |   1 |  244
 200305 |   0 | 1419
 200305 |   1 |  278
 200306 |   0 | 1248
 200306 |   1 |  237
 200307 |   0 | 1306
 200307 |   1 |  317
 200308 |   0 | 1575
 200308 |   1 |  398
 200309 |   0 | 1278
 200309 |   1 |  237
 200310 |   0 | 1086
 200310 |   1 |  167
 200311 |   0 | 1113
 200311 |   1 |  157
 200312 |   0 |  943
 200312 |   1 |  137
 200401 |   0 |  904
 200401 |   1 |  134
 200402 |   0 | 1018
 200402 |   1 |  131
 200403 |   0 | 1244
 200403 |   1 |  254
 200404 |   0 | 1549
 200404 |   1 |  316
 200405 |   0 | 1792
 200405 |   1 |  382
 200406 |   0 | 1607
 200406 |   1 |  372
 200407 |   0 | 1072
 200407 |   1 |  290
 200408 |   0 | 1635
 200408 |   1 |  358
 200409 |   0 | 1074
 200409 |   1 |  226
 200410 |   0 | 1195
 200410 |   1 |  265
 200411 |   0 |  800
 200411 |   1 |  157
 200412 |   0 |  669
 200412 |   1 |  113
 200501 |   0 |  827
 200501 |   1 |  168
 200502 |   0 |  915
 200502 |   1 |  139
 200503 |   0 | 1120
 200503 |   1 |  220
 200504 |   0 | 1476
 200504 |   1 |  365
 200505 |   0 | 1241
 200505 |   1 |  309
 200506 |   0 | 1079
 200506 |   1 |  263
 200507 |   0 | 1344
 200507 |   1 |  406
 200508 |   0 | 1275
 200508 |   1 |  321
 200509 |   0 | 1445
 200509 |   1 |  377
 200510 |   0 | 1088
 200510 |   1 |  224
 200511 |   0 | 1005
 200511 |   1 |  169
 200512 |   0 |  857
 200512 |   1 |  122
 200601 |   0 | 1029
 200601 |   1 |  192
 200602 |   0 |  671
 200602 |   1 |  148
 200603 |   0 | 1075
 200603 |   1 |  306
 200604 |   0 | 1162
 200604 |   1 |  356
 200605 |   0 | 1229
 200605 |   1 |  347
 200606 |   0 | 1271
 200606 |   1 |  370
 200607 |   0 | 1245
 200607 |   1 |  352
 200608 |   0 | 1239
 200608 |   1 |  397
 200609 |   0 | 1029
 200609 |   1 |  309
 200610 |   0 |  894
 200610 |   1 |  265
 200611 |   0 |  729
 200611 |   1 |  188
 200612 |   0 |  575
 200612 |   1 |  140
 200701 |   0 |  552
 200701 |   1 |  121
 200702 |   0 |  624
 200702 |   1 |  138
 200703 |   0 |  956
 200703 |   1 |  281
 200704 |   0 | 1209
 200704 |   1 |  303
 200705 |   0 | 1453
 200705 |   1 |  386
 200706 |   0 | 1382
 200706 |   1 |  523
 200707 |   0 | 1456
 200707 |   1 |  506
 200708 |   0 | 1252
 200708 |   1 |  456
 200709 |   0 | 1089
 200709 |   1 |  279
 200710 |   0 |  876
 200710 |   1 |  258
 200711 |   0 |  591
 200711 |   1 |  123
 200712 |   0 |  223
 200712 |   1 |   61
 200801 |   0 |  489
 200801 |   1 |  123
 200802 |   0 |  859
 200802 |   1 |  202
 200803 |   0 | 1008
 200803 |   1 |  213
 200804 |   0 | 1036
 200804 |   1 |  262
 200805 |   0 | 1460
 200805 |   1 |  345
 200806 |   0 | 1327
 200806 |   1 |  330
 200807 |   0 | 1372
 200807 |   1 |  445
 200808 |   0 | 1366
 200808 |   1 |  417
 200809 |   0 |   55
 200809 |   1 |   10
 200810 |   0 |   55
 200810 |   1 |   10
 200811 |   0 |   55
 200811 |   1 |   10
 200812 |   0 |  157
 200812 |   1 |   45
 200901 |   0 |  592
 200901 |   1 |  101
 200902 |   0 |  821
 200902 |   1 |  175
 200903 |   0 | 1078
 200903 |   1 |  297
 200904 |   0 | 1563
 200904 |   1 |  469
 200905 |   0 | 1691
 200905 |   1 |  581
 200906 |   0 | 1911
 200906 |   1 |  501
 200907 |   0 | 1707
 200907 |   1 |  465
 200908 |   0 | 1491
 200908 |   1 |  431
 200909 |   0 | 1053
 200909 |   1 |  287
 200910 |   0 | 1046
 200910 |   1 |  285
 200911 |   0 |  564
 200911 |   1 |  160
 200912 |   0 |  871
 200912 |   1 |  181
 201001 |   0 |  716
 201001 |   1 |  170
 201002 |   0 |  621
 201002 |   1 |  139
 201003 |   0 | 1042
 201003 |   1 |  231
 201004 |   0 | 1158
 201004 |   1 |  240
 201005 |   0 | 1584
 201005 |   1 |  422
 201006 |   0 | 1602
 201006 |   1 |  464
 201007 |   0 | 1578
 201007 |   1 |  454
 201008 |   0 | 1536
 201008 |   1 |  356
 201009 |   0 | 1203
 201009 |   1 |  288
 201010 |   0 |  885
 201010 |   1 |  216
 201011 |   0 |  745
 201011 |   1 |  153
 201012 |   0 |  721
 201012 |   1 |  122
 201101 |   0 |  663
 201101 |   1 |  107
 201102 |   0 |  648
 201102 |   1 |  167
 201103 |   0 | 1022
 201103 |   1 |  273
 201104 |   0 | 1444
 201104 |   1 |  319
 201105 |   0 | 1478
 201105 |   1 |  498
 201106 |   0 | 1741
 201106 |   1 |  412
 201107 |   0 | 1588
 201107 |   1 |  451
 201108 |   0 | 1457
 201108 |   1 |  370
 201109 |   0 | 1249
 201109 |   1 |  294
 201110 |   0 | 1037
 201110 |   1 |  282
 201111 |   0 |  857
 201111 |   1 |  193
 201112 |   0 |  886
 201112 |   1 |  184
 201201 |   0 |  884
 201201 |   1 |  216
 201202 |   0 |  994
 201202 |   1 |  244
 201203 |   0 | 1328
 201203 |   1 |  302
 201204 |   0 | 1502
 201204 |   1 |  333
 201205 |   0 | 1643
 201205 |   1 |  558
 201206 |   0 | 1774
 201206 |   1 |  523
 201207 |   0 | 1871
 201207 |   1 |  570
 201208 |   0 | 1473
 201208 |   1 |  427
 201209 |   0 | 1231
 201209 |   1 |  419
 201210 |   0 | 1055
 201210 |   1 |  301
 201211 |   0 |  672
 201211 |   1 |  157
 201212 |   0 | 1045
 201212 |   1 |  199
 201301 |   0 |  832
 201301 |   1 |  141
 201302 |   0 |  838
 201302 |   1 |  236
 201303 |   0 |  906
 201303 |   1 |  272
 201304 |   0 | 1294
 201304 |   1 |  437
 201305 |   0 | 1488
 201305 |   1 |  535
 201306 |   0 | 1624
 201306 |   1 |  479
 201307 |   0 | 1519
 201307 |   1 |  548
 201308 |   0 | 1503
 201308 |   1 |  516
 201309 |   0 | 1066
 201309 |   1 |  350
 201310 |   0 |  986
 201310 |   1 |  285
 201311 |   0 |  731
 201311 |   1 |  157
 201312 |   0 |  806
 201312 |   1 |  152
 201401 |   0 |  601
 201401 |   1 |  131
 201402 |   0 |  799
 201402 |   1 |  198
 201403 |   0 | 1043
 201403 |   1 |  269
 201404 |   0 | 1373
 201404 |   1 |  419
 201405 |   0 | 1487
 201405 |   1 |  572
 201406 |   0 | 1844
 201406 |   1 |  563
 201407 |   0 | 1664
 201407 |   1 |  578
 201408 |   0 | 1452
 201408 |   1 |  493
 201409 |   0 | 1136
 201409 |   1 |  408
 201410 |   0 | 1099
 201410 |   1 |  335
 201411 |   0 |  840
 201411 |   1 |  220
 201412 |   0 |  894
 201412 |   1 |  195
 201501 |   0 |  646
 201501 |   1 |  178
 201502 |   0 |  691
 201502 |   1 |  178
 201503 |   0 |  983
 201503 |   1 |  352
 201504 |   0 | 1427
 201504 |   1 |  525
 201505 |   0 | 1452
 201505 |   1 |  483
 201506 |   0 | 1640
 201506 |   1 |  538
 201507 |   0 | 1442
 201507 |   1 |  566
 201508 |   0 | 1240
 201508 |   1 |  477
 201509 |   0 |  873
 201509 |   1 |  335
 201510 |   0 |  906
 201510 |   1 |  332
 201511 |   0 |  837
 201511 |   1 |  220
 201512 |   0 |  893
 201512 |   1 |  231
 201601 |   0 |  742
 201601 |   1 |  196
 201602 |   0 |  804
 201602 |   1 |  168
 201603 |   0 | 1233
 201603 |   1 |  385
 201604 |   0 | 1183
 201604 |   1 |  374
 201605 |   0 | 1441
 201605 |   1 |  508
 201606 |   0 | 1476
 201606 |   1 |  433
 201607 |   0 |  367
 201607 |   1 |  185
"""


def main():
    """Go Main Go."""
    df = pd.read_csv(StringIO(data.replace(" ", "")), sep="|")
    df["date"] = df["month"].astype(str) + "01"
    df["date"] = pd.to_datetime(df["date"])
    df.drop("month", axis=1, inplace=True)
    jdf = df.pivot(index="date", columns="word", values="count")
    jdf["ratio"] = jdf[0] / jdf[1]
    overall = jdf[0].sum() / float(jdf[1].sum())
    s = pd.rolling_mean(jdf["ratio"], window=12)
    jdf["month"] = jdf.index.month

    fig = figure()
    ax = [
        fig.add_axes((0.1, 0.55, 0.85, 0.4)),
        fig.add_axes((0.1, 0.1, 0.85, 0.4)),
    ]
    ax[0].bar(
        jdf.index.values,
        jdf["ratio"],
        width=31,
        ec="tan",
        fc="tan",
        align="center",
    )
    ax[0].plot(
        s.index.values,
        s.values,
        lw=2,
        color="k",
        zorder=5,
        label="12mon trailing avg",
    )
    ax[0].grid(True)
    ax[0].axhline(overall, color="r", lw=2, label="Avg", zorder=4)
    ax[0].legend(loc=4, fontsize=10, ncol=2)
    ax[0].text(
        0.5,
        0.92,
        "Monthly",
        transform=ax[0].transAxes,
        ha="center",
        va="center",
        bbox=dict(color="white"),
    )
    ax[0].set_ylabel("Ratio (certain / uncertain)")
    fig.text(
        0.5,
        0.95,
        (
            "2001-2016 Storm Prediction Center Day1 Outlook Text, "
            f"Avg: {overall:.1f}\n"
            "certain:  'WILL', 'LIKELY', 'UNLIKELY', 'CERTAINLY', "
            "'UNDOUBTEDLY'\n"
            "uncertain: 'MAY', 'PERHAPS', 'UNCERTAIN', 'COULD', 'MAYBE'"
        ),
        ha="center",
        va="center",
    )

    g = jdf.groupby("month").sum()
    g["ratio"] = g[0] / g[1]

    ax[1].bar(g.index.values, g["ratio"], ec="tan", fc="tan", align="center")
    ax[1].axhline(overall, color="r", lw=2, label="Avg", zorder=4)
    ax[1].set_xticks(range(1, 13))
    ax[1].text(
        0.5,
        0.92,
        "By Month",
        transform=ax[1].transAxes,
        ha="center",
        va="center",
        bbox=dict(color="white"),
    )
    ax[1].set_xticklabels(calendar.month_abbr[1:])
    ax[1].grid(True)
    ax[1].set_xlim(0.5, 12.5)
    ax[1].set_ylabel("Ratio (certain / uncertain)")

    fig.text(0.01, 0.01, "Generated 6 July 2016 by @akrherz", fontsize=10)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
