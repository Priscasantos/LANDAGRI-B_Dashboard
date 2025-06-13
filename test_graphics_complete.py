#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Graphics Test Script
=============================

Test all graphics functionality with the new fixed generate_graphics module.
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from scripts.data_generation.data_processing import load_data_from_jsonc
from scripts.plotting.generate_graphics import plot_timeline, plot_distribuicao_classes, plot_annual_coverage_multiselect
import plotly.graph_objects as go

def test_all_graphics():
    """Test all graphics functions with the loaded data."""
    print("=" * 60)
    print("TESTING ALL GRAPHICS FUNCTIONS")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading data from JSONC...")
    df, metadata = load_data_from_jsonc()
    
    if df is None or df.empty:
        print("❌ Failed to load data - cannot test graphics")
        return
    
    print(f"✅ Loaded {len(df)} initiatives")
    print(f"✅ Metadata for {len(metadata)} initiatives")
    
    # Check if 'Sigla' column exists
    if 'Sigla' in df.columns:
        print("✅ Sigla column found in DataFrame")
        print(f"   Sample siglas: {df['Sigla'].head(3).tolist()}")
    else:
        print("❌ Sigla column not found in DataFrame")
        print(f"   Available columns: {df.columns.tolist()}")
    
    print("\n2. Testing Timeline Graphics...")
    try:
        timeline_fig = plot_timeline(metadata, df)
        if timeline_fig and timeline_fig.data:
            print(f"✅ Timeline plot created with {len(timeline_fig.data)} traces")
        else:
            print("❌ Timeline plot returned empty figure")
    except Exception as e:
        print(f"❌ Timeline plot failed: {e}")
    
    print("\n3. Testing Class Distribution Graphics...")
    try:
        class_dist_fig = plot_distribuicao_classes(df)
        if class_dist_fig and class_dist_fig.data:
            print(f"✅ Class distribution plot created with {len(class_dist_fig.data)} traces")
        else:
            print("❌ Class distribution plot returned empty figure")
    except Exception as e:
        print(f"❌ Class distribution plot failed: {e}")
    
    print("\n4. Testing Annual Coverage Graphics...")
    try:
        # Get some initiatives for testing
        sample_initiatives = df['Nome'].head(3).tolist()
        coverage_fig = plot_annual_coverage_multiselect(
            filtered_df=df,
            metadata=metadata,
            selected_initiatives=sample_initiatives
        )
        if coverage_fig and coverage_fig.data:
            print(f"✅ Annual coverage plot created with {len(coverage_fig.data)} traces")
        else:
            print("❌ Annual coverage plot returned empty figure")
    except Exception as e:
        print(f"❌ Annual coverage plot failed: {e}")
    
    print("\n5. Data Summary:")
    print(f"   Total initiatives: {len(df)}")
    print(f"   Initiatives with temporal data: {len([k for k, v in metadata.items() if 'anos_disponiveis' in v])}")
    print(f"   Initiatives with class data: {len(df[df['Classes'].notna()])}")
    
    # Show sample of what data looks like
    print("\n6. Sample Data Structure:")
    if not df.empty:
        sample_row = df.iloc[0]
        print(f"   Sample initiative: {sample_row.get('Nome', 'N/A')}")
        print(f"   Sample sigla: {sample_row.get('Sigla', 'N/A')}")
        print(f"   Sample classes: {sample_row.get('Classes', 'N/A')}")
        
        # Check metadata for first initiative
        first_name = sample_row['Nome']
        if first_name in metadata:
            meta = metadata[first_name]
            print(f"   Sample temporal data: {meta.get('anos_disponiveis', 'N/A')[:5]}...")
    
    print("\n" + "=" * 60)
    print("GRAPHICS TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_all_graphics()
