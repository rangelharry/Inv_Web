#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final para verificar melhorias na página de obras
"""

import os

def verificar_melhorias_obras():
    """Verificar se as melhorias na página de obras foram aplicadas"""
    print("🔍 Verificando melhorias na página de obras...")
    
    arquivo_obras = "pages/obras.py"
    
    if not os.path.exists(arquivo_obras):
        print("❌ Arquivo pages/obras.py não encontrado!")
        return False
    
    with open(arquivo_obras, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar melhorias implementadas
    melhorias = [
        '"✏️ Editar"',  # Botões com texto
        '"🗑️ Excluir"',  # Botões com texto
        'col_edit, col_delete = st.columns(2)',  # Layout de 2 colunas para botões
        'col1, col2, col3, col4 = st.columns([3, 2, 2, 2])',  # Layout principal melhorado
        'st.markdown("---")',  # Separadores
        '**#{row[\'id\']} - {row[\'nome\']}**',  # Formatação melhorada do título
        'with tab_list:',  # Estrutura de abas
        'with tab_create:',
        'with tab_manage:'
    ]
    
    problemas_corrigidos = []
    problemas_pendentes = []
    
    for melhoria in melhorias:
        if melhoria in content:
            problemas_corrigidos.append(melhoria)
            print(f"✅ Implementado: {melhoria}")
        else:
            problemas_pendentes.append(melhoria)
            print(f"❌ Não encontrado: {melhoria}")
    
    # Verificar se estruturas problemáticas foram removidas
    estruturas_antigas = [
        'col_actions1, col_actions2, col_actions3 = st.columns(3)',  # Layout de 3 colunas pequenas
        'st.button("✏️", key=',  # Botões só com ícone
        'st.button("🗑️", key='   # Botões só com ícone
    ]
    
    print("\n🔍 Verificando remoção de estruturas problemáticas...")
    
    for estrutura in estruturas_antigas:
        if estrutura in content:
            print(f"⚠️ Estrutura antiga ainda presente: {estrutura}")
        else:
            print(f"✅ Estrutura antiga removida: {estrutura}")
    
    # Calcular pontuação
    total_melhorias = len(melhorias)
    melhorias_implementadas = len(problemas_corrigidos)
    pontuacao = (melhorias_implementadas / total_melhorias) * 100
    
    print(f"\n📊 Pontuação das melhorias: {pontuacao:.1f}% ({melhorias_implementadas}/{total_melhorias})")
    
    if pontuacao >= 80:
        print("✅ EXCELENTE: Maioria das melhorias implementadas!")
        return True
    elif pontuacao >= 60:
        print("⚠️ BOM: Algumas melhorias implementadas, mas pode ser aprimorado.")
        return True
    else:
        print("❌ PRECISA MELHORAR: Muitas melhorias ainda pendentes.")
        return False

def main():
    """Executar teste"""
    print("🧪 TESTE FINAL - MELHORIAS NA PÁGINA OBRAS")
    print("=" * 60)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar teste
    resultado = verificar_melhorias_obras()
    
    print("\n" + "=" * 60)
    if resultado:
        print("🎉 SUCESSO: Página de obras melhorada!")
    else:
        print("💥 PRECISA AJUSTES: Página ainda tem problemas!")

if __name__ == "__main__":
    main()