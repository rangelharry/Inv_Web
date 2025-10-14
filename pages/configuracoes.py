#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Configurações
Página de configurações do sistema
"""

import streamlit as st
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth, check_authentication
from database.connection import DatabaseConnection
import hashlib

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def hash_password(password):
    """Cria hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def show_change_password_form():
    """Formulário para alterar senha"""
    with st.form("change_password_form"):
        st.markdown("#### 🔑 Alterar Senha")
        
        current_password = st.text_input("Senha Atual", type="password")
        new_password = st.text_input("Nova Senha", type="password")
        confirm_password = st.text_input("Confirmar Nova Senha", type="password")
        
        submitted = st.form_submit_button("Alterar Senha", use_container_width=True)
        
        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("⚠️ Todos os campos são obrigatórios")
                return
            
            if new_password != confirm_password:
                st.error("⚠️ As senhas não coincidem")
                return
            
            if len(new_password) < 6:
                st.error("⚠️ A senha deve ter pelo menos 6 caracteres")
                return
            
            # Verificar senha atual
            auth = get_auth()
            user = auth.get_current_user()
            
            if user:
                db = DatabaseConnection()
                
                # Verificar senha atual
                current_hash = hash_password(current_password)
                result = db.execute_query(
                    "SELECT id FROM usuarios WHERE id = ? AND senha = ?",
                    (user['id'], current_hash)
                )
                
                if result:
                    # Atualizar senha
                    new_hash = hash_password(new_password)
                    db.execute_query(
                        "UPDATE usuarios SET senha = ? WHERE id = ?",
                        (new_hash, user['id'])
                    )
                    st.success("✅ Senha alterada com sucesso!")
                    st.rerun()
                else:
                    st.error("⚠️ Senha atual incorreta")
            else:
                st.error("⚠️ Erro ao identificar usuário")

def show_activity_log():
    """Mostra log de atividades do usuário"""
    auth = get_auth()
    user = auth.get_current_user()
    
    if user:
        db = DatabaseConnection()
        
        # Buscar registros de auditoria do usuário
        logs = db.execute_query("""
            SELECT data_hora, acao, detalhes 
            FROM auditoria 
            WHERE usuario_id = ? 
            ORDER BY data_hora DESC 
            LIMIT 20
        """, (user['id'],))
        
        st.markdown("#### 📋 Últimas Atividades")
        
        if logs:
            import pandas as pd
            df = pd.DataFrame(logs)
            df['data_hora'] = pd.to_datetime(df['data_hora'])
            df['data_hora'] = df['data_hora'].dt.strftime('%d/%m/%Y %H:%M:%S')
            
            st.dataframe(
                df,
                column_config={
                    "data_hora": "Data/Hora",
                    "acao": "Ação",
                    "detalhes": "Detalhes"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📝 Nenhuma atividade registrada")
    else:
        st.error("⚠️ Erro ao identificar usuário")

def show():
    """Função principal da página Configurações"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    user = auth.get_current_user()
    
    st.markdown(f"## ⚙️ Configurações do Sistema")
    st.markdown("Configurações gerais e preferências do usuário")
    
    # Seções de configurações
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Perfil", "🔧 Sistema", "🔒 Segurança", "📊 Relatórios"])
    
    with tab1:
        st.markdown("### 👤 Informações do Perfil")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Nome", value=user['nome'] if user else "", disabled=True)
            st.text_input("Usuário", value=user['usuario'] if user else "", disabled=True)
        
        with col2:
            st.text_input("Tipo de Usuário", value="Administrador", disabled=True)
            if user and 'ultimo_acesso' in user:
                st.text_input("Último Acesso", value=user['ultimo_acesso'], disabled=True)
        
        st.markdown("---")
        st.info("Para alterar informações do perfil, entre em contato com o administrador do sistema.")
    
    with tab2:
        st.markdown("### 🔧 Configurações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Tema da Interface", ["Claro", "Escuro", "Automático"], index=0, disabled=True)
            st.selectbox("Idioma", ["Português (BR)", "English"], index=0, disabled=True)
        
        with col2:
            st.number_input("Timeout da Sessão (horas)", min_value=1, max_value=24, value=8, disabled=True)
            st.selectbox("Fuso Horário", ["America/Sao_Paulo"], index=0, disabled=True)
        
        st.markdown("---")
        st.warning("⚠️ Configurações do sistema estão em desenvolvimento")
    
    with tab3:
        st.markdown("### 🔒 Configurações de Segurança")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔑 Alterar Senha", use_container_width=True):
                show_change_password_form()
            
            if st.button("📱 Autenticação 2FA", use_container_width=True):
                st.info("Funcionalidade em desenvolvimento...")
        
        with col2:
            if st.button("📋 Log de Atividades", use_container_width=True):
                show_activity_log()
            
            if st.button("🔐 Sessões Ativas", use_container_width=True):
                st.info("Funcionalidade em desenvolvimento...")
        
        st.markdown("---")
        st.info("💡 Por segurança, algumas configurações requerem confirmação por email")
    
    with tab4:
        st.markdown("### 📊 Configurações de Relatórios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Formato Padrão", ["PDF", "Excel", "CSV"], index=0, disabled=True)
            st.selectbox("Frequência de Backup", ["Diário", "Semanal", "Mensal"], index=1, disabled=True)
        
        with col2:
            st.text_input("Email para Relatórios", placeholder="seu@email.com", disabled=True)
            st.checkbox("Receber Alertas por Email", value=True, disabled=True)
        
        st.markdown("---")
        st.warning("⚠️ Configurações de relatórios estão em desenvolvimento")
    
    # Informações do sistema
    st.markdown("---")
    st.markdown("### 📋 Informações do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🌐 Sistema Web**
        - Versão: 2.0
        - Framework: Streamlit
        - Banco: SQLite
        """)
    
    with col2:
        st.info("""
        **🔒 Segurança**
        - Autenticação: Ativa
        - Criptografia: SHA256
        - Sessões: Seguras
        """)
    
    with col3:
        st.info("""
        **📊 Performance**
        - Status: Online
        - Cache: Ativo
        - Backup: Automático
        """)
    
    # Informações sobre desenvolvimento
    st.markdown("---")
    st.info("""
    💡 **Funcionalidades em desenvolvimento:**
    - ✅ Interface de configurações
    - ⏳ Alteração de senha
    - ⏳ Configurações de tema
    - ⏳ Notificações por email
    - ⏳ Backup automático
    - ⏳ Personalização avançada
    """)

if __name__ == "__main__":
    from pages import configuracoes
    configuracoes.show()