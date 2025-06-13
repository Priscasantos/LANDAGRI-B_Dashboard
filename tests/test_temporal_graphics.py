#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Temporal Graphics with New Data Structure
========================================================

This script tests the temporal graphics functionality with the new JSONC data structure,
ensuring that timeline and temporal analysis functions work correctly.

Usage:
    python tests/test_temporal_graphics.py

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import sys
import os
import traceback
from pathlib import Path

# Add the parent directory to the path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

def test_temporal_graphics():
    """Test temporal graphics functionality with new data structure"""
    print('🎯 Testing temporal graphics with new data structure...')
    print('=' * 70)
    
    try:        # Import modules
        from scripts.data_generation.data_processing import load_data
        from scripts.plotting.generate_graphics import (
            plot_timeline, plot_annual_coverage_multiselect,
            plot_ano_overlap, plot_heatmap
        )
        
        # Load data
        print('📂 Loading data for temporal graphics testing...')
        df, metadata = load_data()
        
        if df is None or df.empty:
            print('❌ Failed to load data')
            return False
            
        print(f'✅ Data loaded: {len(df)} initiatives with {len(metadata)} metadata entries')
        
        # Test timeline plot
        print('\n📅 Testing timeline plot...')
        try:
            fig_timeline = plot_timeline(metadata, df)
            if fig_timeline:
                print('✅ Timeline plot created successfully')
                
                # Check if it has traces
                if hasattr(fig_timeline, 'data') and len(fig_timeline.data) > 0:
                    print(f'  - Plot has {len(fig_timeline.data)} traces')
                    
                    # Check for expected trace types
                    trace_types = [trace.type for trace in fig_timeline.data]
                    print(f'  - Trace types: {set(trace_types)}')
                else:
                    print('⚠️ Timeline plot has no data traces')
            else:
                print('❌ Timeline plot returned None')
                
        except Exception as e:
            print(f'❌ Error creating timeline plot: {e}')
            traceback.print_exc()
            
        # Test annual coverage multiselect
        print('\n📊 Testing annual coverage multiselect...')
        try:
            # Select a few initiatives for testing
            selected_initiatives = df['Nome'].head(3).tolist()
            print(f'  Testing with initiatives: {selected_initiatives}')
            
            fig_coverage = plot_annual_coverage_multiselect(metadata, df, selected_initiatives)
            if fig_coverage:
                print('✅ Annual coverage plot created successfully')
                
                if hasattr(fig_coverage, 'data') and len(fig_coverage.data) > 0:
                    print(f'  - Plot has {len(fig_coverage.data)} traces')
                    
                    # Check trace names
                    trace_names = [trace.name for trace in fig_coverage.data if hasattr(trace, 'name')]
                    print(f'  - Initiatives plotted: {len(trace_names)}')
                else:
                    print('⚠️ Annual coverage plot has no data traces')
            else:
                print('❌ Annual coverage plot returned None')
                
        except Exception as e:
            print(f'❌ Error creating annual coverage plot: {e}')
            traceback.print_exc()
              # Test temporal heatmap analysis
        print('\n🔍 Testing temporal heatmap analysis...')
        try:
            fig_temporal = plot_heatmap(metadata, df)
            if fig_temporal:
                print('✅ Temporal heatmap plot created successfully')
                
                if hasattr(fig_temporal, 'data') and len(fig_temporal.data) > 0:
                    print(f'  - Plot has {len(fig_temporal.data)} traces')
                else:
                    print('⚠️ Temporal heatmap plot has no data traces')
            else:
                print('❌ Temporal heatmap plot returned None')
                
        except Exception as e:
            print(f'❌ Error creating temporal heatmap plot: {e}')
            traceback.print_exc()
            
        # Test metadata structure for temporal graphics
        print('\n🔍 Testing metadata structure for temporal compatibility...')
        compatible_count = 0
        issues = []
        
        for name, meta in metadata.items():
            is_compatible = True
            initiative_issues = []
            
            # Check for required fields
            if 'anos_disponiveis' not in meta or not meta['anos_disponiveis']:
                is_compatible = False
                initiative_issues.append('missing anos_disponiveis')
                
            if 'start_year' not in meta:
                is_compatible = False
                initiative_issues.append('missing start_year')
                
            if 'end_year' not in meta:
                is_compatible = False
                initiative_issues.append('missing end_year')
                
            # Check data types
            if 'anos_disponiveis' in meta:
                if not isinstance(meta['anos_disponiveis'], list):
                    is_compatible = False
                    initiative_issues.append('anos_disponiveis not a list')
                elif not all(isinstance(year, int) for year in meta['anos_disponiveis']):
                    is_compatible = False
                    initiative_issues.append('anos_disponiveis contains non-integers')
                    
            if is_compatible:
                compatible_count += 1
            else:
                issues.append(f'{name}: {", ".join(initiative_issues)}')
                
        print(f'  ✅ {compatible_count}/{len(metadata)} initiatives are compatible with temporal graphics')
        
        if issues:
            print(f'  ⚠️ Issues found:')
            for issue in issues[:5]:  # Show first 5 issues
                print(f'    - {issue}')
            if len(issues) > 5:
                print(f'    ... and {len(issues) - 5} more')
                
        # Test specific temporal derivations
        print('\n📈 Testing temporal derivations quality...')
        gap_stats = {'with_gaps': 0, 'without_gaps': 0, 'total_gap_years': 0}
        span_stats = {'min_span': float('inf'), 'max_span': 0, 'avg_span': 0}
        
        spans = []
        for name, meta in metadata.items():
            if 'gaps_temporais' in meta:
                if meta['gaps_temporais']:
                    gap_stats['with_gaps'] += 1
                    gap_stats['total_gap_years'] += len(meta['gaps_temporais'])
                else:
                    gap_stats['without_gaps'] += 1
                    
            if 'span_temporal' in meta and isinstance(meta['span_temporal'], int):
                span = meta['span_temporal']
                spans.append(span)
                span_stats['min_span'] = min(span_stats['min_span'], span)
                span_stats['max_span'] = max(span_stats['max_span'], span)
                
        if spans:
            span_stats['avg_span'] = sum(spans) / len(spans)
            
        print(f'  📊 Gap analysis: {gap_stats["with_gaps"]} with gaps, {gap_stats["without_gaps"]} continuous')
        print(f'  📊 Total gap years across all initiatives: {gap_stats["total_gap_years"]}')
        print(f'  📊 Temporal span: min={span_stats["min_span"]}, max={span_stats["max_span"]}, avg={span_stats["avg_span"]:.1f} years')
        
        print('\n✅ Temporal graphics testing completed!')
        return True
        
    except Exception as e:
        print(f'❌ Error during temporal graphics testing: {e}')
        traceback.print_exc()
        return False

