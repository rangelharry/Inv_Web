#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Dashboard
Página inicial com métricas, gráficos e informações gerais
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# CSS global
from utils.global_css import apply_global_css, force_light_theme, get_success_style, get_warning_style, get_error_style

# Importação segura do Plotly
try:
    import plotly.express as px  # type: ignore
    import plotly.graph_objects as go  # type: ignore
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly não disponível. Gráficos serão exibidos em formato alternativo.")

# Inicializar cache da sessão para evitar erro de cache_data
from utils.performance import get_cache_manager
get_cache_manager()._initialize_session_cache()

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import get_database
from utils.auth import get_auth
from utils.performance import get_cache_manager, optimize_query_performance
from utils.lazy_loading import get_lazy_loader, lazy_component, lazy_chart
from utils.feedback import get_feedback_manager, NotificationType
from typing import Dict, Any

def get_dashboard_metrics() -> Dict[str, Any]:
    """Obter métricas para o dashboard com cache otimizado"""
    db = get_database()
    
    try:
        # Contadores principais - consultas individuais para evitar erros
        try:
            equipamentos_result = db.execute_query("SELECT COUNT(*) as count FROM equipamentos_eletricos")
            equipamentos = equipamentos_result[0]['count'] if equipamentos_result else 0
        except:
            equipamentos = 0
            
        try:
            equipamentos_manuais_result = db.execute_query("SELECT COUNT(*) as count FROM equipamentos_manuais")
            equipamentos_manuais = equipamentos_manuais_result[0]['count'] if equipamentos_manuais_result else 0
        except:
            equipamentos_manuais = 0
            
        try:
            insumos_result = db.execute_query("SELECT COUNT(*) as count FROM insumos")
            insumos = insumos_result[0]['count'] if insumos_result else 0
        except:
            insumos = 0
            
        try:
            obras_result = db.execute_query("SELECT COUNT(*) as count FROM obras")
            obras = obras_result[0]['count'] if obras_result else 0
        except:
            obras = 0
        
        # Status dos equipamentos - consultas separadas para evitar problemas de UNION
        # Equipamentos disponíveis
        disp_eletricos = db.execute_query("""
            SELECT COUNT(*) as count FROM equipamentos_eletricos WHERE status = 'Disponível'
        """)
        disp_manuais = db.execute_query("""
            SELECT COUNT(*) as count FROM equipamentos_manuais WHERE status = 'Disponível'
        """)
        
        count_disp_eletricos = disp_eletricos[0]['count'] if disp_eletricos else 0
        count_disp_manuais = disp_manuais[0]['count'] if disp_manuais else 0
        equipamentos_disponiveis = count_disp_eletricos + count_disp_manuais
        
        # Contar equipamentos em uso - eletricos e manuais (consultas separadas)
        equipamentos_em_uso_eletricos = db.execute_query("""
            SELECT COUNT(*) as count FROM equipamentos_eletricos WHERE status = 'Em uso'
        """)
        equipamentos_em_uso_manuais = db.execute_query("""
            SELECT COUNT(*) as count FROM equipamentos_manuais WHERE status = 'Em Uso'
        """)
        
        count_eletricos = equipamentos_em_uso_eletricos[0]['count'] if equipamentos_em_uso_eletricos else 0
        count_manuais = equipamentos_em_uso_manuais[0]['count'] if equipamentos_em_uso_manuais else 0
        equipamentos_em_uso = count_eletricos + count_manuais
        
        # Contar equipamentos em manutenção - eletricos e manuais (consultas separadas)
        equipamentos_manutencao_eletricos = db.execute_query("""
            SELECT COUNT(*) as count FROM equipamentos_eletricos WHERE status = 'Em manutenção'
        """)
        equipamentos_manutencao_manuais = db.execute_query("""
            SELECT COUNT(*) as count FROM equipamentos_manuais WHERE status = 'Manutenção'
        """)
        
        count_manut_eletricos = equipamentos_manutencao_eletricos[0]['count'] if equipamentos_manutencao_eletricos else 0
        count_manut_manuais = equipamentos_manutencao_manuais[0]['count'] if equipamentos_manutencao_manuais else 0
        equipamentos_manutencao = count_manut_eletricos + count_manut_manuais
        
        # Insumos com estoque baixo
        try:
            insumos_baixo_estoque_result = db.execute_query("""
                SELECT COUNT(*) as count FROM insumos 
                WHERE quantidade <= quantidade_minima
            """)
            insumos_baixo_estoque = insumos_baixo_estoque_result[0]['count'] if insumos_baixo_estoque_result else 0
        except:
            insumos_baixo_estoque = 0
        
        # Valor total do inventário
        try:
            valor_total_result = db.execute_query("""
                SELECT COALESCE(SUM(quantidade * preco_unitario), 0) as total 
                FROM insumos WHERE preco_unitario IS NOT NULL AND preco_unitario > 0
            """)
            valor_total = valor_total_result[0]['total'] if valor_total_result else 0
        except:
            valor_total = 0
        
        # Movimentações recentes (últimos 7 dias)
        data_limite = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        try:
            movimentacoes_recentes_result = db.execute_query("""
                SELECT COUNT(*) as count FROM movimentacoes 
                WHERE data >= ?
            """, (data_limite,))
            movimentacoes_recentes = movimentacoes_recentes_result[0]['count'] if movimentacoes_recentes_result else 0
        except:
            # Se a tabela movimentacoes não existir ou houver erro, usar 0
            movimentacoes_recentes = 0
        
        return {
            'equipamentos': equipamentos,
            'equipamentos_manuais': equipamentos_manuais,
            'insumos': insumos,
            'obras': obras,
            'equipamentos_disponiveis': equipamentos_disponiveis,
            'equipamentos_em_uso': equipamentos_em_uso,
            'equipamentos_manutencao': equipamentos_manutencao,
            'insumos_baixo_estoque': insumos_baixo_estoque,
            'valor_total': valor_total,
            'movimentacoes_recentes': movimentacoes_recentes
        }
        
    except Exception as e:
        st.error(f"Erro ao carregar métricas: {e}")
        return {}

