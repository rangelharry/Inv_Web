#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Equipamentos Elétricos
Página para gestão completa de equipamentos elétricos
"""

from typing import Optional, Dict, Any, List
import pandas as pd

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import DatabaseConnection
from utils.auth import get_auth, check_authentication

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

def get_equipamentos_data():
    """Carregar dados dos equipamentos elétricos"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                codigo, nome, categoria, status,
                localizacao, observacoes, marca, modelo, valor_compra
            FROM equipamentos_eletricos
            ORDER BY codigo
        """
        
        result = db.execute_query(query)
        return pd.DataFrame(result) if result else pd.DataFrame()
        
    except Exception as e:
        st.error(f"Erro ao carregar equipamentos: {e}")
        return pd.DataFrame()

def get_locations():
    """Obter lista de localizações disponíveis"""
    # Importar locais da obra/departamento
    from pages.obras import LOCAIS_SUGERIDOS
    locais_simplificados = [local.split(' - ')[1] if ' - ' in local else local for local in LOCAIS_SUGERIDOS]
    return locais_simplificados

def get_categories():
    """Obter categorias de equipamentos"""
    return [
        "Furadeira", "Serra", "Parafusadeira", "Esmerilhadeira", "Soldadora",
        "Compressor", "Gerador", "Medição", "Iluminação", "Outros"
    ]

def show_equipment_filters():
    """Exibir filtros para equipamentos"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Buscar equipamento:",
            placeholder="Digite código, descrição, marca ou modelo...",
            help="Busca em código, descrição, marca e modelo"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Status:",
            ["Todos", "Disponível", "Em uso", "Em manutenção", "Inativo"]
        )
    
    with col3:
        category_filter = st.selectbox(
            "Categoria:",
            ["Todas"] + get_categories()
        )
    
    with col4:
        location_filter = st.selectbox(
            "Localização:",
            ["Todas"] + get_locations()
        )
    
    return search_term, status_filter, category_filter, location_filter

def apply_filters(df: pd.DataFrame, search_term: str, status_filter: str, category_filter: str, location_filter: str) -> pd.DataFrame:
    """Aplicar filtros ao DataFrame"""
    if df.empty:
        return df
    
    # Filtro de busca
    if search_term:
        mask = (
            df['codigo'].str.contains(search_term, case=False, na=False) |
            df['nome'].str.contains(search_term, case=False, na=False)
        )
        df = df[mask]
    
    # Filtro de status
    if status_filter != "Todos":
        df = df[df['status'] == status_filter]
    
    # Filtro de categoria
    if category_filter != "Todas":
        df = df[df['categoria'] == category_filter]
    
    # Filtro de localização
    if location_filter != "Todas":
        df = df[df['localizacao'] == location_filter]
    
    return df

def show_equipment_form(equipment_data: Optional[Dict[str, Any]] = None, edit_mode: bool = False) -> None:
    """Exibir formulário para adicionar/editar equipamento"""
    
    form_title = "✏️ Editar Equipamento" if edit_mode else "➕ Novo Equipamento"
    
    with st.form("equipment_form", clear_on_submit=not edit_mode):
        st.subheader(form_title)
        
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input(
                "Código *",
                value=equipment_data.get('codigo', '') if equipment_data else '',
                help="Código único do equipamento",
                disabled=edit_mode  # Não permitir editar código
            )
            
            nome = st.text_area(
                "Nome/Descrição *",
                value=equipment_data.get('nome', '') if equipment_data else '',
                height=100,
                help="Nome/Descrição detalhada do equipamento"
            )
            
            categoria = st.selectbox(
                "Categoria *",
                get_categories(),
                index=get_categories().index(equipment_data.get('categoria', 'Outros')) if equipment_data and equipment_data.get('categoria') in get_categories() else 0
            )
        
        with col2:
            status = st.selectbox(
                "Status *",
                ["Disponível", "Em uso", "Em manutenção", "Inativo"],
                index=["Disponível", "Em uso", "Em manutenção", "Inativo"].index(equipment_data.get('status', 'Disponível')) if equipment_data else 0
            )
            
            localizacao = st.selectbox(
                "Localização *",
                get_locations(),
                index=get_locations().index(equipment_data.get('localizacao', 'Não Definido')) if equipment_data and equipment_data.get('localizacao') in get_locations() else len(get_locations())-1
            )
        
        observacoes = st.text_area(
            "Observações",
            value=equipment_data.get('observacoes', '') if equipment_data else '',
            height=80
        )
        
        # Botões do formulário
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            submit_button = st.form_submit_button(
                "💾 Salvar Alterações" if edit_mode else "➕ Adicionar Equipamento",
                type="primary",
                use_container_width=True
            )
        
        with col_cancel:
            cancel_button = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if cancel_button:
            st.session_state.show_add_form = False
            st.session_state.edit_equipment = None
            st.rerun()
        
        if submit_button:
            # Validações
            if not codigo or not nome or not categoria or not status or not localizacao:
                st.error("❌ Preencha todos os campos obrigatórios (marcados com *)")
                return
            
            # Preparar dados
            equipment_data_to_save = {
                'codigo': codigo,
                'nome': nome,
                'categoria': categoria,
                'status': status,
                'localizacao': localizacao,
                'observacoes': observacoes
            }
            
            # Salvar no banco
            if edit_mode and equipment_data:
                success = update_equipment(equipment_data['codigo'], equipment_data_to_save)
                if success:
                    st.success("✅ Equipamento atualizado com sucesso!")
                    st.session_state.edit_equipment = None
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar equipamento!")
            else:
                success = add_equipment(equipment_data_to_save)
                if success:
                    st.success("✅ Equipamento adicionado com sucesso!")
                    st.session_state.show_add_form = False
                    st.rerun()
                else:
                    st.error("❌ Erro ao adicionar equipamento!")

