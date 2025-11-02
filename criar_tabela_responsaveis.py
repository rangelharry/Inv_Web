#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar tabela de responsáveis no banco de dados
"""

import sqlite3
from datetime import datetime

def criar_tabela_responsaveis():
    """Criar tabela de responsáveis no banco de dados"""
    
    # Conectar ao banco
    conn = sqlite3.connect('database/inventario.db')
    cursor = conn.cursor()
    
    try:
        # Verificar se tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='responsaveis'")
        tabela_existe = cursor.fetchone() is not None
        
        if tabela_existe:
            print("ℹ️  Tabela 'responsaveis' já existe. Adicionando colunas faltantes...")
            
            # Adicionar colunas se não existirem
            colunas_adicionar = [
                ("cpf", "TEXT"),
                ("setor", "TEXT"),
                ("ativo", "INTEGER DEFAULT 1"),
            ]
            
            for coluna, tipo in colunas_adicionar:
                try:
                    cursor.execute(f"ALTER TABLE responsaveis ADD COLUMN {coluna} {tipo}")
                    print(f"✅ Coluna '{coluna}' adicionada!")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️  Coluna '{coluna}' já existe")
                    else:
                        print(f"⚠️  Erro ao adicionar coluna '{coluna}': {e}")
        else:
            # Criar tabela completa
            cursor.execute("""
                CREATE TABLE responsaveis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT,
                    telefone TEXT,
                    email TEXT,
                    setor TEXT,
                    cargo TEXT,
                    ativo INTEGER DEFAULT 1,
                    observacoes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Tabela 'responsaveis' criada com sucesso!")
        
        # Verificar se já existem responsáveis
        cursor.execute("SELECT COUNT(*) FROM responsaveis")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📝 Inserindo responsáveis padrão...")
            
            # Inserir alguns responsáveis padrão
            responsaveis_padrao = [
                ('João Silva', '111.111.111-11', '(11) 98888-1111', 'joao.silva@empresa.com', 'Manutenção', 'Técnico', 1, 'Responsável pela manutenção geral'),
                ('Maria Santos', '222.222.222-22', '(11) 98888-2222', 'maria.santos@empresa.com', 'Almoxarifado', 'Coordenadora', 1, 'Coordenadora do almoxarifado'),
                ('Pedro Costa', '333.333.333-33', '(11) 98888-3333', 'pedro.costa@empresa.com', 'Obras', 'Engenheiro', 1, 'Engenheiro responsável'),
                ('Ana Oliveira', '444.444.444-44', '(11) 98888-4444', 'ana.oliveira@empresa.com', 'Logística', 'Analista', 1, 'Analista de logística'),
                ('Carlos Ferreira', '555.555.555-55', '(11) 98888-5555', 'carlos.ferreira@empresa.com', 'Compras', 'Comprador', 1, 'Responsável por compras'),
            ]
            
            cursor.executemany("""
                INSERT INTO responsaveis (nome, cpf, telefone, email, setor, cargo, ativo, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, responsaveis_padrao)
            
            print(f"✅ {len(responsaveis_padrao)} responsáveis padrão cadastrados!")
        else:
            print(f"ℹ️  Já existem {count} responsáveis cadastrados")
        
        # Commit das alterações
        conn.commit()
        
        # Verificar resultado final
        cursor.execute("SELECT COUNT(*) FROM responsaveis WHERE ativo = 1")
        count_ativos = cursor.fetchone()[0]
        print(f"✅ Total de responsáveis ativos no banco: {count_ativos}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao criar tabela: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔨 Criando tabela de responsáveis...")
    if criar_tabela_responsaveis():
        print("✅ Processo concluído com sucesso!")
    else:
        print("❌ Erro no processo!")
