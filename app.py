#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Aplicação Principal
Versão Streamlit para acesso multiusuário online
"""

import streamlit as st
import os
import sys
from datetime import datetime

# Adicionar pasta utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Imports locais
from database.connection import init_database, get_database
from utils.auth import get_auth
from utils.backup import get_backup_manager
from utils.themes import get_theme_manager
from utils.feedback import get_feedback_manager, NotificationType

# Inicialização robusta do session_state
def init_session_state():
    """Inicializar todas as variáveis de session_state necessárias"""
    # Rate limiting
    if 'rate_limit_data' not in st.session_state:
        st.session_state.rate_limit_data = {}
    
    # Autenticação
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    
    # Feedback e notificações
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'loading_states' not in st.session_state:
        st.session_state.loading_states = {}
    if 'user_actions' not in st.session_state:
        st.session_state.user_actions = []
    
    # Outras variáveis
    if 'selected_theme' not in st.session_state:
        st.session_state.selected_theme = 'default'

# Executar inicialização
init_session_state()

# Configuração dinâmica da página
# Verificar se usuário está logado para configurar sidebar
try:
    from utils.auth import get_auth
    auth = get_auth()
    sidebar_state = "expanded" if auth.is_authenticated() else "collapsed"
except:
    sidebar_state = "collapsed"

st.set_page_config(
    page_title="Sistema de Inventário Web",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state=sidebar_state,
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
        # Sistema de Inventário Web v2.0
        
        Sistema completo para gestão de:
        - Equipamentos Elétricos e Manuais
        - Insumos e Materiais
        - Obra/Departamento
        - Movimentações e Relatórios
        
        **Desenvolvido com Streamlit**
        """
    }
)

# CSS personalizado - Aplicar tema atual
theme_manager = get_theme_manager()
st.markdown(theme_manager.apply_theme_css(), unsafe_allow_html=True)

def show_header():
    """Exibir header da aplicação"""
    feedback_manager = get_feedback_manager()
    
    # Header principal com animação
    st.markdown('<h1 class="main-header fade-in">🏗️ Sistema de Inventário Web</h1>', 
                unsafe_allow_html=True)
    
    # Exibir notificações
    feedback_manager.show_notifications()
    
    # Adicionar breadcrumb de navegação se houver página selecionada
    current_page = st.session_state.get('navigation_select', '🏠 Dashboard')
    if current_page:
        st.markdown(f"""
        <div class="fade-in" style="
            text-align: center; 
            margin-bottom: 1.5rem;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 25px;
            border: 1px solid #dee2e6;
        ">
            <small style="color: #6c757d;">📍 Você está em: <strong>{current_page}</strong></small>
        </div>
        """, unsafe_allow_html=True)

