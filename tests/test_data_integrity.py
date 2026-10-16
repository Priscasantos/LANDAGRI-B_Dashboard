"""Data-integrity tests for the regenerated MECE methodology outputs.

These run against the generated ``data/processed/*`` artifacts, which are
DERIVED from ``data/json/initiatives_metadata.jsonc`` (the declared SSoT for
the free-text classification method). Never hand-edit the generated files.
"""

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "initiatives_processed.csv"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "metadata_processed.json"
JSONC_PATH = PROJECT_ROOT / "data" / "json" / "initiatives_metadata.jsonc"

EXPECTED_COUNTS = {
    "Shallow ML": 4,
    "Deep Learning": 2,
    "Hybrid": 7,
    "Visual Interpretation": 2,
    "Statistical / Spectral": 0,
}


def _load_metadata() -> dict:
    with open(METADATA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def _load_jsonc() -> dict:
    text = JSONC_PATH.read_text(encoding="utf-8")
    body = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("//")
    )
    return json.loads(body)


def test_csv_methodology_counts_match_mece_target():
    frame = pd.read_csv(CSV_PATH)
    counts = frame["Methodology"].value_counts().to_dict()
    full_counts = {leaf: counts.get(leaf, 0) for leaf in EXPECTED_COUNTS}
    assert full_counts == EXPECTED_COUNTS


def test_csv_and_metadata_methodology_agree_per_initiative():
    frame = pd.read_csv(CSV_PATH)
    metadata = _load_metadata()
    csv_by_name = dict(zip(frame["Name"], frame["Methodology"]))
    assert set(csv_by_name) == set(metadata)
    for name, metadata_entry in metadata.items():
        assert metadata_entry["Methodology"] == csv_by_name[name], name


def test_umd_sasm_has_a_reference():
    jsonc = _load_jsonc()
    for entry in jsonc.values():
        if entry.get("acronym") == "UMD-SASM":
            references = entry.get("references")
            assert references, "UMD-SASM is missing its reference"
            assert any("Massive soybean expansion" in ref for ref in references)
            return
    raise AssertionError("UMD-SASM not found in the source JSONC")


def test_no_composite_methodology_cells():
    frame = pd.read_csv(CSV_PATH)
    for value in frame["Methodology"].dropna():
        text = str(value)
        assert "RF+DL" not in text, text
        assert "BLANK" not in text.upper()
        assert "+" not in text, f"Composite methodology leaked into a cell: {text!r}"


def test_methodology_components_are_sorted_and_hidden_from_label():
    frame = pd.read_csv(CSV_PATH)
    allowed = set(EXPECTED_COUNTS)
    for _, row in frame.iterrows():
        components = row.get("Methodology Components")
        if isinstance(components, str) and components:
            parsed = components.split("|")
            assert parsed == sorted(parsed)
            assert all(component in allowed for component in parsed)
        assert row["Methodology"] in allowed
