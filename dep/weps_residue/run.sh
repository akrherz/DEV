#!/bin/bash

rm -f weps.runx

# c0 don't produce soil conditioning output
# -E1 we want to model erosion here
# -W1 avoid expensive calculation
/opt/dep/bin/weps_dep -c0 -E1 -e0 -H0 -i3 -I0 -n0 -o12052026 -t0 -T0 -W0 -u0

python process_plot.py --var1=ne_wzzo --var2=ne_sfcv

