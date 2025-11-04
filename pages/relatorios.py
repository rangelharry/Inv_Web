#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Relatórios Avançados
Página de relatórios detalhados com gráficos, filtros e exportação
"""

import streamlit as st
## Removido import de CSS externo
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
import json

# Importação segura do Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly não disponível. Relatórios serão exibidos em formato alternativo.")

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth, check_authentication
from database.connection import DatabaseConnection
from utils.logging import SystemLogger

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

logger = SystemLogger()

def safe_plotly_chart(chart_func, *args, **kwargs):
    """Função auxiliar para criar gráficos com fallback"""
    if PLOTLY_AVAILABLE:
        try:
            return chart_func(*args, **kwargs)
        except Exception as e:
            st.error(f"Erro ao criar gráfico: {e}")
            return None
    else:
        return None

def safe_dataframe(df, use_container_width=True, **kwargs):
    """Função segura para exibir dataframe com fallback"""
    try:
        st.dataframe(df, use_container_width=use_container_width, **kwargs)
    except Exception as e:
        # Fallback para exibição alternativa
        st.markdown("**📊 Dados:**")
        if hasattr(df, 'to_string'):
            st.text(df.to_string())
        else:
            st.write(df)

def show_chart_or_table(fig, df, title="Dados"):
    """Mostrar gráfico se disponível, senão mostrar tabela"""
    if fig is not None and PLOTLY_AVAILABLE:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(f"#### 📊 {title}")
        if not df.empty:
            try:
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                # Fallback para exibição simples se dataframe falhar
                st.markdown("**Dados:**")
                if hasattr(df, 'to_string'):
                    st.text(df.to_string())
                else:
                    st.write(df)
        else:
            st.info("Nenhum dado disponível para exibir")

class AdvancedReportsManager:
    """Gerenciador de relatórios avançados"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_inventario_completo(self):
        """Obter dados completos do inventário"""
        try:
            # Equipamentos elétricos
            equipamentos_eletricos = self.db.execute_query("""
                SELECT 
                    'Equipamento Elétrico' as tipo,
                    codigo, nome as descricao, marca, categoria, status, 
                    localizacao, valor_compra as valor, data_compra
                FROM equipamentos_eletricos
            """)
            
            # Equipamentos manuais
            equipamentos_manuais = self.db.execute_query("""
                SELECT 
                    'Equipamento Manual' as tipo,
                    codigo, descricao, marca, tipo as categoria, status, 
                    localizacao, valor, data_compra
                FROM equipamentos_manuais
            """)
            
            # Insumos
            insumos = self.db.execute_query("""
                SELECT 
                    'Insumo' as tipo,
                    codigo, descricao, '' as marca, categoria, 
                    CASE 
                        WHEN quantidade > 0 THEN 'Disponível'
                        ELSE 'Esgotado'
                    END as status,
                    localizacao, preco_unitario as valor, '' as data_compra
                FROM insumos
            """)
            
            # Combinar todos os dados
            all_data = []
            for items in [equipamentos_eletricos or [], equipamentos_manuais or [], insumos or []]:
                all_data.extend(items)
            
            return pd.DataFrame(all_data) if all_data else pd.DataFrame()
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao obter dados do inventário: {e}")
            return pd.DataFrame()
    
    def get_movimentacoes_data(self, days=30):
        """Obter dados de movimentações"""
        try:
            data_limite = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            query = """
                SELECT 
                    m.id, m.codigo as item_codigo, m.origem, m.destino, 
                    m.quantidade, m.responsavel, m.data as data_movimentacao, m.status,
                    CASE 
                        WHEN ee.codigo IS NOT NULL THEN 'Equipamento Elétrico'
                        WHEN em.codigo IS NOT NULL THEN 'Equipamento Manual'
                        WHEN i.codigo IS NOT NULL THEN 'Insumo'
                        ELSE 'Desconhecido'
                    END as tipo_item,
                    CASE 
                        WHEN ee.codigo IS NOT NULL THEN ee.nome
                        WHEN em.codigo IS NOT NULL THEN em.descricao
                        WHEN i.codigo IS NOT NULL THEN i.descricao
                        ELSE 'Item não encontrado'
                    END as item_descricao
                FROM movimentacoes m
                LEFT JOIN equipamentos_eletricos ee ON m.codigo = ee.codigo
                LEFT JOIN equipamentos_manuais em ON m.codigo = em.codigo
                LEFT JOIN insumos i ON m.codigo = i.codigo
                WHERE DATE(m.data) >= ?
                ORDER BY m.data DESC
            """
            
            result = self.db.execute_query(query, (data_limite,))
            return pd.DataFrame(result) if result else pd.DataFrame()
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao obter movimentações: {e}")
            return pd.DataFrame()
    
    def generate_dashboard_metrics(self, df_inventario):
        """Gerar métricas para dashboard"""
        if df_inventario.empty:
            return {}
        
        # Calcular valor total (convertendo strings para float)
        valor_total = 0
        if 'valor' in df_inventario.columns:
            # Converter valores para numérico, ignorando valores não numéricos
            valores_numericos = pd.to_numeric(df_inventario['valor'], errors='coerce')
            valor_total = valores_numericos.fillna(0).sum()
        
        metrics = {
            'total_itens': len(df_inventario),
            'tipos_distribuicao': df_inventario['tipo'].value_counts().to_dict(),
            'status_distribuicao': df_inventario['status'].value_counts().to_dict(),
            'localizacoes': df_inventario['localizacao'].value_counts().to_dict(),
            'valor_total': valor_total
        }
        
        return metrics
    
    def create_status_pie_chart(self, df_inventario):
        """Criar gráfico de pizza para status dos itens"""
        if df_inventario.empty:
            return None
        
        status_counts = df_inventario['status'].value_counts()
        
        if PLOTLY_AVAILABLE:
            try:
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Distribuição por Status",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                
                return fig
            except Exception as e:
                st.error(f"Erro ao criar gráfico de pizza: {e}")
                return None
        else:
            return None
    
    def create_tipo_bar_chart(self, df_inventario):
        """Criar gráfico de barras para tipos de itens"""
        if df_inventario.empty:
            return None
        
        tipo_counts = df_inventario['tipo'].value_counts()
        
        if PLOTLY_AVAILABLE:
            try:
                fig = px.bar(
                    x=tipo_counts.index,
                    y=tipo_counts.values,
                    title="Distribuição por Tipo de Item",
                    labels={'x': 'Tipo', 'y': 'Quantidade'},
                    color=tipo_counts.values,
                    color_continuous_scale='viridis'
                )
                
                fig.update_layout(height=400, showlegend=False)
                
                return fig
            except Exception as e:
                st.error(f"Erro ao criar gráfico de barras: {e}")
                return None
        else:
            return None
    
    def create_localizacao_chart(self, df_inventario):
        """Criar gráfico para localização dos itens"""
        if df_inventario.empty:
            return None
        
        if not PLOTLY_AVAILABLE:
            return None
        
        loc_counts = df_inventario['localizacao'].value_counts().head(10)
        
        try:
            fig = px.bar(
                x=loc_counts.values,
                y=loc_counts.index,
                orientation='h',
                title="Top 10 Localizações",
                labels={'x': 'Quantidade', 'y': 'Localização'},
                color=loc_counts.values,
                color_continuous_scale='blues'
            )
        except NameError:
            return None
        except Exception as e:
            logger.log_action("error", f"Erro ao criar gráfico de localização: {e}")
            return None
        
        fig.update_layout(height=400, showlegend=False)
        
        return fig
    
    def create_movimentacoes_timeline(self, df_movimentacoes):
        """Criar timeline das movimentações"""
        if df_movimentacoes.empty:
            return None
        
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            # Converter data para datetime
            df_movimentacoes['data_movimentacao'] = pd.to_datetime(df_movimentacoes['data_movimentacao'])
            
            # Agrupar por dia
            daily_counts = df_movimentacoes.groupby(df_movimentacoes['data_movimentacao'].dt.date).size()
            
            fig = px.line(
                x=daily_counts.index,
                y=daily_counts.values,
                title="Movimentações ao Longo do Tempo",
                labels={'x': 'Data', 'y': 'Número de Movimentações'}
            )
            
            fig.update_layout(height=400)
            
            return fig
        except Exception as e:
            logger.log_action("error", f"Erro ao criar timeline de movimentações: {e}")
            return None
    
    def create_movimentacoes_by_type(self, df_movimentacoes):
        """Criar gráfico de movimentações por tipo"""
        if df_movimentacoes.empty:
            return None
        
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            type_counts = df_movimentacoes['tipo_item'].value_counts()
            
            fig = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                title="Movimentações por Tipo de Item",
                labels={'x': 'Tipo', 'y': 'Movimentações'},
                color=type_counts.values,
                color_continuous_scale='plasma'
            )
            
            fig.update_layout(height=400, showlegend=False)
            
            return fig
        except Exception as e:
            logger.log_action("error", f"Erro ao criar gráfico de movimentações por tipo: {e}")
            return None
    
    def generate_excel_report(self, df_inventario, df_movimentacoes=None):
        """Gerar relatório em Excel"""
        try:
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Aba do inventário
                df_inventario.to_excel(writer, sheet_name='Inventário Completo', index=False)
                
                if df_movimentacoes is not None and not df_movimentacoes.empty:
                    # Aba das movimentações
                    df_movimentacoes.to_excel(writer, sheet_name='Movimentações', index=False)
                
                # Aba de estatísticas
                if not df_inventario.empty:
                    stats_data = {
                        'Métrica': ['Total de Itens', 'Equipamentos Elétricos', 'Equipamentos Manuais', 'Insumos'],
                        'Valor': [
                            len(df_inventario),
                            len(df_inventario[df_inventario['tipo'] == 'Equipamento Elétrico']),
                            len(df_inventario[df_inventario['tipo'] == 'Equipamento Manual']),
                            len(df_inventario[df_inventario['tipo'] == 'Insumo'])
                        ]
                    }
                    
                    pd.DataFrame(stats_data).to_excel(writer, sheet_name='Estatísticas', index=False)
            
            output.seek(0)
            return output
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao gerar relatório Excel: {e}")
            return None
    
    def generate_csv_report(self, df_inventario):
        """Gerar relatório em CSV"""
        try:
            output = io.StringIO()
            df_inventario.to_csv(output, index=False, encoding='utf-8')
            return output.getvalue()
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao gerar relatório CSV: {e}")
            return None

