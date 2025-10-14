#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Script de Teste
Verificar se todas as dependências e funcionalidades estão funcionando
"""

import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Testar todas as importações necessárias"""
    print("🧪 Testando Importações...")
    
    try:
        import streamlit as st
        print("✅ Streamlit importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Streamlit: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Pandas: {e}")
        return False
    
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly importado com sucesso")
    except ImportError as e:
        print(f"⚠️  Plotly não disponível: {e}")
    
    try:
        from database.connection import get_database
        print("✅ Database connection importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar database connection: {e}")
        return False
    
    try:
        from utils.auth import get_auth
        print("✅ Auth utils importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar auth utils: {e}")
        return False
    
    return True

def test_database():
    """Testar conexão com banco de dados"""
    print("\n🗄️  Testando Banco de Dados...")
    
    try:
        from database.connection import get_database
        db = get_database()
        
        # Testar conexão
        result = db.execute_query("SELECT 1 as test")
        if result and len(result) > 0:
            print("✅ Conexão com banco de dados funcionando")
        else:
            print("❌ Problema na conexão com banco de dados")
            return False
        
        # Testar tabelas principais
        tables = ["usuarios", "equipamentos_eletricos", "equipamentos_manuais", "insumos", "obras"]
        
        for table in tables:
            try:
                result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count'] if result else 0
                print(f"✅ Tabela {table}: {count} registros")
            except Exception as e:
                print(f"❌ Erro na tabela {table}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral no banco de dados: {e}")
        return False

def test_authentication():
    """Testar sistema de autenticação"""
    print("\n🔐 Testando Autenticação...")
    
    try:
        from utils.auth import WebAuth
        
        auth = WebAuth()
        
        # Testar autenticação com dados válidos
        user = auth.authenticate_user("admin", "admin123")
        if user:
            print("✅ Autenticação com admin funcionando")
        else:
            print("❌ Falha na autenticação com admin")
            return False
        
        # Testar autenticação com dados inválidos
        user = auth.authenticate_user("invalid", "invalid")
        if not user:
            print("✅ Rejeição de credenciais inválidas funcionando")
        else:
            print("❌ Sistema não está rejeitando credenciais inválidas")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de autenticação: {e}")
        return False

def test_pages():
    """Testar se todas as páginas podem ser importadas"""
    print("\n📄 Testando Páginas...")
    
    pages = [
        ("Dashboard", "pages.dashboard"),
        ("Equipamentos Elétricos", "pages.equipamentos_eletricos"),
        ("Equipamentos Manuais", "pages.equipamentos_manuais"),
        ("Insumos", "pages.insumos"),
        ("Obras", "pages.obras"),
        ("Movimentações", "pages.movimentacoes"),
        ("Relatórios", "pages.relatorios"),
        ("Configurações", "pages.configuracoes")
    ]
    
    for page_name, module_name in pages:
        try:
            __import__(module_name)
            print(f"✅ {page_name} - importação OK")
        except Exception as e:
            print(f"❌ {page_name} - erro: {e}")
            return False
    
    return True

def main():
    """Executar todos os testes"""
    print("🚀 INICIANDO TESTES DO SISTEMA DE INVENTÁRIO WEB")
    print("=" * 60)
    
    all_passed = True
    
    # Executar testes
    tests = [
        ("Importações", test_imports),
        ("Banco de Dados", test_database),
        ("Autenticação", test_authentication),
        ("Páginas", test_pages)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results[test_name] = False
            all_passed = False
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:20} | {status}")
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        print(f"🌐 URL do sistema: http://localhost:8509")
        print("👤 Login: admin / admin123 ou cinthia / cinthia123")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verificar problemas acima.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()