#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test for Fixed Graphics Functions
======================================

Test the timeline and class distribution graphics with the new fixes.

Usage:
    python tests/test_fixed_graphics.py

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import sys
import traceback
from pathlib import Path

# Add the parent directory to the path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

def test_fixed_graphics():
    """Test the fixed timeline and class distribution graphics"""
    print('🧪 Testing Fixed Graphics Functions...')
    print('=' * 50)
    
    try:
        # Import modules
        from scripts.data_generation.data_processing import load_data
        from scripts.plotting.generate_graphics import plot_timeline, plot_distribuicao_classes
        from scripts.utilities.acronyms import get_initiative_acronym, INITIATIVE_ACRONYMS
        
        # Test acronym mapping
        print('📋 Testing acronym mapping...')
        print(f'Total mappings: {len(INITIATIVE_ACRONYMS)}')
        
        # Test a few examples
        test_names = [
            "Dynamic World V1",
            "ESRI-10m Annual LULC", 
            "MapBiomas Brasil"
        ]
        
        for name in test_names:
            acronym = get_initiative_acronym(name)
            print(f'  "{name}" -> "{acronym}"')
        
        # Load data
        print('\n📂 Loading data...')
        df, metadata = load_data()
        
        if df is None or df.empty:
            print('❌ Failed to load data')
            return False
            
        print(f'✅ Data loaded: {len(df)} initiatives')
        
        # Test timeline with acronyms
        print('\n📅 Testing timeline plot with acronyms...')
        try:
            fig_timeline = plot_timeline(metadata, df)
            if fig_timeline and hasattr(fig_timeline, 'data'):
                trace_count = len(fig_timeline.data)
                print(f'✅ Timeline plot created with {trace_count} traces')
                
                # Check if layout has proper y-axis labels
                if hasattr(fig_timeline, 'layout') and hasattr(fig_timeline.layout, 'yaxis'):
                    if hasattr(fig_timeline.layout.yaxis, 'ticktext'):
                        labels = fig_timeline.layout.yaxis.ticktext
                        print(f'  Y-axis labels (first 3): {labels[:3] if labels else "None"}')
                        
                        # Check if acronyms are being used
                        if labels and any(len(label) <= 20 for label in labels[:5]):
                            print('  ✅ Using shorter labels (likely acronyms)')
                        else:
                            print('  ⚠️ Still using long labels')
                else:
                    print('  ⚠️ No y-axis configuration found')
            else:
                print('❌ Timeline plot failed or returned empty')
                
        except Exception as e:
            print(f'❌ Error creating timeline: {e}')
            traceback.print_exc()
            
        # Test class distribution
        print('\n📊 Testing class distribution plot...')
        try:
            fig_classes = plot_distribuicao_classes(df)
            if fig_classes and hasattr(fig_classes, 'data'):
                trace_count = len(fig_classes.data)
                print(f'✅ Class distribution plot created with {trace_count} traces')
                  # Check if data exists
                if trace_count > 0 and hasattr(fig_classes.data[0], 'x'):
                    x_data = fig_classes.data[0].x
                    data_points = len(x_data) if x_data is not None else 0
                    print(f'  Data points: {data_points}')
                    
                    if data_points > 0:
                        print('  ✅ Plot has data')
                    else:
                        print('  ⚠️ Plot created but no data points')
                else:
                    print('  ⚠️ No trace data found')
            else:
                print('❌ Class distribution plot failed or returned empty')
                
        except Exception as e:
            print(f'❌ Error creating class distribution: {e}')
            traceback.print_exc()
            
        # Test data availability for graphics
        print('\n🔍 Testing data availability...')
        
        # Check Classes column
        if 'Classes' in df.columns:
            classes_data = df['Classes'].dropna()
            print(f'  Classes column: {len(classes_data)} valid values')
            print(f'  Range: {classes_data.min()} - {classes_data.max()}')
            print(f'  Sample values: {classes_data.head(3).tolist()}')
        else:
            print('  ❌ Classes column not found')
            
        # Check temporal metadata
        temporal_count = 0
        for name, meta in metadata.items():
            if 'anos_disponiveis' in meta and meta['anos_disponiveis']:
                temporal_count += 1
                
        print(f'  Initiatives with temporal data: {temporal_count}/{len(metadata)}')
        
        print('\n✅ Testing completed!')
        return True
        
    except Exception as e:
        print(f'❌ Error during testing: {e}')
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print('🚀 Starting Fixed Graphics Tests')
    print('=' * 60)
    
    success = test_fixed_graphics()
    
    print('\n' + '=' * 60)
    if success:
        print('🎉 Graphics tests completed! Check results above for any issues.')
    else:
        print('❌ Graphics tests failed. Please check the errors above.')
        
    print('=' * 60)

if __name__ == "__main__":
    main()
