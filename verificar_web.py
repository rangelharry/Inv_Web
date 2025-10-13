#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Verificador de Instalação
Verifica se todos os componentes da versão web estão funcionando
"""

import os
import sys
import importlib.util

def verificar_python():
    """Verificar versão do Python"""
    print("🔍 Verificando Python...")
    versao = sys.version_info
    print(f"   Versão: {versao.major}.{versao.minor}.{versao.micro}")
    
    if versao.major < 3 or (versao.major == 3 and versao.minor < 8):
        print("❌ Python 3.8+ é necessário")
        return False
    
    print("✅ Versão do Python compatível")
    return True

def verificar_modulos_web():
    """Verificar módulos necessários para versão web"""
    print("\n🔍 Verificando módulos web...")
    
    modulos_necessarios = [
        ('streamlit', 'Framework web principal'),
        ('pandas', 'Manipulação de dados'),
        ('plotly', 'Gráficos interativos'),
        ('sqlite3', 'Banco de dados'),
        ('datetime', 'Data e hora'),
        ('hashlib', 'Criptografia')
    ]
    
    falhas = 0
    for modulo, descricao in modulos_necessarios:
        try:
            spec = importlib.util.find_spec(modulo)
            if spec is not None:
                print(f"   ✅ {modulo} - {descricao}")
            else:
                print(f"   ❌ {modulo} - {descricao}")
                falhas += 1
        except Exception as e:
            print(f"   ❌ {modulo} - Erro: {e}")
            falhas += 1
    
    if falhas > 0:
        print(f"\n❌ {falhas} módulos faltando")
        print("💡 Execute: pip install streamlit pandas plotly")
        return False
    
    print("\n✅ Todos os módulos necessários estão disponíveis")
    return True

def verificar_estrutura():
    """Verificar estrutura de arquivos"""
    print("\n🔍 Verificando estrutura do projeto...")
    
    arquivos_necessarios = [
        'app.py',
        'requirements.txt',
        'database/connection.py',
        'utils/auth.py',
        'pages/dashboard.py',
        'pages/equipamentos_eletricos.py',
        '.streamlit/config.toml'
    ]
    
    diretorios_necessarios = [
        'pages/',
        'utils/',
        'database/',
        'static/',
        '.streamlit/'
    ]
    
    # Verificar arquivos
    falhas = 0
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo}")
            falhas += 1
    
    # Verificar diretórios
    for diretorio in diretorios_necessarios:
        if os.path.exists(diretorio):
            print(f"   ✅ {diretorio}")
        else:
            print(f"   ❌ {diretorio}")
            falhas += 1
    
    if falhas > 0:
        print(f"\n❌ {falhas} arquivos/diretórios faltando")
        return False
    
    print("\n✅ Estrutura do projeto completa")
    return True

def verificar_banco():
    """Verificar banco de dados"""
    print("\n🔍 Verificando banco de dados...")
    
    db_path = "database/inventario.db"
    
    if os.path.exists(db_path):
        tamanho = os.path.getsize(db_path)
        print(f"   ✅ Banco encontrado ({tamanho} bytes)")
        
        # Testar conexão
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Testar tabelas principais
            tabelas = ['usuarios', 'equipamentos', 'insumos']
            for tabela in tabelas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"   ✅ Tabela {tabela}: {count} registros")
            
            conn.close()
            print("✅ Banco de dados funcionando")
            return True
            
        except Exception as e:
            print(f"   ❌ Erro no banco: {e}")
            return False
    else:
        print("   ⚠️  Banco não encontrado")
        print("   💡 Copie o banco da versão desktop:")
        print("       copy \"..\\inv\\inventario.db\" \"database\\inventario.db\"")
        return False

def verificar_streamlit():
    """Verificar se Streamlit pode ser executado"""
    print("\n🔍 Verificando Streamlit...")
    
    try:
        import streamlit as st
        print("   ✅ Streamlit importado com sucesso")
        
        # Verificar comandos do Streamlit
        import subprocess
        result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"   ✅ Streamlit CLI: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Erro no Streamlit CLI: {result.stderr}")
            return False
            
    except ImportError:
        print("   ❌ Streamlit não instalado")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def gerar_relatorio():
    """Gerar relatório final"""
    print("\n" + "="*60)
    print("                 RELATÓRIO DE VERIFICAÇÃO")
    print("="*60)
    
    verificacoes = [
        ("Python", verificar_python()),
        ("Módulos Web", verificar_modulos_web()),
        ("Estrutura", verificar_estrutura()),
        ("Banco de Dados", verificar_banco()),
        ("Streamlit", verificar_streamlit())
    ]
    
    sucessos = sum(1 for _, resultado in verificacoes if resultado)
    total = len(verificacoes)
    
    print(f"\n📊 RESUMO:")
    for nome, resultado in verificacoes:
        status = "✅ OK" if resultado else "❌ ERRO"
        print(f"   {nome:<15} {status}")
    
    print(f"\n📈 RESULTADO: {sucessos}/{total} verificações passaram")
    
    if sucessos == total:
        print("\n🎉 SISTEMA WEB PRONTO PARA EXECUÇÃO!")
        print("\n📋 Para iniciar:")
        print("   1. Execute: instalar_web.bat (se ainda não executou)")
        print("   2. Execute: executar_web.bat")
        print("   3. Acesse: http://localhost:8501")
        print("   4. Login: admin / 123456")
        print("\n🌐 Para acesso online:")
        print("   - Deploy no Streamlit Cloud (gratuito)")
        print("   - Veja README.md para instruções")
        return True
    else:
        falhas = total - sucessos
        print(f"\n⚠️  {falhas} problemas encontrados")
        print("\n💡 SOLUÇÕES:")
        
        for nome, resultado in verificacoes:
            if not resultado:
                if nome == "Módulos Web":
                    print("   • Execute: pip install streamlit pandas plotly")
                elif nome == "Estrutura":
                    print("   • Verifique se está na pasta Inv_Web")
                    print("   • Execute instalar_web.bat para criar arquivos")
                elif nome == "Banco de Dados":
                    print("   • Copie banco da versão desktop:")
                    print("     copy \"..\\inv\\inventario.db\" \"database\\inventario.db\"")
                elif nome == "Streamlit":
                    print("   • Reinstale: pip uninstall streamlit && pip install streamlit")
        
        print("\n🔄 Execute este script novamente após correções")
        return False

def main():
    """Função principal"""
    print("="*60)
    print("         VERIFICAÇÃO - SISTEMA DE INVENTÁRIO WEB")
    print("="*60)
    print("🌐 Verificando se a versão web está pronta para uso")
    print()
    
    try:
        sucesso = gerar_relatorio()
        return 0 if sucesso else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificação interrompida pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())