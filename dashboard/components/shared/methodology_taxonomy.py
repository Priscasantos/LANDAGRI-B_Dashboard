"""Methodology taxonomy — the single source of truth (SSoT).

Pure, dependency-free (stdlib only) rule engine shared by the data pipeline
(``scripts/``) and the dashboard (``dashboard/``). Both sides MUST import from
here so the "Methodology Distribution" pie, the "Methodology Deep Dive"
treemap and the Overview label can never disagree.

Design (LOCKED):
- Flat MECE leaves. ``Hybrid`` is a single display label derived from an
  initiative matching two or more term families; the component families are
  stored internally (``MethodologyResult.families``) and are NEVER displayed.
- ``Shallow ML`` is the non-deep machine-learning bucket (classical / "raso":
  random forest, gradient boosting, SVM, decision trees, ...). It is NOT a
  peer of ``Deep Learning`` in the semantic sense (DL is a subset of ML); it
  merely names the non-deep branch of the MECE partition.
- The words "hybrid" and "combined" are NOT dictionary terms: a text is Hybrid
  only when the rule engine finds >= 2 distinct families. ``"Combined"``
  therefore matches no family and has NO label (``label is None``); the data
  pipeline treats a ``None`` label as a hard error at generation time
  (fail loud), so such a method is never silently bucketed.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import re
from typing import Any

LEAVES: tuple[str, ...] = (
    "Shallow ML",
    "Deep Learning",
    "Hybrid",
    "Visual Interpretation",
    "Statistical / Spectral",
)

#: Membership set for O(1) "already a leaf?" checks.
_LEAF_SET: frozenset[str] = frozenset(LEAVES)

HYBRID = "Hybrid"

#: Stable, colour-blind-friendly palette (one colour per leaf).
METHODOLOGY_COLORS: dict[str, str] = {
    "Shallow ML": "#4C78A8",
    "Deep Learning": "#F58518",
    "Hybrid": "#54A24B",
    "Visual Interpretation": "#B279A2",
    "Statistical / Spectral": "#E45756",
}

#: Dictionary of record. Terms are stored normalised (lowercase, hyphens and
#: any other punctuation already collapsed to single spaces).
TERM_FAMILIES: dict[str, tuple[str, ...]] = {
    "Shallow ML": (
        "random forest",
        "gradient boosting",
        "gradient boost",
        "decision trees",
        "decision tree",
        "regression trees",
        "regression tree",
        "catboost",
        "xgboost",
        "support vector",
        "svm",
        "k nearest",
        "knn",
        "machine learning",
        "supervised machine learning",
        "rf",
    ),
    "Deep Learning": (
        "deep learning",
        "neural networks",
        "neural network",
        "convolutional",
        "cnn",
        "u net",
        "unet",
        "resnet",
        "transformer",
        "lstm",
        "rnn",
        "fcn",
        "gan",
    ),
    "Visual Interpretation": (
        "visual interpretation",
        "photo interpretation",
        "photointerpretation",
        "manual",
    ),
    "Statistical / Spectral": (
        "spectral mixture",
        "mixture model",
        "bhattacharyya",
        "bhattacharya",
        "maximum likelihood",
        "statistical",
        "pca",
        "regression",
    ),
}

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_WHITESPACE = re.compile(r"\s+")

#: Columns to probe (in order) when handed a DataFrame.
_TEXT_COLUMNS: tuple[str, ...] = (
    "Classification Method",
    "classification_method",
    "Methodology",
    "methodology",
)
_NAME_COLUMNS: tuple[str, ...] = ("Name", "Acronym", "name", "acronym")


def normalize(text: Any) -> str:
    """Normalise free text to the dictionary's canonical form.

    Lowercases, replaces every run of non ``[a-z0-9]`` characters with a single
    space, collapses whitespace and strips. ``None`` becomes ``""``.
    """
    if text is None:
        return ""
    lowered = str(text).lower()
    return _WHITESPACE.sub(" ", _NON_ALNUM.sub(" ", lowered)).strip()


def _compile_term(term: str) -> re.Pattern[str]:
    """Compile a normalised term to a word-boundary regex (spaces -> ``\\s+``)."""
    parts = [re.escape(part) for part in term.split(" ")]
    return re.compile(r"\b" + r"\s+".join(parts) + r"\b")


def _build_index() -> tuple[tuple[str, str, int, int, re.Pattern[str]], ...]:
    """Build the (term, family, n_tokens, n_chars, pattern) index, longest first."""
    entries: list[tuple[str, str, int, int, re.Pattern[str]]] = []
    for family, terms in TERM_FAMILIES.items():
        for term in terms:
            entries.append(
                (term, family, len(term.split(" ")), len(term), _compile_term(term))
            )
    # DESCENDING token length, then descending character length, so the most
    # specific term always wins ("regression tree" before "regression",
    # "decision trees" before "decision tree").
    entries.sort(key=lambda item: (-item[2], -item[3]))
    return tuple(entries)


_TERM_INDEX = _build_index()


def match_families(text: Any) -> tuple[frozenset[str], tuple[str, ...]]:
    """Return ``(families, matched_terms)`` for ``text``.

    Longest terms are walked first; on a match the span is consumed and any
    later term overlapping a consumed span is skipped. This prevents
    "regression" firing inside "regression tree" and "decision tree" firing
    inside "decision trees".
    """
    normalized = normalize(text)
    if not normalized:
        return frozenset(), ()

    consumed: list[tuple[int, int]] = []
    families: set[str] = set()
    matched_terms: list[str] = []

    for term, family, _tokens, _length, pattern in _TERM_INDEX:
        hit = False
        for match in pattern.finditer(normalized):
            start, end = match.span()
            if any(start < c_end and c_start < end for c_start, c_end in consumed):
                continue
            consumed.append((start, end))
            hit = True
        if hit:
            families.add(family)
            matched_terms.append(term)

    return frozenset(families), tuple(matched_terms)


@dataclass(frozen=True)
class MethodologyResult:
    """Outcome of classifying one free-text methodology description.

    ``label`` is ``None`` when no dictionary family matched: the taxonomy has
    no ``Unclassified`` leaf, and the pipeline must treat a ``None`` label as a
    hard error rather than silently bucketing the initiative.
    """

    label: str | None
    families: frozenset[str]
    matched_terms: tuple[str, ...]
    raw: str | None


def classify(text: Any) -> MethodologyResult:
    """Classify free text into exactly one MECE leaf, or ``None``.

    0 families -> ``label is None`` (no silent bucketing); 1 -> that leaf;
    >= 2 -> ``Hybrid``.
    """
    families, matched_terms = match_families(text)
    raw = text if text is None or isinstance(text, str) else str(text)
    if not families:
        return MethodologyResult(
            label=None, families=frozenset(), matched_terms=(), raw=raw
        )
    label = next(iter(families)) if len(families) == 1 else HYBRID
    return MethodologyResult(
        label=label, families=families, matched_terms=matched_terms, raw=raw
    )


def canonical_label(value: Any) -> str | None:
    """Return the MECE leaf that ``value`` denotes, or ``None``.

    Idempotent over :data:`LEAVES`: a value that already IS a leaf label is
    returned unchanged, so a canonical ``Methodology`` column can be fed back
    through :func:`label_counts` / :func:`membership` without "Shallow ML" or
    "Hybrid" being re-classified. Anything else goes through :func:`classify`,
    which returns ``None`` when nothing matches.
    """
    if isinstance(value, MethodologyResult):
        return value.label
    if isinstance(value, str) and value in _LEAF_SET:
        return value
    return classify(value).label


def _label_of(value: Any) -> str | None:
    """Return the label of ``value`` (already a result or a leaf, or raw text)."""
    return canonical_label(value)


def _iter_values(source: Any) -> Iterable[Any]:
    """Yield the text values carried by a DataFrame, Series, mapping or iterable."""
    if hasattr(source, "columns"):  # pandas.DataFrame (duck-typed)
        column = next((c for c in _TEXT_COLUMNS if c in source.columns), None)
        if column is None:
            raise ValueError(
                f"No methodology text column found; expected one of {_TEXT_COLUMNS}"
            )
        return list(source[column])
    if hasattr(source, "tolist") and not isinstance(source, (str, bytes)):
        return list(source.tolist())  # pandas.Series / Index
    if isinstance(source, Mapping):
        return list(source.values())
    if isinstance(source, (str, bytes)):
        return [source]
    return list(source)


def label_counts(source: Any) -> dict[str, int]:
    """Count the MECE leaf each row of ``source`` belongs to.

    Accepts a DataFrame (uses the classification-method column),
    a Series/list of strings, a mapping or an iterable. Only :data:`LEAVES`
    (5 leaves) are counted; unclassifiable inputs (``label is None``) are
    ignored for chart safety. Zero-count leaves are omitted; remaining keys
    follow :data:`LEAVES` order.
    """
    counts: dict[str, int] = {}
    for value in _iter_values(source):
        label = _label_of(value)
        if label is None:  # no family matched -> not a taxonomy leaf; ignore
            continue
        counts[label] = counts.get(label, 0) + 1
    return {leaf: counts[leaf] for leaf in LEAVES if counts.get(leaf)}


def membership(source: Any) -> dict[str, frozenset[str]]:
    """Map each MECE leaf to the frozenset of initiatives that fall under it.

    Identifiers come from ``Name`` then ``Acronym`` when ``source`` is a
    DataFrame; otherwise the positional index is used. Only :data:`LEAVES`
    (5 leaves) are returned; unclassifiable inputs (``label is None``) are
    ignored for chart safety. Leaves with no member are omitted; keys follow
    :data:`LEAVES` order. This is the shared drill-down path so charts cannot
    diverge from :func:`label_counts`.
    """
    values = _iter_values(source)

    identifiers: list[str]
    if hasattr(source, "columns"):
        name_column = next((c for c in _NAME_COLUMNS if c in source.columns), None)
        if name_column is not None:
            identifiers = [str(v) for v in source[name_column]]
        else:
            identifiers = [str(i) for i in range(len(values))]
    else:
        identifiers = [str(i) for i in range(len(values))]

    buckets: dict[str, list[str]] = {}
    for identifier, value in zip(identifiers, values):
        label = _label_of(value)
        if label is None:  # no family matched -> not a taxonomy leaf; ignore
            continue
        buckets.setdefault(label, []).append(identifier)

    return {leaf: frozenset(buckets[leaf]) for leaf in LEAVES if leaf in buckets}


def present_leaves(counts: Mapping[str, int]) -> tuple[str, ...]:
    """Return the leaves with a positive count, in :data:`LEAVES` order.

    DISPLAY helper only: the model still carries all :data:`LEAVES`, but
    charts omit zero-count leaves (e.g. the ``Statistical / Spectral`` reserve)
    when nothing maps to them. Pure and testable — does not mutate ``counts``.
    """
    return tuple(leaf for leaf in LEAVES if counts.get(leaf, 0) > 0)
