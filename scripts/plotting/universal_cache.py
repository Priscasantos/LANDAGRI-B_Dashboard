"""
Universal Cache Utilities
========================

Cache utilities for data processing and optimization.

Author: Dashboard Iniciativas LULC
Date: 2025-07-30
"""

import functools
import os
import pickle
from collections.abc import Callable


def smart_cache_data(func: Callable) -> Callable:
    """
    Smart cache decorator for data processing functions.

    Args:
        func: Function to cache

    Returns:
        Cached function
    """
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key based on function name and arguments
        cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
        cache_file = os.path.join(cache_dir, f"{cache_key}.cache")

        # Try to load from cache
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except:
                # If cache is corrupted, remove it
                os.remove(cache_file)

        # Execute function and cache result
        result = func(*args, **kwargs)

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)
        except Exception:
            # Cache failed, but return result anyway
            pass

        return result

    return wrapper


def clear_function_cache(func_name: str = None) -> None:
    """
    Clear cache for specific function or all cache.

    Args:
        func_name: Function name to clear cache for (None for all)
    """
    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        return

    for file in os.listdir(cache_dir):
        if file.endswith(".cache"):
            if func_name is None or file.startswith(f"{func_name}_"):
                try:
                    os.remove(os.path.join(cache_dir, file))
                except:
                    pass


def get_cache_info() -> dict:
    """
    Get information about cached files.

    Returns:
        Dictionary with cache information
    """
    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        return {"total_files": 0, "total_size": 0}

    total_files = 0
    total_size = 0

    for file in os.listdir(cache_dir):
        if file.endswith(".cache"):
            total_files += 1
            try:
                total_size += os.path.getsize(os.path.join(cache_dir, file))
            except:
                pass

    return {
        "total_files": total_files,
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
    }
