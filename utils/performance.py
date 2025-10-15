#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cache Inteligente
Otimização de performance para consultas e dados frequentes
"""

import streamlit as st
import time
import hashlib
import pickle
import os
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import threading

class CacheManager:
    """Gerenciador de cache inteligente da aplicação"""
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Inicializar gerenciador de cache
        
        Args:
            cache_dir: Diretório para arquivos de cache
        """
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'cache_size': 0
        }
        self._lock = threading.Lock()
        
        # Criar diretório de cache se não existir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Inicializar estado da sessão
        self._initialize_session_cache()
    
    def _initialize_session_cache(self):
        """Inicializar cache da sessão Streamlit"""
        if 'cache_data' not in st.session_state:
            st.session_state.cache_data = {}
        
        if 'cache_timestamps' not in st.session_state:
            st.session_state.cache_timestamps = {}
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """
        Gerar chave única para cache
        
        Args:
            func_name: Nome da função
            args: Argumentos posicionais
            kwargs: Argumentos nomeados
        
        Returns:
            str: Chave de cache
        """
        # Criar string única baseada na função e parâmetros
        key_data = f"{func_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_from_cache(self, key: str, max_age: int = 300) -> Optional[Any]:
        """
        Obter valor do cache
        
        Args:
            key: Chave do cache
            max_age: Idade máxima em segundos
        
        Returns:
            Valor do cache ou None se não encontrado/expirado
        """
        with self._lock:
            self.cache_stats['total_requests'] += 1
            
            # Verificar cache da sessão primeiro (mais rápido)
            if key in st.session_state.cache_data:
                timestamp = st.session_state.cache_timestamps.get(key, datetime.min)
                
                if datetime.now() - timestamp < timedelta(seconds=max_age):
                    self.cache_stats['hits'] += 1
                    return st.session_state.cache_data[key]
                else:
                    # Expirado - remover
                    del st.session_state.cache_data[key]
                    del st.session_state.cache_timestamps[key]
            
            # Verificar cache em memória
            if key in self.memory_cache:
                cache_entry = self.memory_cache[key]
                if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=max_age):
                    self.cache_stats['hits'] += 1
                    # Copiar para cache da sessão para acesso mais rápido
                    st.session_state.cache_data[key] = cache_entry['data']
                    st.session_state.cache_timestamps[key] = cache_entry['timestamp']
                    return cache_entry['data']
                else:
                    # Expirado - remover
                    del self.memory_cache[key]
            
            # Verificar cache em disco
            cache_file = os.path.join(self.cache_dir, f"{key}.cache")
            if os.path.exists(cache_file):
                try:
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
                    
                    if file_age < timedelta(seconds=max_age):
                        with open(cache_file, 'rb') as f:
                            data = pickle.load(f)
                        
                        # Carregar para caches em memória
                        timestamp = datetime.fromtimestamp(os.path.getmtime(cache_file))
                        self.memory_cache[key] = {'data': data, 'timestamp': timestamp}
                        st.session_state.cache_data[key] = data
                        st.session_state.cache_timestamps[key] = timestamp
                        
                        self.cache_stats['hits'] += 1
                        return data
                    else:
                        # Arquivo expirado - remover
                        os.remove(cache_file)
                
                except (pickle.PickleError, IOError):
                    # Erro ao ler cache - remover arquivo corrompido
                    try:
                        os.remove(cache_file)
                    except:
                        pass
            
            self.cache_stats['misses'] += 1
            return None
    
    def set_cache(self, key: str, data: Any, persist_to_disk: bool = False):
        """
        Definir valor no cache
        
        Args:
            key: Chave do cache
            data: Dados para cachear
            persist_to_disk: Se deve persistir no disco
        """
        with self._lock:
            timestamp = datetime.now()
            
            # Cache da sessão (mais rápido)
            st.session_state.cache_data[key] = data
            st.session_state.cache_timestamps[key] = timestamp
            
            # Cache em memória
            self.memory_cache[key] = {'data': data, 'timestamp': timestamp}
            
            # Cache em disco se solicitado
            if persist_to_disk:
                cache_file = os.path.join(self.cache_dir, f"{key}.cache")
                try:
                    with open(cache_file, 'wb') as f:
                        pickle.dump(data, f)
                except (pickle.PickleError, IOError):
                    pass  # Falha silenciosa para cache em disco
            
            self.cache_stats['cache_size'] = len(self.memory_cache)
    
    def clear_cache(self, pattern: Optional[str] = None):
        """
        Limpar cache
        
        Args:
            pattern: Padrão para limpeza seletiva (opcional)
        """
        with self._lock:
            if pattern:
                # Limpeza seletiva
                keys_to_remove = [key for key in self.memory_cache.keys() if pattern in key]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                
                keys_to_remove = [key for key in st.session_state.cache_data.keys() if pattern in key]
                for key in keys_to_remove:
                    del st.session_state.cache_data[key]
                    if key in st.session_state.cache_timestamps:
                        del st.session_state.cache_timestamps[key]
                
                # Limpar arquivos de cache
                for filename in os.listdir(self.cache_dir):
                    if pattern in filename and filename.endswith('.cache'):
                        try:
                            os.remove(os.path.join(self.cache_dir, filename))
                        except:
                            pass
            else:
                # Limpeza completa
                self.memory_cache.clear()
                st.session_state.cache_data.clear()
                st.session_state.cache_timestamps.clear()
                
                # Limpar arquivos de cache
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        try:
                            os.remove(os.path.join(self.cache_dir, filename))
                        except:
                            pass
            
            self.cache_stats['cache_size'] = len(self.memory_cache)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas do cache
        
        Returns:
            Dict: Estatísticas do cache
        """
        hit_rate = 0
        if self.cache_stats['total_requests'] > 0:
            hit_rate = (self.cache_stats['hits'] / self.cache_stats['total_requests']) * 100
        
        return {
            **self.cache_stats,
            'hit_rate_percent': round(hit_rate, 2),
            'session_cache_size': len(st.session_state.cache_data),
            'disk_cache_files': len([f for f in os.listdir(self.cache_dir) if f.endswith('.cache')])
        }
    
    def cache_function(self, max_age: int = 300, persist: bool = False):
        """
        Decorator para cachear resultado de funções
        
        Args:
            max_age: Idade máxima do cache em segundos
            persist: Se deve persistir no disco
        
        Returns:
            Decorator function
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Gerar chave de cache
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Tentar obter do cache
                cached_result = self.get_from_cache(cache_key, max_age)
                if cached_result is not None:
                    return cached_result
                
                # Executar função e cachear resultado
                result = func(*args, **kwargs)
                self.set_cache(cache_key, result, persist)
                
                return result
            
            return wrapper
        return decorator
    
    def preload_common_data(self):
        """Pré-carregar dados comumente acessados"""
        try:
            from database.connection import get_database
            
            # Pré-carregar estatísticas básicas
            db = get_database()
            
            # Contagem de itens por tipo
            @self.cache_function(max_age=600, persist=True)  # 10 minutos
            def get_item_counts():
                equipamentos = db.execute_query("SELECT COUNT(*) as count FROM equipamentos_eletricos")
                manuais = db.execute_query("SELECT COUNT(*) as count FROM equipamentos_manuais")
                insumos = db.execute_query("SELECT COUNT(*) as count FROM insumos")
                
                return {
                    'equipamentos_eletricos': equipamentos[0]['count'] if equipamentos else 0,
                    'equipamentos_manuais': manuais[0]['count'] if manuais else 0,
                    'insumos': insumos[0]['count'] if insumos else 0
                }
            
            # Obras/departamentos
            @self.cache_function(max_age=1800, persist=True)  # 30 minutos
            def get_obras_list():
                obras = db.execute_query("SELECT id, nome FROM obras ORDER BY nome")
                return obras or []
            
            # Executar pré-carregamento
            get_item_counts()
            get_obras_list()
            
        except Exception:
            pass  # Falha silenciosa no pré-carregamento

