# Methodology Taxonomy

The methodology taxonomy classifies every LULC initiative into exactly one
**MECE** (mutually exclusive, collectively exhaustive) leaf, driven by a single
shared rule engine.

- **Single source of truth (SSoT) in code:**
  `dashboard/components/shared/methodology_taxonomy.py` (stdlib only — `re`,
  `dataclasses`).

All consumers — the data pipeline (`scripts/`), the "Methodology Distribution"
pie/bar, the "Methodology Deep Dive" treemap and the Overview label — import
from that module, so the buckets can never diverge.

---

## 1. Problem

The dashboard previously treated **`Machine Learning`** and
**`Deep Learning`** as flat peer categories:

```text
Machine Learning   ← peers? ────   Deep Learning
```

This is a **category error**: Deep Learning is a *subset* of Machine Learning
(every neural network is a machine-learning model). Placing them side by side
means the buckets are **not mutually exclusive**, so an initiative that uses
both could land in either one, and the pie chart double-counted a concept it
had split in two. It also produced a non-exhaustive tail (`Combined`,
`Other`, `Unknown`) and a keyword list duplicated in three places
(`lulc_data_engine.py`, `json_interpreter.py`, `methodology_deepdive_component.py`)
that had already drifted apart.

---

## 2. The partition

The fix is to rename the non-deep bucket to **`Shallow ML`**, which turns the
pair `{Shallow ML, Deep Learning}` into a valid **shallow-vs-deep** partition
instead of a false `{ML, DL}` peer partition.

The flat MECE leaves, in canonical order (`LEAVES`):

| Leaf | Role |
|------|------|
| `Shallow ML` | Classical / "raso" machine learning |
| `Deep Learning` | Neural-network based methods |
| `Hybrid` | Two or more families detected (single display label) |
| `Visual Interpretation` | Human/photo interpretation |
| `Statistical / Spectral` | Statistical and spectral-mixture methods *(reserve)* |

Every initiative lands in exactly one leaf (mutually exclusive), and the five
leaves cover every possible input (collectively exhaustive), so each chart is
additive. There is **no `Unclassified` leaf**: an input that matches no family
gets `label is None` and the pipeline **fails loudly** at generation (see §6),
so nothing is ever silently bucketed into a catch-all.

Each leaf has a stable colour in `METHODOLOGY_COLORS`.

---

## 3. Vocabulary

- **`Shallow ML`** — classical / *raso* machine learning: random forest,
  gradient boosting, decision/regression trees, SVM, k-NN, CatBoost/XGBoost,
  etc. It is the explicit name for the **non-deep** branch; it is not a claim
  that Deep Learning is a sibling of Machine Learning.
- **`Hybrid`** — derived, **not** a dictionary term. An initiative is `Hybrid`
  when the rule engine detects **two or more families**. The component
  families are stored internally on `MethodologyResult.families` and exposed
  in the derived `Methodology Components` column (pipe-joined, sorted), but
  `Hybrid` is always rendered as a **single label**. The words *"hybrid"* and
  *"combined"* are deliberately **not** dictionary terms, so a free text that
  merely says "Combined" (with no recognisable technique) matches no family and
  has **no label** — it is never assumed to be mixed.
- **No `Unclassified` leaf** — the taxonomy has five leaves only. When no
  dictionary family matches (empty/`None` input, or text with no recognisable
  term), `classify()` returns `label=None` and the data pipeline raises a
  `ValueError` naming the initiative and the raw `classification_method`
  (**fail loud** at generation). Unclassifiable methods are therefore caught
  and fixed at the source; they are never silently bucketed into the data or
  the charts.

---

## 4. Rule engine

`normalize(text)` → `match_families(text)` → `classify(text)`.

1. **Normalise.** Lowercase; replace every run of non `[a-z0-9]` characters
   with a single space; collapse whitespace; strip. So `"U-Net"` → `"u net"`,
   `"k-Nearest"` → `"k nearest"`, `"CNN + visual interpretation"` →
   `"cnn visual interpretation"`. `None` → `""`.
2. **Compile.** Each `TERM_FAMILIES` term becomes a word-boundary regex:
   `\b` + escaped term (internal spaces → `\s+`) + `\b`, so `"u net"` matches
   `"u-net"`/`"u net"` but not `"unrelated"`.
