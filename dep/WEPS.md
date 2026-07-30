# Surf_H20 investigation

Having issues with the Surf_H2O variable indicating that the runs are rarely
drying out, so being restrictive of erosion events. Hourly surface water is
defined as:

    bhrwc0(hourstep) = theta(0)/bulkden(1)

where theta(0) is:

    theta(0) = calctht0(bszlyd, theta, dvwp(isr)%thetaw, evapratio)

- bszlyd : Depth of layers
- theta: water content
- dvwp: volumetic water content
- evapratio: ratio reduction in evaporation rate due to soil dryness

where:

    evapratio = evapredu( surf_cum, evaplimit, vaptrans, bhzep )

We find that evaporation reduction is almost always 1, hard coding it to 0.01
helps Surf_H20 behave.  Reported to the [dailyerosion/weps#24](https://github.com/dailyerosion/weps/issues/24).
