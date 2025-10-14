#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Movimentações
Página de controle de movimentações
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

def get_movimentacoes_data():
    """Carregar dados das movimentações"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                id, codigo, origem, destino, data, responsavel, status, quantidade
            FROM movimentacoes
            ORDER BY data DESC
            LIMIT 100
        """
        
        result = db.execute_query(query)
        
        if result:
            return pd.DataFrame(result)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def registrar_movimentacao(codigo, origem, destino, quantidade, responsavel):
    """Registrar nova movimentação (direto, sem aprovação)"""
    db = DatabaseConnection()
    
    try:
        from datetime import datetime
        
        # Inserir nova movimentação diretamente aprovada
        query = """
            INSERT INTO movimentacoes (
                codigo, origem, destino, data, responsavel, status, quantidade
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            codigo,
            origem, 
            destino,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            responsavel,
            'concluida',  # Status direto concluída
            quantidade
        )
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao registrar movimentação: {e}")
        return False

def aprovar_movimentacao(movimentacao_id):
    """Aprovar movimentação"""
    db = DatabaseConnection()
    
    try:
        query = "UPDATE movimentacoes SET status = 'aprovada' WHERE id = ?"
        return db.execute_update(query, (movimentacao_id,))
    except Exception as e:
        st.error(f"Erro ao aprovar movimentação: {e}")
        return False

def rejeitar_movimentacao(movimentacao_id):
    """Rejeitar movimentação"""
    db = DatabaseConnection()
    
    try:
        query = "UPDATE movimentacoes SET status = 'cancelada' WHERE id = ?"
        return db.execute_update(query, (movimentacao_id,))
    except Exception as e:
        st.error(f"Erro ao rejeitar movimentação: {e}")
        return False

def show():
    """Função principal da página Movimentações"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 📊 Movimentações")
    st.markdown("Controle de transferências e movimentação de itens")
    
    # Carregar dados
    with st.spinner("📊 Carregando movimentações..."):
        df = get_movimentacoes_data()
    
    if df.empty:
        st.warning("⚠️ Nenhuma movimentação encontrada no sistema")
        st.info("""
        💡 **Movimentações não encontradas**
        
        As movimentações serão exibidas aqui quando houver:
        - Transferências de equipamentos
        - Movimentações de insumos
        - Registros de entrada/saída
        """)
    else:
        # Métricas básicas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Movimentações", len(df))
        
        with col2:
            equipamentos = len(df[df['tipo'] == 'equipamento']) if 'tipo' in df.columns else 0
            st.metric("Equipamentos", equipamentos)
        
        with col3:
            insumos = len(df[df['tipo'] == 'insumo']) if 'tipo' in df.columns else 0
            st.metric("Insumos", insumos)
        
        with col4:
            hoje = pd.Timestamp.now().date()
            if 'data' in df.columns:
                df['data_mov'] = pd.to_datetime(df['data']).dt.date
                hoje_count = len(df[df['data_mov'] == hoje])
            else:
                hoje_count = 0
            st.metric("Hoje", hoje_count)
        
        st.markdown("---")
        
        # Lista de movimentações
        st.markdown("### 📋 Últimas Movimentações")
        
        if not df.empty:
            for idx, row in df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{row['codigo']}**")
                        st.caption(f"📦 Qtd: {row['quantidade']}")
                    
                    with col2:
                        st.markdown(f"📍 **{row['origem']}** → **{row['destino']}**")
                        st.caption(f"👤 {row['responsavel']}")
                    
                    with col3:
                        status_emoji = {"concluida": "✅", "pendente": "⏳", "cancelada": "❌", "aprovada": "🟢"}.get(row['status'], "⚪")
                        st.markdown(f"{status_emoji} **{row['status'].title()}**")
                        st.caption(f"📅 {row['data']}")
                    
                    with col4:
                        # Remover botões de aprovação - movimentações são registradas diretamente
                        st.write("")  # Espaço vazio
                    
                    st.markdown("---")
        else:
            st.info("Nenhuma movimentação encontrada.")
    
    # Formulário para nova movimentação
    st.markdown("---")
    st.markdown("### ➕ Nova Movimentação")
    
    with st.form("nova_movimentacao"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo_item = st.text_input("Código do Item *", help="Código do equipamento ou insumo")
            
            # Importar locais da obra/departamento
            from pages.obras import LOCAIS_SUGERIDOS
            locais_simplificados = [local.split(' - ')[1] if ' - ' in local else local for local in LOCAIS_SUGERIDOS]
            
            origem = st.selectbox("Origem *", locais_simplificados, help="Local de origem do item")
            quantidade = st.number_input("Quantidade *", min_value=1, value=1)
        
        with col2:
            destino = st.selectbox("Destino *", locais_simplificados, help="Local de destino do item")
            responsavel = st.text_input("Responsável *", help="Nome do responsável pela movimentação")
        
        submitted = st.form_submit_button("📦 Registrar Movimentação", type="primary")
        
        if submitted:
            if codigo_item and origem and destino and responsavel:
                # Registrar movimentação
                success = registrar_movimentacao(codigo_item, origem, destino, quantidade, responsavel)
                if success:
                    st.success("✅ Movimentação registrada com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao registrar movimentação!")
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")
    
    # Informações sobre funcionalidades
    st.markdown("---")
    st.info("""
    💡 **Funcionalidades implementadas:**
    - ✅ Listagem de movimentações
    - ✅ Registro direto de movimentações (sem aprovação)
    - ✅ Integração com locais da Obra/Departamento
    - ✅ Controle de quantidade
    - ✅ Rastreamento em tempo real
    """)

if __name__ == "__main__":
    from pages import movimentacoes
    movimentacoes.show()