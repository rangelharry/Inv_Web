#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Dashboard
Página inicial com métricas, gráficos e informações gerais
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import get_database
from utils.auth import get_auth

def get_dashboard_metrics():
    """Obter métricas para o dashboard"""
    db = get_database()
    
    try:
        # Contadores principais
        equipamentos_result = db.execute_query("SELECT COUNT(*) as count FROM equipamentos")
        equipamentos = equipamentos_result[0]['count'] if equipamentos_result else 0
        
        equipamentos_manuais_result = db.execute_query("SELECT COUNT(*) as count FROM equipamentos_manuais")
        equipamentos_manuais = equipamentos_manuais_result[0]['count'] if equipamentos_manuais_result else 0
        
        insumos_result = db.execute_query("SELECT COUNT(*) as count FROM insumos")
        insumos = insumos_result[0]['count'] if insumos_result else 0
        
        obras_result = db.execute_query("SELECT COUNT(*) as count FROM obras")
        obras = obras_result[0]['count'] if obras_result else 0
        
        # Status dos equipamentos (combinando elétricos e manuais)
        equipamentos_disponiveis_result = db.execute_query(
            "SELECT COUNT(*) as count FROM equipamentos WHERE status = 'Disponível'"
        )
        equipamentos_disponiveis = equipamentos_disponiveis_result[0]['count'] if equipamentos_disponiveis_result else 0
        
        # Adicionar equipamentos manuais disponíveis
        equipamentos_manuais_disponiveis_result = db.execute_query(
            "SELECT COUNT(*) as count FROM equipamentos_manuais WHERE status = 'Disponível'"
        )
        equipamentos_disponiveis += equipamentos_manuais_disponiveis_result[0]['count'] if equipamentos_manuais_disponiveis_result else 0
        
        equipamentos_em_uso_result = db.execute_query(
            "SELECT COUNT(*) as count FROM equipamentos WHERE status = 'Em Uso'"
        )
        equipamentos_em_uso = equipamentos_em_uso_result[0]['count'] if equipamentos_em_uso_result else 0
        
        # Adicionar equipamentos manuais em uso
        equipamentos_manuais_em_uso_result = db.execute_query(
            "SELECT COUNT(*) as count FROM equipamentos WHERE categoria NOT LIKE '%Elétrica%' AND status = 'Em Uso'"
        )
        equipamentos_em_uso += equipamentos_manuais_em_uso_result[0]['count'] if equipamentos_manuais_em_uso_result else 0
        
        equipamentos_manutencao_result = db.execute_query(
            "SELECT COUNT(*) as count FROM equipamentos WHERE status = 'Manutenção'"
        )
        equipamentos_manutencao = equipamentos_manutencao_result[0]['count'] if equipamentos_manutencao_result else 0
        
        # Adicionar equipamentos manuais em manutenção
        equipamentos_manuais_manutencao_result = db.execute_query(
            "SELECT COUNT(*) as count FROM equipamentos WHERE categoria NOT LIKE '%Elétrica%' AND status = 'Manutenção'"
        )
        equipamentos_manutencao += equipamentos_manuais_manutencao_result[0]['count'] if equipamentos_manuais_manutencao_result else 0
        
        # Insumos com estoque baixo
        insumos_baixo_estoque_result = db.execute_query("""
            SELECT COUNT(*) as count FROM insumos 
            WHERE quantidade <= quantidade_minima
        """)
        insumos_baixo_estoque = insumos_baixo_estoque_result[0]['count'] if insumos_baixo_estoque_result else 0
        
        # Valor total do inventário
        valor_total_result = db.execute_query("""
            SELECT COALESCE(SUM(quantidade * preco_unitario), 0) as total 
            FROM insumos WHERE preco_unitario IS NOT NULL AND preco_unitario > 0
        """)
        valor_total = valor_total_result[0]['total'] if valor_total_result else 0
        
        # Movimentações recentes (últimos 7 dias)
        data_limite = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        movimentacoes_recentes_result = db.execute_query(f"""
            SELECT COUNT(*) as count FROM movimentacoes 
            WHERE data >= '{data_limite}'
        """)
        movimentacoes_recentes = movimentacoes_recentes_result[0]['count'] if movimentacoes_recentes_result else 0
        
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

