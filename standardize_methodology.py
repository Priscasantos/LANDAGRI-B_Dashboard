#!/usr/bin/env python3
"""
Script to standardize methodology fields in metadata and perform other cleanup.
"""

import json
import re
from pathlib import Path

# Define the path to the metadata file relative to this script or project root
PROJECT_ROOT = Path(__file__).resolve().parent 
# Adjusted path: removed "raw"
METADATA_FILE_PATH = PROJECT_ROOT / "data" / "initiatives_metadata.jsonc"


def standardize_methodology_term(classification_method):
    """Map classification_method to standardized methodology categories."""
    if not isinstance(classification_method, str):
        return "Unknown" # Or handle as an error
    method = classification_method.lower()
    
    # More specific terms first
    if any(term in method for term in ['u-net', 'unet', 'convolutional neural network', 'cnn']):
        return 'Deep Learning'
    if any(term in method for term in ['random forest', 'gradient boosting', 'catboost', 'decision tree', 'support vector machine', 'svm']):
        return 'Machine Learning' # General ML if specific DL not identified
    if 'machine learning' in method: # Broader ML check
        return 'Machine Learning'
    if 'deep learning' in method: # Broader DL check
        return 'Deep Learning'
    if 'visual interpretation' in method:
        # Check for hybrid indicators
        if any(term in method for term in ['spectral', 'classification', 'automated']):
            return 'Hybrid'
        return 'Visual Interpretation'
    if 'combined' in method or 'hybrid' in method:
        return 'Hybrid'
    if 'object-based' in method or 'obia' in method:
        return 'OBIA' # Object-Based Image Analysis
    if 'pixel-based' in method:
        return 'Pixel-based Classification'
    if any(term in method for term in ['time series', 'temporal analysis']): # Added 'temporal analysis'
        # This could be ML/DL or other; if more context, refine
        return 'Time Series Analysis' 

    # Fallback for less clear cases or if none of the above match
    # Consider if a more generic term or 'Other' is appropriate
    # For now, defaulting to 'Machine Learning' if common keywords are present, else 'Other/複合'
    if any(term in method for term in ['classification', 'algorithm', 'model']):
        return 'Machine Learning' # Default assumption if classification related
        
    return 'Other/複合' # Default for truly unclassified or mixed methods not fitting above

def update_metadata_structure():
    """Update the metadata structure to standardize methodology fields."""
    
    # Check if the path needs to be adjusted based on where the script is located vs. workspace root
    # For a script inside dashboard-iniciativas (workspace root):
    actual_metadata_path = Path("data/raw/initiatives_metadata.jsonc")
    if not actual_metadata_path.exists():
        # Fallback if script is run from a different CWD, try the original relative path logic
        # This assumes the script itself is in the root of 'dashboard-iniciativas'
        # If the script is in a subfolder like 'scripts', this needs adjustment.
        # For this case, let's assume the script is in the root of the workspace.
        # If it's in /scripts/, then it should be Path("../data/raw/initiatives_metadata.jsonc")
        # Given the original error, the script is likely being run from the workspace root.
        # The METADATA_FILE_PATH was constructed assuming the script is in a parent of 'data'
        # Let's use a path relative to the workspace root directly.
        # This should be the most robust if the script is run from 'dashboard-iniciativas'
        pass # Keep actual_metadata_path as defined

    try:
        with open(actual_metadata_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Metadata file not found at {actual_metadata_path.resolve()}")
        return
    
    # Remove comments from JSONC for parsing
    json_content_for_parsing = re.sub(r"//.*", "", content)
    json_content_for_parsing = re.sub(r"/\\*[\\s\\S]*?\\*/", "", json_content_for_parsing) # Remove block comments
    
    try:
        metadata = json.loads(json_content_for_parsing)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from metadata file: {e}")
        # Attempt to find the problematic line
        lines = json_content_for_parsing.splitlines()
        for i, line_content in enumerate(lines):
            try:
                json.loads(line_content) # Try to parse line by line if it's a list of JSON objects
            except json.JSONDecodeError:
                if i < len(lines) -1 and (lines[i+1].strip().startswith("{") or lines[i+1].strip().startswith("[")):
                     # Likely a missing comma if the next line starts a new object/array
                    print(f"Possible syntax error (e.g., missing comma) near line {e.lineno}, column {e.colno}: '{lines[e.lineno-1]}'")
                    break
        return

    updated_count = 0
    for initiative_name, initiative_data in metadata.items():
        if isinstance(initiative_data, dict): # Ensure it's a dictionary
            # Standardize 'Methodology' and ensure 'Algorithm' exists
            classification_method_raw = initiative_data.get('classification_method')
            current_methodology = initiative_data.get('methodology')

            new_standardized_methodology = None
            if classification_method_raw:
                new_standardized_methodology = standardize_methodology_term(classification_method_raw)
            elif current_methodology: # If classification_method is missing, try to standardize current methodology
                new_standardized_methodology = standardize_methodology_term(current_methodology)
            
            if new_standardized_methodology:
                if initiative_data.get('methodology') != new_standardized_methodology:
                    initiative_data['methodology'] = new_standardized_methodology
                    updated_count += 1
                
                # Ensure 'algorithm' field exists, possibly populating from old 'methodology' or 'classification_method'
                if 'algorithm' not in initiative_data or not initiative_data['algorithm']:
                    if current_methodology and current_methodology != new_standardized_methodology : # If old methodology was more specific
                        initiative_data['algorithm'] = current_methodology
                    elif classification_method_raw:
                         initiative_data['algorithm'] = classification_method_raw # Use raw as algorithm detail
                    else:
                        initiative_data['algorithm'] = 'Not specified' 
            
            # Remove old/redundant fields if necessary (be cautious)
            # For example, if classification_method is now fully captured by methodology and algorithm
            # if 'classification_method' in initiative_data and new_standardized_methodology:
            #     del initiative_data['classification_method'] # Or set to None

    if updated_count > 0:
        print(f"Standardized 'methodology' for {updated_count} initiatives.")
        # Write the updated metadata back to the file (or a new file)
        # This part needs to be careful to preserve comments if possible, or write clean JSON
        try:
            with open(actual_metadata_path, 'w', encoding='utf-8') as f: # Use actual_metadata_path
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            print(f"Successfully updated and saved: {actual_metadata_path.resolve()}")
        except IOError as e:
            print(f"Error writing updated metadata to file: {e}")
    else:
        print("No methodology fields required updates based on current standardization rules.")

    # Print summary of new methodology distribution
    print("\nNew Methodology Distribution:")
    method_counts = {}
    for initiative_data in metadata.values():
        if isinstance(initiative_data, dict):
            method = initiative_data.get('methodology', 'Unknown')
            method_counts[method] = method_counts.get(method, 0) + 1
        
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count} initiatives")

if __name__ == "__main__":
    # Correct the path for __main__ execution context
    # This assumes the script is in the root of 'dashboard-iniciativas'
    script_dir = Path(__file__).parent
    metadata_file_to_run = script_dir / "data" / "raw" / "initiatives_metadata.jsonc"
    print(f"Running methodology standardization for: {metadata_file_to_run.resolve()}")
    update_metadata_structure()
