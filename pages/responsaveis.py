#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Cadastro de Responsáveis
Gerenciamento completo (CRUD) de responsáveis pelas movimentações
"""

import streamlit as st
from utils.global_css import apply_global_css, force_light_theme
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

def get_responsaveis():
    """Carregar lista de responsáveis"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                id, nome, cpf, telefone, email, setor, cargo, ativo, 
                observacoes, created_at
            FROM responsaveis
            ORDER BY ativo DESC, nome ASC
        """
        
        result = db.execute_query(query)
        
        if result:
            return pd.DataFrame(result)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao carregar responsáveis: {e}")
        return pd.DataFrame()

def adicionar_responsavel(nome, cpf, telefone, email, setor, cargo, observacoes):
    """Adicionar novo responsável"""
    db = DatabaseConnection()
    
    try:
        query = """
            INSERT INTO responsaveis (nome, cpf, telefone, email, setor, cargo, ativo, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """
        
        success = db.execute_update(query, (nome, cpf, telefone, email, setor, cargo, observacoes))
        
        if success:
            # Log de auditoria
            from utils.logging import log_action
            log_action(
                "responsavel_criado",
                f"Novo responsável cadastrado: {nome} - {cargo}",
                user_id=get_auth().get_current_user()['id']
            )
        
        return success
        
    except Exception as e:
        st.error(f"Erro ao adicionar responsável: {e}")
        return False

def editar_responsavel(responsavel_id, nome, cpf, telefone, email, setor, cargo, observacoes):
    """Editar responsável existente"""
    db = DatabaseConnection()
    
    try:
        query = """
            UPDATE responsaveis 
            SET nome = ?, cpf = ?, telefone = ?, email = ?, setor = ?, cargo = ?, observacoes = ?
            WHERE id = ?
        """
        
        success = db.execute_update(query, (nome, cpf, telefone, email, setor, cargo, observacoes, responsavel_id))
        
        if success:
            # Log de auditoria
            from utils.logging import log_action
            log_action(
                "responsavel_editado",
                f"Responsável editado: {nome} (ID: {responsavel_id})",
                user_id=get_auth().get_current_user()['id']
            )
        
        return success
        
    except Exception as e:
        st.error(f"Erro ao editar responsável: {e}")
        return False

def ativar_desativar_responsavel(responsavel_id, ativo):
    """Ativar ou desativar responsável"""
    db = DatabaseConnection()
    
    try:
        query = "UPDATE responsaveis SET ativo = ? WHERE id = ?"
        success = db.execute_update(query, (ativo, responsavel_id))
        
        if success:
            # Log de auditoria
            from utils.logging import log_action
            acao = "ativado" if ativo else "desativado"
            log_action(
                f"responsavel_{acao}",
                f"Responsável {acao} (ID: {responsavel_id})",
                user_id=get_auth().get_current_user()['id']
            )
        
        return success
        
    except Exception as e:
        st.error(f"Erro ao alterar status: {e}")
        return False

def show():
    """Função principal da página Responsáveis"""
    
    # Aplicar CSS
    apply_global_css()
    force_light_theme()
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown("## 👥 Cadastro de Responsáveis")
    st.markdown("Gerenciamento de pessoas responsáveis pelas movimentações")
    
    # Tabs para organização
    tab1, tab2 = st.tabs(["📋 Lista de Responsáveis", "➕ Novo Responsável"])
    
    with tab1:
        # Carregar dados
        with st.spinner("📊 Carregando responsáveis..."):
            df = get_responsaveis()
        
        if df.empty:
            st.warning("⚠️ Nenhum responsável cadastrado no sistema")
            st.info("💡 Use a aba 'Novo Responsável' para cadastrar")
        else:
            # Filtros
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                mostrar = st.radio(
                    "Mostrar:",
                    ["Apenas Ativos", "Apenas Inativos", "Todos"],
                    horizontal=True
                )
            
            # Aplicar filtro
            if mostrar == "Apenas Ativos":
                df_filtrado = df[df['ativo'] == 1]
            elif mostrar == "Apenas Inativos":
                df_filtrado = df[df['ativo'] == 0]
            else:
                df_filtrado = df
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Responsáveis", len(df))
            
            with col2:
                ativos = len(df[df['ativo'] == 1])
                st.metric("Ativos", ativos, delta=None if ativos == 0 else "")
            
            with col3:
                inativos = len(df[df['ativo'] == 0])
                st.metric("Inativos", inativos)
            
            st.markdown("---")
            
            # Lista de responsáveis
            for idx, row in df_filtrado.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        status_emoji = "✅" if row['ativo'] else "❌"
                        st.markdown(f"{status_emoji} **{row['nome']}**")
                        if row.get('cargo'):
                            st.caption(f"🏷️ {row['cargo']}")
                    
                    with col2:
                        if row.get('setor'):
                            st.markdown(f"🏢 {row['setor']}")
                        if row.get('telefone'):
                            st.caption(f"📞 {row['telefone']}")
                    
                    with col3:
                        if row.get('email'):
                            st.caption(f"📧 {row['email']}")
                        if row.get('cpf'):
                            st.caption(f"🆔 {row['cpf']}")
                    
                    with col4:
                        # Botões de ação
                        col_editar, col_status = st.columns(2)
                        
                        with col_editar:
                            if st.button("✏️ Editar", key=f"edit_{row['id']}"):
                                st.session_state[f'editar_{row["id"]}'] = True
                                st.rerun()
                        
                        with col_status:
                            if row['ativo']:
                                if st.button("🔴 Desativar", key=f"deactivate_{row['id']}"):
                                    if ativar_desativar_responsavel(row['id'], 0):
                                        st.success("✅ Responsável desativado!")
                                        st.rerun()
                            else:
                                if st.button("🟢 Ativar", key=f"activate_{row['id']}"):
                                    if ativar_desativar_responsavel(row['id'], 1):
                                        st.success("✅ Responsável ativado!")
                                        st.rerun()
                    
                    # Formulário de edição
                    if st.session_state.get(f'editar_{row["id"]}', False):
                        with st.form(f"form_edit_{row['id']}"):
                            st.markdown("#### Editar Responsável")
                            
                            col_e1, col_e2 = st.columns(2)
                            
                            with col_e1:
                                nome_edit = st.text_input("Nome *", value=row['nome'])
                                cpf_edit = st.text_input("CPF", value=row.get('cpf', ''))
                                telefone_edit = st.text_input("Telefone", value=row.get('telefone', ''))
                            
                            with col_e2:
                                cargo_edit = st.text_input("Cargo", value=row.get('cargo', ''))
                                setor_edit = st.text_input("Setor", value=row.get('setor', ''))
                                email_edit = st.text_input("E-mail", value=row.get('email', ''))
                            
                            obs_edit = st.text_area("Observações", value=row.get('observacoes', ''))
                            
                            col_salvar, col_cancelar = st.columns(2)
                            
                            with col_salvar:
                                if st.form_submit_button("💾 Salvar", type="primary"):
                                    if nome_edit:
                                        if editar_responsavel(row['id'], nome_edit, cpf_edit, telefone_edit, 
                                                            email_edit, setor_edit, cargo_edit, obs_edit):
                                            st.success("✅ Responsável atualizado!")
                                            del st.session_state[f'editar_{row["id"]}']
                                            st.rerun()
                                    else:
                                        st.error("❌ Nome é obrigatório!")
                            
                            with col_cancelar:
                                if st.form_submit_button("🔙 Cancelar"):
                                    del st.session_state[f'editar_{row["id"]}']
                                    st.rerun()
                    
                    if row.get('observacoes'):
                        st.caption(f"💬 {row['observacoes']}")
                    
                    st.markdown("---")
    
    with tab2:
        st.markdown("### Cadastrar Novo Responsável")
        
        with st.form("novo_responsavel"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *", help="Nome do responsável")
                cpf = st.text_input("CPF", help="CPF do responsável (opcional)")
                telefone = st.text_input("Telefone", placeholder="(11) 98888-9999", help="Telefone de contato")
            
            with col2:
                cargo = st.text_input("Cargo", placeholder="Ex: Técnico, Coordenador, Engenheiro", help="Cargo do responsável")
                setor = st.text_input("Setor", placeholder="Ex: Manutenção, Obras, Logística", help="Setor de atuação")
                email = st.text_input("E-mail", placeholder="nome@empresa.com", help="E-mail corporativo")
            
            observacoes = st.text_area("Observações", help="Informações adicionais sobre o responsável")
            
            submitted = st.form_submit_button("➕ Cadastrar Responsável", type="primary")
            
            if submitted:
                if nome:
                    if adicionar_responsavel(nome, cpf, telefone, email, setor, cargo, observacoes):
                        st.success(f"✅ Responsável '{nome}' cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao cadastrar responsável!")
                else:
                    st.error("❌ O nome é obrigatório!")
    
    # Informações
    st.markdown("---")
    st.info("""
    💡 **Sobre Responsáveis:**
    - Responsáveis são pessoas autorizadas a fazer movimentações
    - Apenas responsáveis **ativos** aparecem nas movimentações
    - É obrigatório selecionar um responsável para registrar movimentações
    - Desativar um responsável não apaga o histórico de movimentações
    """)

if __name__ == "__main__":
    show()
