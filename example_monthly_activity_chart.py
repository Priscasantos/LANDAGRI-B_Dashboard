"""
Example usage of the new Monthly Activities Stacked Bar Chart
=============================================================

This example demonstrates how to use the create_monthly_activities_stacked_bar_chart function
from the charts module.

Author: LANDAGRI-B Project Team 
Date: 2025-08-11
"""

import streamlit as st
import pandas as pd
from dashboard.components.agricultural_analysis.charts import create_monthly_activities_stacked_bar_chart


def demo_monthly_activities_stacked_bar():
    """
    Demonstra o uso do gráfico de atividades mensais empilhadas.
    """
    st.markdown("## 📊 Monthly Activities Stacked Bar Chart Demo")
    
    # Example: Using with col2 layout as shown in your original code
    col1, col2 = st.columns(2)
    
    with col2:
        st.markdown("##### 📊 Atividades por Mês")
        
        # Example filtered_data (replace with your actual data)
        # This should come from your data loading function
        filtered_data = {
            'crop_calendar': {
                # Your actual crop calendar data structure
                # This is just an example structure
                'corn': [
                    {
                        'state': 'São Paulo',
                        'calendar': {
                            'January': 'P',
                            'February': 'P', 
                            'March': 'H',
                            'April': 'H'
                        }
                    }
                ],
                'soy': [
                    {
                        'state': 'Mato Grosso',
                        'calendar': {
                            'October': 'P',
                            'November': 'P',
                            'February': 'H',
                            'March': 'H'
                        }
                    }
                ]
            }
        }
        
        # Create the stacked bar chart
        fig_bars = create_monthly_activities_stacked_bar_chart(filtered_data)
        
        if fig_bars:
            st.plotly_chart(fig_bars, use_container_width=True, key="monthly_activities_bars")
        else:
            st.warning("No data available for monthly activities chart")


def main():
    """Main function for the demo."""
    st.set_page_config(
        page_title="Monthly Activities Chart Demo",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Monthly Activities Stacked Bar Chart Demo")
    st.markdown("---")
    
    demo_monthly_activities_stacked_bar()
    
    st.markdown("---")
    st.markdown("### 💡 How to Use")
    st.markdown("""
    1. **Import the function:**
       ```python
       from dashboard.components.agricultural_analysis.charts import create_monthly_activities_stacked_bar_chart
       ```
    
    2. **Call the function with your filtered data:**
       ```python
       fig = create_monthly_activities_stacked_bar_chart(filtered_data)
       ```
    
    3. **Display the chart:**
       ```python
       if fig:
           st.plotly_chart(fig, use_container_width=True, key="monthly_activities_bars")
       ```
    
    **Data Structure Expected:**
    The function expects `filtered_data` to have a `crop_calendar` key containing
    a dictionary where each crop has a list of states with calendar information.
    
    **Chart Features:**
    - **P (Green)**: Planting activities only
    - **H (Orange)**: Harvesting activities only  
    - **PH (Blue)**: Both planting and harvesting activities
    - Stacked bars showing distribution by month
    - Responsive design with container width
    """)


if __name__ == "__main__":
    main()
