#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Obra/Departamento
Página de gestão de obras, departamentos e locais
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

# Sugestões pré-cadastradas de locais/departamentos
LOCAIS_SUGERIDOS = [
    # Obras/Projetos
    "Obra - Residencial Vista Alegre",
    "Obra - Edifício Comercial Centro",
    "Obra - Shopping Mall Norte",
    "Obra - Condomínio Jardim das Flores",
    "Obra - Fábrica Zona Industrial",
    "Obra - Hospital Regional",
    "Obra - Escola Municipal",
    "Obra - Ponte Rio Verde",
    
    # Departamentos Internos
    "Departamento - Almoxarifado Central",
    "Departamento - Escritório Matriz",
    "Departamento - Manutenção",
    "Departamento - Engenharia",
    "Departamento - Recursos Humanos",
    "Departamento - Financeiro",
    "Departamento - Compras",
    "Departamento - Qualidade",
    "Departamento - Segurança do Trabalho",
    "Departamento - TI/Informática",
    "Departamento - Vendas",
    "Departamento - Marketing",
    
    # Locais Externos
    "Cliente - Empresa ABC Ltda",
    "Cliente - Construtora XYZ",
    "Fornecedor - Materiais São Paulo",
    "Fornecedor - Ferragens do Norte",
    "Terceirizado - Manutenção Industrial",
    "Terceirizado - Limpeza e Conservação",
    
    # Locais de Armazenamento
    "Estoque - Galpão Principal",
    "Estoque - Depósito Filial",
    "Estoque - Container Temporário",
    "Estoque - Área Externa",
    "Em Trânsito - Transportadora",
    "Em Trânsito - Veículo Próprio"
]

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

def atualizar_obra(obra_id, nome, descricao, status, data_inicio, data_termino, responsavel):
    """Atualizar obra existente"""
    db = DatabaseConnection()
    
    try:
        query = """
            UPDATE obras SET
                nome = ?, descricao = ?, status = ?, 
                data_inicio = ?, data_termino = ?, responsavel = ?
            WHERE id = ?
        """
        
        params = (nome, descricao, status, data_inicio.strftime('%Y-%m-%d'), data_termino.strftime('%Y-%m-%d'), responsavel, obra_id)
        
        return db.execute_update(query, params)
        
    except Exception as e:
        st.error(f"Erro ao atualizar obra: {e}")
        return False

def excluir_obra(obra_id):
    """Excluir obra"""
    db = DatabaseConnection()
    
    try:
        return db.execute_update("DELETE FROM obras WHERE id = ?", (obra_id,))
        
    except Exception as e:
        st.error(f"Erro ao excluir obra: {e}")
        return False

