"""Process GHCNh files into IEM Access, so destined for ASOS database."""

import os
import subprocess
import sys
from collections import defaultdict
from collections.abc import Generator
from typing import Optional

import click
from metpy.units import units
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.nws.products.metar_util import metar_from_dict
from pyiem.nws.products.metarcollect import normalize_temp
from pyiem.observation import Observation
from pyiem.util import c2f, logger, utc

LOG = logger()
MB = units("millibar")
HG = units("inch_Hg")
MPS = units("meters / second")
KTS = units("knot")
MM = units("millimeter")
INCH = units("inch")
KM = units("kilometer")
MILE = units("mile")
M = units("meter")
FT = units("feet")

# For those we don't take verbatim
PRESWX_TO_METAR = {
    "FG:44": "FG",
    "FG:45": "FZFG",
    "FG:49": "FZFG",
    "RA:61": "-RA",
    "RA:63": "+RA",
    "RA:65": "+RA",
    "SHRA:81": "SHRA",
    "SHRA:82": "+SHRA",
    "SN:71": "-SN",
    "SN:75": "+SN",
    "SQ": "SQ",
    "TS:95": "+TSRA",
    "TS:97": "+TSRA",
}


def build_dialect(colnames: list) -> dict[str, int]:
    """Figure out how to map colnames to token indices we need."""
    return {
        "year": colnames.index("Year"),
        "month": colnames.index("Month"),
        "day": colnames.index("Day"),
        "hour": colnames.index("Hour"),
        "minute": colnames.index("Minute"),
        "tmpc": colnames.index("temperature"),
        "dwpc": colnames.index("dew_point_temperature"),
        "mslp": colnames.index("sea_level_pressure"),  # hPa
        "drct": colnames.index("wind_direction"),
        "smps": colnames.index("wind_speed"),  # m/s
        "gmps": colnames.index("wind_gust"),  # m/s
        "p01m": colnames.index("precipitation"),  # mm
        "p03m": colnames.index("precipitation_3_hour"),  # mm
        "p06m": colnames.index("precipitation_6_hour"),  # mm
        "p24m": colnames.index("precipitation_24_hour"),  # mm
        # NCEI Calculated "relh": colnames.index("relative_humidity"),  # %
        "vsby_km": colnames.index("visibility"),  # km
        "alti_mb": colnames.index("altimeter"),  # hPa
        "pres_wx_mw1": colnames.index("pres_wx_MW1"),  # code
        "pres_wx_mw2": colnames.index("pres_wx_MW2"),  # code
        "pres_wx_mw3": colnames.index("pres_wx_MW3"),  # code
        "pres_wx_au1": colnames.index("pres_wx_AU1"),  # code
        "pres_wx_au2": colnames.index("pres_wx_AU2"),  # code
        "pres_wx_au3": colnames.index("pres_wx_AU3"),  # code
        "pres_wx_aw1": colnames.index("pres_wx_AW1"),  # code
        "pres_wx_aw2": colnames.index("pres_wx_AW2"),  # code
        "pres_wx_aw3": colnames.index("pres_wx_AW3"),  # code
        "skyc1": colnames.index("sky_cover_1"),  # octas
        "skyl1": colnames.index("sky_cover_baseht_1"),  # meters
        "skyc2": colnames.index("sky_cover_2"),  # octas
        "skyl2": colnames.index("sky_cover_baseht_2"),  # meters
        "skyc3": colnames.index("sky_cover_3"),  # octas
        "skyl3": colnames.index("sky_cover_baseht_3"),  # meters
        "remarks": colnames.index("remarks"),
    }


def parse_packet(
    value: str,
    measure: str,
    qc: str,
    report_type: str,
    source_code: str,
    station_id: str,
) -> Optional[float]:
    """Parse the temperature."""
    if value in ["", "9999"]:
        return None
    if source_code == "335" and qc in ["2", "3"]:
        return None
    if qc in ["a", "b"]:
        LOG.info(
            "'%s','%s','%s','%s','%s','%s'",
            value,
            measure,
            qc,
            report_type,
            source_code,
            station_id,
        )
        sys.exit()
    return float(value)


