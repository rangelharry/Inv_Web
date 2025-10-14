#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Insumos
Página de gestão de insumos e materiais
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

def get_insumos_data():
    """Carregar dados dos insumos"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                codigo, descricao, categoria, unidade,
                quantidade as quantidade_atual, quantidade_minima, preco_unitario,
                localizacao, observacoes
            FROM insumos
            ORDER BY codigo
        """
        
        result = db.execute_query(query)
        
        if result:
            return pd.DataFrame(result)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def show_insumos_table(df):
    """Exibir tabela de insumos"""
    if df.empty:
        st.warning("Nenhum insumo encontrado")
        return
    
    # Configurar colunas para exibição
    df_display = df.copy()
    
    # Calcular valor total
    df_display['Valor Total'] = df_display['quantidade_atual'] * df_display['preco_unitario']
    
    # Status do estoque
    df_display['Status Estoque'] = df_display.apply(
        lambda row: "🔴 Baixo" if row['quantidade_atual'] <= row['quantidade_minima'] 
        else "🟡 Atenção" if row['quantidade_atual'] <= row['quantidade_minima'] * 1.5
        else "🟢 OK", axis=1
    )
    
    # Exibir tabela sem pyarrow
    # Renomear colunas para exibição
    df_display = df_display.rename(columns={
        'codigo': 'Código',
        'descricao': 'Descrição', 
        'categoria': 'Categoria',
        'quantidade_atual': 'Quantidade',
        'unidade': 'Unidade',
        'localizacao': 'Localização'
    })
    
    # Formatar valor total
    df_display['Valor Total'] = df_display['Valor Total'].apply(lambda x: f"R$ {x:.2f}")
    
    # Exibir dados usando HTML para evitar dependência do pyarrow
    if not df_display.empty:
        for idx, row in df_display.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.markdown(f"**{row['Código']}** - {row['Descrição']}")
                    st.caption(f"📍 {row['Localização']}")
                
                with col2:
                    st.markdown(f"{row['Status Estoque']} **{row['Categoria']}**")
                    st.caption(f"📦 {row['Quantidade']} {row['Unidade']}")
                
                with col3:
                    st.markdown(f"**{row['Valor Total']}**")
                
                st.markdown("---")
    else:
        st.info("Nenhum insumo encontrado.")

