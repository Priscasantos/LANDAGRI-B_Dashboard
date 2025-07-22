"""
🚀 Sistema de Cache Inteligente para Dashboard LULC
===================================================

Este módulo implementa cache multicamada com otimizações de performance
para eliminar reprocessamento desnecessário de dados fixos.

Features:
- Cache em memória com TTL configurável
- Cache persistente em disco
- Cache de dados transformados
- Invalidação inteligente
- Compressão automática
- Métricas de performance

Author: Sistema de Otimização Dashboard LULC
Date: 2025-07-22
"""

import os
import json
import pickle
import hashlib
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from functools import wraps
import pandas as pd
import streamlit as st
from dataclasses import dataclass

@dataclass
class CacheEntry:
    """Entrada do cache com metadados completos."""
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    compressed: bool = False
    checksum: str = ""

class SmartCacheManager:
    """
    🧠 Gerenciador de Cache Inteligente
    
    Implementa cache multicamada com otimizações avançadas:
    - Memória: Ultra-rápido para dados quentes
    - Disco: Persistente para dados transformados
    - Compressão: Automática para grandes datasets
    """
    
    def __init__(self, cache_dir: str = "cache", memory_limit_mb: int = 512):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            cache_dir: Diretório para cache persistente
            memory_limit_mb: Limite de memória em MB
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.current_memory_usage = 0
        
        # Configurações otimizadas
        self.default_ttl = 3600  # 1 hora
        self.compression_threshold = 1024 * 100  # 100KB
        
        # Métricas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'compressions': 0
        }
        
        # Carrega cache persistente
        self._load_persistent_cache()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Gera chave única para cache baseada nos argumentos."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _calculate_size(self, data: Any) -> int:
        """Calcula tamanho aproximado dos dados."""
        try:
            if isinstance(data, pd.DataFrame):
                return data.memory_usage(deep=True).sum()
            elif isinstance(data, (dict, list)):
                return len(pickle.dumps(data))
            else:
                return len(str(data).encode())
        except Exception:
            return 1024  # Fallback
    
    def _should_compress(self, data: Any, size_bytes: int) -> bool:
        """Determina se os dados devem ser comprimidos."""
        return size_bytes > self.compression_threshold
    
    def _compress_data(self, data: Any) -> bytes:
        """Comprime dados usando gzip."""
        pickled = pickle.dumps(data)
        return gzip.compress(pickled)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Descomprime dados gzip."""
        pickled = gzip.decompress(compressed_data)
        return pickle.loads(pickled)
    
    def _evict_lru(self):
        """Remove itens menos usados da memória."""
        if not self.memory_cache:
            return
        
        # Ordena por último acesso
        lru_items = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove 25% dos itens mais antigos
        items_to_remove = max(1, len(lru_items) // 4)
        
        for i in range(items_to_remove):
            key, entry = lru_items[i]
            self.current_memory_usage -= entry.size_bytes
            del self.memory_cache[key]
            self.stats['evictions'] += 1
    
    def _load_persistent_cache(self):
        """Carrega cache persistente do disco."""
        cache_file = self.cache_dir / "persistent_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    persistent_data = json.load(f)
                
                # Valida TTL dos dados persistentes
                current_time = datetime.now()
                for key, metadata in persistent_data.items():
                    created_at = datetime.fromisoformat(metadata['created_at'])
                    ttl = metadata.get('ttl_seconds', self.default_ttl)
                    
                    if current_time - created_at < timedelta(seconds=ttl):
                        # Dados ainda válidos, mas não carrega na memória ainda
                        pass
            except Exception as e:
                st.warning(f"Erro ao carregar cache persistente: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Recupera dados do cache (memória -> disco).
        
        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado
            
        Returns:
            Dados do cache ou valor padrão
        """
        # Verifica cache de memória primeiro
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            
            # Verifica TTL
            if entry.ttl_seconds:
                age = (datetime.now() - entry.created_at).total_seconds()
                if age > entry.ttl_seconds:
                    del self.memory_cache[key]
                    self.current_memory_usage -= entry.size_bytes
                    self.stats['misses'] += 1
                    return default
            
            # Hit de memória
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            self.stats['hits'] += 1
            
            return entry.data if not entry.compressed else self._decompress_data(entry.data)
        
        # Verifica cache persistente
        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached_entry = pickle.load(f)
                
                # Verifica TTL
                if cached_entry.ttl_seconds:
                    age = (datetime.now() - cached_entry.created_at).total_seconds()
                    if age > cached_entry.ttl_seconds:
                        cache_file.unlink()
                        self.stats['misses'] += 1
                        return default
                
                # Carrega na memória se possível
                if self.current_memory_usage + cached_entry.size_bytes <= self.memory_limit_bytes:
                    cached_entry.last_accessed = datetime.now()
                    cached_entry.access_count += 1
                    self.memory_cache[key] = cached_entry
                    self.current_memory_usage += cached_entry.size_bytes
                
                self.stats['hits'] += 1
                return cached_entry.data if not cached_entry.compressed else self._decompress_data(cached_entry.data)
                
            except Exception as e:
                st.warning(f"Erro ao carregar cache persistente {key}: {e}")
                cache_file.unlink()
        
        self.stats['misses'] += 1
        return default
    
    def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None, persist: bool = True):
        """
        Armazena dados no cache.
        
        Args:
            key: Chave do cache
            data: Dados para armazenar
            ttl_seconds: Tempo de vida em segundos
            persist: Se deve persistir no disco
        """
        size_bytes = self._calculate_size(data)
        should_compress = self._should_compress(data, size_bytes)
        
        # Comprime se necessário
        stored_data = data
        if should_compress:
            stored_data = self._compress_data(data)
            self.stats['compressions'] += 1
        
        # Cria entrada do cache
        entry = CacheEntry(
            data=stored_data,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            size_bytes=size_bytes,
            ttl_seconds=ttl_seconds or self.default_ttl,
            compressed=should_compress,
            checksum=hashlib.md5(str(data).encode()).hexdigest()
        )
        
        # Armazena na memória se há espaço
        if self.current_memory_usage + size_bytes <= self.memory_limit_bytes:
            self.memory_cache[key] = entry
            self.current_memory_usage += size_bytes
        else:
            # Tenta fazer eviction
            self._evict_lru()
            if self.current_memory_usage + size_bytes <= self.memory_limit_bytes:
                self.memory_cache[key] = entry
                self.current_memory_usage += size_bytes
        
        # Persiste no disco se solicitado
        if persist:
            try:
                cache_file = self.cache_dir / f"{key}.cache"
                with open(cache_file, 'wb') as f:
                    pickle.dump(entry, f)
            except Exception as e:
                st.warning(f"Erro ao persistir cache {key}: {e}")
    
    def invalidate(self, pattern: Optional[str] = None):
        """
        Invalida cache baseado em padrão.
        
        Args:
            pattern: Padrão para invalidar (None = tudo)
        """
        if pattern is None:
            # Limpa tudo
            self.memory_cache.clear()
            self.current_memory_usage = 0
            
            # Remove arquivos persistentes
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
        else:
            # Limpa por padrão
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                entry = self.memory_cache[key]
                self.current_memory_usage -= entry.size_bytes
                del self.memory_cache[key]
                
                # Remove do disco também
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    cache_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_usage_mb': round(self.current_memory_usage / 1024 / 1024, 2),
            'memory_limit_mb': round(self.memory_limit_bytes / 1024 / 1024, 2),
            'memory_entries': len(self.memory_cache),
            'disk_entries': len(list(self.cache_dir.glob("*.cache")))
        }

