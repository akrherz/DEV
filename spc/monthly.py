"""See SQL.txt."""

import calendar
from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd

data = """month|word|count
 200101 | MAY  |    44
 200101 | WILL |   545
 200102 | MAY  |    94
 200102 | WILL |   612
 200103 | MAY  |   145
 200103 | WILL |   733
 200104 | MAY  |   204
 200104 | WILL |   896
 200105 | MAY  |   203
 200105 | WILL |  1038
 200106 | MAY  |   238
 200106 | WILL |   951
 200107 | MAY  |   266
 200107 | WILL |  1036
 200108 | MAY  |   167
 200108 | WILL |   972
 200109 | MAY  |   181
 200109 | WILL |   748
 200110 | MAY  |   154
 200110 | WILL |   660
 200111 | MAY  |   113
 200111 | WILL |   537
 200112 | MAY  |   136
 200112 | WILL |   643
 200201 | MAY  |    73
 200201 | WILL |   513
 200202 | MAY  |    72
 200202 | WILL |   466
 200203 | MAY  |   152
 200203 | WILL |   730
 200204 | MAY  |   170
 200204 | WILL |   859
 200205 | MAY  |   197
 200205 | WILL |  1074
 200206 | MAY  |   224
 200206 | WILL |   888
 200207 | MAY  |   212
 200207 | WILL |  1003
 200208 | MAY  |   158
 200208 | WILL |   899
 200209 | MAY  |   204
 200209 | WILL |   887
 200210 | MAY  |   148
 200210 | WILL |   797
 200211 | MAY  |    93
 200211 | WILL |   527
 200212 | MAY  |    82
 200212 | WILL |   579
 200301 | MAY  |    44
 200301 | WILL |   425
 200302 | MAY  |   116
 200302 | WILL |   620
 200303 | MAY  |   128
 200303 | WILL |   828
 200304 | MAY  |   202
 200304 | WILL |  1006
 200305 | MAY  |   294
 200305 | WILL |  1256
 200306 | MAY  |   242
 200306 | WILL |  1206
 200307 | MAY  |   258
 200307 | WILL |  1274
 200308 | MAY  |   267
 200308 | WILL |  1198
 200309 | MAY  |   179
 200309 | WILL |   901
 200310 | MAY  |   104
 200310 | WILL |   694
 200311 | MAY  |    49
 200311 | WILL |   473
 200312 | MAY  |    65
 200312 | WILL |   385
 200401 | MAY  |    67
 200401 | WILL |   388
 200402 | MAY  |    60
 200402 | WILL |   449
 200403 | MAY  |    97
 200403 | WILL |   573
 200404 | MAY  |   109
 200404 | WILL |   573
 200405 | MAY  |   136
 200405 | WILL |   733
 200406 | MAY  |   184
 200406 | WILL |   873
 200407 | MAY  |   290
 200407 | WILL |  1324
 200408 | MAY  |   266
 200408 | WILL |  1216
 200409 | MAY  |   174
 200409 | WILL |   942
 200410 | MAY  |   150
 200410 | WILL |  1014
 200411 | MAY  |   154
 200411 | WILL |   680
 200412 | MAY  |   111
 200412 | WILL |   774
 200501 | MAY  |    64
 200501 | WILL |   419
 200502 | MAY  |    59
 200502 | WILL |   460
 200503 | MAY  |    79
 200503 | WILL |   560
 200504 | MAY  |   127
 200504 | WILL |   647
 200505 | MAY  |   151
 200505 | WILL |   775
 200506 | MAY  |   175
 200506 | WILL |   764
 200507 | MAY  |   175
 200507 | WILL |   630
 200508 | MAY  |   124
 200508 | WILL |   532
 200509 | MAY  |   104
 200509 | WILL |   546
 200510 | MAY  |    57
 200510 | WILL |   460
 200511 | MAY  |    89
 200511 | WILL |   442
 200512 | MAY  |    67
 200512 | WILL |   436
 200601 | MAY  |    71
 200601 | WILL |   457
 200602 | MAY  |    59
 200602 | WILL |   316
 200603 | MAY  |   125
 200603 | WILL |   498
 200604 | MAY  |   105
 200604 | WILL |   514
 200605 | MAY  |   157
 200605 | WILL |   579
 200606 | MAY  |   120
 200606 | WILL |   543
 200607 | MAY  |   138
 200607 | WILL |   752
 200608 | MAY  |   222
 200608 | WILL |   695
 200609 | MAY  |    91
 200609 | WILL |   463
 200610 | MAY  |   116
 200610 | WILL |   451
 200611 | MAY  |    58
 200611 | WILL |   377
 200612 | MAY  |    65
 200612 | WILL |   252
 200701 | MAY  |    75
 200701 | WILL |   303
 200702 | MAY  |    68
 200702 | WILL |   379
 200703 | MAY  |   155
 200703 | WILL |   536
 200704 | MAY  |   108
 200704 | WILL |   509
 200705 | MAY  |   186
 200705 | WILL |   652
 200706 | MAY  |   167
 200706 | WILL |   713
 200707 | MAY  |   151
 200707 | WILL |   718
 200708 | MAY  |   206
 200708 | WILL |   482
 200709 | MAY  |   110
 200709 | WILL |   445
 200710 | MAY  |    78
 200710 | WILL |   349
 200711 | MAY  |    48
 200711 | WILL |   323
 200712 | MAY  |    67
 200712 | WILL |   371
 200801 | MAY  |    66
 200801 | WILL |   380
 200802 | MAY  |    72
 200802 | WILL |   391
 200803 | MAY  |    91
 200803 | WILL |   389
 200804 | MAY  |   119
 200804 | WILL |   618
 200805 | MAY  |   136
 200805 | WILL |   610
 200806 | MAY  |   153
 200806 | WILL |   768
 200807 | MAY  |   187
 200807 | WILL |   708
 200808 | MAY  |   110
 200808 | WILL |   535
 200809 | MAY  |    81
 200809 | WILL |   390
 200810 | MAY  |    83
 200810 | WILL |   356
 200811 | MAY  |    89
 200811 | WILL |   312
 200812 | MAY  |    54
 200812 | WILL |   313
 200901 | MAY  |    39
 200901 | WILL |   314
 200902 | MAY  |    58
 200902 | WILL |   313
 200903 | MAY  |    83
 200903 | WILL |   500
 200904 | MAY  |   128
 200904 | WILL |   704
 200905 | MAY  |    93
 200905 | WILL |   540
 200906 | MAY  |   136
 200906 | WILL |   724
 200907 | MAY  |   148
 200907 | WILL |   660
 200908 | MAY  |   134
 200908 | WILL |   476
 200909 | MAY  |    64
 200909 | WILL |   546
 200910 | MAY  |    68
 200910 | WILL |   339
 200911 | MAY  |    45
 200911 | WILL |   350
 200912 | MAY  |    48
 200912 | WILL |   398
 201001 | MAY  |    53
 201001 | WILL |   327
 201002 | MAY  |    37
 201002 | WILL |   258
 201003 | MAY  |    93
 201003 | WILL |   431
 201004 | MAY  |    86
 201004 | WILL |   491
 201005 | MAY  |   108
 201005 | WILL |   561
 201006 | MAY  |   113
 201006 | WILL |   633
 201007 | MAY  |   115
 201007 | WILL |   550
 201008 | MAY  |   115
 201008 | WILL |   530
 201009 | MAY  |    71
 201009 | WILL |   377
 201010 | MAY  |    67
 201010 | WILL |   424
 201011 | MAY  |    49
 201011 | WILL |   258
 201012 | MAY  |    52
 201012 | WILL |   255
 201101 | MAY  |    47
 201101 | WILL |   291
 201102 | MAY  |    50
 201102 | WILL |   219
 201103 | MAY  |   140
 201103 | WILL |   460
 201104 | MAY  |   108
 201104 | WILL |   449
 201105 | MAY  |   167
 201105 | WILL |   608
 201106 | MAY  |   168
 201106 | WILL |   611
 201107 | MAY  |   136
 201107 | WILL |   587
 201108 | MAY  |   124
 201108 | WILL |   458
 201109 | MAY  |    75
 201109 | WILL |   324
 201110 | MAY  |    68
 201110 | WILL |   324
 201111 | MAY  |    54
 201111 | WILL |   276
 201112 | MAY  |    62
 201112 | WILL |   285
 201201 | MAY  |    54
 201201 | WILL |   330
 201202 | MAY  |    74
 201202 | WILL |   410
 201203 | MAY  |    84
 201203 | WILL |   364
 201204 | MAY  |   132
 201204 | WILL |   655
 201205 | MAY  |   156
 201205 | WILL |   557
 201206 | MAY  |   123
 201206 | WILL |   438
 201207 | MAY  |   166
 201207 | WILL |   720
 201208 | MAY  |   149
 201208 | WILL |   464
 201209 | MAY  |    95
 201209 | WILL |   380
 201210 | MAY  |   104
 201210 | WILL |   287
 201211 | MAY  |    58
 201211 | WILL |   286
 201212 | MAY  |    73
 201212 | WILL |   282
 201301 | MAY  |    52
 201301 | WILL |   227
 201302 | MAY  |    70
 201302 | WILL |   294
 201303 | MAY  |    78
 201303 | WILL |   324
 201304 | MAY  |   106
 201304 | WILL |   484
 201305 | MAY  |   136
 201305 | WILL |   473
 201306 | MAY  |   155
 201306 | WILL |   444
 201307 | MAY  |   166
 201307 | WILL |   571
 201308 | MAY  |   127
 201308 | WILL |   573
 201309 | MAY  |    69
 201309 | WILL |   395
 201310 | MAY  |    80
 201310 | WILL |   339
 201311 | MAY  |    53
 201311 | WILL |   269
 201312 | MAY  |    47
 201312 | WILL |   281
 201401 | MAY  |    44
 201401 | WILL |   204
 201402 | MAY  |    31
 201402 | WILL |   260
 201403 | MAY  |    74
 201403 | WILL |   344
 201404 | MAY  |    96
 201404 | WILL |   463
 201405 | MAY  |   152
 201405 | WILL |   496
 201406 | MAY  |   162
 201406 | WILL |   768
 201407 | MAY  |   151
 201407 | WILL |   591
 201408 | MAY  |   133
 201408 | WILL |   550
 201409 | MAY  |   108
 201409 | WILL |   359
 201410 | MAY  |    87
 201410 | WILL |   404
 201411 | MAY  |    70
 201411 | WILL |   296
 201412 | MAY  |    86
 201412 | WILL |   308
 201501 | MAY  |    55
 201501 | WILL |   241
 201502 | MAY  |    48
 201502 | WILL |   214
 201503 | MAY  |    88
 201503 | WILL |   399
 201504 | MAY  |   109
 201504 | WILL |   442
 201505 | MAY  |   150
 201505 | WILL |   519
 201506 | MAY  |   139
 201506 | WILL |   536
 201507 | MAY  |   159
 201507 | WILL |   486
 201508 | MAY  |    99
 201508 | WILL |   404
 201509 | MAY  |   101
 201509 | WILL |   315
 201510 | MAY  |    76
 201510 | WILL |   299
 201511 | MAY  |    59
 201511 | WILL |   314
 201512 | MAY  |    79
 201512 | WILL |   353
 201601 | MAY  |    72
 201601 | WILL |   292
 201602 | MAY  |    59
 201602 | WILL |   282
 201603 | MAY  |   111
 201603 | WILL |   473
 201604 | MAY  |   179
 201604 | WILL |   428
 201605 | MAY  |   180
 201605 | WILL |   621
 201606 | MAY  |   177
 201606 | WILL |   509
 201607 | MAY  |   155
 201607 | WILL |   568
 201608 | MAY  |    98
 201608 | WILL |   472
 201609 | MAY  |   106
 201609 | WILL |   465
 201610 | MAY  |    72
 201610 | WILL |   357
 201611 | MAY  |    86
 201611 | WILL |   297
 201612 | MAY  |    74
 201612 | WILL |   291
 201701 | MAY  |    83
 201701 | WILL |   272
 201702 | MAY  |    60
 201702 | WILL |   368
 201703 | MAY  |   116
 201703 | WILL |   398
 201704 | MAY  |   154
 201704 | WILL |   457
 201705 | MAY  |   149
 201705 | WILL |   744
 201706 | MAY  |   173
 201706 | WILL |   557
 201707 | MAY  |   150
 201707 | WILL |   647
 201708 | MAY  |   174
 201708 | WILL |   501
 201709 | MAY  |    89
 201709 | WILL |   405
 201710 | MAY  |    69
 201710 | WILL |   341
 201711 | MAY  |    65
 201711 | WILL |   261
 201712 | MAY  |    43
 201712 | WILL |   247
 201801 | MAY  |    42
 201801 | WILL |   272
 201802 | MAY  |    51
 201802 | WILL |   315
 201803 | MAY  |   128
 201803 | WILL |   361
 201804 | MAY  |    84
 201804 | WILL |   432
 201805 | MAY  |   217
 201805 | WILL |   515
 201806 | MAY  |   258
 201806 | WILL |   669
 201807 | MAY  |   140
 201807 | WILL |   489
 201808 | MAY  |   140
 201808 | WILL |   472
 201809 | MAY  |   155
 201809 | WILL |   359
 201810 | MAY  |   116
 201810 | WILL |   356
 201811 | MAY  |    75
 201811 | WILL |   343
 201812 | MAY  |    83
 201812 | WILL |   309
 201901 | MAY  |    47
 201901 | WILL |   268
 201902 | MAY  |    76
 201902 | WILL |   278
 201903 | MAY  |    59
 201903 | WILL |   374
 201904 | MAY  |   103
 201904 | WILL |   519
 201905 | MAY  |   130
 201905 | WILL |   695
 201906 | MAY  |   174
 201906 | WILL |   609
 201907 | MAY  |   182
 201907 | WILL |   572
 201908 | MAY  |   143
 201908 | WILL |   658
 201909 | MAY  |   151
 201909 | WILL |   521
 201910 | MAY  |   101
 201910 | WILL |   456
 201911 | MAY  |    44
 201911 | WILL |   288
 201912 | MAY  |   115
 201912 | WILL |   312
"""


