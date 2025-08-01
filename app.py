import os
import sys
import warnings
from pathlib import Path

import pandas as pd  # Added import for pandas
import streamlit as st
from streamlit_option_menu import option_menu

# Add paths for imports
current_dir = Path(__file__).parent
root_path = str(current_dir)
scripts_path = str(current_dir / "scripts")

# Add both root and scripts to Python path
for path in [root_path, scripts_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Initialize modern themes system
try:
    from scripts.utilities.modern_themes import ModernThemes

    # Setup the modern theme globally
    ModernThemes.setup_modern_theme()
except ImportError as e:
    st.warning(f"⚠️ Modern themes system not available: {e}")

# Updated import using the new JSON interpreter
try:
    from scripts.utilities.json_interpreter import interpret_initiatives_metadata
except ImportError as e:
    st.error(f"❌ Error importing JSON interpreter: {e}")
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
    page_title="LANDAGRI-B Dashboard",
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
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
        border-right: 3px solid #3b82f6; /* Accent border */
        box-shadow: 2px 0 15px rgba(15, 23, 42, 0.1);
    }
    /* Style for the first element in sidebar (often the menu title container) */
    .stSidebar .element-container:first-child {
        background: rgba(59, 130, 246, 0.08); /* Light blue accent */
        border-radius: 0.75rem;
        margin-bottom: 1.2rem;
        padding: 0.8rem;
        border: 1px solid rgba(59, 130, 246, 0.15);
    }
    .stSidebar * {
        color: #1e293b !important; /* Dark text color for sidebar */
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #1e293b !important; /* Dark color for sidebar headers */
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
            "page_icons": ["speedometer2"],
        },
        "🔍 Initiative Analysis": {
            "icon": "search",
            "pages": ["Temporal Analysis", "Comparative Analysis", "Detailed Analysis"],
            "page_icons": ["calendar-event", "bar-chart", "zoom-in"],
        },
        "🌾 Agriculture Analysis": {
            "icon": "leaf",
            "pages": ["Crop Calendar", "Agriculture Availability"],
            "page_icons": ["calendar3", "graph-up-arrow"],
        },
    }

    # Estilos modernos para o menu hierárquico
    modern_menu_styles = {
        "container": {
            "padding": "0.8rem",
            "background": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)",
            "border-radius": "16px",
            "box-shadow": "0 10px 40px rgba(15, 23, 42, 0.15)",
            "backdrop-filter": "blur(10px)",
            "border": "1px solid rgba(148, 163, 184, 0.2)",
        },
        "nav-link": {
            "font-size": "16px",
            "text-align": "left",
            "margin": "0.4rem 0",
            "padding": "1.2rem 1.4rem",
            "border-radius": "12px",
            "transition": "all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)",
            "background": "rgba(255, 255, 255, 0.7)",
            "border-left": "4px solid transparent",
            "backdrop-filter": "blur(5px)",
            "color": "#1e293b",
            "font-weight": "500",
            "box-shadow": "0 2px 8px rgba(15, 23, 42, 0.08)",
        },
        "nav-link-selected": {
            "background": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
            "color": "#ffffff",
            "font-weight": "600",
            "transform": "translateX(8px) scale(1.02)",
            "box-shadow": "0 8px 25px rgba(59, 130, 246, 0.35)",
            "border-left": "4px solid #60a5fa",
        },
        "icon": {"color": "#475569", "font-size": "18px", "margin-right": "12px"},
        # Menu Title - LANDAGRI-B
        "menu-title": {
            "color": "#1e293b",
            "font-weight": "700",
            "font-size": "24px",
            "text-align": "center",
            "margin-bottom": "1.8rem",
            "padding": "1.2rem",
            "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.05) 100%)",
            "border-radius": "12px",
            "border": "1px solid rgba(59, 130, 246, 0.15)",
            "box-shadow": "0 4px 20px rgba(59, 130, 246, 0.1)",
        },
    }

    # Menu principal - categorias
    selected_category = option_menu(
        menu_title="🛰️ LANDAGRI-B Dashboard",
        options=list(menu_structure.keys()),
        icons=[menu_structure[cat]["icon"] for cat in menu_structure],
        default_index=0,
        styles=modern_menu_styles,
        key="main_category_menu",
    )

    # Sub-menu para categoria selecionada
    selected_page = None
    if selected_category in menu_structure:
        st.markdown("---")

        # Estilos para sub-menu
        sub_menu_styles = {
            "container": {
                "padding": "0.6rem",
                "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(29, 78, 216, 0.05) 100%)",
                "border-radius": "12px",
                "border": "1px solid rgba(59, 130, 246, 0.15)",
                "box-shadow": "0 4px 15px rgba(59, 130, 246, 0.1)",
            },
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "0.3rem 0",
                "padding": "1rem 1.2rem",
                "border-radius": "8px",
                "transition": "all 0.3s ease",
                "color": "#334155",
                "background": "rgba(255, 255, 255, 0.6)",
                "font-weight": "500",
                "box-shadow": "0 1px 4px rgba(15, 23, 42, 0.05)",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(29, 78, 216, 0.15) 100%)",
                "color": "#1e40af",
                "font-weight": "600",
                "transform": "translateX(4px)",
                "box-shadow": "0 3px 12px rgba(59, 130, 246, 0.2)",
            },
            "icon": {"color": "#475569", "font-size": "16px", "margin-right": "8px"},
            "menu-title": {
                "color": "#1e293b",
                "font-weight": "600",
                "font-size": "16px",
                "text-align": "center",
                "margin-bottom": "1rem",
                "padding": "0.8rem",
            },
        }

        # Extrair nome limpo da categoria (sem emoji)
        clean_category_name = (
            selected_category.split(" ", 1)[1]
            if " " in selected_category
            else selected_category
        )

        selected_page = option_menu(
            menu_title=f"📋 {clean_category_name}",
            options=menu_structure[selected_category]["pages"],
            icons=menu_structure[selected_category]["page_icons"],
            default_index=0,
            styles=sub_menu_styles,
            key=f"sub_menu_{selected_category.replace(' ', '_')}",
        )

        # Breadcrumb navigation
        if selected_page:
            st.markdown(
                f"""
            <div style="
                margin-top: 1.2rem;
                padding: 1rem;
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(29, 78, 216, 0.03) 100%);
                border-radius: 10px;
                border: 1px solid rgba(59, 130, 246, 0.1);
                font-size: 13px;
                color: #475569;
                backdrop-filter: blur(5px);
                font-weight: 500;
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.05);
            ">
                🏠 <span style="color: #1e293b; font-weight: 600;">Dashboard</span> →
                <span style="color: #334155; font-weight: 600;">{clean_category_name}</span> →
                <span style="color: #3b82f6; font-weight: 700;">{selected_page}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

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
    if selected_page in [
        "Temporal Analysis",
        "Comparative Analysis",
        "Detailed Analysis",
    ]:
        # Usar o novo orchestrator consolidado para análise de iniciativas
        from dashboard import initiative_analysis

        initiative_analysis.run()

elif selected_category == "🌾 Agriculture Analysis":
    # Usar o novo orchestrator consolidado para análise agrícola
    from dashboard import agricultural_analysis

    agricultural_analysis.run()

# Fallback para caso nenhuma página seja selecionada
if not selected_page:
    st.markdown("### 🏠 Bem-vindo ao LANDAGRI-B Dashboard")
    st.markdown(
        """
    **Selecione uma categoria no menu lateral para começar:**

    - 📊 **Overview**: Visão geral do dashboard
    - 🔍 **Initiative Analysis**: Análises detalhadas das iniciativas (Temporal, Comparativa, Detalhada)
    - 🌾 **Agriculture Analysis**: Análises agrícolas (Calendário de Culturas, Disponibilidade Agrícola)
    """
    )
