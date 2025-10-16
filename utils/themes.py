#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Temas Personalizados
Gerencia aparência visual da aplicação
"""

import streamlit as st
from typing import Dict, Any
import json
import os

class ThemeManager:
    """Gerenciador de temas da aplicação"""
    
    def __init__(self):
        """Inicializar gerenciador de temas"""
        self.themes = {
            "default": self._get_default_theme(),
            "dark": self._get_dark_theme(),
            "professional": self._get_professional_theme(),
            "modern": self._get_modern_theme(),
            "high_contrast": self._get_high_contrast_theme()
        }
        
        # Carregar tema salvo ou usar padrão
        self.current_theme = self._load_user_theme()
    
    def _get_default_theme(self) -> Dict[str, Any]:
        """Tema padrão da aplicação"""
        return {
            "name": "Padrão",
            "primary_color": "#1f77b4",
            "secondary_color": "#ff7f0e",
            "success_color": "#2ca02c",
            "warning_color": "#ff7f0e",
            "error_color": "#d62728",
            "background_color": "#ffffff",
            "sidebar_color": "#f8f9fa",
            "text_color": "#333333",
            "border_color": "#dee2e6",
            "card_shadow": "0 2px 4px rgba(0,0,0,0.1)",
            "border_radius": "10px",
            "font_family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }
    
    def _get_dark_theme(self) -> Dict[str, Any]:
        """Tema escuro"""
        return {
            "name": "Escuro",
            "primary_color": "#4dabf7",
            "secondary_color": "#ffc947",
            "success_color": "#51cf66",
            "warning_color": "#ffc947",
            "error_color": "#ff6b6b",
            "background_color": "#1a1a1a",
            "sidebar_color": "#2d2d2d",
            "text_color": "#ffffff",
            "border_color": "#444444",
            "card_shadow": "0 2px 4px rgba(255,255,255,0.1)",
            "border_radius": "10px",
            "font_family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }
    
    def _get_professional_theme(self) -> Dict[str, Any]:
        """Tema profissional"""
        return {
            "name": "Profissional",
            "primary_color": "#2c3e50",
            "secondary_color": "#3498db",
            "success_color": "#27ae60",
            "warning_color": "#f39c12",
            "error_color": "#e74c3c",
            "background_color": "#ecf0f1",
            "sidebar_color": "#34495e",
            "text_color": "#2c3e50",
            "border_color": "#bdc3c7",
            "card_shadow": "0 3px 6px rgba(0,0,0,0.16)",
            "border_radius": "5px",
            "font_family": "'Roboto', 'Arial', sans-serif"
        }
    
    def _get_modern_theme(self) -> Dict[str, Any]:
        """Tema moderno"""
        return {
            "name": "Moderno",
            "primary_color": "#6c5ce7",
            "secondary_color": "#fd79a8",
            "success_color": "#00b894",
            "warning_color": "#fdcb6e",
            "error_color": "#e84393",
            "background_color": "#ffeaa7",
            "sidebar_color": "#ddd",
            "text_color": "#2d3436",
            "border_color": "#74b9ff",
            "card_shadow": "0 4px 8px rgba(0,0,0,0.12)",
            "border_radius": "15px",
            "font_family": "'Inter', 'Segoe UI', sans-serif"
        }
    
    def _get_high_contrast_theme(self) -> Dict[str, Any]:
        """Tema de alto contraste (acessibilidade)"""
        return {
            "name": "Alto Contraste",
            "primary_color": "#000000",
            "secondary_color": "#ffffff",
            "success_color": "#008000",
            "warning_color": "#ffff00",
            "error_color": "#ff0000",
            "background_color": "#ffffff",
            "sidebar_color": "#f0f0f0",
            "text_color": "#000000",
            "border_color": "#000000",
            "card_shadow": "0 2px 4px rgba(0,0,0,0.8)",
            "border_radius": "3px",
            "font_family": "'Arial', sans-serif"
        }
    
    def _load_user_theme(self) -> str:
        """Carregar tema salvo do usuário"""
        try:
            # Verificar se há tema salvo na sessão
            if 'selected_theme' in st.session_state:
                return st.session_state.selected_theme
            
            # Tema padrão
            return "default"
        except:
            return "default"
    
    def set_theme(self, theme_name: str):
        """
        Definir tema atual
        
        Args:
            theme_name: Nome do tema
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
            st.session_state.selected_theme = theme_name
            st.rerun()
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Obter configurações do tema atual"""
        return self.themes.get(self.current_theme, self.themes["default"])
    
    def get_theme_names(self) -> list:
        """Obter lista de nomes de temas disponíveis"""
        return [theme["name"] for theme in self.themes.values()]
    
    def show_theme_selector(self):
        """Exibir seletor de temas"""
        st.subheader("🎨 Personalização Visual")
        
        current_theme_data = self.get_current_theme()
        theme_names = list(self.themes.keys())
        current_index = theme_names.index(self.current_theme)
        
        # Seletor de tema
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_theme = st.selectbox(
                "Escolha um tema:",
                theme_names,
                index=current_index,
                format_func=lambda x: self.themes[x]["name"],
                key="theme_selector"
            )
        
        with col2:
            if st.button("🎨 Aplicar Tema", use_container_width=True):
                self.set_theme(selected_theme)
        
        # Preview do tema
        st.subheader("👁️ Visualização")
        theme_data = self.themes[selected_theme]
        
        # Mostrar cores do tema
        cols = st.columns(5)
        colors = [
            ("Primária", theme_data["primary_color"]),
            ("Secundária", theme_data["secondary_color"]),
            ("Sucesso", theme_data["success_color"]),
            ("Aviso", theme_data["warning_color"]),
            ("Erro", theme_data["error_color"])
        ]
        
        for i, (name, color) in enumerate(colors):
            with cols[i]:
                st.markdown(f"""
                <div style="
                    background-color: {color};
                    height: 50px;
                    border-radius: 5px;
                    margin-bottom: 5px;
                    border: 1px solid #ddd;
                "></div>
                <small><center>{name}</center></small>
                """, unsafe_allow_html=True)
    
    def apply_theme_css(self) -> str:
        """
        Gerar CSS personalizado baseado no tema atual
        
        Returns:
            str: CSS customizado
        """
        theme = self.get_current_theme()
        
        return f"""
        <style>
            /* Reset e base */
            .stApp {{
                font-family: {theme['font_family']};
                background-color: {theme['background_color']};
                color: {theme['text_color']};
            }}
            
            /* Header personalizado */
            .main-header {{
                font-size: 2.8rem;
                color: {theme['primary_color']};
                text-align: center;
                margin-bottom: 2rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                font-weight: 700;
                letter-spacing: -1px;
            }}
            
            /* Sidebar customizada */
            .stSidebar {{
                background: {theme['sidebar_color']};
            }}
            
            .stSidebar .stSelectbox > div > div {{
                background-color: {theme['background_color']};
                border: 2px solid {theme['primary_color']};
                border-radius: {theme['border_radius']};
            }}
            
            /* Botões personalizados */
            .stButton > button {{
                background: {theme['primary_color']};
                color: white;
                border: none;
                border-radius: {theme['border_radius']};
                padding: 0.6rem 1.2rem;
                font-weight: 600;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                box-shadow: {theme['card_shadow']};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
                filter: brightness(1.1);
            }}
            
            .stButton > button:active {{
                transform: translateY(0);
            }}
            
            /* Cards de métricas */
            .metric-card {{
                background: {theme['background_color']};
                padding: 1.8rem;
                border-radius: {theme['border_radius']};
                box-shadow: {theme['card_shadow']};
                border-left: 5px solid {theme['primary_color']};
                margin-bottom: 1.5rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .metric-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: {theme['primary_color']};
            }}
            
            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            
            /* Alertas customizados */
            .stAlert {{
                border-radius: {theme['border_radius']};
                border: none;
                box-shadow: {theme['card_shadow']};
            }}
            
            .stSuccess {{
                background: {theme['success_color']}15;
                border-left: 4px solid {theme['success_color']};
            }}
            
            .stWarning {{
                background: {theme['warning_color']}15;
                border-left: 4px solid {theme['warning_color']};
            }}
            
            .stError {{
                background: {theme['error_color']}15;
                border-left: 4px solid {theme['error_color']};
            }}
            
            .stInfo {{
                background: {theme['primary_color']}15;
                border-left: 4px solid {theme['primary_color']};
            }}
            
            /* Inputs personalizados */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stTextArea > div > div > textarea {{
                border: 2px solid {theme['border_color']};
                border-radius: {theme['border_radius']};
                background-color: {theme['background_color']};
                color: {theme['text_color']};
                font-family: {theme['font_family']};
                transition: all 0.3s ease;
            }}
            
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus,
            .stTextArea > div > div > textarea:focus {{
                border-color: {theme['primary_color']};
                box-shadow: 0 0 10px {theme['primary_color']}30;
            }}
            
            /* Tabelas */
            .stDataFrame {{
                border-radius: {theme['border_radius']};
                overflow: hidden;
                box-shadow: {theme['card_shadow']};
            }}
            
            /* Métricas do Streamlit */
            [data-testid="metric-container"] {{
                background: {theme['background_color']};
                border: 1px solid {theme['border_color']};
                padding: 1rem;
                border-radius: {theme['border_radius']};
                box-shadow: {theme['card_shadow']};
                transition: all 0.3s ease;
            }}
            
            [data-testid="metric-container"]:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            }}
            
            /* Tabs personalizadas */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 24px;
                background-color: {theme['background_color']};
                border-radius: {theme['border_radius']};
                padding: 0.5rem;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                height: 50px;
                background-color: transparent;
                border-radius: {theme['border_radius']};
                color: {theme['text_color']};
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            
            .stTabs [aria-selected="true"] {{
                background: {theme['primary_color']};
                color: white !important;
            }}
            
            /* Footer */
            .footer {{
                text-align: center;
                padding: 2.5rem;
                color: {theme['text_color']}80;
                border-top: 2px solid {theme['border_color']};
                margin-top: 3rem;
                background: {theme['background_color']};
            }}
            
            /* Login container */
            .login-container {{
                max-width: 450px;
                margin: 0 auto;
                padding: 2.5rem;
                background: {theme['background_color']};
                border-radius: {theme['border_radius']};
                box-shadow: {theme['card_shadow']};
                border: 1px solid {theme['border_color']};
            }}
            
            /* Animações */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateX(-30px); }}
                to {{ opacity: 1; transform: translateX(0); }}
            }}
            
            .fade-in {{
                animation: fadeIn 0.6s ease-out;
            }}
            
            .slide-in {{
                animation: slideIn 0.5s ease-out;
            }}
            
            /* Progress bars */
            .stProgress > div > div > div > div {{
                background: {theme['primary_color']};
            }}
            
            /* Expanders */
            .streamlit-expanderHeader {{
                background-color: {theme['sidebar_color']};
                border-radius: {theme['border_radius']};
                border: 1px solid {theme['border_color']};
            }}
            
            /* Scrollbars */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {theme['sidebar_color']};
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {theme['primary_color']};
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {theme['secondary_color']};
            }}
            
            /* Loading spinners */
            .stSpinner > div {{
                border-top-color: {theme['primary_color']} !important;
            }}
            
            /* Data editor */
            .stDataEditor {{
                border-radius: {theme['border_radius']};
                overflow: hidden;
                box-shadow: {theme['card_shadow']};
            }}
            
            /* Charts */
            .js-plotly-plot .plotly {{
                border-radius: {theme['border_radius']};
                box-shadow: {theme['card_shadow']};
            }}
        </style>
        """

# Instância global do gerenciador de temas
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """
    Obter instância global do gerenciador de temas
    
    Returns:
        ThemeManager: Instância do gerenciador
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager