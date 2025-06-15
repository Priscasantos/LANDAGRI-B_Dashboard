#!/usr/bin/env python3
"""
Main modernized script for complete LULC initiatives analysis.

This script executes all analysis modules in the correct order:
1. Data Preview
2. Main Analysis with Comparative Charts
3. Temporal Charts
4. Detailed Charts

Output Structure:
- graphics/comparisons/  - PNGs of comparative charts between initiatives
- graphics/temporal/     - PNGs of temporal analyses of initiatives
- graphics/detailed/     - PNGs of specific detailed analyses

Interactive Dashboard Structure:
- dashboard/comparisons/ - Streamlit modules for comparative analyses
- dashboard/temporal/    - Streamlit modules for temporal analyses
- dashboard/detailed/    - Streamlit modules for detailed analyses

Based on the standard structure of dashboard-agricultura
Author: LULC Analysis System
Date: 2025
"""

import sys
from pathlib import Path
import pandas as pd # Added import for pd.Series

# Global cache for data loading optimization
_DATA_CACHE = {}

def get_cached_data():
    """Get cached data or load it if not cached"""
    if 'data' not in _DATA_CACHE:
        from scripts.data_generation.data_wrapper import load_data, prepare_plot_data
        df, metadata, _ = load_data()
        df_prepared_dict = prepare_plot_data(df)
        df_for_plots = df_prepared_dict.get('data', pd.DataFrame())
        _DATA_CACHE['data'] = {
            'df': df,
            'metadata': metadata,
            'df_for_plots': df_for_plots
        }
        print(f"📊 Data loaded and cached: {len(df_for_plots)} initiatives")
    return _DATA_CACHE['data']

# Add the scripts directory to the path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.append(str(scripts_dir))

def run_analysis_step(module_name, description):
    """Executes an analysis step and handles errors"""
    print(f"\n{'='*60}")
    print(f"🔄 EXECUTING: {description}")
    print(f"{'='*60}")
    
    try:
        if module_name == "preview_dados":
            from scripts.data_generation.data_wrapper import load_data  # Use correct import
            # Preview of loaded data
            print("📊 Loading LULC initiatives data...")
            df, metadata, _ = load_data()  # Fixed tuple unpacking
            print(f"✅ Data loaded: {len(df)} initiatives")
            print(f"📋 Available columns: {list(df.columns)}")
            if 'Type' in df.columns:
                print(f"🏷️ Initiative types: {df['Type'].unique().tolist()}")            
            elif 'Tipo' in df.columns: # Fallback for Portuguese column name
                print(f"🏷️ Initiative types: {df['Tipo'].unique().tolist()}")
                
        elif module_name == "analise_comparativa":
            # Use cached data for better performance
            cached_data = get_cached_data()
            df_for_plots = cached_data['df_for_plots']
            metadata = cached_data['metadata']
            
            # Import direct from modular chart files for better performance
            from scripts.plotting.charts.distribution_charts import (
                plot_resolution_accuracy,
                plot_classes_por_iniciativa,
                plot_distribuicao_classes,
                plot_distribuicao_metodologias
            )
            from scripts.plotting.charts.temporal_charts import plot_timeline
            
            plot_resolution_accuracy(df_for_plots)
            plot_timeline(metadata, df_for_plots) 
            plot_classes_por_iniciativa(df_for_plots)
            plot_distribuicao_classes(df_for_plots)
            plot_distribuicao_metodologias(df_for_plots['Methodology'].value_counts() if 'Methodology' in df_for_plots and not df_for_plots.empty else pd.Series())
            
        elif module_name == "analise_temporal":
            from dashboard.temporal import prepare_temporal_data 
            from scripts.plotting.charts.temporal_charts_offline import (
                create_gaps_chart_non_streamlit,
                create_evolution_charts_non_streamlit
            )
            # create_timeline_chart_non_streamlit is available but called in comparative analysis
            from scripts.utilities.chart_saver import save_chart_robust 
            from pathlib import Path

            cached_data = get_cached_data()
            df = cached_data['df'] 
            metadata = cached_data['metadata']
            
            output_dir = Path("graphics/temporal")
            output_dir.mkdir(parents=True, exist_ok=True)

            print("Preparing temporal data for offline charts...")
            temporal_data_script = prepare_temporal_data(metadata, df_original=df) 

            if temporal_data_script.empty:
                print("No temporal data available to generate charts.")
                return False # Indicate failure or skip

            print("Generating offline temporal charts...")
            
            # Gaps Chart
            fig_gaps_ns = create_gaps_chart_non_streamlit(temporal_data_script)
            if fig_gaps_ns:
                gaps_df_for_height = temporal_data_script[temporal_data_script['Anos_Faltando'] > 0]
                height_gaps = max(400, len(gaps_df_for_height) * 25) if not gaps_df_for_height.empty else 400
                save_chart_robust(fig_gaps_ns, output_dir, "temporal_gaps_offline", width=1000, height=height_gaps)
                print("Temporal Gaps chart (offline) saved.")

            # Evolution Charts
            fig_evolution_ns, fig_heatmap_evo_ns = create_evolution_charts_non_streamlit(temporal_data_script)
            if fig_evolution_ns: 
                save_chart_robust(fig_evolution_ns, output_dir, "availability_evolution_offline")
                print("Availability Evolution line chart (offline) saved.")
            if fig_heatmap_evo_ns:
                height_heatmap = max(400, len(temporal_data_script['Tipo'].unique()) * 50) if 'Tipo' in temporal_data_script and temporal_data_script['Tipo'].nunique() > 0 else 400
                save_chart_robust(fig_heatmap_evo_ns, output_dir, "heatmap_type_year_evolution_offline", height=height_heatmap)
                print("Evolution Heatmap (offline) saved.")
            
            # The old call to run_non_streamlit from temporal.py is fully replaced
            # success = run_non_streamlit(metadata, df, "graphics/temporal") 
            # if not success:
            #     print("❌ Failed to generate temporal analyses.") # Translated
            #     return False   
            return True 
                     
        elif module_name == "analise_detalhada":
            from dashboard.detailed.detailed import run_non_streamlit as detailed_run_non_streamlit
            # No need to load data again if using cached data, but detailed_run_non_streamlit might expect its own loading.
            # For consistency, let's ensure it uses cached data or document why it reloads.
            # Assuming detailed_run_non_streamlit is adapted or can take df, metadata:
            cached_data = get_cached_data()
            df_for_plots = cached_data['df_for_plots'] # Or 'df' depending on what detailed_run_non_streamlit expects
            metadata = cached_data['metadata']
            
            success = detailed_run_non_streamlit(df_for_plots, metadata, "graphics/detailed")
            if not success:
                print("❌ Failed to generate detailed analyses.") # Translated
                return False
        
        print(f"✅ {description} - COMPLETED SUCCESSFULLY!") # Translated
        return True
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}") # Translated
        print("💡 Make sure all dependencies are installed:") # Translated
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ ERROR DURING EXECUTION: {e}") # Translated
        print(f"💡 Check the module: {module_name}") # Translated
        return False

