## 📊 Monthly Activities Stacked Bar Chart

### Overview
The `create_monthly_activities_stacked_bar_chart` function creates a stacked bar chart showing the distribution of agricultural activities by month, categorized by type (P, H, PH).

### Location
File: `dashboard/components/agricultural_analysis/charts/calendar/monthly_activity_charts.py`

### Import
```python
from dashboard.components.agricultural_analysis.charts import create_monthly_activities_stacked_bar_chart
```

### Function Signature
```python
def create_monthly_activities_stacked_bar_chart(filtered_data: dict) -> Optional[go.Figure]:
```

### Usage Example
```python
import streamlit as st
from dashboard.components.agricultural_analysis.charts import create_monthly_activities_stacked_bar_chart

# In your Streamlit app
col1, col2 = st.columns(2)

with col2:
    st.markdown("##### 📊 Atividades por Mês")
    
    # Create the stacked bar chart
    fig_bars = create_monthly_activities_stacked_bar_chart(filtered_data)
    
    if fig_bars:
        st.plotly_chart(fig_bars, use_container_width=True, key="monthly_activities_bars")
    else:
        st.info("No data available for monthly activities chart")
```

### Parameters
- **filtered_data** (dict): Dictionary containing crop calendar data with the following structure:
  ```python
  {
      'crop_calendar': {
          'crop_name': [
              {
                  'state': 'State Name',
                  'calendar': {
                      'January': 'P',   # P = Planting only
                      'February': 'H',  # H = Harvesting only
                      'March': 'PH',    # PH = Both planting and harvesting
                      # ... other months
                  }
              }
          ]
      }
  }
  ```

### Return Value
- **go.Figure or None**: Plotly figure object if data is available, None otherwise

### Chart Features
1. **Activity Types**:
   - **P (Green #2E8B57)**: Planting activities only
   - **H (Orange #FF6B35)**: Harvesting activities only  
   - **PH (Blue #4682B4)**: Both planting and harvesting activities

2. **Chart Properties**:
   - Stacked bar chart showing monthly distribution
   - 45-degree rotated month labels for better readability
   - Responsive design with container width
   - Hover tooltips with detailed information
   - Horizontal legend positioned at the top

### Data Processing
The function:
1. Extracts crop calendar data from the filtered dataset
2. Maps full month names to abbreviations (Jan, Feb, Mar, etc.)
3. Counts activities by type for each month
4. Creates a pandas DataFrame in the correct format for Plotly
5. Generates a stacked bar chart with custom styling

### Error Handling
- Returns None if no crop calendar data is available
- Shows info message if no monthly activities are found
- Handles exceptions gracefully with error messages
- Validates data structure before processing

### Notes
- The chart uses month abbreviations (Jan, Feb, Mar) for better display
- Activities marked as 'PH' are counted as both planting and harvesting
- Colors are consistent with the agricultural theme
- Chart height is set to 400px for optimal display