3. **Order.** Sort all `(term, family)` pairs by **descending token length,
   then descending character length**, so the most specific term is always
   walked first (`"regression tree"` before `"regression"`; `"decision trees"`
   before `"decision tree"`).
4. **Span suppression.** Walk in that order. On a match, record the family and
   **consume** its `[start, end)` span; skip any later term whose match
   overlaps a consumed span.
5. **Decide.** Let `families` be the set of matched families:
   - **0 → `label is None`** — no taxonomy leaf; the pipeline fails loudly
   - **1 → that leaf**
   - **≥ 2 → `Hybrid`** (components kept internally, never displayed)

### Worked examples

| Input (`classification_method`) | Matched families | Result |
|---|---|---|
| `"Supervised Random Forest and Deep Learning"` | `Shallow ML` + `Deep Learning` | **`Hybrid`** |
| `"Statistical Methods"` | `Statistical / Spectral` | **`Statistical / Spectral`** |
| `"CNN + visual interpretation"` | `Deep Learning` + `Visual Interpretation` | **`Hybrid`** |
| `"Machine Learning"` | `Shallow ML` | **`Shallow ML`** |

### Span-suppression edge cases

| Input | Walk | Result |
|---|---|---|
| `"Gradient Boosting on decision trees"` | `gradient boosting` (Shallow) + `decision trees` (Shallow); the stem `regression` never fires | `Shallow ML` |
| `"regression tree"` | `regression tree` (Shallow) consumes the span; the shorter `regression` (Statistical) is skipped | `Shallow ML` only — no false `Hybrid` |
| `"decision trees"` | `decision trees` consumes the span; `decision tree` is skipped | `Shallow ML` |
| `""` / `None` / `"Combined"` | no family matched | **no label** (`label is None`; generation fails loudly) |

---

## 5. Dictionary of record

`TERM_FAMILIES` in `dashboard/components/shared/methodology_taxonomy.py` is the
**single place** a methodology term is defined. Terms are stored **normalised**
(lowercase, hyphens and other punctuation already collapsed to single spaces).

| Family | Terms |
|---|---|
| `Shallow ML` | random forest, gradient boosting, gradient boost, decision trees, decision tree, regression trees, regression tree, catboost, xgboost, support vector, svm, k nearest, knn, machine learning, supervised machine learning, rf |
| `Deep Learning` | deep learning, neural networks, neural network, convolutional, cnn, u net, unet, resnet, transformer, lstm, rnn, fcn, gan |
| `Visual Interpretation` | visual interpretation, photo interpretation, photointerpretation, manual |
| `Statistical / Spectral` | spectral mixture, mixture model, bhattacharyya, bhattacharya, maximum likelihood, statistical, pca, regression |

**Maintenance contract**

- Add a term **only here** — never in a router, chart or script.
- Store the term **normalised** (run it through `normalize()` first); a test
  asserts every term equals `normalize(term)`.
- Prefer the **longest specific form** (`"decision trees"` and
  `"decision tree"` both exist so plural/singular inputs match); span
  suppression guarantees the longest match wins.
- Terms are matched as whole words on word boundaries, so `"rf"` will not fire
  inside `"surface"`.

### Public API

| Name | Kind | Purpose |
|---|---|---|
| `LEAVES` | constant | Canonical ordered tuple of the five leaves |
| `HYBRID` | constant | `"Hybrid"` (no `Unclassified` constant — no such leaf) |
| `METHODOLOGY_COLORS` | constant | Stable colour per leaf |
| `TERM_FAMILIES` | constant | Dictionary of record |
| `normalize(text)` | function | Canonical text form |
| `match_families(text)` | function | `(families, matched_terms)` |
| `classify(text)` | function | `MethodologyResult` (frozen dataclass) |
| `canonical_label(value)` | function | Idempotent leaf for a value that may already be a leaf |
| `label_counts(source)` | function | MECE counts from a DataFrame/Series/iterable |
| `membership(source)` | function | leaf → frozenset of member identifiers |
| `present_leaves(counts)` | function | Display helper: leaves with `count > 0`, in `LEAVES` order |

`canonical_label()` makes the aggregate helpers idempotent: a value that is
already one of `LEAVES` is returned unchanged, so a canonical `Methodology`
column can be fed back through `label_counts()` / `membership()` without
`"Shallow ML"` or `"Hybrid"` being re-classified. Unclassifiable values yield
`None` and are ignored by `label_counts()` / `membership()` for chart safety.