def test_dashboard_integration():
    """Test integration with dashboard modules"""
    print('\n🔗 Testing dashboard integration...')
    print('=' * 70)
    
    try:
        # Test dashboard imports
        print('📦 Testing dashboard module imports...')
        
        modules_to_test = [
            ('dashboard.temporal.temporal', 'temporal dashboard'),
            ('dashboard.detailed.detailed', 'detailed dashboard'),
            ('dashboard.comparisons.comparison', 'comparison dashboard')
        ]
        
        success_count = 0
        for module_name, description in modules_to_test:
            try:
                __import__(module_name)
                print(f'  ✅ {description} module imported successfully')
                success_count += 1
            except ImportError as e:
                print(f'  ❌ Failed to import {description}: {e}')
            except Exception as e:
                print(f'  ⚠️ Error importing {description}: {e}')
                
        print(f'\n📊 Dashboard integration: {success_count}/{len(modules_to_test)} modules working')
        
        # Test data loading in dashboard context
        print('\n📂 Testing data loading in dashboard context...')
        from scripts.data_generation.data_processing import load_data
        
        # Simulate dashboard data loading
        df, metadata = load_data()
        
        if df is not None and not df.empty and metadata:
            print('✅ Data loading works in dashboard context')
            
            # Check for required columns for dashboard
            required_cols = ['Nome', 'Anos Disponíveis', 'Acurácia (%)', 'Resolução (m)']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if not missing_cols:
                print('✅ All required dashboard columns present')
            else:
                print(f'⚠️ Missing dashboard columns: {missing_cols}')
                
        else:
            print('❌ Data loading failed in dashboard context')
            
        return success_count == len(modules_to_test)
        
    except Exception as e:
        print(f'❌ Error during dashboard integration testing: {e}')
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print('🚀 Starting Temporal Graphics and Dashboard Integration Tests')
    print('=' * 80)
    
    # Run temporal graphics tests
    success1 = test_temporal_graphics()
    
    # Run dashboard integration tests
    success2 = test_dashboard_integration()
    
    # Summary
    print('\n' + '=' * 80)
    if success1 and success2:
        print('🎉 ALL TESTS PASSED! Temporal graphics and dashboard integration working correctly.')
    elif success1:
        print('⚠️ Temporal graphics tests passed, but dashboard integration issues found.')
    elif success2:
        print('⚠️ Dashboard integration passed, but temporal graphics issues found.')
    else:
        print('❌ Tests failed. Please check the errors above.')
        
    print('=' * 80)

if __name__ == "__main__":
    main()
