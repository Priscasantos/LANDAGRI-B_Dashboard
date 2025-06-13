# Configuration for the LULC Initiatives Dashboard
import plotly.express as px

# Color and style configuration for the app
COLORS = {
    'background': '#18181b',
    'text': '#F3F4F6',
    'primary': '#00BFFF',
    'secondary': '#FFD700',
    'tertiary': '#FF69B4',
    'grid': '#444',
}

# Standardized English column names
STANDARD_COLUMNS = {
    'name': 'Name',
    'type': 'Type',
    'resolution': 'Resolution (m)',
    'accuracy': 'Accuracy (%)',
    'classes': 'Classes',
    'methodology': 'Methodology',
    'temporal_frequency': 'Temporal Frequency',
    'available_years': 'Available Years',
    'scope': 'Scope',
    'provider': 'Provider',
    'acronym': 'Acronym'
}

# Portuguese to English column mapping for data standardization
PT_TO_EN_COLUMNS = {
    'Nome': 'Name',
    'Tipo': 'Type',
    'Resolução (m)': 'Resolution (m)',
    'Acurácia (%)': 'Accuracy (%)',
    'Classes': 'Classes',
    'Metodologia': 'Methodology',
    'Frequência Temporal': 'Temporal Frequency',
    'Anos Disponíveis': 'Available Years',
    'Escopo': 'Scope',
    'Provedor': 'Provider',
    'Sigla': 'Acronym'
}

def standardize_dataframe_columns(df):
    """Convert Portuguese column names to English standard."""
    return df.rename(columns=PT_TO_EN_COLUMNS)

def get_initiative_color_map(initiative_names):
    """Assign a unique color to each initiative using a qualitative palette."""
    palette = px.colors.qualitative.Plotly
    n = len(initiative_names)
    # Repeat palette if not enough colors
    colors = (palette * ((n // len(palette)) + 1))[:n]
    return dict(zip(initiative_names, colors))
