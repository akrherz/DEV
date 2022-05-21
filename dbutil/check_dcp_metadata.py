"""Do some self diagnostics on NWSLI / DCP metadata"""
from pyiem.reference import nwsli2country, nwsli2state
from pyiem.util import get_dbconn


def main():
    """Go Main"""
    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()

    cursor.execute(
        "SELECT id, state, country, network from stations "
        "WHERE network ~* 'DCP' and length(id) = 5"
    )

    for row in cursor:
        nwsli = row[0]
        # only care about digits
        if not nwsli[-1].isdigit():
            continue
        state = row[1]
        country = row[2]
        network = row[3]
        code = nwsli[-2:]

        country2 = nwsli2country.get(code)
        if country != country2:
            print(
                f"ID:{nwsli} ST:{state} C:{country} NET:{network} "
                f"L_C:{country2}"
            )
        network2 = f"{state}_DCP"
        if country in ["MX", "CA"]:
            network2 = f"{country}_{state}_DCP"
        elif country not in ["MX", "CA", "US"]:
            network2 = f"{country}__DCP"
        if network != network2:
            print(
                f"ID:{nwsli} ST:{state} C:{country} NET:{network} "
                f"L_N:{network2}"
            )

        state2 = nwsli2state.get(code)
        if state is not None and state != state2:
            print(
                f"ID:{nwsli} ST:{state} C:{country} NET:{network} "
                f"L_S:{state2}"
            )


if __name__ == "__main__":
    main()