def show_metrics_cards(metrics: Dict[str, Any]) -> None:
    """Exibir cards com métricas principais"""
    st.markdown("### 📊 Visão Geral do Inventário")
    
    # Linha 1 - Contadores principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_equipamentos = metrics.get('equipamentos', 0) + metrics.get('equipamentos_manuais', 0)
        st.metric(
            label="⚡ Total Equipamentos",
            value=total_equipamentos,
            delta=f"{metrics.get('equipamentos_disponiveis', 0)} disponíveis",
            help="Equipamentos elétricos + manuais"
        )
    
    with col2:
        st.metric(
            label="📦 Insumos",
            value=metrics.get('insumos', 0),
            delta=f"-{metrics.get('insumos_baixo_estoque', 0)} baixo estoque" if metrics.get('insumos_baixo_estoque', 0) > 0 else "Estoque OK",
            delta_color="inverse" if metrics.get('insumos_baixo_estoque', 0) > 0 else "normal"
        )
    
    with col3:
        st.metric(
            label="🏗️ Obras Ativas",
            value=metrics.get('obras', 0),
            delta="Em andamento",
            help="Projetos e obras cadastradas"
        )
    
    with col4:
        valor_formatado = f"R$ {metrics.get('valor_total', 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        st.metric(
            label="💰 Valor Total",
            value=valor_formatado,
            delta=f"{metrics.get('movimentacoes_recentes', 0)} movimentações (7d)",
            help="Valor total dos insumos em estoque"
        )

