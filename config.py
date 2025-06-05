# Color and style configuration for the app
import plotly.express as px

COLORS = {
    'background': '#18181b',
    'text': '#F3F4F6',
    'primary': '#00BFFF',
    'secondary': '#FFD700',
    'tertiary': '#FF69B4',
    'grid': '#444',
}

def get_initiative_color_map(initiative_names):
    """Assign a unique color to each initiative using a qualitative palette."""
    palette = px.colors.qualitative.Plotly
    n = len(initiative_names)
    # Repeat palette if not enough colors
    colors = (palette * ((n // len(palette)) + 1))[:n]
    return dict(zip(initiative_names, colors))
