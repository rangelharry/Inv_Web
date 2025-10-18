#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global CSS simples e agradável para Streamlit
Uma única opção de estilo com paleta suave, tipografia moderna e elementos limpos.
"""

import streamlit as st


def apply_global_css():
    """Aplica um CSS leve e consistente à aplicação."""
    st.markdown("""
    <style>
      :root {
        --bg: #f7f9fb;
        --card: #ffffff;
        --muted: #6b7280;
        --accent: #2563eb; /* azul */
        --accent-600: #1e40af;
        --border: #e6edf3;
        --radius: 10px;
        --font-sans: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
      }

      html, body, .stApp {
        background: var(--bg) !important;
        color: #0f172a !important;
        font-family: var(--font-sans) !important;
      }

      /* Container principal */
      .main .block-container {
        background: transparent !important;
        padding: 24px !important;
      }

      /* Cards e blocos */
      .stCard, .stMetric, .stBlock, .stExpandable, .element-container {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06) !important;
        padding: 14px !important;
      }

      /* Sidebar */
      .stSidebar {
        background: var(--card) !important;
        border-right: 1px solid var(--border) !important;
      }

      /* Títulos */
      h1, h2, h3 {
        color: #0f172a !important;
        margin: 0.25rem 0 0.6rem 0 !important;
      }

      /* Botões */
      .stButton>button, button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
      }
      .stButton>button:hover, button:hover {
        background: var(--accent-600) !important;
      }

      /* Inputs */
      input, textarea, select {
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 8px !important;
        background: white !important;
      }

      /* Tabelas */
      table, thead, tbody, tr, th, td {
        border: 1px solid var(--border) !important;
        background: white !important;
        color: #0f172a !important;
      }
      tbody tr:nth-child(even) td { background: #fbfdff !important; }

      /* Texto secundário */
      .muted, .stMarkdown em, .stText {
        color: var(--muted) !important;
      }

      a { color: var(--accent) !important; }

      /* Pequenos ajustes responsivos */
      @media (max-width: 600px) {
        .main .block-container { padding: 12px !important; }
        .stButton>button { width: 100% !important; }
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
