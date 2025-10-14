#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de debug das páginas do sistema
"""

import sys
import os
sys.path.append('E:/GITHUB/Inv_Web')

def test_page_loading():
    """Testar carregamento das páginas exatamente como o app.py faz"""
    
    pages_to_test = [
        "equipamentos_manuais",
        "insumos", 
        "obras",
        "movimentacoes",
        "relatorios",
        "configuracoes"
    ]
    
    for page_name in pages_to_test:
        print(f"\n=== Testando {page_name} ===")
        
        try:
            if page_name == "equipamentos_manuais":
                from pages import show_equipamentos_manuais
                print(f"Importacao OK: {show_equipamentos_manuais}")
                # Não vamos executar por causa do streamlit, só testar import
                
            elif page_name == "insumos":
                from pages import show_insumos
                print(f"Importacao OK: {show_insumos}")
                
            elif page_name == "obras":
                from pages import show_obras
                print(f"Importacao OK: {show_obras}")
                
            elif page_name == "movimentacoes":
                from pages import show_movimentacoes
                print(f"Importacao OK: {show_movimentacoes}")
                
            elif page_name == "relatorios":
                from pages import show_relatorios
                print(f"Importacao OK: {show_relatorios}")
                
            elif page_name == "configuracoes":
                from pages import show_configuracoes
                print(f"Importacao OK: {show_configuracoes}")
                
        except ImportError as e:
            print(f"ImportError: {e}")
        except Exception as e:
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_page_loading()