#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para debugar o problema de permissões na página de configurações
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append('.')

from utils.auth import get_auth
from database.connection import get_database

def testar_permissoes_usuario():
    """Testar as permissões do usuário atual"""
    print("🔍 TESTE DE PERMISSÕES DO USUÁRIO")
    print("=" * 50)
    
    try:
        # Inicializar auth
        print("1. Inicializando sistema de autenticação...")
        auth = get_auth()
        
        # Verificar se está autenticado
        print("2. Verificando autenticação...")
        is_authenticated = auth.is_authenticated()
        print(f"   ✅ Autenticado: {is_authenticated}")
        
        if not is_authenticated:
            print("❌ Usuário não está logado!")
            return False
        
        # Obter dados do usuário
        print("3. Obtendo dados do usuário...")
        user_data = auth.get_current_user()
        print(f"   📊 Dados do usuário: {user_data}")
        
        # Obter role do usuário
        print("4. Verificando role do usuário...")
        user_role = auth.get_user_role()
        print(f"   🎭 Role atual: {user_role}")
        
        # Testar permissão admin
        print("5. Testando permissão de admin...")
        has_admin = auth.has_permission('admin')
        print(f"   🔑 Tem permissão admin: {has_admin}")
        
        # Verificar estrutura da tabela usuarios
        print("6. Verificando tabela de usuários...")
        db = get_database()
        usuarios = db.execute_query("SELECT id, usuario, nome, role, ativo FROM usuarios ORDER BY usuario")
        print(f"   👥 Usuários no banco: {len(usuarios) if usuarios else 0}")
        
        if usuarios:
            for user in usuarios:
                print(f"      - {user}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_usuario_admin():
    """Verificar se existe usuário admin no sistema"""
    print("\n🔍 VERIFICANDO USUÁRIO ADMIN")
    print("=" * 50)
    
    try:
        db = get_database()
        
        # Verificar estrutura da tabela
        print("1. Verificando estrutura da tabela usuarios...")
        try:
            colunas = db.execute_query("PRAGMA table_info(usuarios)")
            print("   📋 Colunas da tabela:")
            for col in colunas:
                print(f"      - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"   ❌ Erro ao verificar estrutura: {e}")
        
        # Buscar usuários admin
        print("2. Buscando usuários com role admin...")
        admins = db.execute_query("SELECT * FROM usuarios WHERE role = 'admin'")
        
        if admins:
            print(f"   ✅ Encontrados {len(admins)} administradores:")
            for admin in admins:
                print(f"      - ID: {admin[0]}, Usuário: {admin[1]}, Nome: {admin[2]}, Ativo: {admin[4]}")
        else:
            print("   ❌ Nenhum administrador encontrado!")
            
            # Tentar criar usuário admin
            print("3. Tentando criar usuário admin...")
            from utils.auth import WebAuth
            auth = WebAuth()
            senha_hash = auth.hash_password("admin123")
            
            result = db.execute_update("""
                INSERT OR REPLACE INTO usuarios (id, usuario, nome, role, senha, ativo)
                VALUES (1, 'admin', 'Administrador', 'admin', ?, 1)
            """, (senha_hash,))
            
            if result:
                print("   ✅ Usuário admin criado com sucesso!")
                print("   📝 Login: admin | Senha: admin123")
            else:
                print("   ❌ Erro ao criar usuário admin!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar todos os testes"""
    print("🧪 DIAGNÓSTICO DO SISTEMA DE PERMISSÕES")
    print("=" * 60)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar testes
    teste1 = testar_permissoes_usuario()
    teste2 = verificar_usuario_admin()
    
    print("\n" + "=" * 60)
    if teste1 and teste2:
        print("🎉 DIAGNÓSTICO CONCLUÍDO!")
    else:
        print("💥 PROBLEMAS ENCONTRADOS!")
    
    print("\n💡 SOLUÇÕES SUGERIDAS:")
    print("   1. Faça login com usuário 'admin' e senha 'admin123'")
    print("   2. Verifique se a tabela 'usuarios' existe no banco")
    print("   3. Certifique-se de que o usuário logado tem role 'admin'")

if __name__ == "__main__":
    main()