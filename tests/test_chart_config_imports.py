"""Regression test: ``chart_config`` must import cleanly.

The original bug: ``scripts/utilities/chart_config.py`` did
``from .modern_themes import ModernThemes, modern_colors`` but
``modern_themes`` never exported a ``modern_colors`` name, raising
ImportError at import time and cascading into ``responsive_charts``.

These tests pin the palette contract so the module keeps importing and the
semantic colour roles stay resolvable.
"""

from scripts.utilities import chart_config

MODERN_COLORS_ROLES = (
    "primary",
    "success",
    "warning",
    "danger",
    "info",
    "purple",
    "gradient",
)

SEMANTIC_SOURCE_ROLES = (
    "primary",
    "secondary",
    "accent",
    "success",
    "warning",
    "danger",
    "info",
    "purple",
    "pink",
    "indigo",
)


def test_chart_config_imports_and_exposes_palettes() -> None:
    """Importing chart_config yields populated palette containers."""
    assert chart_config.MODERN_COLORS
    assert chart_config.EXTENDED_PALETTE


def test_semantic_roles_resolve_to_hex_colors() -> None:
    """Every palette role maps to a non-empty list of hex colour strings."""
    for role in MODERN_COLORS_ROLES:
        shades = chart_config.MODERN_COLORS.get(role)
        assert shades, f"missing palette for role: {role}"
        assert shades[0].startswith("#")


def test_semantic_source_map_covers_all_roles() -> None:
    """The semantic source map used by EXTENDED_PALETTE resolves every role."""
    for role in SEMANTIC_SOURCE_ROLES:
        value = chart_config.modern_colors.get(role)
        assert value, f"unresolved semantic role: {role}"
        assert value.startswith("#")


def test_get_color_palette_returns_requested_count() -> None:
    """``get_color_palette`` honours the requested size."""
    palette = chart_config.get_color_palette(3, "primary")
    assert len(palette) == 3
    assert all(color.startswith("#") for color in palette)