def show_filters(df):
    """Mostrar filtros avançados"""
    st.markdown("### 🔍 Filtros Avançados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tipos_disponiveis = ['Todos'] + list(df['tipo'].dropna().unique()) if not df.empty else ['Todos']
        tipo_filter = st.selectbox("Tipo:", tipos_disponiveis)
    
    with col2:
        status_disponiveis = ['Todos'] + list(df['status'].dropna().unique()) if not df.empty else ['Todos']
        status_filter = st.selectbox("Status:", status_disponiveis)
    
    with col3:
        localizacoes_disponiveis = ['Todas'] + list(df['localizacao'].dropna().unique()) if not df.empty else ['Todas']
        localizacao_filter = st.selectbox("Localização:", localizacoes_disponiveis)
    
    with col4:
        search_term = st.text_input("Buscar:", placeholder="Código ou descrição...")
    
    # Aplicar filtros
    df_filtered = df.copy() if not df.empty else df
    
    if not df_filtered.empty:
        if tipo_filter != "Todos":
            df_filtered = df_filtered[df_filtered['tipo'] == tipo_filter]
        
        if status_filter != "Todos":
            df_filtered = df_filtered[df_filtered['status'] == status_filter]
        
        if localizacao_filter != "Todas":
            df_filtered = df_filtered[df_filtered['localizacao'] == localizacao_filter]
        
        if search_term:
            mask = (
                df_filtered['codigo'].str.contains(search_term, case=False, na=False) |
                df_filtered['descricao'].str.contains(search_term, case=False, na=False)
            )
            df_filtered = df_filtered[mask]
    
    return df_filtered

def show_export_options(reports_manager, df_inventario, df_movimentacoes=None):
    """Mostrar opções de exportação"""
    st.markdown("### 📤 Exportar Relatórios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Exportar Excel", help="Exportar inventário completo em Excel"):
            excel_data = reports_manager.generate_excel_report(df_inventario, df_movimentacoes)
            
            if excel_data:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_data,
                    file_name=f"inventario_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("✅ Relatório Excel gerado!")
    
    with col2:
        if st.button("📋 Exportar CSV", help="Exportar inventário em CSV"):
            csv_data = reports_manager.generate_csv_report(df_inventario)
            
            if csv_data:
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.success("✅ Relatório CSV gerado!")
    
    with col3:
        if st.button("📄 Gerar JSON", help="Exportar dados em formato JSON"):
            json_data = df_inventario.to_json(orient='records', indent=2)
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            st.success("✅ Relatório JSON gerado!")

def show():
    """Função principal da página de Relatórios Avançados"""
    
    # FORÃ‡AR TEMA CLARO - MODO EXTREMO
    # CSS global agora é aplicado pelo app.py
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    user = auth.get_current_user()
    
    st.markdown("## 📈 Relatórios Avançados")
    st.markdown("**Análises detalhadas** - Gráficos, filtros avançados e exportação")
    
    # Instanciar gerenciador de relatórios
    reports_manager = AdvancedReportsManager()
    
    # Tabs para organizar os relatórios
    tab_dashboard, tab_inventario, tab_movimentacoes, tab_analises = st.tabs([
        "📊 Dashboard", "📋 Inventário", "🔄 Movimentações", "📈 Análises"
    ])
    
    with tab_dashboard:
        st.markdown("### 📊 Dashboard Executivo")
        
        # Carregar dados
        with st.spinner("📊 Carregando dados..."):
            df_inventario = reports_manager.get_inventario_completo()
            df_movimentacoes = reports_manager.get_movimentacoes_data(30)
        
        if not df_inventario.empty:
            # Métricas principais
            metrics = reports_manager.generate_dashboard_metrics(df_inventario)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Itens", metrics['total_itens'])
            
            with col2:
                equipamentos_total = (
                    metrics['tipos_distribuicao'].get('Equipamento Elétrico', 0) +
                    metrics['tipos_distribuicao'].get('Equipamento Manual', 0)
                )
                st.metric("Equipamentos", equipamentos_total)
            
            with col3:
                insumos_total = metrics['tipos_distribuicao'].get('Insumo', 0)
                st.metric("Insumos", insumos_total)
            
            with col4:
                valor_total = f"R$ {metrics['valor_total']:,.2f}" if metrics['valor_total'] > 0 else "N/A"
                st.metric("Valor Total", valor_total)
            
            st.divider()
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                fig_status = reports_manager.create_status_pie_chart(df_inventario)
                status_counts = df_inventario['status'].value_counts() if not df_inventario.empty else pd.Series()
                show_chart_or_table(fig_status, status_counts.to_frame('Quantidade'), "Distribuição por Status")
            
            with col2:
                fig_tipo = reports_manager.create_tipo_bar_chart(df_inventario)
                tipo_counts = df_inventario['tipo'].value_counts() if not df_inventario.empty else pd.Series()
                show_chart_or_table(fig_tipo, tipo_counts.to_frame('Quantidade'), "Distribuição por Tipo")
            
            # Gráfico de localização
            fig_loc = reports_manager.create_localizacao_chart(df_inventario)
            loc_counts = df_inventario['localizacao'].value_counts() if not df_inventario.empty else pd.Series()
            show_chart_or_table(fig_loc, loc_counts.to_frame('Quantidade'), "Distribuição por Localização")
        
        else:
            st.warning("⚠️ Nenhum dado encontrado para gerar o dashboard")
    
    with tab_inventario:
        st.markdown("### 📋 Relatório de Inventário")
        
        # Carregar dados
        with st.spinner("📊 Carregando inventário..."):
            df_inventario = reports_manager.get_inventario_completo()
        
        if not df_inventario.empty:
            # Filtros
            df_filtered = show_filters(df_inventario)
            
            st.divider()
            
            # Tabela de dados
            st.markdown(f"### 📋 Inventário ({len(df_filtered)} itens)")
            
            # Configurar exibição da tabela
            columns_to_show = ['tipo', 'codigo', 'descricao', 'categoria', 'status', 'localizacao']
            if 'marca' in df_filtered.columns:
                columns_to_show.append('marca')
            if 'valor' in df_filtered.columns:
                columns_to_show.append('valor')
            
            # Usar função segura para exibir DataFrame
            safe_dataframe(
                df_filtered[columns_to_show],
                use_container_width=True,
                height=400
            )
            
            st.divider()
            
            # Opções de exportação
            show_export_options(reports_manager, df_filtered)
        
        else:
            st.warning("⚠️ Nenhum item encontrado no inventário")
    
    with tab_movimentacoes:
        st.markdown("### 🔄 Relatório de Movimentações")
        
        # Filtro de período
        col1, col2 = st.columns(2)
        
        with col1:
            dias_periodo = st.slider("Período (dias)", 7, 365, 30)
        
        with col2:
            incluir_pendentes = st.checkbox("Incluir movimentações pendentes", value=True)
        
        # Carregar dados
        with st.spinner("📊 Carregando movimentações..."):
            df_movimentacoes = reports_manager.get_movimentacoes_data(dias_periodo)
        
        if not df_movimentacoes.empty:
            # Filtrar pendentes se necessário
            if not incluir_pendentes:
                df_movimentacoes = df_movimentacoes[df_movimentacoes['status'] != 'Pendente']
            
            # Métricas das movimentações
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Movimentações", len(df_movimentacoes))
            
            with col2:
                aprovadas = len(df_movimentacoes[df_movimentacoes['status'] == 'Aprovada'])
                st.metric("Aprovadas", aprovadas)
            
            with col3:
                pendentes = len(df_movimentacoes[df_movimentacoes['status'] == 'Pendente'])
                st.metric("Pendentes", pendentes)
            
            with col4:
                tipos_unicos = df_movimentacoes['tipo_item'].nunique()
                st.metric("Tipos Movimentados", tipos_unicos)
            
            st.divider()
            
            # Gráficos de movimentações
            col1, col2 = st.columns(2)
            
            with col1:
                fig_timeline = reports_manager.create_movimentacoes_timeline(df_movimentacoes)
                if fig_timeline:
                    st.plotly_chart(fig_timeline, use_container_width=True)
            
            with col2:
                fig_by_type = reports_manager.create_movimentacoes_by_type(df_movimentacoes)
                if fig_by_type:
                    st.plotly_chart(fig_by_type, use_container_width=True)
            
            # Tabela de movimentações
            st.markdown("### 📋 Detalhes das Movimentações")
            
            columns_to_show = ['data_movimentacao', 'item_codigo', 'item_descricao', 'tipo_item', 
                             'origem', 'destino', 'quantidade', 'responsavel', 'status']
            
            # Usar função segura para exibir DataFrame  
            safe_dataframe(
                df_movimentacoes[columns_to_show],
                use_container_width=True,
                height=400
            )
            
            # Exportar movimentações
            if st.button("📤 Exportar Movimentações"):
                csv_movimentacoes = df_movimentacoes.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download Movimentações CSV",
                    data=csv_movimentacoes,
                    file_name=f"movimentacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.warning("⚠️ Nenhuma movimentação encontrada no período selecionado")
    
    with tab_analises:
        st.markdown("### 📈 Análises Estatísticas")
        
        # Carregar dados
        with st.spinner("📊 Preparando análises..."):
            df_inventario = reports_manager.get_inventario_completo()
            df_movimentacoes = reports_manager.get_movimentacoes_data(90)
        
        if not df_inventario.empty:
            # Análises estatísticas
            st.markdown("#### 📊 Estatísticas Descritivas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Distribuição por Categoria:**")
                if 'categoria' in df_inventario.columns:
                    categoria_counts = df_inventario['categoria'].value_counts()
                    for categoria, count in categoria_counts.head(10).items():
                        st.text(f"• {categoria}: {count}")
                
            with col2:
                st.markdown("**Distribuição por Localização:**")
                if 'localizacao' in df_inventario.columns:
                    loc_counts = df_inventario['localizacao'].value_counts()
                    for loc, count in loc_counts.head(10).items():
                        st.text(f"• {loc}: {count}")
            
            st.divider()
            
            # Análise de valores
            if 'valor' in df_inventario.columns:
                st.markdown("#### 💰 Análise Financeira")
                
                # Filtrar valores válidos (converter para numérico antes de comparar)
                try:
                    # Converter valores para numérico, colocando NaN onde não for possível
                    df_inventario_copy = df_inventario.copy()
                    df_inventario_copy['valor_numerico'] = pd.to_numeric(df_inventario_copy['valor'], errors='coerce')
                    
                    # Filtrar apenas valores válidos (não NaN e > 0)
                    df_com_valor = df_inventario_copy[
                        df_inventario_copy['valor_numerico'].notna() & 
                        (df_inventario_copy['valor_numerico'] > 0)
                    ]
                    
                    # Usar a coluna numérica para cálculos
                    df_com_valor = df_com_valor.copy()
                    df_com_valor['valor'] = df_com_valor['valor_numerico']
                except Exception as e:
                    st.error(f"Erro ao processar valores monetários: {e}")
                    df_com_valor = pd.DataFrame()  # DataFrame vazio se houver erro
                
                if not df_com_valor.empty:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        valor_total = df_com_valor['valor'].sum()
                        st.metric("Valor Total", f"R$ {valor_total:,.2f}")
                    
                    with col2:
                        valor_medio = df_com_valor['valor'].mean()
                        st.metric("Valor Médio", f"R$ {valor_medio:,.2f}")
                    
                    with col3:
                        valor_maximo = df_com_valor['valor'].max()
                        st.metric("Maior Valor", f"R$ {valor_maximo:,.2f}")
                    
                    with col4:
                        itens_com_valor = len(df_com_valor)
                        st.metric("Itens Avaliados", itens_com_valor)
                    
                    # Histograma de valores
                    if PLOTLY_AVAILABLE:
                        try:
                            fig_histogram = px.histogram(
                                df_com_valor,
                                x='valor',
                                nbins=20,
                                title="Distribuição dos Valores dos Itens",
                                labels={'valor': 'Valor (R$)', 'count': 'Quantidade'}
                            )
                            
                            fig_histogram.update_layout(height=400)
                            st.plotly_chart(fig_histogram, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erro ao criar histograma: {e}")
                            # Fallback: mostrar dados em tabela
                            st.subheader("Distribuição dos Valores dos Itens")
                            safe_dataframe(df_com_valor[['codigo', 'descricao', 'valor']].head(20))
                    else:
                        st.subheader("Distribuição dos Valores dos Itens")
                        safe_dataframe(df_com_valor[['codigo', 'descricao', 'valor']].head(20))
                
                else:
                    st.info("ℹ️ Poucos itens têm valores registrados para análise financeira")
            
            st.divider()
            
            # Tendências de movimentação
            if not df_movimentacoes.empty:
                st.markdown("#### 📈 Tendências de Movimentação")
                
                # Converter data para análise
                df_movimentacoes['data_movimentacao'] = pd.to_datetime(df_movimentacoes['data_movimentacao'])
                
                # Movimentações por semana
                df_movimentacoes['semana'] = df_movimentacoes['data_movimentacao'].dt.to_period('W')
                movimentacoes_semana = df_movimentacoes.groupby('semana').size()
                
                if len(movimentacoes_semana) > 1:
                    if PLOTLY_AVAILABLE:
                        try:
                            fig_tendencia = px.line(
                                x=movimentacoes_semana.index.astype(str),
                                y=movimentacoes_semana.values,
                                title="Tendência de Movimentações por Semana",
                                labels={'x': 'Semana', 'y': 'Número de Movimentações'}
                            )
                            
                            fig_tendencia.update_layout(height=400)
                            st.plotly_chart(fig_tendencia, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erro ao criar gráfico de tendência: {e}")
                            # Fallback: mostrar dados em tabela
                            st.subheader("Tendência de Movimentações por Semana")
                            trend_df = pd.DataFrame({
                                'Semana': movimentacoes_semana.index.astype(str),
                                'Movimentações': movimentacoes_semana.values
                            })
                            safe_dataframe(trend_df)
                    else:
                        st.subheader("Tendência de Movimentações por Semana")
                        trend_df = pd.DataFrame({
                            'Semana': movimentacoes_semana.index.astype(str),
                            'Movimentações': movimentacoes_semana.values
                        })
                        safe_dataframe(trend_df)
                
                # Top itens mais movimentados
                st.markdown("#### 🏆 Top Itens Mais Movimentados")
                top_itens = df_movimentacoes['item_codigo'].value_counts().head(10)
                
                if not top_itens.empty:
                    for i, (item, count) in enumerate(top_itens.items(), 1):
                        item_desc = df_movimentacoes[df_movimentacoes['item_codigo'] == item]['item_descricao'].iloc[0]
                        st.text(f"{i}. {item} - {item_desc}: {count} movimentações")
            
        else:
            st.warning("⚠️ Dados insuficientes para análises estatísticas")

if __name__ == "__main__":
    show()