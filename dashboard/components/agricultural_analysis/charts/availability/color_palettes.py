"""
Color Palettes for Agricultural Analysis Dashboard
==============================================

Consistent color palettes for Brazilian states and regions in agricultural visualizations.

Author: LANDAGRI-B Project Team
Date: 2025-08-11
"""

# Regional color palette for Brazilian regions
REGIONAL_COLORS = {
    'North': '#E8F8F5',         # Light mint green for Amazon region
    'Northeast': '#FDF2E9',     # Light warm orange for dry region
    'Central-West': '#FEF9E7',  # Light yellow for cerrado region
    'Southeast': '#EBF5FB',     # Light blue for industrial region
    'South': '#F4ECF7'          # Light purple for temperate region
}

# Darker versions for better contrast
REGIONAL_COLORS_DARK = {
    'North': '#52C9B2',         # Medium green
    'Northeast': '#F39C12',     # Orange
    'Central-West': '#F7DC6F',  # Yellow
    'Southeast': '#5DADE2',     # Blue
    'South': '#BB8FCE'          # Purple
}

# State to region mapping
STATE_TO_REGION = {
    # North (Norte)
    'AC': 'North', 'AP': 'North', 'AM': 'North', 'PA': 'North',
    'RO': 'North', 'RR': 'North', 'TO': 'North',
    
    # Northeast (Nordeste)
    'AL': 'Northeast', 'BA': 'Northeast', 'CE': 'Northeast', 'MA': 'Northeast',
    'PB': 'Northeast', 'PE': 'Northeast', 'PI': 'Northeast', 'RN': 'Northeast', 'SE': 'Northeast',
    
    # Central-West (Centro-Oeste)
    'DF': 'Central-West', 'GO': 'Central-West', 'MT': 'Central-West', 'MS': 'Central-West',
    
    # Southeast (Sudeste)
    'ES': 'Southeast', 'MG': 'Southeast', 'RJ': 'Southeast', 'SP': 'Southeast',
    
    # South (Sul)
    'PR': 'South', 'RS': 'South', 'SC': 'South'
}

# Modern color palette for general use
MODERN_COLORS = {
    'primary': '#2E86C1',      # Professional blue
    'secondary': '#28B463',     # Fresh green
    'accent': '#F39C12',        # Warm orange
    'danger': '#E74C3C',        # Alert red
    'gradient_low': '#EBF5FB',  # Light blue
    'gradient_mid': '#AED6F1',  # Medium blue
    'gradient_high': '#2874A6', # Dark blue
    'coverage_excellent': '#27AE60', # Excellent coverage
    'coverage_good': '#F39C12',      # Good coverage
    'coverage_fair': '#E67E22',      # Fair coverage
    'coverage_poor': '#E74C3C'       # Poor coverage
}

# Crop-specific colors (enhanced palette with high contrast and accessibility)
# Palette chosen to provide strong visual distinction between crop types
CROP_COLORS = {
    'Corn': '#1f77b4',           # Blue
    'Soybean': '#ff7f0e',        # Orange
    'Wheat': '#2ca02c',          # Green
    'Rice': '#d62728',           # Red (for generic rice)
    'Irrigated Rice': '#d62728', # Red (same family as Rice)
    'Sugar cane': '#9467bd',     # Purple
    'Sugar cane mill': '#8c564b',# Brown
    'Coffee': '#e377c2',         # Pink
    'Beans': '#7f7f7f',          # Gray
    'Cassava': '#bcbd22',        # Olive
    'Cotton': '#17becf',         # Teal/Cyan
    'Other winter crops': '#aec7e8',
    'Other summer crops': '#ffbb78',
    'Millet': '#98df8a',
    'Sorghum': '#ff9896',
    'default': '#6c757d'         # Neutral dark gray fallback
}

def get_state_acronym(state_name: str) -> str:
    """Convert full state name to acronym"""
    state_mapping = {
        'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
        'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF', 'Espírito Santo': 'ES',
        'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS',
        'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
        'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
        'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC',
        'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'
    }
    return state_mapping.get(state_name, state_name)

def get_state_color(state_code: str, use_dark: bool = False) -> str:
    """
    Get color for a state based on its region.
    
    Args:
        state_code: Two-letter state code (e.g., 'SP', 'MG')
        use_dark: Whether to use dark colors for better contrast
    
    Returns:
        Hex color code for the state's region
    """
    region = STATE_TO_REGION.get(state_code, 'Southeast')  # Default to Southeast
    
    if use_dark:
        return REGIONAL_COLORS_DARK.get(region, MODERN_COLORS['primary'])
    else:
        return REGIONAL_COLORS.get(region, MODERN_COLORS['gradient_low'])

def get_region_color(region: str, use_dark: bool = False) -> str:
    """
    Get color for a Brazilian region.
    
    Args:
        region: Region name (North, Northeast, Central-West, Southeast, South)
        use_dark: Whether to use dark colors for better contrast
    
    Returns:
        Hex color code for the region
    """
    if use_dark:
        return REGIONAL_COLORS_DARK.get(region, MODERN_COLORS['primary'])
    else:
        return REGIONAL_COLORS.get(region, MODERN_COLORS['gradient_low'])

def get_coverage_color(coverage_percentage: float) -> str:
    """
    Get color based on coverage percentage.
    
    Args:
        coverage_percentage: Coverage percentage (0-100)
    
    Returns:
        Hex color code based on coverage level
    """
    if coverage_percentage >= 75:
        return MODERN_COLORS['coverage_excellent']
    elif coverage_percentage >= 50:
        return MODERN_COLORS['coverage_good']
    elif coverage_percentage >= 25:
        return MODERN_COLORS['coverage_fair']
    else:
        return MODERN_COLORS['coverage_poor']

def get_crop_color(crop_name: str) -> str:
    """
    Get color for a specific crop.
    
    Args:
        crop_name: Name of the crop
    
    Returns:
        Hex color code for the crop
    """
    # Extract base crop name by removing harvest information in parentheses
    import re
    base_crop = re.sub(r'\s*\([^)]*\)$', '', crop_name).strip()
    return CROP_COLORS.get(base_crop, CROP_COLORS.get(crop_name, CROP_COLORS['default']))

def get_gradient_colors(num_colors: int = 5) -> list:
    """
    Get a list of gradient colors for data visualization.
    
    Args:
        num_colors: Number of colors needed
    
    Returns:
        List of hex color codes
    """
    if num_colors <= 5:
        base_colors = ['#E8F6F3', '#A3E4D7', '#52C9B2', '#1ABC9C', '#16A085']
        return base_colors[:num_colors]
    else:
        # Generate more colors if needed
        import plotly.colors as pc
        return pc.sample_colorscale('Viridis', num_colors)
