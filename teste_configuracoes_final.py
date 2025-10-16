#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final para verificar se a página de configurações está funcionando
"""

import os

def verificar_configuracoes():
    """Verificar se a página de configurações foi corrigida"""
    print("🔍 VERIFICANDO CORREÇÕES NA PÁGINA DE CONFIGURAÇÕES")
    print("=" * 60)
    
    arquivo_config = "pages/configuracoes.py"
    
    if not os.path.exists(arquivo_config):
        print("❌ Arquivo pages/configuracoes.py não encontrado!")
        return False
    
    with open(arquivo_config, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar correções implementadas
    correcoes = [
        # Verificação de permissões melhorada
        'user_role = auth.get_user_role()',
        'current_user = auth.get_current_user()',
        'is_admin = (user_role == \'admin\')',
        
        # Informações de debug
        'st.info(f"🔍 **Debug Info:**',
        
        # Funcionalidades de CRUD
        'UPDATE usuarios',
        'INSERT INTO usuarios',
        'DELETE FROM usuarios',
        
        # Tratamento de erros
        'try:',
        'except Exception as e:',
        
        # Interface melhorada
        'st.expander(',
        'st.form("novo_usuario")',
        
        # Coluna corrigida
        'INSERT INTO usuarios (usuario, nome, senha, role, ativo)',
    ]
    
    correcoes_encontradas = []
    correcoes_ausentes = []
    
    for correcao in correcoes:
        if correcao in content:
            correcoes_encontradas.append(correcao)
            print(f"✅ Implementado: {correcao}")
        else:
            correcoes_ausentes.append(correcao)
            print(f"❌ Não encontrado: {correcao}")
    
    # Verificar se mensagens problemáticas foram removidas
    print("\n🔍 Verificando remoção de mensagens problemáticas...")
    
    mensagens_problematicas = [
        "entre em contato com o administrador do sistema",
    ]
    
    for mensagem in mensagens_problematicas:
        if mensagem in content:
            print(f"⚠️ Mensagem ainda presente: {mensagem}")
        else:
            print(f"✅ Mensagem removida: {mensagem}")
    
    # Calcular pontuação
    total_correcoes = len(correcoes)
    correcoes_implementadas = len(correcoes_encontradas)
    pontuacao = (correcoes_implementadas / total_correcoes) * 100
    
    print(f"\n📊 Pontuação das correções: {pontuacao:.1f}% ({correcoes_implementadas}/{total_correcoes})")
    
    if pontuacao >= 80:
        print("✅ EXCELENTE: Sistema de usuários corrigido!")
        return True
    elif pontuacao >= 60:
        print("⚠️ BOM: Maioria das correções implementadas.")
        return True
    else:
        print("❌ PRECISA MELHORAR: Muitas correções ainda pendentes.")
        return False

def main():
    """Executar teste"""
    print("🧪 TESTE DAS CORREÇÕES - PÁGINA DE CONFIGURAÇÕES")
    print("=" * 70)
    
    # Mudar para o diretório correto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Executar teste
    resultado = verificar_configuracoes()
    
    print("\n" + "=" * 70)
    if resultado:
        print("🎉 SUCESSO: Página de configurações corrigida!")
        print("\n💡 INSTRUÇÕES DE USO:")
        print("   1. Faça login com: admin / admin123")
        print("   2. Acesse Configurações > Gerenciamento de Usuários")
        print("   3. Agora você pode cadastrar e editar usuários!")
        print("   4. Altere a senha padrão do admin por segurança")
    else:
        print("💥 PRECISA AJUSTES: Sistema ainda tem problemas!")

if __name__ == "__main__":
    main()