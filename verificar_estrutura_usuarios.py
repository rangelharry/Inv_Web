#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar estrutura da tabela usuarios
"""

import sqlite3
import os

def verificar_estrutura_usuarios():
    """Verificar estrutura da tabela usuarios"""
    print("🔍 VERIFICANDO ESTRUTURA DA TABELA USUARIOS")
    print("=" * 60)
    
    try:
        # Caminho do banco
        db_path = "database/inventario.db"
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado: {db_path}")
            return
        
        print("1. Conectando ao banco de dados...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("2. Obtendo informações da tabela usuarios...")
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        
        print("\n📋 ESTRUTURA DA TABELA 'usuarios':")
        print("-" * 50)
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - PK: {col[5]}, NotNull: {col[3]}, Default: {col[4]}")
        
        print("\n3. Verificando dados do usuário admin...")
        cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
        admin_data = cursor.fetchone()
        
        if admin_data:
            print("\n👤 DADOS DO ADMIN:")
            print("-" * 30)
            for i, col in enumerate(columns):
                col_name = col[1]
                value = admin_data[i] if i < len(admin_data) else "N/A"
                if col_name.lower() in ['password', 'senha', 'pwd']:
                    # Não mostrar senha completa
                    value = f"{str(value)[:20]}..." if value else "N/A"
                print(f"   {col_name}: {value}")
        else:
            print("   ❌ Usuário admin não encontrado!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verificar_estrutura_usuarios()