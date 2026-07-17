"""Rank feature sensitivity for WEPS outputs.

This script trains a random-forest regressor and computes grouped permutation
importance by shuffling one original input column at a time.
"""

import argparse
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

OUTPUT_LIKE_COLUMNS = {
    "erosion_tayr",
    "spring_erosion_tayr",
    "fall_erosion_tayr",
    "suspension_tayr",
    "spring_suspension_tayr",
    "fall_suspension_tayr",
    "pm10_tayr",
    "spring_pm10_tayr",
    "fall_pm10_tayr",
    "saltation_tayr",
    "spring_saltation_tayr",
    "fall_saltation_tayr",
}

META_LIKE_COLUMNS = {
    "fpath",
    "man_file",
    "climate_file",
    "wind_file",
    "soil_file",
}


def shuffled_importance(
    pipe: Pipeline,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    repeats: int,
    seed: int,
) -> pd.DataFrame:
    """Return grouped permutation importance by original column."""
    rng = np.random.default_rng(seed)
    baseline = pipe.score(x_test, y_test)
    rows: list[dict[str, float | str]] = []

    for col in x_test.columns:
        drops: list[float] = []
        for _ in range(repeats):
            xp = x_test.copy()
            xp[col] = (
                xp[col]
                .sample(
                    frac=1.0,
                    replace=False,
                    random_state=int(rng.integers(0, 1_000_000)),
                )
                .values
            )
            drops.append(baseline - pipe.score(xp, y_test))
        rows.append(
            {
                "feature": col,
                "importance_mean": float(np.mean(drops)),
                "importance_std": float(np.std(drops)),
            }
        )

    df = pd.DataFrame(rows).sort_values("importance_mean", ascending=False)
    positive_sum = max(df["importance_mean"].clip(lower=0).sum(), 1e-12)
    df["importance_share_pct"] = (
        df["importance_mean"].clip(lower=0) / positive_sum * 100.0
    )
    df.insert(0, "rank", np.arange(1, len(df.index) + 1))
    return df


def parse_args() -> argparse.Namespace:
    """Build and parse CLI args."""
    parser = argparse.ArgumentParser(
        description=(
            "Compute feature sensitivity ranking for WEPS output columns."
        ),
    )
    parser.add_argument(
        "--input",
        default="results.csv",
        help="Input CSV file.",
    )
    parser.add_argument(
        "--output",
        default="sensitivity_importance.csv",
        help="Output CSV path for ranked sensitivities.",
    )
    parser.add_argument(
        "--target",
        default="erosion_tayr",
        help="Target column to explain.",
    )
    parser.add_argument(
        "--test-size",
        default=0.25,
        type=float,
        help="Fraction of rows for the test split.",
    )
    parser.add_argument(
        "--random-seed",
        default=42,
        type=int,
        help="Random seed for split, model, and permutations.",
    )
    parser.add_argument(
        "--n-estimators",
        default=400,
        type=int,
        help="Number of trees in random forest.",
    )
    parser.add_argument(
        "--min-samples-leaf",
        default=2,
        type=int,
        help="Random forest min_samples_leaf.",
    )
    parser.add_argument(
        "--perm-repeats",
        default=10,
        type=int,
        help="How many shuffle repeats per column.",
    )
    parser.add_argument(
        "--exclude-columns",
        default="",
        help="Comma-separated additional columns to exclude.",
    )
    parser.add_argument(
        "--drop-man-file",
        default="090203090201_758.man",
        help=(
            "Optional man_file value to drop. Set to empty string to disable."
        ),
    )
    parser.add_argument(
        "--include-meta-columns",
        action="store_true",
        help="Include file-ID/meta columns (man_file, climate_file, ...).",
    )
    parser.add_argument(
        "--include-derived-output-columns",
        action="store_true",
        help="Include other WEPS output columns; usually not recommended.",
    )
    parser.add_argument(
        "--top-n",
        default=20,
        type=int,
        help="How many top rows to print to stdout.",
    )
    return parser.parse_args()


def parse_exclusions(raw: str) -> set[str]:
    """Parse comma-delimited exclusion list."""
    if not raw.strip():
        return set()
    return {token.strip() for token in raw.split(",") if token.strip()}


def build_feature_columns(
    all_columns: Iterable[str],
    target: str,
    include_meta: bool,
    include_derived_outputs: bool,
    extra_exclusions: set[str],
) -> list[str]:
    """Select model feature columns from available columns."""
    excluded = {target} | extra_exclusions
    if not include_meta:
        excluded |= META_LIKE_COLUMNS
    if not include_derived_outputs:
        excluded |= OUTPUT_LIKE_COLUMNS
    return [col for col in all_columns if col not in excluded]


def main():
    """Go main."""
    args = parse_args()
    df = pd.read_csv(args.input)

    if args.drop_man_file and "man_file" in df.columns:
        df = df[df["man_file"] != args.drop_man_file].copy()

    if args.target not in df.columns:
        msg = f"Target column '{args.target}' not found in {args.input}."
        raise ValueError(msg)

    feature_cols = build_feature_columns(
        df.columns,
        target=args.target,
        include_meta=args.include_meta_columns,
        include_derived_outputs=args.include_derived_output_columns,
        extra_exclusions=parse_exclusions(args.exclude_columns),
    )
    if not feature_cols:
        raise ValueError("No feature columns remain after exclusions.")

    x = df[feature_cols]
    y = df[args.target]

    numeric_cols = x.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_cols = [col for col in x.columns if col not in numeric_cols]

    pre = ColumnTransformer(
        [
            (
                "num",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                numeric_cols,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                sparse_output=False,
                            ),
                        ),
                    ]
                ),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )

    pipe = Pipeline(
        [
            ("pre", pre),
            (
                "rf",
                RandomForestRegressor(
                    n_estimators=args.n_estimators,
                    random_state=args.random_seed,
                    n_jobs=-1,
                    min_samples_leaf=args.min_samples_leaf,
                ),
            ),
        ]
    )

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=args.test_size,
        random_state=args.random_seed,
    )
    pipe.fit(x_train, y_train)
    r2 = pipe.score(x_test, y_test)

    importance_df = shuffled_importance(
        pipe,
        x_test,
        y_test,
        repeats=args.perm_repeats,
        seed=args.random_seed,
    )
    importance_df.to_csv(args.output, index=False)

    print(f"Rows used: {len(df.index)}")
    print(f"Target: {args.target}")
    print(f"Test R2: {r2:.4f}")
    print(f"Wrote: {args.output}")
    print("")
    print("Top features:")
    view = importance_df.head(args.top_n)
    for _, row in view.iterrows():
        print(
            f"{int(row['rank']):2d}. {row['feature']:30s} "
            f"mean={row['importance_mean']:.5f} "
            f"std={row['importance_std']:.5f} "
            f"share={row['importance_share_pct']:.2f}%"
        )


if __name__ == "__main__":
    main()
