#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global CSS - REDESENHADO DO ZERO
CSS limpo e minimalista para todo o sistema
"""

import streamlit as st


def apply_global_css():
    """Aplica CSS global minimalista e funcional"""
    st.markdown("""
    <style>
      /* =========================
         RESET E BASE
         ========================= */
      
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      .stApp {
        background-color: #f5f7fa;
      }

      [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e1e4e8;
      }

      /* =========================
         INPUTS - SIMPLES E LIMPOS
         ========================= */
      
      input, textarea, select {
        background-color: #ffffff !important;
        color: #24292e !important;
        border: 2px solid #d1d5da !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        transition: border-color 0.2s ease !important;
      }

      input:focus, textarea:focus, select:focus {
        border-color: #0366d6 !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1) !important;
      }

      /* =========================
         BOTÕES - CLAROS E LEGÍVEIS
         ========================= */
      
      button {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        font-weight: 500 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
      }

      /* Botão primário - Roxo/Azul Vibrante */
      button[kind="primary"],
      .stButton > button[kind="primary"],
      button[type="submit"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        font-size: 15px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        letter-spacing: 0.3px !important;
      }

      button[kind="primary"]:hover,
      .stButton > button[kind="primary"]:hover,
      button[type="submit"]:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a8a 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
      }

      /* Botão secundário - Verde Moderno */
      button[kind="secondary"],
      .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        font-size: 15px !important;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3) !important;
        letter-spacing: 0.3px !important;
      }

      button[kind="secondary"]:hover,
      .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #0d7d72 0%, #2ed664 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(17, 153, 142, 0.4) !important;
      }

      /* Botão normal - Azul Padrão */
      .stButton > button {
        background-color: #0366d6 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
      }

      .stButton > button:hover {
        background-color: #0256c1 !important;
        transform: translateY(-2px) !important;
      }

      /* =========================
         TEXTOS E TIPOGRAFIA
         ========================= */
      
      body, p, div, span, label {
        color: #24292e !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
      }

      h1, h2, h3, h4, h5, h6 {
        color: #24292e !important;
        font-weight: 600 !important;
      }

      label {
        font-weight: 500 !important;
        margin-bottom: 4px !important;
        display: block !important;
      }

      /* =========================
         TABELAS
         ========================= */
      
      table {
        border-collapse: collapse !important;
        width: 100% !important;
      }

      th {
        background-color: #f6f8fa !important;
        color: #24292e !important;
        font-weight: 600 !important;
        padding: 8px !important;
        border: 1px solid #d1d5da !important;
      }

      td {
        padding: 8px !important;
        border: 1px solid #d1d5da !important;
        color: #24292e !important;
        background-color: #ffffff !important;
      }

      /* =========================
         OUTROS ELEMENTOS
         ========================= */
      
      .stAlert {
        border-radius: 6px !important;
        padding: 12px !important;
      }

      .stTabs [data-baseweb="tab"] {
        color: #586069 !important;
      }

      .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #0366d6 !important;
        border-bottom: 2px solid #0366d6 !important;
      }

      [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e1e4e8 !important;
        border-radius: 6px !important;
        padding: 16px !important;
      }
    </style>
    """, unsafe_allow_html=True)


def get_success_style():
    return "background: #d4edda; color: #155724; border: 1px solid #c3e6cb; padding: 12px; border-radius: 6px;"


def get_warning_style():
    return "background: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 12px; border-radius: 6px;"


def get_error_style():
    return "background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 12px; border-radius: 6px;"


def force_light_theme():
    """Compat shim: reaplica o CSS"""
    apply_global_css()

    """Aplica CSS global profissional com tema claro forçado em todos os elementos."""
    st.markdown("""
    <style>
      /* ========== TEMA CLARO GLOBAL ========== */
      
      /* Background principal */
      .stApp, 
      [data-testid="stAppViewContainer"],
      [data-testid="stHeader"],
      section[data-testid="stSidebar"] > div {
        background-color: #f8f9fa !important;
      }

      /* Sidebar */
      [data-testid="stSidebar"],
      [data-testid="stSidebarNav"] {
        background-color: #ffffff !important;
        border-right: 1px solid #dee2e6 !important;
      }

      /* Container principal */
      .main .block-container {
        padding: 2rem 1rem !important;
        background-color: transparent !important;
      }

      /* ========== TEXTOS E TIPOGRAFIA ========== */
      
      /* Todos os textos */
      body, p, span, div, label, 
      .stMarkdown, .stText, li, td, th,
      [data-testid="stMarkdownContainer"] {
        color: #212529 !important;
      }

      /* Títulos */
      h1, h2, h3, h4, h5, h6 {
        color: #212529 !important;
        font-weight: 600 !important;
      }

      /* ========== INPUTS E FORMULÁRIOS ========== */
      
      /* Text Inputs - CORRIGIDO */
      .stTextInput input,
      .stTextInput > div > div > input,
      input[type="text"],
      input[type="email"],
      input[type="password"],
      input[type="number"],
      [data-baseweb="input"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
      }

      .stTextInput input:focus,
      input:focus,
      [data-baseweb="input"]:focus {
        border-color: #667eea !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
      }

      /* Text Areas - CORRIGIDO */
      .stTextArea textarea,
      .stTextArea > div > div > textarea,
      textarea,
      [data-baseweb="textarea"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
      }

      .stTextArea textarea:focus,
      textarea:focus {
        border-color: #667eea !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
      }

      /* Selectboxes - CRÍTICO */
      .stSelectbox,
      .stSelectbox > div,
      .stSelectbox > div > div,
      .stSelectbox select,
      .stSelectbox [data-baseweb="select"],
      .stSelectbox [data-baseweb="select"] > div,
      [data-baseweb="select"],
      [data-baseweb="select"] > div,
      [role="combobox"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
      }

      /* Dropdown items */
      [data-baseweb="menu"],
      [data-baseweb="popover"],
      [role="listbox"],
      [role="option"] {
        background-color: #ffffff !important;
        color: #212529 !important;
      }

      /* MultiSelect */
      .stMultiSelect,
      .stMultiSelect > div,
      .stMultiSelect > div > div,
      [data-baseweb="tag"] {
        background-color: #ffffff !important;
        color: #212529 !important;
      }

      /* Date Input */
      .stDateInput input,
      input[type="date"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
      }

      /* Number Input */
      .stNumberInput input,
      input[type="number"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
      }

      /* Labels */
      label,
      .stTextInput label,
      .stSelectbox label,
      .stTextArea label,
      .stNumberInput label,
      .stDateInput label,
      [data-testid="stWidgetLabel"] {
        color: #495057 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.25rem !important;
      }

      /* ========== BOTÕES ========== */
      
      /* Botões primários (azul) - MELHORADO */
      .stButton > button,
      button[kind="primary"],
      button[data-testid="baseButton-primary"],
      button[type="submit"] {
        background-color: #0d6efd !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(13, 110, 253, 0.3) !important;
        cursor: pointer !important;
        text-shadow: none !important;
      }

      .stButton > button:hover,
      button[kind="primary"]:hover {
        background-color: #0b5ed7 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(13, 110, 253, 0.4) !important;
      }

      /* Botões secundários (verde) - MELHORADO */
      button[kind="secondary"],
      button[data-testid="baseButton-secondary"] {
        background-color: #28a745 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3) !important;
        text-shadow: none !important;
      }

      button[kind="secondary"]:hover {
        background-color: #218838 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4) !important;
      }

      /* Buttons no form de login */
      form[data-testid="stForm"] button {
        min-height: 50px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
      }

      form[data-testid="stForm"] button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      }

      form[data-testid="stForm"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a8a 100%) !important;
      }
      }

      /* ========== TABS ========== */
      
      .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        gap: 0.5rem !important;
      }

      .stTabs [data-baseweb="tab"] {
        color: #6c757d !important;
        background-color: transparent !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.75rem 1rem !important;
      }

      .stTabs [data-baseweb="tab"]:hover {
        color: #0d6efd !important;
      }

      .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #0d6efd !important;
        background-color: #e7f1ff !important;
        border-bottom: 2px solid #0d6efd !important;
        border-radius: 6px 6px 0 0 !important;
      }

      /* ========== TABELAS E DATAFRAMES ========== */
      
      .stDataFrame,
      [data-testid="stDataFrame"],
      .dataframe,
      table {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
      }

      table thead,
      table thead tr,
      table thead th {
        background-color: #f8f9fa !important;
        color: #212529 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #dee2e6 !important;
      }

      table tbody tr {
        background-color: #ffffff !important;
        border-bottom: 1px solid #dee2e6 !important;
      }

      table tbody tr:hover {
        background-color: #f8f9fa !important;
      }

      table td, table th {
        color: #212529 !important;
        padding: 0.75rem !important;
      }

      /* ========== MÉTRICAS ========== */
      
      [data-testid="stMetric"],
      [data-testid="metric-container"],
      .stMetric {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
      }

      [data-testid="stMetricLabel"] {
        color: #6c757d !important;
        font-weight: 500 !important;
      }

      [data-testid="stMetricValue"] {
        color: #212529 !important;
        font-weight: 700 !important;
      }

      /* ========== ALERTAS E MENSAGENS ========== */
      
      .stAlert {
        border-radius: 6px !important;
        border-left-width: 4px !important;
        padding: 1rem !important;
      }

      .stSuccess {
        background-color: #d1e7dd !important;
        color: #0f5132 !important;
        border-left-color: #198754 !important;
      }

      .stError {
        background-color: #f8d7da !important;
        color: #842029 !important;
        border-left-color: #dc3545 !important;
      }

      .stWarning {
        background-color: #fff3cd !important;
        color: #664d03 !important;
        border-left-color: #ffc107 !important;
      }

      .stInfo {
        background-color: #cfe2ff !important;
        color: #084298 !important;
        border-left-color: #0d6efd !important;
      }

      /* ========== EXPANDERS ========== */
      
      .streamlit-expanderHeader,
      [data-testid="stExpander"] summary {
        background-color: #f8f9fa !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 6px !important;
        padding: 0.75rem 1rem !important;
      }

      .streamlit-expanderHeader:hover {
        background-color: #e9ecef !important;
      }

      /* ========== OUTROS ELEMENTOS ========== */
      
      /* Links */
      a {
        color: #0d6efd !important;
        text-decoration: none !important;
      }

      a:hover {
        color: #0b5ed7 !important;
        text-decoration: underline !important;
      }

      /* Slider */
      .stSlider [data-baseweb="slider"] {
        background-color: #dee2e6 !important;
      }

      .stSlider [data-baseweb="slider"] [role="slider"] {
        background-color: #0d6efd !important;
      }

      /* Checkbox/Radio */
      .stCheckbox label,
      .stRadio label {
        color: #212529 !important;
      }

      /* Download button */
      .stDownloadButton > button {
        background-color: #198754 !important;
        color: #ffffff !important;
      }

      .stDownloadButton > button:hover {
        background-color: #157347 !important;
      }

      /* Spinner */
      .stSpinner > div {
        border-top-color: #0d6efd !important;
      }

      /* Progress bar */
      .stProgress > div > div {
        background-color: #0d6efd !important;
      }

      /* ========== TOOLTIPS E POPOVERS ========== */
      
      /* Tooltips - FORÇAR TEMA CLARO */
      [role="tooltip"],
      [data-baseweb="tooltip"],
      .stTooltipIcon,
      div[data-baseweb="popover"],
      [class*="Tooltip"] {
        background-color: #212529 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
      }

      /* Autocomplete dropdown */
      [data-baseweb="popover"] > div,
      [role="presentation"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
      }

      /* ========== PÁGINA DE LOGIN ========== */
      
      /* Container de login */
      .login-container,
      form[data-testid="stForm"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        padding: 2rem !important;
      }

      /* Inputs na página de login */
      form[data-testid="stForm"] input {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
      }

      /* Placeholders */
      ::placeholder {
        color: #6c757d !important;
        opacity: 0.7 !important;
      }

      /* Form submit buttons */
      form button[type="submit"] {
        background-color: #0d6efd !important;
        color: #ffffff !important;
      }
    </style>
    """, unsafe_allow_html=True)


def get_success_style():
    return "background: #d1fae5; color: #065f46; border: 1px solid #10b981; padding: 0.6rem; border-radius: 8px;"


def get_warning_style():
    return "background: #fff7ed; color: #92400e; border: 1px solid #f59e0b; padding: 0.6rem; border-radius: 8px;"


def get_error_style():
    return "background: #fee2e2; color: #7f1d1d; border: 1px solid #ef4444; padding: 0.6rem; border-radius: 8px;"


def force_light_theme():
  """Compat shim: reaplica o CSS leve. Mantido para compatibilidade com imports antigos."""
  apply_global_css()
