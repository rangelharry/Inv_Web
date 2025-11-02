#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Movimentações
Página de controle de movimentações
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

def get_movimentacoes_data(filtro_status="todos"):
    """Carregar dados das movimentações com filtros"""
    db = DatabaseConnection()
    
    try:
        if filtro_status == "pendentes":
            query = """
                SELECT 
                    id, codigo, origem, destino, data, responsavel, status, quantidade, 
                    tabela_origem as tipo_item, observacoes
                FROM movimentacoes
                WHERE status = 'pendente'
                ORDER BY data DESC
            """
        else:
            query = """
                SELECT 
                    id, codigo, origem, destino, data, responsavel, status, quantidade,
                    tabela_origem as tipo_item, observacoes
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

def get_historico_item(codigo):
    """Obter histórico completo de movimentações de um item específico"""
    db = DatabaseConnection()
    
    try:
        query = """
            SELECT 
                data, origem, destino, responsavel, status, quantidade, observacoes
            FROM movimentacoes
            WHERE codigo = ?
            ORDER BY data DESC
        """
        
        result = db.execute_query(query, (codigo,))
        
        if result:
            return pd.DataFrame(result)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        return pd.DataFrame()

def show_aprovacoes_pendentes(df_pendentes):
    """Exibir movimentações pendentes para aprovação"""
    if df_pendentes.empty:
        st.info("✅ Nenhuma movimentação pendente")
        return
    
    for idx, row in df_pendentes.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**🔄 {row['codigo']}**")
                st.caption(f"📦 Qtd: {row['quantidade']} | Tipo: {row.get('tipo_item', 'N/A')}")
                if row.get('observacoes'):
                    st.caption(f"💬 {row['observacoes']}")
            
            with col2:
                st.markdown(f"📍 **{row['origem']}** → **{row['destino']}**")
                st.caption(f"👤 {row['responsavel']}")
            
            with col3:
                st.markdown(f"⏳ **PENDENTE**")
                st.caption(f"📅 {row['data']}")
            
            with col4:
                col_aprovar, col_rejeitar = st.columns(2)
                
                with col_aprovar:
                    if st.button("✅ Aprovar", key=f"aprovar_{row['id']}", type="primary"):
                        if aprovar_movimentacao(row['id']):
                            st.success("✅ Movimentação aprovada!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao aprovar!")
                
                with col_rejeitar:
                    if st.button("❌ Rejeitar", key=f"rejeitar_{row['id']}"):
                        # Mostrar campo para motivo
                        st.session_state[f'rejeicao_{row["id"]}'] = True
                        st.rerun()
            
            # Campo para motivo de rejeição
            if st.session_state.get(f'rejeicao_{row["id"]}', False):
                with st.form(f"form_rejeicao_{row['id']}"):
                    motivo = st.text_input("Motivo da rejeição:", placeholder="Ex: Item indisponível, documentação insuficiente...")
                    
                    col_confirmar, col_cancelar = st.columns(2)
                    
                    with col_confirmar:
                        if st.form_submit_button("❌ Confirmar Rejeição"):
                            if rejeitar_movimentacao(row['id'], motivo):
                                st.success("✅ Movimentação rejeitada!")
                                del st.session_state[f'rejeicao_{row["id"]}']
                                st.rerun()
                            else:
                                st.error("❌ Erro ao rejeitar!")
                    
                    with col_cancelar:
                        if st.form_submit_button("🔙 Cancelar"):
                            del st.session_state[f'rejeicao_{row["id"]}']
                            st.rerun()
            
            st.markdown("---")

def registrar_movimentacao(codigo, origem, destino, quantidade, responsavel, observacoes="", auto_approved=True):
    """Registrar nova movimentação com validações e triggers automáticos"""
    db = DatabaseConnection()
    
    try:
        from datetime import datetime
        
        # Validar se o item existe em alguma tabela
        item_encontrado = False
        tipo_item = ""
        
        # Verificar em equipamentos elétricos
        eq_eletrico = db.execute_query("SELECT codigo, localizacao FROM equipamentos_eletricos WHERE codigo = ?", (codigo,))
        if eq_eletrico:
            item_encontrado = True
            tipo_item = "equipamento_eletrico"
            localizacao_atual = eq_eletrico[0]['localizacao']
        
        # Verificar em equipamentos manuais
        if not item_encontrado:
            eq_manual = db.execute_query("SELECT codigo, localizacao FROM equipamentos_manuais WHERE codigo = ?", (codigo,))
            if eq_manual:
                item_encontrado = True
                tipo_item = "equipamento_manual"
                localizacao_atual = eq_manual[0]['localizacao']
        
        # Verificar em insumos
        if not item_encontrado:
            insumo = db.execute_query("SELECT codigo, localizacao FROM insumos WHERE codigo = ?", (codigo,))
            if insumo:
                item_encontrado = True
                tipo_item = "insumo"
                localizacao_atual = insumo[0]['localizacao']
        
        if not item_encontrado:
            st.error(f"❌ Item com código '{codigo}' não encontrado no sistema!")
            return False
        
        # Validar se a origem confere com a localização atual
        if origem != localizacao_atual:
            st.warning(f"⚠️ Origem informada ({origem}) diferente da localização atual ({localizacao_atual}). Usando localização atual.")
            origem = localizacao_atual
        
        # Determinar status baseado no tipo de movimentação
        status = 'concluida' if auto_approved else 'pendente'
        
        # Movimentações críticas precisam de aprovação (equipamentos caros, transferências externas)
        if any(palavra in destino.lower() for palavra in ['cliente', 'fornecedor', 'terceirizado']) and tipo_item.startswith('equipamento'):
            status = 'pendente'
            auto_approved = False
        
        # Registrar movimentação
        movimentacao_query = """
            INSERT INTO movimentacoes (
                codigo, origem, destino, data, responsavel, status, quantidade, tabela_origem, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            codigo,
            origem, 
            destino,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            responsavel,
            status,
            quantidade,
            tipo_item,
            observacoes
        )
        
        movimentacao_success = db.execute_update(movimentacao_query, params)
        
        if not movimentacao_success:
            return False
        
        # Se aprovada automaticamente, atualizar localização do item
        if auto_approved and status == 'concluida':
            if tipo_item == "equipamento_eletrico":
                update_success = db.execute_update(
                    "UPDATE equipamentos_eletricos SET localizacao = ? WHERE codigo = ?",
                    (destino, codigo)
                )
            elif tipo_item == "equipamento_manual":
                update_success = db.execute_update(
                    "UPDATE equipamentos_manuais SET localizacao = ? WHERE codigo = ?",
                    (destino, codigo)
                )
            elif tipo_item == "insumo":
                update_success = db.execute_update(
                    "UPDATE insumos SET localizacao = ? WHERE codigo = ?",
                    (destino, codigo)
                )
            
            if not update_success:
                st.error("❌ Erro ao atualizar localização do item!")
                return False
        
        # Registrar no log de auditoria
        from utils.auth import get_auth
        auth = get_auth()
        user = auth.get_current_user()
        user_id = user['id'] if user else None
        
        log_query = """
            INSERT INTO logs_sistema (
                timestamp, user_id, action, details, ip_address
            ) VALUES (?, ?, ?, ?, ?)
        """
        
        log_details = f"Movimentacao {status}: {codigo} de {origem} para {destino} (Qtd: {quantidade})"
        if not auto_approved:
            log_details += " - REQUER APROVACAO"
        
        db.execute_update(log_query, (
            datetime.now().isoformat(),
            user_id,
            'movimentacao_registro',
            log_details,
            'streamlit_session'  # Em produção, capturar IP real
        ))
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao registrar movimentação: {e}")
        return False

