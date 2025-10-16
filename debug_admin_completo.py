#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir o usuário admin atual
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append('.')

from database.connection import get_database
from utils.auth import WebAuth

def verificar_usuario_admin_atual():
    """Verificar o usuário admin no banco e suas permissões"""
    print("🔍 VERIFICAÇÃO DO USUÁRIO ADMIN")
    print("=" * 50)
    
    try:
        db = get_database()
        
        # Buscar todos os usuários
        print("1. Buscando todos os usuários...")
        usuarios = db.execute_query("SELECT * FROM usuarios ORDER BY id")
        
        if usuarios:
            print(f"   ✅ Encontrados {len(usuarios)} usuários:")
            for user in usuarios:
                print(f"      - ID: {user.get('id')}")
                print(f"        Usuário: {user.get('usuario')}")
                print(f"        Nome: {user.get('nome')}")
                print(f"        Role: {user.get('role')}")
                print(f"        Ativo: {user.get('ativo')}")
                print("      ---")
        else:
            print("   ❌ Nenhum usuário encontrado!")
            return False
        
        # Verificar especificamente o usuário admin
        print("2. Verificando usuário admin...")
        admin = db.execute_query("SELECT * FROM usuarios WHERE usuario = 'admin'")
        
        if admin:
            admin_user = admin[0]
            print("   ✅ Usuário admin encontrado:")
            print(f"      - ID: {admin_user.get('id')}")
            print(f"      - Nome: {admin_user.get('nome')}")
            print(f"      - Role: {admin_user.get('role')}")
            print(f"      - Ativo: {admin_user.get('ativo')}")
            
            # Verificar se role é admin
            if admin_user.get('role') != 'admin':
                print("   ⚠️ Role não é 'admin', corrigindo...")
                success = db.execute_update("UPDATE usuarios SET role = 'admin' WHERE usuario = 'admin'")
                if success:
                    print("   ✅ Role corrigida para 'admin'!")
                else:
                    print("   ❌ Erro ao corrigir role!")
            
            # Verificar se está ativo
            if not admin_user.get('ativo'):
                print("   ⚠️ Usuário não está ativo, corrigindo...")
                success = db.execute_update("UPDATE usuarios SET ativo = 1 WHERE usuario = 'admin'")
                if success:
                    print("   ✅ Usuário ativado!")
                else:
                    print("   ❌ Erro ao ativar usuário!")
        else:
            print("   ❌ Usuário admin não encontrado!")
            
            # Criar usuário admin
            print("3. Criando usuário admin...")
            auth = WebAuth()
            senha_hash = auth.hash_password("admin123")
            
            success = db.execute_update("""
                INSERT INTO usuarios (usuario, nome, senha, role, ativo)
                VALUES ('admin', 'Administrador', ?, 'admin', 1)
            """, (senha_hash,))
            
            if success:
                print("   ✅ Usuário admin criado!")
            else:
                print("   ❌ Erro ao criar usuário admin!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_login_admin():
    """Testar se é possível fazer login com admin"""
    print("\n🔐 TESTE DE LOGIN ADMIN")
    print("=" * 50)
    
    try:
        auth = WebAuth()
        
        print("1. Tentando login como admin...")
        
        # Simular login (sem interface Streamlit)
        db = get_database()
        user_data = db.execute_query("SELECT * FROM usuarios WHERE usuario = 'admin' AND ativo = 1")
        
        if user_data:
            user = user_data[0]
            print("   ✅ Usuário encontrado para login:")
            print(f"      - Role: {user.get('role')}")
            print(f"      - Senha armazenada: {'Sim' if user.get('senha') else 'Não'}")
            
            # Verificar senha
            if auth.verify_password("admin123", user.get('senha', '')):
                print("   ✅ Senha válida!")
                
                # Verificar permissões
                if user.get('role') == 'admin':
                    print("   ✅ Usuário tem permissões de admin!")
                    return True
                else:
                    print(f"   ❌ Role incorreta: {user.get('role')}")
                    return False
            else:
                print("   ❌ Senha inválida!")
                return False
        else:
            print("   ❌ Usuário não encontrado ou inativo!")
            return False
        
    except Exception as e:
        print(f"❌ Erro durante teste de login: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar verificações"""
    print("🧪 VERIFICAÇÃO COMPLETA DO USUÁRIO ADMIN")
    print("=" * 60)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar verificações
    usuario_ok = verificar_usuario_admin_atual()
    login_ok = testar_login_admin() if usuario_ok else False
    
    print("\n" + "=" * 60)
    if usuario_ok and login_ok:
        print("🎉 TUDO OK: Usuário admin configurado corretamente!")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Acesse http://localhost:8545")
        print("   2. Faça login com: admin / admin123")
        print("   3. Vá em Configurações → aba 'Usuários'")
        print("   4. Agora você deve conseguir gerenciar usuários!")
    else:
        print("💥 PROBLEMAS ENCONTRADOS!")
        print("   Corrija os problemas acima antes de continuar.")

if __name__ == "__main__":
    main()