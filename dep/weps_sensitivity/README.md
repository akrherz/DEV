# WEPS sensitivity work (read: figure out what is wrong with our files)

We presently have an opaque issue of not being sure if our cobbled together
input files are doing what we are hoping they do.  So a sensitivity test seems
like a good place to start to see if we can isolate if zero erosion runs are
real or not.  My current procedural thought is to run a large matrix of various
file combinations, collate the results into a simple CSV table that can be
futher analyzed.

## Variable importance ranking

Use `sensitivity_importance.py` to rank which input columns are most important
for explaining `erosion_tayr` (or another target column).

```bash
cd dep/weps_sensitivity
python sensitivity_importance.py
```

Default behavior:

- Reads `results.csv`
- Drops `man_file == 090203090201_758.man`
- Excludes derived WEPS output columns (for example `spring_erosion_tayr`)
- Excludes file-ID/meta columns (for example `soil_file`)
- Writes ranked output to `sensitivity_importance.csv`

Useful options:

```bash
# Different target
python sensitivity_importance.py --target pm10_tayr --output pm10_importance.csv

# Keep meta columns in the ranking
python sensitivity_importance.py --include-meta-columns

# Keep derived output columns (usually not recommended)
python sensitivity_importance.py --include-derived-output-columns
```
