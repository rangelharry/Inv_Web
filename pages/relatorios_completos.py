#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Relatórios
Página de geração de relatórios completos
"""

import streamlit as st
from utils.global_css import apply_global_css, force_light_theme
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import DatabaseConnection
from utils.auth import get_auth, check_authentication

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def get_inventario_completo():
    """Gerar relatório de inventário completo"""
    db = DatabaseConnection()
    
    try:
        # Equipamentos elétricos
        query_eletricos = """
            SELECT 'Elétrico' as tipo, 
                   COALESCE(codigo, '') as codigo, 
                   COALESCE(nome, '') as descricao, 
                   COALESCE(categoria, '') as categoria, 
                   COALESCE(status, 'indefinido') as status, 
                   COALESCE(localizacao, 'N/A') as localizacao
            FROM equipamentos_eletricos
        """
        
        # Equipamentos manuais  
        query_manuais = """
            SELECT 'Manual' as tipo, 
                   COALESCE(codigo, '') as codigo, 
                   COALESCE(descricao, '') as descricao, 
                   COALESCE(tipo, '') as categoria, 
                   COALESCE(status, 'indefinido') as status, 
                   COALESCE(localizacao, 'N/A') as localizacao
            FROM equipamentos_manuais
        """
        
        # Insumos
        query_insumos = """
            SELECT 'Insumo' as tipo, 
                   COALESCE(codigo, '') as codigo, 
                   COALESCE(descricao, '') as descricao, 
                   COALESCE(categoria, '') as categoria, 
                   CASE 
                       WHEN quantidade <= quantidade_minima THEN 'Estoque Baixo' 
                       ELSE 'OK' 
                   END as status,
                   COALESCE(localizacao, 'N/A') as localizacao
            FROM insumos
        """
        
        eletricos = db.execute_query(query_eletricos)
        manuais = db.execute_query(query_manuais)
        insumos = db.execute_query(query_insumos)
        
        # Combinar todos os dados
        all_data = []
        if eletricos:
            all_data.extend(eletricos)
        if manuais:
            all_data.extend(manuais)
        if insumos:
            all_data.extend(insumos)
        
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
        
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return pd.DataFrame()

def get_movimentacoes_periodo(data_inicio, data_fim):
    """Relatório de movimentações por período"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT codigo, origem, destino, data, responsavel, status, quantidade
            FROM movimentacoes
            WHERE date(data) BETWEEN ? AND ?
            ORDER BY data DESC
        """
        
        result = db.execute_query(query, (data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d')))
        return pd.DataFrame(result) if result else pd.DataFrame()
        
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return pd.DataFrame()

def get_status_equipamentos():
    """Relatório de status dos equipamentos"""
    db = DatabaseConnection()
    
    try:
        # Status equipamentos elétricos
        query_eletricos = """
            SELECT status, COUNT(*) as quantidade, 'Elétrico' as tipo
            FROM equipamentos_eletricos
            GROUP BY status
        """
        
        # Status equipamentos manuais
        query_manuais = """
            SELECT status, COUNT(*) as quantidade, 'Manual' as tipo
            FROM equipamentos_manuais
            GROUP BY status
        """
        
        eletricos = db.execute_query(query_eletricos)
        manuais = db.execute_query(query_manuais)
        
        all_data = []
        if eletricos:
            all_data.extend(eletricos)
        if manuais:
            all_data.extend(manuais)
        
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
        
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return pd.DataFrame()

def get_valor_inventario():
    """Calcular valor do inventário"""
    db = DatabaseConnection()
    
    try:
        # Valor dos equipamentos manuais
        query_manuais = """
            SELECT 
                COALESCE(SUM(CAST(COALESCE(valor, 0) as REAL)), 0) as valor_total, 
                COUNT(*) as quantidade
            FROM equipamentos_manuais
        """
        
        # Valor dos insumos
        query_insumos = """
            SELECT 
                COALESCE(SUM(COALESCE(quantidade, 0) * COALESCE(preco_unitario, 0)), 0) as valor_total, 
                COUNT(*) as quantidade
            FROM insumos
        """
        
        manuais = db.execute_query(query_manuais)
        insumos = db.execute_query(query_insumos)
        
        valor_manuais = manuais[0]['valor_total'] if manuais and manuais[0]['valor_total'] else 0
        valor_insumos = insumos[0]['valor_total'] if insumos and insumos[0]['valor_total'] else 0
        
        return {
            'valor_manuais': valor_manuais,
            'valor_insumos': valor_insumos,
            'valor_total': valor_manuais + valor_insumos
        }
        
    except Exception as e:
        st.error(f"Erro ao calcular valor: {e}")
        return {'valor_manuais': 0, 'valor_insumos': 0, 'valor_total': 0}

def show():
    """Função principal da página Relatórios"""
    
    # FORÃ‡AR TEMA CLARO - MODO EXTREMO
    apply_global_css()
    force_light_theme()
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown("## 📈 Relatórios Completos")
    st.markdown("Relatórios gerenciais e operacionais detalhados")
    
    # Seletor de tipo de relatório
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Inventário Completo", 
        "📊 Status Equipamentos", 
        "🔄 Movimentações", 
        "💰 Valor do Inventário",
        "📈 Dashboard"
    ])
    
    with tab1:
        st.markdown("### 📋 Inventário Completo")
        
        if st.button("🔄 Gerar Relatório de Inventário", type="primary"):
            with st.spinner("Gerando relatório..."):
                df = get_inventario_completo()
                
                if not df.empty:
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total de Itens", len(df))
                    
                    with col2:
                        eletricos = len(df[df['tipo'] == 'Elétrico'])
                        st.metric("Elétricos", eletricos)
                    
                    with col3:
                        manuais = len(df[df['tipo'] == 'Manual'])
                        st.metric("Manuais", manuais)
                    
                    with col4:
                        insumos = len(df[df['tipo'] == 'Insumo'])
                        st.metric("Insumos", insumos)
                    
                    st.markdown("---")
                    
                    # Filtros
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        tipo_filter = st.selectbox("Filtrar por tipo:", ["Todos"] + list(df['tipo'].unique()))
                    
                    with col2:
                        status_filter = st.selectbox("Filtrar por status:", ["Todos"] + list(df['status'].unique()))
                    
                    # Aplicar filtros
                    df_filtered = df.copy()
                    if tipo_filter != "Todos":
                        df_filtered = df_filtered[df_filtered['tipo'] == tipo_filter]
                    if status_filter != "Todos":
                        df_filtered = df_filtered[df_filtered['status'] == status_filter]
                    
                    st.markdown(f"### 📊 Resultados ({len(df_filtered)} itens)")
                    
                    # Exibir dados
                    for _, row in df_filtered.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns([3, 2, 2])
                            
                            with col1:
                                tipo_emoji = {"Elétrico": "⚡", "Manual": "🔧", "Insumo": "📦"}.get(row['tipo'], "📋")
                                st.markdown(f"{tipo_emoji} **{row['codigo']}** - {row['descricao']}")
                                st.caption(f"📍 {row['localizacao']}")
                            
                            with col2:
                                st.markdown(f"**{row['categoria']}**")
                                st.caption(f"Tipo: {row['tipo']}")
                            
                            with col3:
                                status_emoji = {"Disponível": "🟢", "Em Uso": "🟡", "Manutenção": "🔴", "OK": "✅", "Estoque Baixo": "⚠️"}.get(row['status'], "⚪")
                                st.markdown(f"{status_emoji} **{row['status']}**")
                            
                            st.markdown("---")
                else:
                    st.warning("Nenhum item encontrado no inventário")
    
    with tab2:
        st.markdown("### 📊 Status dos Equipamentos")
        
        if st.button("🔄 Gerar Relatório de Status", type="primary"):
            with st.spinner("Analisando status..."):
                df = get_status_equipamentos()
                
                if not df.empty:
                    # Gráfico de status por tipo
                    for tipo in df['tipo'].unique():
                        st.markdown(f"#### {tipo}s")
                        df_tipo = df[df['tipo'] == tipo]
                        
                        for _, row in df_tipo.iterrows():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                status_emoji = {"Disponível": "🟢", "Em Uso": "🟡", "Manutenção": "🔴", "Inativo": "⚫"}.get(row['status'], "⚪")
                                st.markdown(f"{status_emoji} **{row['status']}**")
                            with col2:
                                st.metric("", row['quantidade'])
                        
                        st.markdown("---")
                else:
                    st.warning("Nenhum dado de status encontrado")
    
    with tab3:
        st.markdown("### 🔄 Movimentações por Período")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_inicio = st.date_input("Data início:", datetime.now() - timedelta(days=30))
        
        with col2:
            data_fim = st.date_input("Data fim:", datetime.now())
        
        if st.button("🔄 Gerar Relatório de Movimentações", type="primary"):
            with st.spinner("Buscando movimentações..."):
                df = get_movimentacoes_periodo(data_inicio, data_fim)
                
                if not df.empty:
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total", len(df))
                    
                    with col2:
                        aprovadas = len(df[df['status'] == 'aprovada'])
                        st.metric("Aprovadas", aprovadas)
                    
                    with col3:
                        pendentes = len(df[df['status'] == 'pendente'])
                        st.metric("Pendentes", pendentes)
                    
                    with col4:
                        canceladas = len(df[df['status'] == 'cancelada'])
                        st.metric("Canceladas", canceladas)
                    
                    st.markdown("---")
                    
                    # Lista de movimentações
                    for _, row in df.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns([3, 2, 2])
                            
                            with col1:
                                st.markdown(f"**{row['codigo']}**")
                                st.caption(f"📦 Qtd: {row['quantidade']}")
                            
                            with col2:
                                st.markdown(f"📍 **{row['origem']}** → **{row['destino']}**")
                                st.caption(f"👤 {row['responsavel']}")
                            
                            with col3:
                                status_emoji = {"aprovada": "✅", "pendente": "⏳", "cancelada": "❌"}.get(row['status'], "⚪")
                                st.markdown(f"{status_emoji} **{row['status'].title()}**")
                                st.caption(f"📅 {row['data']}")
                            
                            st.markdown("---")
                else:
                    st.info("Nenhuma movimentação encontrada no período selecionado")
    
    with tab4:
        st.markdown("### 💰 Valor do Inventário")
        
        if st.button("🔄 Calcular Valor do Inventário", type="primary"):
            with st.spinner("Calculando valores..."):
                valores = get_valor_inventario()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Equipamentos Manuais", f"R$ {valores['valor_manuais']:,.2f}")
                
                with col2:
                    st.metric("Insumos", f"R$ {valores['valor_insumos']:,.2f}")
                
                with col3:
                    st.metric("**TOTAL**", f"R$ {valores['valor_total']:,.2f}")
    
    with tab5:
        st.markdown("### 📈 Dashboard Geral")
        
        # Dashboard com resumo geral
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Resumo do Inventário")
            df_inventario = get_inventario_completo()
            
            if not df_inventario.empty:
                tipos = df_inventario['tipo'].value_counts()
                for tipo, count in tipos.items():
                    tipo_emoji = {"Elétrico": "⚡", "Manual": "🔧", "Insumo": "📦"}.get(str(tipo), "📋")
                    st.markdown(f"{tipo_emoji} **{tipo}:** {count} itens")
        
        with col2:
            st.markdown("#### 💰 Resumo Financeiro")
            valores = get_valor_inventario()
            st.markdown(f"💰 **Valor Total:** R$ {valores['valor_total']:,.2f}")
            st.markdown(f"🔧 **Equipamentos:** R$ {valores['valor_manuais']:,.2f}")
            st.markdown(f"📦 **Insumos:** R$ {valores['valor_insumos']:,.2f}")

if __name__ == "__main__":
    show()