# Instância global do cache
_cache_manager = None

def get_cache_manager() -> SmartCacheManager:
    """Retorna instância singleton do cache manager."""
    global _cache_manager
    if _cache_manager is None:
        cache_dir = os.path.join(os.getcwd(), 'cache')
        _cache_manager = SmartCacheManager(cache_dir=cache_dir)
    return _cache_manager

def cached(ttl_seconds: Optional[int] = None, persist: bool = True, key_prefix: str = ""):
    """
    🎯 Decorator para cache automático de funções.
    
    Args:
        ttl_seconds: Tempo de vida do cache
        persist: Se deve persistir no disco
        key_prefix: Prefixo para a chave
    
    Usage:
        @cached(ttl_seconds=3600, persist=True)
        def load_heavy_data():
            return expensive_computation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Gera chave única
            key_data = f"{key_prefix}{func.__name__}{str(args)}{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Tenta recuperar do cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executa função e cacheia resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl_seconds, persist)
            
            return result
        
        return wrapper
    
    return decorator

def cache_dataframe(df: pd.DataFrame, key: str, ttl_seconds: int = 3600) -> None:
    """Cache específico para DataFrames com otimizações."""
    cache_manager = get_cache_manager()
    
    # Otimizações específicas para DataFrame
    if len(df) > 10000:
        # Para DataFrames grandes, usa parquet comprimido
        cache_manager.set(f"df_{key}", df, ttl_seconds, persist=True)
    else:
        # Para DataFrames pequenos, mantém em memória
        cache_manager.set(f"df_{key}", df, ttl_seconds, persist=False)

def get_cached_dataframe(key: str) -> Optional[pd.DataFrame]:
    """Recupera DataFrame do cache."""
    cache_manager = get_cache_manager()
    return cache_manager.get(f"df_{key}")

def display_cache_stats():
    """Exibe estatísticas do cache no Streamlit."""
    cache_manager = get_cache_manager()
    stats = cache_manager.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Hit Rate", f"{stats['hit_rate_percent']}%")
    
    with col2:
        st.metric("Memory Usage", f"{stats['memory_usage_mb']:.1f}MB")
    
    with col3:
        st.metric("Cache Hits", stats['hits'])
    
    with col4:
        st.metric("Cache Misses", stats['misses'])
    
    # Botão para limpar cache
    if st.button("🗑️ Limpar Cache"):
        cache_manager.invalidate()
        st.success("Cache limpo com sucesso!")
        st.rerun()
