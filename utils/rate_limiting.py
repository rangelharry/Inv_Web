#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Rate Limiting
Sistema de limitação de tentativas por IP para prevenir ataques
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import json

# Inicialização global do session_state para rate limiting
if 'rate_limit_data' not in st.session_state:
    st.session_state.rate_limit_data = {}

class RateLimiter:
    """Sistema de rate limiting para prevenir ataques de força bruta"""
    
    def __init__(self):
        """Inicializar rate limiter"""
        # Configurações
        self.MAX_ATTEMPTS = 5  # Máximo de tentativas
        self.WINDOW_MINUTES = 1  # Janela de tempo em minutos
        self.BLOCK_MINUTES = 30  # Tempo de bloqueio em minutos
    
    def _get_client_key(self) -> str:
        """
        Obter chave única para o cliente
        Em produção, seria o IP real. Para Streamlit, usamos session ID simulado.
        """
        # Simular ID de sessão único
        if 'client_key' not in st.session_state:
            # Gerar chave baseada em timestamp e dados da sessão
            timestamp = str(datetime.now().timestamp())
            session_data = str(st.session_state)
            combined = f"{timestamp}_{session_data}"
            st.session_state.client_key = hashlib.md5(combined.encode()).hexdigest()[:12]
        
        return st.session_state.client_key
    
    def _cleanup_old_entries(self, client_key: str):
        """Limpar entradas antigas fora da janela de tempo"""
        if client_key not in st.session_state.rate_limit_data:
            return
        
        now = datetime.now()
        window_start = now - timedelta(minutes=self.WINDOW_MINUTES)
        
        # Filtrar tentativas dentro da janela
        attempts = st.session_state.rate_limit_data[client_key].get('attempts', [])
        valid_attempts = [
            attempt for attempt in attempts 
            if datetime.fromisoformat(attempt) > window_start
        ]
        
        st.session_state.rate_limit_data[client_key]['attempts'] = valid_attempts
    
    def check_rate_limit(self, client_key: Optional[str] = None) -> tuple[bool, str]:
        """
        Verificar se cliente está dentro do limite de tentativas
        
        Args:
            client_key: Chave do cliente (opcional, usa IP/sessão por padrão)
            
        Returns:
            Tuple (is_allowed, message)
        """
        if not client_key:
            client_key = self._get_client_key()
        
        # Inicializar dados do cliente se não existir
        if client_key not in st.session_state.rate_limit_data:
            st.session_state.rate_limit_data[client_key] = {
                'attempts': [],
                'blocked_until': None
            }
        
        client_data = st.session_state.rate_limit_data[client_key]
        now = datetime.now()
        
        # Verificar se está bloqueado
        if client_data.get('blocked_until'):
            blocked_until = datetime.fromisoformat(client_data['blocked_until'])
            if now < blocked_until:
                remaining_minutes = int((blocked_until - now).total_seconds() / 60)
                return False, f"IP bloqueado. Tente novamente em {remaining_minutes} minutos."
            else:
                # Desbloqueou - limpar bloqueio
                client_data['blocked_until'] = None
                client_data['attempts'] = []
        
        # Limpar tentativas antigas
        self._cleanup_old_entries(client_key)
        
        # Verificar número de tentativas na janela atual
        attempts_count = len(client_data['attempts'])
        
        if attempts_count >= self.MAX_ATTEMPTS:
            # Bloquear cliente
            blocked_until = now + timedelta(minutes=self.BLOCK_MINUTES)
            client_data['blocked_until'] = blocked_until.isoformat()
            
            # Log do bloqueio
            from utils.logging import log_security
            log_security(
                'rate_limit_exceeded',
                f"Cliente {client_key} bloqueado por excesso de tentativas: {attempts_count} em {self.WINDOW_MINUTES}min",
                'high'
            )
            
            return False, f"Muitas tentativas. IP bloqueado por {self.BLOCK_MINUTES} minutos."
        
        remaining_attempts = self.MAX_ATTEMPTS - attempts_count
        return True, f"Tentativas restantes: {remaining_attempts}"
    
    def record_attempt(self, client_key: Optional[str] = None, success: bool = False):
        """
        Registrar tentativa de acesso
        
        Args:
            client_key: Chave do cliente
            success: Se a tentativa foi bem-sucedida
        """
        if not client_key:
            client_key = self._get_client_key()
        
        now = datetime.now()
        
        # Inicializar dados do cliente se não existir
        if client_key not in st.session_state.rate_limit_data:
            st.session_state.rate_limit_data[client_key] = {
                'attempts': [],
                'blocked_until': None
            }
        
        # Se tentativa foi bem-sucedida, limpar histórico
        if success:
            st.session_state.rate_limit_data[client_key]['attempts'] = []
            st.session_state.rate_limit_data[client_key]['blocked_until'] = None
        else:
            # Registrar tentativa falhada
            st.session_state.rate_limit_data[client_key]['attempts'].append(now.isoformat())
        
        # Limpar tentativas antigas
        self._cleanup_old_entries(client_key)
    
    def get_client_status(self, client_key: Optional[str] = None) -> Dict:
        """
        Obter status atual do cliente
        
        Args:
            client_key: Chave do cliente
            
        Returns:
            Dict com informações do status
        """
        if not client_key:
            client_key = self._get_client_key()
        
        if client_key not in st.session_state.rate_limit_data:
            return {
                'client_key': client_key,
                'attempts_count': 0,
                'is_blocked': False,
                'blocked_until': None,
                'remaining_attempts': self.MAX_ATTEMPTS
            }
        
        client_data = st.session_state.rate_limit_data[client_key]
        now = datetime.now()
        
        # Limpar tentativas antigas
        self._cleanup_old_entries(client_key)
        
        attempts_count = len(client_data['attempts'])
        is_blocked = False
        blocked_until = None
        
        if client_data.get('blocked_until'):
            blocked_until_dt = datetime.fromisoformat(client_data['blocked_until'])
            is_blocked = now < blocked_until_dt
            blocked_until = client_data['blocked_until'] if is_blocked else None
        
        return {
            'client_key': client_key,
            'attempts_count': attempts_count,
            'is_blocked': is_blocked,
            'blocked_until': blocked_until,
            'remaining_attempts': max(0, self.MAX_ATTEMPTS - attempts_count)
        }
    
    def reset_client(self, client_key: Optional[str] = None):
        """
        Resetar dados de um cliente (para administradores)
        
        Args:
            client_key: Chave do cliente
        """
        if not client_key:
            client_key = self._get_client_key()
        
        if client_key in st.session_state.rate_limit_data:
            del st.session_state.rate_limit_data[client_key]
        
        # Log da ação
        from utils.logging import log_security
        log_security(
            'rate_limit_reset',
            f"Rate limit resetado para cliente {client_key}",
            'medium'
        )
    
    def get_all_blocked_clients(self) -> List[Dict]:
        """Obter lista de todos os clientes bloqueados"""
        blocked_clients = []
        now = datetime.now()
        
        for client_key, client_data in st.session_state.rate_limit_data.items():
            if client_data.get('blocked_until'):
                blocked_until_dt = datetime.fromisoformat(client_data['blocked_until'])
                if now < blocked_until_dt:  # Ainda bloqueado
                    blocked_clients.append({
                        'client_key': client_key,
                        'blocked_until': client_data['blocked_until'],
                        'attempts_count': len(client_data['attempts'])
                    })
        
        return blocked_clients

# Instância global do rate limiter
rate_limiter = RateLimiter()

def check_rate_limit() -> tuple[bool, str]:
    """Função conveniente para verificar rate limit"""
    return rate_limiter.check_rate_limit()

def record_login_attempt(success: bool = False):
    """Função conveniente para registrar tentativa de login"""
    return rate_limiter.record_attempt(success=success)