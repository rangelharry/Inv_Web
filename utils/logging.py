#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Sistema de Logging
Logging centralizado para auditoria e rastreabilidade
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any
from database.connection import get_database
import json

class SystemLogger:
    """Sistema centralizado de logging para auditoria"""
    
    def __init__(self):
        self.db = get_database()
    
    def log_action(self, action: str, details: str, user_id: Optional[int] = None, 
                   item_code: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None):
        """
        Registrar ação no log de auditoria
        
        Args:
            action: Tipo de ação (login, logout, create, update, delete, etc.)
            details: Detalhes da ação
            user_id: ID do usuário (opcional)
            item_code: Código do item afetado (opcional)
            additional_data: Dados adicionais em formato dict (opcional)
        """
        try:
            # Obter informações do usuário atual se não fornecido
            if user_id is None:
                from utils.auth import get_auth
                auth = get_auth()
                user = auth.get_current_user()
                user_id = user['id'] if user else None
            
            # Preparar dados adicionais como JSON
            additional_json = json.dumps(additional_data) if additional_data else None
            
            # Capturar IP (simulado para Streamlit)
            ip_address = self._get_client_ip()
            
            # Inserir log
            query = """
                INSERT INTO logs_sistema (
                    timestamp, user_id, action, details, item_code, additional_data, ip_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                datetime.now().isoformat(),
                user_id,
                action,
                details,
                item_code,
                additional_json,
                ip_address
            )
            
            return self.db.execute_update(query, params)
            
        except Exception as e:
            # Não deve quebrar a aplicação por erro de logging
            print(f"Erro no logging: {e}")
            return False
    
    def log_login_attempt(self, username: str, success: bool, user_id: Optional[int] = None):
        """Log de tentativa de login"""
        action = "login_success" if success else "login_failed"
        details = f"Login {'bem-sucedido' if success else 'falhado'} para usuário: {username}"
        
        return self.log_action(action, details, user_id)
    
    def log_logout(self, username: str, user_id: int):
        """Log de logout"""
        return self.log_action("logout", f"Logout do usuário: {username}", user_id)
    
    def log_crud_operation(self, operation: str, table: str, item_code: str, 
                          details: str, old_data: Optional[Dict] = None, 
                          new_data: Optional[Dict] = None):
        """
        Log de operações CRUD
        
        Args:
            operation: create, update, delete
            table: Nome da tabela
            item_code: Código do item
            details: Detalhes da operação
            old_data: Dados antigos (para updates/deletes)
            new_data: Dados novos (para creates/updates)
        """
        action = f"{operation}_{table}"
        
        additional_data = {}
        if old_data:
            additional_data['old_data'] = old_data
        if new_data:
            additional_data['new_data'] = new_data
        
        return self.log_action(action, details, item_code=item_code, additional_data=additional_data)
    
    def log_security_event(self, event_type: str, details: str, severity: str = "medium"):
        """Log de eventos de segurança"""
        action = f"security_{event_type}"
        full_details = f"[{severity.upper()}] {details}"
        
        additional_data = {"severity": severity, "event_type": event_type}
        
        return self.log_action(action, full_details, additional_data=additional_data)
    
    def get_logs(self, limit: int = 100, user_id: Optional[int] = None, 
                 action_filter: Optional[str] = None, date_from: Optional[str] = None,
                 date_to: Optional[str] = None):
        """
        Recuperar logs com filtros
        
        Args:
            limit: Número máximo de logs
            user_id: Filtrar por usuário
            action_filter: Filtrar por tipo de ação
            date_from: Data inicial (ISO format)
            date_to: Data final (ISO format)
        """
        try:
            query = """
                SELECT l.*, u.usuario as username
                FROM logs_sistema l
                LEFT JOIN usuarios u ON l.user_id = u.id
                WHERE 1=1
            """
            params = []
            
            if user_id:
                query += " AND l.user_id = ?"
                params.append(user_id)
            
            if action_filter:
                query += " AND l.action LIKE ?"
                params.append(f"%{action_filter}%")
            
            if date_from:
                query += " AND l.timestamp >= ?"
                params.append(date_from)
            
            if date_to:
                query += " AND l.timestamp <= ?"
                params.append(date_to)
            
            query += " ORDER BY l.timestamp DESC LIMIT ?"
            params.append(limit)
            
            return self.db.execute_query(query, tuple(params))
            
        except Exception as e:
            print(f"Erro ao recuperar logs: {e}")
            return []
    
    def get_audit_summary(self, days: int = 30):
        """Obter resumo de auditoria dos últimos N dias"""
        try:
            from datetime import timedelta
            date_limit = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Total de ações por tipo
            actions_query = """
                SELECT action, COUNT(*) as count
                FROM logs_sistema
                WHERE timestamp >= ?
                GROUP BY action
                ORDER BY count DESC
            """
            
            actions = self.db.execute_query(actions_query, (date_limit,))
            
            # Ações por usuário
            users_query = """
                SELECT u.usuario, COUNT(*) as count
                FROM logs_sistema l
                LEFT JOIN usuarios u ON l.user_id = u.id
                WHERE l.timestamp >= ?
                GROUP BY l.user_id, u.usuario
                ORDER BY count DESC
            """
            
            users = self.db.execute_query(users_query, (date_limit,))
            
            # Eventos de segurança
            security_query = """
                SELECT COUNT(*) as count
                FROM logs_sistema
                WHERE timestamp >= ? AND action LIKE 'security_%'
            """
            
            security = self.db.execute_query(security_query, (date_limit,))
            security_count = security[0]['count'] if security else 0
            
            return {
                'actions': actions,
                'users': users,
                'security_events': security_count,
                'period_days': days
            }
            
        except Exception as e:
            print(f"Erro ao gerar resumo de auditoria: {e}")
            return None
    
    def _get_client_ip(self):
        """Obter IP do cliente (simulado para Streamlit)"""
        # Em produção, isso seria capturado do request real
        # Para Streamlit, usamos um placeholder
        return "streamlit_session"

# Instância global do logger
system_logger = SystemLogger()

def log_action(action: str, details: str, **kwargs):
    """Função conveniente para logging"""
    return system_logger.log_action(action, details, **kwargs)

def log_crud(operation: str, table: str, item_code: str, details: str, **kwargs):
    """Função conveniente para logging CRUD"""
    return system_logger.log_crud_operation(operation, table, item_code, details, **kwargs)

def log_security(event_type: str, details: str, severity: str = "medium"):
    """Função conveniente para logging de segurança"""
    return system_logger.log_security_event(event_type, details, severity)