# Instância global do gerenciador de cache
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """
    Obter instância global do gerenciador de cache
    
    Returns:
        CacheManager: Instância do gerenciador
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

# Decorator de conveniência
def cache_data(max_age: int = 300, persist: bool = False):
    """
    Decorator de conveniência para cachear dados
    
    Args:
        max_age: Idade máxima em segundos
        persist: Se deve persistir no disco
    """
    cache_manager = get_cache_manager()
    return cache_manager.cache_function(max_age, persist)

# Função para mostrar widget de estatísticas de cache
def show_cache_stats():
    """Exibir widget de estatísticas de cache"""
    cache_manager = get_cache_manager()
    stats = cache_manager.get_cache_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Taxa de Acerto", 
            f"{stats['hit_rate_percent']:.1f}%",
            delta=f"{stats['hits']} hits"
        )
    
    with col2:
        st.metric(
            "Total de Requests", 
            stats['total_requests'],
            delta=f"{stats['misses']} misses"
        )
    
    with col3:
        st.metric(
            "Cache em Memória", 
            stats['cache_size'],
            delta=f"{stats['session_cache_size']} sessão"
        )
    
    with col4:
        st.metric(
            "Cache em Disco", 
            stats['disk_cache_files'],
            help="Arquivos de cache persistentes"
        )
    
    # Ações de cache
    col_clear1, col_clear2 = st.columns(2)
    
    with col_clear1:
        if st.button("🧹 Limpar Cache", help="Limpar todo o cache"):
            cache_manager.clear_cache()
            st.success("Cache limpo com sucesso!")
            st.rerun()
    
    with col_clear2:
        if st.button("🔄 Pré-carregar Dados", help="Pré-carregar dados comuns"):
            with st.spinner("Pré-carregando dados..."):
                cache_manager.preload_common_data()
            st.success("Dados pré-carregados!")

# Função para otimização de queries
def optimize_query_performance():
    """Aplicar otimizações de performance em queries"""
    try:
        from database.connection import get_database
        
        db = get_database()
        
        # Índices para melhorar performance (baseado no schema real)
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_equipamentos_eletricos_status ON equipamentos_eletricos(status)",
            "CREATE INDEX IF NOT EXISTS idx_equipamentos_eletricos_codigo ON equipamentos_eletricos(codigo)",
            "CREATE INDEX IF NOT EXISTS idx_equipamentos_manuais_status ON equipamentos_manuais(status)",
            "CREATE INDEX IF NOT EXISTS idx_equipamentos_manuais_codigo ON equipamentos_manuais(codigo)",
            "CREATE INDEX IF NOT EXISTS idx_insumos_codigo ON insumos(codigo)",
            "CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes(data)",
            "CREATE INDEX IF NOT EXISTS idx_movimentacoes_codigo ON movimentacoes(codigo)",
            "CREATE INDEX IF NOT EXISTS idx_auditoria_timestamp ON auditoria(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario)"
        ]
        
        for index_sql in indexes:
            try:
                db.execute_update(index_sql)
            except:
                pass  # Índice pode já existir
        
        return True
    
    except Exception:
        return False