def add_equipment(equipment_data: Dict[str, Any]) -> bool:
    """Adicionar novo equipamento"""
    db = DatabaseConnection()
    
    try:
        query = """
            INSERT INTO equipamentos_eletricos (
                codigo, nome, categoria, status,
                localizacao, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            equipment_data['codigo'],
            equipment_data['nome'],
            equipment_data['categoria'],
            equipment_data['status'],
            equipment_data['localizacao'],
            equipment_data['observacoes']
        )
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao adicionar equipamento: {e}")
        return False

def update_equipment(equipment_id: str, equipment_data: Dict[str, Any]) -> bool:
    """Atualizar equipamento existente"""
    db = DatabaseConnection()
    
    try:
        query = """
            UPDATE equipamentos_eletricos SET
                nome = ?, categoria = ?, status = ?,
                localizacao = ?, observacoes = ?
            WHERE codigo = ?
        """
        
        params = (
            equipment_data['nome'],
            equipment_data['categoria'],
            equipment_data['status'],
            equipment_data['localizacao'],
            equipment_data['observacoes'],
            equipment_id
        )
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao atualizar equipamento: {e}")
        return False

def delete_equipment(equipment_id: str) -> bool:
    """Deletar equipamento"""
    db = DatabaseConnection()
    
    try:
        return db.execute_update("DELETE FROM equipamentos_eletricos WHERE codigo = ?", (equipment_id,))
    except Exception as e:
        st.error(f"Erro ao deletar equipamento: {e}")
        return False

def show_equipment_table(df: pd.DataFrame) -> None:
    """Exibir tabela de equipamentos"""
    if df.empty:
        st.info("📭 Nenhum equipamento encontrado com os filtros aplicados")
        return
    
    # Configurar colunas para exibição
    df_display = df.copy()
    
    # Formatar dados para melhor visualização
    df_display['Código'] = df['codigo']
    df_display['Descrição'] = df['nome'].str[:50] + '...' if len(df) > 0 and len(df['nome'].iloc[0]) > 50 else df['nome']
    df_display['Categoria'] = df['categoria']
    df_display['Status'] = df['status']
    df_display['Localização'] = df['localizacao']
    
    # Colunas a exibir
    columns_to_show = ['Código', 'Descrição', 'Categoria', 'Status', 'Localização']
    
    # Criar colunas para tabela e ações
    col_table, col_actions = st.columns([4, 1])
    
    with col_table:
        # Exibir tabela usando HTML para evitar dependência do pyarrow
        if not df_display.empty:
            st.markdown("**Equipamentos Cadastrados:**")
            
            for idx, row in df_display.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{row['Código']}** - {row['Descrição'][:30]}...")
                        st.caption(f"📍 {row['Localização']}")
                    
                    with col2:
                        status_color = {"Disponível": "🟢", "Em Uso": "�", "Manutenção": "�", "Inativo": "⚫"}.get(row['Status'], "⚪")
                        st.markdown(f"{status_color} **{row['Status']}**")
                        st.caption(f"� {row['Categoria']}")
                    
                    with col3:
                        st.caption(f" {row.get('data_entrada', 'N/A')}")
                    
                    with col4:
                        # Botão de movimentação rápida
                        if st.button("🔄", key=f"move_btn_{row['Código']}", help="Movimentação Rápida"):
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
    
    with col_actions:
        st.markdown("#### Ações")
        
        # Seletor de equipamento para ações
        if not df.empty:
            selected_equipment = st.selectbox(
                "Selecionar:",
                options=range(len(df)),
                format_func=lambda x: f"{df.iloc[x]['codigo']} - {df.iloc[x]['nome'][:20]}...",
                key="equipment_selector"
            )
            
            equipment_data = df.iloc[selected_equipment].to_dict()
            
            # Botões de ação
            if st.button("✏️ Editar", use_container_width=True):
                st.session_state.edit_equipment = equipment_data
                st.rerun()
            
            if st.button("🔄 Movimentar", use_container_width=True):
                st.session_state.move_equipment = equipment_data
                st.rerun()
            
            if st.button("🗑️ Excluir", use_container_width=True, type="secondary"):
                if st.session_state.get('confirm_delete') != equipment_data['codigo']:
                    st.session_state.confirm_delete = equipment_data['codigo']
                    st.warning("⚠️ Clique novamente para confirmar exclusão")
                else:
                    if delete_equipment(equipment_data['codigo']):
                        st.success("✅ Equipamento excluído com sucesso!")
                        del st.session_state.confirm_delete
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir equipamento!")

def show():
    """Função principal da página Equipamentos Elétricos"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    # Header da página
    st.markdown("## ⚡ Equipamentos Elétricos")
    st.markdown("Gestão completa de ferramentas e equipamentos elétricos")
    
    # Controles superiores
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Filtros
        search_term, status_filter, category_filter, location_filter = show_equipment_filters()
    
    with col2:
        st.markdown("#### Ações")
        if st.button("➕ Novo Equipamento", use_container_width=True, type="primary"):
            st.session_state.show_add_form = True
            st.rerun()
        
        if st.button("📊 Relatório", use_container_width=True):
            st.info("Funcionalidade de relatório será implementada")
    
    st.markdown("---")
    
    # Formulário de novo equipamento
    if st.session_state.get('show_add_form', False):
        show_equipment_form()
        st.markdown("---")
    
    # Formulário de edição
    if st.session_state.get('edit_equipment'):
        show_equipment_form(st.session_state.edit_equipment, edit_mode=True)
        st.markdown("---")
    
    # Carregar e exibir dados
    with st.spinner("⚡ Carregando equipamentos..."):
        df = get_equipamentos_data()
    
    if not df.empty:
        # Aplicar filtros
        df_filtered = apply_filters(df, search_term, status_filter, category_filter, location_filter)
        
        # Exibir estatísticas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Equipamentos", len(df))
        
        with col2:
            disponivel = len(df[df['status'] == 'Disponível'])
            st.metric("Disponíveis", disponivel)
        
        with col3:
            em_uso = len(df[df['status'] == 'Em Uso'])
            st.metric("Em Uso", em_uso)
        
        with col4:
            manutencao = len(df[df['status'] == 'Manutenção'])
            st.metric("Em Manutenção", manutencao, delta_color="inverse")
        
        st.markdown("---")
        
        # Exibir tabela
        st.markdown(f"### 📋 Lista de Equipamentos ({len(df_filtered)} encontrados)")
        show_equipment_table(df_filtered)
        
    else:
        st.warning("⚠️ Nenhum equipamento encontrado no banco de dados")
        st.info("Use o botão 'Novo Equipamento' para adicionar o primeiro equipamento")
    
    # Informações sobre funcionalidades
    st.markdown("---")
    st.info("""
    💡 **Funcionalidades implementadas:**
    - ✅ Listagem completa de equipamentos elétricos
    - ✅ Cadastro de novos equipamentos
    - ✅ Edição e exclusão de equipamentos
    - ✅ Filtros avançados (status, categoria, localização)
    - ✅ Movimentação rápida com quantidade
    - ✅ Integração com locais da Obra/Departamento
    - ✅ Sistema de busca por código/descrição
    - ✅ Métricas e estatísticas em tempo real
    """)

if __name__ == "__main__":
    from pages import equipamentos_eletricos
    equipamentos_eletricos.show()