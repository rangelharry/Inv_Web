#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Equipamentos Manuais
Página de gestão de equipamentos manuais
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import DatabaseConnection
from utils.auth import get_auth, check_authentication

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def get_equipamentos_manuais_data():
    """Carregar dados dos equipamentos manuais"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                codigo, descricao, tipo as categoria, status,
                localizacao, quantitativo, estado, marca, valor, data_compra
            FROM equipamentos_manuais
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

def show_equipamentos_table(df):
    """Exibir tabela de equipamentos manuais"""
    if df.empty:
        st.warning("Nenhum equipamento manual encontrado")
        return
    
    # Configurar colunas para exibição
    df_display = df.copy()
    df_display['Quantidade'] = df_display['quantitativo']
    df_display['Data Compra'] = df_display['data_compra']
    
    # Exibir tabela sem pyarrow
    # Renomear colunas para exibição
    df_display = df_display.rename(columns={
        'codigo': 'Código',
        'descricao': 'Descrição',
        'categoria': 'Tipo',
        'status': 'Status',
        'localizacao': 'Localização',
        'Quantidade': 'Quantidade',
        'estado': 'Estado',
        'marca': 'Marca'
    })
    
    # Exibir dados com ações de movimentação rápida
    if not df_display.empty:
        for idx, row in df_display.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{row['Código']}** - {row['Descrição']}")
                    st.caption(f"📍 {row['Localização']}")
                
                with col2:
                    status_emoji = {"Disponível": "🟢", "Em Uso": "🟡", "Manutenção": "🔴", "Inativo": "⚫"}.get(row['Status'], "⚪")
                    st.markdown(f"{status_emoji} **{row['Status']}**")
                    st.caption(f"🏭 {row['Marca']}")
                
                with col3:
                    st.markdown(f"**{row['Tipo']}**")
                    estado_emoji = {"Novo": "✨", "Usado": "🔧", "Danificado": "⚠️"}.get(row['Estado'], "❓")
                    st.caption(f"{estado_emoji} {row['Estado']} - Qtd: {row['Quantidade']}")
                
                with col4:
                    # Botão de movimentação rápida
                    if st.button("🔄", key=f"move_{row['Código']}", help="Movimentação Rápida"):
                        st.session_state[f'show_move_{row["Código"]}'] = True
                        st.rerun()
                
                # Formulário de movimentação rápida
                if st.session_state.get(f'show_move_{row["Código"]}', False):
                    with st.form(f"move_form_{row['Código']}"):
                        st.markdown(f"#### 🔄 Movimentar: {row['Código']}")
                        
                        col_origem, col_destino, col_qtd = st.columns(3)
                        
                        with col_origem:
                            st.text_input("Origem", value=row['Localização'], disabled=True)
                        
                        with col_destino:
                            # Importar locais da obra/departamento
                            from pages.obras import LOCAIS_SUGERIDOS
                            locais_simplificados = [local.split(' - ')[1] if ' - ' in local else local for local in LOCAIS_SUGERIDOS]
                            destino = st.selectbox("Novo Destino", locais_simplificados)
                        
                        with col_qtd:
                            quantidade = st.number_input("Quantidade", min_value=1, value=1, help="Quantidade a movimentar")
                        
                        responsavel = st.text_input("Responsável", help="Nome do responsável pela movimentação")
                        
                        col_submit, col_cancel = st.columns(2)
                        
                        with col_submit:
                            submitted = st.form_submit_button("✅ Confirmar", type="primary")
                        
                        with col_cancel:
                            cancelled = st.form_submit_button("❌ Cancelar")
                        
                        if submitted and responsavel:
                            # Registrar movimentação
                            from pages.movimentacoes import registrar_movimentacao
                            success = registrar_movimentacao(
                                row['Código'], 
                                row['Localização'], 
                                destino, 
                                quantidade, 
                                responsavel
                            )
                            if success:
                                st.success(f"✅ Movimentação de {quantidade}x {row['Código']} registrada!")
                                del st.session_state[f'show_move_{row["Código"]}']
                                st.rerun()
                            else:
                                st.error("❌ Erro ao registrar movimentação!")
                        
                        elif submitted and not responsavel:
                            st.error("❌ Informe o responsável!")
                        
                        if cancelled:
                            del st.session_state[f'show_move_{row["Código"]}']
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("Nenhum equipamento encontrado.")

def show_metrics_manuais(df):
    """Exibir métricas dos equipamentos manuais"""
    if df.empty:
        st.info("Sem dados para exibir métricas")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.metric("Total de Equipamentos", total)
    
    with col2:
        disponiveis = len(df[df['status'] == 'Disponível'])
        st.metric("Disponíveis", disponiveis, f"{(disponiveis/total*100):.1f}%" if total > 0 else "0%")
    
    with col3:
        em_uso = len(df[df['status'] == 'Em Uso'])
        st.metric("Em Uso", em_uso, f"{(em_uso/total*100):.1f}%" if total > 0 else "0%")
    
    with col4:
        manutencao = len(df[df['status'] == 'Manutenção'])
        st.metric("Manutenção", manutencao, f"{(manutencao/total*100):.1f}%" if total > 0 else "0%")

def show():
    """Função principal da página Equipamentos Manuais"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    user = auth.get_current_user()
    
    st.markdown(f"## 🔧 Equipamentos Manuais")
    st.markdown("Gestão de ferramentas e equipamentos manuais")
    
    # Carregar dados
    with st.spinner("📊 Carregando equipamentos manuais..."):
        df = get_equipamentos_manuais_data()
    
    if df.empty:
        st.warning("⚠️ Nenhum equipamento manual encontrado no sistema")
        st.info("""
        💡 **Equipamentos manuais não encontrados**
        
        Para ver equipamentos manuais nesta página, certifique-se de que:
        - Existem equipamentos cadastrados no sistema
        - Os equipamentos estão categorizados como 'manual' ou 'ferramenta'
        - Você tem permissão para visualizar estes dados
        """)
        return
    
    # Métricas
    st.markdown("### 📊 Resumo Geral")
    show_metrics_manuais(df)
    
    st.markdown("---")
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status:",
            ["Todos"] + list(df['status'].unique()),
            key="status_filter_manuais"
        )
    
    with col2:
        categoria_filter = st.selectbox(
            "Categoria:",
            ["Todas"] + list(df['categoria'].unique()),
            key="categoria_filter_manuais"
        )
    
    with col3:
        search_term = st.text_input(
            "Buscar:",
            placeholder="Digite código ou descrição...",
            key="search_manuais"
        )
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if status_filter != "Todos":
        df_filtered = df_filtered[df_filtered['status'] == status_filter]
    
    if categoria_filter != "Todas":
        df_filtered = df_filtered[df_filtered['categoria'] == categoria_filter]
    
    if search_term:
        mask = (
            df_filtered['codigo'].str.contains(search_term, case=False, na=False) |
            df_filtered['descricao'].str.contains(search_term, case=False, na=False)
        )
        df_filtered = df_filtered[mask]
    
    st.markdown("---")
    
    # Tabela de equipamentos
    if not df_filtered.empty:
        st.markdown(f"### 📋 Equipamentos Manuais ({len(df_filtered)} encontrados)")
        show_equipamentos_table(df_filtered)
        
        # Informações adicionais
        st.markdown("---")
        st.info("""
        💡 **Funcionalidades em desenvolvimento:**
        - ✅ Listagem e filtros de equipamentos manuais
        - ⏳ Cadastro de novos equipamentos
        - ⏳ Edição e exclusão
        - ⏳ Controle de movimentação
        - ⏳ Relatórios específicos
        """)
        
    else:
        st.warning("⚠️ Nenhum equipamento manual encontrado no sistema")
        
        st.info("""
        **💡 Equipamentos manuais não encontrados**
        
        Para ver equipamentos manuais nesta página, certifique-se de que:
        
        • Existem equipamentos cadastrados no sistema
        • Os equipamentos estão categorizados como 'manual' ou 'ferramenta'  
        • Você tem permissão para visualizar estes dados
        """)

if __name__ == "__main__":
    from pages import equipamentos_manuais
    equipamentos_manuais.show()