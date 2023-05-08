from eccodes import (
    CodesInternalError,
    codes_bufr_new_from_file,
    codes_get,
    codes_release,
    codes_set,
)


def main():
    """Try things."""
    keys = [
        "blockNumber",
        "stationNumber",
        "latitude",
        "longitude",
        "airTemperatureAt2M",
        "dewpointTemperatureAt2M",
        "windSpeedAt10M",
        "windDirectionAt10M",
        "#1#cloudAmount",  # cloud amount (low and mid level)
        "#1#heightOfBaseOfCloud",
        "#1#cloudType",  # cloud type (low clouds)
        "#2#cloudType",  # cloud type (middle clouds)
        "#3#cloudType",  # cloud type (highclouds)
    ]
    with open("ob", "rb") as fh:
        while True:
            bufr = codes_bufr_new_from_file(fh)
            if bufr is None:
                break
            codes_set(bufr, "unpack", 1)

            # print the values for the selected keys from the message
            for key in keys:
                try:
                    print("  %s: %s" % (key, codes_get(bufr, key)))
                except CodesInternalError:
                    pass
            """
            # get BUFR key iterator
            iterid = codes_bufr_keys_iterator_new(bufr)
    
            # loop over the keys
            while codes_bufr_keys_iterator_next(iterid):
                # print key name
                keyname = codes_bufr_keys_iterator_get_name(iterid)
                if keyname == "subsetNumber":
                    subset += 1
                    print("  Subset: %d" % subset)
                else:
                    try:
                        print(f"  {keyname} -> {codes_get(bufr, keyname)}")
                    except:
                        pass

            # delete the key iterator
            codes_bufr_keys_iterator_delete(iterid)
            """
            # delete handle
            codes_release(bufr)


if __name__ == "__main__":
    main()