def show_status_chart(metrics: Dict[str, Any]) -> None:
    """Exibir gráfico de status dos equipamentos"""
    st.markdown("### 📈 Status dos Equipamentos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Dados para o gráfico
        status_data = {
            'Status': ['Disponível', 'Em Uso', 'Em Manutenção'],
            'Quantidade': [
                metrics.get('equipamentos_disponiveis', 0),
                metrics.get('equipamentos_em_uso', 0),
                metrics.get('equipamentos_manutencao', 0)
            ],
            'Cores': ['#28a745', '#ffc107', '#dc3545']
        }
        
        # Criar gráfico de pizza
        if PLOTLY_AVAILABLE:
            fig = px.pie(
                values=status_data['Quantidade'],
                names=status_data['Status'],
                color_discrete_sequence=status_data['Cores'],
                title="Distribuição por Status"
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
            )
            
            fig.update_layout(
                showlegend=True,
                height=400,
                font_size=12
            )
            
            st.plotly_chart(fig, use_container_width=True, key="status_chart")
        else:
            # Versão alternativa sem Plotly - usando métricas
            st.markdown("#### 📊 Distribuição por Status")
            
            total = sum(status_data['Quantidade'])
            if total > 0:
                for i, (status, qtd, cor) in enumerate(zip(status_data['Status'], status_data['Quantidade'], status_data['Cores'])):
                    percentual = (qtd / total) * 100
                    st.metric(
                        label=status,
                        value=qtd,
                        delta=f"{percentual:.1f}%"
                    )
            else:
                st.info("📊 Nenhum equipamento cadastrado ainda")
    
    with col2:
        st.markdown("#### 📋 Resumo")
        
        # Cards de status
        st.markdown(f"""
        <div style='{get_success_style()}'>
            <strong>✅ Disponíveis:</strong> {metrics.get('equipamentos_disponiveis', 0)} equipamentos
        </div>
        <div style='{get_warning_style()}'>
            <strong>🔄 Em Uso:</strong> {metrics.get('equipamentos_em_uso', 0)} equipamentos
        </div>
        <div style='{get_error_style()}'>
            <strong>🔧 Manutenção:</strong> {metrics.get('equipamentos_manutencao', 0)} equipamentos
        </div>
        """, unsafe_allow_html=True)
        
        # Taxa de disponibilidade
        total_equipamentos = sum([
            metrics.get('equipamentos_disponiveis', 0),
            metrics.get('equipamentos_em_uso', 0),
            metrics.get('equipamentos_manutencao', 0)
        ])
        
        if total_equipamentos > 0:
            taxa_disponibilidade = (metrics.get('equipamentos_disponiveis', 0) / total_equipamentos) * 100
            st.metric(
                label="Taxa de Disponibilidade",
                value=f"{taxa_disponibilidade:.1f}%",
                delta="Meta: 80%",
                delta_color="normal" if taxa_disponibilidade >= 80 else "inverse"
            )

def show_alerts(metrics: Dict[str, Any]) -> None:
    """Exibir alertas e notificações integrados com o sistema de alertas"""
    try:
        from utils.alerts import alert_system
        alert_system.show_alerts_widget()
    except Exception as e:
        # Fallback para alertas básicos se o sistema de alertas não estiver disponível
        st.markdown("### 🚨 Alertas do Sistema")
        
        alerts = []
        
        # Alerta de estoque baixo
        if metrics.get('insumos_baixo_estoque', 0) > 0:
            alerts.append({
                'tipo': 'warning',
                'titulo': '📦 Estoque Baixo',
                'mensagem': f"{metrics.get('insumos_baixo_estoque', 0)} insumos com estoque abaixo do mínimo"
            })
        
        # Alerta de equipamentos em manutenção
        if metrics.get('equipamentos_manutencao', 0) > 0:
            alerts.append({
                'tipo': 'info',
                'titulo': '🔧 Manutenção Pendente',
                'mensagem': f"{metrics.get('equipamentos_manutencao', 0)} equipamentos em manutenção"
            })
        
        # Exibir alertas
        if alerts:
            for alert in alerts:
                if alert['tipo'] == 'warning':
                    st.warning(f"**{alert['titulo']}:** {alert['mensagem']}")
                else:
                    st.info(f"**{alert['titulo']}:** {alert['mensagem']}")
        else:
            st.success("✅ **Sistema OK:** Nenhum alerta no momento")

def show_recent_activity() -> None:
    """Exibir atividades recentes"""
    st.markdown("### 📋 Atividades Recentes")
    
    db = get_database()
    
    try:
        # Buscar movimentações recentes
        movimentacoes = db.execute_query("""
            SELECT 
                m.data,
                'Movimentação' as tipo_movimentacao,
                m.codigo as equipamento_codigo,
                CASE 
                    WHEN m.tabela_origem = 'equipamentos' THEN e.descricao
                    WHEN m.tabela_origem = 'insumos' THEN i.descricao
                    ELSE 'Item não identificado'
                END as equipamento_descricao,
                m.origem,
                m.destino,
                m.responsavel
            FROM movimentacoes m
            LEFT JOIN equipamentos e ON m.codigo = e.codigo AND m.tabela_origem = 'equipamentos'
            LEFT JOIN insumos i ON m.codigo = i.codigo AND m.tabela_origem = 'insumos'
            ORDER BY m.data DESC
            LIMIT 10
        """)
        
        if movimentacoes:
            # Criar DataFrame
            df = pd.DataFrame(movimentacoes)
            
            # Formatar colunas para exibição
            df_display = df.copy()
            df_display['Data/Hora'] = pd.to_datetime(df['data'], errors='coerce').dt.strftime('%d/%m/%Y')
            df_display['Equipamento'] = df['equipamento_codigo'] + ' - ' + df['equipamento_descricao'].astype(str).str[:30]
            df_display['Movimentação'] = df['tipo_movimentacao']
            df_display['De → Para'] = df['origem'].astype(str) + ' → ' + df['destino'].astype(str)
            df_display['Responsável'] = df['responsavel']
            
            # Exibir movimentações usando containers HTML
            st.markdown("**Movimentações Recentes:**")
            
            for _, row in df_display.head(5).iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{row['Equipamento']}**")
                        st.caption(f"🕒 {row['Data/Hora']}")
                    
                    with col2:
                        st.markdown(f"📦 {row['Movimentação']}")
                        st.caption(f"🔄 {row['De → Para']}")
                    
                    with col3:
                        st.markdown(f"👤 {row['Responsável']}")
                    
                    st.markdown("---")
        else:
            st.info("📭 Nenhuma movimentação recente encontrada")
            
    except Exception as e:
        st.error(f"Erro ao carregar atividades: {e}")

def show_quick_actions() -> None:
    """Exibir botões de ações rápidas"""
    st.markdown("### ⚡ Ações Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Novo Equipamento", use_container_width=True):
            st.switch_page("pages/equipamentos_eletricos.py")
    
    with col2:
        if st.button("📦 Novo Insumo", use_container_width=True):
            st.switch_page("pages/insumos.py")
    
    with col3:
        if st.button("🔄 Nova Movimentação", use_container_width=True):
            st.switch_page("pages/movimentacoes.py")
    
    with col4:
        if st.button("📊 Gerar Relatório", use_container_width=True):
            st.switch_page("pages/relatorios.py")

def show():
    """Função principal da página Dashboard com otimizações de performance"""
    
    # FORÃ‡AR TEMA CLARO - MODO EXTREMO
    apply_global_css()
    force_light_theme()
    
    # Verificar autenticação
    auth = get_auth()
    auth.require_auth()
    
    # Inicializar otimizações de performance
    optimize_query_performance()
    
    # Header da página
    user = auth.get_current_user()
    user_name = user['nome'] if user and 'nome' in user else 'Usuário'
    
    # Header com animação
    st.markdown(f"""
    <div class="fade-in">
        <h2>🏠 Dashboard - Bem-vindo, {user_name}!</h2>
        <p style="color: #6c757d; margin-top: 0.5rem;">
            📅 {datetime.now().strftime('%d/%m/%Y')} • 🕐 {datetime.now().strftime('%H:%M')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feedback manager
    feedback_manager = get_feedback_manager()
    feedback_manager.log_user_action("dashboard_access")
    
    # Carregar métricas
    try:
        metrics = get_dashboard_metrics()
        if not metrics:
            st.error("❌ Erro ao carregar dados do dashboard")
            return
            
        # Exibir cartões de métricas
        show_metrics_cards(metrics)
    except Exception as e:
        st.error(f"❌ Erro ao carregar métricas: {e}")
        return
    
    st.markdown("---")
    
    # Gráficos e alertas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        try:
            show_status_chart(metrics)
        except Exception as e:
            st.error(f"Erro ao carregar gráficos: {e}")
    
    with col2:
        try:
            show_alerts(metrics)
        except Exception as e:
            st.error(f"Erro ao carregar alertas: {e}")
    
    st.markdown("---")
    
    # Performance stats (apenas para admins)
    if auth.has_permission('admin'):
        with st.expander("⚡ Estatísticas de Performance"):
            from utils.performance import show_cache_stats
            from utils.lazy_loading import show_lazy_loading_stats
            
            col_perf1, col_perf2 = st.columns(2)
            
            with col_perf1:
                st.markdown("### 💾 Cache")
                show_cache_stats()
            
            with col_perf2:
                st.markdown("### 📊 Lazy Loading")
                show_lazy_loading_stats()
    
    # Atividades recentes com lazy loading
    show_recent_activity()
    
    st.markdown("---")
    
    # Ações rápidas
    show_quick_actions()
    
    # Atualização automática
    st.markdown("---")
    st.markdown("🔄 **Atualização automática:** Os dados são atualizados a cada carregamento da página")
    
    if st.button("🔄 Atualizar Dashboard", type="secondary"):
        st.rerun()

if __name__ == "__main__":
    from pages import dashboard
    dashboard.show()
