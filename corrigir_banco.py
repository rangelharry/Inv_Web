#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir estrutura do banco de dados
"""

import sqlite3
import os
import sys

def verificar_e_corrigir_banco():
    """Verificar estrutura do banco e criar tabelas se necessário"""
    print("🔍 VERIFICANDO ESTRUTURA DO BANCO DE DADOS")
    print("=" * 60)
    
    db_path = "database/inventario.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas_existentes = [row[0] for row in cursor.fetchall()]
        
        print("📋 TABELAS ENCONTRADAS:")
        for tabela in tabelas_existentes:
            print(f"   ✅ {tabela}")
        
        # Tabelas esperadas
        tabelas_esperadas = [
            'usuarios', 'equipamentos_eletricos', 'equipamentos_manuais', 
            'insumos', 'obras', 'movimentacoes'
        ]
        
        # Verificar tabelas faltantes
        tabelas_faltantes = [t for t in tabelas_esperadas if t not in tabelas_existentes]
        
        if tabelas_faltantes:
            print("\n⚠️ TABELAS FALTANTES:")
            for tabela in tabelas_faltantes:
                print(f"   ❌ {tabela}")
                
            print("\n🔧 CRIANDO TABELAS FALTANTES...")
            
            # Criar tabela equipamentos_eletricos se não existir
            if 'equipamentos_eletricos' in tabelas_faltantes:
                cursor.execute("""
                    CREATE TABLE equipamentos_eletricos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo TEXT UNIQUE NOT NULL,
                        nome TEXT NOT NULL,
                        categoria TEXT,
                        status TEXT DEFAULT 'Disponível',
                        localizacao TEXT,
                        marca TEXT,
                        modelo TEXT,
                        valor_compra REAL,
                        observacoes TEXT
                    )
                """)
                print("   ✅ Tabela equipamentos_eletricos criada")
            
            # Criar tabela equipamentos_manuais se não existir
            if 'equipamentos_manuais' in tabelas_faltantes:
                cursor.execute("""
                    CREATE TABLE equipamentos_manuais (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo TEXT UNIQUE NOT NULL,
                        descricao TEXT NOT NULL,
                        tipo TEXT,
                        status TEXT DEFAULT 'Disponível',
                        localizacao TEXT,
                        quantitativo INTEGER DEFAULT 1,
                        estado TEXT,
                        marca TEXT,
                        valor REAL,
                        data_compra DATE,
                        loja TEXT,
                        observacoes TEXT
                    )
                """)
                print("   ✅ Tabela equipamentos_manuais criada")
            
            # Criar tabela insumos se não existir
            if 'insumos' in tabelas_faltantes:
                cursor.execute("""
                    CREATE TABLE insumos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo TEXT UNIQUE NOT NULL,
                        descricao TEXT NOT NULL,
                        categoria TEXT,
                        quantidade INTEGER DEFAULT 0,
                        quantidade_minima INTEGER DEFAULT 0,
                        preco_unitario REAL,
                        localizacao TEXT,
                        observacoes TEXT
                    )
                """)
                print("   ✅ Tabela insumos criada")
            
            # Criar tabela obras se não existir
            if 'obras' in tabelas_faltantes:
                cursor.execute("""
                    CREATE TABLE obras (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo TEXT UNIQUE NOT NULL,
                        nome TEXT NOT NULL,
                        descricao TEXT,
                        status TEXT DEFAULT 'Ativa',
                        data_inicio DATE,
                        data_fim DATE,
                        responsavel TEXT,
                        observacoes TEXT
                    )
                """)
                print("   ✅ Tabela obras criada")
            
            # Criar tabela movimentacoes se não existir
            if 'movimentacoes' in tabelas_faltantes:
                cursor.execute("""
                    CREATE TABLE movimentacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT NOT NULL,
                        item_codigo TEXT NOT NULL,
                        item_descricao TEXT,
                        origem TEXT,
                        destino TEXT,
                        quantidade INTEGER DEFAULT 1,
                        responsavel TEXT,
                        data DATETIME DEFAULT CURRENT_TIMESTAMP,
                        observacoes TEXT
                    )
                """)
                print("   ✅ Tabela movimentacoes criada")
            
            conn.commit()
            print("\n✅ ESTRUTURA DO BANCO CORRIGIDA!")
        else:
            print("\n✅ TODAS AS TABELAS ESTÃO PRESENTES!")
        
        # Inserir dados de exemplo se as tabelas estão vazias
        print("\n📊 VERIFICANDO DADOS DE EXEMPLO...")
        
        # Verificar se há equipamentos elétricos
        cursor.execute("SELECT COUNT(*) FROM equipamentos_eletricos")
        count_eletricos = cursor.fetchone()[0]
        
        if count_eletricos == 0:
            print("   📦 Inserindo equipamentos elétricos de exemplo...")
            equipamentos_exemplo = [
                ('ELE-001', 'Furadeira Makita', 'Furadeira', 'Disponível', 'Almoxarifado', 'Makita', 'DHP484', 450.00),
                ('ELE-002', 'Serra Circular Bosch', 'Serra', 'Em uso', 'Obra A', 'Bosch', 'GKS 190', 320.00),
                ('ELE-003', 'Parafusadeira Dewalt', 'Parafusadeira', 'Disponível', 'Almoxarifado', 'Dewalt', 'DCD771', 280.00),
            ]
            
            for equip in equipamentos_exemplo:
                cursor.execute("""
                    INSERT INTO equipamentos_eletricos 
                    (codigo, nome, categoria, status, localizacao, marca, modelo, valor_compra)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, equip)
            
            print(f"   ✅ {len(equipamentos_exemplo)} equipamentos elétricos inseridos")
        
        # Verificar se há equipamentos manuais
        cursor.execute("SELECT COUNT(*) FROM equipamentos_manuais")
        count_manuais = cursor.fetchone()[0]
        
        if count_manuais == 0:
            print("   🔧 Inserindo equipamentos manuais de exemplo...")
            manuais_exemplo = [
                ('MAN-001', 'Chave de Fenda 1/4', 'Ferramenta Manual', 'Disponível', 'Almoxarifado', 5, 'Novo', 'Tramontina', 15.00),
                ('MAN-002', 'Martelo 500g', 'Ferramenta Manual', 'Em Uso', 'Obra B', 2, 'Usado - Bom Estado', 'Stanley', 35.00),
                ('MAN-003', 'Chave Inglesa 12', 'Ferramenta Manual', 'Disponível', 'Almoxarifado', 3, 'Novo', 'Gedore', 85.00),
            ]
            
            for equip in manuais_exemplo:
                cursor.execute("""
                    INSERT INTO equipamentos_manuais 
                    (codigo, descricao, tipo, status, localizacao, quantitativo, estado, marca, valor)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, equip)
            
            print(f"   ✅ {len(manuais_exemplo)} equipamentos manuais inseridos")
        
        # Verificar se há insumos
        cursor.execute("SELECT COUNT(*) FROM insumos")
        count_insumos = cursor.fetchone()[0]
        
        if count_insumos == 0:
            print("   📦 Inserindo insumos de exemplo...")
            insumos_exemplo = [
                ('INS-001', 'Parafuso Phillips 3x20mm', 'Fixação', 500, 100, 0.05, 'Almoxarifado'),
                ('INS-002', 'Tinta Látex Branca 18L', 'Tintas', 5, 2, 85.00, 'Almoxarifado'),
                ('INS-003', 'Cimento CP-II 50kg', 'Materiais', 20, 5, 28.50, 'Depósito'),
            ]
            
            for insumo in insumos_exemplo:
                cursor.execute("""
                    INSERT INTO insumos 
                    (codigo, descricao, categoria, quantidade, quantidade_minima, preco_unitario, localizacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, insumo)
            
            print(f"   ✅ {len(insumos_exemplo)} insumos inseridos")
        
        # Verificar se há obras
        cursor.execute("SELECT COUNT(*) FROM obras")
        count_obras = cursor.fetchone()[0]
        
        if count_obras == 0:
            print("   🏗️ Inserindo obras de exemplo...")
            obras_exemplo = [
                ('OBR-001', 'Reforma Escritório Central', 'Reforma completa do escritório', 'Ativa', '2025-01-15', None, 'João Silva'),
                ('OBR-002', 'Construção Galpão B', 'Novo galpão industrial', 'Ativa', '2025-02-01', None, 'Maria Santos'),
            ]
            
            for obra in obras_exemplo:
                cursor.execute("""
                    INSERT INTO obras 
                    (codigo, nome, descricao, status, data_inicio, data_fim, responsavel)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, obra)
            
            print(f"   ✅ {len(obras_exemplo)} obras inseridas")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 BANCO DE DADOS CONFIGURADO COM SUCESSO!")
        print("\n📊 RESUMO:")
        print(f"   📱 Equipamentos Elétricos: {count_eletricos if count_eletricos > 0 else len(equipamentos_exemplo) if count_eletricos == 0 else 0}")
        print(f"   🔧 Equipamentos Manuais: {count_manuais if count_manuais > 0 else len(manuais_exemplo) if count_manuais == 0 else 0}")
        print(f"   📦 Insumos: {count_insumos if count_insumos > 0 else len(insumos_exemplo) if count_insumos == 0 else 0}")
        print(f"   🏗️ Obras: {count_obras if count_obras > 0 else len(obras_exemplo) if count_obras == 0 else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    verificar_e_corrigir_banco()