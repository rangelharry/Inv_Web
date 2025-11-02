#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Autenticação
Sistema de login, sessões e controle de acesso para Streamlit
"""

import hashlib
import bcrypt
import streamlit as st
from datetime import datetime, timedelta
from database.connection import get_database
from typing import Optional, Dict, Any
import re

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
    
    def hash_password(self, password: str, use_bcrypt: bool = True) -> str:
        """
        Gerar hash da senha (bcrypt ou SHA256 para compatibilidade)
        
        Args:
            password: Senha em texto plano
            use_bcrypt: Se True, usa bcrypt; se False, usa SHA256 (compatibilidade)
            
        Returns:
            Hash da senha
        """
        if use_bcrypt:
            # Usar bcrypt com salt automático para novas senhas
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            # SHA256 para compatibilidade com senhas existentes
            return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verificar senha contra hash armazenado
        
        Args:
            password: Senha em texto plano
            stored_hash: Hash armazenado no banco
            
        Returns:
            True se senha correta, False caso contrário
        """
        # Verificar se é hash bcrypt (começa com $2b$)
        if stored_hash.startswith('$2b$'):
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except Exception:
                return False
        else:
            # Hash SHA256 legado
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            return sha256_hash == stored_hash
    
    def validate_password_strength(self, password: str) -> tuple[bool, list[str]]:
        """
        Validar força da senha
        
        Args:
            password: Senha a ser validada
            
        Returns:
            Tupla (é_válida, lista_de_erros)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Senha deve ter pelo menos 8 caracteres")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Senha deve conter pelo menos uma letra maiúscula")
        
        if not re.search(r'[a-z]', password):
            errors.append("Senha deve conter pelo menos uma letra minúscula")
        
        if not re.search(r'\d', password):
            errors.append("Senha deve conter pelo menos um número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Senha deve conter pelo menos um caractere especial")
        
        return len(errors) == 0, errors
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autenticar usuário no banco de dados com suporte a bcrypt e SHA256
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            Dados do usuário se autenticado, None se falha
        """
        if not username or not password:
            return None
        
        # Buscar usuário primeiro
        query = """
            SELECT id, usuario, nome, ativo, ultimo_acesso, senha_hash, tentativas_login, bloqueado_ate, role
            FROM usuarios
            WHERE usuario = ?
        """
        
        result = self.db.execute_query(query, (username,))
        
        if not result or len(result) == 0:
            return None
        
        user = result[0]
        
        # Verificar se usuário está ativo
        if not user['ativo']:
            return None
        
        # Verificar se está bloqueado por tentativas
        if user.get('bloqueado_ate'):
            bloqueado_ate = datetime.fromisoformat(user['bloqueado_ate'])
            if datetime.now() < bloqueado_ate:
                return None
        
        # Verificar senha
        stored_hash = user['senha_hash']
        if not self.verify_password(password, stored_hash):
            # Incrementar tentativas falhadas
            tentativas = user.get('tentativas_login', 0) + 1
            bloqueado_ate = None
            
            # Bloquear após 5 tentativas por 30 minutos
            if tentativas >= 5:
                bloqueado_ate = (datetime.now() + timedelta(minutes=30)).isoformat()
                tentativas = 0  # Reset counter
            
            self.db.execute_update("""
                UPDATE usuarios 
                SET tentativas_login = ?, bloqueado_ate = ? 
                WHERE id = ?
            """, (tentativas, bloqueado_ate, user['id']))
            
            return None
        
        # Login bem-sucedido - resetar tentativas e atualizar último acesso
        self.db.execute_update("""
            UPDATE usuarios 
            SET ultimo_acesso = ?, tentativas_login = 0, bloqueado_ate = NULL
            WHERE id = ?
        """, (datetime.now().isoformat(), user['id']))
        
        # Verificar se precisa atualizar hash da senha (migração SHA256 -> bcrypt)
        if not stored_hash.startswith('$2b$'):
            new_hash = self.hash_password(password, use_bcrypt=True)
            self.db.execute_update(
                "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
                (new_hash, user['id'])
            )
        
        return user
    
    def login_user(self, username: str, password: str) -> bool:
        """
        Fazer login do usuário com rate limiting
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            True se login bem-sucedido, False caso contrário
        """
        # Verificar rate limiting primeiro
        from utils.rate_limiting import rate_limiter
        
        is_allowed, rate_message = rate_limiter.check_rate_limit()
        if not is_allowed:
            st.error(f"🚫 {rate_message}")
            return False
        
        user_data = self.authenticate_user(username, password)
        
        if user_data:
            st.session_state.authenticated = True
            st.session_state.user_data = user_data
            st.session_state.login_time = datetime.now()
            
            # Registrar tentativa bem-sucedida (limpa rate limit)
            rate_limiter.record_attempt(success=True)
            
            # Log de auditoria
            from utils.logging import log_action
            log_action(
                "login_success", 
                f"Login bem-sucedido para usuário: {username}",
                user_id=user_data['id']
            )
            
            return True
        else:
            # Registrar tentativa falhada
            rate_limiter.record_attempt(success=False)
            
            # Log de tentativa falhada
            from utils.logging import log_action
            log_action(
                "login_failed", 
                f"Tentativa de login falhada para usuário: {username}"
            )
            return False
    
    def logout_user(self):
        """Fazer logout do usuário com novo sistema de logging"""
        if st.session_state.authenticated and st.session_state.user_data:
            user = st.session_state.user_data
            
            # Log de logout com novo sistema
            from utils.logging import log_action
            log_action(
                "logout", 
                f"Logout do usuário: {user['usuario']}",
                user_id=user['id']
            )
        
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
        Verificar se usuário está autenticado e sessão não expirou
        
        Returns:
            True se autenticado e sessão válida, False caso contrário
        """
        if not st.session_state.get('authenticated', False) or not st.session_state.get('user_data'):
            return False
        
        # Verificar timeout de sessão (30 minutos)
        login_time = st.session_state.get('login_time')
        if not login_time:
            return False
        
        # Calcular tempo desde login
        now = datetime.now()
        time_diff = now - login_time
        
        # Timeout de 30 minutos
        SESSION_TIMEOUT = timedelta(minutes=30)
        
        if time_diff > SESSION_TIMEOUT:
            # Sessão expirou - fazer logout automático
            user = st.session_state.get('user_data')  # Acessar diretamente para evitar recursão
            if user:
                from utils.logging import log_action
                log_action(
                    "session_timeout", 
                    f"Sessão expirada para usuário: {user['usuario']} (duração: {time_diff})",
                    user_id=user['id']
                )
            
            # Limpar sessão
            self.logout_user()
            return False
        
        # Atualizar último acesso para atividade recente
        st.session_state.last_activity = now
        
        return True
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Obter dados do usuário atual
        
        Returns:
            Dados do usuário ou None se não autenticado
        """
        if self.is_authenticated():
            return st.session_state.get('user_data')
        return None
    
    def get_user_role(self) -> str:
        """
        Obter role do usuário atual
        
        Returns:
            Role do usuário ('admin', 'usuario', 'visualizador')
        """
        user = self.get_current_user()
        if user:
            return user.get('role', 'usuario')
        return 'guest'
    
    def has_permission(self, required_role: str) -> bool:
        """
        Verificar se usuário tem permissão para ação
        
        Args:
            required_role: Role mínima necessária
            
        Returns:
            True se tem permissão, False caso contrário
        """
        role_hierarchy = {
            'guest': 0,
            'visualizador': 1,
            'usuario': 2,
            'admin': 3
        }
        
        current_role = self.get_user_role()
        
        return role_hierarchy.get(current_role, 0) >= role_hierarchy.get(required_role, 0)
    
    def require_role(self, required_role: str) -> bool:
        """
        Verificar se usuário tem role necessário, bloquear se não tiver
        
        Args:
            required_role: Role mínima necessária
            
        Returns:
            True se tem permissão, False e mostra erro se não tiver
        """
        if not self.is_authenticated():
            st.error("🔒 Você precisa fazer login para acessar esta funcionalidade.")
            return False
        
        if not self.has_permission(required_role):
            current_role = self.get_user_role()
            st.error(f"⛔ Acesso negado. Seu nível de acesso ({current_role}) é insuficiente. Necessário: {required_role}")
            return False
        
        return True
    
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
                INSERT INTO logs_sistema (user_id, action, details, timestamp)
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
                INSERT INTO logs_sistema (user_id, action, details, timestamp)
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
        """Página de login - REDESIGN COMPLETO"""
        
        # CSS COMPLETAMENTE NOVO - Baseado no exemplo fornecido
        st.markdown("""
        <style>
            /* Ocultar elementos do Streamlit */
            #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {
                display: none !important;
            }
            
            /* Fundo gradiente suave */
            [data-testid="stApp"] {
                background: linear-gradient(135deg, #E8F0FE 0%, #C5DBFF 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            /* Remover TODOS os containers e paddings do Streamlit */
            [data-testid="stVerticalBlock"],
            [data-testid="block-container"],
            .main .block-container,
            section[data-testid="stSidebar"] {
                background: transparent !important;
                padding: 0 !important;
                max-width: none !important;
            }
            
            /* FORÇAR container principal a centralizar */
            .main > div:first-child {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                min-height: 100vh !important;
                padding: 20px !important;
            }
            
            /* Card de login - TAMANHO FIXO E CENTRALIZADO */
            .login-container {
                max-width: 480px !important;
                width: 480px !important;
                margin: 0 auto !important;
                background: #FFFFFF !important;
                border-radius: 12px !important;
                padding: 40px 50px !important;
                box-shadow: 0 4px 20px rgba(79, 142, 247, 0.15) !important;
            }
            
            /* Título principal */
            .login-container h1 {
                font-size: 26px !important;
                font-weight: 700 !important;
                color: #5B7FE8 !important;
                text-align: center !important;
                margin: 0 0 8px 0 !important;
            }
            
            /* Subtítulo */
            .login-container .subtitle {
                font-size: 14px !important;
                color: #6B7280 !important;
                text-align: center !important;
                margin: 0 0 32px 0 !important;
            }
            
            /* Labels dos campos */
            [data-testid="stForm"] label,
            .field-label {
                font-size: 14px !important;
                font-weight: 600 !important;
                color: #374151 !important;
                margin: 0 0 6px 0 !important;
                display: block !important;
                text-align: left !important;
            }
            
            /* Ocultar labels padrão do Streamlit */
            [data-testid="stForm"] [data-testid="stWidgetLabel"] {
                display: none !important;
            }
            
            /* INPUTS - Estilo moderno e compacto */
            [data-testid="stForm"] input[type="text"],
            [data-testid="stForm"] input[type="password"] {
                width: 100% !important;
                height: 44px !important;
                padding: 10px 14px !important;
                font-size: 14px !important;
                border: 1px solid #D1D5DB !important;
                border-radius: 6px !important;
                background: #FFFFFF !important;
                color: #374151 !important;
                box-shadow: none !important;
                transition: border-color 0.2s ease !important;
            }
            
            [data-testid="stForm"] input:focus {
                border-color: #5B7FE8 !important;
                outline: none !important;
                box-shadow: 0 0 0 3px rgba(91, 127, 232, 0.1) !important;
            }
            
            [data-testid="stForm"] input::placeholder {
                color: #9CA3AF !important;
            }
            
            /* Container de inputs - espaçamento */
            [data-testid="stForm"] > div > div {
                margin-bottom: 20px !important;
            }
            
            /* BOTÕES - Lado a lado, estilo moderno */
            [data-testid="stForm"] button {
                width: 100% !important;
                height: 44px !important;
                padding: 0 24px !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                border-radius: 6px !important;
                border: none !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                line-height: 44px !important;
            }
            
            /* Botão primário (Entrar) */
            [data-testid="stForm"] button[kind="primary"] {
                background: #5B7FE8 !important;
                color: #FFFFFF !important;
            }
            
            [data-testid="stForm"] button[kind="primary"]:hover {
                background: #4A6AD6 !important;
                box-shadow: 0 4px 12px rgba(91, 127, 232, 0.3) !important;
            }
            
            /* Botão secundário (Demo) */
            [data-testid="stForm"] button[kind="secondary"] {
                background: #F3F4F6 !important;
                color: #374151 !important;
                border: 1px solid #D1D5DB !important;
            }
            
            [data-testid="stForm"] button[kind="secondary"]:hover {
                background: #E5E7EB !important;
            }
            
            /* Container de botões - 2 colunas */
            [data-testid="column"] {
                padding: 0 4px !important;
            }
            
            [data-testid="column"]:first-child {
                padding-left: 0 !important;
            }
            
            [data-testid="column"]:last-child {
                padding-right: 0 !important;
            }
            
            /* Info boxes abaixo do login */
            .info-section {
                max-width: 1000px;
                margin: 40px auto 0;
                padding: 0 20px;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
            }
            
            .info-card {
                background: #FFFFFF;
                padding: 24px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(79, 142, 247, 0.1);
            }
            
            .info-card .icon {
                font-size: 32px;
                margin-bottom: 12px;
            }
            
            .info-card h3 {
                font-size: 16px !important;
                font-weight: 600 !important;
                color: #374151 !important;
                margin: 0 0 8px 0 !important;
            }
            
            .info-card p {
                font-size: 13px !important;
                color: #6B7280 !important;
                line-height: 1.5 !important;
                margin: 0 !important;
            }
            
            /* Responsivo */
            @media (max-width: 768px) {
                .login-container {
                    padding: 30px 24px;
                }
                .info-grid {
                    grid-template-columns: 1fr;
                    gap: 16px;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # LAYOUT COM COLUNAS PARA CENTRALIZAR
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_center:
            # CONTAINER DE LOGIN
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            # Cabeçalho
            st.markdown('<h1>Bem-vindo!</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitle">Faça o login para continuar.</p>', unsafe_allow_html=True)
            
            # FORMULÁRIO
            with st.form("login_form", clear_on_submit=False):
                # Campo Usuário
                st.markdown('<p class="field-label">👤 Usuário</p>', unsafe_allow_html=True)
                username = st.text_input("username", placeholder="Digite seu usuário", label_visibility="collapsed", key="user_input")
                
                # Campo Senha
                st.markdown('<p class="field-label">🔒 Senha</p>', unsafe_allow_html=True)
                password = st.text_input("password", type="password", placeholder="Digite sua senha", label_visibility="collapsed", key="pass_input")
                
                # Espaçamento
                st.markdown('<div style="margin: 24px 0 16px 0;"></div>', unsafe_allow_html=True)
                
                # Botões lado a lado
                col1, col2 = st.columns(2)
                with col1:
                    login_btn = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)
                with col2:
                    demo_btn = st.form_submit_button("🎯 Demo", type="secondary", use_container_width=True)
                
                # Processar login
                if login_btn:
                    if username and password:
                        if self.login_user(username, password):
                            st.success("✅ Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha inválidos!")
                    else:
                        st.warning("⚠️ Por favor, preencha todos os campos!")
                
                if demo_btn:
                    if self.login_user("admin", "admin"):
                        st.success("✅ Modo Demo ativado!")
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # INFO BOXES CENTRALIZADAS
        st.markdown("""
        <div class="info-section">
            <div class="info-grid">
                <div class="info-box">
                    <div class="icon">🌐</div>
                    <h3>Sistema Web</h3>
                    <p>✓ Acesso simultâneo<br>✓ Tempo real<br>✓ Multiplataforma</p>
                </div>
                <div class="info-box">
                    <div class="icon">🔒</div>
                    <h3>Segurança</h3>
                    <p>✓ Criptografia<br>✓ Sessões seguras<br>✓ Auditoria completa</p>
                </div>
                <div class="info-box">
                    <div class="icon">💡</div>
                    <h3>Acesso Padrão</h3>
                    <p><strong>Usuário:</strong> admin<br><strong>Senha:</strong> admin</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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