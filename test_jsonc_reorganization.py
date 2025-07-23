#!/usr/bin/env python3
"""
Test script to validate JSONC file paths after reorganization.

This script verifies that all JSONC files are correctly accessible
in their new location under data/json/ and that the applications
can load them successfully.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

try:
    from scripts.data_generation.lulc_data_engine import UnifiedDataProcessor
    from scripts.utilities.data_optimizer import load_and_optimize_initiatives
    from scripts.utilities.json_interpreter import (
        interpret_combined_conab_metadata,
        interpret_initiatives_metadata,
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_jsonc_file_access():
    """Test if all JSONC files are accessible in their new location."""
    print("🧪 Testing JSONC file accessibility...")

    jsonc_files = [
        "data/json/initiatives_metadata.jsonc",
        "data/json/sensors_metadata.jsonc",
        "data/json/conab_detailed_initiative.jsonc",
        "data/json/conab_crop_calendar.jsonc",
    ]

    all_files_exist = True
    for file_path in jsonc_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_files_exist = False

    return all_files_exist


def test_json_interpreter():
    """Test the JSON interpreter with new paths."""
    print("\n🧪 Testing JSON interpreter functionality...")

    try:
        # Test initiatives metadata loading
        df = interpret_initiatives_metadata()
        print(f"✅ Loaded initiatives metadata: {len(df)} records")

        # Test combined metadata loading
        combined_df = interpret_combined_conab_metadata()
        print(f"✅ Loaded combined metadata: {len(combined_df)} records")

        return True
    except Exception as e:
        print(f"❌ JSON interpreter test failed: {e}")
        return False


def test_unified_processor():
    """Test the UnifiedDataProcessor with new paths."""
    print("\n🧪 Testing UnifiedDataProcessor...")

    try:
        processor = UnifiedDataProcessor()
        df, metadata = processor.load_data_from_jsonc()
        print(f"✅ UnifiedDataProcessor loaded: {len(df)} records")
        return True
    except Exception as e:
        print(f"❌ UnifiedDataProcessor test failed: {e}")
        return False


def test_data_optimizer():
    """Test the data optimizer with new paths."""
    print("\n🧪 Testing data optimizer...")

    try:
        initiatives_file = PROJECT_ROOT / "data/json/initiatives_metadata.jsonc"
        if initiatives_file.exists():
            df, optimized_data = load_and_optimize_initiatives(str(initiatives_file))
            print(
                f"✅ Data optimizer loaded: {len(df)} records with {len(optimized_data)} optimizations"
            )
            return True
        else:
            print("❌ Data optimizer test failed: initiatives file not found")
            return False
    except Exception as e:
        print(f"❌ Data optimizer test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🚀 Starting JSONC reorganization validation tests")
    print("=" * 60)

    tests = [
        ("File Accessibility", test_jsonc_file_access),
        ("JSON Interpreter", test_json_interpreter),
        ("Unified Processor", test_unified_processor),
        ("Data Optimizer", test_data_optimizer),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        success = test_func()
        results.append((test_name, success))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if not success:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! JSONC reorganization successful!")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
