"""Review IEM processing of 6 hourly max/min temperatures."""

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.network import Table as NetworkTable


@click.command()
@click.option("--station", type=str, required=True, help="ASOS Station ID")
@click.option("--network", type=str, required=True, help="ASOS Network ID")
def main(station, network):
    """xref."""
    nt = NetworkTable(network)
    with get_sqlalchemy_conn("asos") as conn:
        # backup the timestamp to make top of the hour obs work more cleanly
        # and account for standard time
        obsdf = pd.read_sql(
            sql_helper("""
            select (valid - '61 minutes'::interval) at time zone 'UTC'
            as utc_valid,
            (valid - '61 minutes'::interval) at time zone :tzname
            as localvalid,
            max_tmpf_6hr,
            min_tmpf_6hr from alldata where station = :station and
            max_tmpf_6hr is not null and min_tmpf_6hr is not null
            ORDER by valid ASC
            """),
            conn,
            params={"station": station, "tzname": nt.sts[station]["tzname"]},
            index_col="utc_valid",
            parse_dates=["utc_valid", "localvalid"],
        )
    # OK, we should always be able to summarize this by the localvalid.date()
    minmaxdf = obsdf.groupby(obsdf["localvalid"].dt.date).agg(
        {"max_tmpf_6hr": "max", "min_tmpf_6hr": "min"}
    )
    minmaxdf["count"] = obsdf.groupby(obsdf["localvalid"].dt.date).size()
    with get_sqlalchemy_conn("iem") as conn:
        summarydf = pd.read_sql(
            sql_helper(
                """
            select day,
            max_tmpf, min_tmpf from summary where iemid = :iemid
            and max_tmpf is not null and min_tmpf is not null
            ORDER by day ASC
        """
            ),
            conn,
            params={"iemid": nt.sts[station]["iemid"]},
            index_col="day",
            parse_dates="day",
        )
    summarydf["obs_max"] = minmaxdf["max_tmpf_6hr"]
    summarydf["obs_min"] = minmaxdf["min_tmpf_6hr"]
    summarydf["count"] = minmaxdf["count"]
    # ensure we have valid obs_max and obs_min values
    summarydf = summarydf[summarydf["obs_max"].notna()]
    summarydf = summarydf[summarydf["obs_min"].notna()]
    summarydf["diff_max"] = summarydf["max_tmpf"] - summarydf["obs_max"]
    summarydf["diff_min"] = summarydf["min_tmpf"] - summarydf["obs_min"]
    print(summarydf.sort_values("diff_max", ascending=False))
    print(
        summarydf[
            (summarydf["count"] == 4) & (summarydf["diff_max"].abs() > 1)
        ].tail(100)
    )


if __name__ == "__main__":
    main()
