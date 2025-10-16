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
        # Usar st.table como alternativa mais simples e compatível
        if data.empty:
            st.info("📭 Nenhum registro encontrado")
            return
            
        # Mostrar informações básicas
        st.info(f"📊 **{len(data)} registros** | **{len(data.columns)} colunas**")
        
        # Para datasets grandes, mostrar amostra
        if len(data) > 20:
            st.table(data.head(20))
            if st.button("📋 Mostrar todos os registros"):
                st.table(data)
        else:
            st.table(data)
            
    except Exception as e:
        # Fallback final: mostrar dados como texto
        st.warning(f"⚠️ Usando visualização básica: {e}")
        
        if not data.empty:
            st.text(f"Registros: {len(data)} | Colunas: {', '.join(data.columns)}")
            
            # Mostrar primeiras 5 linhas como texto
            for i, (idx, row) in enumerate(data.head(5).iterrows()):
                with st.expander(f"Registro {i + 1}"):
                    for col, val in row.items():
                        st.text(f"{col}: {val}")
        else:
            st.info("📭 Nenhum registro encontrado")

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
            # Simplificar: mostrar dados como tabela
            st.info(f"📊 Dados do gráfico de barras")
            safe_dataframe(data)
            
        elif chart_type == "line":
            st.info(f"📈 Dados do gráfico de linha")
            safe_dataframe(data)
            
        elif chart_type == "area":
            st.info(f"📊 Dados do gráfico de área")
            safe_dataframe(data)
            
        else:
            st.warning(f"⚠️ Tipo de gráfico '{chart_type}' não suportado")
            safe_dataframe(data)
            
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {e}")
        # Mostrar apenas informações básicas
        st.text(f"Dados: {len(data)} registros, {len(data.columns) if hasattr(data, 'columns') else 0} colunas")

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