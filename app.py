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
        - Obras e Projetos
        - Movimentações e Relatórios
        
        **Desenvolvido com Streamlit**
        """
    }
)

# CSS personalizado
st.markdown("""
<style>
    /* Header personalizado */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sidebar customizada */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Melhorar espaçamento do sidebar */
    .css-1v3fvcr {
        padding-top: 1rem;
    }
    
    /* Botão de sair no sidebar */
    .stSidebar .stButton > button {
        width: 100%;
        margin-top: 0.5rem;
        background-color: #dc3545;
        color: white;
    }
    
    /* Informações do usuário no sidebar */
    .stSidebar .stMarkdown {
        font-size: 0.9rem;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    
    /* Alertas customizados */
    .custom-alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1.25rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    
    .custom-alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem 1.25rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    
    /* Botões personalizados */
    .stButton > button {
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 1px solid #eee;
        margin-top: 3rem;
    }
    
    /* Login container */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Ocultar sidebar quando não logado */
    .css-1d391kg {
        display: none !important;
    }
    
    /* Mostrar sidebar apenas quando logado */
    .user-logged-in .css-1d391kg {
        display: block !important;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
</style>
""", unsafe_allow_html=True)

def show_header():
    """Exibir header da aplicação"""
    st.markdown('<h1 class="main-header fade-in">🏗️ Sistema de Inventário Web</h1>', 
                unsafe_allow_html=True)

def show_user_info():
    """Exibir informações do usuário logado"""
    auth = get_auth()
    user = auth.get_current_user()
    
    if user:
        # Layout simplificado para sidebar
        st.markdown(f"**👤 Usuário:** {user['nome']}")
        
        login_time = st.session_state.get('login_time')
        if login_time:
            time_str = login_time.strftime("%H:%M")
            st.markdown(f"**🕐 Login:** {time_str}")
        
        # Botão de sair em linha separada
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
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
            "⚡ Equipamentos Elétricos": "equipamentos_eletricos", 
            "🔧 Equipamentos Manuais": "equipamentos_manuais",
            "📦 Insumos": "insumos",
            "🏗️ Obras": "obras",
            "📊 Movimentações": "movimentacoes",
            "📈 Relatórios": "relatorios",
            "⚙️ Configurações": "configuracoes"
        }
        
        selected_page = st.selectbox(
            "Selecione uma seção:",
            list(pages.keys()),
            index=0,
            key="navigation_select"
        )
        
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

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Erro crítico na aplicação: {e}")
        st.info("Por favor, recarregue a página ou entre em contato com o suporte.")
        
        # Mostrar detalhes do erro em modo debug
        if st.checkbox("🔍 Mostrar detalhes do erro"):
            st.exception(e)