def process_line(line: str, dialect: dict[str, int]) -> dict:
    """Process a line of the file."""
    tokens = line.strip().split("|")
    ob = defaultdict(lambda: None)
    ob["valid"] = utc(
        int(tokens[dialect["year"]]),
        int(tokens[dialect["month"]]),
        int(tokens[dialect["day"]]),
        int(tokens[dialect["hour"]]),
        int(tokens[dialect["minute"]]),
    )
    val = parse_packet(*tokens[dialect["tmpc"] : dialect["tmpc"] + 6])
    if val is not None:
        ob["tmpf"] = normalize_temp(c2f(val))
        # Require a temperature to proceed
        val = parse_packet(*tokens[dialect["dwpc"] : dialect["dwpc"] + 6])
        if val is not None:
            ob["dwpf"] = normalize_temp(c2f(val))

    val = parse_packet(*tokens[dialect["alti_mb"] : dialect["alti_mb"] + 6])
    if val is not None:
        ob["alti"] = (MB * val).to(HG).m

    val = parse_packet(*tokens[dialect["mslp"] : dialect["mslp"] + 6])
    if val is not None:
        ob["mslp"] = val

    val = parse_packet(*tokens[dialect["drct"] : dialect["drct"] + 6])
    if val is not None:
        ob["drct"] = val

    val = parse_packet(*tokens[dialect["smps"] : dialect["smps"] + 6])
    if val is not None:
        ob["sknt"] = (MPS * val).to(KTS).m
        if ob["sknt"] == 0:
            ob["drct"] = 0

    val = parse_packet(*tokens[dialect["gmps"] : dialect["gmps"] + 6])
    if val is not None:
        ob["gust"] = (MPS * val).to(KTS).m

    val = parse_packet(*tokens[dialect["vsby_km"] : dialect["vsby_km"] + 6])
    if val is not None:
        ob["vsby"] = (KM * val).to(MILE).m
        if ob["vsby"] > 3:
            ob["vsby"] = round(ob["vsby"], 0)

    val = parse_packet(*tokens[dialect["p01m"] : dialect["p01m"] + 6])
    if val is not None:
        ob["hour"] = (MM * val).to(INCH).m

    for hr in [3, 6, 24]:
        val = parse_packet(
            *tokens[dialect[f"p{hr:02.0f}m"] : dialect[f"p{hr:02.0f}m"] + 6]
        )
        if val is not None:
            ob[f"p{hr:02.0f}i"] = (MM * val).to(INCH).m

    for i in range(1, 4):
        val = tokens[dialect[f"skyc{i}"]]
        if val not in [""] and val.find(":") > 0:
            ob[f"skyc{i}"] = val.split(":")[0]
        val = parse_packet(
            *tokens[dialect[f"skyl{i}"] : dialect[f"skyl{i}"] + 6]
        )
        if val is not None:
            ob[f"skyl{i}"] = int((M * val).to(FT).m)

    remark = tokens[dialect["remarks"]]
    if remark.find("SPECI") > 0:
        ob["raw"] = remark[remark.find("SPECI") :].split(";")[0]
    if remark.find("METAR") > 0:
        ob["raw"] = remark[remark.find("METAR") :].split(";")[0]

    wxcodes = []
    for i in range(1, 4):
        for src in ["mw", "au", "aw"]:
            val = tokens[dialect[f"pres_wx_{src}{i}"]]
            if val not in ["", "00", "9999"]:
                code = PRESWX_TO_METAR.get(
                    val,
                    val.split(":")[0],
                )
                if code not in wxcodes:
                    wxcodes.append(code)
    if wxcodes:
        ob["wxcodes"] = wxcodes

    return ob


def process_file(filename: str) -> Generator[dict]:
    """Process the provided file."""
    with open(filename) as fh:
        for linenum, line in enumerate(fh):
            if linenum == 0:
                dialect = build_dialect(line.strip().split("|"))
                continue
            yield process_line(line, dialect)


@click.command()
@click.option("--icao", required=True, help="ICAO Identifier")
def main(icao: str):
    """Go Main."""
    year = 1800
    station = icao if not icao.startswith("K") else icao[1:]
    iconn, icursor = get_dbconnc("iem")
    updates = 0
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            sql_helper("""
                select s.iemid, tzname, value as ghcnh_id from stations s
                JOIN station_attributes a on (s.iemid = a.iemid)
                where id = :station and network ~* 'ASOS' and attr = 'GHCNH_ID'
            """),
            {"station": station},
        )
        iemid, tzname, ghcnh_id = res.first()
    fn = f"GHCNh_{ghcnh_id}_por.psv"
    if not os.path.isfile(fn):
        subprocess.call(
            [
                "wget",
                (
                    "https://www.ncei.noaa.gov/oa/"
                    "global-historical-climatology-network/hourly/"
                    f"access/by-station/GHCNh_{ghcnh_id}_por.psv"
                ),
            ]
        )
    with get_sqlalchemy_conn("asos") as conn:
        for obdict in process_file(fn):
            obdict["station"] = icao

            if obdict["valid"].year != year:
                year = obdict["valid"].year
                table = f"t{year}"
                res = conn.execute(
                    sql_helper(
                        """
                    select to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI'),
                to_char((valid + '13 minutes'::interval) at time zone 'UTC',
                        'YYYYMMDDHH24') || '00'
                    from {table} WHERE station = :station
                    and report_type in (3, 4) ORDER by valid ASC
                """,
                        table=table,
                    ),
                    {"station": station},
                )
                dbhas = []
                for rr in res:
                    dbhas.append(rr[0])
                    # Ugliness with data not matching, so we are a bit more
                    # careful
                    if year >= 1996:
                        dbhas.append(rr[1])
                LOG.info("Found %s rows in %s", len(dbhas), table)
            if obdict["valid"].strftime("%Y%m%d%H%M") in dbhas:
                continue
            if obdict["raw"] is None or obdict["raw"].find(station) == -1:
                obdict["raw"] = metar_from_dict(obdict) + " IEM_GHCNH"
                if obdict["raw"].endswith("AUTO /////KT RMK AO2 IEM_GHCNH"):
                    continue
            LOG.info(
                "New %s[%s] %s",
                obdict["station"],
                obdict["valid"],
                obdict["raw"],
            )
            iemob = Observation(
                iemid=iemid, valid=obdict["valid"], tzname=tzname
            )
            iemob.data.update(obdict)
            iemob.save(icursor, force_current_log=True)
            updates += 1
            if updates % 100 == 0:
                icursor.close()
                iconn.commit()
                icursor = iconn.cursor()

        icursor.close()
        iconn.commit()
    os.unlink(fn)


if __name__ == "__main__":
    main()
