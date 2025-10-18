#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global CSS simples e agradável para Streamlit
Uma única opção de estilo com paleta suave, tipografia moderna e elementos limpos.
"""

import streamlit as st


def apply_global_css():
    """Aplica um CSS leve e consistente à aplicação com tema claro forçado."""
    st.markdown("""
    <style>
      /* FORÇAR TEMA CLARO EM TUDO */
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8f9fa !important;
        color: #212529 !important;
      }

      /* Sidebar clara */
      [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        background-color: #ffffff !important;
        color: #212529 !important;
      }

      /* Textos sempre escuros */
      body, p, span, div, label, .stMarkdown, .stText {
        color: #212529 !important;
      }

      /* Títulos */
      h1, h2, h3, h4, h5, h6 {
        color: #212529 !important;
      }

      /* Inputs SEMPRE claros */
      input, textarea, select,
      .stTextInput input,
      .stTextArea textarea,
      .stSelectbox select,
      [data-baseweb="input"],
      [data-baseweb="textarea"],
      [data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px !important;
      }

      /* Labels dos inputs */
      label, .stTextInput label, .stSelectbox label, .stTextArea label {
        color: #495057 !important;
        font-weight: 500 !important;
      }

      /* Botões azuis */
      .stButton > button, button[kind="primary"] {
        background-color: #0d6efd !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
      }

      .stButton > button:hover, button[kind="primary"]:hover {
        background-color: #0b5ed7 !important;
      }

      /* Botões secundários */
      button[kind="secondary"] {
        background-color: #6c757d !important;
        color: #ffffff !important;
        border: none !important;
      }

      button[kind="secondary"]:hover {
        background-color: #5c636a !important;
      }

      /* Tabs */
      .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
      }

      .stTabs [data-baseweb="tab"] {
        color: #495057 !important;
        background-color: transparent !important;
      }

      .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #0d6efd !important;
        background-color: #e7f1ff !important;
      }

      /* Dataframes e tabelas */
      .stDataFrame, [data-testid="stDataFrame"],
      table, thead, tbody, tr, th, td {
        background-color: #ffffff !important;
        color: #212529 !important;
        border-color: #dee2e6 !important;
      }

      /* Métricas */
      [data-testid="stMetric"], [data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
      }

      [data-testid="stMetricLabel"] {
        color: #6c757d !important;
      }

      [data-testid="stMetricValue"] {
        color: #212529 !important;
      }

      /* Expanders */
      .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 6px !important;
      }

      /* Alertas */
      .stAlert, .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 6px !important;
        border: 1px solid !important;
      }

      /* Container principal */
      .main .block-container {
        padding: 2rem 1rem !important;
        background-color: transparent !important;
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
