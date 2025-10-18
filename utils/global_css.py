#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS TOTALMENTE NOVO - ZERO TOLERÂNCIA AO TEMA ESCURO
Sistema de CSS de força bruta absoluta
"""

import streamlit as st

def apply_global_css():
    """
    CSS EXTREMAMENTE AGRESSIVO - QUEBRA QUALQUER TEMA ESCURO
    """
    # APLICAR CSS INLINE COM MÁXIMA PRIORIDADE
    st.markdown("""
    <style>
        /* ========================================
           NUCLEAR CSS - DESTRUIR TEMA ESCURO
           ======================================== */
        
        /* RESET ABSOLUTO - SEM EXCEÇÕES */
        * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            box-sizing: border-box !important;
        }
        
        /* STREAMLIT FORÇADO BRANCO */
        .stApp, .stApp *, [data-testid="stApp"], [data-testid="stApp"] * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        /* CONTAINERS PRINCIPAIS - BRANCO ABSOLUTO */
        html, body, #root, .stApp, .main, 
        [data-testid="stAppViewContainer"],
        [data-testid="stMainBlockContainer"],
        [data-testid="stMain"],
        .stMainBlockContainer, .stMain,
        .main .block-container,
        [data-testid="block-container"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            font-family: Arial, sans-serif !important;
        }
        
        /* SIDEBAR - CINZA CLARO */
        .stSidebar, .stSidebar *, .stSidebar div {
            background: #f0f0f0 !important;
            background-color: #f0f0f0 !important;
            color: #000000 !important;
        }
        
        /* TÍTULOS - PRETO FORTE */
        h1, h2, h3, h4, h5, h6 {
            color: #000000 !important;
            background: #ffffff !important;
            font-weight: bold !important;
            margin: 1rem 0 !important;
        }
        
        /* BOTÕES - AZUL FORTE */
        .stButton > button, button {
            background: #0066ff !important;
            background-color: #0066ff !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: bold !important;
        }
        
        .stButton > button:hover, button:hover {
            background: #0044cc !important;
            background-color: #0044cc !important;
        }
        
        /* INPUTS - BRANCO COM BORDA */
        input, textarea, select,
        .stTextInput input, 
        .stTextArea textarea, 
        .stSelectbox select,
        .stNumberInput input {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #cccccc !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
        }
        
        input:focus, textarea:focus, select:focus {
            background: #ffffff !important;
            color: #000000 !important;
            border-color: #0066ff !important;
        }
        
        /* ALERTAS - CORES VIVAS */
        .stSuccess {
            background: #00ff00 !important;
            color: #000000 !important;
            border: 2px solid #00cc00 !important;
            padding: 1rem !important;
            border-radius: 8px !important;
        }
        
        .stError {
            background: #ff6666 !important;
            color: #000000 !important;
            border: 2px solid #ff0000 !important;
            padding: 1rem !important;
            border-radius: 8px !important;
        }
        
        .stWarning {
            background: #ffff66 !important;
            color: #000000 !important;
            border: 2px solid #ffcc00 !important;
            padding: 1rem !important;
            border-radius: 8px !important;
        }
        
        .stInfo {
            background: #66ccff !important;
            color: #000000 !important;
            border: 2px solid #0099cc !important;
            padding: 1rem !important;
            border-radius: 8px !important;
        }
        
        /* TEXTO - PRETO ABSOLUTO */
        p, span, div, label, a, li, ul, ol {
            color: #000000 !important;
            background: transparent !important;
        }
        
        /* TABELAS - BRANCO */
        table, thead, tbody, tr, th, td {
            background: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cccccc !important;
        }
        
        /* MÉTRICAS - BRANCO */
        .stMetric, [data-testid="metric-container"] {
            background: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #cccccc !important;
            border-radius: 8px !important;
            padding: 1rem !important;
        }
        
        /* QUEBRAR QUALQUER TEMA ESCURO - ULTRA AGRESSIVO */
        [style*="background-color: rgb(14, 17, 23)"],
        [style*="background-color: #0e1117"],
        [style*="background: rgb(14, 17, 23)"],
        [style*="background: #0e1117"],
        [style*="color: white"],
        [style*="color: #ffffff"],
        [data-theme="dark"],
        [data-theme="dark"] *,
        .stApp[data-theme="dark"],
        .stApp[data-theme="dark"] * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        /* TODAS AS CLASSES CSS DINÂMICAS */
        [class*="css-"], [class*="st-"], [class*="css-"] * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        /* FORÇAR EM ELEMENTOS ESPECÍFICOS */
        section, article, div, main, aside, header, footer,
        .element-container, .stMarkdown, .stText, .stButton,
        .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        /* ÚLTIMA LINHA DE DEFESA - SEM ESCAPE */
        html, body, #root {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        .stApp, .stApp > div, .stApp * {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def get_success_style():
    """Estilo de sucesso"""
    return "background: #00ff00 !important; color: #000000 !important; border: 2px solid #00cc00 !important; padding: 1rem !important; border-radius: 8px !important;"

def get_warning_style():
    """Estilo de aviso"""
    return "background: #ffff66 !important; color: #000000 !important; border: 2px solid #ffcc00 !important; padding: 1rem !important; border-radius: 8px !important;"

def get_error_style():
    """Estilo de erro"""
    return "background: #ff6666 !important; color: #000000 !important; border: 2px solid #ff0000 !important; padding: 1rem !important; border-radius: 8px !important;"

def force_light_theme():
    """
    FUNÇÃO NUCLEAR - FORÇA TEMA CLARO VIA JAVASCRIPT
    """
    st.markdown("""
    <script>
        // FORÇAR TEMA CLARO VIA JAVASCRIPT
        function forceWhiteTheme() {
            // Remover qualquer atributo de tema escuro
            document.documentElement.removeAttribute('data-theme');
            document.body.removeAttribute('data-theme');
            
            // Forçar estilos no HTML diretamente
            const style = document.createElement('style');
            style.innerHTML = `
                * { 
                    background: #ffffff !important; 
                    background-color: #ffffff !important; 
                    color: #000000 !important; 
                }
                .stApp, .stApp * { 
                    background: #ffffff !important; 
                    color: #000000 !important; 
                }
            `;
            document.head.appendChild(style);
            
            // Aplicar estilos em todos os elementos
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                el.style.setProperty('background-color', '#ffffff', 'important');
                el.style.setProperty('color', '#000000', 'important');
                el.style.setProperty('background', '#ffffff', 'important');
            });
        }
        
        // Executar imediatamente
        forceWhiteTheme();
        
        // Executar quando a página carregar
        document.addEventListener('DOMContentLoaded', forceWhiteTheme);
        
        // Executar em intervalos para pegar mudanças dinâmicas
        setInterval(forceWhiteTheme, 1000);
    </script>
    """, unsafe_allow_html=True)