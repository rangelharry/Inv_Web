#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar a senha do admin para 321nimda
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append('.')

from database.connection import get_database
from utils.auth import WebAuth

def atualizar_senha_admin():
    """Atualizar senha do admin para 321nimda"""
    print("🔧 ATUALIZAÇÃO DA SENHA ADMIN")
    print("=" * 50)
    
    try:
        db = get_database()
        auth = WebAuth()
        
        print("1. Gerando hash da senha '321nimda'...")
        nova_senha_hash = auth.hash_password("321nimda")
        print(f"   ✅ Hash gerado: {nova_senha_hash[:20]}...")
        
        print("2. Atualizando senha no banco de dados...")
        success = db.execute_update(
            "UPDATE usuarios SET senha = ? WHERE usuario = 'admin'", 
            (nova_senha_hash,)
        )
        
        if success:
            print("   ✅ Senha atualizada com sucesso!")
            
            # Verificar se funcionou
            print("3. Testando nova senha...")
            user_data = db.execute_query("SELECT * FROM usuarios WHERE usuario = ?", ("admin",))
            
            if user_data:
                user = user_data[0]
                if auth.verify_password("321nimda", user.get('senha', '')):
                    print("   ✅ Teste da nova senha: SUCESSO!")
                    return True
                else:
                    print("   ❌ Teste da nova senha: FALHOU!")
                    return False
            else:
                print("   ❌ Usuário não encontrado após atualização!")
                return False
        else:
            print("   ❌ Erro ao atualizar senha!")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante atualização: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar atualização"""
    print("🚀 CONFIGURAÇÃO DA SENHA ADMIN")
    print("=" * 60)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar atualização
    resultado = atualizar_senha_admin()
    
    print("\n" + "=" * 60)
    if resultado:
        print("🎉 SENHA CONFIGURADA COM SUCESSO!")
        print("\n💡 CREDENCIAIS DE ACESSO:")
        print("   👤 Usuário: admin")
        print("   🔑 Senha: 321nimda")
        print("\n🌐 PRÓXIMOS PASSOS:")
        print("   1. Acesse http://localhost:8545")
        print("   2. Faça login com as credenciais acima")
        print("   3. Vá em Configurações → aba 'Usuários' (5ª aba)")
        print("   4. Agora você deve conseguir gerenciar usuários!")
    else:
        print("💥 FALHA NA CONFIGURAÇÃO!")
        print("   Verifique os erros acima.")

if __name__ == "__main__":
    main()