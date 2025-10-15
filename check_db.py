#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar estrutura do banco de dados
"""

import sqlite3
import os

def check_database():
    db_path = 'database/inventario.db'
    
    if not os.path.exists(db_path):
        print('❌ ERRO: Arquivo do banco não encontrado!')
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print('=== 📊 TABELAS EXISTENTES ===')
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            print(f'✓ {table[0]}')
        
        print('\n=== 🔍 ESTRUTURA DAS PRINCIPAIS TABELAS ===')
        main_tables = ['usuarios', 'equipamentos', 'equipamentos_manuais', 'insumos', 'obras', 'movimentacoes', 'auditoria']
        
        for table_name in main_tables:
            try:
                print(f'\n--- 📋 {table_name.upper()} ---')
                cursor.execute(f'PRAGMA table_info({table_name})')
                columns = cursor.fetchall()
                
                if columns:
                    for col in columns:
                        nullable = "NULL" if col[3] == 0 else "NOT NULL"
                        default = f" DEFAULT {col[4]}" if col[4] else ""
                        pk = " 🔑 PRIMARY KEY" if col[5] == 1 else ""
                        print(f'  • {col[1]} ({col[2]}) {nullable}{default}{pk}')
                else:
                    print('  ❌ Tabela não encontrada')
                    
            except Exception as e:
                print(f'  ❌ ERRO: {e}')
        
        # Verificar contagem de registros
        print('\n=== 📈 CONTAGEM DE REGISTROS ===')
        for table_name in [t[0] for t in tables]:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f'📊 {table_name}: {count} registros')
            except Exception as e:
                print(f'❌ {table_name}: ERRO - {e}')
        
        conn.close()
        print('\n✅ Verificação concluída!')
        
    except Exception as e:
        print(f'❌ ERRO GERAL: {e}')

if __name__ == "__main__":
    check_database()