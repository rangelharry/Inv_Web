#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Obras
Página de gestão de obras e projetos
"""

import streamlit as st
import sys
import os
import pandas as pd

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import DatabaseConnection
from utils.auth import get_auth, check_authentication

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def get_obras_data():
    """Carregar dados das obras"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                id, nome, descricao, status,
                data_inicio, data_termino, responsavel
            FROM obras
            ORDER BY id
        """
        
        result = db.execute_query(query)
        
        if result:
            return pd.DataFrame(result)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def cadastrar_obra(nome, descricao, status, data_inicio, data_termino, responsavel):
    """Cadastrar nova obra"""
    db = DatabaseConnection()
    
    try:
        query = """
            INSERT INTO obras (
                nome, descricao, status, data_inicio, data_termino, responsavel
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (nome, descricao, status, data_inicio.strftime('%Y-%m-%d'), data_termino.strftime('%Y-%m-%d'), responsavel)
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao cadastrar obra: {e}")
        return False

def show():
    """Função principal da página Obras"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 🏗️ Obras e Projetos")
    st.markdown("Gestão de obras, projetos e contratos")
    
    # Carregar dados
    with st.spinner("📊 Carregando dados de obras..."):
        df = get_obras_data()
    
    if df.empty:
        st.warning("⚠️ Nenhuma obra encontrada no sistema")
        st.info("""
        💡 **Obras não encontradas**
        
        Para visualizar obras nesta página:
        - Certifique-se de que existem obras cadastradas no sistema
        - Verifique se a tabela 'obras' existe no banco de dados
        - Confirme suas permissões de acesso
        """)
    else:
        # Métricas básicas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Obras", len(df))
        
        with col2:
            ativas = len(df[df['status'] == 'ativa']) if 'status' in df.columns else 0
            st.metric("Obras Ativas", ativas)
        
        with col3:
            concluidas = len(df[df['status'] == 'concluida']) if 'status' in df.columns else 0
            st.metric("Concluídas", concluidas)
        
        with col4:
            pausadas = len(df[df['status'] == 'pausada']) if 'status' in df.columns else 0
            st.metric("Pausadas", pausadas)
        
        st.markdown("---")
        
        # Lista de obras
        st.markdown("### 📋 Lista de Obras")
        
        if not df.empty:
            for idx, row in df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{row['id']}** - {row['nome']}")
                        st.caption(f"📝 {row['descricao']}")
                    
                    with col2:
                        status_emoji = {"ativa": "🟢", "concluida": "✅", "pausada": "⏸️", "cancelada": "❌"}.get(row['status'], "⚪")
                        st.markdown(f"{status_emoji} **{row['status'].title()}**")
                        st.caption(f"👤 {row['responsavel']}")
                    
                    with col3:
                        st.markdown(f"📅 Início: {row['data_inicio']}")
                        st.caption(f"🏁 Término: {row['data_termino']}")
                    
                    st.markdown("---")
        else:
            st.info("Nenhuma obra encontrada.")
    
    # Formulário para nova obra
    st.markdown("---")
    st.markdown("### ➕ Cadastrar Nova Obra")
    
    with st.form("nova_obra"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome da Obra *", help="Nome identificador da obra")
            descricao = st.text_area("Descrição *", help="Descrição detalhada da obra")
            responsavel = st.text_input("Responsável *", help="Nome do responsável pela obra")
        
        with col2:
            status = st.selectbox("Status *", ["ativa", "pausada", "concluida", "cancelada"])
            data_inicio = st.date_input("Data de Início *")
            data_termino = st.date_input("Data de Término Prevista")
        
        submitted = st.form_submit_button("🏗️ Cadastrar Obra", type="primary")
        
        if submitted:
            if nome and descricao and responsavel:
                success = cadastrar_obra(nome, descricao, status, data_inicio, data_termino, responsavel)
                if success:
                    st.success("✅ Obra cadastrada com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao cadastrar obra!")
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")
    
    # Informações sobre desenvolvimento
    st.markdown("---")
    st.info("""
    💡 **Funcionalidades implementadas:**
    - ✅ Listagem básica de obras
    - ✅ Cadastro de novas obras
    - ✅ Controle de status
    - ⏳ Vinculação com equipamentos
    - ⏳ Relatórios de progresso
    """)

if __name__ == "__main__":
    from pages import obras
    obras.show()