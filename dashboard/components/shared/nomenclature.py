"""
Global nomenclature configuration for LULC dashboard.
Provides standardized, user-friendly labels for metrics and columns.
"""

# Global dictionary for friendly column names (English)
COLUMN_LABELS = {
    # Basic info
    "Name": "Initiative Name",
    "Acronym": "Acronym",
    "Display_Name": "Display Name",
    "Type": "Type",
    "Methodology": "Methodology",
    
    # Performance metrics (more specific)
    "Accuracy (%)": "Accuracy (%)",
    "Accuracy": "Overall Accuracy",
    "Accuracy_max_val": "Accuracy Max Value", 
    "Accuracy_min_val": "Accuracy Min Value",
    "Overall_Accuracy": "Overall Accuracy (%)",
    "Producer_Accuracy": "Producer Accuracy (%)",
    "User_Accuracy": "User Accuracy (%)",
    "Kappa": "Kappa Coefficient",
    "F1_Score": "F1 Score",
    
    # Spatial metrics (more specific to avoid duplicates)
    "Resolution": "Spatial Resolution (m)",
    "Resolution_m": "Resolution (meters)",
    "Spatial_Resolution": "Resolution (spatial)",
    "Pixel_Size": "Pixel Size (m)",
    "Resolution_max_val": "Resolution Max Value",
    "Resolution_min_val": "Resolution Min Value",
    
    # Agricultural classes (specific mappings)
    "Agricultural_Classes": "Agricultural Classes",
    "Agri_Classes": "Agri Classes", 
    "Class_Count": "Number of Classes",
    "Total_Classes": "Total Classes",
    "Classes": "Classes",
    "Num_Agri_Classes": "Num Agri Classes",
    "Crop_Classes": "Crop Classes",
    "Class_Legend": "Class Legend",
    "Agricultural_Class_Legend": "Agricultural Class Legend",
    
    # Temporal coverage (specific mappings)
    "Start_Year": "Start Year",
    "End_Year": "End Year",
    "First_Year": "First Year",
    "Last_Year": "Last Year",
    "Years_Count": "Years of Coverage",
    "Coverage_Years": "Coverage Years",
    "Temporal_Coverage": "Temporal Coverage (%)",
    "Temporal_Coverage_Start": "Temporal Coverage Start",
    "Temporal_Coverage_End": "Temporal Coverage End", 
    "Coverage_Percentage": "Coverage Percentage (%)",
    "Available_Years_Str": "Available Years Str",
    "Available_Years_List": "Available Years List",
    "Available_Years": "Available Years",
    
    # Geographic coverage
    "Geographic_Coverage": "Geographic Coverage",
    "Area_Coverage": "Area Coverage (km²)",
    "Country": "Country",
    "Region": "Region",
    "Continent": "Continent",
    
    # Data characteristics (specific mappings)
    "Data_Source": "Data Source",
    "Source": "Source",
    "Sensor": "Sensor",
    "Primary_Sensor": "Primary Sensor",
    "Platform": "Platform",
    "Processing_Level": "Processing Level",
    "Data_Format": "Data Format",
    "Provider": "Provider",
    "Coverage": "Coverage",
    "Sensors_Referenced": "Sensors Referenced",
    "Reference_System": "Reference System",
    
    # Validation metrics
    "Validation_Method": "Validation Method",
    "Sample_Size": "Sample Size",
    "Reference_Data": "Reference Data",
    "Cross_Validation": "Cross Validation",
    
    # Technical details
    "Algorithm": "Algorithm",
    "Classification_Method": "Classification Method",
    "Machine_Learning": "Machine Learning",
    "Deep_Learning": "Deep Learning",
    "Random_Forest": "Random Forest",
    "SVM": "Support Vector Machine",
    "CNN": "Convolutional Neural Network",
    
    # Output characteristics (specific mappings)
    "Output_Format": "Output Format",
    "Output_Resolution": "Output Resolution",
    "Update_Frequency": "Update Frequency",
    "Temporal_Frequency": "Temporal Frequency",
    "Access_Type": "Access Type",
    "Capability": "Capability",
    
    # Quality metrics
    "Quality_Score": "Quality Score",
    "Completeness": "Completeness (%)",
    "Consistency": "Consistency (%)",
    "Timeliness": "Timeliness (%)",
    
    # Usage metrics
    "Downloads": "Downloads",
    "Citations": "Citations",
    "Usage_Count": "Usage Count",
    "Popularity": "Popularity Score"
}

# Reverse mapping for internal use
INTERNAL_NAMES = {v: k for k, v in COLUMN_LABELS.items()}

# Methodology categories (English)
METHODOLOGY_CATEGORIES = {
    "machine_learning": "Machine Learning",
    "deep_learning": "Deep Learning", 
    "random_forest": "Random Forest",
    "svm": "Support Vector Machine",
    "cnn": "Convolutional Neural Network",
    "lstm": "Long Short-Term Memory",
    "decision_tree": "Decision Tree",
    "ensemble": "Ensemble Methods",
    "pixel_based": "Pixel-based Classification",
    "object_based": "Object-based Classification",
    "hybrid": "Hybrid Approach",
    "supervised": "Supervised Learning",
    "unsupervised": "Unsupervised Learning",
    "semi_supervised": "Semi-supervised Learning",
    "time_series": "Time Series Analysis",
    "spectral_analysis": "Spectral Analysis",
    "texture_analysis": "Texture Analysis",
    "change_detection": "Change Detection",
    "multitemporal": "Multitemporal Analysis"
}

