import os
import sys
import warnings
from pathlib import Path

import pandas as pd  # Added import for pandas
import streamlit as st
from streamlit_option_menu import option_menu

# Add scripts directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "scripts"))

# Initialize modern themes system
try:
    from scripts.utilities.modern_themes import ModernThemes

    # Setup the modern theme globally
    ModernThemes.setup_modern_theme()
except ImportError:
    st.warning("⚠️ Modern themes system not available. Using default styling.")

# Updated import using the new JSON interpreter
try:
    from scripts.utilities.json_interpreter import interpret_initiatives_metadata
except ImportError:
    st.error("❌ Error importing JSON interpreter. Please check module structure.")
    st.stop()

# Set environment variable to disable PyArrow optimization
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

# Suppress warnings to clean up output
warnings.filterwarnings("ignore")


# Cache main data for better performance
@st.cache_data(
    ttl=300
)  # Cache por 5 minutos para permitir atualizações mais frequentes
def load_cached_data():
    """Loads and caches the main dashboard data using JSON interpreter"""
    try:
        # Correct path to new data/json structure
        metadata_file_path = (
            current_dir / "data" / "json" / "initiatives_metadata.jsonc"
        )
        df = interpret_initiatives_metadata(metadata_file_path)
        if df.empty:
            st.error("❌ No data loaded from JSON interpreter.")
            return None
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None


# Page configuration with performance optimizations
st.set_page_config(
    page_title="LULC Dashboard",
    layout="wide",
    page_icon="🌍",
    initial_sidebar_state="expanded",
    # Performance optimizations
    menu_items={"Report a bug": None, "Get Help": None, "About": None},
)

