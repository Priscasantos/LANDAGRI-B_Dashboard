"""
Type Safety Utilities for NumPy to Python Native Type Conversions

This module provides utility functions to safely convert NumPy types to Python native types,
preventing compatibility issues with libraries that expect specific Python types.

Created as part of Issue #2: Implement robust type checking for NumPy to Python conversions
"""

import numpy as np
from typing import Any, Type

def safe_bool_conversion(value: Any) -> bool:
    """
    Safely convert any value to a Python native bool.
    
    Args:
        value: Value to convert (can be numpy.bool_, bool, or any truthy/falsy value)
        
    Returns:
        bool: Python native boolean value
        
    Examples:
        >>> safe_bool_conversion(np.True_)
        True
        >>> safe_bool_conversion(np.False_)
        False
        >>> safe_bool_conversion(1)
        True
    """
    return bool(value)

def safe_numeric_conversion(value: Any, target_type: Type = float) -> Any:
    """
    Safely convert NumPy numeric types to Python native numeric types.
    
    Args:
        value: Numeric value to convert (can be numpy types or Python types)
        target_type: Target Python type (int, float, etc.)
        
    Returns:
        Target type value
        
    Examples:
        >>> safe_numeric_conversion(np.int64(42), int)
        42
        >>> safe_numeric_conversion(np.float64(3.14), float)
        3.14
    """
    return target_type(value)

def safe_string_conversion(value: Any) -> str:
    """
    Safely convert any value to a Python native string.
    
    Args:
        value: Value to convert
        
    Returns:
        str: Python native string
    """
    if isinstance(value, (np.bytes_, bytes)):
        return value.decode('utf-8') if isinstance(value, bytes) else str(value)
    return str(value)

def safe_list_conversion(value: Any) -> list:
    """
    Safely convert array-like objects to Python native list.
    
    Args:
        value: Array-like value to convert (numpy array, list, tuple, etc.)
        
    Returns:
        list: Python native list
    """
    if isinstance(value, np.ndarray):
        return value.tolist()
    elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        return list(value)
    else:
        return [value]

def ensure_python_types(obj: Any) -> Any:
    """
    Recursively convert numpy types to Python native types in complex objects.
    
    Args:
        obj: Object that may contain numpy types
        
    Returns:
        Object with all numpy types converted to Python native types
    """
    if isinstance(obj, dict):
        return {key: ensure_python_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        converted = [ensure_python_types(item) for item in obj]
        return type(obj)(converted)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def validate_plotly_params(**kwargs) -> dict:
    """
    Validate and convert parameters for Plotly to ensure compatibility.
    
    Args:
        **kwargs: Parameters to validate and convert
        
    Returns:
        dict: Dictionary with converted parameters safe for Plotly
    """
    converted = {}
    
    # Common Plotly parameters that need type validation
    boolean_params = ['showlegend', 'visible', 'fill', 'connectgaps']
    numeric_params = ['width', 'size', 'opacity', 'line_width']
    
    for key, value in kwargs.items():
        if key in boolean_params:
            converted[key] = safe_bool_conversion(value)
        elif key in numeric_params:
            converted[key] = safe_numeric_conversion(value, float)
        else:
            converted[key] = ensure_python_types(value)
    
    return converted

# Decorator for automatic type conversion in plotting functions
def ensure_native_types(func):
    """
    Decorator to automatically convert numpy types to Python native types
    in function arguments and return values.
    """
    def wrapper(*args, **kwargs):
        # Convert arguments
        converted_args = [ensure_python_types(arg) for arg in args]
        converted_kwargs = {k: ensure_python_types(v) for k, v in kwargs.items()}
        
        # Call function with converted arguments
        result = func(*converted_args, **converted_kwargs)
        
        # Convert return value
        return ensure_python_types(result)
    
    return wrapper

# Type checking utilities
def is_numpy_type(obj: Any) -> bool:
    """Check if an object is a numpy type."""
    return isinstance(obj, (np.generic, np.ndarray))

def get_python_equivalent_type(numpy_obj: Any) -> Type:
    """Get the Python equivalent type for a numpy type."""
    if isinstance(numpy_obj, np.bool_):
        return bool
    elif isinstance(numpy_obj, np.integer):
        return int
    elif isinstance(numpy_obj, np.floating):
        return float
    elif isinstance(numpy_obj, (np.bytes_, np.str_)):
        return str
    elif isinstance(numpy_obj, np.ndarray):
        return list
    else:
        return type(numpy_obj)
