"""Compare with older DEP output."""

# stdlib
import os

import click
import numpy as np
import pandas as pd
from pydep.io.wepp import read_env, read_ofe
from pyiem.database import get_sqlalchemy_conn
from tqdm import tqdm


def compute_env(huc12):
    """Compute for the env results."""
    # Figure out the flowpath lengths
    with get_sqlalchemy_conn("idep") as conn:
        fp = pd.read_sql(
            """
            select fpath, real_length from flowpaths
            where huc_12 = %s and scenario = 0
            """,
            conn,
            params=(huc12,),
            index_col="fpath",
        )

    os.chdir(f"/i/0/env/{huc12[:8]}/{huc12[8:]}")
    progress = tqdm(os.listdir("."))
    res = []
    for envfn in progress:
        progress.set_description(f"{envfn}")
        df = read_env(envfn)
        fpath = int(envfn.split("_")[1].split(".")[0])
        res.append(
            df["sed_del"].sum() * 4.463 / 17.0 / fp.at[fpath, "real_length"]
        )
    print(f"ENV Mean: {np.mean(res):.2f} T/a/yr")


@click.command()
@click.option("--huc12", default="102300060301")
def main(huc12):
    """Go Main Go."""
    with get_sqlalchemy_conn("idep") as conn:
        res = pd.read_sql(
            """
            select * from results_by_huc12 where scenario = 0 and huc_12 = %s
            """,
            conn,
            params=(huc12,),
        )
    print(
        f"Prod Delivery: {res['avg_delivery'].sum() * 4.463 / 17:.2f} T/a/yr"
    )

    compute_env(huc12)

    # Figure out the fields
    with get_sqlalchemy_conn("idep") as conn:
        fields = pd.read_sql(
            """
            select f.fbndid, f.landuse, l.label, f.acres from fields f,
            general_landuse l where f.huc12 = %s and
            f.genlu = l.id
            """,
            conn,
            params=(huc12,),
            index_col="fbndid",
        )
    # Figure out the OFEs
    with get_sqlalchemy_conn("idep") as conn:
        ofes = pd.read_sql(
            """
            select ofe, fpath, fbndid, o.real_length
            from flowpath_ofes o JOIN flowpaths f
            on (o.flowpath = f.fid) WHERE f.huc_12 = %s and
            f.scenario = 0 ORDER by fpath ASC, ofe ASC
            """,
            conn,
            params=(huc12,),
            index_col=None,
        )
        ofes["loss"] = -1.0
        ofes["delivery"] = -1.0

    # Figure out the DEP results by OFE
    for fpath, gdf in ofes.groupby("fpath"):
        lastdelivery = 0
        accum_length = 0
        df = read_ofe(
            f"/i/0/ofe/{huc12[:8]}/{huc12[8:]}/{huc12}_{fpath:.0f}.ofe"
        )
        for ofe in gdf["ofe"]:
            ofedf = ofes[(ofes["ofe"] == ofe) & (ofes["fpath"] == fpath)]
            row = ofedf.iloc[0]
            accum_length += row["real_length"]
            df2 = df[df["ofe"] == ofe]
            thisdelivery = df2["sedleave"].sum() * 4.463 / 17.0 / accum_length
            ofes.loc[ofedf.index, "delivery"] = thisdelivery
            ofes.loc[ofedf.index, "loss"] = thisdelivery - lastdelivery
            lastdelivery = thisdelivery

    # Join the field info back into the ofes
    ofes = pd.merge(ofes, fields, left_on="fbndid", right_index=True)

    fields["delivery"] = ofes.groupby("fbndid")["delivery"].mean()
    df2 = fields[fields["delivery"] > 0]
    fields["weight"] = fields["acres"] / df2["acres"].sum()

    for label, gdf in fields.groupby("label"):
        modelled = gdf[pd.notna(gdf["delivery"])]
        ma = modelled["acres"].sum()
        ta = gdf["acres"].sum()
        print(f"{label} {ma:.1f}/{ta:.1f} {ma / ta * 100.0:.2f}")

    # weighting by acres
    print(
        "delivery average with acres weighting: %.2f"
        % ((fields["delivery"] * fields["weight"]).sum(),)
    )

    print("bulk delivery average: %.2f" % (ofes["delivery"].mean(),))
    df2 = ofes[ofes["label"] != "Pasture|Grass|Hay"]
    print("bulk delivery average no pasture: %.2f" % (df2["delivery"].mean(),))
    print(
        "groupby field delivery average: %.2f" % (fields["delivery"].mean(),)
    )

    print(ofes.groupby("label")["delivery"].mean())


if __name__ == "__main__":
    main()
