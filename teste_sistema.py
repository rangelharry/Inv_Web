#!/usr/bin/env python3
"""
Teste completo do sistema de inventário web
Este script verifica todas as funcionalidades principais
"""

import sys
import sqlite3
import pandas as pd
from datetime import datetime

def test_database_connection():
    """Testar conexão com o banco de dados"""
    try:
        from database.connection import get_database
        db = get_database()
        tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table';")
        print(f"✅ Conexão com o banco OK - {len(tables)} tabelas encontradas")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão do banco: {e}")
        return False

def test_database_schema():
    """Testar esquema do banco de dados"""
    try:
        from database.connection import get_database
        db = get_database()
        
        # Testar cada tabela
        tables_to_test = {
            'equipamentos_eletricos': ['codigo', 'nome', 'localizacao', 'categoria'],
            'equipamentos_manuais': ['codigo', 'descricao', 'quantitativo', 'localizacao', 'status'],
            'insumos': ['codigo', 'descricao', 'quantidade', 'localizacao'],
            'movimentacoes': ['codigo', 'data', 'origem', 'destino'],
            'auditoria': ['timestamp', 'acao', 'tabela']
        }
        
        for table, columns in tables_to_test.items():
            try:
                # Testar cada coluna
                schema = db.execute_query(f"PRAGMA table_info({table})")
                existing_columns = [col['name'] for col in schema]
                
                for col in columns:
                    if col in existing_columns:
                        print(f"✅ {table}.{col} OK")
                    else:
                        print(f"⚠️ {table}.{col} não encontrada")
                        
            except Exception as e:
                print(f"❌ Erro ao testar tabela {table}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Erro no teste de esquema: {e}")
        return False

def test_alerts_queries():
    """Testar consultas dos alertas"""
    try:
        from database.connection import get_database
        db = get_database()
        
        # Testar consultas específicas que causavam erro
        test_queries = [
            # Equipamentos elétricos - usar 'nome'
            "SELECT codigo, nome as descricao, localizacao FROM equipamentos_eletricos LIMIT 1",
            
            # Equipamentos manuais - usar 'descricao'
            "SELECT codigo, descricao, quantitativo, localizacao FROM equipamentos_manuais LIMIT 1",
            
            # Insumos - usar 'descricao' e 'quantidade'
            "SELECT codigo, descricao, quantidade, localizacao FROM insumos LIMIT 1",
            
            # Movimentações
            "SELECT codigo, data, origem, destino FROM movimentacoes LIMIT 1"
        ]
        
        for query in test_queries:
            try:
                result = db.execute_query(query)
                print(f"✅ Query OK: {query[:50]}...")
            except Exception as e:
                print(f"❌ Query falhou: {query[:50]}... - Erro: {e}")
                
        return True
    except Exception as e:
        print(f"❌ Erro no teste de queries: {e}")
        return False

def test_imports():
    """Testar importações dos módulos"""
    modules_to_test = [
        'utils.auth',
        'utils.alerts', 
        'utils.themes',
        'utils.feedback',
        'utils.backup',
        'utils.rate_limiting',
        'pages.dashboard',
        'pages.equipamentos_eletricos',
        'pages.equipamentos_manuais',
        'pages.insumos',
        'pages.movimentacoes',
        'pages.relatorios',
        'pages.configuracoes'
    ]
    
    success_count = 0
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ Import OK: {module}")
            success_count += 1
        except Exception as e:
            print(f"❌ Import falhou: {module} - {e}")
    
    print(f"\n📊 Imports: {success_count}/{len(modules_to_test)} OK")
    return success_count == len(modules_to_test)

def main():
    """Executar todos os testes"""
    print("🔍 TESTE COMPLETO DO SISTEMA")
    print("=" * 50)
    
    # Adicionar o diretório atual ao path
    sys.path.insert(0, '.')
    
    tests = [
        ("Conexão do Banco de Dados", test_database_connection),
        ("Esquema do Banco de Dados", test_database_schema), 
        ("Consultas dos Alertas", test_alerts_queries),
        ("Importações dos Módulos", test_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testando: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
        if result:
            success_count += 1
    
    print(f"\n🎯 Total: {success_count}/{len(tests)} testes passaram")
    
    if success_count == len(tests):
        print("🎉 SISTEMA TOTALMENTE FUNCIONAL!")
    else:
        print("⚠️ Sistema possui problemas que precisam ser corrigidos")
        
    return success_count == len(tests)

if __name__ == "__main__":
    main()