def show_user_info():
    """Exibir informações do usuário logado"""
    auth = get_auth()
    user = auth.get_current_user()
    
    if user:
        # Layout simplificado para sidebar
        st.markdown(f"**👤 Usuário:** {user['nome']}")
        
        login_time = st.session_state.get('login_time')
        if login_time:
            # Calcular tempo de sessão
            now = datetime.now()
            session_duration = now - login_time
            
            # Timeout de 30 minutos
            SESSION_TIMEOUT = 30 * 60  # em segundos
            remaining_seconds = SESSION_TIMEOUT - session_duration.total_seconds()
            
            if remaining_seconds > 0:
                remaining_minutes = int(remaining_seconds // 60)
                remaining_secs = int(remaining_seconds % 60)
                
                # Cor baseada no tempo restante
                if remaining_minutes < 5:
                    color = "🔴"
                elif remaining_minutes < 10:
                    color = "🟡"
                else:
                    color = "🟢"
                
                st.markdown(f"**🕐 Login:** {login_time.strftime('%H:%M')}")
                st.markdown(f"**⏱️ Sessão:** {color} {remaining_minutes:02d}:{remaining_secs:02d}")
                
                # Alerta quando restam menos de 5 minutos
                if remaining_minutes < 5:
                    st.warning(f"⚠️ Sessão expira em {remaining_minutes}min")
            else:
                st.error("🔴 Sessão expirada")
        
        # Botão de sair em linha separada
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            feedback_manager = get_feedback_manager()
            feedback_manager.log_user_action("user_logout")
            feedback_manager.show_notification("👋 Logout realizado com sucesso!", NotificationType.INFO)
            auth.logout_user()
            st.rerun()

def show_navigation():
    """Exibir menu de navegação lateral (apenas para usuários autenticados)"""
    
    # Verificar se usuário está autenticado antes de mostrar navegação
    auth = get_auth()
    if not auth.is_authenticated():
        return None
    
    with st.sidebar:
        st.title("📋 Menu Principal")
        
        # Informações do usuário
        show_user_info()
        
        st.divider()
        
        # Menu de navegação
        pages = {
            "🏠 Dashboard": "dashboard",
            "🚨 Alertas": "alertas",
            "⚡ Equipamentos Elétricos": "equipamentos_eletricos", 
            "🔧 Equipamentos Manuais": "equipamentos_manuais",
            "📦 Insumos": "insumos",
            "🏗️ Obras/Departamentos": "obras",
            "📊 Movimentações": "movimentacoes",
            "📈 Relatórios": "relatorios",
            "⚙️ Configurações": "configuracoes"
        }
        
        # Adicionar página de logs apenas para admins
        if auth.has_permission('admin'):
            pages["📋 Logs de Auditoria"] = "logs_auditoria"
        
        # Seletor de página com feedback
        current_index = 0
        if 'navigation_select' in st.session_state:
            try:
                current_page = st.session_state.navigation_select
                if current_page in pages.keys():
                    current_index = list(pages.keys()).index(current_page)
            except:
                pass
        
        selected_page = st.selectbox(
            "Selecione uma seção:",
            list(pages.keys()),
            index=current_index,
            key="navigation_select"
        )
        
        # Log da navegação
        if selected_page != st.session_state.get('last_page'):
            feedback_manager = get_feedback_manager()
            feedback_manager.log_user_action("navigate", {'page': selected_page})
            st.session_state.last_page = selected_page
        
        st.divider()
        
        # Status do sistema
        st.markdown("### 📊 Status do Sistema")
        
        # Testar conexão com banco
        try:
            db = get_database()
            result = db.execute_query("SELECT COUNT(*) as count FROM usuarios")
            if result:
                st.success("🟢 Banco Online")
            else:
                st.error("🔴 Banco Offline")
        except:
            st.error("🔴 Erro de Conexão")
        
        # Informações adicionais
        st.info(f"""
        **🌐 Versão Web 2.0**
        
        **📅 Data:** {datetime.now().strftime('%d/%m/%Y')}
        
        **🕐 Hora:** {datetime.now().strftime('%H:%M:%S')}
        """)
        
        return pages[selected_page]

def load_page(page_name: str):
    """
    Carregar página selecionada
    
    Args:
        page_name: Nome da página a carregar
    """
    try:
        if page_name == "dashboard":
            from pages import dashboard
            dashboard.show()
        elif page_name == "alertas":
            from pages import alertas
            alertas.show()
        elif page_name == "equipamentos_eletricos":
            from pages import equipamentos_eletricos
            equipamentos_eletricos.show()
        elif page_name == "equipamentos_manuais":
            from pages import equipamentos_manuais
            equipamentos_manuais.show()
        elif page_name == "insumos":
            from pages import insumos
            insumos.show()
        elif page_name == "obras":
            from pages import obras
            obras.show()
        elif page_name == "movimentacoes":
            from pages import movimentacoes
            movimentacoes.show()
        elif page_name == "relatorios":
            from pages import relatorios
            relatorios.show()
        elif page_name == "configuracoes":
            from pages import configuracoes
            configuracoes.show()
        elif page_name == "logs_auditoria":
            from pages import logs_auditoria
            logs_auditoria.show()
        else:
            st.error(f"❌ Página '{page_name}' não encontrada!")
            
    except ImportError as e:
        st.error(f"❌ Erro de importação na página '{page_name}': {e}")
        st.warning("⚠️ Página em desenvolvimento...")
        st.info("Esta funcionalidade será implementada em breve.")
        
        # Mostrar progresso do desenvolvimento
        if page_name == "dashboard":
            st.progress(0.9, "Dashboard - 90% concluído")
        elif page_name in ["equipamentos_eletricos", "insumos"]:
            st.progress(0.7, f"{page_name} - 70% concluído")
        else:
            st.progress(0.3, f"{page_name} - 30% concluído")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar página '{page_name}': {e}")
        st.error(f"Tipo do erro: {type(e).__name__}")
        
        # Mostrar traceback para debug
        import traceback
        st.code(traceback.format_exc(), language="python")

def show_footer():
    """Exibir footer da aplicação"""
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p><strong>Sistema de Inventário Web v2.0</strong></p>
        <p>Desenvolvido com ❤️ usando Streamlit | 2025</p>
        <p>🔒 Dados protegidos • 🌐 Acesso seguro • 📊 Relatórios em tempo real</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Função principal da aplicação"""
    
    # Inicializar banco de dados
    if not init_database():
        st.error("❌ Erro crítico: Não foi possível conectar ao banco de dados!")
        st.stop()
    
    # Sistema de autenticação
    auth = get_auth()
    
    # Verificar se usuário está autenticado
    if not auth.is_authenticated():
        # Limpar sidebar quando não autenticado
        st.sidebar.empty()
        auth.show_login_page()
        return
    
    # Verificar timeout da sessão
    if not auth.check_session_timeout():
        # Limpar sidebar em caso de timeout
        st.sidebar.empty()
        st.warning("⏰ Sua sessão expirou. Faça login novamente.")
        auth.show_login_page()
        return
    
    # Interface principal (apenas após autenticação)
    show_header()
    
    # Menu de navegação e carregamento de página (apenas para usuários logados)
    selected_page = show_navigation()
    
    # Container principal
    if selected_page:
        with st.container():
            load_page(selected_page)
    else:
        st.error("❌ Erro na navegação do sistema")
    
    # Footer
    show_footer()

def init_system():
    """Inicializar sistema e backup automático"""
    try:
        # Executar backup automático na inicialização (uma vez por dia)
        if 'backup_checked' not in st.session_state:
            backup_mgr = get_backup_manager()
            backup_mgr.auto_backup()  # Cria backup se necessário
            st.session_state.backup_checked = True
    except Exception as e:
        # Não falhar a aplicação se backup der erro
        pass

if __name__ == "__main__":
    try:
        # Inicializar sistema
        init_system()
        
        # Executar aplicação principal
        main()
    except Exception as e:
        st.error(f"❌ Erro crítico na aplicação: {e}")
        st.info("Por favor, recarregue a página ou entre em contato com o suporte.")
        
        # Mostrar detalhes do erro em modo debug
        if st.checkbox("🔍 Mostrar detalhes do erro"):
            st.exception(e)