"""
JSON Interpreter for LULC Initiatives Metadata
==============================================

This module provides functions to directly read, parse, and transform the
initiatives_metadata.jsonc file into a data structure suitable for dashboard visualizations.
It aims to replace the dependency on pre-processed data files.

Key Features:
- Direct parsing of initiatives_metadata.jsonc.
- Extraction and standardization of key fields like Resolution and Accuracy.
- Generation of display-friendly names.
- Robust handling of various data formats and missing information.
"""
import json
import re
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Union, Optional

# Helper function to load and clean JSONC content
def _load_jsonc_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Loads a JSONC file, stripping comments before parsing."""
    lines: List[str] = [] # Initialize lines
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Remove single-line comments (//...)
        valid_json_lines = [line for line in lines if not line.strip().startswith('//')]
        # Remove multi-line comments (/* ... */) - basic removal
        valid_json_content = ''.join(valid_json_lines)
        # A more robust multi-line comment removal might be needed for complex cases
        # For now, assuming simple comment structures or that they are on their own lines.
        return json.loads(valid_json_content)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSONC from {file_path}: {e}")
        # Attempt to provide more context for the error
        # This is a simplified error reporting for JSONC
        error_line_content = "Unknown line"
        if lines: # Check if lines was populated
            error_line_content = "".join(lines).splitlines()[e.lineno - 1] if hasattr(e, 'lineno') and e.lineno <= len(lines) else "Error line out of bounds or not available"
        print(f"Problematic line (approx.): {error_line_content}")

        # Fallback: try to parse line by line to find the issue (very basic)
        cleaned_lines_for_fallback = []
        if lines: # Check if lines was populated
            for line_num, line_content_iter in enumerate(lines):
                if not line_content_iter.strip().startswith('//'):
                    try:
                        # Try to parse each part that looks like a JSON object/array boundary
                        # This is not a full JSONC parser but a heuristic for simple structures
                        if line_content_iter.strip().endswith(',') or line_content_iter.strip().endswith('{') or line_content_iter.strip().endswith('['):
                            cleaned_lines_for_fallback.append(line_content_iter)
                        elif ':' in line_content_iter: # Likely a key-value pair
                            cleaned_lines_for_fallback.append(line_content_iter)
                    except Exception:
                        print(f"Skipping potentially problematic line {line_num+1}: {line_content_iter.strip()}")
        try:
            return json.loads("".join(cleaned_lines_for_fallback))
        except Exception as final_e:
            print(f"Final fallback parsing also failed: {final_e}")
            return {} # Return empty if all parsing fails
    except Exception as e:
        print(f"An unexpected error occurred while loading {file_path}: {e}")
        return {}

# --- Parsing functions adapted from lulc_data_engine.py ---

def _parse_single_resolution(res_value: Any) -> Optional[float]:
    """Parses a single resolution value."""
    if isinstance(res_value, (int, float)):
        return float(res_value)
    if isinstance(res_value, str):
        res_str = re.sub(r'[^\d.]', '', res_value)
        if res_str:
            return float(res_str)
    return None

def parse_resolution(resolution_field: Any) -> Dict[str, Optional[float]]:
    """
    Parses the 'spatial_resolution' field which can be a number, string, or list of objects.
    Returns a dictionary with 'value', 'min_val', 'max_val'.
    """
    default_res = 30.0
    parsed_values = []

    if isinstance(resolution_field, list):
        current_res_obj = None
        for item in resolution_field:
            if isinstance(item, dict):
                if item.get('current', False):
                    current_res_obj = item
                    break
        
        if current_res_obj: # Prioritize 'current' object
            val = _parse_single_resolution(current_res_obj.get('resolution'))
            if val is not None:
                parsed_values.append(val)
        else: # Process all resolution values in the list
            for item in resolution_field:
                if isinstance(item, dict):
                    val = _parse_single_resolution(item.get('resolution'))
                    if val is not None:
                        parsed_values.append(val)
                else: # Handle direct values in list
                    val = _parse_single_resolution(item)
                    if val is not None:
                        parsed_values.append(val)
    else: # Single value
        val = _parse_single_resolution(resolution_field)
        if val is not None:
            parsed_values.append(val)

    if not parsed_values:
        return {'value': default_res, 'min_val': default_res, 'max_val': default_res}

    # For simplicity, if multiple values, use the first as 'value', and actual min/max
    # This matches the slider behavior needing min/max for range.
    # If only one value, it's used for all.
    final_value = parsed_values[0]
    min_val = min(parsed_values)
    max_val = max(parsed_values)
    
    return {'value': final_value, 'min_val': min_val, 'max_val': max_val}


def _parse_single_accuracy(acc_value: Any) -> Optional[float]:
    """Parses a single accuracy value."""
    if isinstance(acc_value, (int, float)):
        return float(acc_value)
    if isinstance(acc_value, str):
        # Handle cases like "80.3%" or "Not available"
        if acc_value.lower() in ['not informed', 'incomplete', 'n/a', 'not available']:
            return 0.0 # Or None, depending on how downstream handles it
        acc_str = re.sub(r'[^\d.]', '', acc_value)
        if acc_str:
            return float(acc_str)
    return None

def parse_accuracy(accuracy_field: Any) -> Dict[str, Optional[float]]:
    """
    Parses the 'overall_accuracy' or 'accuracy' field.
    Handles numbers, strings, or dicts with 'overall', 'status', 'by_product', etc.
    Returns a dictionary with 'value', 'min_val', 'max_val'.
    """
    default_acc = 0.0
    accuracies = []

    if isinstance(accuracy_field, dict):
        if accuracy_field.get('status') == 'not_available':
            return {'value': 0.0, 'min_val': 0.0, 'max_val': 0.0}
        
        # Prioritize 'current' product if available
        if 'by_product' in accuracy_field and isinstance(accuracy_field['by_product'], list):
            current_product_acc = None
            for prod in accuracy_field['by_product']:
                if isinstance(prod, dict) and prod.get('current', False):
                    current_product_acc = _parse_single_accuracy(prod.get('accuracy'))
                    break
            if current_product_acc is not None:
                 accuracies.append(current_product_acc)

        if not accuracies and 'overall' in accuracy_field: # Fallback to main 'overall'
            val = _parse_single_accuracy(accuracy_field['overall'])
            if val is not None:
                accuracies.append(val)
        
        # If still no accuracies, check other nested structures like by_collection
        if not accuracies and 'by_collection' in accuracy_field and isinstance(accuracy_field['by_collection'], list):
            current_collection_acc = None
            for coll in accuracy_field['by_collection']:
                if isinstance(coll, dict) and coll.get('current', False):
                    current_collection_acc = _parse_single_accuracy(coll.get('accuracy'))
                    break
            if current_collection_acc is not None:
                accuracies.append(current_collection_acc)
            elif accuracy_field['by_collection']: # take first if no current
                first_coll_acc = _parse_single_accuracy(accuracy_field['by_collection'][0].get('accuracy'))
                if first_coll_acc is not None:
                     accuracies.append(first_coll_acc)

    else: # Single value
        val = _parse_single_accuracy(accuracy_field)
        if val is not None:
            accuracies.append(val)

    if not accuracies:
        return {'value': default_acc, 'min_val': default_acc, 'max_val': default_acc}

    # Use the first found accuracy as the primary 'value', and actual min/max
    final_value = accuracies[0]
    min_val = min(accuracies)
    max_val = max(accuracies)

    return {'value': final_value, 'min_val': min_val, 'max_val': max_val}

def parse_reference_system(reference_system_field: Any) -> str:
    """
    Parses the 'reference_system' field and returns a string representation.
    Handles strings, lists of strings, or lists containing dictionaries.
    """
    parsed_systems: List[str] = []
    if isinstance(reference_system_field, str):
        # Split if it's a comma-separated string, otherwise add as is
        if ',' in reference_system_field:
            parsed_systems.extend([s.strip() for s in reference_system_field.split(',') if s.strip()])
        else:
            parsed_systems.append(reference_system_field.strip())
    elif isinstance(reference_system_field, list):
        for item in reference_system_field:
            if isinstance(item, str):
                parsed_systems.append(item.strip())
            elif isinstance(item, dict):
                # Try to extract a common key for the system name
                epsg_code = item.get('epsg_code', '')
                description = item.get('description', '')
                if epsg_code:
                    parsed_systems.append(f"{epsg_code} ({description})" if description else epsg_code)
                elif description:
                    parsed_systems.append(description)
    # Remove duplicates and return as comma-separated string
    unique_systems = sorted(list(set(s for s in parsed_systems if s)))
    return ', '.join(unique_systems) if unique_systems else 'Not specified'


def _generate_display_name(name: str, acronym: Optional[str]) -> str:
    """Generates a display name, preferring acronym if short and available."""
    if acronym and len(acronym) <= 15: # Arbitrary length for a good display acronym
        return acronym
    return name.split('(')[0].strip() # Basic truncation

def _standardize_type(coverage_field: Optional[str]) -> str:
    """Standardizes coverage to a type category."""
    if not coverage_field:
        return "Unknown"
    coverage_lower = coverage_field.lower()
    if "global" in coverage_lower:
        return "Global"
    if "continental" in coverage_lower:
        return "Continental"
    if "national" in coverage_lower or "nacional" in coverage_lower:
        return "National"
    if "regional" in coverage_lower:
        return "Regional"
    return "Other"

def _standardize_methodology(methodology: Optional[str], classification_method: Optional[str]) -> str:
    """Standardizes methodology from available fields."""
    text_to_check = ""
    if methodology:
        text_to_check += methodology.lower() + " "
    if classification_method:
        text_to_check += classification_method.lower()
    
    if not text_to_check.strip():
        return "Unknown"

    if any(term in text_to_check for term in ['deep learning', 'neural network', 'cnn', 'u-net']):
        return 'Deep Learning'
    if any(term in text_to_check for term in ['machine learning', 'random forest', 'gradient boost', 'catboost', 'decision tree']): # Added decision tree here
        return 'Machine Learning'
    if any(term in text_to_check for term in ['visual interpretation', 'visual']):
        return 'Visual Interpretation'
    if 'hybrid' in text_to_check or ('combined' in text_to_check and not ('learning' in text_to_check or 'visual' in text_to_check)): # Refined 'Combined'
        return 'Hybrid/Combined'
    if 'statistical' in text_to_check or 'regression' in text_to_check:
        return 'Statistical Methods'
    return 'Other'


def _parse_available_years(years_field: Any) -> List[int]:
    """Parses the 'available_years' field into a list of integers."""
    if isinstance(years_field, list):
        return sorted(list(set(int(y) for y in years_field if isinstance(y, (int, float)) or (isinstance(y, str) and y.isdigit()))))
    if isinstance(years_field, str):
        try:
            # Assuming comma-separated or space-separated, or single year
            return sorted(list(set(int(y.strip()) for y in re.split(r'[\s,]+', years_field) if y.strip().isdigit())))
        except ValueError:
            return []
    return []

def _get_safe_value(data: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    return data.get(key, default)

# Main interpreter function
def interpret_initiatives_metadata(file_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    Reads initiatives_metadata.jsonc, processes it, and returns a Pandas DataFrame.
    """
    actual_file_path: Path
    if file_path is None:        # Default path relative to this script's parent's parent directory (project root)
        actual_file_path = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "initiatives_metadata.jsonc"
    else:
        actual_file_path = Path(file_path)
        
    raw_data = _load_jsonc_file(actual_file_path)
    if not raw_data:
        return pd.DataFrame() # Return empty DataFrame if loading failed

    processed_initiatives = []
    for initiative_name, details in raw_data.items():
        if not isinstance(details, dict): # Skip if details are not a dictionary
            print(f"Warning: Skipping initiative '{initiative_name}' due to unexpected data format: {type(details)}")
            continue

        acronym = _get_safe_value(details, 'acronym')
        display_name = _generate_display_name(initiative_name, acronym)
        
        resolution_data = parse_resolution(_get_safe_value(details, 'spatial_resolution'))
        accuracy_data = parse_accuracy(_get_safe_value(details, 'overall_accuracy') or _get_safe_value(details, 'accuracy')) # Check both keys
        available_years_list = _parse_available_years(_get_safe_value(details, 'available_years'))
        available_years_str = f"{min(available_years_list)}-{max(available_years_list)}" if available_years_list else "N/A"
        sensors_referenced_list = _get_safe_value(details, 'sensors_referenced', [])
        class_legend_data = _get_safe_value(details, 'class_legend') # Get class legend data

        initiative_dict = {
            'Name': initiative_name,
            'Acronym': acronym,
            'Display_Name': display_name,
            'Resolution': resolution_data['value'],
            'Resolution_min_val': resolution_data['min_val'],
            'Resolution_max_val': resolution_data['max_val'],
            'Accuracy': accuracy_data['value'],
            'Accuracy_min_val': accuracy_data['min_val'],
            'Accuracy_max_val': accuracy_data['max_val'],
            'Type': _standardize_type(_get_safe_value(details, 'coverage')),
            'Methodology': _standardize_methodology(
                _get_safe_value(details, 'methodology'),
                _get_safe_value(details, 'classification_method')
            ),
            'Coverage': _get_safe_value(details, 'coverage'),
            'Provider': _get_safe_value(details, 'provider'),
            'Source': _get_safe_value(details, 'source'),
            'Update_Frequency': _get_safe_value(details, 'update_frequency'),
            'Temporal_Frequency': _get_safe_value(details, 'update_frequency'), # Add Temporal_Frequency column
            'Temporal_Coverage_Start': _get_safe_value(details, 'temporal_coverage_start_date'),
            'Temporal_Coverage_End': _get_safe_value(details, 'temporal_coverage_end_date'),
            'Available_Years_Str': available_years_str,
            'Available_Years_List': json.dumps(available_years_list), # Convert list to JSON string
            'Number_of_Classes': _get_safe_value(details, 'number_of_classes'),
            'Class_Legend': json.dumps(class_legend_data) if isinstance(class_legend_data, list) else class_legend_data, # Convert to JSON string if it's a list
            'Algorithm': _get_safe_value(details, 'algorithm'),
            'Classification_Method': _get_safe_value(details, 'classification_method'),
            'Sensors_Referenced': json.dumps(sensors_referenced_list) # Already a JSON string
        }
        processed_initiatives.append(initiative_dict)

    df = pd.DataFrame(processed_initiatives)    # Post-processing: Ensure essential numeric columns are float, fill NaNs if necessary
    numeric_cols = ['Resolution', 'Resolution_min_val', 'Resolution_max_val', 
                    'Accuracy', 'Accuracy_min_val', 'Accuracy_max_val', 'Number_of_Classes']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) # Coerce errors to NaN, then fill with 0

    return df

