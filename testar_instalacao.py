#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Validação de Instalação
Sistema de Inventário Web

Este script testa se todas as dependências estão instaladas corretamente
e se o sistema pode inicializar sem erros.
"""

import sys
import importlib
import traceback

def testar_dependencia(nome_modulo, nome_exibicao=None):
    """Testa se um módulo pode ser importado"""
    if nome_exibicao is None:
        nome_exibicao = nome_modulo
    
    try:
        importlib.import_module(nome_modulo)
        print(f"✅ {nome_exibicao} - OK")
        return True
    except ImportError as e:
        print(f"❌ {nome_exibicao} - ERRO: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {nome_exibicao} - AVISO: {e}")
        return True

def main():
    """Função principal de teste"""
    print("🔍 TESTE DE VALIDAÇÃO DE INSTALAÇÃO")
    print("=" * 60)
    print(f"🐍 Python: {sys.version}")
    print("=" * 60)
    
    # Lista de dependências essenciais
    dependencias_essenciais = [
        ("streamlit", "Streamlit (Framework Web)"),
        ("pandas", "Pandas (Manipulação de Dados)"),
        ("numpy", "NumPy (Computação Numérica)"),
        ("plotly", "Plotly (Gráficos Interativos)"),
        ("dateutil", "Python-dateutil (Formatação de Datas)"),
        ("PIL", "Pillow (Processamento de Imagens)")
    ]
    
    # Lista de dependências opcionais
    dependencias_opcionais = [
        ("streamlit_authenticator", "Streamlit Authenticator"),
        ("streamlit_option_menu", "Streamlit Option Menu"),
        ("streamlit_aggrid", "Streamlit AgGrid")
    ]
    
    # Lista de módulos do sistema
    modulos_sistema = [
        ("sqlite3", "SQLite3 (Banco de Dados)"),
        ("os", "OS (Sistema Operacional)"),
        ("datetime", "DateTime (Data e Hora)"),
        ("json", "JSON (Serialização)")
    ]
    
    print("\n📦 TESTANDO DEPENDÊNCIAS ESSENCIAIS:")
    print("-" * 40)
    essenciais_ok = 0
    for modulo, nome in dependencias_essenciais:
        if testar_dependencia(modulo, nome):
            essenciais_ok += 1
    
    print(f"\n✅ Dependências essenciais: {essenciais_ok}/{len(dependencias_essenciais)}")
    
    print("\n📦 TESTANDO DEPENDÊNCIAS OPCIONAIS:")
    print("-" * 40)
    opcionais_ok = 0
    for modulo, nome in dependencias_opcionais:
        if testar_dependencia(modulo, nome):
            opcionais_ok += 1
    
    print(f"\n✅ Dependências opcionais: {opcionais_ok}/{len(dependencias_opcionais)}")
    
    print("\n🔧 TESTANDO MÓDULOS DO SISTEMA:")
    print("-" * 40)
    sistema_ok = 0
    for modulo, nome in modulos_sistema:
        if testar_dependencia(modulo, nome):
            sistema_ok += 1
    
    print(f"\n✅ Módulos do sistema: {sistema_ok}/{len(modulos_sistema)}")
    
    # Teste específico do Streamlit
    print("\n🌐 TESTANDO STREAMLIT:")
    print("-" * 40)
    try:
        import streamlit as st
        print(f"✅ Streamlit versão: {st.__version__}")
        
        # Testar comandos básicos do Streamlit
        from streamlit.web import cli as stcli
        print("✅ Streamlit CLI disponível")
        
    except Exception as e:
        print(f"❌ Erro no teste do Streamlit: {e}")
    
    # Teste de conexão com banco
    print("\n🗄️ TESTANDO BANCO DE DADOS:")
    print("-" * 40)
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('SELECT sqlite_version()')
        versao = cursor.fetchone()[0]
        conn.close()
        print(f"✅ SQLite versão: {versao}")
    except Exception as e:
        print(f"❌ Erro no teste do SQLite: {e}")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VALIDAÇÃO:")
    print("=" * 60)
    
    total_essenciais = len(dependencias_essenciais)
    total_sistema = len(modulos_sistema)
    
    if essenciais_ok == total_essenciais and sistema_ok == total_sistema:
        print("🎉 INSTALAÇÃO VÁLIDA - Sistema pronto para uso!")
        print("\n📋 Para iniciar o sistema:")
        print("   Windows: executar_web.bat")
        print("   Manual:  streamlit run app.py")
        return True
    else:
        print("⚠️  INSTALAÇÃO INCOMPLETA")
        print(f"   Essenciais: {essenciais_ok}/{total_essenciais}")
        print(f"   Sistema: {sistema_ok}/{total_sistema}")
        print("\n🔧 Execute novamente: instalar_web.bat")
        return False

if __name__ == "__main__":
    try:
        sucesso = main()
        input("\nPressione Enter para continuar...")
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("\n🔍 Stack trace completo:")
        traceback.print_exc()
        input("\nPressione Enter para continuar...")
        sys.exit(1)