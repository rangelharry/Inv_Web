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
from datetime import datetime, timedelta
import io
import base64
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

# Importação segura do plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth, check_authentication
from database.connection import DatabaseConnection
from utils.logging import SystemLogger

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

logger = SystemLogger()

def get_database():
    """Obter conexão com banco de dados"""
    return DatabaseConnection()

def safe_plotly_chart(chart_func, fallback_title="Gráfico"):
    """Função auxiliar para exibir gráficos com fallback"""
    if PLOTLY_AVAILABLE:
        try:
            return chart_func()
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {str(e)}")
            st.info(f"📊 {fallback_title} - Dados disponíveis em formato de tabela")
            return None
    else:
        st.info(f"📊 {fallback_title} - Plotly não disponível, exibindo dados em tabela")
        return None

def show_chart_or_table(chart_result, data, title="Dados"):
    """Mostrar gráfico ou tabela como fallback"""
    if chart_result is not None:
        st.plotly_chart(chart_result, use_container_width=True)
    else:
        st.markdown(f"**📊 {title}**")
        if isinstance(data, pd.DataFrame):
            st.dataframe(data)
        elif isinstance(data, dict):
            st.json(data)
        else:
            st.write(data)

def get_inventario_data():
    """Carregar dados do inventário de backup"""
    db = get_database()
    
    try:
        # DEBUG temporário
        st.write("🔍 DEBUG: Executando consulta equipamentos elétricos...")
        
        # Equipamentos elétricos
        equipamentos_eletricos = db.execute_query("""
            SELECT 'Elétrico' as tipo, codigo, nome, categoria, COALESCE(status, 'indefinido') as status, COALESCE(localizacao, 'N/A') as localizacao
            FROM equipamentos_eletricos
        """)
        st.write(f"🔍 DEBUG: Equipamentos elétricos encontrados: {len(equipamentos_eletricos or [])}")
        print(f"DEBUG: Equipamentos elétricos: {len(equipamentos_eletricos or [])}")
        
        # Equipamentos manuais (usa 'descricao' ao invés de 'nome')
        equipamentos_manuais = db.execute_query("""
            SELECT 'Manual' as tipo, codigo, descricao as nome, tipo as categoria, COALESCE(status, 'indefinido') as status, COALESCE(localizacao, 'N/A') as localizacao
            FROM equipamentos_manuais
        """)
        
        # Equipamentos manuais (usa 'descricao' ao invés de 'nome')
        st.write("🔍 DEBUG: Executando consulta equipamentos manuais...")
        equipamentos_manuais = db.execute_query("""
            SELECT 'Manual' as tipo, codigo, descricao as nome, tipo as categoria, COALESCE(status, 'indefinido') as status, COALESCE(localizacao, 'N/A') as localizacao
            FROM equipamentos_manuais
        """)
        st.write(f"🔍 DEBUG: Equipamentos manuais encontrados: {len(equipamentos_manuais or [])}")
        
        # Insumos (usa 'descricao' ao invés de 'nome' e não tem 'estoque_atual')
        st.write("🔍 DEBUG: Executando consulta insumos...")
        insumos = db.execute_query("""
            SELECT 'Insumo' as tipo, codigo, descricao as nome, categoria, CAST(COALESCE(quantidade, 0) as TEXT) as status, COALESCE(localizacao, 'N/A') as localizacao
            FROM insumos
        """)
        st.write(f"🔍 DEBUG: Insumos encontrados: {len(insumos or [])}")
        
        # Combinar todos os dados
        all_data = (equipamentos_eletricos or []) + (equipamentos_manuais or []) + (insumos or [])
        st.write(f"🔍 DEBUG: Total de itens combinados: {len(all_data)}")
        
        if all_data:
            df = pd.DataFrame(all_data)
            # Garantir que todas as colunas sejam strings
            for col in ['tipo', 'codigo', 'nome', 'categoria', 'status', 'localizacao']:
                if col in df.columns:
                    df[col] = df[col].astype(str).fillna('N/A')
            st.write(f"🔍 DEBUG: DataFrame criado com {len(df)} linhas")
            return df
        else:
            st.write("🔍 DEBUG: all_data está vazio, retornando DataFrame vazio")
            return pd.DataFrame()        # Insumos (usa 'descricao' ao invés de 'nome' e não tem 'estoque_atual')
        insumos = db.execute_query("""
            SELECT 'Insumo' as tipo, codigo, descricao as nome, categoria, CAST(COALESCE(quantidade, 0) as TEXT) as status, COALESCE(localizacao, 'N/A') as localizacao
            FROM insumos
        """)
        print(f"DEBUG: Insumos: {len(insumos or [])}")
        
        # Combinar todos os dados
        all_data = (equipamentos_eletricos or []) + (equipamentos_manuais or []) + (insumos or [])
        print(f"DEBUG: Total combinado: {len(all_data)}")
        
        if all_data:
            df = pd.DataFrame(all_data)
            # Garantir que todas as colunas sejam strings
            for col in ['tipo', 'codigo', 'nome', 'categoria', 'status', 'localizacao']:
                if col in df.columns:
                    df[col] = df[col].astype(str).fillna('N/A')
            print(f"DEBUG: DataFrame criado com {len(df)} linhas")
            return df
        else:
            print("DEBUG: all_data está vazio!")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"🔍 DEBUG: ERRO ao carregar dados do inventário: {str(e)}")
        import traceback
        st.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        return pd.DataFrame()

