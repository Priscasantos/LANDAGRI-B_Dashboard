#!/usr/bin/env python3
"""
Script to standardize methodology fields in metadata
"""

import json
import re

def standardize_methodology(classification_method):
    """Map classification_method to standardized methodology categories"""
    method = classification_method.lower()
    
    if any(word in method for word in ['random forest', 'gradient boost', 'decision tree', 'machine learning', 'catboost']):
        return 'Machine Learning'
    elif any(word in method for word in ['deep learning', 'neural network', 'u-net', 'cnn']):
        return 'Deep Learning'
    elif 'visual interpretation' in method:
        if any(word in method for word in ['machine learning', 'spectral', 'classification', 'random forest', 'deep learning']):
            return 'Hybrid'
        else:
            return 'Visual Interpretation'
    elif 'combined' in method:
        return 'Hybrid'
    else:
        return 'Machine Learning'  # Default fallback

def update_metadata_structure():
    """Update the metadata structure to standardize methodology fields"""
    
    # Read the JSONC file
    with open('data/raw/initiatives_metadata.jsonc', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comments from JSONC
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if '//' in line:
            comment_pos = line.find('//')
            # Preserve the comment but separate it
            comment = line[comment_pos:]
            line_content = line[:comment_pos].rstrip()
            if line_content:
                cleaned_lines.append(line_content)
            cleaned_lines.append('        ' + comment)  # Preserve comment with proper indentation
        else:
            cleaned_lines.append(line)
    
    # Parse JSON
    # First, extract only the JSON part for parsing
    json_lines = []
    for line in lines:
        if '//' in line:
            comment_pos = line.find('//')
            line = line[:comment_pos].rstrip()
        if line.strip():
            json_lines.append(line)
    
    json_content = '\n'.join(json_lines)
    metadata = json.loads(json_content)
    
    # Update each entry
    for initiative_name, initiative_data in metadata.items():
        if 'methodology' in initiative_data and 'classification_method' in initiative_data:
            # Move current methodology to algorithm
            initiative_data['algorithm'] = initiative_data['methodology']
            
            # Create standardized methodology
            classification_method = initiative_data['classification_method']
            initiative_data['methodology'] = standardize_methodology(classification_method)
    
    print("Standardization mapping:")
    method_counts = {}
    for initiative_name, initiative_data in metadata.items():
        method = initiative_data.get('methodology', 'Unknown')
        method_counts[method] = method_counts.get(method, 0) + 1
        
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count} initiatives")
    
    # Write back with preserved structure and comments
    # This is a simplified approach - we'll manually update the specific entries

if __name__ == "__main__":
    update_metadata_structure()
