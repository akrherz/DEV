"""Unsure of origin."""
from io import StringIO

import pandas as pd
import matplotlib.pyplot as plt

data = """num | cnt
   1 |   148
   2 |   194
   3 |   246
   4 |   239
   5 |   244
   6 |   232
   7 |   252
   8 |   222
   9 |   208
  10 |   185
  11 |   217
  12 |   188
  13 |   180
  14 |   182
  15 |   177
  16 |   140
  17 |   116
  18 |   134
  19 |   109
  20 |   107
  21 |    98
  22 |   105
  23 |    81
  24 |    79
  25 |    74
  26 |    64
  27 |    69
  28 |    61
  29 |    70
  30 |    53
  31 |    51
  32 |    46
  33 |    42
  34 |    34
  35 |    24
  36 |    30
  37 |    33
  38 |    38
  39 |    13
  40 |    22
  41 |    26
  42 |    21
  43 |    19
  44 |    12
  45 |    21
  46 |    13
  47 |    17
  48 |    11
  49 |     9
  50 |    13
  51 |    13
  52 |     9
  53 |     8
  54 |    10
  55 |    12
  56 |     8
  57 |    14
  58 |     5
  59 |     3
  60 |     4
  61 |     3
  62 |     5
  63 |     7
  64 |     8
  65 |     1
  66 |     3
  67 |     3
  68 |     2
  69 |     2
  71 |     3
  72 |     1
  74 |     3
  75 |     3
  76 |     2
  77 |     1
  78 |     4
  79 |     2
  80 |     1
  81 |     1
  83 |     2
  85 |     1
  86 |     1
  87 |     3
  89 |     2
  91 |     1
  92 |     1
  95 |     1
  98 |     1
 101 |     1
 104 |     1
 107 |     1
 112 |     1
 118 |     1
 122 |     1"""


def main():
    """Go Main Go."""
    df = pd.read_csv(StringIO(data.replace(" ", "")), sep="|", index_col="num")
    df.index -= 1

    df["cs"] = df["cnt"].cumsum()
    total = float(df["cnt"].sum())

    (fig, ax) = plt.subplots(1, 1)
    ax.bar(df.index.values, df["cnt"], fc="tan", ec="tan")
    ax.grid(True)
    ax.set_yticks([0, 75, 150, 225, 300])
    ax.set_xlabel("Number of Severe T'Storm and Tornado Warnings in Watch")
    ax.set_ylabel("Frequency [# of watches]")
    ax.set_title(
        (
            "Number of Severe T'Storm + Tornado Warnings per Severe T'Storm Watch\n"
            "2005-2016, number of distinct storm based warnings issued during watch"
        ),
        fontsize=12,
    )
    ax2 = ax.twinx()
    ax2.plot(df.index.values, df["cs"] / total * 100, lw=2)
    ax2.set_ylim(0, 100)
    ax2.set_yticks([0, 25, 50, 75, 100])
    ax2.set_ylabel("Accumulated Frequency [%]", color="b")

    ax.text(
        0.35,
        0.5,
        (
            "%% of watches with no warnings: %.2f%%\n"
            "Most Warnings: 2015 Watch #5 had 121\n"
            "Largest Frequency at 6 Warnings"
        )
        % (df.at[0, "cnt"] / total * 100.0,),
        va="center",
        bbox=dict(color="white"),
        transform=ax.transAxes,
    )
    fig.text(0.005, 0.01, "@akrherz\n7 July 2016", fontsize=10)

    fig.savefig("test.png")


if __name__ == "__main__":
    main()
