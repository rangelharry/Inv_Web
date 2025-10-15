#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Página de Alertas
Interface principal para o sistema de alertas automáticos
"""

import streamlit as st
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth, check_authentication
from utils.alerts import show_alerts_page

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def show():
    """Função principal da página de Alertas"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    # Mostrar página de alertas
    show_alerts_page()

if __name__ == "__main__":
    show()