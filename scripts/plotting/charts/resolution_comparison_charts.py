import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Attempt to import common chart utilities, handle if not found for robustness
try:
    from scripts.plotting.chart_core import apply_standard_layout, smart_cache_data
except ImportError:
    # Define dummy decorators/functions if chart_core is not available
    # This allows the file to be imported and functions defined, even if core utilities are missing.
    def smart_cache_data(ttl=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def apply_standard_layout(fig, title="", xaxis_title="", yaxis_title=""):
        fig.update_layout(title_text=title, xaxis_title_text=xaxis_title, yaxis_title_text=yaxis_title)
        # Add any other minimal layout defaults here if needed
        return fig

@smart_cache_data(ttl=300)
def plot_resolution_vs_launch_year(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Scatter Plot: Resolution vs. Year of Launch.
    Shows the relationship between spatial resolution and the year each initiative began.
    X-axis: Year of first map release or main operational year.
    Y-axis: Spatial resolution (log scale recommended).
    Points: Each initiative, labeled with acronym.
    Highlight CGLS (PROBA-V, 100 m) for contrast.
    """
    if filtered_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution vs. Launch Year", "Start Year", "Resolution (m)")
        fig.add_annotation(text="No data available for the selected filters.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    # Ensure required columns are present and numeric where needed
    if 'Start_Year' not in filtered_df.columns or 'Resolution' not in filtered_df.columns:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution vs. Launch Year", "Start Year", "Resolution (m)")
        fig.add_annotation(text="Missing 'Start_Year' or 'Resolution' data.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    plot_df = filtered_df.copy()
    plot_df['Resolution'] = pd.to_numeric(plot_df['Resolution'], errors='coerce')
    plot_df['Start_Year'] = pd.to_numeric(plot_df['Start_Year'], errors='coerce') # Ensure Start_Year is numeric for plotting
    plot_df.dropna(subset=['Resolution', 'Start_Year'], inplace=True)

    if plot_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution vs. Launch Year", "Start Year", "Resolution (m)")
        fig.add_annotation(text="No valid numeric data for Resolution or Start Year.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    # Determine Display_Name (Acronym or fallback)
    if 'Display_Name' not in plot_df.columns:
        if 'Acronym' in plot_df.columns:
            plot_df['Display_Name'] = plot_df['Acronym']
        elif 'Name' in plot_df.columns:
            plot_df['Display_Name'] = plot_df['Name'].str[:15] # Fallback to truncated name
        else:
            plot_df['Display_Name'] = "N/A" 

    # Highlight CGLS
    # Create a 'color_col', 'size_col', 'symbol_col' for px.scatter arguments
    plot_df['color_col'] = 'rgba(31, 119, 180, 0.7)' # Default color
    plot_df['size_col'] = 10 # Default size
    plot_df['symbol_col'] = 'circle' # Default symbol

    # Identify CGLS - assuming it might be in 'Acronym' or 'Name'
    # More robust CGLS identification might be needed if Display_Name is too generic
    cgls_mask = plot_df['Display_Name'].str.contains("CGLS", case=False, na=False) 
    # As a fallback, check original 'Name' or 'Acronym' if Display_Name was a generic fallback
    if not cgls_mask.any() and 'Name' in plot_df.columns:
        cgls_mask = plot_df['Name'].str.contains("CGLS", case=False, na=False)
    if not cgls_mask.any() and 'Acronym' in plot_df.columns:
        cgls_mask = plot_df['Acronym'].str.contains("CGLS", case=False, na=False)

    if cgls_mask.any():
        plot_df.loc[cgls_mask, 'color_col'] = 'rgba(255, 127, 14, 1)' # Orange for CGLS
        plot_df.loc[cgls_mask, 'size_col'] = 15
        plot_df.loc[cgls_mask, 'symbol_col'] = 'star'

    fig = px.scatter(
        plot_df,
        x='Start_Year',
        y='Resolution',
        text='Display_Name', 
        hover_name='Display_Name',
        hover_data={
            'Start_Year': True,
            'Resolution': ':.0f m',
            'Display_Name': False,
            'color_col': False, # Don't show these helper columns in hover
            'size_col': False,
            'symbol_col': False
        },
        color='color_col', 
        color_discrete_map="identity",
        size='size_col', 
        symbol='symbol_col' 
    )

    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1, color='DarkSlateGrey')),
        textfont_size=9
    )
    
    apply_standard_layout(
        fig, 
        title="Spatial Resolution vs. Launch Year of Initiatives", 
        xaxis_title="Year of First Map Release / Main Operational Year", 
        yaxis_title="Spatial Resolution (meters) - Log Scale"
    )
    
    fig.update_layout(
        yaxis_type="log",
        showlegend=False 
    )

    return fig

@smart_cache_data(ttl=300)
def plot_initiatives_by_resolution_category(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Stacked Bar Chart: Number of Initiatives per Resolution Category.
    Summarizes how many initiatives fall into each resolution class.
    X-axis: Resolution categories (e.g., ≤10 m, 11–30 m, 31–100 m, >100 m).
    Y-axis: Count of initiatives.
    Color segments: Regional vs. global initiatives, or by sensor type (using Type column for now).
    """
    if filtered_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Initiatives by Resolution Category", "Resolution Category", "Number of Initiatives")
        fig.add_annotation(text="No data available for the selected filters.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    if 'Resolution' not in filtered_df.columns or 'Type' not in filtered_df.columns:
        fig = go.Figure()
        apply_standard_layout(fig, "Initiatives by Resolution Category", "Resolution Category", "Number of Initiatives")
        fig.add_annotation(text="Missing 'Resolution' or 'Type' data.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    plot_df = filtered_df.copy()
    plot_df['Resolution'] = pd.to_numeric(plot_df['Resolution'], errors='coerce')
    plot_df.dropna(subset=['Resolution'], inplace=True)

    if plot_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Initiatives by Resolution Category", "Resolution Category", "Number of Initiatives")
        fig.add_annotation(text="No valid numeric data for Resolution.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    # Define resolution categories and labels
    bins = [0, 10, 30, 100, float('inf')]
    labels = ['≤10 m', '11–30 m', '31–100 m', '>100 m']
    plot_df['Resolution_Category'] = pd.cut(plot_df['Resolution'], bins=bins, labels=labels, right=True)

    # Ensure 'Type' is treated as categorical and fill NA for grouping
    plot_df['Type'] = plot_df['Type'].astype(str).fillna('Unknown')

    # Group by Resolution_Category and Type to get counts for stacking
    category_counts = plot_df.groupby(['Resolution_Category', 'Type'], observed=False).size().reset_index(name='Count')

    if category_counts.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Initiatives by Resolution Category", "Resolution Category", "Number of Initiatives")
        fig.add_annotation(text="No initiatives to categorize.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    fig = px.bar(
        category_counts,
        x='Resolution_Category',
        y='Count',
        color='Type',
        text_auto=True, # Display count on bars
        hover_name='Type',
        hover_data={'Count': True, 'Resolution_Category': True, 'Type': False}
    )

    apply_standard_layout(
        fig,
        title="Number of Initiatives by Resolution Category",
        xaxis_title="Spatial Resolution Category",
        yaxis_title="Number of Initiatives"
    )
    
    fig.update_layout(
        barmode='stack',
        xaxis_categoryorder='array', # Ensure categories are in the defined order
        xaxis_categoryarray=labels,
        legend_title_text='Initiative Type'
    )

    return fig

@smart_cache_data(ttl=300)
def plot_resolution_coverage_heatmap(filtered_df: pd.DataFrame) -> go.Figure:
    """
    Heatmap: Resolution vs. Coverage Type.
    Visualizes how spatial resolution varies by geographic coverage.
    X-axis: Coverage type (global, continental, regional, national) - maps to 'Type' column.
    Y-axis: Resolution bins.
    Cell color: Number of initiatives in each cell.
    """
    if filtered_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution vs. Coverage Type Heatmap", "Coverage Type (Initiative Type)", "Resolution Category")
        fig.add_annotation(text="No data available for the selected filters.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    if 'Resolution' not in filtered_df.columns or 'Type' not in filtered_df.columns:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution vs. Coverage Type Heatmap", "Coverage Type (Initiative Type)", "Resolution Category")
        fig.add_annotation(text="Missing 'Resolution' or 'Type' data.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    plot_df = filtered_df.copy()
    plot_df['Resolution'] = pd.to_numeric(plot_df['Resolution'], errors='coerce')
    plot_df.dropna(subset=['Resolution'], inplace=True)

    if plot_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution vs. Coverage Type Heatmap", "Coverage Type (Initiative Type)", "Resolution Category")
        fig.add_annotation(text="No valid numeric data for Resolution.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    # Define resolution categories and labels (consistent with the bar chart)
    bins = [0, 10, 30, 100, float('inf')]
    resolution_labels = ['≤10 m', '11–30 m', '31–100 m', '>100 m']
    plot_df['Resolution_Category'] = pd.cut(plot_df['Resolution'], bins=bins, labels=resolution_labels, right=True)

    # Ensure 'Type' is treated as categorical and fill NA for grouping
    plot_df['Type'] = plot_df['Type'].astype(str).fillna('Unknown')
    # Get unique types for X-axis order if needed, or let Plotly handle it
    coverage_types = sorted(plot_df['Type'].unique().tolist())

    # Create the pivot table for the heatmap
    heatmap_data = plot_df.groupby(['Resolution_Category', 'Type'], observed=False).size().unstack(fill_value=0)
    
    # Ensure all defined resolution labels are present in the index, even if no data
    heatmap_data = heatmap_data.reindex(index=resolution_labels, fill_value=0)
    # Ensure all coverage types are present in columns
    heatmap_data = heatmap_data.reindex(columns=coverage_types, fill_value=0)

    if heatmap_data.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution vs. Coverage Type Heatmap", "Coverage Type (Initiative Type)", "Resolution Category")
        fig.add_annotation(text="No data to display in heatmap.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis', # Or any other colorscale like 'Blues', 'YlGnBu'
        hoverongaps=False,
        text=heatmap_data.values, # Show count on cells
        texttemplate="%{text}", # Format for text on cells
        colorbar_title='Number of Initiatives'
    ))

    apply_standard_layout(
        fig,
        title="Heatmap: Resolution vs. Coverage Type",
        xaxis_title="Coverage Type (Initiative Type)",
        yaxis_title="Spatial Resolution Category"
    )
    
    fig.update_layout(
        # Ensure y-axis categories are in the desired order (reversed for typical heatmap bottom-to-top)
        yaxis_categoryorder='array',
        yaxis_categoryarray=resolution_labels[::-1], # Show ≤10m at the top, >100m at bottom
        xaxis_categoryorder='array',
        xaxis_categoryarray=coverage_types # Order coverage types alphabetically or by a custom logic if needed
    )

    return fig

@smart_cache_data(ttl=300)
def plot_resolution_by_sensor_family(filtered_df: pd.DataFrame, sensors_meta: dict) -> go.Figure:
    """
    Boxplot: Distribution of Spatial Resolution by Sensor Family.
    Compares the spread and median of spatial resolutions grouped by sensor family.
    X-axis: Sensor family (e.g., Sentinel, Landsat, MODIS, PROBA-V).
    Y-axis: Spatial resolution (meters).
    Boxplot: Shows median, quartiles, and outliers.
    """
    if filtered_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution by Sensor Family", "Sensor Family", "Spatial Resolution (m)")
        fig.add_annotation(text="No initiative data available.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    if not sensors_meta:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution by Sensor Family", "Sensor Family", "Spatial Resolution (m)")
        fig.add_annotation(text="Sensor metadata not available.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    if 'Resolution' not in filtered_df.columns or 'Sensors_Referenced' not in filtered_df.columns:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution by Sensor Family", "Sensor Family", "Spatial Resolution (m)")
        fig.add_annotation(text="Missing 'Resolution' or 'Sensors_Referenced' data in initiatives.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    plot_data = []
    processed_df = filtered_df.copy()
    processed_df['Resolution'] = pd.to_numeric(processed_df['Resolution'], errors='coerce')
    processed_df.dropna(subset=['Resolution', 'Sensors_Referenced'], inplace=True)

    # Define a helper to get sensor family (can be expanded)
    def get_sensor_family(sensor_key, meta):
        if not isinstance(sensor_key, str) or not isinstance(meta, dict):
            return "Unknown"
        
        sensor_details = meta.get(sensor_key, {})
        family = sensor_details.get('family') # Prioritize 'family' field
        if family and isinstance(family, str):
            return family
        
        # Fallback: Infer from sensor_key or platform
        # This is a simple inference, can be made more sophisticated
        name_to_check = sensor_key.lower()
        platform = sensor_details.get('platform', "").lower() if isinstance(sensor_details.get('platform'), str) else ""

        if "sentinel-1" in name_to_check or "sentinel 1" in platform or "s1" in name_to_check.split('-'):
            return "Sentinel-1"
        if "sentinel-2" in name_to_check or "sentinel 2" in platform or "s2" in name_to_check.split('-'):
            return "Sentinel-2"
        if "sentinel-3" in name_to_check or "sentinel 3" in platform or "s3" in name_to_check.split('-'):
            return "Sentinel-3" # Or group all Sentinels if preferred
        if "sentinel" in name_to_check or "sentinel" in platform:
             return "Sentinel (Other)"
        if "landsat" in name_to_check or "landsat" in platform:
            return "Landsat"
        if "modis" in name_to_check or "modis" in platform:
            return "MODIS"
        if "proba-v" in name_to_check or "proba v" in platform or "proba_v" in name_to_check:
            return "PROBA-V"
        if "spot" in name_to_check or "spot" in platform:
            return "SPOT"
        if "planet" in name_to_check or "planetscope" in name_to_check or "rapideye" in name_to_check:
            return "Planet/RapidEye"
        # Add more specific families as needed
        return sensor_details.get('platform', "Unknown") # Fallback to platform if no family found

    for _, row in processed_df.iterrows():
        resolution = row['Resolution']
        sensors = row['Sensors_Referenced']
        initiative_name = row.get('Display_Name', row.get('Acronym', row.get('Name', 'Unknown Initiative')))

        if pd.isna(resolution) or not sensors:
            continue

        # Sensors_Referenced can be a list of strings or a list of dicts
        current_initiative_families = set()
        if isinstance(sensors, list):
            for sensor_ref in sensors:
                sensor_key = None
                if isinstance(sensor_ref, dict):
                    sensor_key = sensor_ref.get('sensor_key')
                elif isinstance(sensor_ref, str):
                    sensor_key = sensor_ref
                
                if sensor_key:
                    family = get_sensor_family(sensor_key, sensors_meta)
                    if family != "Unknown": # Only add if family is identified
                        current_initiative_families.add(family)
        
        for family in current_initiative_families:
            plot_data.append({
                'Sensor_Family': family,
                'Resolution': resolution,
                'Initiative': initiative_name
            })

    if not plot_data:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution by Sensor Family", "Sensor Family", "Spatial Resolution (m)")
        fig.add_annotation(text="No data to display after processing sensors.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    plot_df_final = pd.DataFrame(plot_data)

    fig = px.box(
        plot_df_final,
        x='Sensor_Family',
        y='Resolution',
        color='Sensor_Family', # Color by family for distinction
        points="outliers", # Show outliers
        hover_data=['Initiative'] # Show initiative name on hover
    )

    apply_standard_layout(
        fig,
        title="Distribution of Spatial Resolution by Sensor Family",
        xaxis_title="Sensor Family",
        yaxis_title="Spatial Resolution (meters) - Log Scale Recommended"
    )
    
    fig.update_layout(
        yaxis_type="log", # Log scale for resolution is often better
        showlegend=False # Legend not essential if colors match x-axis categories
    )
    fig.update_xaxes(categoryorder='array', categoryarray=sorted(plot_df_final['Sensor_Family'].unique()))

    return fig

@smart_cache_data(ttl=300)
def plot_resolution_slopegraph(filtered_df: pd.DataFrame, sensors_meta: dict) -> go.Figure:
    """
    Combined Table-Chart (Slopegraph): Resolution Improvement Over Time.
    Shows how the same initiative improved spatial resolution over time.
    List initiatives on the left.
    Draw lines to spatial resolution values on the right, with years annotated.
    Highlight transitions (e.g., from 30 m to 10 m with Sentinel-2 adoption).
    """
    if filtered_df.empty:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution Improvement Over Time", "Year", "Spatial Resolution (m)")
        fig.add_annotation(text="No initiative data available.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    if not sensors_meta:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution Improvement Over Time", "Year", "Spatial Resolution (m)")
        fig.add_annotation(text="Sensor metadata not available.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    if 'Sensors_Referenced' not in filtered_df.columns:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution Improvement Over Time", "Year", "Spatial Resolution (m)")
        fig.add_annotation(text="Missing 'Sensors_Referenced' data.", xref="paper", yref="paper", showarrow=False, font=dict(size=14))
        return fig

    slope_graph_points = []
    initiatives_with_changes = set()

    for _, row in filtered_df.iterrows():
        initiative_name = row.get('Display_Name', row.get('Acronym', row.get('Name', 'Unknown Initiative')))
        sensors_referenced = row.get('Sensors_Referenced')

        if not isinstance(sensors_referenced, list):
            continue

        initiative_resolutions_by_year = {}

        for sensor_entry in sensors_referenced:
            if isinstance(sensor_entry, dict):
                sensor_key = sensor_entry.get('sensor_key')
                years_used = sensor_entry.get('years_used')

                if not sensor_key or not years_used or not isinstance(years_used, list) or not years_used:
                    continue
                
                sensor_detail = sensors_meta.get(str(sensor_key))
                if not sensor_detail or 'resolution' not in sensor_detail:
                    continue
                
                # Ensure resolution is numeric, skip if not
                try:
                    resolution = pd.to_numeric(sensor_detail['resolution'])
                    if pd.isna(resolution):
                        continue
                except ValueError:
                    continue

                # Use the minimum year from years_used as the representative year for this sensor's resolution
                # Ensure years are integers
                valid_years = [int(y) for y in years_used if str(y).isdigit()]
                if not valid_years:
                    continue
                event_year = min(valid_years)

                # If multiple sensors provide resolution for the same year, take the best (lowest numeric value)
                if event_year not in initiative_resolutions_by_year or resolution < initiative_resolutions_by_year[event_year]:
                    initiative_resolutions_by_year[event_year] = resolution
            # We are not handling simple list of sensor strings for slopegraph as year info is missing

        if len(initiative_resolutions_by_year) >= 2:
            sorted_years = sorted(initiative_resolutions_by_year.keys())
            # Check if resolution actually changes over time
            unique_resolutions_in_time = {initiative_resolutions_by_year[year] for year in sorted_years}
            
            if len(unique_resolutions_in_time) > 1: # More than one unique resolution value
                initiatives_with_changes.add(initiative_name)
                for year_point in sorted_years:
                    slope_graph_points.append({
                        'Initiative': initiative_name,
                        'Year': year_point,
                        'Resolution': initiative_resolutions_by_year[year_point]
                    })
    
    if not slope_graph_points or not initiatives_with_changes:
        fig = go.Figure()
        apply_standard_layout(fig, "Resolution Improvement Over Time", "Year", "Spatial Resolution (m)")
        fig.add_annotation(text="No initiatives found with documented resolution changes over time through sensor updates.", 
                           xref="paper", yref="paper", showarrow=False, font=dict(size=12), align="center", width=500)
        return fig

    plot_df_final = pd.DataFrame(slope_graph_points)
    # Ensure Year and Resolution are numeric for plotting
    plot_df_final['Year'] = pd.to_numeric(plot_df_final['Year'])
    plot_df_final['Resolution'] = pd.to_numeric(plot_df_final['Resolution'])
    plot_df_final.sort_values(by=['Initiative', 'Year'], inplace=True)

    fig = px.line(
        plot_df_final,
        x='Year',
        y='Resolution',
        color='Initiative',
        markers=True,
        text='Resolution' # Show resolution value on markers
    )

    fig.update_traces(textposition='top right', textfont_size=9)

    apply_standard_layout(
        fig,
        title="Resolution Improvement Over Time for Initiatives",
        xaxis_title="Year",
        yaxis_title="Spatial Resolution (meters) - Log Scale"
    )
    
    fig.update_layout(
        yaxis_type="log",
        legend_title_text='Initiative'
    )
    # Ensure x-axis shows years as discrete points if few, or continuous if many
    # This can be tricky; for now, let Plotly decide, or use tickmode='linear' if years are dense.
    # If years are sparse, px.line should handle it well.

    return fig
