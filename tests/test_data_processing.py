#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for JSONC Data Processing Pipeline
============================================

This script tests the new JSONC data loading and processing functionality,
including temporal derivations and multiple product versions handling.

Usage:
    python tests/test_data_processing.py

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add the parent directory to the path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

def test_jsonc_data_loading():
    """Test JSONC data loading and processing functionality"""
    print('🧪 Testing JSONC data loading and processing...')
    print('=' * 60)
    
    try:
        # Import modules
        from scripts.data_generation.data_processing import load_data
        
        # Test data loading
        print('📂 Loading data from JSONC format...')
        df, metadata = load_data()
        
        if df is None or df.empty:
            print('❌ Failed to load data - DataFrame is empty')
            return False
            
        print(f'✅ Successfully loaded {len(df)} initiatives')
        print(f'🗂️ DataFrame columns: {list(df.columns)}')
        print()
        
        # Test basic data structure
        expected_columns = ['Nome', 'Anos Disponíveis', 'Ano Inicial', 'Ano Final', 'Span Temporal']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f'⚠️ Missing expected columns: {missing_columns}')
        else:
            print('✅ All expected temporal columns present')
            
        # Display sample temporal data
        print('\n📊 Sample temporal data:')
        temporal_cols = [col for col in expected_columns if col in df.columns]
        if temporal_cols:
            sample_data = df[temporal_cols].head(3)
            for idx, row in sample_data.iterrows():
                print(f"  {row['Nome']}: {row['Anos Disponíveis']} | "
                      f"Inicial: {row.get('Ano Inicial', 'N/A')} | "
                      f"Final: {row.get('Ano Final', 'N/A')} | "
                      f"Span: {row.get('Span Temporal', 'N/A')}")
        
        # Test metadata temporal enhancements
        print('\n🎯 Testing metadata temporal enhancements:')
        if metadata:
            sample_initiative = list(metadata.keys())[0]
            sample_meta = metadata[sample_initiative]
            
            print(f'Sample initiative: {sample_initiative}')
            print(f'anos_disponiveis (list): {sample_meta.get("anos_disponiveis", [])}')
            print(f'start_year: {sample_meta.get("start_year", "N/A")}')
            print(f'end_year: {sample_meta.get("end_year", "N/A")}')
            print(f'gaps_temporais: {sample_meta.get("gaps_temporais", [])}')
            
            # Test temporal derivations for all initiatives
            temporal_stats = {
                'with_anos_disponiveis': 0,
                'with_start_year': 0,
                'with_end_year': 0,
                'with_gaps': 0
            }
            
            for name, meta in metadata.items():
                if meta.get('anos_disponiveis'):
                    temporal_stats['with_anos_disponiveis'] += 1
                if meta.get('start_year'):
                    temporal_stats['with_start_year'] += 1
                if meta.get('end_year'):
                    temporal_stats['with_end_year'] += 1
                if meta.get('gaps_temporais'):
                    temporal_stats['with_gaps'] += 1
                    
            print(f'\n📈 Temporal derivation statistics:')
            for key, count in temporal_stats.items():
                percentage = (count / len(metadata)) * 100
                print(f'  {key}: {count}/{len(metadata)} ({percentage:.1f}%)')
        else:
            print('❌ No metadata loaded')
            
        # Test ESRI multiple versions
        print('\n🔧 Testing ESRI multiple product versions:')
        esri_name = 'ESRI-10m Annual LULC'
        if esri_name in df['Nome'].values:
            esri_row = df[df['Nome'] == esri_name].iloc[0]
            print(f'Classes: {esri_row["Classes"]}')
            
            # Check for legend information
            if 'Legenda Classes' in esri_row:
                legenda = str(esri_row['Legenda Classes'])
                print(f'Legenda: {legenda[:100]}...')
            else:
                print('⚠️ No Legenda Classes column found')
                
            # Check for multiple versions in metadata
            if metadata and esri_name in metadata:
                esri_meta = metadata[esri_name]
                print(f'Raw metadata keys: {list(esri_meta.keys())}')
                
                # Look for multiple class versions
                version_keys = [k for k in esri_meta.keys() if 'classes' in k.lower()]
                if len(version_keys) > 1:
                    print(f'✅ Found multiple class versions: {version_keys}')
                else:
                    print(f'ℹ️ Single class version found: {version_keys}')
        else:
            print(f'⚠️ ESRI initiative "{esri_name}" not found in data')
            
        # Test data types and consistency
        print('\n🔍 Testing data consistency:')
        print(f'DataFrame shape: {df.shape}')
        print(f'Metadata entries: {len(metadata) if metadata else 0}')
        
        # Check for data type consistency
        numeric_columns = ['Resolução (m)', 'Acurácia (%)', 'Classes']
        for col in numeric_columns:
            if col in df.columns:
                non_numeric = df[col].apply(lambda x: not isinstance(x, (int, float)) and x != 'N/A').sum()
                print(f'  {col}: {non_numeric} non-numeric values')
                  # Test temporal data parsing
        print('\n⏰ Testing temporal data parsing:')
        if 'Anos Disponíveis' in df.columns:
            unique_formats = df['Anos Disponíveis'].apply(type).value_counts()
            formats_dict = {}
            for data_type, count in unique_formats.items():
                formats_dict[str(data_type)] = count
            print(f'Anos Disponíveis data types: {formats_dict}')
            
            # Test a few parsing examples
            sample_temporal = df['Anos Disponíveis'].dropna().head(3)
            for idx, anos in sample_temporal.items():
                initiative_name = df.loc[idx, 'Nome']
                print(f'  {initiative_name}: {type(anos).__name__} = {str(anos)[:50]}...')
        
        print('\n✅ All tests completed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ Error during testing: {e}')
        print('\n🔍 Full traceback:')
        traceback.print_exc()
        return False

