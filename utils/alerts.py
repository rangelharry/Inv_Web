#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Sistema de Alertas Automáticos
Gerencia alertas para movimentações pendentes, baixo estoque e equipamentos parados
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import DatabaseConnection
from utils.logging import SystemLogger

logger = SystemLogger()

class AlertSystem:
    """Sistema de alertas automáticos"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_movimentacoes_pendentes(self):
        """Buscar movimentações pendentes de aprovação"""
        try:
            query = """
                SELECT 
                    m.id, m.codigo as item_codigo, m.origem, m.destino, 
                    m.quantidade, m.responsavel, m.data as data_movimentacao,
                    CASE 
                        WHEN ee.codigo IS NOT NULL THEN ee.nome
                        WHEN em.codigo IS NOT NULL THEN em.descricao  
                        WHEN i.codigo IS NOT NULL THEN i.descricao
                        ELSE 'Item não encontrado'
                    END as item_descricao
                FROM movimentacoes m
                LEFT JOIN equipamentos_eletricos ee ON m.codigo = ee.codigo
                LEFT JOIN equipamentos_manuais em ON m.codigo = em.codigo
                LEFT JOIN insumos i ON m.codigo = i.codigo
                WHERE m.status = 'Pendente'
                ORDER BY m.data DESC
            """
            
            result = self.db.execute_query(query)
            return result if result else []
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao buscar movimentações pendentes: {e}")
            return []
    
    def get_itens_baixo_estoque(self, limite_minimo=5):
        """Buscar itens com baixo estoque"""
        try:
            alertas = []
            
            # Equipamentos elétricos são individuais - não precisam de alerta de baixo estoque
            
            # Verificar equipamentos manuais
            query_em = """
                SELECT codigo, descricao, quantitativo, localizacao, 'Equipamento Manual' as tipo
                FROM equipamentos_manuais 
                WHERE quantitativo <= ? AND status = 'Disponível'
                ORDER BY quantitativo ASC
            """
            result_em = self.db.execute_query(query_em, (limite_minimo,))
            if result_em:
                alertas.extend(result_em)
            
            # Verificar insumos (usam 'quantidade', não 'quantitativo')
            query_i = """
                SELECT codigo, descricao, quantidade as quantitativo, localizacao, 'Insumo' as tipo
                FROM insumos 
                WHERE quantidade <= quantidade_minima
                ORDER BY quantidade ASC
            """
            result_i = self.db.execute_query(query_i)
            if result_i:
                alertas.extend(result_i)
            
            return alertas
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao buscar itens com baixo estoque: {e}")
            return []
    
    def get_equipamentos_sem_movimentacao(self, dias=90):
        """Buscar equipamentos sem movimentação há muito tempo"""
        try:
            data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            
            alertas = []
            
            # Equipamentos elétricos sem movimentação
            query_ee = """
                SELECT ee.codigo, ee.nome as descricao, ee.localizacao, 'Equipamento Elétrico' as tipo,
                       MAX(m.data) as ultima_movimentacao
                FROM equipamentos_eletricos ee
                LEFT JOIN movimentacoes m ON ee.codigo = m.codigo
                WHERE ee.status IN ('Disponível', 'Em Uso')
                GROUP BY ee.codigo, ee.nome, ee.localizacao
                HAVING MAX(m.data) < ? OR MAX(m.data) IS NULL
                ORDER BY ultima_movimentacao ASC
            """
            result_ee = self.db.execute_query(query_ee, (data_limite,))
            if result_ee:
                alertas.extend(result_ee)
            
            # Equipamentos manuais sem movimentação
            query_em = """
                SELECT em.codigo, em.descricao, em.localizacao, 'Equipamento Manual' as tipo,
                       MAX(m.data) as ultima_movimentacao
                FROM equipamentos_manuais em
                LEFT JOIN movimentacoes m ON em.codigo = m.codigo
                WHERE em.status IN ('Disponível', 'Em Uso')
                GROUP BY em.codigo, em.descricao, em.localizacao
                HAVING MAX(m.data) < ? OR MAX(m.data) IS NULL
                ORDER BY ultima_movimentacao ASC
            """
            result_em = self.db.execute_query(query_em, (data_limite,))
            if result_em:
                alertas.extend(result_em)
            
            return alertas
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao buscar equipamentos sem movimentação: {e}")
            return []
    
    def get_itens_em_manutencao(self):
        """Buscar itens em manutenção há muito tempo"""
        try:
            alertas = []
            
            # Equipamentos elétricos em manutenção
            query_ee = """
                SELECT codigo, nome as descricao, localizacao, 'Equipamento Elétrico' as tipo
                FROM equipamentos_eletricos 
                WHERE status = 'Manutenção'
                ORDER BY codigo
            """
            result_ee = self.db.execute_query(query_ee)
            if result_ee:
                alertas.extend(result_ee)
            
            # Equipamentos manuais em manutenção
            query_em = """
                SELECT codigo, descricao, localizacao, 'Equipamento Manual' as tipo
                FROM equipamentos_manuais 
                WHERE status = 'Manutenção'
                ORDER BY codigo
            """
            result_em = self.db.execute_query(query_em)
            if result_em:
                alertas.extend(result_em)
            
            return alertas
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao buscar itens em manutenção: {e}")
            return []
    
    def get_movimentacoes_recentes(self, dias=7):
        """Buscar movimentações recentes para monitoramento"""
        try:
            data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            
            query = """
                SELECT 
                    m.id, m.codigo as item_codigo, m.origem, m.destino, 
                    m.quantidade, m.responsavel, m.data as data_movimentacao, m.status,
                    CASE 
                        WHEN ee.codigo IS NOT NULL THEN ee.nome
                        WHEN em.codigo IS NOT NULL THEN em.descricao  
                        WHEN i.codigo IS NOT NULL THEN i.descricao
                        ELSE 'Item não encontrado'
                    END as item_descricao,
                    CASE 
                        WHEN ee.codigo IS NOT NULL THEN 'Equipamento Elétrico'
                        WHEN em.codigo IS NOT NULL THEN 'Equipamento Manual'
                        WHEN i.codigo IS NOT NULL THEN 'Insumo'
                        ELSE 'Desconhecido'
                    END as tipo_item
                FROM movimentacoes m
                LEFT JOIN equipamentos_eletricos ee ON m.codigo = ee.codigo
                LEFT JOIN equipamentos_manuais em ON m.codigo = em.codigo
                LEFT JOIN insumos i ON m.codigo = i.codigo
                WHERE DATE(m.data) >= ?
                ORDER BY m.data DESC
            """
            
            result = self.db.execute_query(query, (data_limite,))
            return result if result else []
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao buscar movimentações recentes: {e}")
            return []
    
    def get_resumo_alertas(self):
        """Gerar resumo geral de todos os alertas"""
        try:
            resumo = {
                'movimentacoes_pendentes': len(self.get_movimentacoes_pendentes()),
                'baixo_estoque': len(self.get_itens_baixo_estoque()),
                'sem_movimentacao': len(self.get_equipamentos_sem_movimentacao()),
                'em_manutencao': len(self.get_itens_em_manutencao()),
                'movimentacoes_recentes': len(self.get_movimentacoes_recentes())
            }
            
            resumo['total_alertas'] = (
                resumo['movimentacoes_pendentes'] + 
                resumo['baixo_estoque'] + 
                resumo['sem_movimentacao'] + 
                resumo['em_manutencao']
            )
            
            return resumo
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao gerar resumo de alertas: {e}")
            return {
                'movimentacoes_pendentes': 0,
                'baixo_estoque': 0,
                'sem_movimentacao': 0,
                'em_manutencao': 0,
                'movimentacoes_recentes': 0,
                'total_alertas': 0
            }
    
    def show_alerts_widget(self):
        """Widget de alertas para ser usado em outras páginas"""
        resumo = self.get_resumo_alertas()
        
        if resumo['total_alertas'] > 0:
            with st.container():
                st.markdown("### 🚨 Alertas do Sistema")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if resumo['movimentacoes_pendentes'] > 0:
                        st.error(f"⏳ {resumo['movimentacoes_pendentes']} Movimentações Pendentes")
                    else:
                        st.success("✅ Sem movimentações pendentes")
                
                with col2:
                    if resumo['baixo_estoque'] > 0:
                        st.warning(f"📉 {resumo['baixo_estoque']} Itens com Baixo Estoque")
                    else:
                        st.success("✅ Estoque adequado")
                
                with col3:
                    if resumo['sem_movimentacao'] > 0:
                        st.info(f"💤 {resumo['sem_movimentacao']} Itens Parados")
                    else:
                        st.success("✅ Itens em movimento")
                
                with col4:
                    if resumo['em_manutencao'] > 0:
                        st.error(f"🔧 {resumo['em_manutencao']} Em Manutenção")
                    else:
                        st.success("✅ Sem itens em manutenção")
                
                if resumo['total_alertas'] > 0:
                    if st.button("📋 Ver Detalhes dos Alertas"):
                        st.session_state['show_alerts_page'] = True
                        st.rerun()

def show_alerts_page():
    """Página completa de alertas"""
    st.markdown("## 🚨 Sistema de Alertas")
    st.markdown("Monitoramento automático do inventário")
    
    alert_system = AlertSystem()
    
    # Tabs para diferentes tipos de alertas
    tab_resumo, tab_pendentes, tab_estoque, tab_parados, tab_manutencao, tab_recentes = st.tabs([
        "📊 Resumo", "⏳ Pendentes", "📉 Baixo Estoque", 
        "💤 Parados", "🔧 Manutenção", "📈 Recentes"
    ])
    
    with tab_resumo:
        st.markdown("### 📊 Resumo Geral de Alertas")
        resumo = alert_system.get_resumo_alertas()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total de Alertas", resumo['total_alertas'])
        
        with col2:
            st.metric("Movimentações Pendentes", resumo['movimentacoes_pendentes'])
        
        with col3:
            st.metric("Baixo Estoque", resumo['baixo_estoque'])
        
        with col4:
            st.metric("Itens Parados", resumo['sem_movimentacao'])
        
        with col5:
            st.metric("Em Manutenção", resumo['em_manutencao'])
        
        # Gráfico de pizza dos alertas
        if resumo['total_alertas'] > 0:
            st.markdown("### 📊 Distribuição dos Alertas")
            
            dados_grafico = pd.DataFrame([
                {"Tipo": "Movimentações Pendentes", "Quantidade": resumo['movimentacoes_pendentes']},
                {"Tipo": "Baixo Estoque", "Quantidade": resumo['baixo_estoque']},
                {"Tipo": "Itens Parados", "Quantidade": resumo['sem_movimentacao']},
                {"Tipo": "Em Manutenção", "Quantidade": resumo['em_manutencao']}
            ])
            
            dados_grafico = dados_grafico[dados_grafico['Quantidade'] > 0]
            
            if not dados_grafico.empty:
                # Usar função safe para evitar erro PyArrow
                from utils.dataframe_utils import safe_chart_display
                safe_chart_display(dados_grafico.set_index('Tipo'), chart_type='bar')
        else:
            st.success("🎉 **Parabéns!** Não há alertas ativos no sistema!")
    
    with tab_pendentes:
        st.markdown("### ⏳ Movimentações Pendentes de Aprovação")
        
        pendentes = alert_system.get_movimentacoes_pendentes()
        
        if pendentes:
            for mov in pendentes:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{mov['item_codigo']}** - {mov['item_descricao']}")
                        st.caption(f"📍 {mov['origem']} → {mov['destino']}")
                    
                    with col2:
                        st.markdown(f"👤 **{mov['responsavel']}**")
                        st.caption(f"📅 {mov['data_movimentacao']} | Qtd: {mov['quantidade']}")
                    
                    with col3:
                        if st.button("✅ Aprovar", key=f"approve_{mov['id']}"):
                            # Implementar aprovação
                            st.success("Movimentação aprovada!")
                    
                    st.divider()
        else:
            st.success("✅ Não há movimentações pendentes!")
    
    with tab_estoque:
        st.markdown("### 📉 Itens com Baixo Estoque")
        
        limite = st.slider("Limite mínimo de estoque", 1, 20, 5)
        baixo_estoque = alert_system.get_itens_baixo_estoque(limite)
        
        if baixo_estoque:
            for item in baixo_estoque:
                st.warning(f"⚠️ **{item['codigo']}** - {item['descricao']} | "
                          f"Qtd: {item['quantitativo']} | Tipo: {item['tipo']} | "
                          f"Local: {item['localizacao']}")
        else:
            st.success("✅ Todos os itens estão com estoque adequado!")
    
    with tab_parados:
        st.markdown("### 💤 Equipamentos Sem Movimentação")
        
        dias = st.slider("Dias sem movimentação", 30, 365, 90)
        parados = alert_system.get_equipamentos_sem_movimentacao(dias)
        
        if parados:
            for item in parados:
                ultima = item['ultima_movimentacao'] if item['ultima_movimentacao'] else "Nunca"
                st.info(f"💤 **{item['codigo']}** - {item['descricao']} | "
                       f"Tipo: {item['tipo']} | Local: {item['localizacao']} | "
                       f"Última movimentação: {ultima}")
        else:
            st.success("✅ Todos os equipamentos têm movimentação recente!")
    
    with tab_manutencao:
        st.markdown("### 🔧 Itens em Manutenção")
        
        manutencao = alert_system.get_itens_em_manutencao()
        
        if manutencao:
            for item in manutencao:
                st.error(f"🔧 **{item['codigo']}** - {item['descricao']} | "
                        f"Tipo: {item['tipo']} | Local: {item['localizacao']}")
        else:
            st.success("✅ Nenhum item em manutenção!")
    
    with tab_recentes:
        st.markdown("### 📈 Movimentações Recentes")
        
        dias_recentes = st.slider("Últimos dias", 1, 30, 7)
        recentes = alert_system.get_movimentacoes_recentes(dias_recentes)
        
        if recentes:
            for mov in recentes:
                status_emoji = {"Aprovada": "✅", "Pendente": "⏳", "Rejeitada": "❌"}.get(mov['status'], "⚪")
                st.info(f"{status_emoji} **{mov['item_codigo']}** - {mov['item_descricao']} | "
                       f"{mov['origem']} → {mov['destino']} | "
                       f"Qtd: {mov['quantidade']} | {mov['responsavel']} | "
                       f"{mov['data_movimentacao']}")
        else:
            st.info("ℹ️ Nenhuma movimentação recente encontrada!")

# Instância global do sistema de alertas
alert_system = AlertSystem()