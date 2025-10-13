#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Equipamentos Elétricos
Página para gestão completa de equipamentos elétricos
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import get_database
from utils.auth import get_auth

def get_equipamentos_data():
    """Carregar dados dos equipamentos elétricos"""
    db = get_database()
    
    try:
        query = """
            SELECT 
                id, codigo, descricao, marca, modelo, categoria,
                tensao, potencia, corrente_eletrica, status,
                localizacao, responsavel, data_entrada, observacoes
            FROM equipamentos
            ORDER BY codigo
        """
        
        result = db.execute_query(query)
        return pd.DataFrame(result) if result else pd.DataFrame()
        
    except Exception as e:
        st.error(f"Erro ao carregar equipamentos: {e}")
        return pd.DataFrame()

def get_locations():
    """Obter lista de localizações disponíveis"""
    return [
        "Almoxarifado Central", "Depósito A", "Depósito B", "Oficina Principal",
        "Oficina Secundária", "Obra Centro", "Obra Zona Norte", "Obra Zona Sul",
        "Obra Zona Leste", "Obra Zona Oeste", "Manutenção", "Em Trânsito",
        "Emprestado", "Vendido", "Descartado", "Garantia", "Outros", "Não Definido"
    ]

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

def apply_filters(df, search_term, status_filter, category_filter, location_filter):
    """Aplicar filtros ao DataFrame"""
    if df.empty:
        return df
    
    # Filtro de busca
    if search_term:
        mask = (
            df['codigo'].str.contains(search_term, case=False, na=False) |
            df['descricao'].str.contains(search_term, case=False, na=False) |
            df['marca'].str.contains(search_term, case=False, na=False) |
            df['modelo'].str.contains(search_term, case=False, na=False)
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

def show_equipment_form(equipment_data=None, edit_mode=False):
    """Exibir formulário para adicionar/editar equipamento"""
    
    form_title = "✏️ Editar Equipamento" if edit_mode else "➕ Novo Equipamento"
    
    with st.form("equipment_form", clear_on_submit=not edit_mode):
        st.subheader(form_title)
        
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input(
                "Código *",
                value=equipment_data.get('codigo', '') if equipment_data else '',
                help="Código único do equipamento"
            )
            
            descricao = st.text_area(
                "Descrição *",
                value=equipment_data.get('descricao', '') if equipment_data else '',
                height=100,
                help="Descrição detalhada do equipamento"
            )
            
            marca = st.text_input(
                "Marca",
                value=equipment_data.get('marca', '') if equipment_data else ''
            )
            
            modelo = st.text_input(
                "Modelo",
                value=equipment_data.get('modelo', '') if equipment_data else ''
            )
            
            categoria = st.selectbox(
                "Categoria *",
                get_categories(),
                index=get_categories().index(equipment_data.get('categoria', 'Outros')) if equipment_data and equipment_data.get('categoria') in get_categories() else 0
            )
        
        with col2:
            tensao = st.text_input(
                "Tensão (V)",
                value=equipment_data.get('tensao', '') if equipment_data else '',
                help="Ex: 110V, 220V, 380V"
            )
            
            potencia = st.text_input(
                "Potência (W)",
                value=equipment_data.get('potencia', '') if equipment_data else '',
                help="Potência em Watts"
            )
            
            corrente_eletrica = st.text_input(
                "Corrente (A)",
                value=equipment_data.get('corrente_eletrica', '') if equipment_data else '',
                help="Corrente elétrica em Ampères"
            )
            
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
            
            responsavel = st.text_input(
                "Responsável",
                value=equipment_data.get('responsavel', '') if equipment_data else ''
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
            if not codigo or not descricao or not categoria or not status or not localizacao:
                st.error("❌ Preencha todos os campos obrigatórios (marcados com *)")
                return
            
            # Preparar dados
            equipment_data_to_save = {
                'codigo': codigo,
                'descricao': descricao,
                'marca': marca,
                'modelo': modelo,
                'categoria': categoria,
                'tensao': tensao,
                'potencia': potencia,
                'corrente_eletrica': corrente_eletrica,
                'status': status,
                'localizacao': localizacao,
                'responsavel': responsavel,
                'observacoes': observacoes
            }
            
            # Salvar no banco
            if edit_mode and equipment_data:
                success = update_equipment(equipment_data['id'], equipment_data_to_save)
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

def add_equipment(equipment_data):
    """Adicionar novo equipamento"""
    db = get_database()
    
    try:
        query = """
            INSERT INTO equipamentos (
                codigo, descricao, marca, modelo, categoria,
                tensao, potencia, corrente_eletrica, status,
                localizacao, responsavel, data_entrada, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            equipment_data['codigo'],
            equipment_data['descricao'],
            equipment_data['marca'],
            equipment_data['modelo'],
            equipment_data['categoria'],
            equipment_data['tensao'],
            equipment_data['potencia'],
            equipment_data['corrente_eletrica'],
            equipment_data['status'],
            equipment_data['localizacao'],
            equipment_data['responsavel'],
            datetime.now().isoformat(),
            equipment_data['observacoes']
        )
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao adicionar equipamento: {e}")
        return False

def update_equipment(equipment_id, equipment_data):
    """Atualizar equipamento existente"""
    db = get_database()
    
    try:
        query = """
            UPDATE equipamentos SET
                codigo = ?, descricao = ?, marca = ?, modelo = ?, categoria = ?,
                tensao = ?, potencia = ?, corrente_eletrica = ?, status = ?,
                localizacao = ?, responsavel = ?, observacoes = ?
            WHERE id = ?
        """
        
        params = (
            equipment_data['codigo'],
            equipment_data['descricao'],
            equipment_data['marca'],
            equipment_data['modelo'],
            equipment_data['categoria'],
            equipment_data['tensao'],
            equipment_data['potencia'],
            equipment_data['corrente_eletrica'],
            equipment_data['status'],
            equipment_data['localizacao'],
            equipment_data['responsavel'],
            equipment_data['observacoes'],
            equipment_id
        )
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao atualizar equipamento: {e}")
        return False

def delete_equipment(equipment_id):
    """Deletar equipamento"""
    db = get_database()
    
    try:
        return db.execute_update("DELETE FROM equipamentos WHERE id = ?", (equipment_id,))
    except Exception as e:
        st.error(f"Erro ao deletar equipamento: {e}")
        return False

def show_equipment_table(df):
    """Exibir tabela de equipamentos"""
    if df.empty:
        st.info("📭 Nenhum equipamento encontrado com os filtros aplicados")
        return
    
    # Configurar colunas para exibição
    df_display = df.copy()
    
    # Formatar dados para melhor visualização
    df_display['Código'] = df['codigo']
    df_display['Descrição'] = df['descricao'].str[:50] + '...' if len(df['descricao'].iloc[0]) > 50 else df['descricao']
    df_display['Marca/Modelo'] = df['marca'] + ' / ' + df['modelo']
    df_display['Categoria'] = df['categoria']
    df_display['Status'] = df['status']
    df_display['Localização'] = df['localizacao']
    df_display['Responsável'] = df['responsavel']
    
    # Colunas a exibir
    columns_to_show = ['Código', 'Descrição', 'Marca/Modelo', 'Categoria', 'Status', 'Localização', 'Responsável']
    
    # Criar colunas para tabela e ações
    col_table, col_actions = st.columns([4, 1])
    
    with col_table:
        # Usar data_editor para permitir seleção
        edited_df = st.data_editor(
            df_display[columns_to_show],
            hide_index=True,
            use_container_width=True,
            disabled=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Disponível", "Em uso", "Em manutenção", "Inativo"],
                    disabled=True
                )
            }
        )
    
    with col_actions:
        st.markdown("#### Ações")
        
        # Seletor de equipamento para ações
        if not df.empty:
            selected_equipment = st.selectbox(
                "Selecionar:",
                options=range(len(df)),
                format_func=lambda x: f"{df.iloc[x]['codigo']} - {df.iloc[x]['descricao'][:20]}...",
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
                if st.session_state.get('confirm_delete') != equipment_data['id']:
                    st.session_state.confirm_delete = equipment_data['id']
                    st.warning("⚠️ Clique novamente para confirmar exclusão")
                else:
                    if delete_equipment(equipment_data['id']):
                        st.success("✅ Equipamento excluído com sucesso!")
                        del st.session_state.confirm_delete
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir equipamento!")

def show():
    """Função principal da página Equipamentos Elétricos"""
    
    # Verificar autenticação
    auth = get_auth()
    auth.require_auth()
    
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
            em_uso = len(df[df['status'] == 'Em uso'])
            st.metric("Em Uso", em_uso)
        
        with col4:
            manutencao = len(df[df['status'] == 'Em manutenção'])
            st.metric("Em Manutenção", manutencao, delta_color="inverse")
        
        st.markdown("---")
        
        # Exibir tabela
        st.markdown(f"### 📋 Lista de Equipamentos ({len(df_filtered)} encontrados)")
        show_equipment_table(df_filtered)
        
    else:
        st.warning("⚠️ Nenhum equipamento encontrado no banco de dados")
        st.info("Use o botão 'Novo Equipamento' para adicionar o primeiro equipamento")

if __name__ == "__main__":
    show()