"""Regression tests for cross-chart methodology consistency.

The original bug: the "Methodology Deep Dive" treemap folded
"deep learning"/"neural" INSIDE the "Machine Learning" bucket, contradicting
the pie/bar which separate "Deep Learning" from "Shallow ML".

These tests build one deterministic 15-row fixture and prove that the pie/bar
data path and the treemap data path resolve to the same MECE membership —
``dict[label -> frozenset(acronyms)]`` — matching the canonical target.
"""

import pandas as pd
import pytest

from dashboard.components.initiative_analysis.charts.comparison import (
    methodology_deepdive_component as deepdive,
)
from dashboard.components.shared.methodology_taxonomy import (
    LEAVES,
    membership,
    present_leaves,
)

# Canonical fixture: 15 initiatives, mirroring the real dataset distribution.
# ``Methodology`` is the canonical leaf column; ``Classification Method`` is
# the free text the SSoT rule engine classifies.
FIXTURE_ROWS = [
    ("CGLS", "Shallow ML", "Supervised Random Forest"),
    ("GDW", "Deep Learning", "Deep Learning"),
    ("ESRI-10m LULC", "Deep Learning", "Convolutional Neural Network"),
    ("UMD-GLC", "Hybrid", "Decision/Regression Trees and U-Net CNN"),
    ("GPW", "Shallow ML", "Supervised Machine Learning"),
    ("UMD-SASM", "Hybrid", "Regression, Visual Interpretation, and Decision Trees"),
    ("ESA-WC", "Shallow ML", "Gradient Boosting Decision Tree Algorithm"),
    ("WorldCereal", "Shallow ML", "Gradient Boosting on decision trees"),
    ("PRODES", "Visual Interpretation", "Visual Interpretation"),
    ("DETER", "Hybrid", "Visual Interpretation and Spectral Mixture Model"),
    (
        "TerraClass Amazon",
        "Hybrid",
        "Visual Interpretation, Supervised Bhattacharya Classification, and Deep Learning",
    ),
    (
        "TerraClass Cerrado",
        "Hybrid",
        "Visual Interpretation, Supervised Bhattacharya Classification, and Deep Learning",
    ),
    ("MapBiomas", "Hybrid", "Supervised Random Forest and Deep Learning"),
    ("IBGE-MLCU", "Visual Interpretation", "Visual Interpretation"),
    (
        "CONAB-AM",
        "Hybrid",
        "Machine Learning, Statistical Methods, Visual Interpretation",
    ),
]

#: The four non-empty leaves, as ``dict[label -> frozenset(acronyms)]``.
TARGET_MEMBERSHIP = {
    "Shallow ML": frozenset({"CGLS", "GPW", "ESA-WC", "WorldCereal"}),
    "Deep Learning": frozenset({"GDW", "ESRI-10m LULC"}),
    "Hybrid": frozenset(
        {
            "UMD-GLC",
            "UMD-SASM",
            "DETER",
            "TerraClass Amazon",
            "TerraClass Cerrado",
            "MapBiomas",
            "CONAB-AM",
        }
    ),
    "Visual Interpretation": frozenset({"PRODES", "IBGE-MLCU"}),
}

TARGET_COUNTS = {
    "Shallow ML": 4,
    "Deep Learning": 2,
    "Hybrid": 7,
    "Visual Interpretation": 2,
    "Statistical / Spectral": 0,
}


@pytest.fixture
def fixture_df() -> pd.DataFrame:
    """Deterministic 15-row frame with canonical + free-text methodology."""
    return pd.DataFrame(
        FIXTURE_ROWS, columns=["Acronym", "Methodology", "Classification Method"]
    )


def test_fixture_shape_and_leaves(fixture_df):
    assert len(fixture_df) == 15
    assert set(fixture_df["Methodology"]).issubset(set(LEAVES))


def test_pie_bar_treemap_membership_agree(fixture_df):
    """The regression test for the pie/bar vs treemap contradiction.

    Exercises three DISTINCT code paths (not the same function three times):
    the pie path (canonical frame -> SSoT membership), the bar path (SSoT
    counts) and the treemap path (`categorize_methodologies` over the
    DataFrame). If the treemap re-folded Deep Learning into a "Machine
    Learning" bucket, the treemap keys would diverge from the pie/bar
    membership and this test fails.
    """
    # Pie path: canonical frame through the SSoT membership drill-down.
    pie_membership = membership(deepdive.methodology_distribution_frame(fixture_df))
    assert pie_membership == TARGET_MEMBERSHIP

    # Bar path: independent count aggregation; positive counts must match the
    # membership sizes leaf-by-leaf.
    expected_sizes = {leaf: len(acronyms) for leaf, acronyms in pie_membership.items()}
    bar_counts = deepdive.methodology_counts(fixture_df)
    assert {leaf: n for leaf, n in bar_counts.items() if n} == expected_sizes

    # Treemap path: its own aggregation function over the DataFrame.
    treemap_counts = deepdive.categorize_methodologies(fixture_df)
    assert {leaf: n for leaf, n in treemap_counts.items() if n} == expected_sizes

    # The original bug guard: Deep Learning stays its own leaf.
    assert treemap_counts["Deep Learning"] == len(pie_membership["Deep Learning"])
    assert "Machine Learning" not in treemap_counts


def test_membership_equals_target_mapping(fixture_df):
    """Drill-down membership (all five leaves, empties as empty frozensets)."""
    resolved = deepdive.methodology_membership(fixture_df)
    assert set(resolved) == set(LEAVES)
    assert resolved == {
        **TARGET_MEMBERSHIP,
        "Statistical / Spectral": frozenset(),
    }


def test_counts_and_treemap_path_agree(fixture_df):
    """Both paths expose the full five-leaf shape, zero-count leaves included."""
    counts = deepdive.methodology_counts(fixture_df)
    treemap = deepdive.categorize_methodologies(fixture_df)
    assert counts == treemap == TARGET_COUNTS
    assert set(counts) == set(LEAVES)
    assert counts["Statistical / Spectral"] == 0


def test_treemap_keeps_deep_learning_separate_from_shallow_ml(fixture_df):
    """The original bug: DL must NOT be folded into a 'Machine Learning' bucket."""
    counts = deepdive.categorize_methodologies(fixture_df)

    assert counts["Deep Learning"] == 2
    assert counts["Shallow ML"] == 4
    assert counts["Deep Learning"] != counts["Shallow ML"]
    # No legacy coarse bucket may survive.
    assert "Machine Learning" not in counts
    assert "Other" not in counts
    assert set(counts) == set(LEAVES)


def test_display_omits_zero_count_leaves(fixture_df):
    """Only present leaves are rendered; reserve leaves stay in the model."""
    counts = deepdive.categorize_methodologies(fixture_df)

    assert present_leaves(counts) == (
        "Shallow ML",
        "Deep Learning",
        "Hybrid",
        "Visual Interpretation",
    )
    assert "Statistical / Spectral" not in present_leaves(counts)
    # The engine/taxonomy contract is unchanged: all five leaves are retained.
    assert set(counts) == set(LEAVES)


def test_categorize_methodologies_list_keeps_deep_learning_apart():
    """Points directly at the removed local keyword dict."""
    counts = deepdive.categorize_methodologies(["Deep Learning", "neural networks"])

    assert counts["Deep Learning"] == 2
    assert counts["Shallow ML"] == 0
    assert "Machine Learning" not in counts
