#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Configurações
Página de configurações do sistema
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pages import show_configuracoes
from utils.auth import get_auth

# Verificar autenticação quando acessado diretamente
auth = get_auth()
if not auth.is_authenticated():
    auth.show_login_page()
else:
    show_configuracoes()

# Para compatibilidade com o sistema de navegação do app.py
show = show_configuracoes