---

## 6. Single source of truth

| Layer | Artifact | Authority |
|---|---|---|
| **Rule engine (SSoT)** | `dashboard/components/shared/methodology_taxonomy.py` | Owns the leaves, the dictionary and the decision rule |
| **Source free text** | `data/json/initiatives_metadata.jsonc` → `classification_method` | **Authoritative** for what each initiative actually does |
| **Generated outputs** | `data/processed/initiatives_processed.csv`, `metadata_processed.json`, `auxiliary_data.json`, `validation_report.json` | Derived — **never hand-edited** |

- `data/json/initiatives_metadata.jsonc` is the authority for the free-text
  method. Its `methodology` field is **machine-managed**: it is set to the
  derived leaf so the Overview label agrees with the charts.
- `data/processed/*` is regenerated with
  `.venv/bin/python scripts/data_generation/process_data.py`. On any conflict,
  the JSONC wins: the processed CSV/JSON are rebuilt from it by construction.
- The engine reads the **`classification_method`** field. Where an `algorithm`
  field mentions an extra technique that the `classification_method` free text
  omits, the taxonomy follows `classification_method` (see GPW below).
- **Fail loud.** If `classify()` returns `label is None` (no family matched),
  both `scripts/utilities/json_interpreter.py` and
  `scripts/data_generation/lulc_data_engine.py` raise a `ValueError` naming the
  initiative and the raw `classification_method`. An unclassifiable method is
  therefore caught when the data is generated and must be fixed by extending
  `TERM_FAMILIES` — it is never silently bucketed. All 15 current initiatives
  classify cleanly.

---

## 7. Per-initiative classification (15)

Final leaves after regeneration: `Shallow ML` 4 · `Deep Learning` 2 ·
`Hybrid` 7 · `Visual Interpretation` 2 · `Statistical / Spectral` 0
(5 leaves; no `Unclassified`).

| # | Initiative (acronym) | `classification_method` | Final leaf | Rationale |
|---|---|---|---|---|
| 1 | Copernicus Global Land Cover Service (CGLS) | Supervised Random Forest | `Shallow ML` | Random forest = classical (shallow) ML |
| 2 | Google Dynamic World V1 (GDW) | Deep Learning | `Deep Learning` | Deep-learning classifier |
| 3 | ESRI-10m Annual LULC | Convolutional Neural Network | `Deep Learning` | CNN = deep |
| 4 | Global LULC change 2000 and 2020 (UMD-GLC) | Decision/Regression Trees and U-Net CNN | `Hybrid` | Decision/regression trees (shallow) **+** U-Net CNN (deep) |
| 5 | Global Pasture Watch (GPW) | Supervised Machine Learning | `Shallow ML` | Classical supervised ensembles (RF, GBT);¹ see note below |
| 6 | South America Soybean Maps (UMD-SASM) | Regression, Visual Interpretation, and Decision Trees | `Hybrid` | Regression + visual interpretation + decision trees (Song et al., 2021)² |
| 7 | WorldCover 10m 2021 (ESA-WC) | Gradient Boosting Decision Tree Algorithm | `Shallow ML` | Gradient-boosted trees |
| 8 | WorldCereal | Gradient Boosting on decision trees | `Shallow ML` | Gradient boosting + decision trees |
| 9 | PRODES | Visual Interpretation | `Visual Interpretation` | Human visual interpretation |
| 10 | DETER | Visual Interpretation and Spectral Mixture Model | `Hybrid` | Visual interpretation + spectral mixture |
| 11 | TerraClass Amazônia | Visual Interpretation, Supervised Bhattacharya Classification, and Deep Learning | `Hybrid` | Visual + Bhattacharya (spectral) + deep learning |
| 12 | TerraClass Cerrado | Visual Interpretation, Supervised Bhattacharya Classification, and Deep Learning | `Hybrid` | Visual + Bhattacharya (spectral) + deep learning |
| 13 | MapBiomas | Supervised Random Forest and Deep Learning | `Hybrid` | Random forest (shallow) + deep learning |
| 14 | IBGE Monitoring Land Cover and Land Use (IBGE-MLCU) | Visual Interpretation | `Visual Interpretation` | Human visual interpretation |
| 15 | National Supply Company Agricultural Mapping (CONAB-AM) | Machine Learning, Statistical Methods, Visual Interpretation | `Hybrid` | Shallow ML + statistical + visual interpretation |

