#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuário admin padrão no sistema
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append('.')

from database.connection import get_database
from utils.auth import WebAuth

def criar_usuario_admin():
    """Criar usuário admin padrão se não existir"""
    print("🔧 CRIAÇÃO DE USUÁRIO ADMIN PADRÃO")
    print("=" * 50)
    
    try:
        db = get_database()
        
        # Verificar se já existe admin
        print("1. Verificando usuários admin existentes...")
        admins = db.execute_query("SELECT * FROM usuarios WHERE role = 'admin'")
        
        if admins:
            print(f"   ✅ Já existem {len(admins)} administradores no sistema:")
            for admin in admins:
                print(f"      - {admin['usuario']} ({admin['nome']})")
            return True
        
        print("   ⚠️ Nenhum administrador encontrado. Criando admin padrão...")
        
        # Criar usuário admin
        auth = WebAuth()
        senha_admin = "admin123"
        senha_hash = auth.hash_password(senha_admin)
        
        # Inserir admin padrão
        success = db.execute_update("""
            INSERT OR REPLACE INTO usuarios (id, usuario, nome, senha, role, ativo)
            VALUES (1, 'admin', 'Administrador do Sistema', ?, 'admin', 1)
        """, (senha_hash,))
        
        if success:
            print("   ✅ Usuário admin criado com sucesso!")
            print("   📋 Credenciais:")
            print("      - Usuário: admin")
            print("      - Senha: admin123")
            print("   ⚠️ Altere a senha após o primeiro login!")
            return True
        else:
            print("   ❌ Erro ao criar usuário admin!")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante criação: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_estrutura_usuarios():
    """Verificar e criar estrutura da tabela usuarios se necessário"""
    print("\n🔧 VERIFICAÇÃO DA ESTRUTURA DA TABELA")
    print("=" * 50)
    
    try:
        db = get_database()
        
        # Verificar se tabela existe
        print("1. Verificando se tabela usuarios existe...")
        tabelas = db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        
        if not tabelas:
            print("   ⚠️ Tabela usuarios não existe. Criando...")
            
            # Criar tabela usuarios
            success = db.execute_update("""
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    senha TEXT NOT NULL,
                    role TEXT DEFAULT 'usuario',
                    ativo INTEGER DEFAULT 1,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            if success:
                print("   ✅ Tabela usuarios criada com sucesso!")
            else:
                print("   ❌ Erro ao criar tabela usuarios!")
                return False
        else:
            print("   ✅ Tabela usuarios já existe!")
            
        # Verificar estrutura
        print("2. Verificando estrutura da tabela...")
        colunas = db.execute_query("PRAGMA table_info(usuarios)")
        print("   📋 Colunas encontradas:")
        for col in colunas:
            print(f"      - {col['name']} ({col['type']})")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar configuração inicial"""
    print("🚀 CONFIGURAÇÃO INICIAL DO SISTEMA DE USUÁRIOS")
    print("=" * 60)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar configuração
    estrutura_ok = verificar_estrutura_usuarios()
    admin_ok = criar_usuario_admin() if estrutura_ok else False
    
    print("\n" + "=" * 60)
    if estrutura_ok and admin_ok:
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Acesse o sistema em http://localhost:8545")
        print("   2. Faça login com: admin / admin123")
        print("   3. Vá em Configurações > Gerenciamento de Usuários")
        print("   4. Altere a senha padrão do admin")
        print("   5. Crie outros usuários conforme necessário")
    else:
        print("💥 PROBLEMAS NA CONFIGURAÇÃO!")
        print("   Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
    main()