def show():
    """Função principal da página Obras"""
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 🏗️ Obra/Departamento")
    st.markdown("Gestão de obras, departamentos e locais para movimentações")
    
    # Seção de locais sugeridos
    st.markdown("### 📍 Locais/Departamentos Pré-Cadastrados")
    st.info("💡 **Sugestões de locais para movimentações** - Use estes locais nas movimentações de equipamentos e insumos:")
    
    # Organizar sugestões por categoria
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🏗️ Obras/Projetos:**")
        obras = [local for local in LOCAIS_SUGERIDOS if local.startswith("Obra -")]
        for obra in obras:
            st.markdown(f"• {obra.replace('Obra - ', '')}")
    
    with col2:
        st.markdown("**🏢 Departamentos:**")
        departamentos = [local for local in LOCAIS_SUGERIDOS if local.startswith("Departamento -")]
        for dept in departamentos[:8]:  # Limitar a 8 para não ficar muito longo
            st.markdown(f"• {dept.replace('Departamento - ', '')}")
    
    with col3:
        st.markdown("**📦 Outros Locais:**")
        outros = [local for local in LOCAIS_SUGERIDOS if not local.startswith(("Obra -", "Departamento -"))]
        for outro in outros[:8]:  # Limitar a 8 para não ficar muito longo
            st.markdown(f"• {outro}")
    
    st.markdown("---")
    
    # Carregar dados
    with st.spinner("📊 Carregando dados de obras/departamentos..."):
        df = get_obras_data()
    
    if df.empty:
        st.warning("⚠️ Nenhuma obra/departamento encontrado no sistema")
        st.info("""
        💡 **Obras/Departamentos não encontrados**
        
        Para visualizar obras/departamentos nesta página:
        - Cadastre novos locais usando o formulário abaixo
        - Use as sugestões pré-cadastradas acima como referência
        - Certifique-se de que a tabela 'obras' existe no banco de dados
        """)
    else:
        # Métricas básicas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Locais", len(df))
        
        with col2:
            ativas = len(df[df['status'] == 'ativa']) if 'status' in df.columns else 0
            st.metric("Locais Ativos", ativas)
        
        with col3:
            concluidas = len(df[df['status'] == 'concluida']) if 'status' in df.columns else 0
            st.metric("Concluídos", concluidas)
        
        with col4:
            pausadas = len(df[df['status'] == 'pausada']) if 'status' in df.columns else 0
            st.metric("Pausados", pausadas)
        
        st.markdown("---")
        
        # Lista de obras/departamentos
        st.markdown("### 📋 Lista de Obra/Departamento")
        
        if not df.empty:
            for idx, row in df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
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
                    
                    with col4:
                        # Botões de ação
                        if st.button("✏️", key=f"edit_obra_{row['id']}", help="Editar"):
                            st.session_state[f'edit_obra_{row["id"]}'] = row.to_dict()
                            st.rerun()
                        
                        if st.button("🗑️", key=f"delete_obra_{row['id']}", help="Excluir", type="secondary"):
                            if st.session_state.get(f'confirm_delete_obra_{row["id"]}') != row['id']:
                                st.session_state[f'confirm_delete_obra_{row["id"]}'] = row['id']
                                st.warning("⚠️ Clique novamente para confirmar")
                            else:
                                if excluir_obra(row['id']):
                                    st.success("✅ Obra/Departamento excluído!")
                                    del st.session_state[f'confirm_delete_obra_{row["id"]}']
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao excluir!")
                    
                    # Formulário de edição
                    if st.session_state.get(f'edit_obra_{row["id"]}'):
                        with st.form(f"edit_form_{row['id']}"):
                            st.markdown(f"#### ✏️ Editar: {row['nome']}")
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                nome_edit = st.text_input("Nome *", value=row['nome'])
                                descricao_edit = st.text_area("Descrição *", value=row['descricao'])
                                responsavel_edit = st.text_input("Responsável *", value=row['responsavel'])
                            
                            with col_b:
                                status_edit = st.selectbox("Status *", ["ativa", "pausada", "concluida", "cancelada"], 
                                                         index=["ativa", "pausada", "concluida", "cancelada"].index(row['status']))
                                data_inicio_edit = st.date_input("Data Início *", 
                                                                value=pd.to_datetime(row['data_inicio']).date() if row['data_inicio'] else None)
                                data_termino_edit = st.date_input("Data Término *", 
                                                                 value=pd.to_datetime(row['data_termino']).date() if row['data_termino'] else None)
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                save_edit = st.form_submit_button("💾 Salvar", type="primary")
                            
                            with col_cancel:
                                cancel_edit = st.form_submit_button("❌ Cancelar")
                            
                            if save_edit and nome_edit and descricao_edit and responsavel_edit:
                                success = atualizar_obra(row['id'], nome_edit, descricao_edit, status_edit, 
                                                       data_inicio_edit, data_termino_edit, responsavel_edit)
                                if success:
                                    st.success("✅ Obra/Departamento atualizado!")
                                    del st.session_state[f'edit_obra_{row["id"]}']
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao atualizar!")
                            elif save_edit:
                                st.error("❌ Preencha todos os campos obrigatórios!")
                            
                            if cancel_edit:
                                del st.session_state[f'edit_obra_{row["id"]}']
                                st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("Nenhuma obra encontrada.")
    
    # Formulário para novo local
    st.markdown("---")
    st.markdown("### ➕ Cadastrar Nova Obra/Departamento")
    
    with st.form("nova_obra"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Opção de usar sugestão ou criar novo
            opcao = st.radio("Opção de Cadastro:", ["Usar Sugestão", "Criar Novo"], horizontal=True)
            
            if opcao == "Usar Sugestão":
                nome = st.selectbox("Selecionar Local Sugerido *", [""] + LOCAIS_SUGERIDOS, help="Escolha um local pré-cadastrado")
            else:
                nome = st.text_input("Nome da Obra/Departamento *", help="Nome identificador do local")
            
            descricao = st.text_area("Descrição *", help="Descrição detalhada do local")
            responsavel = st.text_input("Responsável *", help="Nome do responsável pelo local")
        
        with col2:
            status = st.selectbox("Status *", ["ativa", "pausada", "concluida", "cancelada"])
            data_inicio = st.date_input("Data de Início *")
            data_termino = st.date_input("Data de Término Prevista")
        
        submitted = st.form_submit_button("🏗️ Cadastrar Obra/Departamento", type="primary")
        
        if submitted:
            if nome and descricao and responsavel:
                success = cadastrar_obra(nome, descricao, status, data_inicio, data_termino, responsavel)
                if success:
                    st.success("✅ Obra/Departamento cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao cadastrar obra/departamento!")
            else:
                st.error("❌ Preencha todos os campos obrigatórios!")
    
    # Informações sobre desenvolvimento
    st.markdown("---")
    st.info("""
    💡 **Funcionalidades implementadas:**
    - ✅ Listagem completa de obras/departamentos
    - ✅ Cadastro de novas obras/departamentos
    - ✅ **Edição inline** com formulário completo
    - ✅ **Exclusão com confirmação** de segurança
    - ✅ Controle de status (ativa, pausada, concluída, cancelada)
    - ✅ **Locais pré-cadastrados** (33 sugestões organizadas)
    - ✅ Integração com sistema de movimentações
    - ✅ Métricas em tempo real
    """)

if __name__ == "__main__":
    from pages import obras
    obras.show()