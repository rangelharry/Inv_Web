#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Autenticação
Sistema de login, sessões e controle de acesso para Streamlit
"""

import hashlib
import streamlit as st
from datetime import datetime, timedelta
from database.connection import get_database
from typing import Optional, Dict, Any

class WebAuth:
    """Gerenciador de autenticação web"""
    
    def __init__(self):
        """Inicializar sistema de autenticação"""
        self.db = get_database()
        
        # Inicializar sessão se não existir
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
    
    def hash_password(self, password: str) -> str:
        """
        Gerar hash SHA256 da senha
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash SHA256 da senha
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autenticar usuário no banco de dados
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            Dados do usuário se autenticado, None se falha
        """
        if not username or not password:
            return None
        
        password_hash = self.hash_password(password)
        
        query = """
            SELECT id, usuario, nome, ativo, ultimo_acesso
            FROM usuarios
            WHERE usuario = ? AND senha_hash = ?
        """
        
        result = self.db.execute_query(query, (username, password_hash))
        
        if result and len(result) > 0:
            user = result[0]
            
            # Verificar se usuário está ativo
            if not user['ativo']:
                return None
            
            # Atualizar último acesso
            self.db.execute_update(
                "UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?",
                (datetime.now().isoformat(), user['id'])
            )
            
            return user
        
        return None
    
    def login_user(self, username: str, password: str) -> bool:
        """
        Fazer login do usuário
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            True se login bem-sucedido, False caso contrário
        """
        user_data = self.authenticate_user(username, password)
        
        if user_data:
            st.session_state.authenticated = True
            st.session_state.user_data = user_data
            st.session_state.login_time = datetime.now()
            
            # Log de auditoria
            self.log_login_attempt(user_data['id'], True)
            
            return True
        else:
            # Log de tentativa falhada
            self.log_login_attempt(None, False, username)
            return False
    
    def logout_user(self):
        """Fazer logout do usuário"""
        if st.session_state.authenticated and st.session_state.user_data:
            # Log de logout
            self.log_logout(st.session_state.user_data['id'])
        
        # Limpar sessão
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.login_time = None
        
        # Limpar outros dados da sessão
        keys_to_clear = [k for k in st.session_state.keys() if k not in ['authenticated', 'user_data', 'login_time']]
        for key in keys_to_clear:
            del st.session_state[key]
    
    def is_authenticated(self) -> bool:
        """
        Verificar se usuário está autenticado
        
        Returns:
            True se autenticado, False caso contrário
        """
        return st.session_state.get('authenticated', False)
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Obter dados do usuário atual
        
        Returns:
            Dados do usuário ou None se não autenticado
        """
        if self.is_authenticated():
            return st.session_state.get('user_data')
        return None
    
    def check_session_timeout(self, timeout_hours: int = 8) -> bool:
        """
        Verificar timeout da sessão
        
        Args:
            timeout_hours: Horas para timeout
            
        Returns:
            True se sessão válida, False se expirada
        """
        if not self.is_authenticated():
            return False
        
        login_time = st.session_state.get('login_time')
        if not login_time:
            return False
        
        time_diff = datetime.now() - login_time
        if time_diff > timedelta(hours=timeout_hours):
            self.logout_user()
            return False
        
        return True
    
    def require_auth(self):
        """Decorador para páginas que requerem autenticação"""
        if not self.is_authenticated() or not self.check_session_timeout():
            st.warning("⚠️ Você precisa fazer login para acessar esta página.")
            self.show_login_page()
            st.stop()
    
    def log_login_attempt(self, user_id: Optional[int], success: bool, username: str = ""):
        """
        Registrar tentativa de login na auditoria
        
        Args:
            user_id: ID do usuário (None se falha)
            success: Se login foi bem-sucedido
            username: Nome de usuário (para falhas)
        """
        try:
            acao = "Login realizado" if success else f"Tentativa de login falhada: {username}"
            
            # Obter nome do usuário se disponível
            usuario_nome = ""
            if user_id:
                user_result = self.db.execute_query("SELECT usuario FROM usuarios WHERE id = ?", (user_id,))
                usuario_nome = user_result[0]['usuario'] if user_result else str(user_id)
            else:
                usuario_nome = username
            
            self.db.execute_update("""
                INSERT INTO auditoria (usuario, acao, detalhes, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                usuario_nome,
                acao,
                f"Login via web - IP: {st.session_state.get('client_ip', 'Unknown')}",
                datetime.now().isoformat()
            ))
        except Exception as e:
            st.error(f"Erro ao registrar auditoria: {e}")
    
    def log_logout(self, user_id: int):
        """
        Registrar logout na auditoria
        
        Args:
            user_id: ID do usuário
        """
        try:
            # Obter nome do usuário
            user_result = self.db.execute_query("SELECT usuario FROM usuarios WHERE id = ?", (user_id,))
            usuario_nome = user_result[0]['usuario'] if user_result else str(user_id)
            
            self.db.execute_update("""
                INSERT INTO auditoria (usuario, acao, detalhes, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                usuario_nome,
                "Logout realizado",
                "Logout via web",
                datetime.now().isoformat()
            ))
        except Exception as e:
            st.error(f"Erro ao registrar logout: {e}")
    
    def show_login_page(self):
        """Exibir página de login"""
        st.title("🔐 Sistema de Inventário Web")
        st.markdown("---")
        
        # Container centralizado para login
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style='background: #f0f2f6; padding: 2rem; border-radius: 10px; text-align: center;'>
                <h3>Acesso ao Sistema</h3>
                <p>Digite suas credenciais para continuar</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Formulário de login
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "👤 Usuário",
                    placeholder="Digite seu nome de usuário", 
                    help="Use: admin ou cinthia"
                )
                
                password = st.text_input(
                    "🔒 Senha",
                    type="password",
                    placeholder="Digite sua senha",
                    help="Senha definida no sistema"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_login, col_demo = st.columns(2)
                
                with col_login:
                    login_button = st.form_submit_button(
                        "🚀 Entrar",
                        use_container_width=True,
                        type="primary"
                    )
                
                with col_demo:
                    demo_button = st.form_submit_button(
                        "🎯 Demo",
                        use_container_width=True,
                        help="Acesso de demonstração"
                    )
                
                # Processar login
                if login_button:
                    if not username or not password:
                        st.error("❌ Por favor, preencha todos os campos!")
                    else:
                        with st.spinner("🔍 Verificando credenciais..."):
                            if self.login_user(username, password):
                                st.success("✅ Login realizado com sucesso!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Usuário ou senha incorretos!")
                
                # Modo demonstração
                if demo_button:
                    with st.spinner("🎯 Ativando modo demonstração..."):
                        if self.login_user("admin", "admin123"):
                            st.success("✅ Modo demonstração ativado!")
                            st.info("👋 Bem-vindo ao modo demo!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao ativar demonstração!")
        
        # Informações do sistema
        st.markdown("---")
        
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.info("""
            **👥 Usuários de Teste:**
            - admin / admin123
            - cinthia / cinthia123
            """)
        
        with col_info2:
            st.info("""
            **🌐 Sistema Web:**
            - Acesso simultâneo
            - Dados em tempo real
            - Interface responsiva
            """)
        
        with col_info3:
            st.info("""
            **🔒 Segurança:**
            - Senhas criptografadas
            - Sessões seguras
            - Log de auditoria
            """)

# Instância global para cache
@st.cache_resource
def get_auth() -> WebAuth:
    """
    Obter instância de autenticação (cached)
    
    Returns:
        Instância de WebAuth
    """
    return WebAuth()

def check_authentication() -> bool:
    """
    Verificar se o usuário está autenticado
    Função auxiliar para uso direto em páginas
    
    Returns:
        True se autenticado, False caso contrário
    """
    auth = get_auth()
    
    # Verificar se está autenticado e sessão não expirou
    if not auth.is_authenticated() or not auth.check_session_timeout():
        # Se não autenticado, mostrar página de login
        auth.show_login_page()
        return False
    
    return True