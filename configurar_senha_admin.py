#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script direto para atualizar senha_hash do admin
"""

import sqlite3
import bcrypt
import os

def atualizar_senha_admin():
    """Atualizar senha_hash do admin diretamente no banco"""
    print("🔧 ATUALIZANDO SENHA_HASH ADMIN DIRETAMENTE")
    print("=" * 50)
    
    try:
        # Caminho do banco
        db_path = "database/inventario.db"
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado: {db_path}")
            return False
        
        print("1. Conectando ao banco de dados...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("2. Verificando usuário admin atual...")
        cursor.execute("SELECT id, usuario, role FROM usuarios WHERE usuario = 'admin'")
        user = cursor.fetchone()
        
        if user:
            print(f"   ✅ Usuário encontrado: ID={user[0]}, Role={user[2]}")
        else:
            print("   ❌ Usuário admin não encontrado!")
            conn.close()
            return False
        
        print("3. Gerando novo hash da senha '321nimda'...")
        senha = "321nimda"
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
        senha_hash_str = senha_hash.decode('utf-8')
        print(f"   ✅ Hash gerado: {senha_hash_str[:30]}...")
        
        print("4. Atualizando senha_hash no banco...")
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE usuario = 'admin'", 
            (senha_hash_str,)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            print("   ✅ Senha_hash atualizada com sucesso!")
            
            # Verificar se funcionou
            print("5. Testando nova senha...")
            cursor.execute("SELECT senha_hash FROM usuarios WHERE usuario = 'admin'")
            stored_hash = cursor.fetchone()[0]
            
            if bcrypt.checkpw(senha.encode('utf-8'), stored_hash.encode('utf-8')):
                print("   ✅ Teste da nova senha: SUCESSO!")
                conn.close()
                return True
            else:
                print("   ❌ Teste da nova senha: FALHOU!")
                conn.close()
                return False
        else:
            print("   ❌ Nenhuma linha atualizada!")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Erro durante atualização: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """Executar atualização"""
    print("🚀 CONFIGURAÇÃO DA SENHA ADMIN")
    print("=" * 60)
    
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
        print("   3. Vá em Configurações → aba '👥 Usuários' (5ª aba)")
        print("   4. Agora você deve conseguir gerenciar usuários!")
        print("\n📝 INSTRUÇÕES DETALHADAS:")
        print("   • Na página de login, digite 'admin' como usuário")
        print("   • Digite '321nimda' como senha")
        print("   • Após login, clique na aba 'Configurações' no menu lateral")
        print("   • Na página de configurações, clique na 5ª aba '👥 Usuários'")
        print("   • Agora você terá acesso completo ao gerenciamento de usuários!")
    else:
        print("💥 FALHA NA CONFIGURAÇÃO!")
        print("   Verifique os erros acima.")

if __name__ == "__main__":
    main()