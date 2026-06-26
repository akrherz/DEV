"""Review what we have on disk and sync with the database."""

import os
from pathlib import Path

from pyiem.database import get_sqlalchemy_conn
from sqlalchemy import text


def main():
    """Go Main Go."""
    with get_sqlalchemy_conn("dep") as conn:
        for root, _dirs, files in os.walk("/i/0/cli/"):
            for file in files:
                path = Path(root) / Path(file)
                # Figure out the lat/lon of this filename, it has the form
                # 087.81x044.63.cli
                tokens = file.split("x")
                lon = 0 - float(tokens[0])
                lat = float(tokens[1].rsplit(".", maxsplit=1)[0])
                res = conn.execute(
                    text("""
    select climate_file_id from climate_file
    where filepath = :path and scenario_id = 0
                                  """),
                    {"path": str(path)},
                )
                if res.rowcount == 0:
                    print(f"Adding {path}")
                    conn.execute(
                        text(
                            """
        INSERT into climate_file(filepath, scenario_id, geom)
        VALUES (:path, 0, ST_Point(:lon, :lat, 4326))
        """
                        ),
                        {"path": str(path), "lat": lat, "lon": lon},
                    )
                    conn.commit()


if __name__ == "__main__":
    main()
