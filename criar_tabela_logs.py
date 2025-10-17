#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar a tabela de logs_sistema no banco de dados
"""

import sqlite3
import os

def criar_tabela_logs():
    """Criar tabela de logs se não existir"""
    
    db_path = "database/inventario.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela já existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='logs_sistema'
        """)
        
        if cursor.fetchone():
            print("✅ Tabela logs_sistema já existe")
            return True
        
        # Criar tabela de logs
        cursor.execute("""
            CREATE TABLE logs_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                item_code TEXT,
                additional_data TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios (id)
            )
        """)
        
        # Criar índices para melhor performance
        cursor.execute("""
            CREATE INDEX idx_logs_timestamp ON logs_sistema(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_logs_user_id ON logs_sistema(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_logs_action ON logs_sistema(action)
        """)
        
        conn.commit()
        print("✅ Tabela logs_sistema criada com sucesso!")
        
        # Inserir alguns logs de exemplo
        cursor.execute("""
            INSERT INTO logs_sistema (action, details, item_code)
            VALUES ('system_init', 'Sistema inicializado com tabela de logs', 'SYSTEM')
        """)
        
        conn.commit()
        print("✅ Log inicial inserido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Criando tabela de logs...")
    sucesso = criar_tabela_logs()
    
    if sucesso:
        print("✅ Processo concluído com sucesso!")
    else:
        print("❌ Processo falhou!")