def create_excel_download(df, filename):
    """Criar link de download para Excel ou CSV"""
    try:
        # Tentar Excel primeiro
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatório')
        
        processed_data = output.getvalue()
        b64 = base64.b64encode(processed_data).decode()
        return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Baixar Excel</a>'
    
    except Exception as e:
        # Fallback para CSV se Excel falhar
        output = io.StringIO()
        df.to_csv(output, index=False)
        csv_filename = filename.replace('.xlsx', '.csv')
        encoded = base64.b64encode(output.getvalue().encode()).decode()
        return f'<a href="data:text/csv;base64,{encoded}" download="{csv_filename}">📥 Baixar CSV</a>'

def show_inventario_completo():
    """Mostrar relatório de inventário completo"""
    st.subheader("📄 Relatório de Inventário Completo")
    
    # DEBUG temporário
    st.info("🔍 DEBUG: Iniciando carregamento de dados...")
    
    with st.spinner("Carregando dados..."):
        df = get_inventario_data()
    
    # DEBUG temporário
    st.info(f"🔍 DEBUG: DataFrame carregado - Linhas: {len(df)}, Vazio: {df.empty}")
    
    if df.empty:
        st.error("❌ PROBLEMA: DataFrame está vazio!")
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
        if PLOTLY_AVAILABLE and px:
            try:
                fig_tipo = px.pie(values=tipo_counts.values, names=tipo_counts.index, 
                                 title="Distribuição por Tipo")
                st.plotly_chart(fig_tipo, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráfico: {str(e)}")
                st.markdown("**📊 Distribuição por Tipo**")
                st.dataframe(tipo_counts.to_frame("Quantidade"))
        else:
            st.markdown("**📊 Distribuição por Tipo**")
            st.dataframe(tipo_counts.to_frame("Quantidade"))
    
    with col2:
        # Gráfico por categoria
        cat_counts = df['categoria'].value_counts().head(10)
        if PLOTLY_AVAILABLE and px:
            try:
                fig_cat = px.bar(x=cat_counts.values, y=cat_counts.index, 
                                orientation='h', title="Top 10 Categorias")
                st.plotly_chart(fig_cat, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar gráfico: {str(e)}")
                st.markdown("**📊 Top 10 Categorias**")
                st.dataframe(cat_counts.to_frame("Quantidade"))
        else:
            st.markdown("**📊 Top 10 Categorias**")
            st.dataframe(cat_counts.to_frame("Quantidade"))
    
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
    
    try:
        if tipo_filter != "Todos":
            filtered_df = filtered_df[filtered_df['tipo'].astype(str) == str(tipo_filter)]
        
        if categoria_filter != "Todas":
            filtered_df = filtered_df[filtered_df['categoria'].astype(str) == str(categoria_filter)]
        
        if status_filter != "Todos":
            filtered_df = filtered_df[filtered_df['status'].astype(str) == str(status_filter)]
    except Exception as e:
        st.error(f"Erro ao aplicar filtros: {str(e)}")
        filtered_df = df.copy()  # Usar dados originais se houver erro
    
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
    
    # Garantir que status seja string e tratar valores None
    df_mov['status'] = df_mov['status'].astype(str).fillna('indefinido')
    
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
    
    if PLOTLY_AVAILABLE and px:
        try:
            fig_daily = px.line(df_daily, x='data', y='movimentacoes', 
                               title="Movimentações por Dia")
            st.plotly_chart(fig_daily, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {str(e)}")
            st.markdown("**📊 Movimentações por Dia**")
            st.dataframe(df_daily)
    else:
        st.markdown("**📊 Movimentações por Dia**")
        st.dataframe(df_daily)
    
    # Tabela de movimentações
    st.markdown("### 📋 Detalhes das Movimentações")
    st.dataframe(df_mov, use_container_width=True)
    
    # Download
    filename = f"movimentacoes_{data_inicio}_{data_fim}.xlsx"
    excel_link = create_excel_download(df_mov, filename)
    st.markdown(excel_link, unsafe_allow_html=True)

def show():
    """Função principal da página Relatórios"""
    
    st.title("🔍 TESTE: Página Relatórios Backup")
    st.write("Se você está vendo esta mensagem, a página está funcionando!")
    
    try:
        # Verificar autenticação
        auth = get_auth()
        if not auth.is_authenticated():
            st.error("❌ Usuário não autenticado!")
            auth.show_login_page()
            return
        
        st.success("✅ Usuário autenticado!")
        
        # Verificar permissões 
        if not auth.require_role('visualizador'):
            st.error("❌ Usuário sem permissão!")
            return
        
        st.success("✅ Permissões OK!")
        
        # Teste simples de botão
        if st.button("🧪 TESTE: Carregar Dados", type="primary"):
            st.success("✅ Botão funcionou!")
            
            # Teste simples de consulta
            try:
                db = get_database()
                result = db.execute_query("SELECT COUNT(*) as total FROM equipamentos_eletricos")
                if result:
                    st.info(f"📊 Equipamentos elétricos no banco: {result[0]['total']}")
                else:
                    st.warning("⚠️ Consulta retornou vazio")
            except Exception as e:
                st.error(f"❌ Erro na consulta: {e}")
        
    except Exception as e:
        st.error(f"❌ ERRO GERAL: {e}")
        import traceback
        st.code(traceback.format_exc())
    
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
            if st.button("🔙 Voltar aos Relatórios", key="voltar_mov"):
                st.session_state.show_movimentacoes = False
    
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
                        SELECT timestamp, user_id, action as acao, details as detalhes
                        FROM logs_sistema
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
                
                if st.button("📊 Estatísticas de Backup", use_container_width=True):
                    try:
                        from utils.backup import get_backup_manager
                        backup_mgr = get_backup_manager()
                        stats = backup_mgr.get_backup_stats()
                        
                        if stats and isinstance(stats, dict):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                total_backups = stats.get('total_backups', 0)
                                st.metric("Total Backups", str(total_backups))
                                
                                last_backup = stats.get('last_backup')
                                if last_backup:
                                    if hasattr(last_backup, 'strftime'):
                                        st.metric("Último Backup", last_backup.strftime('%d/%m/%Y'))
                                    else:
                                        st.metric("Último Backup", str(last_backup))
                                else:
                                    st.metric("Último Backup", "Nenhum")
                            with col_b:
                                total_size = stats.get('total_size', 0)
                                if total_size and isinstance(total_size, (int, float)) and total_size > 0:
                                    size_mb = total_size / (1024 * 1024)
                                    st.metric("Tamanho Total", f"{size_mb:.1f} MB")
                                else:
                                    st.metric("Tamanho Total", "N/A")
                        else:
                            st.error("Erro ao obter estatísticas de backup")
                    except Exception as e:
                        st.error(f"Erro ao carregar estatísticas de backup: {str(e)}")
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

# Este arquivo deve ser importado, não executado diretamente