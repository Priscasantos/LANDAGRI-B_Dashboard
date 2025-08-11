#!/usr/bin/env python3
"""
Test script for verifying spatial coverage and crop diversity charts
"""

import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

try:
    from dashboard.components.agricultural_analysis.charts.availability.spatial_coverage import plot_conab_spatial_coverage
    from dashboard.components.agricultural_analysis.charts.availability.crop_diversity import plot_conab_crop_diversity
    
    print("✅ Successfully imported chart functions")
    
    # Test with crop calendar format (simulated data)
    test_data = {
        'crop_calendar': {
            'Soja': [
                {
                    'region': 'São Paulo',
                    'state': 'SP',
                    'calendar': {
                        'January': 'P',
                        'February': 'H',
                        'March': '',
                        'April': '',
                        'May': '',
                        'June': '',
                        'July': '',
                        'August': '',
                        'September': 'P',
                        'October': 'P',
                        'November': '',
                        'December': ''
                    }
                },
                {
                    'region': 'Mato Grosso',
                    'state': 'MT',
                    'calendar': {
                        'January': 'H',
                        'February': 'H',
                        'March': '',
                        'April': '',
                        'May': '',
                        'June': '',
                        'July': '',
                        'August': '',
                        'September': 'P',
                        'October': 'P',
                        'November': 'P',
                        'December': ''
                    }
                }
            ],
            'Milho': [
                {
                    'region': 'São Paulo',
                    'state': 'SP',
                    'calendar': {
                        'January': '',
                        'February': '',
                        'March': 'P',
                        'April': 'P',
                        'May': '',
                        'June': '',
                        'July': 'H',
                        'August': 'H',
                        'September': '',
                        'October': '',
                        'November': '',
                        'December': ''
                    }
                },
                {
                    'region': 'Rio Grande do Sul',
                    'state': 'RS',
                    'calendar': {
                        'January': '',
                        'February': '',
                        'March': '',
                        'April': 'P',
                        'May': 'P',
                        'June': '',
                        'July': '',
                        'August': 'H',
                        'September': 'H',
                        'October': '',
                        'November': '',
                        'December': ''
                    }
                }
            ]
        }
    }
    
    print("📊 Testing spatial coverage chart...")
    spatial_fig = plot_conab_spatial_coverage(test_data)
    if spatial_fig and hasattr(spatial_fig, 'data') and len(spatial_fig.data) > 0:
        print("✅ Spatial coverage chart created successfully")
        print(f"   Chart has {len(spatial_fig.data)} traces")
    else:
        print("❌ Spatial coverage chart failed to create data")
    
    print("🌱 Testing crop diversity chart...")
    diversity_fig = plot_conab_crop_diversity(test_data)
    if diversity_fig and hasattr(diversity_fig, 'data') and len(diversity_fig.data) > 0:
        print("✅ Crop diversity chart created successfully")
        print(f"   Chart has {len(diversity_fig.data)} traces")
    else:
        print("❌ Crop diversity chart failed to create data")
    
    # Test with CONAB initiative format
    print("\n🔄 Testing with CONAB initiative format...")
    conab_data = {
        "CONAB Crop Monitoring Initiative": {
            "detailed_crop_coverage": {
                "Soja": {
                    "regions": ["São Paulo", "Mato Grosso"],
                    "first_crop_years": {
                        "São Paulo": ["2020-2023"],
                        "Mato Grosso": ["2018-2023"]
                    },
                    "second_crop_years": {
                        "São Paulo": ["2021-2023"]
                    }
                },
                "Milho": {
                    "regions": ["São Paulo", "Rio Grande do Sul"],
                    "first_crop_years": {
                        "São Paulo": ["2019-2023"],
                        "Rio Grande do Sul": ["2020-2023"]
                    },
                    "second_crop_years": {}
                }
            }
        }
    }
    
    spatial_fig_conab = plot_conab_spatial_coverage(conab_data)
    if spatial_fig_conab and hasattr(spatial_fig_conab, 'data') and len(spatial_fig_conab.data) > 0:
        print("✅ CONAB spatial coverage chart created successfully")
    else:
        print("❌ CONAB spatial coverage chart failed")
        
    diversity_fig_conab = plot_conab_crop_diversity(conab_data)
    if diversity_fig_conab and hasattr(diversity_fig_conab, 'data') and len(diversity_fig_conab.data) > 0:
        print("✅ CONAB crop diversity chart created successfully")
    else:
        print("❌ CONAB crop diversity chart failed")
    
    print("\n🎉 All tests completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
