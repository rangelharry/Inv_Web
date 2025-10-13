#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Conexão com Banco de Dados
Gerencia conexões SQLite com cache e otimizações para Streamlit
"""

import sqlite3
import streamlit as st
import os
import threading
from typing import Optional, List, Dict, Any

# Lock para thread safety
db_lock = threading.Lock()

class DatabaseConnection:
    """Gerenciador de conexão com banco de dados SQLite"""
    
    def __init__(self, db_path: str = "database/inventario.db"):
        """
        Inicializar conexão com banco
        
        Args:
            db_path: Caminho para arquivo do banco SQLite
        """
        self.db_path = db_path
        self._connection = None
        
    def get_connection(self) -> sqlite3.Connection:
        """
        Obter conexão com banco (thread-safe)
        
        Returns:
            Conexão SQLite ativa
        """
        with db_lock:
            if self._connection is None:
                if not os.path.exists(self.db_path):
                    raise FileNotFoundError(f"Banco de dados não encontrado: {self.db_path}")
                
                self._connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                
                # Configurações de performance
                self._connection.execute("PRAGMA journal_mode=WAL")
                self._connection.execute("PRAGMA synchronous=NORMAL")
                self._connection.execute("PRAGMA cache_size=10000")
                self._connection.execute("PRAGMA temp_store=MEMORY")
                
            return self._connection
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Executar consulta SELECT
        
        Args:
            query: Query SQL
            params: Parâmetros para query
            
        Returns:
            Lista de dicionários com resultados
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            st.error(f"Erro na consulta: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """
        Executar query de modificação (INSERT, UPDATE, DELETE)
        
        Args:
            query: Query SQL
            params: Parâmetros para query
            
        Returns:
            True se sucesso, False se erro
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return True
            
        except Exception as e:
            st.error(f"Erro na operação: {e}")
            conn.rollback()
            return False
    
    def close(self):
        """Fechar conexão com banco"""
        with db_lock:
            if self._connection:
                self._connection.close()
                self._connection = None

# Instância global para cache do Streamlit
@st.cache_resource
def get_database() -> DatabaseConnection:
    """
    Obter instância do banco (cached)
    
    Returns:
        Instância de DatabaseConnection
    """
    return DatabaseConnection()

def init_database():
    """Inicializar e verificar banco de dados"""
    try:
        db = get_database()
        
        # Testar conexão
        result = db.execute_query("SELECT COUNT(*) as count FROM usuarios")
        
        if result:
            st.success("✅ Conexão com banco de dados estabelecida")
            return True
        else:
            st.error("❌ Erro ao conectar com banco de dados")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro na inicialização do banco: {e}")
        return False

def test_database():
    """Testar todas as tabelas do banco"""
    db = get_database()
    
    tables_to_test = [
        'usuarios', 'equipamentos', 'equipamentos_manuais', 
        'insumos', 'obras', 'movimentacoes', 'responsaveis'
    ]
    
    results = {}
    
    for table in tables_to_test:
        try:
            result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            results[table] = count
        except Exception as e:
            results[table] = f"Erro: {e}"
    
    return results