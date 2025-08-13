"""
Universal Cache Utilities
========================

Utilitários de cache para processamento de dados e otimização.
Reorganizado para estrutura modular do dashboard.

Author: LANDAGRI-B Project Team 
Date: 2025-07-30
"""

import functools
import os
import pickle
from collections.abc import Callable


def smart_cache_data(func: Callable | None = None, *, ttl: int = 3600) -> Callable:
    """
    Smart cache decorator para funções de processamento de dados.

    Args:
        func: Função para fazer cache
        ttl: Time to live em segundos (padrão: 3600)

    Returns:
        Função com cache aplicado
    """

    def decorator(func: Callable) -> Callable:
        cache_dir = "cache"
        os.makedirs(cache_dir, exist_ok=True)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key based on function name and arguments
            cache_key = (
                f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            )
            cache_file = os.path.join(cache_dir, f"{cache_key}.cache")

            # Check if cache exists and is valid
            if os.path.exists(cache_file):
                try:
                    # Check file age
                    file_age = os.path.getmtime(cache_file)
                    import time

                    if time.time() - file_age < ttl:
                        with open(cache_file, "rb") as f:
                            return pickle.load(f)
                    else:
                        # Cache expired, remove it
                        os.remove(cache_file)
                except Exception:
                    # If cache is corrupted, remove it
                    try:
                        os.remove(cache_file)
                    except:
                        pass

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

    if func is None:
        # Called with arguments: @smart_cache_data(ttl=300)
        return decorator
    else:
        # Called without arguments: @smart_cache_data
        return decorator(func)


def clear_function_cache(func_name: str | None = None) -> None:
    """
    Limpa cache para função específica ou todo o cache.

    Args:
        func_name: Nome da função para limpar cache (None para tudo)
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
    Obtém informações sobre arquivos de cache.

    Returns:
        Dicionário com informações do cache
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
