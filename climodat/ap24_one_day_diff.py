"""A one off, as per the usual."""

import pandas as pd
from pyiem.plot import figure


def main():
    """Go Main Go."""
    ncei_sep = pd.read_csv(
        "http://iem.local/plotting/auto/plot/24/which:cd::"
        "csector:midwest::var:precip::w:rank::p:day::year:2026::month:9::"
        "sdate:2026-09-01::edate:2026-09-30::cmap:BrBG_r::_r:t::dpi:100.csv"
    ).set_index("station")
    sep = pd.read_csv(
        "http://iem.local/plotting/auto/plot/24/which:cd::"
        "csector:midwest::var:precip::w:rank::p:day::year:2026::month:9::"
        "sdate:2026-09-02::edate:2026-10-01::cmap:BrBG_r::_r:t::dpi:100.csv"
    ).set_index("station")

    combined = pd.merge(
        ncei_sep,
        sep,
        left_index=True,
        right_index=True,
        suffixes=("_ncei", "_sep"),
    )
    combined["state"] = combined.index.to_series().str[:2]
    combined["rank_delta"] = (
        combined["precip_rank_ncei"] - combined["precip_rank_sep"]
    )
    combined = combined.sort_values("rank_delta")
    print(
        combined[
            [
                "precip_val_ncei",
                "precip_rank_ncei",
                "precip_val_sep",
                "precip_rank_sep",
                "rank_delta",
            ]
        ]
    )

    iowa = combined[combined["state"] == "IA"]
    print(
        iowa[
            [
                "precip_val_ncei",
                "precip_rank_ncei",
                "precip_val_sep",
                "precip_rank_sep",
                "rank_delta",
            ]
        ]
    )

    # Make a plot
    fig = figure(
        title="Impact of One Day Accounting Difference on Sep Precip Rank",
        subtitle=(
            "Based on unofficial IEM climate district data for contiguous US, "
            "1 is wettest since 1893."
        ),
        figsize=(10.24, 7.68),
    )

    fig.text(
        0.1,
        0.87,
        "'1-30 Sep' is ~7 AM 31 August till ~7 AM 30 September (standard)",
        ha="left",
        va="top",
        fontsize=12,
    )
    fig.text(
        0.1,
        0.84,
        "'2 Sep-1 Oct' is ~7 AM 1 September till ~7 AM 1 October",
        ha="left",
        va="top",
        fontsize=12,
    )

    cols = [
        "name_ncei",
        "precip_val_ncei",
        "precip_rank_ncei",
        "precip_val_sep",
        "precip_rank_sep",
        "rank_delta",
    ]
    headers = [
        "ID",
        "Name",
        "1-30 Sep\nTotal",
        "1-30 Sep\nRank",
        "2 Sep-1 Oct\nTotal",
        "2 Sep-1 Oct\nRank",
        "Rank Change",
    ]

    def fmt(idx, row):
        rank_delta = f"{row['rank_delta']:+.0f}"
        if rank_delta == "+0":
            rank_delta = "0"
        return [
            str(idx),
            str(row["name_ncei"]),
            f"{row['precip_val_ncei']:.2f}",
            f"{row['precip_rank_ncei']:.0f}",
            f"{row['precip_val_sep']:.2f}",
            f"{row['precip_rank_sep']:.0f}",
            rank_delta,
        ]

    cells = []
    colors = []
    sections = [
        ("Top 5 Decreases in Rank", combined.head(5), "#e8f0fe"),
        ("Bottom 5 Increases in Rank", combined.tail(5), "#fde8e8"),
        ("Iowa", iowa, "#e8f5e9"),
    ]
    for label, df, color in sections:
        cells.append([""] + [label] + [""] * 5)
        colors.append("#cccccc")
        for idx, row in df[cols].iterrows():
            cells.append(fmt(idx, row))
            colors.append(color)

    ax = fig.add_axes((0.03, 0.03, 0.94, 0.78))
    ax.axis("off")
    table = ax.table(
        cellText=cells,
        colLabels=headers,
        cellColours=[[c] * 7 for c in colors],
        colColours=["#999999"] * 7,
        colWidths=[0.08, 0.36, 0.11, 0.11, 0.11, 0.11, 0.11],
        loc="upper center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.3)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold", color="white")
            cell.set_height(cell.get_height() * 2)
        elif cells[row - 1][1:] == [""] * 6:
            cell.set_text_props(weight="bold")
            cell.visible_edges = "TB"
            cell.set_facecolor("none")
            if col == 0:
                cell._loc = "left"
        if col == 1 and row > 0:
            cell._loc = "left"
            cell.PAD = 0.03

    fig.savefig("261006.png")


if __name__ == "__main__":
    main()