def cadastrar_insumo(codigo, descricao, categoria, unidade, quantidade, quantidade_minima, preco_unitario, localizacao, observacoes=""):
    """Cadastrar novo insumo"""
    db = DatabaseConnection()
    
    try:
        query = """
            INSERT INTO insumos (
                codigo, descricao, categoria, unidade, quantidade, quantidade_minima, 
                preco_unitario, localizacao, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (codigo, descricao, categoria, unidade, quantidade, quantidade_minima, preco_unitario, localizacao, observacoes)
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao cadastrar insumo: {e}")
        return False

def show_metrics_insumos(df):
    """Exibir métricas dos insumos"""
    if df.empty:
        st.info("Sem dados para exibir métricas")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.metric("Total de Insumos", total)
    
    with col2:
        estoque_baixo = len(df[df['quantidade_atual'] <= df['quantidade_minima']])
        st.metric(
            "Estoque Baixo", 
            estoque_baixo, 
            f"{(estoque_baixo/total*100):.1f}%" if total > 0 else "0%",
            delta_color="inverse" if estoque_baixo > 0 else "normal"
        )
    
    with col3:
        valor_total = (df['quantidade_atual'] * df['preco_unitario']).sum()
        st.metric("Valor Total", f"R$ {valor_total:,.2f}")
    
    with col4:
        categorias = df['categoria'].nunique()
        st.metric("Categorias", categorias)

def show():
    """Função principal da página Insumos"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 📦 Insumos e Materiais")
    st.markdown("Controle de estoque de materiais, insumos e consumíveis")
    
    # Carregar dados
    with st.spinner("📊 Carregando dados de insumos..."):
        df = get_insumos_data()
    
    if df.empty:
        st.warning("⚠️ Nenhum insumo encontrado no sistema")
        st.info("""
        💡 **Insumos não encontrados**
        
        Para visualizar insumos nesta página:
        - Certifique-se de que existem insumos cadastrados no sistema
        - Verifique se a tabela 'insumos' existe no banco de dados
        - Confirme suas permissões de acesso
        """)
        return
    
    # Métricas
    st.markdown("### 📊 Resumo do Estoque")
    show_metrics_insumos(df)
    
    st.markdown("---")
    
    # Alertas de estoque baixo
    estoque_baixo = df[df['quantidade_atual'] <= df['quantidade_minima']]
    if not estoque_baixo.empty:
        st.error(f"⚠️ **ALERTA:** {len(estoque_baixo)} insumos com estoque baixo!")
        
        with st.expander("Ver insumos com estoque baixo"):
            for _, item in estoque_baixo.iterrows():
                st.warning(f"🔴 **{item['codigo']}** - {item['descricao']} (Atual: {item['quantidade_atual']} {item['unidade']}, Mínimo: {item['quantidade_minima']} {item['unidade']})")
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        categoria_filter = st.selectbox(
            "Categoria:",
            ["Todas"] + list(df['categoria'].unique()),
            key="categoria_filter_insumos"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Status do Estoque:",
            ["Todos", "🔴 Baixo", "🟡 Atenção", "🟢 OK"],
            key="status_filter_insumos"
        )
    
    with col3:
        localizacao_filter = st.selectbox(
            "Localização:",
            ["Todas"] + list(df['localizacao'].unique()),
            key="localizacao_filter_insumos"
        )
    
    with col4:
        search_term = st.text_input(
            "Buscar:",
            placeholder="Digite código ou descrição...",
            key="search_insumos"
        )
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if categoria_filter != "Todas":
        df_filtered = df_filtered[df_filtered['categoria'] == categoria_filter]
    
    if localizacao_filter != "Todas":
        df_filtered = df_filtered[df_filtered['localizacao'] == localizacao_filter]
    
    if status_filter != "Todos":
        if status_filter == "🔴 Baixo":
            df_filtered = df_filtered[df_filtered['quantidade_atual'] <= df_filtered['quantidade_minima']]
        elif status_filter == "🟡 Atenção":
            df_filtered = df_filtered[
                (df_filtered['quantidade_atual'] > df_filtered['quantidade_minima']) &
                (df_filtered['quantidade_atual'] <= df_filtered['quantidade_minima'] * 1.5)
            ]
        elif status_filter == "🟢 OK":
            df_filtered = df_filtered[df_filtered['quantidade_atual'] > df_filtered['quantidade_minima'] * 1.5]
    
    if search_term:
        mask = (
            df_filtered['codigo'].str.contains(search_term, case=False, na=False) |
            df_filtered['descricao'].str.contains(search_term, case=False, na=False)
        )
        df_filtered = df_filtered[mask]
    
    st.markdown("---")
    
    # Tabela de insumos
    if not df_filtered.empty:
        st.markdown(f"### 📋 Lista de Insumos ({len(df_filtered)} encontrados)")
        show_insumos_table(df_filtered)
        
    # Formulário para novo insumo
    st.markdown("---")
    st.markdown("### ➕ Cadastrar Novo Insumo")
    
    with st.form("novo_insumo"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código *", help="Código único do insumo")
            descricao = st.text_input("Descrição *", help="Descrição detalhada do insumo")
            categoria = st.selectbox("Categoria *", [
                "Material Elétrico", "Ferragem", "Parafusos", "Produtos Químicos",
                "Material de Limpeza", "Consumíveis", "Outros"
            ])
            unidade = st.selectbox("Unidade *", ["UN", "M", "KG", "L", "M²", "M³", "PC", "CX"])
        
        with col2:
            quantidade = st.number_input("Quantidade Inicial *", min_value=0.0, value=0.0, step=0.1)
            quantidade_minima = st.number_input("Quantidade Mínima *", min_value=0.0, value=1.0, step=0.1)
            preco_unitario = st.number_input("Preço Unitário (R$) *", min_value=0.0, value=0.0, step=0.01)
            localizacao = st.selectbox("Localização *", [
                "Almoxarifado Central", "Depósito A", "Depósito B", "Oficina Principal"
            ])
        
        observacoes = st.text_area("Observações")
        
        submitted = st.form_submit_button("📦 Cadastrar Insumo", type="primary")
        
        if submitted:
            if codigo and descricao and categoria and unidade and preco_unitario > 0:
                success = cadastrar_insumo(codigo, descricao, categoria, unidade, quantidade, quantidade_minima, preco_unitario, localizacao, observacoes)
                if success:
                    st.success("✅ Insumo cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao cadastrar insumo!")
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")
    
    # Informações adicionais
    st.markdown("---")
    st.info("""
    💡 **Funcionalidades implementadas:**
    - ✅ Listagem e controle de estoque
    - ✅ Alertas de estoque baixo
    - ✅ Filtros avançados
    - ✅ Cadastro de novos insumos
    - ⏳ Movimentações de entrada/saída
    - ⏳ Relatórios de consumo
    """)
        
    else:
        st.warning("⚠️ Nenhum insumo encontrado com os filtros aplicados")
        st.info("Tente ajustar os filtros ou termo de busca")

if __name__ == "__main__":
    from pages import insumos
    insumos.show()