def aprovar_movimentacao(movimentacao_id):
    """Aprovar movimentação e atualizar localização do item"""
    db = DatabaseConnection()
    
    try:
        from datetime import datetime
        
        # Buscar dados da movimentação
        mov_data = db.execute_query("""
            SELECT codigo, destino, tabela_origem as tipo_item, responsavel, quantidade 
            FROM movimentacoes 
            WHERE id = ? AND status = 'pendente'
        """, (movimentacao_id,))
        
        if not mov_data:
            st.error("Movimentação não encontrada ou já processada!")
            return False
        
        mov = mov_data[0]
        
        # Atualizar status da movimentação
        update_mov = db.execute_update(
            "UPDATE movimentacoes SET status = 'aprovada', data_aprovacao = ? WHERE id = ?",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), movimentacao_id)
        )
        
        if not update_mov:
            return False
        
        # Atualizar localização do item na tabela correspondente
        if mov['tipo_item'] == "equipamento_eletrico":
            update_success = db.execute_update(
                "UPDATE equipamentos_eletricos SET localizacao = ? WHERE codigo = ?",
                (mov['destino'], mov['codigo'])
            )
        elif mov['tipo_item'] == "equipamento_manual":
            update_success = db.execute_update(
                "UPDATE equipamentos_manuais SET localizacao = ? WHERE codigo = ?",
                (mov['destino'], mov['codigo'])
            )
        elif mov['tipo_item'] == "insumo":
            update_success = db.execute_update(
                "UPDATE insumos SET localizacao = ? WHERE codigo = ?",
                (mov['destino'], mov['codigo'])
            )
        
        # Log da aprovação
        from utils.auth import get_auth
        auth = get_auth()
        user = auth.get_current_user()
        user_id = user['id'] if user else None
        
        log_query = """
            INSERT INTO logs_sistema (
                timestamp, user_id, action, details, ip_address
            ) VALUES (?, ?, ?, ?, ?)
        """
        
        db.execute_update(log_query, (
            datetime.now().isoformat(),
            user_id,
            'movimentacao_aprovacao',
            f"Aprovada movimentacao ID {movimentacao_id}: {mov['codigo']} para {mov['destino']}",
            'streamlit_session'
        ))
        
        return True
        
    except Exception as e:
        st.error(f"Erro ao aprovar movimentação: {e}")
        return False

