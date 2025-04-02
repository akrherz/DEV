"""
with warns as (
    select wfo, ugc, issue, expire from warnings
    where phenomena = 'HW' and significance ='W' and issue > '2005-10-01'),
watch as (
    select wfo, ugc, phenomena, issue, greatest(init_expire, expire) as expire
    from warnings where
    phenomena in ('HW') and significance = 'A'),
agg as (
    SELECT w.ugc, w.wfo, w.issue as w_issue, w.expire, a.ugc as a_ugc,
    a.phenomena,
    a.issue, a.expire from warns w LEFT JOIN watch a on (w.ugc = a.ugc
    and w.issue < a.expire and w.expire > a.issue))

 SELECT wfo, count(*), sum(case when phenomena = 'HW' then 1 else 0 end)
    as haswatch,
 sum(case when phenomena is null then 1 else 0 end) as nowatch from agg
 GROUP by wfo ORDER by wfo

 agg2 as (SELECT extract(week from w_issue) as week, count(*),
 sum(case when a_ugc is not null then 1 else 0 end) from agg GROUP by week)
  select week, sum / count::float * 100 from agg2 ORDER by week;

"""

from io import StringIO

import pandas as pd
from pyiem.plot import MapPlot, get_cmap


def main():
    """Go Main."""
    tor_data = """ ABQ |  3067 |     2238 |     829
 ABR |   944 |      449 |     495
 AFC |   790 |      412 |     378
 AFG |   529 |      206 |     323
 AJK |   629 |      314 |     315
 AKQ |   409 |      118 |     291
 ALY |   850 |      424 |     426
 AMA |  1654 |      904 |     750
 APX |   210 |      122 |      88
 ARX |   126 |       76 |      50
 BGM |   304 |      193 |     111
 BIS |  1742 |     1039 |     703
 BMX |    72 |        0 |      72
 BOI |   142 |       47 |      95
 BOU |  1251 |      691 |     560
 BOX |  1618 |     1084 |     534
 BRO |    24 |       11 |      13
 BTV |   407 |      285 |     122
 BUF |   810 |      565 |     245
 BYZ |  1643 |      911 |     732
 CAE |    49 |       24 |      25
 CAR |   534 |      348 |     186
 CHS |    86 |       24 |      62
 CLE |   826 |      463 |     363
 CRP |    66 |        2 |      64
 CTP |   442 |      312 |     130
 CYS |  5353 |     3478 |    1875
 DDC |  2329 |     1088 |    1241
 DLH |    32 |        9 |      23
 DMX |   897 |      418 |     479
 DTX |   336 |      277 |      59
 DVN |   331 |      141 |     190
 EAX |   446 |       96 |     350
 EKA |   185 |      122 |      63
 EPZ |  1091 |      720 |     371
 EWX |    38 |        0 |      38
 FFC |   401 |       78 |     323
 FGF |   653 |      208 |     445
 FGZ |   439 |      237 |     202
 FSD |   990 |      385 |     605
 FWD |   197 |       42 |     155
 GGW |  1036 |      611 |     425
 GID |  1165 |      718 |     447
 GJT |   276 |      144 |     132
 GLD |  1706 |      833 |     873
 GRB |    85 |       54 |      31
 GRR |   311 |      167 |     144
 GSP |   984 |      507 |     477
 GUM |    12 |        8 |       4
 GYX |   488 |      321 |     167
 HFO |   535 |      300 |     235
 HGX |     4 |        0 |       4
 HNX |   428 |      165 |     263
 HUN |    99 |        0 |      99
 ICT |   725 |      293 |     432
 ILM |     5 |        5 |       0
 ILN |   891 |      440 |     451
 ILX |   306 |       92 |     214
 IND |   436 |      180 |     256
 IWX |   533 |      335 |     198
 JAN |   109 |        0 |     109
 JAX |     7 |        0 |       7
 JKL |   337 |       96 |     241
 KEY |     1 |        0 |       1
 LBF |  1280 |      748 |     532
 LCH |    86 |       29 |      57
 LIX |   290 |       96 |     194
 LKN |   239 |      119 |     120
 LMK |   732 |      160 |     572
 LOT |   351 |      173 |     178
 LOX |  1617 |     1001 |     616
 LSX |   118 |       21 |      97
 LUB |  1205 |      783 |     422
 LWX |  1165 |      753 |     412
 LZK |    39 |        0 |      39
 MAF |  3094 |     2017 |    1077
 MEG |   301 |        4 |     297
 MFL |     5 |        0 |       5
 MFR |  1188 |      775 |     413
 MHX |   163 |       74 |      89
 MKX |   205 |       79 |     126
 MLB |     9 |        0 |       9
 MOB |    73 |       20 |      53
 MPX |   347 |       77 |     270
 MQT |   116 |       67 |      49
 MRX |  1455 |      939 |     516
 MSO |   247 |      104 |     143
 MTR |   379 |      288 |      91
 OAX |   660 |      323 |     337
 OHX |   136 |        0 |     136
 OKX |  1013 |      573 |     440
 OTX |   208 |      136 |      72
 OUN |  1206 |      503 |     703
 PAH |   272 |       58 |     214
 PBZ |   496 |      279 |     217
 PDT |   515 |      238 |     277
 PHI |  1010 |      601 |     409
 PIH |   234 |      131 |     103
 PQR |  1162 |      762 |     400
 PSR |   105 |       36 |      69
 PUB |  2285 |     1326 |     959
 RAH |   218 |       47 |     171
 REV |   393 |      267 |     126
 RIW |  1571 |      974 |     597
 RLX |   250 |      139 |     111
 RNK |  1199 |      589 |     610
 SEW |   918 |      560 |     358
 SGF |   258 |       27 |     231
 SGX |  1233 |      779 |     454
 SHV |    10 |        0 |      10
 SJT |   233 |       54 |     179
 SLC |   699 |      326 |     373
 STO |   205 |      122 |      83
 TAE |    12 |        5 |       7
 TFX |  3605 |     2490 |    1115
 TOP |   346 |      108 |     238
 TSA |   157 |       38 |     119
 TWC |    81 |       26 |      55
 UNR |  2008 |     1238 |     770
 VEF |   968 |      610 |     358"""

    sio = StringIO()
    sio.write(tor_data)
    sio.seek(0)
    # need to strip all whitespace
    tor = pd.read_csv(
        sio, sep=r"\s*\|\s*", names=["wfo", "count", "inwatch", "nowatch"]
    ).set_index("wfo")

    tor["freq"] = tor["inwatch"] / tor["count"] * 100.0
    print(tor["freq"].to_dict())
    overall = tor["inwatch"].sum() / tor["count"].sum() * 100.0
    mp = MapPlot(
        sector="conus",
        title=(
            "Percentage of Counties/Zones in High Wind Warning with a HW Watch"
        ),
        subtitle=(
            f"Oct 2005 - 2 Apr 2025, Overall: {tor['inwatch'].sum():,.0f} / "
            f"{tor['count'].sum():,.0f} = {overall:.1f}%"
        ),
    )
    cmap = get_cmap("plasma")
    mp.fill_cwas(
        tor["freq"].to_dict(),
        cmap=cmap,
        bins=range(0, 101, 10),
        extend="neither",
        units="%",
        lblformat="%.0f",
        ilabel=True,
    )

    mp.fig.savefig("HWW_in_watch.png")


if __name__ == "__main__":
    main()
