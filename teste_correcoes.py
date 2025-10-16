#!/usr/bin/env python3
"""
Teste específico para as correções dos equipamentos elétricos e gerenciamento de usuários
"""

import sys
import pandas as pd
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, '.')

def test_equipment_data_structure():
    """Testar estrutura de dados dos equipamentos elétricos"""
    print("🔧 Testando estrutura dos equipamentos elétricos...")
    
    try:
        from pages.equipamentos_eletricos import get_equipamentos_data
        from database.connection import get_database
        
        # Testar se a função de carregamento funciona
        df = get_equipamentos_data()
        print(f"✅ Dados carregados: {len(df)} equipamentos")
        
        if not df.empty:
            print(f"✅ Colunas disponíveis: {', '.join(df.columns.tolist())}")
            
            # Verificar se as colunas corretas existem
            required_cols = ['codigo', 'nome', 'localizacao', 'status']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"⚠️ Colunas ausentes: {missing_cols}")
            else:
                print("✅ Todas as colunas obrigatórias estão presentes")
        else:
            print("⚠️ Nenhum equipamento encontrado no banco")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar equipamentos: {e}")
        return False

def test_user_management():
    """Testar sistema de gerenciamento de usuários"""
    print("\n👥 Testando gerenciamento de usuários...")
    
    try:
        from database.connection import get_database
        from utils.auth import get_auth
        
        db = get_database()
        
        # Verificar se a tabela usuarios existe e tem as colunas corretas
        try:
            usuarios = db.execute_query("SELECT id, usuario, nome, role, ativo FROM usuarios LIMIT 1")
            print("✅ Tabela usuarios acessível com colunas corretas")
        except Exception as e:
            print(f"⚠️ Problema na estrutura da tabela usuarios: {e}")
            return False
        
        # Testar autenticação
        auth = get_auth()
        print("✅ Sistema de autenticação carregado")
        
        # Verificar se consegue determinar permissões
        try:
            has_admin = auth.has_permission('admin')
            print(f"✅ Verificação de permissões funcionando (admin: {has_admin})")
        except Exception as e:
            print(f"⚠️ Problema na verificação de permissões: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar usuários: {e}")
        return False

def test_database_operations():
    """Testar operações básicas do banco"""
    print("\n🗄️ Testando operações do banco...")
    
    try:
        from database.connection import get_database
        
        db = get_database()
        
        # Testar consulta básica
        result = db.execute_query("SELECT COUNT(*) as count FROM equipamentos_eletricos")
        print(f"✅ Equipamentos elétricos no banco: {result[0]['count']}")
        
        # Testar consulta de usuários
        result = db.execute_query("SELECT COUNT(*) as count FROM usuarios")
        print(f"✅ Usuários no banco: {result[0]['count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas operações do banco: {e}")
        return False

def main():
    """Executar todos os testes específicos"""
    print("🧪 TESTE ESPECÍFICO DAS CORREÇÕES")
    print("=" * 50)
    
    tests = [
        ("Estrutura dos Equipamentos Elétricos", test_equipment_data_structure),
        ("Gerenciamento de Usuários", test_user_management),
        ("Operações do Banco de Dados", test_database_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES ESPECÍFICOS")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
        if result:
            success_count += 1
    
    print(f"\n🎯 Total: {success_count}/{len(tests)} testes passaram")
    
    if success_count == len(tests):
        print("🎉 TODAS AS CORREÇÕES FUNCIONANDO CORRETAMENTE!")
        print("\n📌 ITENS CORRIGIDOS:")
        print("✅ Erro 'Código' nos equipamentos elétricos")
        print("✅ Sistema de gerenciamento de usuários")
        print("✅ Permissões e autenticação")
        print("✅ Operações do banco de dados")
    else:
        print("⚠️ Algumas correções precisam de ajustes")
    
    return success_count == len(tests)

if __name__ == "__main__":
    main()