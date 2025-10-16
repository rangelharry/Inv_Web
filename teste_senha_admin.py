#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da senha correta do admin
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append('.')

from database.connection import get_database
from utils.auth import WebAuth

def testar_senha_admin():
    """Testar se a senha 321nimda funciona"""
    print("🔐 TESTE DA SENHA ADMIN")
    print("=" * 40)
    
    try:
        db = get_database()
        auth = WebAuth()
        
        # Buscar usuário admin
        user_data = db.execute_query("SELECT * FROM usuarios WHERE usuario = ?", ("admin",))
        
        if user_data:
            user = user_data[0]
            print(f"✅ Usuário encontrado: {user.get('usuario')}")
            print(f"   Role: {user.get('role')}")
            print(f"   Ativo: {user.get('ativo')}")
            
            # Testar senha 321nimda
            if auth.verify_password("321nimda", user.get('senha', '')):
                print("✅ Senha '321nimda' está CORRETA!")
                return True
            else:
                print("❌ Senha '321nimda' NÃO confere!")
                print(f"   Hash armazenado: {user.get('senha', '')[:20]}...")
                return False
        else:
            print("❌ Usuário admin não encontrado!")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    testar_senha_admin()