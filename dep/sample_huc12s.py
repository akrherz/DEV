from sqlalchemy import text

from pyiem.util import get_sqlalchemy_conn

with get_sqlalchemy_conn("idep") as conn:
    res = conn.execute(
        text("""
with data as (select huc_12, mlra_id,
    rank() OVER (PARTITION by mlra_id ORDER by random() desc)
        from huc12 where states in ('MN', 'IA') and scenario = 0)
    select * from data where
             rank < 100 order by mlra_id desc;
""")
    )
    mlras = {}
    for row in res:
        if row[1] not in mlras:
            mlras[row[1]] = []
        if len(mlras[row[1]]) > 2:
            continue
        res2 = conn.execute(
            text(
                "select distinct fid from flowpath_ofes o JOIN flowpaths f on "
                "(o.flowpath = f.fid) where scenario = 0 and huc_12 = :huc12 "
                "and substr(landuse, 17, 1) in ('C', 'B')"
            ),
            {"huc12": row[0]},
        )
        if res2.rowcount < 50:
            print("HUC12: %s MLRA: %s %s" % (row[0], row[1], res2.rowcount))
            continue
        mlras[row[1]].append(row[0])

for mlra, hucs in mlras.items():
    print("MLRA: %s HUCS: %s" % (mlra, hucs))

for _, hucs in mlras.items():
    for huc in hucs:
        print(huc)
