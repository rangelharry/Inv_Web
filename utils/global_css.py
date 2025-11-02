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
    """Compat shim: reaplica o CSS leve. Mantido para compatibilidade com imports antigos."""
    apply_global_css()
