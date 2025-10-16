#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Feedback Visual Avançado
Gerencia notificações, loading states e feedback para o usuário
"""

import streamlit as st
import time
import threading
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum

class NotificationType(Enum):
    """Tipos de notificação"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

class FeedbackManager:
    """Gerenciador de feedback visual da aplicação"""
    
    def __init__(self):
        """Inicializar gerenciador de feedback"""
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Inicializar estado da sessão"""
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        if 'loading_states' not in st.session_state:
            st.session_state.loading_states = {}
        
        if 'user_actions' not in st.session_state:
            st.session_state.user_actions = []
    
    def show_loading(self, message: str = "Carregando...", key: str = "default"):
        """
        Exibir indicador de carregamento
        
        Args:
            message: Mensagem de carregamento
            key: Chave única para o loading
        """
        st.session_state.loading_states[key] = {
            'message': message,
            'start_time': datetime.now()
        }
        
        # Container para loading
        placeholder = st.empty()
        
        with placeholder.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 2rem;
                    background: #f8f9fa;
                    border-radius: 15px;
                    border: 2px dashed #6c757d;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                ">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border: 4px solid #e3e3e3;
                        border-top: 4px solid #007bff;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 1rem auto;
                    "></div>
                    <h4 style="color: #495057; margin: 0;">{message}</h4>
                    <small style="color: #6c757d;">Por favor, aguarde...</small>
                </div>
                
                <style>
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
                """, unsafe_allow_html=True)
        
        return placeholder
    
    def hide_loading(self, key: str = "default"):
        """
        Ocultar indicador de carregamento
        
        Args:
            key: Chave do loading a remover
        """
        if key in st.session_state.loading_states:
            del st.session_state.loading_states[key]
    
    def show_notification(
        self, 
        message: str, 
        type_: NotificationType = NotificationType.INFO,
        duration: int = 5,
        auto_hide: bool = True
    ):
        """
        Exibir notificação
        
        Args:
            message: Mensagem da notificação
            type_: Tipo da notificação
            duration: Duração em segundos
            auto_hide: Se deve ocultar automaticamente
        """
        notification = {
            'id': f"notif_{len(st.session_state.notifications)}_{int(time.time())}",
            'message': message,
            'type': type_.value,
            'timestamp': datetime.now(),
            'duration': duration,
            'auto_hide': auto_hide
        }
        
        st.session_state.notifications.append(notification)
        
        # Auto-remove após duração especificada
        if auto_hide:
            self._auto_remove_notification(notification['id'], duration)
    
    def _auto_remove_notification(self, notification_id: str, delay: int):
        """
        Remove notificação automaticamente após delay
        
        Args:
            notification_id: ID da notificação
            delay: Delay em segundos
        """
        def remove_after_delay():
            time.sleep(delay)
            self.remove_notification(notification_id)
        
        thread = threading.Thread(target=remove_after_delay)
        thread.daemon = True
        thread.start()
    
    def remove_notification(self, notification_id: str):
        """
        Remover notificação específica
        
        Args:
            notification_id: ID da notificação
        """
        st.session_state.notifications = [
            n for n in st.session_state.notifications 
            if n['id'] != notification_id
        ]
    
    def show_notifications(self):
        """Exibir todas as notificações ativas"""
        if not st.session_state.notifications:
            return
        
        # Container para notificações
        notifications_container = st.container()
        
        with notifications_container:
            for notification in st.session_state.notifications.copy():
                self._render_notification(notification)
    
    def _render_notification(self, notification: Dict[str, Any]):
        """
        Renderizar uma notificação individual
        
        Args:
            notification: Dados da notificação
        """
        # Cores por tipo
        colors = {
            'success': {'bg': '#d1edff', 'border': '#28a745', 'icon': '✅'},
            'warning': {'bg': '#fff3cd', 'border': '#ffc107', 'icon': '⚠️'},
            'error': {'bg': '#f8d7da', 'border': '#dc3545', 'icon': '❌'},
            'info': {'bg': '#d4edda', 'border': '#17a2b8', 'icon': 'ℹ️'}
        }
        
        color_config = colors.get(notification['type'], colors['info'])
        
        # Calcular tempo decorrido
        elapsed = datetime.now() - notification['timestamp']
        elapsed_str = f"{int(elapsed.total_seconds())}s atrás"
        
        # Renderizar notificação
        col1, col2 = st.columns([6, 1])
        
        with col1:
            st.markdown(f"""
            <div style="
                background-color: {color_config['bg']};
                border-left: 4px solid {color_config['border']};
                padding: 1rem;
                margin-bottom: 0.5rem;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                animation: slideInRight 0.3s ease-out;
            ">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">
                        {color_config['icon']}
                    </span>
                    <div>
                        <strong>{notification['message']}</strong>
                        <br>
                        <small style="color: #6c757d;">{elapsed_str}</small>
                    </div>
                </div>
            </div>
            
            <style>
                @keyframes slideInRight {{
                    from {{ transform: translateX(100%); opacity: 0; }}
                    to {{ transform: translateX(0); opacity: 1; }}
                }}
            </style>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("✖", key=f"close_{notification['id']}", help="Fechar"):
                self.remove_notification(notification['id'])
    
    def show_progress_bar(
        self, 
        current: int, 
        total: int, 
        message: str = "",
        color: str = "#007bff"
    ):
        """
        Exibir barra de progresso personalizada
        
        Args:
            current: Valor atual
            total: Valor total
            message: Mensagem do progresso
            color: Cor da barra
        """
        percentage = int((current / total) * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            {f'<p style="margin-bottom: 0.5rem; font-weight: 600;">{message}</p>' if message else ''}
            <div style="
                background-color: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                height: 20px;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="
                    background: {color};
                    height: 100%;
                    width: {percentage}%;
                    border-radius: 10px;
                    transition: width 0.3s ease;
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(255,255,255,0.3);
                        animation: shimmer 2s infinite;
                    "></div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 0.5rem;">
                <small><strong>{current}/{total}</strong> ({percentage}%)</small>
            </div>
        </div>
        
        <style>
            @keyframes shimmer {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
        </style>
        """, unsafe_allow_html=True)
    
    def show_success_animation(self, message: str = "Sucesso!", duration: int = 3):
        """
        Exibir animação de sucesso
        
        Args:
            message: Mensagem de sucesso
            duration: Duração da animação
        """
        placeholder = st.empty()
        
        with placeholder.container():
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 2rem;
                background: #d4edda;
                border-radius: 15px;
                border: 2px solid #28a745;
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                animation: successPulse 0.6s ease-out;
            ">
                <div style="
                    font-size: 4rem;
                    color: #28a745;
                    animation: checkmark 0.8s ease-out;
                ">
                    ✅
                </div>
                <h3 style="color: #155724; margin: 1rem 0 0 0;">{message}</h3>
            </div>
            
            <style>
                @keyframes successPulse {{
                    0% {{ transform: scale(0.8); opacity: 0; }}
                    50% {{ transform: scale(1.05); }}
                    100% {{ transform: scale(1); opacity: 1; }}
                }}
                
                @keyframes checkmark {{
                    0% {{ transform: scale(0) rotate(0deg); }}
                    50% {{ transform: scale(1.2) rotate(180deg); }}
                    100% {{ transform: scale(1) rotate(360deg); }}
                }}
            </style>
            """, unsafe_allow_html=True)
        
        # Auto-remove após duração
        time.sleep(duration)
        placeholder.empty()
    
    def show_error_animation(self, message: str = "Erro!", duration: int = 3):
        """
        Exibir animação de erro
        
        Args:
            message: Mensagem de erro
            duration: Duração da animação
        """
        placeholder = st.empty()
        
        with placeholder.container():
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 2rem;
                background: #f8d7da;
                border-radius: 15px;
                border: 2px solid #dc3545;
                box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
                animation: errorShake 0.6s ease-out;
            ">
                <div style="
                    font-size: 4rem;
                    color: #dc3545;
                    animation: errorIcon 0.8s ease-out;
                ">
                    ❌
                </div>
                <h3 style="color: #721c24; margin: 1rem 0 0 0;">{message}</h3>
            </div>
            
            <style>
                @keyframes errorShake {{
                    0% {{ transform: translateX(0); }}
                    25% {{ transform: translateX(-5px); }}
                    50% {{ transform: translateX(5px); }}
                    75% {{ transform: translateX(-5px); }}
                    100% {{ transform: translateX(0); }}
                }}
                
                @keyframes errorIcon {{
                    0% {{ transform: scale(0) rotate(0deg); }}
                    50% {{ transform: scale(1.2) rotate(90deg); }}
                    100% {{ transform: scale(1) rotate(0deg); }}
                }}
            </style>
            """, unsafe_allow_html=True)
        
        # Auto-remove após duração
        time.sleep(duration)
        placeholder.empty()
    
    def log_user_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """
        Registrar ação do usuário para analytics
        
        Args:
            action: Nome da ação
            details: Detalhes adicionais
        """
        action_log = {
            'action': action,
            'timestamp': datetime.now(),
            'details': details or {},
            'session_id': st.session_state.get('session_id', 'unknown')
        }
        
        st.session_state.user_actions.append(action_log)
        
        # Manter apenas os últimos 100 registros
        if len(st.session_state.user_actions) > 100:
            st.session_state.user_actions = st.session_state.user_actions[-100:]
    
    def show_confirmation_dialog(
        self, 
        title: str, 
        message: str, 
        confirm_text: str = "Confirmar",
        cancel_text: str = "Cancelar"
    ) -> bool:
        """
        Exibir diálogo de confirmação
        
        Args:
            title: Título do diálogo
            message: Mensagem do diálogo
            confirm_text: Texto do botão confirmar
            cancel_text: Texto do botão cancelar
        
        Returns:
            bool: True se confirmado
        """
        # Container do modal
        st.markdown(f"""
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
        ">
            <div style="
                background: white;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                max-width: 500px;
                width: 90%;
                animation: modalFadeIn 0.3s ease-out;
            ">
                <h3 style="color: #495057; margin-bottom: 1rem;">{title}</h3>
                <p style="color: #6c757d; margin-bottom: 2rem;">{message}</p>
            </div>
        </div>
        
        <style>
            @keyframes modalFadeIn {{
                from {{ opacity: 0; transform: scale(0.8); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}
        </style>
        """, unsafe_allow_html=True)
        
        # Botões de confirmação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(cancel_text, use_container_width=True, key="cancel_dialog"):
                return False
        
        with col2:
            if st.button(confirm_text, use_container_width=True, key="confirm_dialog", type="primary"):
                return True
        
        return False
    
    def clear_all_notifications(self):
        """Limpar todas as notificações"""
        st.session_state.notifications = []
    
    def get_user_actions_summary(self) -> Dict[str, Any]:
        """
        Obter resumo das ações do usuário
        
        Returns:
            Dict: Resumo das ações
        """
        if not st.session_state.user_actions:
            return {'total_actions': 0, 'unique_actions': 0, 'most_common': None}
        
        actions = [action['action'] for action in st.session_state.user_actions]
        unique_actions = list(set(actions))
        
        # Ação mais comum
        most_common = max(set(actions), key=actions.count) if actions else None
        
        return {
            'total_actions': len(actions),
            'unique_actions': len(unique_actions),
            'most_common': most_common,
            'session_duration': datetime.now() - st.session_state.user_actions[0]['timestamp'] if st.session_state.user_actions else None
        }

# Instância global do gerenciador de feedback
_feedback_manager = None

def get_feedback_manager() -> FeedbackManager:
    """
    Obter instância global do gerenciador de feedback
    
    Returns:
        FeedbackManager: Instância do gerenciador
    """
    global _feedback_manager
    if _feedback_manager is None:
        _feedback_manager = FeedbackManager()
    return _feedback_manager