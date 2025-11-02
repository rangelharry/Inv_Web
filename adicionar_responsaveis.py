#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar responsáveis padrão ao sistema
"""

import sqlite3

def adicionar_responsaveis():
    """Adicionar responsáveis padrão"""
    
    conn = sqlite3.connect('database/inventario.db')
    cursor = conn.cursor()
    
    try:
        # Verificar quantos já existem
        cursor.execute("SELECT COUNT(*) FROM responsaveis")
        count_atual = cursor.fetchone()[0]
        
        print(f"📊 Responsáveis já cadastrados: {count_atual}")
        
        # Responsáveis padrão
        responsaveis = [
            ('João Silva', '111.111.111-11', '(11) 98888-1111', 'joao.silva@empresa.com', 'Manutenção', 'Técnico', 1, 'Responsável pela manutenção geral'),
            ('Maria Santos', '222.222.222-22', '(11) 98888-2222', 'maria.santos@empresa.com', 'Almoxarifado', 'Coordenadora', 1, 'Coordenadora do almoxarifado'),
            ('Pedro Costa', '333.333.333-33', '(11) 98888-3333', 'pedro.costa@empresa.com', 'Obras', 'Engenheiro', 1, 'Engenheiro responsável'),
            ('Ana Oliveira', '444.444.444-44', '(11) 98888-4444', 'ana.oliveira@empresa.com', 'Logística', 'Analista', 1, 'Analista de logística'),
            ('Carlos Ferreira', '555.555.555-55', '(11) 98888-5555', 'carlos.ferreira@empresa.com', 'Compras', 'Comprador', 1, 'Responsável por compras'),
        ]
        
        adicionados = 0
        
        for nome, cpf, telefone, email, setor, cargo, ativo, obs in responsaveis:
            # Verificar se já existe (por nome)
            cursor.execute("SELECT id FROM responsaveis WHERE nome = ?", (nome,))
            existe = cursor.fetchone()
            
            if not existe:
                cursor.execute("""
                    INSERT INTO responsaveis (nome, cpf, telefone, email, setor, cargo, ativo, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, cpf, telefone, email, setor, cargo, ativo, obs))
                adicionados += 1
                print(f"✅ Adicionado: {nome}")
            else:
                print(f"ℹ️  Já existe: {nome}")
        
        conn.commit()
        
        # Verificar total final
        cursor.execute("SELECT COUNT(*) FROM responsaveis WHERE ativo = 1")
        count_final = cursor.fetchone()[0]
        
        print(f"\n📊 Total de responsáveis ativos: {count_final}")
        print(f"✅ Responsáveis adicionados nesta execução: {adicionados}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔨 Adicionando responsáveis padrão...\n")
    if adicionar_responsaveis():
        print("\n✅ Processo concluído!")
    else:
        print("\n❌ Erro no processo!")