¹ GPW's `algorithm` field additionally mentions an artificial neural network
(RF, gradient-boosted trees, ANN), but the authoritative
`classification_method` free text is "Supervised Machine Learning", which
matches only the shallow family. The engine deliberately classifies
`classification_method`.

² **Song, X.-P., Hansen, M.C., Potapov, P., et al. (2021).** *Massive soybean
expansion in South America since 2000 and implications for conservation.*
**Nature Sustainability, 4, 784–792.** DOI:
[10.1038/s41893-021-00729-z](https://doi.org/10.1038/s41893-021-00729-z)
(UMD-SASM was the only initiative without a reference; this was added to the
source JSONC.)

---

## 8. Display contract

- Charts and labels render **only** the leaf (`Methodology`). The internal
  component families (`Methodology Components`, `MethodologyResult.families`)
  are **never displayed** — `Hybrid` always reads as one category, never as
  "Shallow ML + Deep Learning".
- Chained classifications such as `Hybrid (Shallow ML + Deep Learning)` must
  **not** appear in any chart.
- Any tooltip or legend explaining the taxonomy should carry the note:

  > **Deep Learning ⊂ Machine Learning; "Shallow ML" = ML clássico (raso)**

- `label_counts()` / `membership()` are the shared aggregation path: charts
  must obtain counts and members from them (or from the canonical
  `Methodology` column) rather than re-deriving categories locally, so the
  pie, bar and treemap cannot diverge.
- **Leaves with `0` count are not displayed.** Charts render only
  `present_leaves(counts)` — the leaves with a positive count, in `LEAVES`
  order. The reserve leaf (`Statistical / Spectral`) is therefore omitted from
  the chart when nothing maps to it, so no empty `0%` slice/tile appears. It is
  **retained in the model**: `LEAVES`, `classify()`, `label_counts()`,
  `methodology_counts()` and `membership()` all carry the five leaves. Display
  suppression must never be implemented by removing a leaf from `LEAVES`.

---

## 9. Change log & how to add an initiative

### Change log

| Date | Change |
|---|---|
| 2026-09-22 | Replaced the flat `{Machine Learning, Deep Learning}` peer buckets (plus `Combined`/`Other`/`Unknown` tail) with the MECE taxonomy and a single shared rule engine. Renamed the non-deep bucket to `Shallow ML`; `Hybrid` is now derived from ≥2 families. Added `dashboard/components/shared/methodology_taxonomy.py`; deleted the duplicated keyword lists in `scripts/data_generation/lulc_data_engine.py` and `scripts/utilities/json_interpreter.py`. Curated UMD-GLC and UMD-SASM and added UMD-SASM's missing reference. Regenerated `data/processed/*`. |
| 2026-09-22 | Added `present_leaves(counts)` and updated the display contract: zero-count leaves are no longer rendered (no empty `0%` slice/tile), while the model still retained all six leaves. |
| 2026-09-22 | **Removed the `Unclassified` leaf** — the taxonomy is now 5 leaves. `classify()` returns `label=None` when no family matches and the data pipeline (`json_interpreter.py`, `lulc_data_engine.py`) **fails loudly** with a `ValueError` naming the initiative and raw `classification_method`. `label_counts()` / `membership()` iterate the 5 `LEAVES` and ignore `None`. All 15 initiatives still classify (counts unchanged). |

### How to add an initiative

1. Add the initiative to `data/json/initiatives_metadata.jsonc` with an
   accurate free-text **`classification_method`** (the engine's input). Leave
   `methodology` to the pipeline; it is machine-managed.
2. If the free text uses a technique not yet recognised, add the **normalised**
   term to `TERM_FAMILIES` in `dashboard/components/shared/methodology_taxonomy.py`
   (the only place a term belongs). If you skip this, generation will **fail
   loudly** (a `ValueError` naming the initiative and its
   `classification_method`) rather than silently bucketing the initiative.
3. Regenerate the derived artifacts:
   `.venv/bin/python scripts/data_generation/process_data.py`.
4. Confirm the derived leaf and counts:
   `.venv/bin/python -m pytest tests/test_data_integrity.py` (and
   `tests/test_methodology_taxonomy.py` for the engine).
5. Update the per-initiative table above if the set of 15 changes.
