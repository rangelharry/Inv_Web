#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Lazy Loading
Carregamento otimizado de componentes e dados pesados
"""

import streamlit as st
from typing import Callable, Any, Dict, Optional
import threading
import time
from datetime import datetime
from utils.performance import get_cache_manager

class LazyLoader:
    """Gerenciador de carregamento lazy de componentes"""
    
    def __init__(self):
        """Inicializar lazy loader"""
        self.loading_states = {}
        self.loaded_components = set()
        self._lock = threading.Lock()
    
    def lazy_load_component(
        self,
        component_id: str,
        loader_func: Callable,
        placeholder_text: str = "Carregando...",
        cache_duration: int = 300,
        show_progress: bool = True
    ) -> Any:
        """
        Carregar componente de forma lazy
        
        Args:
            component_id: ID único do componente
            loader_func: Função para carregar o componente
            placeholder_text: Texto do placeholder
            cache_duration: Duração do cache em segundos
            show_progress: Se deve mostrar indicador de progresso
        
        Returns:
            Resultado do carregamento
        """
        cache_manager = get_cache_manager()
        
        # Verificar se já está no cache
        cached_result = cache_manager.get_from_cache(f"lazy_{component_id}", cache_duration)
        if cached_result is not None:
            return cached_result
        
        # Verificar se já está carregado na sessão
        if component_id in self.loaded_components:
            session_key = f"lazy_component_{component_id}"
            if session_key in st.session_state:
                return st.session_state[session_key]
        
        # Placeholder durante carregamento
        placeholder = st.empty()
        
        if show_progress:
            with placeholder.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"""
                    <div style="
                        text-align: center;
                        padding: 1.5rem;
                        background: linear-gradient(135deg, #f1f3f4, #e8eaed);
                        border-radius: 10px;
                        border: 1px dashed #dadce0;
                    ">
                        <div class="loading-spinner"></div>
                        <p style="margin: 1rem 0 0 0; color: #5f6368;">
                            <strong>{placeholder_text}</strong>
                        </p>
                    </div>
                    
                    <style>
                        .loading-spinner {{
                            width: 30px;
                            height: 30px;
                            border: 3px solid #e8eaed;
                            border-top: 3px solid #1a73e8;
                            border-radius: 50%;
                            animation: spin 1s linear infinite;
                            margin: 0 auto;
                        }}
                        
                        @keyframes spin {{
                            0% {{ transform: rotate(0deg); }}
                            100% {{ transform: rotate(360deg); }}
                        }}
                    </style>
                    """, unsafe_allow_html=True)
        
        # Executar carregamento
        try:
            with self._lock:
                self.loading_states[component_id] = {
                    'status': 'loading',
                    'start_time': datetime.now()
                }
            
            # Carregar componente
            result = loader_func()
            
            # Cachear resultado
            cache_manager.set_cache(f"lazy_{component_id}", result, persist_to_disk=True)
            
            # Salvar na sessão
            st.session_state[f"lazy_component_{component_id}"] = result
            self.loaded_components.add(component_id)
            
            with self._lock:
                self.loading_states[component_id] = {
                    'status': 'loaded',
                    'load_time': (datetime.now() - self.loading_states[component_id]['start_time']).total_seconds()
                }
            
            # Substituir placeholder pelo resultado
            placeholder.empty()
            return result
            
        except Exception as e:
            with self._lock:
                self.loading_states[component_id] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            placeholder.error(f"❌ Erro ao carregar: {e}")
            return None
    
    def lazy_load_dataframe(
        self,
        query_func: Callable,
        component_id: str,
        page_size: int = 100,
        show_pagination: bool = True
    ):
        """
        Carregar DataFrame com paginação lazy
        
        Args:
            query_func: Função que retorna os dados
            component_id: ID único do componente
            page_size: Tamanho da página
            show_pagination: Se deve mostrar controles de paginação
        """
        # Obter dados completos do cache ou query
        all_data = self.lazy_load_component(
            f"{component_id}_data",
            query_func,
            "Carregando dados...",
            cache_duration=600  # 10 minutos
        )
        
        if all_data is None or len(all_data) == 0:
            st.info("📊 Nenhum dado encontrado")
            return
        
        # Estado da paginação
        page_key = f"{component_id}_page"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0
        
        total_pages = (len(all_data) - 1) // page_size + 1
        current_page = st.session_state[page_key]
        
        # Calcular índices da página atual
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(all_data))
        
        # Dados da página atual
        page_data = all_data[start_idx:end_idx]
        
        # Exibir dados
        import pandas as pd
        df = pd.DataFrame(page_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Controles de paginação
        if show_pagination and total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ Primeira", disabled=current_page == 0):
                    st.session_state[page_key] = 0
                    st.rerun()
            
            with col2:
                if st.button("◀️ Anterior", disabled=current_page == 0):
                    st.session_state[page_key] = current_page - 1
                    st.rerun()
            
            with col3:
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <strong>Página {current_page + 1} de {total_pages}</strong><br>
                    <small>Mostrando {start_idx + 1}-{end_idx} de {len(all_data)} registros</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if st.button("▶️ Próxima", disabled=current_page >= total_pages - 1):
                    st.session_state[page_key] = current_page + 1
                    st.rerun()
            
            with col5:
                if st.button("⏭️ Última", disabled=current_page >= total_pages - 1):
                    st.session_state[page_key] = total_pages - 1
                    st.rerun()
    
    def lazy_load_chart(
        self,
        chart_func: Callable,
        component_id: str,
        chart_type: str = "plotly"
    ):
        """
        Carregar gráfico de forma lazy
        
        Args:
            chart_func: Função que gera o gráfico
            component_id: ID único do componente
            chart_type: Tipo do gráfico (plotly, matplotlib, etc.)
        """
        def load_chart():
            chart = chart_func()
            
            if chart_type == "plotly":
                st.plotly_chart(chart, use_container_width=True)
            elif chart_type == "matplotlib":
                st.pyplot(chart)
            else:
                st.write(chart)
            
            return chart
        
        return self.lazy_load_component(
            f"{component_id}_chart",
            load_chart,
            "Gerando gráfico...",
            cache_duration=900  # 15 minutos
        )
    
    def preload_critical_components(self, component_ids: list):
        """
        Pré-carregar componentes críticos em background
        
        Args:
            component_ids: Lista de IDs de componentes para pré-carregar
        """
        def preload_worker():
            for component_id in component_ids:
                # Simular pré-carregamento
                time.sleep(0.1)  # Pequeno delay para não sobrecarregar
        
        thread = threading.Thread(target=preload_worker)
        thread.daemon = True
        thread.start()
    
    def get_loading_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas de carregamento
        
        Returns:
            Dict: Estatísticas de carregamento
        """
        loaded_count = len([s for s in self.loading_states.values() if s.get('status') == 'loaded'])
        error_count = len([s for s in self.loading_states.values() if s.get('status') == 'error'])
        
        avg_load_time = 0
        load_times = [s.get('load_time', 0) for s in self.loading_states.values() if s.get('load_time')]
        if load_times:
            avg_load_time = sum(load_times) / len(load_times)
        
        return {
            'total_components': len(self.loading_states),
            'loaded_components': loaded_count,
            'error_components': error_count,
            'average_load_time': round(avg_load_time, 2),
            'components_in_session': len(self.loaded_components)
        }
    
    def clear_loaded_components(self):
        """Limpar componentes carregados da sessão"""
        self.loaded_components.clear()
        
        # Limpar da sessão do Streamlit
        keys_to_remove = [key for key in st.session_state.keys() 
                         if isinstance(key, str) and (key.startswith('lazy_component_') or key.endswith('_page'))]
        
        for key in keys_to_remove:
            del st.session_state[key]

# Instância global do lazy loader
_lazy_loader = None

def get_lazy_loader() -> LazyLoader:
    """
    Obter instância global do lazy loader
    
    Returns:
        LazyLoader: Instância do lazy loader
    """
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = LazyLoader()
    return _lazy_loader

# Funções de conveniência
def lazy_component(component_id: str, loader_func: Callable, **kwargs):
    """Função de conveniência para carregamento lazy"""
    lazy_loader = get_lazy_loader()
    return lazy_loader.lazy_load_component(component_id, loader_func, **kwargs)

def lazy_dataframe(query_func: Callable, component_id: str, **kwargs):
    """Função de conveniência para DataFrame lazy"""
    lazy_loader = get_lazy_loader()
    return lazy_loader.lazy_load_dataframe(query_func, component_id, **kwargs)

def lazy_chart(chart_func: Callable, component_id: str, **kwargs):
    """Função de conveniência para gráfico lazy"""
    lazy_loader = get_lazy_loader()
    return lazy_loader.lazy_load_chart(chart_func, component_id, **kwargs)

def show_lazy_loading_stats():
    """Exibir estatísticas de lazy loading"""
    lazy_loader = get_lazy_loader()
    stats = lazy_loader.get_loading_stats()
    
    st.subheader("📊 Estatísticas de Lazy Loading")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Componentes", stats['total_components'])
    
    with col2:
        st.metric("Componentes Carregados", stats['loaded_components'])
    
    with col3:
        st.metric("Erros de Carregamento", stats['error_components'])
    
    with col4:
        st.metric("Tempo Médio de Carga", f"{stats['average_load_time']}s")
    
    # Ações
    if st.button("🧹 Limpar Componentes Carregados"):
        lazy_loader.clear_loaded_components()
        st.success("Componentes limpos!")
        st.rerun()