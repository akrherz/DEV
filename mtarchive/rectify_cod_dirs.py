"""
Attempt to recitfy older COD satellite directories.
"""

import os
from datetime import datetime
from pathlib import Path

import click
from pyiem.util import logger

GOOD_DIR_NAMES = "continental,global,meso,regional,subregional".split(",")
LOG = logger()
MOVE_TO_REGIONAL = {
    "ca_baffin",
    "ca_lksuper",
    "ca_reg_east",
    "ca_reg_west",
    "eastcoast",
    "northcentral",
    "northmexico",
    "nwatlantic",
    "southcentral",
    "southmexico",
    "watlantic",
    "ca_bakerlk",
    "ca_reg_cen",
    "ca_Regina",
    "central",
    "gulf",
    "midwest",
    "northeast",
    "northwest",
    "prregiona",
    "southeast",
    "southwest",
}
MOVE_TO_SUBREGIONAL = {
    "Bahamas",
    "Bootheel",
    "ca_gulf_stl",
    "ca_nl",
    "Carolinas",
    "ca_ungava",
    "Cuba",
    "E_Antilles",
    "Greater_Antilles",
    "MI",
    "N_Iowa",
    "N_Tier",
    "S_Plains",
    "Virginias",
    "Baja",
    "ca_c_quebec",
    "Cali_Gulf",
    "ca_n_mb_sk",
    "ca_s_bc",
    "Cen_Plains",
    "Desert_SW",
    "E_Caribbean",
    "HEADER.html",
    "Mid_Atlantic",
    "N_Plains",
    "NW_Plains",
    "OH_RV",
    "S_SK",
    "W_Caribbean",
    "Bermuda",
    "ca_edmonton",
    "ca_n_alberta",
    "ca_n_ontario",
    "ca_s_mb_sk",
    "Cen_Rockies",
    "Dixie",
    "E_Gulf_Coast",
    "IL",
    "New_England",
    "Nrn_Mo",
    "Quebec",
    "St_Lawrence",
    "W_Gulf_Coast",
    "Big_Bend",
    "ca_ern_nl",
    "ca_n_bc",
    "ca_n_quebec",
    "ca_s_ontario",
    "CO_KS_PanHan",
    "Durango",
    "Florida",
    "Mexico_City",
    "NE_WY",
    "N_Rockies",
    "S_PanHandle",
    "Texas",
    "Yucatan",
    "Michigan",
    "N_Nevada",
    "Pac_NW",
    "Sierra",
    "Alabama",
    "Arizona",
    "Arkansas",
    "Black_Hills",
    "Brownsville",
    "Cabo",
    "Campeche",
    "Carolina",
    "Cayman",
    "Cen_California",
    "Cen_Texas",
    "Chihuahua",
    "Colorado",
    "E_Washington",
    "FL_Panhandle",
    "Four_Corners",
    "Gulf_Stream",
    "Hatteras",
    "Havana",
    "Hispaniola",
    "Houston",
    "Iowa",
    "Jacksonville",
    "Jamaica",
    "Kansas",
    "Kentucky",
    "LakeErie",
    "LakeHuron",
    "LakeOntario",
    "LakeSuperior",
    "Mid_Baja",
    "Mississippi",
    "N_California",
    "N_Dakota",
    "Nebraska",
    "NE_Colorado",
    "NE_Montana",
    "NE_Oregon",
    "NE_Texas",
    "Nevada",
    "New_Brunswick",
    "Newfoundland",
    "New_Jersey",
    "New_Orleans",
    "N_Illinois",
    "N_Minnesota",
    "N_New_Mexico",
    "Nova_Scotia",
    "Ohio",
    "Oklahoma",
    "Ottawa",
    "Panhandle",
    "Pennsylvania",
    "Portland",
    "PuertoRico",
    "Rhode_Island",
    "Salt_Lake",
    "S_California",
    "S_Dakota",
    "Seattle",
    "SE_Coast",
    "SE_Colorado",
    "SE_Montana",
    "SE_Ontario",
    "Serranias_del_Burro",
    "S_Florida",
    "S_Idaho",
    "S_Illinois",
    "S_Maine",
    "S_Minnesota",
    "Sonora",
    "S_Oregon",
    "SW_Missouri",
    "SW_Texas",
    "SW_Utah",
    "Tahoe",
    "Tennessee",
    "Tri_State",
    "Turks_and_Caicos",
    "UP",
    "Virginia",
    "White_Sands",
    "Wisconsin",
    "W_Montana",
    "W_Virginia",
    "Wyoming",
    "Yellowstone",
    "Regina",
    "Brandon",
    "Nuevo_Leon",
    "Calgary",
    "Cozumel",
    "Kelowna",
    "Winnipeg",
    "Wichita_Falls",
    "Austin",
    "Vermont",
    "N_Louisiana",
    "NC_VA",
    "Georgia",
    "Phoenix",
    "Orlando",
    "N_Mississippi",
    "Indiana",
    "ca_stjohns",
    "S_British_Columbia",
    "BristolBay",
    "Fairbanks",
    "HIzoom",
}


def rectify_move(src_dir, dest_dir):
    """Do some protected moving."""
    final_dest = f"{dest_dir}/{src_dir}"
    if os.path.isdir(final_dest):
        LOG.info("Rut roh, final %s exists, doing rsync", final_dest)
        os.system(f"rsync -a --remove-source-files {src_dir} {dest_dir}/")
        os.system(f"rm -rf {src_dir}")
        return
    LOG.info("Renaming %s to %s", src_dir, final_dest)
    os.makedirs(dest_dir, exist_ok=True)
    os.rename(src_dir, final_dest)


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
@click.option("--rootdir", type=str, default="/isu/mtarchive/data")
def main(dt: datetime, rootdir: str):
    """Go Main Go."""
    dt = dt.date()
    LOG.info("Processing %s", dt)
    basedir = Path(f"{rootdir}/{dt:%Y}/{dt:%m}/{dt:%d}/cod/sat")
    if not basedir.exists():
        LOG.warning("Directory %s does not exist, exiting", basedir)
        return

    # Change to the directory
    os.chdir(basedir)

    unknowns = []

    # List out all folders here, they should be in the form of goes**
    for entry in basedir.iterdir():
        if not entry.is_dir():
            continue
        goesdirname = entry.name
        if not goesdirname.startswith("goes"):
            LOG.info("Skipping non-goes directory %s", goesdirname)
            continue
        os.chdir(goesdirname)
        # Again, find all directories in cwd
        for subentry in Path(".").iterdir():
            if not subentry.is_dir():
                continue
            candidate = subentry.name
            # Nothing to do here
            if candidate in GOOD_DIR_NAMES:
                continue
            if candidate in MOVE_TO_REGIONAL:
                rectify_move(candidate, "regional")
            elif candidate in MOVE_TO_SUBREGIONAL:
                rectify_move(candidate, "subregional")
            else:
                LOG.warning(
                    "Unknown directory %s/%s",
                    goesdirname,
                    candidate,
                )
                unknowns.append(candidate)
        os.chdir("..")

    print(repr(unknowns))


if __name__ == "__main__":
    main()