if __name__ == '__main__':
    # Example usage:
    # Ensure the path to initiatives_metadata.jsonc is correct relative to where you run this.
    # For testing, you might need to adjust the default path in interpret_initiatives_metadata
    # or pass the correct path directly.
    
    # Assuming the script is in scripts/utilities/ and data is in data/raw/
    project_root_path = Path(__file__).resolve().parent.parent.parent
    test_file_path = project_root_path / "data" / "raw" / "initiatives_metadata.jsonc"
    
    print(f"Attempting to load data from: {test_file_path}")
    
    df_initiatives = interpret_initiatives_metadata(test_file_path)
    
    if not df_initiatives.empty:
        print("\nSuccessfully processed initiatives:")
        print(df_initiatives.head())
        print(f"\nTotal initiatives processed: {len(df_initiatives)}")
        
        print("\nData types:")
        print(df_initiatives.dtypes)
        
        print("\nChecking for NaNs in key columns:")
        key_cols_for_nan_check = ['Name', 'Display_Name', 'Resolution', 'Accuracy', 'Type', 'Methodology']
        for col in key_cols_for_nan_check:
            if col in df_initiatives.columns:
                 print(f"NaNs in {col}: {df_initiatives[col].isnull().sum()}")
            else:
                print(f"Column {col} not found for NaN check.")

        # Example: Filter for initiatives with resolution <= 10m
        # high_res_initiatives = df_initiatives[df_initiatives['Resolution'] <= 10]
        # print("\nHigh-resolution initiatives (<=10m):")
        # print(high_res_initiatives[['Display_Name', 'Resolution', 'Accuracy']])
    else:
        print("\nNo data processed or an error occurred.")

    # Test with default path (if run from a context where it resolves correctly)
    # print("\n--- Testing with default path ---")
    # df_default = interpret_initiatives_metadata()
    # if not df_default.empty:
    #     print(df_default[['Display_Name', 'Resolution', 'Accuracy']].head())
    # else:
    #     print("Processing with default path failed or returned empty.")