def rejeitar_movimentacao(movimentacao_id, motivo=""):
    """Rejeitar movimentação com motivo"""
    db = DatabaseConnection()
    
    try:
        from datetime import datetime
        
        # Buscar dados da movimentação
        mov_data = db.execute_query("""
            SELECT codigo, origem, destino, responsavel 
            FROM movimentacoes 
            WHERE id = ? AND status = 'pendente'
        """, (movimentacao_id,))
        
        if not mov_data:
            st.error("Movimentação não encontrada ou já processada!")
            return False
        
        mov = mov_data[0]
        
        # Atualizar status da movimentação
        update_mov = db.execute_update(
            "UPDATE movimentacoes SET status = 'rejeitada', data_rejeicao = ?, motivo_rejeicao = ? WHERE id = ?",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), motivo, movimentacao_id)
        )
        
        # Log da rejeição
        from utils.auth import get_auth
        auth = get_auth()
        user = auth.get_current_user()
        user_id = user['id'] if user else None
        
        log_query = """
            INSERT INTO logs_sistema (
                timestamp, user_id, action, details, ip_address
            ) VALUES (?, ?, ?, ?, ?)
        """
        
        db.execute_update(log_query, (
            datetime.now().isoformat(),
            user_id,
            'movimentacao_rejeicao',
            f"Rejeitada movimentacao ID {movimentacao_id}: {mov['codigo']} - Motivo: {motivo}",
            'streamlit_session'
        ))
        
        return update_mov
        
    except Exception as e:
        st.error(f"Erro ao rejeitar movimentação: {e}")
        return False

def show():
    """Função principal da página Movimentações"""
    
    # FORÃ‡AR TEMA CLARO - MODO EXTREMO
    apply_global_css()
    force_light_theme()
    
    # Verificar autenticação
    auth = get_auth()
    if not auth.is_authenticated():
        auth.show_login_page()
        return
    
    st.markdown(f"## 📊 Movimentações")
    st.markdown("Controle de transferências e movimentação de itens")
    
    # Verificar movimentações pendentes de aprovação
    auth = get_auth()
    if auth.has_permission('admin'):
        df_pendentes = get_movimentacoes_data("pendentes")
        
        if not df_pendentes.empty:
            st.error(f"⚠️ **{len(df_pendentes)} MOVIMENTAÇÕES PENDENTES DE APROVAÇÃO!**")
            
            with st.expander("📋 Ver Movimentações Pendentes", expanded=True):
                show_aprovacoes_pendentes(df_pendentes)
            
            st.markdown("---")
    
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
    
    # Buscar responsáveis ativos do banco
    db = DatabaseConnection()
    responsaveis_db = db.execute_query("SELECT id, nome, cargo, setor FROM responsaveis WHERE ativo = 1 ORDER BY nome")
    
    if not responsaveis_db:
        st.warning("⚠️ Nenhum responsável cadastrado. Por favor, cadastre responsáveis antes de registrar movimentações.")
        st.info("💡 Vá para Configurações → Responsáveis para cadastrar novos responsáveis.")
    
    with st.form("nova_movimentacao"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo_item = st.text_input("Código do Item *", help="Código do equipamento ou insumo")
            
            # Locais simplificados sem referência às obras
            locais_simplificados = [
                "Almoxarifado Central", "Escritório Matriz", "Manutenção", "Engenharia", 
                "Recursos Humanos", "Galpão Principal", "Depósito Filial", "Área Externa",
                "Obra Principal", "Cliente Externo", "Fornecedor", "Em Trânsito"
            ]
            
            origem = st.selectbox("Origem *", locais_simplificados, help="Local de origem do item")
            quantidade = st.number_input("Quantidade *", min_value=1, value=1)
        
        with col2:
            destino = st.selectbox("Destino *", locais_simplificados, help="Local de destino do item")
            
            # Selectbox de responsáveis ao invés de text_input
            if responsaveis_db:
                # Criar opções formatadas para o selectbox
                responsaveis_opcoes = [
                    f"{r['nome']} - {r['cargo']} ({r['setor']})" if r.get('cargo') and r.get('setor') 
                    else r['nome'] 
                    for r in responsaveis_db
                ]
                
                # Mapear opções para nomes reais
                responsavel_selecionado_idx = st.selectbox(
                    "Responsável *", 
                    range(len(responsaveis_opcoes)),
                    format_func=lambda x: responsaveis_opcoes[x],
                    help="Selecione o responsável pela movimentação"
                )
                
                responsavel_nome = responsaveis_db[responsavel_selecionado_idx]['nome']
            else:
                st.error("❌ Nenhum responsável disponível!")
                responsavel_nome = None
        
        observacoes = st.text_area("Observações", help="Informações adicionais sobre a movimentação")
        
        submitted = st.form_submit_button("📦 Registrar Movimentação", type="primary")
        
        if submitted:
            if codigo_item and origem and destino and responsavel_nome:
                # Registrar movimentação
                success = registrar_movimentacao(codigo_item, origem, destino, quantidade, responsavel_nome, observacoes)
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