def show_metrics_cards(metrics):
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

def show_status_chart(metrics):
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
    
    with col2:
        st.markdown("#### 📋 Resumo")
        
        # Cards de status
        st.markdown(f"""
        <div style='background: #d4edda; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;'>
            <strong>✅ Disponível:</strong> {metrics.get('equipamentos_disponiveis', 0)} equipamentos
        </div>
        <div style='background: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;'>
            <strong>⚠️ Em Uso:</strong> {metrics.get('equipamentos_em_uso', 0)} equipamentos
        </div>
        <div style='background: #f8d7da; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;'>
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

def show_alerts(metrics):
    """Exibir alertas e notificações"""
    st.markdown("### 🚨 Alertas do Sistema")
    
    alerts = []
    
    # Alerta de estoque baixo
    if metrics.get('insumos_baixo_estoque', 0) > 0:
        alerts.append({
            'tipo': 'warning',
            'titulo': '📦 Estoque Baixo',
            'mensagem': f"{metrics.get('insumos_baixo_estoque', 0)} insumos com estoque abaixo do mínimo",
            'acao': 'Ver Insumos'
        })
    
    # Alerta de equipamentos em manutenção
    if metrics.get('equipamentos_manutencao', 0) > 0:
        alerts.append({
            'tipo': 'info',
            'titulo': '🔧 Manutenção Pendente',
            'mensagem': f"{metrics.get('equipamentos_manutencao', 0)} equipamentos em manutenção",
            'acao': 'Ver Equipamentos'
        })
    
    # Alerta de alta utilização
    total_equipamentos = metrics.get('equipamentos_disponiveis', 0) + metrics.get('equipamentos_em_uso', 0)
    if total_equipamentos > 0:
        taxa_uso = (metrics.get('equipamentos_em_uso', 0) / total_equipamentos) * 100
        if taxa_uso > 70:
            alerts.append({
                'tipo': 'warning',
                'titulo': '⚡ Alta Utilização',
                'mensagem': f"{taxa_uso:.0f}% dos equipamentos estão em uso",
                'acao': 'Monitorar'
            })
    
    # Exibir alertas
    if alerts:
        for alert in alerts:
            if alert['tipo'] == 'warning':
                st.warning(f"**{alert['titulo']}:** {alert['mensagem']}")
            elif alert['tipo'] == 'info':
                st.info(f"**{alert['titulo']}:** {alert['mensagem']}")
            else:
                st.success(f"**{alert['titulo']}:** {alert['mensagem']}")
    else:
        st.success("✅ **Sistema OK:** Nenhum alerta no momento")

def show_recent_activity():
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
            
            for idx, row in df_display.head(5).iterrows():
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

def show_quick_actions():
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
    """Função principal da página Dashboard"""
    
    # Verificar autenticação
    auth = get_auth()
    auth.require_auth()
    
    # Header da página
    user = auth.get_current_user()
    st.markdown(f"## 🏠 Dashboard - Bem-vindo, {user['nome']}!")
    
    st.markdown("---")
    
    # Carregar métricas
    with st.spinner("📊 Carregando dados do dashboard..."):
        metrics = get_dashboard_metrics()
    
    if not metrics:
        st.error("❌ Erro ao carregar dados do dashboard")
        return
    
    # Exibir componentes do dashboard
    show_metrics_cards(metrics)
    
    st.markdown("---")
    
    # Gráficos e alertas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_status_chart(metrics)
    
    with col2:
        show_alerts(metrics)
    
    st.markdown("---")
    
    # Atividades recentes
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
