#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se a seção de locais pré-cadastrados foi removida
"""

import os

def verificar_remocao_locais_pre_cadastrados():
    """Verificar se a seção foi removida da página de obras"""
    print("🔍 Verificando remoção da seção de locais pré-cadastrados...")
    
    arquivo_obras = "pages/obras.py"
    
    if not os.path.exists(arquivo_obras):
        print("❌ Arquivo pages/obras.py não encontrado!")
        return False
    
    with open(arquivo_obras, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se as strings da seção foram removidas
    strings_removidas = [
        "Locais/Departamentos Pré-Cadastrados",
        "Sugestões de locais para movimentações",
        "Use estes locais nas movimentações",
        "Obras/Projetos:",
        "Departamentos:",
        "Outros Locais:"
    ]
    
    todas_removidas = True
    
    for string in strings_removidas:
        if string in content:
            print(f"❌ String ainda presente: '{string}'")
            todas_removidas = False
        else:
            print(f"✅ String removida: '{string}'")
    
    if todas_removidas:
        print("\n✅ SUCESSO: Toda a seção de locais pré-cadastrados foi removida!")
        return True
    else:
        print("\n❌ ERRO: Algumas strings da seção ainda estão presentes!")
        return False

def main():
    """Executar teste"""
    print("🧪 TESTE DE REMOÇÃO - LOCAIS PRÉ-CADASTRADOS")
    print("=" * 50)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar teste
    resultado = verificar_remocao_locais_pre_cadastrados()
    
    print("\n" + "=" * 50)
    if resultado:
        print("🎉 TESTE PASSOU: Seção removida com sucesso!")
    else:
        print("💥 TESTE FALHOU: Seção ainda presente!")

if __name__ == "__main__":
    main()