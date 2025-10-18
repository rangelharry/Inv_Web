#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Equipamentos Manuais
Página de gestão de equipamentos manuais com CRUD completo
"""

import streamlit as st
from utils.global_css import apply_global_css, force_light_theme
import sys
import os
import pandas as pd
from datetime import datetime
import uuid

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import DatabaseConnection
from utils.auth import get_auth, check_authentication
from utils.logging import SystemLogger

# Verificar autenticação quando acessado diretamente
if not check_authentication():
    st.stop()

# Configurações globais
TIPOS_EQUIPAMENTO = ["Ferramenta Manual", "Ferramenta Elétrica", "Instrumento de Medida", "EPI", "Outros"]
ESTADOS_EQUIPAMENTO = ["Novo", "Usado - Bom Estado", "Usado - Estado Regular", "Danificado", "Descartado"]
STATUS_EQUIPAMENTO = ["Disponível", "Em Uso", "Manutenção", "Inativo", "Emprestado"]

logger = SystemLogger()

def get_equipamentos_manuais_data():
    """Carregar dados dos equipamentos manuais"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                codigo, descricao, tipo, status, localizacao, quantitativo, 
                estado, marca, valor, data_compra, loja, observacoes
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

def get_next_codigo():
    """Gerar próximo código para equipamento manual"""
    db = DatabaseConnection()
    try:
        result = db.execute_query("SELECT MAX(CAST(SUBSTR(codigo, 5) AS INTEGER)) as max_num FROM equipamentos_manuais WHERE codigo LIKE 'MAN-%'")
        if result and result[0]['max_num']:
            next_num = result[0]['max_num'] + 1
        else:
            next_num = 1
        return f"MAN-{next_num:04d}"
    except Exception as e:
        st.error(f"Erro ao gerar código: {e}")
        return f"MAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def create_equipamento_manual(dados):
    """Criar novo equipamento manual"""
    db = DatabaseConnection()
    
    try:
        query = """
            INSERT INTO equipamentos_manuais 
            (codigo, descricao, tipo, quantitativo, status, marca, valor, 
             data_compra, loja, localizacao, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            dados['codigo'], dados['descricao'], dados['tipo'], 
            dados['quantitativo'], dados['status'], dados['marca'],
            dados['valor'], dados['data_compra'], dados['loja'],
            dados['localizacao'], dados['observacoes']
        )
        
        result = db.execute_query(query, params)
        
        if result is not None:
            logger.log_crud_operation("CREATE", "equipamentos_manuais", dados['codigo'], f"Criado: {dados['descricao']}")
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Erro ao criar equipamento: {e}")
        return False

def update_equipamento_manual(codigo, dados):
    """Atualizar equipamento manual existente"""
    db = DatabaseConnection()
    
    try:
        query = """
            UPDATE equipamentos_manuais 
            SET descricao=?, tipo=?, quantitativo=?, status=?, marca=?, valor=?, 
                data_compra=?, loja=?, localizacao=?, observacoes=?
            WHERE codigo=?
        """
        
        params = (
            dados['descricao'], dados['tipo'], dados['quantitativo'], 
            dados['status'], dados['marca'], dados['valor'],
            dados['data_compra'], dados['loja'], 
            dados['localizacao'], dados['observacoes'], codigo
        )
        
        result = db.execute_query(query, params)
        
        if result is not None:
            logger.log_crud_operation("UPDATE", "equipamentos_manuais", codigo, f"Atualizado: {dados['descricao']}")
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Erro ao atualizar equipamento: {e}")
        return False

def delete_equipamento_manual(codigo):
    """Excluir equipamento manual"""
    db = DatabaseConnection()
    
    try:
        # Verificar se equipamento está em uso
        check_query = "SELECT status FROM equipamentos_manuais WHERE codigo = ?"
        result = db.execute_query(check_query, (codigo,))
        
        if result and result[0]['status'] in ['Em Uso', 'Emprestado']:
            st.error("❌ Não é possível excluir equipamento em uso ou emprestado!")
            return False
        
        # Excluir equipamento
        query = "DELETE FROM equipamentos_manuais WHERE codigo = ?"
        result = db.execute_query(query, (codigo,))
        
        if result is not None:
            logger.log_crud_operation("DELETE", "equipamentos_manuais", codigo, f"Excluído: {codigo}")
            return True
        
        return False
        
    except Exception as e:
        st.error(f"Erro ao excluir equipamento: {e}")
        return False

def get_equipamento_by_codigo(codigo):
    """Buscar equipamento por código"""
    db = DatabaseConnection()
    
    try:
        query = "SELECT * FROM equipamentos_manuais WHERE codigo = ?"
        result = db.execute_query(query, (codigo,))
        
        if result:
            return result[0]
        return None
        
    except Exception as e:
        st.error(f"Erro ao buscar equipamento: {e}")
        return None

def show_create_form():
    """Formulário para criar novo equipamento manual"""
    with st.form("create_equipamento_form"):
        st.markdown("### ➕ Cadastrar Novo Equipamento Manual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("Código", value=get_next_codigo(), disabled=True)
            descricao = st.text_input("Descrição*", placeholder="Ex: Chave de Fenda 3/8")
            tipo = st.selectbox("Tipo*", TIPOS_EQUIPAMENTO)
            quantitativo = st.number_input("Quantidade*", min_value=1, value=1)
            estado = st.selectbox("Estado*", ESTADOS_EQUIPAMENTO)
            marca = st.text_input("Marca", placeholder="Ex: Bosch, Makita...")
        
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            data_compra = st.date_input("Data de Compra")
            loja = st.text_input("Loja/Fornecedor", placeholder="Ex: Loja de Ferramentas XYZ")
            status = st.selectbox("Status*", STATUS_EQUIPAMENTO)
            localizacao = st.text_input("Localização*", value="Almoxarifado", placeholder="Ex: Almoxarifado, Obra A...")
            observacoes = st.text_area("Observações", placeholder="Informações adicionais...")
        
        submitted = st.form_submit_button("✅ Cadastrar Equipamento", type="primary")
        
        if submitted:
            if not descricao or not tipo or not estado or not status or not localizacao:
                st.error("❌ Preencha todos os campos obrigatórios (*)")
                return
            
            dados = {
                'codigo': codigo,
                'descricao': descricao,
                'tipo': tipo,
                'quantitativo': quantitativo,
                'estado': estado,
                'marca': marca,
                'valor': valor if valor > 0 else None,
                'data_compra': data_compra.strftime('%Y-%m-%d') if data_compra else '',
                'loja': loja,
                'status': status,
                'localizacao': localizacao,
                'observacoes': observacoes
            }
            
            if create_equipamento_manual(dados):
                st.success(f"✅ Equipamento {codigo} cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar equipamento!")

def show_edit_form(equipamento):
    """Formulário para editar equipamento manual"""
    with st.form("edit_equipamento_form"):
        st.markdown(f"### ✏️ Editar Equipamento: {equipamento['codigo']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Código", value=equipamento['codigo'], disabled=True)
            descricao = st.text_input("Descrição*", value=equipamento['descricao'] or '')
            tipo = st.selectbox("Tipo*", TIPOS_EQUIPAMENTO, 
                              index=TIPOS_EQUIPAMENTO.index(equipamento['tipo']) if equipamento['tipo'] in TIPOS_EQUIPAMENTO else 0)
            quantitativo = st.number_input("Quantidade*", min_value=1, value=int(equipamento['quantitativo']) if equipamento['quantitativo'] else 1)
            estado = st.selectbox("Estado*", ESTADOS_EQUIPAMENTO,
                                index=ESTADOS_EQUIPAMENTO.index(equipamento['estado']) if equipamento['estado'] in ESTADOS_EQUIPAMENTO else 0)
            marca = st.text_input("Marca", value=equipamento['marca'] or '')
        
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, value=float(equipamento['valor']) if equipamento['valor'] else 0.0, format="%.2f")
            
            # Data de compra
            data_compra_atual = None
            if equipamento['data_compra']:
                try:
                    data_compra_atual = datetime.strptime(equipamento['data_compra'], '%Y-%m-%d').date()
                except:
                    data_compra_atual = None
            
            data_compra = st.date_input("Data de Compra", value=data_compra_atual)
            loja = st.text_input("Loja/Fornecedor", value=equipamento['loja'] or '')
            status = st.selectbox("Status*", STATUS_EQUIPAMENTO,
                                index=STATUS_EQUIPAMENTO.index(equipamento['status']) if equipamento['status'] in STATUS_EQUIPAMENTO else 0)
            localizacao = st.text_input("Localização*", value=equipamento['localizacao'] or '')
            observacoes = st.text_area("Observações", value=equipamento['observacoes'] or '')
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            submitted = st.form_submit_button("💾 Salvar Alterações", type="primary")
        
        with col_cancel:
            cancelled = st.form_submit_button("❌ Cancelar")
        
        if submitted:
            if not descricao or not tipo or not estado or not status or not localizacao:
                st.error("❌ Preencha todos os campos obrigatórios (*)")
                return
            
            dados = {
                'descricao': descricao,
                'tipo': tipo,
                'quantitativo': quantitativo,
                'estado': estado,
                'marca': marca,
                'valor': valor if valor > 0 else None,
                'data_compra': data_compra.strftime('%Y-%m-%d') if data_compra else '',
                'loja': loja,
                'status': status,
                'localizacao': localizacao,
                'observacoes': observacoes
            }
            
            if update_equipamento_manual(equipamento['codigo'], dados):
                st.success(f"✅ Equipamento {equipamento['codigo']} atualizado com sucesso!")
                st.session_state.pop('edit_equipamento', None)
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar equipamento!")
        
        if cancelled:
            st.session_state.pop('edit_equipamento', None)
            st.rerun()

def show_equipamentos_table(df):
    """Exibir tabela de equipamentos manuais com ações CRUD"""
    if df.empty:
        st.warning("Nenhum equipamento manual encontrado")
        return
    
    # Exibir dados com ações CRUD
    for idx, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{row['codigo']}** - {row['descricao']}")
                st.caption(f"📍 {row['localizacao']} | 🏷️ {row['tipo'] or 'Sem tipo'}")
            
            with col2:
                status_emoji = {"Disponível": "🟢", "Em Uso": "🟡", "Manutenção": "🔴", "Inativo": "⚫", "Emprestado": "🔵"}.get(row['status'], "⚪")
                st.markdown(f"{status_emoji} **{row['status']}**")
                if row['marca']:
                    st.caption(f"🏭 {row['marca']}")
            
            with col3:
                estado_emoji = {"Novo": "✨", "Usado - Bom Estado": "🔧", "Usado - Estado Regular": "⚙️", "Danificado": "⚠️", "Descartado": "🗑️"}.get(row['estado'], "❓")
                st.markdown(f"{estado_emoji} **{row['estado']}**")
                st.caption(f"Qtd: {row['quantitativo']}")
                if row['valor']:
                    try:
                        valor_float = float(row['valor'])
                        st.caption(f"💰 R$ {valor_float:.2f}")
                    except (ValueError, TypeError):
                        st.caption(f"💰 R$ {row['valor']}")
            
            with col4:
                col_actions1, col_actions2, col_actions3 = st.columns(3)
                
                with col_actions1:
                    if st.button("✏️", key=f"edit_{row['codigo']}", help="Editar"):
                        st.session_state['edit_equipamento'] = row['codigo']
                        st.rerun()
                
                with col_actions2:
                    if st.button("🔄", key=f"move_{row['codigo']}", help="Movimentar"):
                        st.session_state[f'show_move_{row["codigo"]}'] = True
                        st.rerun()
                
                with col_actions3:
                    if st.button("🗑️", key=f"delete_{row['codigo']}", help="Excluir"):
                        st.session_state[f'confirm_delete_{row["codigo"]}'] = True
                        st.rerun()
            
            # Confirmação de exclusão
            if st.session_state.get(f'confirm_delete_{row["codigo"]}', False):
                st.warning(f"⚠️ **Confirmar exclusão de {row['codigo']}?**")
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button("✅ Sim, excluir", key=f"confirm_yes_{row['codigo']}", type="primary"):
                        if delete_equipamento_manual(row['codigo']):
                            st.success(f"✅ Equipamento {row['codigo']} excluído!")
                            st.session_state.pop(f'confirm_delete_{row["codigo"]}', None)
                            st.rerun()
                        else:
                            st.error("❌ Erro ao excluir equipamento!")
                
                with col_cancel:
                    if st.button("❌ Cancelar", key=f"confirm_no_{row['codigo']}"):
                        st.session_state.pop(f'confirm_delete_{row["codigo"]}', None)
                        st.rerun()
            
            # Formulário de movimentação rápida
            if st.session_state.get(f'show_move_{row["codigo"]}', False):
                with st.form(f"move_form_{row['codigo']}"):
                    st.markdown(f"#### 🔄 Movimentar: {row['codigo']}")
                    
                    col_origem, col_destino, col_qtd = st.columns(3)
                    
                    with col_origem:
                        st.text_input("Origem", value=row['localizacao'], disabled=True)
                    
                    with col_destino:
                        # Locais comuns
                        locais_comuns = ["Almoxarifado", "Obra A", "Obra B", "Escritório", "Oficina", "Depósito"]
                        destino = st.selectbox("Novo Destino", locais_comuns)
                    
                    with col_qtd:
                        quantidade = st.number_input("Quantidade", min_value=1, max_value=int(row['quantitativo']), value=1)
                    
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
                            row['codigo'], 
                            row['localizacao'], 
                            destino, 
                            quantidade, 
                            responsavel
                        )
                        if success:
                            st.success(f"✅ Movimentação de {quantidade}x {row['codigo']} registrada!")
                            st.session_state.pop(f'show_move_{row["codigo"]}', None)
                            st.rerun()
                        else:
                            st.error("❌ Erro ao registrar movimentação!")
                    
                    elif submitted and not responsavel:
                        st.error("❌ Informe o responsável!")
                    
                    if cancelled:
                        st.session_state.pop(f'show_move_{row["codigo"]}', None)
                        st.rerun()
            
            st.divider()

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
    
    # FORÇAR TEMA CLARO - MODO EXTREMO
    apply_global_css()
    force_light_theme()
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    user = auth.get_current_user()
    
    st.markdown("## 🔧 Equipamentos Manuais")
    st.markdown("**CRUD Completo** - Gestão de ferramentas e equipamentos manuais")
    
    # Tabs para organizar as funcionalidades
    tab_list, tab_create, tab_manage = st.tabs(["📋 Listagem", "➕ Cadastrar", "⚙️ Gerenciar"])
    
    with tab_list:
        # Carregar dados
        with st.spinner("📊 Carregando equipamentos manuais..."):
            df = get_equipamentos_manuais_data()
        
        if not df.empty:
            # Métricas
            st.markdown("### 📊 Resumo Geral")
            show_metrics_manuais(df)
            
            st.divider()
            
            # Filtros
            st.markdown("### 🔍 Filtros")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Status:",
                    ["Todos"] + sorted(df['status'].dropna().unique()),
                    key="status_filter_manuais"
                )
            
            with col2:
                tipo_filter = st.selectbox(
                    "Tipo:",
                    ["Todos"] + sorted(df['tipo'].dropna().unique()),
                    key="tipo_filter_manuais"
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
            
            if tipo_filter != "Todos":
                df_filtered = df_filtered[df_filtered['tipo'] == tipo_filter]
            
            if search_term:
                mask = (
                    df_filtered['codigo'].str.contains(search_term, case=False, na=False) |
                    df_filtered['descricao'].str.contains(search_term, case=False, na=False)
                )
                df_filtered = df_filtered[mask]
            
            st.divider()
            
            # Tabela de equipamentos
            if not df_filtered.empty:
                st.markdown(f"### 📋 Equipamentos Manuais ({len(df_filtered)} encontrados)")
                show_equipamentos_table(df_filtered)
            else:
                st.warning("⚠️ Nenhum equipamento encontrado com os filtros aplicados")
        
        else:
            st.warning("⚠️ Nenhum equipamento manual encontrado no sistema")
            st.info("""
            💡 **Equipamentos manuais não encontrados**
            
            Para ver equipamentos manuais nesta página:
            - Use a aba "➕ Cadastrar" para adicionar novos equipamentos
            - Certifique-se de que você tem permissão para visualizar estes dados
            """)
    
    with tab_create:
        # Formulário de criação
        show_create_form()
    
    with tab_manage:
        # Verificar se há equipamento sendo editado
        if 'edit_equipamento' in st.session_state:
            equipamento = get_equipamento_by_codigo(st.session_state['edit_equipamento'])
            if equipamento:
                show_edit_form(equipamento)
            else:
                st.error("Equipamento não encontrado!")
                st.session_state.pop('edit_equipamento', None)
        else:
            st.info("✏️ **Selecione um equipamento na aba 'Listagem' para editar**")
            
            # Mostrar estatísticas de gestão
            df = get_equipamentos_manuais_data()
            if not df.empty:
                st.markdown("### 📊 Estatísticas de Gestão")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total = len(df)
                    st.metric("Total", total)
                
                with col2:
                    necessitam_manutencao = len(df[df['status'] == 'Manutenção'])
                    st.metric("Em Manutenção", necessitam_manutencao)
                
                with col3:
                    danificados = len(df[df['estado'] == 'Danificado'])
                    st.metric("Danificados", danificados)
                
                with col4:
                    sem_valor = len(df[df['valor'].isna() | (df['valor'] == 0)])
                    st.metric("Sem Valor", sem_valor)
                
                # Lista de equipamentos que precisam de atenção
                st.markdown("### ⚠️ Equipamentos que Precisam de Atenção")
                
                problemas = df[
                    (df['status'] == 'Manutenção') | 
                    (df['estado'] == 'Danificado') |
                    (df['valor'].isna()) |
                    (df['valor'] == 0)
                ]
                
                if not problemas.empty:
                    for _, row in problemas.iterrows():
                        alerts = []
                        if row['status'] == 'Manutenção':
                            alerts.append("🔧 Em manutenção")
                        if row['estado'] == 'Danificado':
                            alerts.append("⚠️ Danificado")
                        if pd.isna(row['valor']) or row['valor'] == 0:
                            alerts.append("💰 Sem valor definido")
                        
                        st.warning(f"**{row['codigo']}** - {row['descricao']}: {' | '.join(alerts)}")
                else:
                    st.success("✅ Todos os equipamentos estão em ordem!")

if __name__ == "__main__":
    from pages import equipamentos_manuais
    equipamentos_manuais.show()