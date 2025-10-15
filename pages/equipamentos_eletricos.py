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
    
    # Container para o formulário com melhor design
    with st.container():
        st.markdown(f"### {form_title}")
        
        # Exibir informações do equipamento sendo editado
        if edit_mode and equipment_data:
            st.info(f"🔧 **Editando equipamento:** {equipment_data.get('codigo', 'N/A')} - {equipment_data.get('nome', 'N/A')}")
        
        with st.form("equipment_form", clear_on_submit=not edit_mode, border=True):
            
            # Seção 1: Identificação
            st.markdown("#### 📝 Informações Básicas")
            col1, col2 = st.columns(2)
            
            with col1:
                codigo = st.text_input(
                    "Código *",
                    value=equipment_data.get('codigo', '') if equipment_data else '',
                    help="Código único do equipamento (não pode ser alterado após criação)",
                    disabled=edit_mode,  # Não permitir editar código
                    placeholder="Ex: ELT001, FUR002, etc."
                )
                
                nome = st.text_area(
                    "Nome/Descrição *",
                    value=equipment_data.get('nome', '') if equipment_data else '',
                    height=100,
                    help="Nome/Descrição detalhada do equipamento",
                    placeholder="Descreva o equipamento de forma clara e objetiva"
                )
            
            with col2:
                categoria = st.selectbox(
                    "Categoria *",
                    get_categories(),
                    index=get_categories().index(equipment_data.get('categoria', 'Outros')) if equipment_data and equipment_data.get('categoria') in get_categories() else 0,
                    help="Categoria do equipamento para melhor organização"
                )
                
                status = st.selectbox(
                    "Status *",
                    ["Disponível", "Em uso", "Em manutenção", "Inativo"],
                    index=["Disponível", "Em uso", "Em manutenção", "Inativo"].index(equipment_data.get('status', 'Disponível')) if equipment_data else 0,
                    help="Status atual do equipamento"
                )
            
            # Seção 2: Localização e Observações
            st.markdown("#### 📍 Localização e Detalhes")
            col3, col4 = st.columns([1, 2])
            
            with col3:
                localizacao = st.selectbox(
                    "Localização *",
                    get_locations(),
                    index=get_locations().index(equipment_data.get('localizacao', 'Não Definido')) if equipment_data and equipment_data.get('localizacao') in get_locations() else len(get_locations())-1,
                    help="Local onde o equipamento está armazenado"
                )
            
            with col4:
                observacoes = st.text_area(
                    "Observações",
                    value=equipment_data.get('observacoes', '') if equipment_data else '',
                    height=80,
                    help="Informações adicionais, condições, restrições, etc.",
                    placeholder="Observações importantes sobre o equipamento..."
                )
        
            # Botões do formulário
            st.markdown("---")
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
            
            # Processar ações dos botões
            if cancel_button:
                st.session_state.show_add_form = False
                st.session_state.edit_equipment = None
                st.rerun()
            
            if submit_button:
                # Validações detalhadas
                errors = []
                
                if not codigo or not codigo.strip():
                    errors.append("Código é obrigatório")
                elif len(codigo.strip()) < 3:
                    errors.append("Código deve ter pelo menos 3 caracteres")
                
                if not nome or not nome.strip():
                    errors.append("Nome/Descrição é obrigatório")
                elif len(nome.strip()) < 5:
                    errors.append("Nome/Descrição deve ter pelo menos 5 caracteres")
                
                if not categoria or categoria == "":
                    errors.append("Categoria é obrigatória")
                
                if not status or status == "":
                    errors.append("Status é obrigatório")
                
                if not localizacao or localizacao == "":
                    errors.append("Localização é obrigatória")
                
                # Verificar se código já existe (apenas para novos equipamentos)
                if not edit_mode and codigo and codigo.strip():
                    existing_equipment = get_equipment_by_code(codigo.strip())
                    if existing_equipment:
                        errors.append(f"Já existe um equipamento com o código '{codigo.strip()}'")
                
                # Exibir erros se houver
                if errors:
                    st.error("❌ **Corrija os seguintes erros:**")
                    for error in errors:
                        st.error(f"• {error}")
                    return
                
                # Preparar dados validados
                equipment_data_to_save = {
                    'codigo': codigo.strip(),
                    'nome': nome.strip(),
                    'categoria': categoria,
                    'status': status,
                    'localizacao': localizacao,
                    'observacoes': observacoes.strip() if observacoes else ''
                }
                
                # Salvar no banco
                try:
                    if edit_mode and equipment_data:
                        success = update_equipment(equipment_data['codigo'], equipment_data_to_save)
                        if success:
                            st.success("✅ **Equipamento atualizado com sucesso!**")
                            st.balloons()
                            st.session_state.edit_equipment = None
                            st.rerun()
                        else:
                            st.error("❌ **Erro ao atualizar equipamento!** Tente novamente.")
                    else:
                        success = add_equipment(equipment_data_to_save)
                        if success:
                            st.success("✅ **Equipamento adicionado com sucesso!**")
                            st.balloons()
                            st.session_state.show_add_form = False
                            st.rerun()
                        else:
                            st.error("❌ **Erro ao adicionar equipamento!** Verifique se o código não está duplicado.")
                except Exception as e:
                    st.error(f"❌ **Erro inesperado:** {str(e)}")
                    st.error("Por favor, tente novamente ou contate o administrador.")