def check_dependencies():
    """Checks if necessary dependencies are installed"""
    required_packages = ["pandas", "matplotlib", "numpy", "plotly", "seaborn", "streamlit"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ MISSING DEPENDENCIES:") # Translated
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 First run: pip install -r requirements.txt") # Translated
        return False
    
    print("✅ All dependencies are installed!") # Translated
    return True

def create_output_directories():
    """Creates output directories for PNGs if they don't exist"""
    base_path = Path("graphics")
    dirs_to_create = [
        base_path / "comparisons",
        base_path / "temporal",
        base_path / "detailed"
    ]
    
    print("📂 Creating output directories...") # Translated
    for dir_path in dirs_to_create:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   Directory created/exists: {dir_path}") # Translated
        except Exception as e:
            print(f"   ❌ Error creating directory {dir_path}: {e}") # Translated
            # Optionally, decide if this is a critical error
    print("✅ Output directories checked/created.") # Translated

def main():
    """Main function to run the complete analysis"""
    print("🚀 STARTING LULC INITIATIVE ANALYSIS 🚀") # Translated
    
    if not check_dependencies():
        print("🔴 Analysis halted due to missing dependencies.") # Translated
        return

    create_output_directories()

    # Analysis Steps (translated descriptions)
    analysis_pipeline = [
        ("preview_dados", "Data Preview"),
        ("analise_comparativa", "Comparative Analysis"),
        ("analise_temporal", "Temporal Analysis (Offline Charts)"),
        ("analise_detalhada", "Detailed Analysis (Offline Charts)")
    ]
    
    all_successful = True
    for module, description in analysis_pipeline:
        if not run_analysis_step(module, description):
            all_successful = False
            print(f"⚠️ Step '{description}' failed or was skipped.") # Translated
            # Decide if to continue or break on failure
            # break 
    
    if all_successful:
        print("\n🎉🎉 ALL ANALYSES COMPLETED SUCCESSFULLY! 🎉🎉") # Translated
    else:
        print("\n💔 SOME ANALYSES FAILED OR WERE SKIPPED. Please check the logs. 💔") # Translated

if __name__ == "__main__":
    main()