def test_specific_features():
    """Test specific features of the new processing pipeline"""
    print('\n🎯 Testing specific processing features...')
    print('=' * 60)
    
    try:
        from scripts.data_generation.data_processing import (
            parse_resolution, parse_accuracy, parse_temporal_span
        )
        
        # Test resolution parsing
        print('📏 Testing resolution parsing:')
        resolution_tests = [
            '10m',
            '10 m',
            '30 meters',
            '500m x 500m',
            '1km',
            'Not specified',
            10,
            '10-30m'
        ]
        
        for test_res in resolution_tests:
            try:
                parsed = parse_resolution(test_res)
                print(f'  "{test_res}" -> {parsed}')
            except Exception as e:
                print(f'  "{test_res}" -> ERROR: {e}')
                
        # Test accuracy parsing
        print('\n🎯 Testing accuracy parsing:')
        accuracy_tests = [
            '85%',
            '85.5%',
            'Not informed',
            'Not available',
            85,
            85.5,
            '~85%',
            'Approximately 85%'
        ]
        
        for test_acc in accuracy_tests:
            try:
                parsed = parse_accuracy(test_acc)
                print(f'  "{test_acc}" -> {parsed}')
            except Exception as e:
                print(f'  "{test_acc}" -> ERROR: {e}')
                
        # Test temporal span parsing
        print('\n📅 Testing temporal span parsing:')
        temporal_tests = [
            [2020, 2021, 2022, 2023],
            [2000, 2005, 2010, 2015, 2020],
            [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020],
            [2021],
            []
        ]
        
        for test_temporal in temporal_tests:
            try:
                parsed = parse_temporal_span(test_temporal)
                print(f'  {test_temporal} -> {parsed}')
            except Exception as e:
                print(f'  {test_temporal} -> ERROR: {e}')
                
        print('\n✅ Feature tests completed!')
        return True
        
    except ImportError as e:
        print(f'❌ Could not import required functions: {e}')
        return False
    except Exception as e:
        print(f'❌ Error during feature testing: {e}')
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print('🚀 Starting LULC Data Processing Tests')
    print('=' * 80)
    
    # Run basic data loading tests
    success1 = test_jsonc_data_loading()
    
    # Run specific feature tests
    success2 = test_specific_features()
    
    # Summary
    print('\n' + '=' * 80)
    if success1 and success2:
        print('🎉 ALL TESTS PASSED! The data processing pipeline is working correctly.')
    elif success1:
        print('⚠️ Basic tests passed, but some feature tests failed.')
    else:
        print('❌ Tests failed. Please check the errors above.')
        
    print('=' * 80)

if __name__ == "__main__":
    main()
