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
        # Adjusted path: removed "raw" - this change is applied where _load_jsonc_file is CALLED,
        # not inside _load_jsonc_file itself, as it's a generic loader.
        # The calling functions (like interpret_initiatives_metadata) will construct the path without "raw".
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
        # Changed default path to remove "raw" subdirectory
        actual_file_path = Path(__file__).resolve().parent.parent.parent / "data" / "initiatives_metadata.jsonc"
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
        class_legend_data = _get_safe_value(details, 'class_legend') 
        
        processed_class_legend_list = []
        if isinstance(class_legend_data, str):
            processed_class_legend_list = [s.strip() for s in class_legend_data.split(',') if s.strip()]
        elif isinstance(class_legend_data, list):
            processed_class_legend_list = class_legend_data # Assumes it's already a list of strings

        # New fields for agricultural classes and capability
        num_agri_classes = _get_safe_value(details, 'number_of_agriculture_classes')
        capability_text = _get_safe_value(details, 'capability') # For general capability display
        agricultural_capabilities_text = _get_safe_value(details, 'agricultural_capabilities') # Specific for agri legend

        # Derive Agricultural_Class_Legend
        agri_legend_list = []
        if isinstance(num_agri_classes, int) and num_agri_classes == 1 and \
           isinstance(agricultural_capabilities_text, str) and agricultural_capabilities_text.strip():
            agri_legend_list.append(agricultural_capabilities_text.strip())
        # TODO: Add logic here if agricultural_capabilities_text could be a list of strings for num_agri_classes > 1
        # For now, it handles the case where number_of_agriculture_classes = 1 and agricultural_capabilities is its name.

        initiative_dict = {
            'Name': initiative_name,
            'Acronym': acronym,
            'Display_Name': display_name,
            'Resolution': resolution_data['value'],
            'Resolution_min_val': resolution_data['min_val'],
            'Resolution_max_val': resolution_data['max_val'],
            'Accuracy (%)': accuracy_data['value'], # Changed 'Accuracy' to 'Accuracy (%)'
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
            'Classes': _get_safe_value(details, 'number_of_classes'), 
            'Num_Agri_Classes': num_agri_classes, # Added new column
            'Class_Legend': json.dumps(processed_class_legend_list), # Store the processed list as JSON string
            'Agricultural_Class_Legend': json.dumps(agri_legend_list), # New: Derived agricultural legend
            'Capability': capability_text, # Added new column
            'Algorithm': _get_safe_value(details, 'algorithm'),
            'Classification_Method': _get_safe_value(details, 'classification_method'),
            'Sensors_Referenced': json.dumps(sensors_referenced_list) 
        }
        processed_initiatives.append(initiative_dict)

    df = pd.DataFrame(processed_initiatives)    # Post-processing: Ensure essential numeric columns are float, fill NaNs if necessary
    numeric_cols = ['Resolution', 'Resolution_min_val', 'Resolution_max_val', 
                    'Accuracy (%)', 'Accuracy_min_val', 'Accuracy_max_val', 'Classes',
                    'Num_Agri_Classes'] # Added Num_Agri_Classes to numeric cols
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) # Coerce errors to NaN, then fill with 0

    return df