# Custom CSS for fonts and modern layout
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, .main .block-container {
        font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif !important;
        font-size: 16px;
        line-height: 1.7;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #1e293b;
    }
    /* Hide Streamlit's default header, footer, and hamburger menu */
    .css-1d391kg, .css-1rs6os, .css-17eq0hr { /* These classes might change with Streamlit updates */
        display: none !important;
    }
    .main > div:first-child {
        padding-top: 1rem; /* Adjust top padding if header is hidden */
    }
    .stSidebar {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        border-right: 3px solid #60a5fa; /* Accent border */
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    /* Style for the first element in sidebar (often the menu title container) */
    .stSidebar .element-container:first-child {
        background: rgba(59, 130, 246, 0.1); /* Light blue accent */
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
    }
    .stSidebar * {
        color: #e2e8f0 !important; /* Light text color for sidebar */
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #60a5fa !important; /* Accent color for sidebar headers */
        font-weight: 600;
    }
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); /* Gradient button */
        color: white;
        border: none;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%); /* Darker gradient on hover */
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    /* Styling for navigation links from streamlit-option-menu */
    .nav-link {
        background: rgba(148, 163, 184, 0.1) !important; /* Subtle background */
        margin-bottom: 0.3rem !important;
        border-radius: 0.7rem !important;
        transition: all 0.3s ease !important;
        border-left: 3px solid transparent !important; /* For hover effect */
    }
    .nav-link:hover {
        background: rgba(59, 130, 246, 0.2) !important; /* Lighter blue on hover */
        border-left: 3px solid #60a5fa !important; /* Accent border on hover */
        transform: translateX(2px) !important;
    }
    .nav-link-selected {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important; /* Selected link style */
        color: #ffffff !important;
        font-weight: 600 !important;
        border-left: 3px solid #60a5fa !important;
        box-shadow: 0 3px 10px rgba(59, 130, 246, 0.3) !important;
    }
    .nav-link i { /* Icon styling */
        margin-right: 0.5rem;
        width: 20px;
        text-align: center;
    }
    /* Responsive adjustments */
    @media (max-width: 900px) {
        html, body, .main .block-container {
            font-size: 15px;
        }
        .stSidebar {
            font-size: 14px;
        }
    }
    @media (max-width: 600px) {
        html, body, .main .block-container {
            font-size: 14px;
        }
        .stSidebar {
            font-size: 13px;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Load and cache data early ---
if "df_interpreted" not in st.session_state or st.session_state.df_interpreted is None:
    df_loaded = load_cached_data()  # Call the cached function
    if df_loaded is not None and not df_loaded.empty:
        st.session_state.df_interpreted = df_loaded
        # Load raw metadata for overview and other components
        try:
            from scripts.utilities.json_interpreter import _load_jsonc_file

            metadata_file_path = (
                current_dir / "data" / "json" / "initiatives_metadata.jsonc"
            )
            raw_metadata = _load_jsonc_file(metadata_file_path)
            st.session_state.metadata = raw_metadata
        except Exception as e_meta:
            st.error(f"❌ Error loading initial raw metadata in app.py: {e_meta}")
            st.session_state.metadata = {}
    elif df_loaded is None:
        # Error messages are handled within load_cached_data, but we might want to stop
        # or ensure pages handle the lack of data gracefully.
        st.error("Initial data loading failed. Some dashboard features may not work.")
        # To prevent pages from running without data, you might initialize df_interpreted to an empty df
        # or handle this explicitly in each page's run() method.
        st.session_state.df_interpreted = (
            pd.DataFrame()
        )  # Ensure it exists, even if empty

# Hide Streamlit's default sidebar navigation (multipage menu)
# This is done because we are using streamlit-option-menu for a custom sidebar.
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- Custom sidebar with hierarchical structure ---
with st.sidebar:
    # Estrutura hierárquica do menu
    menu_structure = {
        "📊 Overview": {
            "icon": "house",
            "pages": ["Dashboard Overview"],
            "page_icons": ["speedometer2"]
        },
        "🔍 Initiative Analysis": {
            "icon": "search",
            "pages": ["Temporal Analysis", "Comparative Analysis", "Detailed Analysis"],
            "page_icons": ["calendar-event", "bar-chart", "zoom-in"]
        },
        "🌾 Agriculture Analysis": {
            "icon": "leaf",
            "pages": ["Crop Calendar", "Agriculture Availability"],
            "page_icons": ["calendar3", "graph-up-arrow"]
        }
    }
    
    # Estilos modernos para o menu hierárquico
    modern_menu_styles = {
        "container": {
            "padding": "0.5rem",
            "background": "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)",
            "border-radius": "12px",
            "box-shadow": "0 8px 32px rgba(0,0,0,0.3)",
            "backdrop-filter": "blur(10px)",
            "border": "1px solid rgba(255,255,255,0.1)"
        },
        "nav-link": {
            "font-size": "16px",
            "text-align": "left",
            "margin": "0.3rem 0",
            "padding": "1rem 1.2rem",
            "border-radius": "10px",
            "transition": "all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            "background": "rgba(255,255,255,0.05)",
            "border-left": "4px solid transparent",
            "backdrop-filter": "blur(5px)"
        },
        "nav-link-selected": {
            "background": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
            "color": "#ffffff",
            "font-weight": "600",
            "transform": "translateX(8px) scale(1.02)",
            "box-shadow": "0 6px 20px rgba(59, 130, 246, 0.4)",
            "border-left": "4px solid #60a5fa"
        },
        "icon": {
            "color": "#60a5fa",
            "font-size": "18px",
            "margin-right": "12px"
        },
        "menu-title": {
            "color": "#60a5fa",
            "font-weight": "700",
            "font-size": "22px",
            "text-align": "center",
            "margin-bottom": "1.5rem",
            "padding": "1rem",
            "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(29, 78, 216, 0.1) 100%)",
            "border-radius": "10px",
            "border": "1px solid rgba(59, 130, 246, 0.2)"
        }
    }
    
    # Menu principal - categorias
    selected_category = option_menu(
        menu_title="🛰️ LULC Dashboard",
        options=list(menu_structure.keys()),
        icons=[menu_structure[cat]["icon"] for cat in menu_structure.keys()],
        default_index=0,
        styles=modern_menu_styles,
        key="main_category_menu"
    )
    
    # Sub-menu para categoria selecionada
    selected_page = None
    if selected_category in menu_structure:
        st.markdown("---")
        
        # Estilos para sub-menu
        sub_menu_styles = {
            "container": {
                "padding": "0.3rem",
                "background": "rgba(59, 130, 246, 0.1)",
                "border-radius": "8px",
                "border": "1px solid rgba(59, 130, 246, 0.2)"
            },
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "0.2rem 0",
                "padding": "0.8rem 1rem",
                "border-radius": "6px",
                "transition": "all 0.3s ease",
                "color": "#e2e8f0"
            },
            "nav-link-selected": {
                "background": "rgba(59, 130, 246, 0.3)",
                "color": "#ffffff",
                "font-weight": "500",
                "transform": "translateX(4px)"
            },
            "icon": {
                "color": "#60a5fa",
                "font-size": "16px",
                "margin-right": "8px"
            },
            "menu-title": {
                "color": "#60a5fa",
                "font-weight": "600",
                "font-size": "16px",
                "text-align": "center",
                "margin-bottom": "0.8rem",
                "padding": "0.5rem"
            }
        }
        
        # Extrair nome limpo da categoria (sem emoji)
        clean_category_name = selected_category.split(' ', 1)[1] if ' ' in selected_category else selected_category
        
        selected_page = option_menu(
            menu_title=f"📋 {clean_category_name}",
            options=menu_structure[selected_category]["pages"],
            icons=menu_structure[selected_category]["page_icons"],
            default_index=0,
            styles=sub_menu_styles,
            key=f"sub_menu_{selected_category.replace(' ', '_')}"
        )
        
        # Breadcrumb navigation
        if selected_page:
            st.markdown(f"""
            <div style="
                margin-top: 1rem;
                padding: 0.8rem;
                background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
                font-size: 12px;
                color: #94a3b8;
                backdrop-filter: blur(5px);
            ">
                🏠 Dashboard → {clean_category_name} → {selected_page}
            </div>
            """, unsafe_allow_html=True)
    
    # Armazenar seleções no session state para uso nas páginas
    if "current_category" not in st.session_state:
        st.session_state.current_category = selected_category
    if "current_page" not in st.session_state:
        st.session_state.current_page = selected_page
    
    st.session_state.current_category = selected_category
    st.session_state.current_page = selected_page

    # Removed: sub-comparison filter, now handled directly on the main page if needed.

# --- Page navigation with hierarchical structure ---
if selected_category == "📊 Overview":
    if selected_page == "Dashboard Overview":
        from dashboard import overview
        overview.run()

elif selected_category == "🔍 Initiative Analysis":
    st.markdown("---")  # Visual separator
    st.markdown(f"### � Initiative Analysis - {selected_page}")  # Page title with sub-page
    
    if selected_page == "Temporal Analysis":
        # Load raw metadata for temporal analysis if not already loaded
        if "metadata" not in st.session_state:
            try:
                from pathlib import Path
                from scripts.utilities.json_interpreter import _load_jsonc_file

                metadata_file_path = (
                    current_dir / "data" / "json" / "initiatives_metadata.jsonc"
                )
                raw_metadata = _load_jsonc_file(metadata_file_path)
                st.session_state.metadata = raw_metadata
            except Exception as e:
                st.error(f"❌ Error loading raw metadata for temporal analysis: {e}")
                st.stop()

        import dashboard.temporal as temporal
        temporal.run()
    
    elif selected_page == "Comparative Analysis":
        import dashboard.comparison as comparison
        comparison.run()
    
    elif selected_page == "Detailed Analysis":
        from dashboard import detailed
        detailed.run()

elif selected_category == "🌾 Agriculture Analysis":
    st.markdown("---")  # Visual separator
    st.markdown(f"### 🌾 Agriculture Analysis - {selected_page}")  # Page title with sub-page
    
    if selected_page == "Crop Calendar":
        # Import and render agricultural dashboard - calendar view
        try:
            from dashboard.components.agricultural.agricultural_dashboard import render_agricultural_dashboard
            # Set specific view for crop calendar
            st.markdown("#### 📅 Brazilian Crop Calendar")
            st.markdown("Interactive calendar showing planting and harvest periods for major crops.")
            
            from scripts.plotting.charts.agricultural_charts import load_conab_data, plot_crop_calendar_heatmap
            with st.spinner("Loading crop calendar data..."):
                detailed_data, calendar_data = load_conab_data()
            
            if calendar_data:
                fig = plot_crop_calendar_heatmap(calendar_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Crop calendar data not available")
        except Exception as e:
            st.error(f"❌ Error loading agricultural calendar: {e}")
    
    elif selected_page == "Agriculture Availability":
        # Import and render agricultural dashboard - full view
        try:
            from dashboard.components.agricultural.agricultural_dashboard import render_agricultural_dashboard
            render_agricultural_dashboard()
        except Exception as e:
            st.error(f"❌ Error loading agricultural dashboard: {e}")
            # Fallback to CONAB module
            from dashboard import conab
            st.session_state.conab_view = "availability"
            conab.run()

# Fallback para caso nenhuma página seja selecionada
if not selected_page:
    st.markdown("### 🏠 Bem-vindo ao LULC Dashboard")
    st.markdown("""
    **Selecione uma categoria no menu lateral para começar:**
    
    - 📊 **Overview**: Visão geral do dashboard
    - 🔍 **Initiative Analysis**: Análises detalhadas das iniciativas (Temporal, Comparativa, Detalhada)
    - 🌾 **Agriculture Analysis**: Análises agrícolas (Calendário de Culturas, Disponibilidade Agrícola)
    """)
