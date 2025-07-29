"""
Modern Chart Theme Configuration
Based on 2024-2025 best practices for clean, minimalist chart design
"""

def get_modern_layout_config(**kwargs):
    """
    Returns modern layout configuration with transparent backgrounds
    and clean styling following current design trends.
    
    Key principles from research:
    - Transparent backgrounds for seamless integration
    - Minimal visual clutter
    - Clean typography
    - Consistent spacing and margins
    - Modern color schemes
    """
    
    base_config = {
        # Modern transparent backgrounds - no distracting colors
        "plot_bgcolor": "rgba(0,0,0,0)",  # Transparent plot area
        "paper_bgcolor": "rgba(0,0,0,0)",  # Transparent paper/canvas
        
        # Modern typography
        "font": {
            "family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            "size": 12,
            "color": "#2D3748"  # Modern dark gray
        },
        
        # Clean title styling
        "title": {
            "font": {
                "size": 18,
                "color": "#1A202C",  # Darker for hierarchy
                "family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            },
            "x": 0.5,  # Center align
            "xanchor": "center"
        },
        
        # Modern legend positioning and styling
        "legend": {
            "orientation": "h",  # Horizontal legends are more modern
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "font": {"size": 11, "color": "#4A5568"},
            "bgcolor": "rgba(255,255,255,0.8)",  # Subtle background
            "bordercolor": "rgba(0,0,0,0.1)",
            "borderwidth": 1
        },
        
        # Clean margins for modern look
        "margin": {
            "l": 60,
            "r": 40,
            "t": 80,
            "b": 60
        },
        
        # Modern hover styling
        "hoverlabel": {
            "bgcolor": "rgba(255,255,255,0.95)",
            "bordercolor": "rgba(0,0,0,0.1)",
            "font": {"size": 12, "color": "#2D3748"}
        },
        
        # Clean grid and axis styling
        "xaxis": {
            "showgrid": True,
            "gridwidth": 1,
            "gridcolor": "rgba(0,0,0,0.08)",  # Very subtle grid
            "zeroline": False,
            "showline": True,
            "linewidth": 1,
            "linecolor": "rgba(0,0,0,0.2)",
            "tickfont": {"size": 11, "color": "#4A5568"},
            "title": {
                "font": {"size": 13, "color": "#2D3748"}
            }
        },
        
        "yaxis": {
            "showgrid": True,
            "gridwidth": 1,
            "gridcolor": "rgba(0,0,0,0.08)",
            "zeroline": False,
            "showline": True,
            "linewidth": 1,
            "linecolor": "rgba(0,0,0,0.2)",
            "tickfont": {"size": 11, "color": "#4A5568"},
            "title": {
                "font": {"size": 13, "color": "#2D3748"}
            }
        }
    }
    
    # Merge with any custom overrides
    base_config.update(kwargs)
    return base_config


def get_modern_color_palette():
    """
    Returns a modern, accessible color palette for charts
    Based on current design system trends
    """
    return [
        "#3B82F6",  # Modern blue
        "#10B981",  # Modern green
        "#F59E0B",  # Modern amber
        "#EF4444",  # Modern red
        "#8B5CF6",  # Modern purple
        "#F97316",  # Modern orange
        "#06B6D4",  # Modern cyan
        "#84CC16",  # Modern lime
        "#EC4899",  # Modern pink
        "#6B7280"   # Modern gray
    ]


def get_modern_template():
    """
    Returns the recommended modern template for Plotly charts
    """
    return "simple_white"  # Clean, minimal template


def apply_modern_styling(fig, **custom_config):
    """
    Apply modern styling to any Plotly figure
    
    Args:
        fig: Plotly figure object
        **custom_config: Additional layout customizations
    """
    
    # Get base modern configuration
    layout_config = get_modern_layout_config(**custom_config)
    
    # Apply the configuration
    fig.update_layout(**layout_config)
    
    # Apply trace-specific modern styling based on trace type
    for i, trace in enumerate(fig.data):
        # Only apply marker properties to trace types that support them
        if hasattr(trace, 'type') and trace.type in ['scatter', 'bar', 'box', 'violin', 'scattergl']:
            fig.update_traces(
                marker_line_width=0,  # Remove outline for cleaner look
                selector=dict(type=trace.type)
            )
        
        # Apply opacity to all trace types (this is universally supported)
        fig.update_traces(
            opacity=0.85,  # Subtle transparency for modern feel
            selector=dict(uid=trace.uid) if hasattr(trace, 'uid') and trace.uid else None
        )
    
    return fig


def get_modern_bar_config():
    """Specific configuration for bar charts"""
    return get_modern_layout_config(
        bargap=0.3,  # Modern spacing between bars
        bargroupgap=0.1
    )


def get_modern_line_config():
    """Specific configuration for line charts"""
    return get_modern_layout_config(
        hovermode="x unified"  # Modern hover mode
    )


def get_modern_scatter_config():
    """Specific configuration for scatter plots"""
    return get_modern_layout_config(
        hovermode="closest"
    )


def get_modern_timeline_config():
    """Specific configuration for timeline charts"""
    return get_modern_layout_config(
        showlegend=True,
        margin={"l": 80, "r": 40, "t": 80, "b": 100}  # Extra space for timeline
    )
