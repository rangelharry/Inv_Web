#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Logs de Auditoria
Página para visualização e análise de logs do sistema
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth, check_authentication
from utils.logging import system_logger

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def show_logs_table(logs_data):
    """Exibir tabela de logs"""
    if not logs_data:
        st.info("📭 Nenhum log encontrado com os filtros aplicados")
        return
    
    for log in logs_data:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            
            with col1:
                # Timestamp formatado
                try:
                    dt = datetime.fromisoformat(log['timestamp'])
                    formatted_time = dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    formatted_time = log['timestamp']
                
                st.markdown(f"**🕒 {formatted_time}**")
                st.caption(f"👤 {log.get('username', 'Sistema')}")
            
            with col2:
                # Ação e detalhes
                action_emoji = {
                    'login_success': '🟢',
                    'login_failed': '🔴',
                    'logout': '🚪',
                    'create': '➕',
                    'update': '✏️',
                    'delete': '🗑️',
                    'movimentacao': '🔄',
                    'security': '🛡️'
                }.get(log['action'].split('_')[0], '📝')
                
                st.markdown(f"{action_emoji} **{log['action'].replace('_', ' ').title()}**")
                st.caption(log['details'])
            
            with col3:
                # Item code e IP
                if log.get('item_code'):
                    st.markdown(f"📦 **{log['item_code']}**")
                
                st.caption(f"🌐 {log.get('ip_address', 'N/A')}")
            
            with col4:
                # Botão para ver detalhes
                if st.button("🔍", key=f"details_{log.get('id', hash(log['timestamp']))}", help="Ver detalhes"):
                    st.session_state[f'show_details_{log.get("id", hash(log["timestamp"]))}'] = True
                    st.rerun()
            
            # Mostrar detalhes adicionais se solicitado
            if st.session_state.get(f'show_details_{log.get("id", hash(log["timestamp"]))}', False):
                with st.expander("📋 Detalhes Completos", expanded=True):
                    col_det1, col_det2 = st.columns(2)
                    
                    with col_det1:
                        st.markdown("**📊 Informações Básicas:**")
                        st.text(f"ID: {log.get('id', 'N/A')}")
                        st.text(f"Ação: {log['action']}")
                        st.text(f"Usuário: {log.get('username', 'Sistema')}")
                        st.text(f"IP: {log.get('ip_address', 'N/A')}")
                        st.text(f"Item: {log.get('item_code', 'N/A')}")
                    
                    with col_det2:
                        st.markdown("**📝 Detalhes:**")
                        st.text_area("", value=log['details'], height=100, disabled=True)
                        
                        if log.get('additional_data'):
                            st.markdown("**🔧 Dados Adicionais:**")
                            st.json(log['additional_data'])
                    
                    if st.button("❌ Fechar", key=f"close_{log.get('id', hash(log['timestamp']))}"):
                        del st.session_state[f'show_details_{log.get("id", hash(log["timestamp"]))}']
                        st.rerun()
            
            st.markdown("---")

def show_audit_summary():
    """Exibir resumo de auditoria"""
    summary = system_logger.get_audit_summary(30)
    
    if not summary:
        st.error("❌ Erro ao gerar resumo de auditoria")
        return
    
    st.markdown("### 📊 Resumo dos Últimos 30 Dias")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Total de ações
        total_actions = sum(action['count'] for action in summary['actions'])
        st.metric("Total de Ações", total_actions)
        
        # Top ações
        if summary['actions']:
            st.markdown("**🔝 Top Ações:**")
            for action in summary['actions'][:5]:
                st.text(f"• {action['action']}: {action['count']}")
    
    with col2:
        # Eventos de segurança
        st.metric(
            "Eventos de Segurança", 
            summary['security_events'],
            delta_color="inverse" if summary['security_events'] > 0 else "normal"
        )
        
        # Top usuários
        if summary['users']:
            st.markdown("**👥 Usuários Mais Ativos:**")
            for user in summary['users'][:5]:
                username = user['usuario'] or 'Sistema'
                st.text(f"• {username}: {user['count']}")
    
    with col3:
        # Métricas de tempo
        st.metric("Período", f"{summary['period_days']} dias")
        
        if total_actions > 0:
            avg_per_day = total_actions / summary['period_days']
            st.metric("Média por Dia", f"{avg_per_day:.1f}")

def show():
    """Função principal da página Logs de Auditoria"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    # Verificar permissões - apenas admin pode ver logs
    if not auth.require_role('admin'):
        st.error("🚫 **Acesso Negado**")
        st.warning("Apenas administradores podem visualizar logs de auditoria.")
        return
    
    st.markdown("## 📋 Logs de Auditoria")
    st.markdown("Sistema de logging e rastreabilidade de ações")
    
    # Resumo de auditoria
    show_audit_summary()
    
    st.markdown("---")
    
    # Filtros
    st.markdown("### 🔍 Filtros de Logs")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filtro por usuário
        users_query = system_logger.db.execute_query("SELECT id, usuario FROM usuarios WHERE ativo = 1")
        user_options = {"Todos": None}
        if users_query:
            user_options.update({user['usuario']: user['id'] for user in users_query})
        
        selected_user = st.selectbox("👤 Usuário:", list(user_options.keys()))
        user_id_filter = user_options[selected_user]
    
    with col2:
        # Filtro por ação
        action_filter = st.selectbox("⚡ Ação:", [
            "Todas", "login", "logout", "create", "update", "delete", 
            "movimentacao", "security"
        ])
        action_filter = None if action_filter == "Todas" else action_filter
    
    with col3:
        # Data inicial
        date_from = st.date_input("📅 Data Inicial:", value=datetime.now() - timedelta(days=7))
    
    with col4:
        # Data final
        date_to = st.date_input("📅 Data Final:", value=datetime.now())
    
    # Limite de registros
    limit = st.slider("📊 Máximo de Registros:", min_value=10, max_value=500, value=100)
    
    st.markdown("---")
    
    # Carregar e exibir logs
    with st.spinner("🔍 Carregando logs..."):
        logs = system_logger.get_logs(
            limit=limit,
            user_id=user_id_filter,
            action_filter=action_filter,
            date_from=date_from.isoformat() if date_from else None,
            date_to=date_to.isoformat() if date_to else None
        )
    
    if logs:
        st.markdown(f"### 📋 Logs Encontrados ({len(logs)})")
        show_logs_table(logs)
        
        # Botão para exportar (futuro)
        st.info("💡 **Próximas funcionalidades:** Exportação para CSV/PDF, alertas automáticos")
    else:
        st.warning("⚠️ Nenhum log encontrado com os filtros aplicados")
        st.info("Tente ajustar os filtros ou verificar se há atividade no sistema")

if __name__ == "__main__":
    show()