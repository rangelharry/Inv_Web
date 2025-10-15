#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitários para renderização de dados sem dependência do PyArrow
"""

import streamlit as st
import pandas as pd
from typing import Optional, Any, Dict, List

def safe_dataframe(
    data: pd.DataFrame, 
    use_container_width: bool = True,
    height: Optional[int] = None,
    **kwargs
) -> None:
    """
    Renderizar DataFrame de forma segura sem PyArrow
    
    Args:
        data: DataFrame para renderizar
        use_container_width: Usar largura completa do container
        height: Altura do componente
        **kwargs: Argumentos adicionais
    """
    try:
        # Tentar com st.dataframe primeiro (mais rápido se funcionar)
        if height is not None:
            st.dataframe(
                data, 
                use_container_width=use_container_width,
                height=height
            )
        else:
            st.dataframe(
                data, 
                use_container_width=use_container_width
            )
    except Exception as e:
        # Se falhar, usar método alternativo
        if "pyarrow" in str(e).lower():
            st.warning("⚠️ Usando visualização alternativa (PyArrow não disponível)")
            
            # Mostrar informações básicas
            if not data.empty:
                st.info(f"📊 **{len(data)} registros encontrados** | **{len(data.columns)} colunas**")
                
                # Mostrar as primeiras 10 linhas em formato de tabela HTML
                if len(data) > 10:
                    st.markdown("**Primeiras 10 linhas:**")
                    st.write(data.head(10).to_html(escape=False, index=False), unsafe_allow_html=True)
                    
                    # Opção para mostrar mais
                    if st.button("📋 Mostrar todos os registros"):
                        st.write(data.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.write(data.to_html(escape=False, index=False), unsafe_allow_html=True)
                    
                # Estatísticas básicas para colunas numéricas
                numeric_cols = data.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    with st.expander("📈 Estatísticas Resumidas"):
                        st.dataframe(data[numeric_cols].describe(), use_container_width=True)
            else:
                st.info("📭 Nenhum registro encontrado")
        else:
            # Outro erro - repassar
            raise e

def safe_metric_display(
    data: Dict[str, Any], 
    cols: Optional[List] = None
) -> None:
    """
    Exibir métricas de forma segura
    
    Args:
        data: Dicionário com dados das métricas
        cols: Colunas para layout (opcional)
    """
    if not data:
        st.info("📭 Nenhuma métrica disponível")
        return
    
    if cols:
        # Layout em colunas
        columns = st.columns(len(cols))
        for i, (key, col_title) in enumerate(zip(data.keys(), cols)):
            with columns[i]:
                value = data[key]
                if isinstance(value, (int, float)):
                    st.metric(col_title, f"{value:,}".replace(",", "."))
                else:
                    st.metric(col_title, str(value))
    else:
        # Layout simples
        for key, value in data.items():
            if isinstance(value, (int, float)):
                st.metric(key, f"{value:,}".replace(",", "."))
            else:
                st.metric(key, str(value))

def safe_chart_display(
    data: pd.DataFrame,
    chart_type: str = "bar",
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    title: Optional[str] = None
) -> None:
    """
    Exibir gráficos de forma segura
    
    Args:
        data: DataFrame com dados
        chart_type: Tipo do gráfico (bar, line, area)
        x_col: Coluna para eixo X
        y_col: Coluna para eixo Y
        title: Título do gráfico
    """
    if data.empty:
        st.info("📊 Nenhum dado disponível para o gráfico")
        return
    
    try:
        if title:
            st.subheader(title)
        
        if chart_type == "bar":
            if x_col and y_col:
                chart_data = data.set_index(x_col)[y_col]
            else:
                chart_data = data.iloc[:, 0] if len(data.columns) > 0 else data
            st.bar_chart(chart_data, use_container_width=True)
            
        elif chart_type == "line":
            if x_col and y_col:
                chart_data = data.set_index(x_col)[y_col]
            else:
                chart_data = data.iloc[:, 0] if len(data.columns) > 0 else data
            st.line_chart(chart_data, use_container_width=True)
            
        elif chart_type == "area":
            if x_col and y_col:
                chart_data = data.set_index(x_col)[y_col]
            else:
                chart_data = data.iloc[:, 0] if len(data.columns) > 0 else data
            st.area_chart(chart_data, use_container_width=True)
            
        else:
            st.warning(f"⚠️ Tipo de gráfico '{chart_type}' não suportado")
            
    except Exception as e:
        st.error(f"❌ Erro ao criar gráfico: {e}")
        # Mostrar dados em tabela como fallback
        safe_dataframe(data.head(10), height=300)

def format_currency(value: Any) -> str:
    """
    Formatar valor como moeda brasileira
    
    Args:
        value: Valor a ser formatado
        
    Returns:
        String formatada como moeda
    """
    try:
        if pd.isna(value) or value is None:
            return "R$ 0,00"
        
        float_value = float(value)
        return f"R$ {float_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return f"R$ {str(value)}"

def format_number(value: Any) -> str:
    """
    Formatar número com separadores brasileiros
    
    Args:
        value: Valor a ser formatado
        
    Returns:
        String formatada
    """
    try:
        if pd.isna(value) or value is None:
            return "0"
        
        if isinstance(value, (int, float)):
            return f"{value:,.0f}".replace(",", ".")
        
        return str(value)
    except:
        return str(value)