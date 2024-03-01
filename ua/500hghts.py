"""
Compute the difference between the 12 UTC 850 hPa temp and afternoon high
"""

import calendar
from datetime import timezone

import seaborn as sns

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_sqlalchemy_conn


def run():
    """Run()."""
    # get 500 heights
    with get_sqlalchemy_conn("raob") as conn:
        h500 = pd.read_sql(
            """
        select valid at time zone 'UTC' as utc_valid,
        max(p.height) as hght from
        raob_profile p JOIN raob_flights f on
        (p.fid = f.fid) where f.station in ('KOAX', 'KOVN', 'KOMA') and
        p.pressure = 500
        and extract(hour from valid at time zone 'UTC') in (0,12)
        GROUP by utc_valid ORDER by utc_valid ASC
        """,
            conn,
        )
    h500 = (
        h500.assign(
            utc_valid=lambda df_: df_["utc_valid"].dt.tz_localize(timezone.utc)
        )
        .set_index("utc_valid")
        .pipe(
            lambda df_: df_.reindex(
                pd.date_range(
                    df_.index.values[0],
                    df_.index.values[-1],
                    freq="12H",
                    tz=timezone.utc,
                )
            )
        )
        .assign(next_hght=lambda df_: df_["hght"].shift(-1))
        .assign(change=lambda df_: df_["next_hght"] - df_["hght"])
    )
    # Get obs
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            """
            select valid at time zone 'UTC' as utc_valid, tmpf from alldata
            where station = 'OMA' and array_to_string(wxcodes, '') ~* 'TS'
            and report_type in (3, 4)
            ORDER by valid ASC
            """,
            conn,
        )
    obs = (
        obs.assign(
            utc_valid=lambda df_: df_["utc_valid"].dt.tz_localize(
                timezone.utc
            ),
            period=lambda df_: df_["utc_valid"].apply(
                lambda x: x.replace(hour=12, minute=0)
            ),
        )
        .assign(
            period=lambda df_: df_["period"].where(
                df_["utc_valid"].dt.hour >= 12,
                df_["utc_valid"].apply(lambda x: x.replace(hour=0, minute=0)),
                axis=0,
            )
        )
        .drop(columns=["utc_valid"])
        .groupby("period")
        .first()
    )
    (
        h500.assign(tmpf=obs["tmpf"])
        .reset_index()
        .rename(columns={"index": "utc_valid"})
        .to_csv("h500.csv")
    )


def main():
    """Go Main Go."""
    df = pd.read_csv("h500.csv", parse_dates=["utc_valid"])
    df = df[(df["change"] > -250) & (df["change"] < 250)]
    df2 = df[pd.notna(df["tmpf"])]

    (fig, ax) = figure_axes(
        title=(
            "Omaha 500hPa 12 Hour Height Change + METAR Thunder (TS) Reported"
        ),
        subtitle=(
            f"{df2['utc_valid'].min():%Y/%m/%d} to "
            f"{df['utc_valid'].max():%Y-%m-%d}, "
            "violin sides individually scaled"
        ),
    )
    df = df.assign(
        month=lambda df_: df_["utc_valid"].dt.month,
        hit=lambda df_: pd.notna(df_["tmpf"]),
    )
    sns.violinplot(
        df,
        x="month",
        y="change",
        hue="hit",
        ax=ax,
        split=True,
    )
    tt = ax.legend(title=None, ncol=2).get_texts()
    tt[0].set_text("No Thunder")
    tt[1].set_text("Thunder")
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylabel("12 Hour Height Change [m]")
    for month, df2 in df.groupby("month"):
        val = (
            len(df2[(df2["change"] < 0) & pd.notna(df2["tmpf"])].index)
            / pd.notna(df2["tmpf"]).sum()
            * 100.0
        )
        ax.text(
            month - 1,
            -320,
            f"{val:.1f}%",
            ha="center",
            bbox={"color": "white"},
        )
    ax.set_xlabel(
        "Percentage Labels indicate % of Thunder Events with decreasing height"
    )

    fig.savefig("230505.png")


if __name__ == "__main__":
    main()
