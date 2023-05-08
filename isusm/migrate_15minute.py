"""One time moving sm_15minute data to sm_minute."""

from psycopg2.extras import DictCursor

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger

LOG = logger()


def workflow(pgconn, cursor, station):
    """Do Work."""
    cursor.execute(
        "SELECT min(valid) from sm_minute where station = %s", (station,)
    )
    minvalid = cursor.fetchone()[0]

    # Fetch me all the sm_15minute data for this site
    df = read_sql(
        "SELECT * from sm_15minute where station = %s and valid < %s",
        pgconn,
        params=(station, minvalid),
    )
    df["slrkj_tot"] = df["slrkw_avg"] * 60.0
    df["rain_in_tot"] = df["rain_mm_tot"] / 25.4
    df["rain_in_2_tot"] = df["rain_mm_2_tot"] / 25.4
    df["ws_mph_s_wvt"] = df["ws_mps_s_wvt"] * 2.23694
    df = df.replace({pd.np.nan: "null"})
    LOG.info(
        "%s min valid: %s, rowcount: %s", station, minvalid, len(df.index)
    )
    for _, row in df.iterrows():
        cursor.execute(
            """
        INSERT into sm_minute(
            station, valid,
            tair_c_avg,  tair_c_avg_qc,
            rh_avg, rh_avg_qc,
            slrkj_tot, slrkj_tot_qc,
            rain_in_tot, rain_in_tot_qc,
            rain_in_2_tot, rain_in_2_tot_qc,
            tsoil_c_avg, tsoil_c_avg_qc,
            ws_mph_s_wvt,  ws_mph_s_wvt_qc,
            winddir_d1_wvt,  winddir_d1_wvt_qc,
            ws_mph_max, ws_mph_max_qc,
            calcvwc02_avg, calcvwc02_avg_qc,
            calcvwc04_avg, calcvwc04_avg_qc,
            calcvwc06_avg, calcvwc06_avg_qc,
            calcvwc08_avg, calcvwc08_avg_qc,
            calcvwc12_avg, calcvwc12_avg_qc,
            calcvwc16_avg, calcvwc16_avg_qc,
            calcvwc20_avg, calcvwc20_avg_qc,
            calcvwc24_avg, calcvwc24_avg_qc,
            calcvwc50_avg, calcvwc50_avg_qc,
            t02_c_avg, t02_c_avg_qc,
            t04_c_avg, t04_c_avg_qc,
            t08_c_avg, t08_c_avg_qc,
            t12_c_avg, t12_c_avg_qc,
            t16_c_avg, t16_c_avg_qc,
            t20_c_avg, t20_c_avg_qc,
            t24_c_avg, t24_c_avg_qc,
            t50_c_avg, t50_c_avg_qc,
            bp_mb, bp_mb_qc,
            lwmv_1, lwmv_1_qc,
            lwmdry_1_tot, lwmdry_1_tot_qc,
            lwmcon_1_tot, lwmcon_1_tot_qc,
            lwmwet_1_tot, lwmwet_1_tot_qc,
            lwmdry_lowbare_tot, lwmdry_lowbare_tot_qc,
            lwmcon_lowbare_tot, lwmcon_lowbare_tot_qc,
            lwmwet_lowbare_tot, lwmwet_lowbare_tot_qc,
            lwmv_2, lwmv_2_qc,
            lwmdry_2_tot, lwmdry_2_tot_qc,
            lwmcon_2_tot, lwmcon_2_tot_qc,
            lwmwet_2_tot, lwmwet_2_tot_qc,
            lwmdry_highbare_tot, lwmdry_highbare_tot_qc,
            lwmcon_highbare_tot, lwmcon_highbare_tot_qc,
            lwmwet_highbare_tot, lwmwet_highbare_tot_qc
        ) VALUES (
            '%(station)s', '%(valid)s',
            %(tair_c_avg)s, %(tair_c_avg_qc)s,
            %(rh)s, %(rh_qc)s,
            %(slrkj_tot)s, %(slrkj_tot)s,
            %(rain_in_tot)s, %(rain_in_tot)s,
            %(rain_in_2_tot)s, %(rain_in_2_tot)s,
            %(tsoil_c_avg)s, %(tsoil_c_avg_qc)s,
            %(ws_mph_s_wvt)s, %(ws_mph_s_wvt)s,
            %(winddir_d1_wvt)s, %(winddir_d1_wvt_qc)s,
            %(ws_mph_max)s, %(ws_mph_max_qc)s,
            %(vwc_06_avg)s, %(vwc_06_avg_qc)s,
            %(vwc_avg2in)s, %(vwc_avg2in_qc)s,
            %(vwc_avg4in)s, %(vwc_avg4in_qc)s,
            %(vwc_avg8in)s, %(vwc_avg8in_qc)s,
            coalesce(%(vwc_12_avg)s, %(calc_vwc_12_avg)s)::real,
            coalesce(%(vwc_12_avg_qc)s, %(calc_vwc_12_avg_qc)s)::real,
            %(vwc_avg16in)s, %(vwc_avg16in_qc)s,
            %(vwc_avg20in)s, %(vwc_avg20in_qc)s,
            coalesce(%(vwc_24_avg)s, %(calc_vwc_24_avg)s)::real,
            coalesce(%(vwc_24_avg_qc)s, %(calc_vwc_24_avg_qc)s)::real,
            coalesce(%(vwc_50_avg)s, %(calc_vwc_50_avg)s)::real,
            coalesce(%(vwc_50_avg_qc)s, %(calc_vwc_50_avg_qc)s)::real,
            %(temp_avg2in)s, %(temp_avg2in)s,
            %(temp_avg4in)s, %(temp_avg4in)s,
            %(temp_avg8in)s, %(temp_avg8in)s,
            %(t12_c_avg)s, %(t12_c_avg_qc)s,
            %(temp_avg16in)s, %(temp_avg16in)s,
            %(temp_avg20in)s, %(temp_avg20in)s,
            %(t24_c_avg)s, %(t24_c_avg_qc)s,
            %(t50_c_avg)s, %(t50_c_avg_qc)s,
            coalesce(%(bp_mb)s, %(bpres_avg)s)::real,
            coalesce(%(bp_mb_qc)s, %(bpres_avg_qc)s)::real,
            %(lwmv_1)s, %(lwmv_1_qc)s,
            %(lwmdry_1_tot)s, %(lwmdry_1_tot_qc)s,
            %(lwmcon_1_tot)s, %(lwmcon_1_tot_qc)s,
            %(lwmwet_1_tot)s, %(lwmwet_1_tot_qc)s,
            %(lwmdry_lowbare_tot)s, %(lwmdry_lowbare_tot_qc)s,
            %(lwmcon_lowbare_tot)s, %(lwmcon_lowbare_tot_qc)s,
            %(lwmwet_lowbare_tot)s, %(lwmwet_lowbare_tot_qc)s,
            %(lwmv_2)s, %(lwmv_2_qc)s,
            %(lwmdry_2_tot)s, %(lwmdry_2_tot_qc)s,
            %(lwmcon_2_tot)s, %(lwmcon_2_tot_qc)s,
            %(lwmwet_2_tot)s, %(lwmwet_2_tot_qc)s,
            %(lwmdry_highbare_tot)s, %(lwmdry_highbare_tot_qc)s,
            %(lwmcon_highbare_tot)s, %(lwmcon_highbare_tot_qc)s,
            %(lwmwet_highbare_tot)s, %(lwmwet_highbare_tot_qc)s
        )
        """
            % row
        )


def main():
    """Go Main Go."""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    stations = []
    cursor.execute("SELECT distinct station from sm_15minute")
    for row in cursor:
        stations.append(row[0])
    cursor.close()
    for station in stations:
        cursor = pgconn.cursor(cursor_factory=DictCursor)
        workflow(pgconn, cursor, station)
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
