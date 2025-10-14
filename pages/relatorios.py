#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Relatórios
Página de relatórios e análises
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pages import show_relatorios
from utils.auth import get_auth

# Verificar autenticação quando acessado diretamente
auth = get_auth()
if not auth.is_authenticated():
    auth.show_login_page()
else:
    show_relatorios()

# Para compatibilidade com o sistema de navegação do app.py
show = show_relatorios