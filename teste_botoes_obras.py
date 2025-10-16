#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se os botões da página de obras foram corrigidos
"""

import os

def verificar_estrutura_obras():
    """Verificar se a página de obras tem a estrutura correta de abas"""
    print("🔍 Verificando estrutura da página de obras...")
    
    arquivo_obras = "pages/obras.py"
    
    if not os.path.exists(arquivo_obras):
        print("❌ Arquivo pages/obras.py não encontrado!")
        return False
    
    with open(arquivo_obras, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se as abas foram implementadas
    elementos_necessarios = [
        'st.tabs(["📋 Listagem", "➕ Cadastrar", "⚙️ Gerenciar"])',
        'with tab_list:',
        'with tab_create:',
        'with tab_manage:',
        'col_actions1, col_actions2, col_actions3 = st.columns(3)',
        '**CRUD Completo**'
    ]
    
    todas_presentes = True
    
    for elemento in elementos_necessarios:
        if elemento in content:
            print(f"✅ Encontrado: '{elemento}'")
        else:
            print(f"❌ Não encontrado: '{elemento}'")
            todas_presentes = False
    
    # Verificar se botões foram simplificados
    botoes_antigos = [
        '"✏️ Editar"',
        '"🗑️ Excluir"'
    ]
    
    botoes_novos = [
        '"✏️"',
        '"🗑️"'
    ]
    
    print("\n🔍 Verificando botões simplificados...")
    
    for botao_antigo in botoes_antigos:
        if botao_antigo in content:
            print(f"⚠️ Botão antigo ainda presente: {botao_antigo}")
        else:
            print(f"✅ Botão antigo removido: {botao_antigo}")
    
    for botao_novo in botoes_novos:
        if botao_novo in content:
            print(f"✅ Botão novo presente: {botao_novo}")
        else:
            print(f"❌ Botão novo não encontrado: {botao_novo}")
    
    if todas_presentes:
        print("\n✅ SUCESSO: Estrutura de abas implementada corretamente!")
        return True
    else:
        print("\n❌ ERRO: Alguns elementos da estrutura estão ausentes!")
        return False

def main():
    """Executar teste"""
    print("🧪 TESTE DOS BOTÕES DA PÁGINA OBRAS")
    print("=" * 50)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar teste
    resultado = verificar_estrutura_obras()
    
    print("\n" + "=" * 50)
    if resultado:
        print("🎉 TESTE PASSOU: Botões corrigidos e estrutura implementada!")
    else:
        print("💥 TESTE FALHOU: Estrutura precisa de ajustes!")

if __name__ == "__main__":
    main()