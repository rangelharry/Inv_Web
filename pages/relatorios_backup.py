#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Relatórios Avançados
Página de relatórios detalhados com gráficos, filtros e exportação
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import base64
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth, check_authentication
from database.connection import DatabaseConnection
from utils.logging import SystemLogger

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

logger = SystemLogger()

def get_inventario_data():
    """Obter dados do inventário para relatórios"""
    db = get_database()
    
    # Equipamentos elétricos
    equipamentos_eletricos = db.execute_query("""
        SELECT 'Elétrico' as tipo, codigo, nome, categoria, status, localizacao
        FROM equipamentos_eletricos
    """)
    
    # Equipamentos manuais
    equipamentos_manuais = db.execute_query("""
        SELECT 'Manual' as tipo, codigo, nome, categoria, status, localizacao
        FROM equipamentos_manuais
    """)
    
    # Insumos
    insumos = db.execute_query("""
        SELECT 'Insumo' as tipo, codigo, nome, categoria, CAST(estoque_atual as TEXT) as status, localizacao
        FROM insumos
    """)
    
    # Combinar todos os dados
    all_data = equipamentos_eletricos + equipamentos_manuais + insumos
    
    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

def create_excel_download(df, filename):
    """Criar link de download para Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatório')
        
        # Formatação básica
        workbook = writer.book
        worksheet = writer.sheets['Relatório']
        
        # Formato do cabeçalho
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Aplicar formato ao cabeçalho
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)
    
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Baixar Excel</a>'

def show_inventario_completo():
    """Mostrar relatório de inventário completo"""
    st.subheader("📄 Relatório de Inventário Completo")
    
    with st.spinner("Carregando dados..."):
        df = get_inventario_data()
    
    if df.empty:
        st.warning("Nenhum dado encontrado para o relatório.")
        return
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Itens", len(df))
    
    with col2:
        equipamentos = len(df[df['tipo'].isin(['Elétrico', 'Manual'])])
        st.metric("Equipamentos", equipamentos)
    
    with col3:
        insumos = len(df[df['tipo'] == 'Insumo'])
        st.metric("Insumos", insumos)
    
    with col4:
        categorias = df['categoria'].nunique()
        st.metric("Categorias", categorias)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico por tipo
        tipo_counts = df['tipo'].value_counts()
        fig_tipo = px.pie(values=tipo_counts.values, names=tipo_counts.index, 
                         title="Distribuição por Tipo")
        st.plotly_chart(fig_tipo, use_container_width=True)
    
    with col2:
        # Gráfico por categoria
        cat_counts = df['categoria'].value_counts().head(10)
        fig_cat = px.bar(x=cat_counts.values, y=cat_counts.index, 
                        orientation='h', title="Top 10 Categorias")
        st.plotly_chart(fig_cat, use_container_width=True)
    
    # Tabela de dados
    st.markdown("### 📋 Detalhes do Inventário")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tipo_filter = st.selectbox("Filtrar por Tipo", 
                                  ["Todos"] + list(df['tipo'].unique()))
    
    with col2:
        categoria_filter = st.selectbox("Filtrar por Categoria", 
                                       ["Todas"] + list(df['categoria'].unique()))
    
    with col3:
        status_filter = st.selectbox("Filtrar por Status", 
                                    ["Todos"] + list(df['status'].unique()))
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if tipo_filter != "Todos":
        filtered_df = filtered_df[filtered_df['tipo'] == tipo_filter]
    
    if categoria_filter != "Todas":
        filtered_df = filtered_df[filtered_df['categoria'] == categoria_filter]
    
    if status_filter != "Todos":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    # Mostrar tabela
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download
    if not filtered_df.empty:
        st.markdown("### 📥 Download")
        filename = f"inventario_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        excel_link = create_excel_download(filtered_df, filename)
        st.markdown(excel_link, unsafe_allow_html=True)

def show_movimentacoes_relatorio():
    """Mostrar relatório de movimentações"""
    st.subheader("📋 Relatório de Movimentações")
    
    db = get_database()
    
    # Período de consulta
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input("Data Início", 
                                   value=datetime.now() - timedelta(days=30))
    
    with col2:
        data_fim = st.date_input("Data Fim", 
                                value=datetime.now())
    
    # Buscar movimentações
    movimentacoes = db.execute_query("""
        SELECT codigo, origem, destino, data, responsavel, status, quantidade
        FROM movimentacoes
        WHERE date(data) BETWEEN ? AND ?
        ORDER BY data DESC
    """, (data_inicio.isoformat(), data_fim.isoformat()))
    
    if not movimentacoes:
        st.warning("Nenhuma movimentação encontrada no período selecionado.")
        return
    
    df_mov = pd.DataFrame(movimentacoes)
    df_mov['data'] = pd.to_datetime(df_mov['data'])
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Movimentações", len(df_mov))
    
    with col2:
        concluidas = len(df_mov[df_mov['status'] == 'concluida'])
        st.metric("Concluídas", concluidas)
    
    with col3:
        pendentes = len(df_mov[df_mov['status'] == 'pendente'])
        st.metric("Pendentes", pendentes)
    
    with col4:
        responsaveis = df_mov['responsavel'].nunique()
        st.metric("Responsáveis", responsaveis)
    
    # Gráfico de movimentações por dia
    df_daily = df_mov.groupby(df_mov['data'].dt.date).size().reset_index()
    df_daily.columns = ['data', 'movimentacoes']
    
    fig_daily = px.line(df_daily, x='data', y='movimentacoes', 
                       title="Movimentações por Dia")
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Tabela de movimentações
    st.markdown("### 📋 Detalhes das Movimentações")
    st.dataframe(df_mov, use_container_width=True)
    
    # Download
    filename = f"movimentacoes_{data_inicio}_{data_fim}.xlsx"
    excel_link = create_excel_download(df_mov, filename)
    st.markdown(excel_link, unsafe_allow_html=True)

def show():
    """Função principal da página Relatórios"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 📈 Relatórios")
    st.markdown("Relatórios gerenciais e operacionais")
    
    # Verificar permissões (relatórios precisam de pelo menos papel de visualizador)
    if not auth.require_role('visualizador'):
        return
    
    # Seções de relatórios
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Inventário", "📋 Movimentações", "💰 Financeiro", "🛠️ Sistema"])
    
    with tab1:
        st.markdown("### 📊 Relatórios de Inventário")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Inventário Completo", use_container_width=True, type="primary"):
                st.session_state.show_inventario_completo = True
                st.rerun()
            
            if st.button("⚡ Equipamentos Elétricos", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
            
            if st.button("🔧 Equipamentos Manuais", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
        
        with col2:
            if st.button("📦 Estoque de Insumos", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
            
            if st.button("⚠️ Alertas de Estoque", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
            
            if st.button("📊 Status dos Equipamentos", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
        
        # Mostrar relatório se solicitado
        if st.session_state.get('show_inventario_completo', False):
            st.markdown("---")
            show_inventario_completo()
            if st.button("🔙 Voltar aos Relatórios"):
                st.session_state.show_inventario_completo = False
                st.rerun()
    
    with tab2:
        st.markdown("### 📋 Relatórios de Movimentação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Movimentações por Período", use_container_width=True, type="primary"):
                st.session_state.show_movimentacoes = True
                st.rerun()
            
            if st.button("🏗️ Movimentações por Obra", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
        
        with col2:
            if st.button("👤 Movimentações por Responsável", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
            
            if st.button("📍 Movimentações por Local", use_container_width=True):
                st.info("📝 Relatório específico em desenvolvimento...")
        
        # Mostrar relatório se solicitado
        if st.session_state.get('show_movimentacoes', False):
            st.markdown("---")
            show_movimentacoes_relatorio()
            if st.button("🔙 Voltar aos Relatórios", key="back_mov"):
                st.session_state.show_movimentacoes = False
                st.rerun()
    
    with tab3:
        st.markdown("### 💰 Relatórios Financeiros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💰 Valor do Inventário", use_container_width=True):
                st.info("📝 Relatório financeiro em desenvolvimento...")
            
            if st.button("📈 Custos por Obra", use_container_width=True):
                st.info("📝 Relatório financeiro em desenvolvimento...")
        
        with col2:
            if st.button("💸 Depreciação", use_container_width=True):
                st.info("📝 Relatório financeiro em desenvolvimento...")
            
            if st.button("📊 ROI por Equipamento", use_container_width=True):
                st.info("📝 Relatório financeiro em desenvolvimento...")
    
    with tab4:
        st.markdown("### 🛠️ Relatórios do Sistema")
        
        # Apenas admins podem ver relatórios do sistema
        if auth.has_permission('admin'):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("👥 Usuários e Acessos", use_container_width=True):
                    db = get_database()
                    usuarios = db.execute_query("""
                        SELECT usuario, nome, role, ativo, ultimo_acesso
                        FROM usuarios
                        ORDER BY ultimo_acesso DESC
                    """)
                    
                    if usuarios:
                        df_users = pd.DataFrame(usuarios)
                        st.dataframe(df_users, use_container_width=True)
                
                if st.button("📋 Log de Auditoria", use_container_width=True):
                    db = get_database()
                    auditoria = db.execute_query("""
                        SELECT usuario, acao, detalhes, timestamp
                        FROM auditoria
                        ORDER BY timestamp DESC
                        LIMIT 100
                    """)
                    
                    if auditoria:
                        df_audit = pd.DataFrame(auditoria)
                        st.dataframe(df_audit, use_container_width=True)
            
            with col2:
                if st.button("🗄️ Status do Banco", use_container_width=True):
                    from database.connection import test_database
                    stats = test_database()
                    
                    for table, count in stats.items():
                        st.metric(f"Tabela {table}", count)
                
                if st.button("� Estatísticas de Backup", use_container_width=True):
                    from utils.backup import get_backup_manager
                    backup_mgr = get_backup_manager()
                    stats = backup_mgr.get_backup_stats()
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Total Backups", stats['total_backups'])
                        if stats['last_backup']:
                            st.metric("Último Backup", stats['last_backup'].strftime('%d/%m/%Y'))
                    
                    with col_b:
                        if stats['total_size'] > 0:
                            size_mb = stats['total_size'] / (1024 * 1024)
                            st.metric("Tamanho Total", f"{size_mb:.1f} MB")
        else:
            st.warning("⛔ Acesso restrito a administradores")
    
    # Informações sobre funcionalidades
    st.markdown("---")
    st.success("""
    ✅ **Funcionalidades implementadas:**
    - ✅ Relatório de Inventário Completo com gráficos
    - ✅ Relatório de Movimentações por período
    - ✅ Exportação para Excel
    - ✅ Gráficos interativos (Plotly)
    - ✅ Filtros avançados
    - ✅ Relatórios do sistema (admin)
    - ✅ Controle de permissões
    """)

if __name__ == "__main__":
    from pages import relatorios
    relatorios.show()