def interpret_combined_conab_metadata(
    main_file_path: Optional[Union[str, Path]] = None, 
    conab_file_path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Reads both initiatives_metadata.jsonc and conab_detailed_initiative.jsonc, 
    combines them, and returns a unified Pandas DataFrame.
    
    Args:
        main_file_path: Path to main initiatives metadata file
        conab_file_path: Path to CONAB detailed initiative file
        
    Returns:
        Combined DataFrame with all initiatives
    """
    # Set default paths
    if main_file_path is None:
        main_file_path = Path(__file__).resolve().parent.parent.parent / "data" / "initiatives_metadata.jsonc"
    else:
        main_file_path = Path(main_file_path)
        
    if conab_file_path is None:
        conab_file_path = Path(__file__).resolve().parent.parent.parent / "data" / "conab_detailed_initiative.jsonc"
    else:
        conab_file_path = Path(conab_file_path)
    
    # Load main initiatives data
    main_df = interpret_initiatives_metadata(main_file_path)
    
    # Load CONAB data
    conab_df = interpret_initiatives_metadata(conab_file_path)
    
    # Combine the DataFrames
    if not main_df.empty and not conab_df.empty:
        combined_df = pd.concat([main_df, conab_df], ignore_index=True)
        print(f"Combined {len(main_df)} main initiatives with {len(conab_df)} CONAB initiatives")
        return combined_df
    elif not main_df.empty:
        print("Only main initiatives loaded (CONAB file not found or empty)")
        return main_df
    elif not conab_df.empty:
        print("Only CONAB initiatives loaded (main file not found or empty)")
        return conab_df
    else:
        print("No initiatives loaded from either file")
        return pd.DataFrame()

def get_conab_crop_availability(conab_file_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Extracts detailed crop availability data from CONAB initiative metadata.
    
    Args:
        conab_file_path: Path to CONAB detailed initiative file
        
    Returns:
        Dictionary with detailed crop coverage information
    """
    if conab_file_path is None:
        conab_file_path = Path(__file__).resolve().parent.parent.parent / "data" / "conab_detailed_initiative.jsonc"
    else:
        conab_file_path = Path(conab_file_path)
    
    raw_data = _load_jsonc_file(conab_file_path)
    
    if not raw_data:
        return {}
    
    # Extract CONAB initiative data
    conab_initiative = raw_data.get("CONAB Crop Monitoring Initiative", {})
    detailed_crop_coverage = conab_initiative.get("detailed_crop_coverage", {})
    
    return {
        "crop_coverage": detailed_crop_coverage,
        "regional_coverage": conab_initiative.get("regional_coverage", []),
        "data_products": conab_initiative.get("data_products", []),
        "available_years": conab_initiative.get("available_years", []),
        "temporal_coverage_notes": conab_initiative.get("temporal_coverage_notes", {})
    }

def load_mesoregions_dictionary(dictionary_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Loads the mesoregions dictionary JSON file.
    
    Args:
        dictionary_path: Path to the json_dictionary.json file
        
    Returns:
        Dictionary with mesoregions data
    """
    if dictionary_path is None:
        dictionary_path = Path(__file__).resolve().parent.parent.parent / "data" / "json_dictionary.json"
    else:
        dictionary_path = Path(dictionary_path)
    
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at {dictionary_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {dictionary_path}: {e}")
        return {}

def get_mesoregion_by_state(state_code: str, mesoregions_dict: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Returns the mesoregion name for a given state code.
    
    Args:
        state_code: Two-letter state code (e.g., 'SP', 'RJ')
        mesoregions_dict: Optional dictionary with mesoregions data
        
    Returns:
        Mesoregion name or None if not found
    """
    if mesoregions_dict is None:
        mesoregions_dict = load_mesoregions_dictionary()
    
    if not mesoregions_dict or 'mesoregions' not in mesoregions_dict:
        return None
    
    state_code_upper = state_code.upper()
    
    for mesoregion_name, mesoregion_data in mesoregions_dict['mesoregions'].items():
        if 'states' in mesoregion_data:
            for state in mesoregion_data['states']:
                if isinstance(state, dict) and state.get('sigla', '').upper() == state_code_upper:
                    return mesoregion_name
    
    return None

def get_states_by_mesoregion(mesoregion_name: str, mesoregions_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """
    Returns list of states for a given mesoregion.
    
    Args:
        mesoregion_name: Name of the mesoregion
        mesoregions_dict: Optional dictionary with mesoregions data
        
    Returns:
        List of dictionaries with state information
    """
    if mesoregions_dict is None:
        mesoregions_dict = load_mesoregions_dictionary()
    
    if not mesoregions_dict or 'mesoregions' not in mesoregions_dict:
        return []
    
    mesoregion_data = mesoregions_dict['mesoregions'].get(mesoregion_name, {})
    return mesoregion_data.get('states', [])

def enrich_conab_data_with_mesoregions(conab_data: Dict[str, Any], mesoregions_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enriches CONAB crop availability data with mesoregion information.
    
    Args:
        conab_data: CONAB crop availability data
        mesoregions_dict: Optional dictionary with mesoregions data
        
    Returns:
        Enriched CONAB data with mesoregion mappings
    """
    if mesoregions_dict is None:
        mesoregions_dict = load_mesoregions_dictionary()
    
    enriched_data = conab_data.copy()
    
    if 'crop_coverage' in enriched_data:
        for crop_name, crop_data in enriched_data['crop_coverage'].items():
            if 'regions' in crop_data:
                # Add mesoregion mapping for each state
                regions_with_mesoregions = []
                for state_code in crop_data['regions']:
                    mesoregion = get_mesoregion_by_state(state_code, mesoregions_dict)
                    mesoregion_info = get_mesoregion_info(mesoregion, mesoregions_dict) if mesoregion else None
                    
                    regions_with_mesoregions.append({
                        'state_code': state_code,
                        'mesoregion': mesoregion,
                        'mesoregion_color': mesoregion_info.get('color') if mesoregion_info else None,
                        'mesoregion_pt': mesoregion_info.get('name_pt') if mesoregion_info else None
                    })
                
                crop_data['regions_with_mesoregions'] = regions_with_mesoregions
                
                # Group by mesoregion with enhanced information
                mesoregion_groups = {}
                for region_info in regions_with_mesoregions:
                    mesoregion = region_info['mesoregion']
                    if mesoregion:
                        if mesoregion not in mesoregion_groups:
                            mesoregion_groups[mesoregion] = {
                                'states': [],
                                'color': region_info['mesoregion_color'],
                                'name_pt': region_info['mesoregion_pt']
                            }
                        mesoregion_groups[mesoregion]['states'].append(region_info['state_code'])
                
                crop_data['mesoregion_groups'] = mesoregion_groups
    
    # Add mesoregion mapping for regional_coverage with enhanced information
    if 'regional_coverage' in enriched_data:
        regional_coverage_with_mesoregions = []
        for region_name in enriched_data['regional_coverage']:
            # Extract state code from region name (e.g., "Rondônia (RO)" -> "RO")
            state_code_match = re.search(r'\(([A-Z]{2})\)', region_name)
            if state_code_match:
                state_code = state_code_match.group(1)
                mesoregion = get_mesoregion_by_state(state_code, mesoregions_dict)
                mesoregion_info = get_mesoregion_info(mesoregion, mesoregions_dict) if mesoregion else None
                
                regional_coverage_with_mesoregions.append({
                    'region_name': region_name,
                    'state_code': state_code,
                    'mesoregion': mesoregion,
                    'mesoregion_color': mesoregion_info.get('color') if mesoregion_info else None,
                    'mesoregion_pt': mesoregion_info.get('name_pt') if mesoregion_info else None
                })
            else:
                regional_coverage_with_mesoregions.append({
                    'region_name': region_name,
                    'state_code': None,
                    'mesoregion': None,
                    'mesoregion_color': None,
                    'mesoregion_pt': None
                })
        
        enriched_data['regional_coverage_with_mesoregions'] = regional_coverage_with_mesoregions
    
    # Add mesoregions color palette
    enriched_data['mesoregions_palette'] = get_all_mesoregions_with_colors(mesoregions_dict)
    
    return enriched_data

def get_integrated_conab_analysis(
    conab_file_path: Optional[Union[str, Path]] = None,
    dictionary_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Gets integrated analysis of CONAB data with mesoregion information.
    
    Args:
        conab_file_path: Path to CONAB detailed initiative file
        dictionary_path: Path to json_dictionary.json file
        
    Returns:
        Dictionary with integrated analysis
    """
    # Load both datasets
    conab_data = get_conab_crop_availability(conab_file_path)
    mesoregions_dict = load_mesoregions_dictionary(dictionary_path)
    
    if not conab_data or not mesoregions_dict:
        return {}
    
    # Enrich CONAB data with mesoregion information
    enriched_data = enrich_conab_data_with_mesoregions(conab_data, mesoregions_dict)
    
    # Create summary analysis
    analysis = {
        'enriched_conab_data': enriched_data,
        'mesoregions_dict': mesoregions_dict,
        'summary': {
            'total_crops': len(enriched_data.get('crop_coverage', {})),
            'total_states_covered': len(set(
                region['state_code'] for crop_data in enriched_data.get('crop_coverage', {}).values()
                for region in crop_data.get('regions_with_mesoregions', [])
                if region['state_code']
            )),
            'mesoregions_covered': list(set(
                region['mesoregion'] for crop_data in enriched_data.get('crop_coverage', {}).values()
                for region in crop_data.get('regions_with_mesoregions', [])
                if region['mesoregion']
            )),
            'crops_by_mesoregion': {}
        }
    }
      # Analyze crops by mesoregion with enhanced information
    crops_by_mesoregion = {}
    for crop_name, crop_data in enriched_data.get('crop_coverage', {}).items():
        for mesoregion, mesoregion_info in crop_data.get('mesoregion_groups', {}).items():
            if mesoregion not in crops_by_mesoregion:
                crops_by_mesoregion[mesoregion] = {
                    'crops': [],
                    'color': mesoregion_info.get('color'),
                    'name_pt': mesoregion_info.get('name_pt'),
                    'total_states': len(set())
                }
            crops_by_mesoregion[mesoregion]['crops'].append({
                'crop': crop_name,
                'states': mesoregion_info.get('states', []),                'first_crop_years': crop_data.get('first_crop_years', {}),
                'second_crop_years': crop_data.get('second_crop_years', {})
            })
            
            # Update total states for this mesoregion
            all_states = set()
            for crop_info in crops_by_mesoregion[mesoregion]['crops']:
                all_states.update(crop_info['states'])
            crops_by_mesoregion[mesoregion]['total_states'] = len(all_states)
    
    analysis['summary']['crops_by_mesoregion'] = crops_by_mesoregion
    
    return analysis

def get_mesoregion_info(mesoregion_name: str, mesoregions_dict: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Returns complete mesoregion information including color and names in both languages.
    
    Args:
        mesoregion_name: Name of the mesoregion (in English or Portuguese)
        mesoregions_dict: Optional dictionary with mesoregions data
        
    Returns:
        Dictionary with mesoregion information or None if not found
    """
    if mesoregions_dict is None:
        mesoregions_dict = load_mesoregions_dictionary()
    
    if not mesoregions_dict or 'mesoregions' not in mesoregions_dict:
        return None
    
    # First try direct match (English names)
    if mesoregion_name in mesoregions_dict['mesoregions']:
        data = mesoregions_dict['mesoregions'][mesoregion_name].copy()
        data['name_en'] = mesoregion_name
        return data
    
    # Try matching Portuguese names
    for eng_name, mesoregion_data in mesoregions_dict['mesoregions'].items():
        if mesoregion_data.get('name_pt') == mesoregion_name:
            data = mesoregion_data.copy()
            data['name_en'] = eng_name
            return data
    
    return None

def get_mesoregion_color(mesoregion_name: str, mesoregions_dict: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Returns the color code for a given mesoregion.
    
    Args:
        mesoregion_name: Name of the mesoregion (in English or Portuguese)
        mesoregions_dict: Optional dictionary with mesoregions data
        
    Returns:
        Color code (hex) or None if not found
    """
    info = get_mesoregion_info(mesoregion_name, mesoregions_dict)
    return info.get('color') if info else None

def get_all_mesoregions_with_colors(mesoregions_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, str]]:
    """
    Returns all mesoregions with their colors and names.
    
    Args:
        mesoregions_dict: Optional dictionary with mesoregions data
        
    Returns:
        Dictionary mapping English names to color and Portuguese name info
    """
    if mesoregions_dict is None:
        mesoregions_dict = load_mesoregions_dictionary()
    
    if not mesoregions_dict or 'mesoregions' not in mesoregions_dict:
        return {}
    
    result = {}
    for eng_name, data in mesoregions_dict['mesoregions'].items():
        result[eng_name] = {
            'color': data.get('color', '#CCCCCC'),
            'name_pt': data.get('name_pt', eng_name),
            'name_en': eng_name
        }
    
    return result

if __name__ == '__main__':
    # Example usage:
    # Ensure the path to initiatives_metadata.jsonc is correct relative to where you run this.
    # For testing, you might need to adjust the default path in interpret_initiatives_metadata
    # or pass the correct path directly.
    
    # Assuming the script is in scripts/utilities/ and data is in data/raw/
    project_root_path = Path(__file__).resolve().parent.parent.parent
    # Changed test file path to remove "raw" subdirectory
    test_file_path = project_root_path / "data" / "initiatives_metadata.jsonc"
    
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