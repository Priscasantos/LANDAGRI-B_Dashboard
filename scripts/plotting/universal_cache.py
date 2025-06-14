#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Cache Decorator
=========================

Provides caching functionality that works both in Streamlit context 
and standalone execution, ensuring charts can be generated in both modes.

Author: Dashboard Iniciativas LULC
Date: 2024
"""

import functools
from typing import Any, Callable, Dict
import hashlib
import pickle
import time

# Global cache for standalone execution
_STANDALONE_CACHE: Dict[str, Dict[str, Any]] = {}

def smart_cache_data(ttl: int = 300, max_entries: int = 50):
    """
    Universal cache decorator that works both with and without Streamlit.
    Automatically detects context and uses appropriate caching strategy.
    
    Args:
        ttl: Time to live in seconds (for standalone mode)
        max_entries: Maximum number of cached entries
        
    Returns:
        Decorated function with appropriate caching
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Simple check: avoid Streamlit completely in standalone mode
            use_streamlit = False
            
            # Only try Streamlit if we detect we might be in a Streamlit context
            try:
                # Check environment variables that indicate Streamlit is running
                import os
                if any(key.startswith('STREAMLIT_') for key in os.environ.keys()):
                    use_streamlit = True
                else:
                    # Check if we're being called from a streamlit process
                    import sys
                    if any('streamlit' in str(arg).lower() for arg in sys.argv):
                        use_streamlit = True
            except Exception:
                pass
            
            if use_streamlit:
                try:
                    import streamlit as st
                    # Use Streamlit caching only if we're sure we're in the right context
                    cached_func = st.cache_data(ttl=ttl)(func)
                    return cached_func(*args, **kwargs)
                except Exception:
                    # Fall back to standalone if Streamlit fails
                    pass
            
            # Use standalone caching (default for most cases)
            return _standalone_cache_wrapper(func, ttl, max_entries)(*args, **kwargs)
        
        return wrapper
    return decorator


def _standalone_cache_wrapper(func: Callable, ttl: int, max_entries: int) -> Callable:
    """Internal wrapper for standalone caching"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        cache_key = _create_cache_key(func.__name__, args, kwargs)
        
        # Check if we have a valid cached result
        if cache_key in _STANDALONE_CACHE:
            cached_data = _STANDALONE_CACHE[cache_key]
            if time.time() - cached_data['timestamp'] < ttl:
                return cached_data['result']
            else:
                # Remove expired entry
                del _STANDALONE_CACHE[cache_key]
        
        # Clean cache if too many entries
        if len(_STANDALONE_CACHE) >= max_entries:
            _clean_old_cache_entries(max_entries // 2)
        
        # Execute function and cache result
        result = func(*args, **kwargs)
        _STANDALONE_CACHE[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
        
        return result
    
    return wrapper


def _create_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Create a hash-based cache key from function arguments"""
    try:
        # Create a string representation of arguments
        args_str = str(args) + str(sorted(kwargs.items()))
        # Create hash
        key_data = f"{func_name}:{args_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    except Exception:
        # Fallback to simple string representation
        return f"{func_name}:{hash(str(args))}:{hash(str(kwargs))}"


def _clean_old_cache_entries(keep_count: int):
    """Remove oldest cache entries, keeping only the specified count"""
    if len(_STANDALONE_CACHE) <= keep_count:
        return
    
    # Sort by timestamp and keep only the newest entries
    sorted_entries = sorted(
        _STANDALONE_CACHE.items(),
        key=lambda x: x[1]['timestamp'],
        reverse=True
    )
    
    # Clear cache and add back only the newest entries
    _STANDALONE_CACHE.clear()
    for key, value in sorted_entries[:keep_count]:
        _STANDALONE_CACHE[key] = value


def clear_cache():
    """Clear the standalone cache"""
    _STANDALONE_CACHE.clear()


def get_cache_info() -> Dict[str, Any]:
    """Get information about the current cache state"""
    return {
        'entries': len(_STANDALONE_CACHE),
        'keys': list(_STANDALONE_CACHE.keys()),
        'total_size': sum(
            len(pickle.dumps(entry['result'])) 
            for entry in _STANDALONE_CACHE.values()
        ) if _STANDALONE_CACHE else 0
    }
