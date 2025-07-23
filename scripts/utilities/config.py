# Configuration for the LULC Initiatives Dashboard

# Color and style configuration for the app
COLORS = {
    "background": "#18181b",
    "text": "#F3F4F6",
    "primary": "#00BFFF",
    "secondary": "#FFD700",
    "tertiary": "#FF69B4",
    "grid": "#444",
}

# Standardized English column names
STANDARD_COLUMNS = {
    "name": "Name",
    "type": "Type",
    "resolution": "Resolution (m)",
    "accuracy": "Accuracy (%)",
    "classes": "Classes",
    "methodology": "Methodology",
    "temporal_frequency": "Temporal Frequency",
    "available_years": "Available Years",
    "scope": "Scope",
    "provider": "Provider",
    "acronym": "Acronym",
}

# Portuguese to English column mapping for data standardization
PT_TO_EN_COLUMNS = {
    "Nome": "Name",
    "Tipo": "Type",
    "Resolução (m)": "Resolution (m)",
    "Acurácia (%)": "Accuracy (%)",
    "Classes": "Classes",
    "Metodologia": "Methodology",
    "Frequência Temporal": "Temporal Frequency",
    "Anos Disponíveis": "Available Years",
    "Escopo": "Scope",
    "Provedor": "Provider",
    "Sigla": "Acronym",
}


def standardize_dataframe_columns(df):
    """Convert Portuguese column names to English standard."""
    return df.rename(columns=PT_TO_EN_COLUMNS)


def get_initiative_color_map(initiative_names):
    """Assign a unique color to each initiative using a highly divergent 15-color palette."""
    # Custom highly divergent 15-color palette based on color theory for maximum visual distinction
    # Uses combinations of primary, secondary, tertiary colors and high contrast variations
    # ColorBrewer "Spectral" 11-color palette extended to 15 colors for high divergence
    divergent_palette = [
        "#9e0142",  # deep red
        "#d53e4f",  # red
        "#f46d43",  # orange
        "#fdae61",  # light orange
        "#fee08b",  # yellow
        "#e6f598",  # light yellow-green
        "#abdda4",  # light green
        "#66c2a5",  # green-cyan
        "#3288bd",  # blue
        "#5e4fa2",  # purple
        "#a6d96a",  # green
        "#140253",  # charcoal
        "#e7298a",  # magenta
        "#1c9099",  # teal
        "#762a83",  # dark purple
    ]

    n = len(initiative_names)
    # Repeat palette if more than 15 initiatives
    colors = (divergent_palette * ((n // len(divergent_palette)) + 1))[:n]
    return dict(zip(initiative_names, colors))
