#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Relatórios
Página de relatórios e análises
"""

import streamlit as st
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.auth import get_auth, check_authentication

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def show():
    """Função principal da página Relatórios"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 📈 Relatórios")
    st.markdown("Relatórios gerenciais e operacionais")
    
    # Seções de relatórios
    tab1, tab2, tab3 = st.tabs(["📊 Inventário", "📋 Movimentações", "💰 Financeiro"])
    
    with tab1:
        st.markdown("### 📊 Relatórios de Inventário")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Inventário Completo", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("⚡ Equipamentos Elétricos", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("🔧 Equipamentos Manuais", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
        
        with col2:
            if st.button("📦 Estoque de Insumos", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("⚠️ Alertas de Estoque", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("📊 Status dos Equipamentos", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
    
    with tab2:
        st.markdown("### 📋 Relatórios de Movimentação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Movimentações por Período", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("🏗️ Movimentações por Obra", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
        
        with col2:
            if st.button("👤 Movimentações por Responsável", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("📍 Movimentações por Local", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
    
    with tab3:
        st.markdown("### 💰 Relatórios Financeiros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💰 Valor do Inventário", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("📈 Custos por Obra", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
        
        with col2:
            if st.button("💸 Depreciação", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
            
            if st.button("📊 ROI por Equipamento", use_container_width=True):
                st.info("Relatório em desenvolvimento...")
    
    # Informações sobre desenvolvimento
    st.markdown("---")
    st.info("""
    💡 **Funcionalidades em desenvolvimento:**
    - ✅ Interface de relatórios
    - ⏳ Geração de PDFs
    - ⏳ Exportação para Excel
    - ⏳ Gráficos interativos
    - ⏳ Agendamento automático
    - ⏳ Relatórios personalizados
    """)

if __name__ == "__main__":
    from pages import relatorios
    relatorios.show()