def get_equipment_by_code(codigo: str) -> Optional[Dict[str, Any]]:
    """Buscar equipamento por código"""
    db = DatabaseConnection()
    
    try:
        query = "SELECT * FROM equipamentos_eletricos WHERE codigo = ?"
        result = db.execute_query(query, (codigo,))
        
        if result and len(result) > 0:
            columns = ['id', 'codigo', 'nome', 'categoria', 'status', 'localizacao', 'observacoes', 'created_at', 'updated_at']
            return dict(zip(columns, result[0]))
        return None
    except Exception as e:
        st.error(f"Erro ao buscar equipamento: {e}")
        return None
    finally:
        db.close()

def add_equipment(equipment_data: Dict[str, Any]) -> bool:
    """Adicionar novo equipamento com logging"""
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
        
        success = db.execute_update(query, params)
        
        if success:
            # Log da operação
            from utils.logging import log_crud
            log_crud(
                'create', 
                'equipamentos_eletricos', 
                equipment_data['codigo'],
                f"Equipamento elétrico criado: {equipment_data['nome']}",
                new_data=equipment_data
            )
        
        return success
        
    except Exception as e:
        st.error(f"Erro ao adicionar equipamento: {e}")
        return False

def update_equipment(equipment_id: str, equipment_data: Dict[str, Any]) -> bool:
    """Atualizar equipamento existente com logging"""
    db = DatabaseConnection()
    
    try:
        # Buscar dados antigos para log
        old_data_query = "SELECT * FROM equipamentos_eletricos WHERE codigo = ?"
        old_result = db.execute_query(old_data_query, (equipment_id,))
        old_data = old_result[0] if old_result else None
        
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
        
        success = db.execute_update(query, params)
        
        if success and old_data:
            # Log da operação
            from utils.logging import log_crud
            log_crud(
                'update', 
                'equipamentos_eletricos', 
                equipment_id,
                f"Equipamento elétrico atualizado: {equipment_data['nome']}",
                old_data=dict(old_data),
                new_data=equipment_data
            )
        
        return success
        
    except Exception as e:
        st.error(f"Erro ao atualizar equipamento: {e}")
        return False

def delete_equipment(equipment_id: str) -> bool:
    """Deletar equipamento com logging"""
    db = DatabaseConnection()
    
    try:
        # Buscar dados antes de deletar para log
        old_data_query = "SELECT * FROM equipamentos_eletricos WHERE codigo = ?"
        old_result = db.execute_query(old_data_query, (equipment_id,))
        old_data = old_result[0] if old_result else None
        
        success = db.execute_update("DELETE FROM equipamentos_eletricos WHERE codigo = ?", (equipment_id,))
        
        if success and old_data:
            # Log da operação
            from utils.logging import log_crud
            log_crud(
                'delete', 
                'equipamentos_eletricos', 
                equipment_id,
                f"Equipamento elétrico excluído: {old_data.get('nome', 'N/A')}",
                old_data=dict(old_data)
            )
        
        return success
        
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
            
            # Obter autenticação para verificar permissões
            auth = get_auth()
            
            # Botões de ação - Layout vertical melhorado
            st.markdown("##### 🛠️ Ações do Equipamento")
            
            # Botões baseados em permissões
            if auth.has_permission('usuario'):
                if st.button("✏️ Editar Equipamento", use_container_width=True, type="primary"):
                    st.session_state.edit_equipment = equipment_data
                    st.rerun()
            else:
                st.button("✏️ Editar Equipamento", use_container_width=True, disabled=True,
                         help="Permissão insuficiente (necessário: usuário)")
            
            if auth.has_permission('visualizador'):
                if st.button("🔄 Movimentar Equipamento", use_container_width=True):
                    st.session_state.move_equipment = equipment_data
                    st.rerun()
            else:
                st.button("🔄 Movimentar Equipamento", use_container_width=True, disabled=True,
                         help="Permissão insuficiente (necessário: visualizador)")
            
            if auth.has_permission('admin'):
                if st.button("🗑️ Excluir Equipamento", use_container_width=True, type="secondary"):
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
            else:
                st.button("🗑️ Excluir Equipamento", use_container_width=True, disabled=True,
                         help="Permissão insuficiente (necessário: admin)")

def show():
    """Função principal da página Equipamentos Elétricos"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    # Verificar permissões básicas
    if not auth.require_role('visualizador'):
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
        if auth.has_permission('usuario'):
            if st.button("➕ Novo Equipamento", use_container_width=True, type="primary"):
                st.session_state.show_add_form = True
                st.rerun()
        else:
            st.button("➕ Novo Equipamento", use_container_width=True, disabled=True, 
                     help="Permissão insuficiente (necessário: usuário)")
        
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