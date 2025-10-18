#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Insumos
Página de gestão de insumos e materiais
"""

import streamlit as st
from utils.global_css import apply_global_css, force_light_theme
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
    
    # Exibir dados com ações de movimentação/entrada/saída rápida
    if not df_display.empty:
        for idx, row in df_display.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['Código']}** - {row['Descrição']}")
                    st.caption(f"📍 {row['Localização']}")
                
                with col2:
                    st.markdown(f"{row['Status Estoque']} **{row['Categoria']}**")
                    st.caption(f"📦 {row['Quantidade']} {row['Unidade']}")
                
                with col3:
                    st.markdown(f"**{row['Valor Total']}**")
                
                with col4:
                    # Botões de entrada/saída rápida
                    col_in, col_out = st.columns(2)
                    
                    with col_in:
                        if st.button("➕", key=f"in_{row['Código']}", help="Entrada"):
                            st.session_state[f'show_entrada_{row["Código"]}'] = True
                            st.rerun()
                    
                    with col_out:
                        if st.button("➖", key=f"out_{row['Código']}", help="Saída"):
                            st.session_state[f'show_saida_{row["Código"]}'] = True
                            st.rerun()
                
                # Formulário de entrada
                if st.session_state.get(f'show_entrada_{row["Código"]}', False):
                    with st.form(f"entrada_form_{row['Código']}"):
                        st.markdown(f"#### ➕ Entrada: {row['Código']}")
                        
                        col_qtd, col_resp = st.columns(2)
                        
                        with col_qtd:
                            quantidade = st.number_input("Quantidade", min_value=0.1, value=1.0, step=0.1)
                        
                        with col_resp:
                            responsavel = st.text_input("Responsável")
                        
                        observacoes = st.text_input("Observações", placeholder="Ex: Compra, transferência...")
                        
                        col_submit, col_cancel = st.columns(2)
                        
                        with col_submit:
                            submitted = st.form_submit_button("✅ Confirmar Entrada", type="primary")
                        
                        with col_cancel:
                            cancelled = st.form_submit_button("❌ Cancelar")
                        
                        if submitted and responsavel:
                            success = movimentar_estoque_insumo(row['Código'], quantidade, 'entrada', responsavel, observacoes)
                            if success:
                                st.success(f"✅ Entrada de {quantidade} {row['Unidade']} registrada!")
                                del st.session_state[f'show_entrada_{row["Código"]}']
                                st.rerun()
                            else:
                                st.error("❌ Erro ao registrar entrada!")
                        
                        elif submitted and not responsavel:
                            st.error("❌ Informe o responsável!")
                        
                        if cancelled:
                            del st.session_state[f'show_entrada_{row["Código"]}']
                            st.rerun()
                
                # Formulário de saída
                if st.session_state.get(f'show_saida_{row["Código"]}', False):
                    with st.form(f"saida_form_{row['Código']}"):
                        st.markdown(f"#### ➖ Saída: {row['Código']}")
                        
                        col_qtd, col_resp = st.columns(2)
                        
                        with col_qtd:
                            quantidade = st.number_input("Quantidade", min_value=0.1, value=1.0, step=0.1)
                        
                        with col_resp:
                            responsavel = st.text_input("Responsável")
                        
                        observacoes = st.text_input("Observações", placeholder="Ex: Uso em obra, transferência...")
                        
                        col_submit, col_cancel = st.columns(2)
                        
                        with col_submit:
                            submitted = st.form_submit_button("✅ Confirmar Saída", type="primary")
                        
                        with col_cancel:
                            cancelled = st.form_submit_button("❌ Cancelar")
                        
                        if submitted and responsavel:
                            success = movimentar_estoque_insumo(row['Código'], quantidade, 'saida', responsavel, observacoes)
                            if success:
                                st.success(f"✅ Saída de {quantidade} {row['Unidade']} registrada!")
                                del st.session_state[f'show_saida_{row["Código"]}']
                                st.rerun()
                            else:
                                st.error("❌ Erro ao registrar saída!")
                        
                        elif submitted and not responsavel:
                            st.error("❌ Informe o responsável!")
                        
                        if cancelled:
                            del st.session_state[f'show_saida_{row["Código"]}']
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("Nenhum insumo encontrado.")

def movimentar_estoque_insumo(codigo, quantidade, tipo, responsavel, observacoes=""):
    """Movimentar estoque de insumo (entrada/saída)"""
    db = DatabaseConnection()
    
    try:
        from datetime import datetime
        
        # Buscar dados atuais do insumo
        insumo = db.execute_query("SELECT * FROM insumos WHERE codigo = ?", (codigo,))
        
        if not insumo:
            st.error("Insumo não encontrado!")
            return False
        
        insumo_atual = insumo[0]
        quantidade_atual = float(insumo_atual['quantidade'])
        
        # Calcular nova quantidade
        if tipo == 'entrada':
            nova_quantidade = quantidade_atual + quantidade
        else:  # saída
            if quantidade > quantidade_atual:
                st.error(f"Quantidade insuficiente! Disponível: {quantidade_atual}")
                return False
            nova_quantidade = quantidade_atual - quantidade
        
        # Atualizar estoque
        update_query = "UPDATE insumos SET quantidade = ? WHERE codigo = ?"
        success = db.execute_update(update_query, (nova_quantidade, codigo))
        
        if success:
            # Registrar movimentação
            from pages.movimentacoes import registrar_movimentacao
            registrar_movimentacao(
                codigo,
                insumo_atual['localizacao'],
                insumo_atual['localizacao'],  # Mesmo local, apenas alteração de quantidade
                quantidade,
                responsavel
            )
        
        return success
        
    except Exception as e:
        st.error(f"Erro ao movimentar estoque: {e}")
        return False

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
    
    # CSS INLINE FORÇA BRUTA
    st.markdown("""
    <style>
        * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        .stApp, .stApp * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        .stSidebar, .stSidebar * {
            background: #f0f0f0 !important;
            color: #000000 !important;
        }
        
        [data-theme="dark"], [data-theme="dark"] * {
            background: #ffffff !important;
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # FORÇAR TEMA CLARO - MODO EXTREMO
    apply_global_css()
    force_light_theme()
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 📦 Insumos e Materiais")
    st.markdown("**CRUD Completo** - Gestão de materiais, insumos e consumíveis")
    
    # Abas principais - igual aos equipamentos manuais
    tab_list, tab_create, tab_manage = st.tabs(["📋 Listagem", "➕ Cadastrar", "⚙️ Gerenciar"])
    
    with tab_list:
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
        else:
            st.warning("⚠️ Nenhum insumo encontrado com os filtros aplicados")
            st.info("Tente ajustar os filtros ou termo de busca")
    
    with tab_create:
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
                # Usar locais simplificados sem as obras
                locais_simplificados = [
                    "Almoxarifado Central", "Escritório Matriz", "Manutenção", "Engenharia", 
                    "Recursos Humanos", "Galpão Principal", "Depósito Filial", "Área Externa"
                ]
                localizacao = st.selectbox("Localização *", locais_simplificados)
            
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
    
    with tab_manage:
        st.markdown("### ⚙️ Gerenciar Insumos")
        st.info("""
        💡 **Funcionalidades disponíveis:**
        - ✅ Listagem e controle de estoque
        - ✅ Alertas de estoque baixo  
        - ✅ Filtros avançados
        - ✅ Cadastro de novos insumos
        - ⏳ Edição e exclusão de insumos
        - ⏳ Movimentações de entrada/saída
        - ⏳ Relatórios de consumo
        """)
        
        # Adicionar aqui futuras funcionalidades de gerenciamento
        st.warning("🚧 Funcionalidades de edição e exclusão em desenvolvimento")

if __name__ == "__main__":
    from pages import insumos
    insumos.show()