# Performance level categories
PERFORMANCE_LEVELS = {
    "excellent": {"min": 90, "label": "Excellent", "color": "#10b981"},
    "good": {"min": 80, "label": "Good", "color": "#f59e0b"},
    "average": {"min": 70, "label": "Average", "color": "#ef4444"},
    "below_average": {"min": 0, "label": "Below Average", "color": "#dc2626"}
}

# Resolution categories
RESOLUTION_CATEGORIES = {
    "very_high": {"max": 1, "label": "Very High (<1m)", "color": "#10b981"},
    "high": {"max": 10, "label": "High (1-10m)", "color": "#3b82f6"},
    "medium": {"max": 100, "label": "Medium (10-100m)", "color": "#f59e0b"},
    "low": {"max": 1000, "label": "Low (100-1000m)", "color": "#ef4444"},
    "very_low": {"max": float('inf'), "label": "Very Low (>1000m)", "color": "#dc2626"}
}

# Chart color palette (consistent across all charts)
CHART_COLORS = [
    "#3b82f6",  # Blue
    "#10b981",  # Green
    "#f59e0b",  # Orange
    "#ef4444",  # Red
    "#8b5cf6",  # Purple
    "#06b6d4",  # Cyan
    "#84cc16",  # Lime
    "#f97316",  # Orange-red
    "#ec4899",  # Pink
    "#6366f1",  # Indigo
]

def get_friendly_name(column_name: str) -> str:
    """
    Get user-friendly name for a column.
    
    Args:
        column_name: Internal column name
        
    Returns:
        User-friendly display name
    """
    return COLUMN_LABELS.get(column_name, column_name.replace("_", " ").title())

def get_internal_name(friendly_name: str) -> str:
    """
    Get internal name from friendly name.
    
    Args:
        friendly_name: User-friendly display name
        
    Returns:
        Internal column name
    """
    return INTERNAL_NAMES.get(friendly_name, friendly_name.lower().replace(" ", "_"))

def categorize_performance(value: float) -> dict:
    """
    Categorize performance value.
    
    Args:
        value: Performance value (0-100)
        
    Returns:
        Dictionary with category info
    """
    for category, info in PERFORMANCE_LEVELS.items():
        if value >= info["min"]:
            return {
                "category": category,
                "label": info["label"],
                "color": info["color"]
            }
    return PERFORMANCE_LEVELS["below_average"]

def categorize_resolution(value: float) -> dict:
    """
    Categorize spatial resolution value.
    
    Args:
        value: Resolution value in meters
        
    Returns:
        Dictionary with category info
    """
    for category, info in RESOLUTION_CATEGORIES.items():
        if value <= info["max"]:
            return {
                "category": category,
                "label": info["label"],
                "color": info["color"]
            }
    return RESOLUTION_CATEGORIES["very_low"]

def get_methodology_label(methodology: str) -> str:
    """
    Get friendly label for methodology.
    
    Args:
        methodology: Internal methodology name
        
    Returns:
        User-friendly methodology label
    """
    methodology_lower = methodology.lower().replace(" ", "_")
    return METHODOLOGY_CATEGORIES.get(methodology_lower, methodology.replace("_", " ").title())

def get_chart_color(index: int) -> str:
    """
    Get chart color by index (cycles through available colors).
    
    Args:
        index: Color index
        
    Returns:
        Hex color code
    """
    return CHART_COLORS[index % len(CHART_COLORS)]

def clean_column_names(df, use_friendly_names: bool = True):
    """
    Clean and standardize DataFrame column names, avoiding duplicates.
    
    Args:
        df: Input DataFrame
        use_friendly_names: Whether to use friendly names or keep internal names clean
        
    Returns:
        DataFrame with cleaned column names (no duplicates)
    """
    df_clean = df.copy()
    
    if use_friendly_names:
        # Apply friendly names with duplicate handling
        new_columns = {}
        used_names = set()
        
        for col in df.columns:
            friendly_name = get_friendly_name(col)
            
            # Handle duplicates by adding suffix
            if friendly_name in used_names:
                counter = 2
                original_name = friendly_name
                while friendly_name in used_names:
                    friendly_name = f"{original_name} ({counter})"
                    counter += 1
            
            new_columns[col] = friendly_name
            used_names.add(friendly_name)
            
        df_clean = df_clean.rename(columns=new_columns)
    else:
        # Clean internal names (remove special characters, standardize)
        new_columns = {}
        used_names = set()
        
        for col in df.columns:
            clean_col = col.strip().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct")
            
            # Handle duplicates
            if clean_col in used_names:
                counter = 2
                original_name = clean_col
                while clean_col in used_names:
                    clean_col = f"{original_name}_{counter}"
                    counter += 1
            
            new_columns[col] = clean_col
            used_names.add(clean_col)
            
        df_clean = df_clean.rename(columns=new_columns)
    
    return df_clean
