import streamlit as st
from streamlit_option_menu import option_menu
import os
import warnings
import sys
from pathlib import Path
import pandas as pd # Added import for pandas

# Add scripts directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "scripts"))

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
@st.cache_data(ttl=None) # Set ttl=None for indefinite caching until code/input changes
def load_cached_data():
    """Loads and caches the main dashboard data using JSON interpreter"""
    try:
        # Path already corrected in previous step to remove "raw"
        metadata_file_path = current_dir / "data" / "initiatives_metadata.jsonc"
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
    menu_items={
        'Report a bug': None,
        'Get Help': None,
        'About': None
    }
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
if 'df_interpreted' not in st.session_state or st.session_state.df_interpreted is None:
    df_loaded = load_cached_data() # Call the cached function
    if df_loaded is not None and not df_loaded.empty:
        st.session_state.df_interpreted = df_loaded
        # Optionally, store raw metadata if your interpreter provides it separately
        # and if it's not already handled by load_cached_data or needed globally earlier.
        # For now, assuming interpret_initiatives_metadata primarily returns the DataFrame.
        # If raw metadata is also needed in session_state from the start:
        # try:
        #     from scripts.utilities.json_interpreter import _load_jsonc_file
        #     metadata_file_path = current_dir / "data" / "initiatives_metadata.jsonc"
        #     raw_metadata = _load_jsonc_file(metadata_file_path)
        #     st.session_state.metadata = raw_metadata
        # except Exception as e_meta:
        #     st.error(f"❌ Error loading initial raw metadata in app.py: {e_meta}")
        #     st.session_state.metadata = {}
    elif df_loaded is None:
        # Error messages are handled within load_cached_data, but we might want to stop 
        # or ensure pages handle the lack of data gracefully.
        st.error("Initial data loading failed. Some dashboard features may not work.")
        # To prevent pages from running without data, you might initialize df_interpreted to an empty df
        # or handle this explicitly in each page's run() method.
        st.session_state.df_interpreted = pd.DataFrame() # Ensure it exists, even if empty

# Hide Streamlit's default sidebar navigation (multipage menu)
# This is done because we are using streamlit-option-menu for a custom sidebar.
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# --- Custom sidebar with new structure ---
with st.sidebar:
    selected = option_menu(
        menu_title="🛰️ LANDAGRI-B Dashboard", # Main title of the menu
        options=[
            "Overview", # Option 1
            "Comparative Analysis", # Option 2
            "Temporal Analysis", # Option 3
            "Detailed Analysis", # Option 4
            "Agricultural Analysis" # Option 5 - New CONAB tab
        ],
        icons=["globe-americas", "bar-chart-steps", "clock-history", "layers", "seedling"], # Icons for each option
        menu_icon="satellite", # Icon for the menu title
        default_index=0, # Default selected option
        styles={
            "container": {"padding": "0.5rem", "background-color": "transparent"},
            "icon": {"color": "#60a5fa", "font-size": "20px"}, # Icon color and size
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "0.2rem 0",
                "padding": "0.8rem 1rem",
                "border-radius": "0.7rem",
                "font-family": "Inter, Roboto, Segoe UI, Arial, sans-serif",
                "background": "rgba(148, 163, 184, 0.1)", # Default nav link background
                "border-left": "3px solid transparent", # For hover effect
                "transition": "all 0.3s ease" # Smooth transition
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)", # Selected nav link background
                "color": "#ffffff", # Selected nav link text color
                "font-weight": "600",
                "border-left": "3px solid #60a5fa", # Accent border for selected link
                "box-shadow": "0 3px 10px rgba(59, 130, 246, 0.3)" # Subtle shadow for selected link
            },
            "menu-title": {
                "color": "#60a5fa", # Menu title color
                "font-weight": "700", 
                "font-size": "20px",
                "text-align": "center",
                "margin-bottom": "1rem",
                "padding": "0.5rem",
                "background": "rgba(59, 130, 246, 0.1)", # Light background for menu title
                "border-radius": "0.5rem" # Rounded corners for menu title background
            }
        }
    )
    
    # Removed: sub-comparison filter, now handled directly on the main page if needed.

# --- Page navigation with new structure ---
if selected == "Overview":
    from dashboard import overview # Corrected import
    overview.run()
    
elif selected == "Comparative Analysis":
    st.markdown("---") # Visual separator
    st.markdown("### 📊 Comparative Analysis") # Page title
    # The comparison type is now primarily defined by the sidebar menu.
    # If sub-selections are needed within this page, they should be handled inside comparison.run()
    
    import dashboard.comparison as comparison # Ensure this module is translated
    comparison.run()

elif selected == "Temporal Analysis":
    st.markdown("---") # Visual separator
    st.markdown("### ⏳ Temporal Analysis") # Page title
    
    # Load raw metadata for temporal analysis if not already loaded
    if 'metadata' not in st.session_state:
        try:
            from scripts.utilities.json_interpreter import _load_jsonc_file
            from pathlib import Path
            
            # current_dir is already defined at the top of app.py
            # Adjusted path: removed "raw"
            metadata_file_path = current_dir / "data" / "initiatives_metadata.jsonc" 
            raw_metadata = _load_jsonc_file(metadata_file_path)
            st.session_state.metadata = raw_metadata
        except Exception as e:
            st.error(f"❌ Error loading raw metadata for temporal analysis: {e}")
            st.stop()
    
    import dashboard.temporal as temporal
    temporal.run()
    
elif selected == "Detailed Analysis":
    from dashboard import detailed 
    detailed.run()

elif selected == "Agricultural Analysis":
    st.markdown("---") # Visual separator
    st.markdown("### 🌾 Agricultural Analysis") # Page title

    from dashboard import conab
    conab.run()
