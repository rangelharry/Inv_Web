#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Página em Desenvolvimento
Template para páginas que ainda serão implementadas
"""

import streamlit as st
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth

def show_development_page(page_name, icon, description, progress=0.3):
    """
    Exibir página em desenvolvimento
    
    Args:
        page_name: Nome da página
        icon: Ícone da página
        description: Descrição da funcionalidade
        progress: Progresso do desenvolvimento (0.0 a 1.0)
    """
    
    # Verificar autenticação
    auth = get_auth()
    auth.require_auth()
    
    st.markdown(f"## {icon} {page_name}")
    st.markdown(description)
    
    st.markdown("---")
    
    # Status de desenvolvimento
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.progress(progress, f"Desenvolvimento: {int(progress*100)}%")
    
    with col2:
        st.metric("Status", "Em Desenvolvimento" if progress < 1.0 else "Concluído")
    
    with col3:
        eta_days = max(1, int((1.0 - progress) * 7))  # Estimativa baseada no progresso
        st.metric("ETA", f"{eta_days} dias" if progress < 1.0 else "Pronto")
    
    st.markdown("---")
    
    # Funcionalidades planejadas
    st.markdown("### 🔧 Funcionalidades Planejadas")
    
    if page_name == "Equipamentos Manuais":
        features = [
            "✅ Listagem de equipamentos manuais",
            "✅ Sistema de busca e filtros",
            "⏳ Formulário de cadastro",
            "⏳ Edição e exclusão",
            "⏳ Controle de estado (Novo, Usado, Danificado)",
            "⏳ Movimentação entre locais",
            "⏳ Relatórios específicos"
        ]
    elif page_name == "Insumos":
        features = [
            "✅ Gestão de estoque",
            "✅ Controle de quantidades",
            "⏳ Alertas de estoque baixo",
            "⏳ Categorização de insumos",
            "⏳ Movimentações de entrada/saída",
            "⏳ Controle de preços",
            "⏳ Relatórios de consumo"
        ]
    elif page_name == "Obras":
        features = [
            "✅ Cadastro de obras e projetos",
            "⏳ Controle de cronograma",
            "⏳ Vinculação com equipamentos",
            "⏳ Acompanhamento de status",
            "⏳ Relatórios de progresso",
            "⏳ Gestão de responsáveis"
        ]
    elif page_name == "Movimentações":
        features = [
            "✅ Registro de movimentações",
            "✅ Histórico completo",
            "⏳ Aprovações de transferência",
            "⏳ Rastreamento em tempo real",
            "⏳ Notificações automáticas",
            "⏳ Relatórios de movimentação"
        ]
    elif page_name == "Relatórios":
        features = [
            "✅ Relatórios básicos",
            "⏳ Gráficos interativos",
            "⏳ Exportação PDF/Excel",
            "⏳ Relatórios personalizados",
            "⏳ Agendamento automático",
            "⏳ Dashboard de KPIs"
        ]
    else:
        features = [
            "⏳ Funcionalidade principal",
            "⏳ Interface de usuário",
            "⏳ Validações de dados",
            "⏳ Integração com banco",
            "⏳ Testes e validação"
        ]
    
    for feature in features:
        st.markdown(f"- {feature}")
    
    st.markdown("---")
    
    # Demonstração ou preview
    if page_name == "Insumos":
        st.markdown("### 📦 Preview - Gestão de Insumos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Insumos", "219", "cadastrados")
        
        with col2:
            st.metric("Estoque Baixo", "175", "alertas", delta_color="inverse")
        
        with col3:
            st.metric("Valor Total", "R$ 39,50", "em estoque")
    
    elif page_name == "Relatórios":
        st.markdown("### 📊 Preview - Relatórios Disponíveis")
        
        reports = [
            {"nome": "Inventário Completo", "status": "✅ Pronto"},
            {"nome": "Equipamentos por Status", "status": "✅ Pronto"},
            {"nome": "Insumos com Estoque Baixo", "status": "✅ Pronto"},
            {"nome": "Movimentações por Período", "status": "⏳ Desenvolvimento"},
            {"nome": "Valor do Inventário", "status": "⏳ Desenvolvimento"},
            {"nome": "Utilização de Equipamentos", "status": "⏳ Planejado"}
        ]
        
        for report in reports:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {report['nome']}")
            with col2:
                st.write(report['status'])
    
    # Informações de contato/suporte
    st.markdown("---")
    st.info("""
    💡 **Sugestões ou dúvidas?**
    
    Esta página está em desenvolvimento ativo. Se você tem sugestões específicas 
    para esta funcionalidade, elas serão bem-vindas para priorizar o desenvolvimento.
    """)
    
    # Botão para voltar ao dashboard
    if st.button("🏠 Voltar ao Dashboard", type="secondary"):
        st.switch_page("app.py")

# Páginas específicas usando o template
def show_equipamentos_manuais():
    show_development_page(
        "Equipamentos Manuais",
        "🔧",
        "Gestão completa de ferramentas e equipamentos manuais",
        0.6
    )

def show_insumos():
    show_development_page(
        "Insumos",
        "📦",
        "Controle de estoque de materiais, insumos e consumíveis",
        0.7
    )

def show_obras():
    show_development_page(
        "Obras",
        "🏗️",
        "Gestão de obras, projetos e contratos",
        0.4
    )

def show_movimentacoes():
    show_development_page(
        "Movimentações",
        "📊",
        "Controle de transferências e movimentação de itens",
        0.5
    )

def show_relatorios():
    show_development_page(
        "Relatórios",
        "📈",
        "Relatórios gerenciais e operacionais",
        0.3
    )

def show_configuracoes():
    show_development_page(
        "Configurações",
        "⚙️",
        "Configurações do sistema e preferências do usuário",
        0.2
    )