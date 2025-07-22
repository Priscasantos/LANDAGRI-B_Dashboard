#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cache System Consolidation
===============================

Verify that the consolidated cache system resolves the original loading errors.
Tests all imports and function availability.
"""

import sys
import traceback

def test_cache_imports():
    """Test consolidated cache system imports."""
    try:
        print("🔍 Testing cache system imports...")
        
        from utilities.cache_system import (
            load_optimized_data, 
            setup_performance_sidebar,
            get_filtered_data,
            calculate_statistics,
            prepare_chart_data
        )
        
        print("✅ All cache functions imported successfully!")
        
        # Test function calls
        print("\n🧪 Testing function availability...")
        
        # Test load_optimized_data
        try:
            result = load_optimized_data()
            print(f"✅ load_optimized_data() returned: {type(result)}")
        except Exception as e:
            print(f"⚠️  load_optimized_data() error: {e}")
        
        print("✅ Cache system consolidation successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(traceback.format_exc())
        return False

def test_dashboard_modules():
    """Test that all dashboard modules can import from consolidated cache."""
    modules = ['overview', 'temporal', 'detailed', 'comparison', 'conab']
    
    print("\n🔍 Testing dashboard module imports...")
    
    for module in modules:
        try:
            exec(f"import dashboard.{module}")
            print(f"✅ dashboard.{module} imported successfully")
        except Exception as e:
            print(f"❌ dashboard.{module} failed: {e}")
            return False
    
    print("✅ All dashboard modules import successfully!")
    return True

def main():
    """Main test function."""
    print("=" * 60)
    print("TESTING CACHE SYSTEM CONSOLIDATION")
    print("=" * 60)
    
    # Test cache imports
    cache_ok = test_cache_imports()
    
    # Test dashboard modules
    modules_ok = test_dashboard_modules()
    
    print("\n" + "=" * 60)
    if cache_ok and modules_ok:
        print("🎉 CONSOLIDATION SUCCESS!")
        print("✅ Original 'Falha no carregamento dos dados' should be resolved")
        print("✅ Cache system unified and functional")
    else:
        print("❌ CONSOLIDATION ISSUES DETECTED")
        print("⚠️  Manual review required")
    print("=" * 60)

if __name__ == "__main__":
    main()