def main():
    """Go Main Go."""
    df = pd.read_csv(StringIO(data.replace(" ", "")), sep="|")
    df["date"] = df["month"].astype(str) + "01"
    df["date"] = pd.to_datetime(df["date"])
    df.drop("month", axis=1, inplace=True)
    jdf = df.pivot(index="date", columns="word", values="count")
    jdf["ratio"] = jdf["WILL"] / jdf["MAY"]
    overall = jdf["WILL"].sum() / float(jdf["MAY"].sum())
    s = jdf["ratio"].rolling(window=12).mean()
    jdf["month"] = jdf.index.month

    (fig, ax) = plt.subplots(2, 1)
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
    ax[0].set_ylabel("Ratio ('WILL' / 'MAY')")
    fig.text(
        0.5,
        0.95,
        (
            "2001-2019 Storm Prediction Center Day2  Outlook Text\n"
            "Ratio of the words 'WILL' vs 'MAY' appearing "
            f"in the text, Avg: {overall:.1f}"
        ),
        ha="center",
        va="center",
    )

    g = jdf.groupby("month").sum()
    g["ratio"] = g["WILL"] / g["MAY"]
    print(g)
    print(g["WILL"].sum() / float(g["MAY"].sum()))

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
    ax[1].set_ylabel("Ratio ('WILL' / 'MAY')")

    fig.text(0.01, 0.01, "Generated 20 Jan 2020 by @akrherz", fontsize=10)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
