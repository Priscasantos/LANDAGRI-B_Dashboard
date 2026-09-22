"""Tests for the single source of truth methodology taxonomy.

These tests pin the normative rule engine: normalisation, longest-match-first
with span consumption, and the MECE label decision (0 -> None,
1 -> that leaf, >=2 -> Hybrid).
"""

import dataclasses

import pandas as pd
import pytest

from dashboard.components.shared.methodology_taxonomy import (
    HYBRID,
    LEAVES,
    METHODOLOGY_COLORS,
    TERM_FAMILIES,
    MethodologyResult,
    classify,
    label_counts,
    match_families,
    normalize,
    present_leaves,
)


class TestLeafVocabulary:
    def test_leaves_are_the_five_mece_buckets(self):
        assert LEAVES == (
            "Shallow ML",
            "Deep Learning",
            "Hybrid",
            "Visual Interpretation",
            "Statistical / Spectral",
        )

    def test_every_leaf_has_a_color(self):
        assert set(METHODOLOGY_COLORS) == set(LEAVES)

    def test_term_families_are_normalised_and_known_leaves(self):
        families = {
            "Shallow ML",
            "Deep Learning",
            "Visual Interpretation",
            "Statistical / Spectral",
        }
        assert set(TERM_FAMILIES) >= families
        for _family, terms in TERM_FAMILIES.items():
            for term in terms:
                assert term == normalize(term), f"{term!r} is not normalised"


class TestNormalize:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("U-Net", "u net"),
            ("k-Nearest", "k nearest"),
            ("  Deep   Learning, CNN  ", "deep learning cnn"),
            (None, ""),
            ("", ""),
        ],
    )
    def test_normalize(self, raw, expected):
        assert normalize(raw) == expected


class TestClassify:
    def test_supervised_random_forest_and_deep_learning_is_hybrid(self):
        result = classify("Supervised Random Forest and Deep Learning")
        assert result.label == HYBRID
        assert result.families == {"Shallow ML", "Deep Learning"}

    def test_statistical_methods_is_statistical(self):
        assert classify("Statistical Methods").label == "Statistical / Spectral"

    def test_cnn_plus_visual_interpretation_is_hybrid(self):
        result = classify("CNN + visual interpretation")
        assert result.label == HYBRID
        assert result.families == {"Deep Learning", "Visual Interpretation"}

    def test_machine_learning_is_shallow_ml(self):
        assert classify("Machine Learning").label == "Shallow ML"

    @pytest.mark.parametrize("raw", ["", None, "   "])
    def test_empty_input_has_no_label(self, raw):
        result = classify(raw)
        assert result.label is None
        assert result.families == frozenset()
        assert result.matched_terms == ()

    def test_combined_is_not_a_dictionary_term(self):
        assert classify("Combined").label is None

    def test_hybrid_and_combined_words_are_not_dictionary_terms(self):
        assert classify("Hybrid").label is None
        assert classify("combined methods").label is None

    def test_gradient_boosting_on_decision_trees_is_shallow_only(self):
        result = classify("Gradient Boosting on decision trees")
        assert result.label == "Shallow ML"
        assert "Statistical / Spectral" not in result.families

    def test_regression_tree_span_suppression(self):
        result = classify("regression tree")
        assert result.label == "Shallow ML"
        assert result.families == frozenset({"Shallow ML"})
        assert result.matched_terms == ("regression tree",)

    def test_decision_trees_win_over_decision_tree(self):
        result = classify("decision trees")
        assert result.families == frozenset({"Shallow ML"})
        assert result.matched_terms == ("decision trees",)

    @pytest.mark.parametrize(
        ("raw", "label"),
        [
            ("U-Net", "Deep Learning"),
            ("u-net convolutional", "Deep Learning"),
            ("k-Nearest Neighbors", "Shallow ML"),
            ("Random Forest", "Shallow ML"),
            ("Bhattacharya classification", "Statistical / Spectral"),
        ],
    )
    def test_normalisation_variants(self, raw, label):
        assert classify(raw).label == label

    def test_result_is_frozen_dataclass_and_keeps_raw(self):
        result = classify("Deep Learning")
        assert isinstance(result, MethodologyResult)
        assert dataclasses.is_dataclass(result)
        assert result.raw == "Deep Learning"
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.label = "Shallow ML"  # type: ignore[misc]

    def test_match_families_returns_components_and_terms(self):
        families, terms = match_families("Visual Interpretation and Spectral Mixture")
        assert families == {"Visual Interpretation", "Statistical / Spectral"}
        assert set(terms) == {"visual interpretation", "spectral mixture"}


class TestSharedAggregationPath:
    def test_label_counts_from_series(self):
        series = pd.Series(
            [
                "Supervised Random Forest and Deep Learning",
                "Machine Learning",
                "Deep Learning",
            ]
        )
        assert label_counts(series)["Hybrid"] == 1
        assert label_counts(series)["Shallow ML"] == 1
        assert label_counts(series)["Deep Learning"] == 1

    def test_label_counts_from_dataframe_uses_classification_method(self):
        frame = pd.DataFrame(
            {
                "Name": ["a", "b"],
                "Classification Method": ["Machine Learning", "Deep Learning"],
            }
        )
        assert label_counts(frame) == {"Shallow ML": 1, "Deep Learning": 1}


class TestPresentLeaves:
    """Display helper: zero-count reserve leaves are omitted, order preserved."""

    def test_zero_count_leaves_excluded_and_order_preserved(self):
        counts = {"Hybrid": 7, "Shallow ML": 4, "Deep Learning": 2}
        assert present_leaves(counts) == ("Shallow ML", "Deep Learning", "Hybrid")

    def test_empty_and_all_zero_return_no_leaves(self):
        assert present_leaves({}) == ()
        assert present_leaves(dict.fromkeys(LEAVES, 0)) == ()

    def test_model_leaves_are_not_mutated(self):
        counts = dict.fromkeys(LEAVES, 0)
        present_leaves(counts)
        assert set(counts) == set(LEAVES)
        assert all(value == 0 for value in counts.values())
