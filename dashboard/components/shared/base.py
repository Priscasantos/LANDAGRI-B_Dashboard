"""
Dashboard Base Components
========================

Shared base components and utilities for all dashboard modules.
Provides consistent functionality across the modular dashboard system.

Author: LANDAGRI-B Project Team   
Date: 2025-07-28
Version: 1.0
"""

import streamlit as st
import pandas as pd
from typing import Any, Dict, Optional
from pathlib import Path
import sys


class DashboardBase:
    @staticmethod
    def validate_data() -> bool:
        """
        Static method to validate that required data is available in session state.
        Returns:
            bool: True if data is valid, False otherwise
        """
        required_keys = ["df_interpreted", "metadata"]
        import streamlit as st
        import pandas as pd
        for key in required_keys:
            if key not in st.session_state:
                st.error(f"❌ Required data '{key}' not found in session state.")
                return False
            data = st.session_state.get(key)
            if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                st.error(f"❌ Data '{key}' is empty or invalid.")
                return False
        return True

    @staticmethod
    def get_data() -> pd.DataFrame:
        """
        Static method to get validated data from session state.
        Returns:
            pd.DataFrame: The main dataframe if valid, else empty DataFrame
        """
        import streamlit as st
        import pandas as pd
        if not DashboardBase.validate_data():
            return pd.DataFrame()
        return st.session_state.get("df_interpreted", pd.DataFrame())

    @staticmethod
    def show_data_info(df: Optional[pd.DataFrame] = None):
        """
        Static method to display information about loaded data in sidebar.
        Args:
            df (pd.DataFrame, optional): DataFrame to show info for. If None, will fetch from session.
        """
        import streamlit as st
        import pandas as pd
        if df is None:
            df = DashboardBase.get_data()
        metadata = st.session_state.get("metadata", {})
        if not df.empty:
            with st.sidebar:
                st.markdown("### 📊 Data Information")
                st.metric("Total Initiatives", len(df))
                st.metric("Metadata Entries", len(metadata))
                if "Type" in df.columns:
                    unique_types = df["Type"].nunique()
                    st.metric("Initiative Types", unique_types)
    """
    Base class for all dashboard components providing common functionality.
    
    Features:
    - Data validation and loading
    - Error handling
    - Session state management
    - Consistent UI patterns
    """
    
    def __init__(self, page_name: str = "Dashboard"):
        """
        Initialize dashboard base component.
        
        Args:
            page_name: Name of the dashboard page
        """
        self.page_name = page_name
        self._setup_paths()
        
    def _setup_paths(self):
        """Setup common paths for data and scripts."""
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.scripts_path = str(self.project_root / "scripts")
        
        # Add scripts to path if not already present
        if self.scripts_path not in sys.path:
            sys.path.insert(0, self.scripts_path)
    
    def validate_session_data(self) -> bool:
        """
        Validate that required data is available in session state.
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        required_keys = ["df_interpreted", "metadata"]
        
        for key in required_keys:
            if key not in st.session_state:
                st.error(f"❌ Required data '{key}' not found in session state.")
                return False
                
            data = st.session_state.get(key)
            if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                st.error(f"❌ Data '{key}' is empty or invalid.")
                return False
                
        return True
    
    def get_session_data(self) -> tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Get validated data from session state.
        
        Returns:
            tuple: (dataframe, metadata)
        """
        if not self.validate_session_data():
            return pd.DataFrame(), {}
            
        return (
            st.session_state.get("df_interpreted", pd.DataFrame()),
            st.session_state.get("metadata", {})
        )
    
    def display_data_info(self):
        """Display information about loaded data in sidebar."""
        df, metadata = self.get_session_data()
        
        if not df.empty:
            with st.sidebar:
                st.markdown("### 📊 Data Information")
                st.metric("Total Initiatives", len(df))
                st.metric("Metadata Entries", len(metadata))
                
                if "Type" in df.columns:
                    unique_types = df["Type"].nunique()
                    st.metric("Initiative Types", unique_types)
    
    def handle_error(self, error: Exception, context: str = ""):
        """
        Handle errors with consistent messaging.
        
        Args:
            error: Exception that occurred
            context: Additional context about where error occurred
        """
        error_msg = f"❌ Error in {self.page_name}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"
        
        st.error(error_msg)
        
        # Display error details in expander for debugging
        with st.expander("🔍 Error Details"):
            st.code(str(error))
    
    def create_info_card(self, title: str, content: str, icon: str = "ℹ️"):
        """
        Create a consistent info card component.
        
        Args:
            title: Card title
            content: Card content
            icon: Icon for the card
        """
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 1rem 0;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #1e293b;">
                {icon} {title}
            </h4>
            <p style="margin: 0; color: #64748b; line-height: 1.6;">
                {content}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_header(self, title: str, subtitle: str = "", gradient_colors: tuple = ("#3b82f6", "#1d4ed8")):
        """
        Display a modern gradient header.
        
        Args:
            title: Main title
            subtitle: Optional subtitle
            gradient_colors: Tuple of gradient colors (start, end)
        """
        gradient = f"linear-gradient(135deg, {gradient_colors[0]} 0%, {gradient_colors[1]} 100%)"
        
        header_html = f"""
        <div style="
            background: {gradient};
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
        ">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                {title}
            </h1>
        """
        
        if subtitle:
            header_html += f"""
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                {subtitle}
            </p>
            """
            
        header_html += "</div>"
        
        st.markdown(header_html, unsafe_allow_html=True)


def apply_modern_dashboard_css():
    """Apply modern CSS styling for dashboard components."""
    st.markdown("""
    <style>
    /* Modern Dashboard Styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Modern metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    
    /* Modern selectbox */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    </style>
    """, unsafe_allow_html=True)


# Export main classes and functions
__all__ = [
    "DashboardBase",
    "apply_modern_dashboard_css"
]
