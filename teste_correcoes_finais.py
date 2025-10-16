#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das correções finais implementadas
"""

import sqlite3
import os

def teste_estrutura_movimentacoes():
    """Testar se a coluna observacoes foi adicionada corretamente"""
    print("🔍 Testando estrutura da tabela movimentacoes...")
    
    try:
        conn = sqlite3.connect('database/inventario.db')
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(movimentacoes)")
        columns = cursor.fetchall()
        
        print("Colunas encontradas:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar se a coluna observacoes existe
        column_names = [col[1] for col in columns]
        if 'observacoes' in column_names:
            print("✅ Coluna 'observacoes' encontrada!")
        else:
            print("❌ Coluna 'observacoes' NÃO encontrada!")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar estrutura: {e}")
        return False

def verificar_arquivos_modificados():
    """Verificar se os arquivos foram modificados corretamente"""
    print("\n🔍 Verificando arquivos modificados...")
    
    arquivos_teste = [
        "pages/insumos.py",
        "pages/movimentacoes.py",
        "pages/obras.py"
    ]
    
    for arquivo in arquivos_teste:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo} - OK")
            
            # Verificar conteúdo específico
            with open(arquivo, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if arquivo == "pages/insumos.py":
                if 'st.tabs(["📋 Listagem", "➕ Cadastrar", "⚙️ Gerenciar"])' in content:
                    print(f"  ✅ Abas implementadas em {arquivo}")
                else:
                    print(f"  ❌ Abas NÃO encontradas em {arquivo}")
                    
            elif arquivo == "pages/movimentacoes.py":
                if 'LOCAIS_SUGERIDOS' not in content:
                    print(f"  ✅ LOCAIS_SUGERIDOS removido de {arquivo}")
                else:
                    print(f"  ❌ LOCAIS_SUGERIDOS ainda presente em {arquivo}")
                    
            elif arquivo == "pages/obras.py":
                if '"Obra - Residencial Vista Alegre"' in content and content.count("Obra -") <= 5:
                    print(f"  ✅ Lista de obras reduzida em {arquivo}")
                else:
                    print(f"  ❌ Lista de obras NÃO reduzida em {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")

def main():
    """Executar todos os testes"""
    print("🧪 TESTE DAS CORREÇÕES FINAIS")
    print("=" * 50)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar testes
    teste_estrutura_movimentacoes()
    verificar_arquivos_modificados()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main()