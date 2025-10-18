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
        # Somente tema padrão para manter simplicidade
        self.themes = { "default": self._get_default_theme() }
        self.current_theme = "default"
    
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
            # Sempre usar o default para simplificar
            return "default"
        except:
            return "default"
    
    def set_theme(self, theme_name: str):
        """
        Definir tema atual
        
        Args:
            theme_name: Nome do tema
        """
        # Mantemos apenas o tema default; função é noop
        return
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Obter configurações do tema atual"""
        return self.themes.get(self.current_theme, self.themes["default"])
    
    def get_theme_names(self) -> list:
        """Obter lista de nomes de temas disponíveis"""
        return [self.themes['default']['name']]
    
    def show_theme_selector(self):
        # Seletor desativado: mantemos apenas o tema unico
        st.info("A aplicação usa um único estilo visual consistente.")
    
    def apply_theme_css(self) -> str:
        """
        Gerar CSS personalizado baseado no tema atual
        
        Returns:
            str: CSS customizado (vazio - usamos apenas global_css)
        """
        # Não aplicar CSS adicional - o global_css.py já cuida de tudo
        return ""

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