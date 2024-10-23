"""Quicker to update the feather file, than to regenerate it."""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from sqlalchemy import text
from tqdm import tqdm


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        newdf = pd.read_sql(
            text("""select p.huc_12, o.ofe, p.fpath,
    case when g.plastic_limit < 40 then
        g.plastic_limit else
        g.wepp_min_sw + (g.wepp_max_sw - g.wepp_min_sw) * 0.42
    end as plastic_limit
    from flowpaths p, flowpath_ofes o, gssurgo g
    WHERE o.flowpath = p.fid and p.scenario = 0 and o.gssurgo_id = g.id
        """),
            conn,
            index_col=["huc_12", "fpath", "ofe"],
        )

    progress = tqdm(list(range(2007, 2025)))
    for year in progress:
        progress.set_description(str(year))
        for dt in pd.date_range(f"{year}-04-10", f"{year}-06-15"):
            df = pd.read_feather(
                f"/mnt/idep2/data/smstate/{year}/smstate{dt:%Y%m%d}.feather"
            ).set_index(["huc12", "fpath", "ofe"])
            df["plastic_limit"] = newdf["plastic_limit"]
            df.reset_index().to_feather(
                f"/mnt/idep2/data/smstate/{year}/smstate{dt:%Y%m%d}.feather"
            )


if __name__ == "__main__":
    main()
