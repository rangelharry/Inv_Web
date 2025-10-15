#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Validações de Integridade do Banco de Dados
Script para implementar constraints, foreign keys, triggers e validações
"""

import sqlite3
import sys
import os
from datetime import datetime

# Adicionar pasta raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.connection import DatabaseConnection
from utils.logging import SystemLogger

logger = SystemLogger()

class DatabaseIntegrityManager:
    """Gerenciador de integridade do banco de dados"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def enable_foreign_keys(self):
        """Habilitar foreign keys no SQLite"""
        try:
            self.db.execute_query("PRAGMA foreign_keys = ON")
            logger.log_action("DATABASE", "Foreign keys habilitadas")
            print("OK - Foreign keys habilitadas")
            return True
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao habilitar foreign keys: {e}")
            print(f"ERRO - Erro ao habilitar foreign keys: {e}")
            return False
    
    def create_indexes(self):
        """Criar índices para melhorar performance e integridade"""
        indexes = [
            # Índices únicos para códigos
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_equipamentos_eletricos_codigo ON equipamentos_eletricos(codigo)",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_equipamentos_manuais_codigo ON equipamentos_manuais(codigo)",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_insumos_codigo ON insumos(codigo)",
            
            # Índices únicos para usuários
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario)",
            
            # Índices para melhorar consultas
            "CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes(data)",
            "CREATE INDEX IF NOT EXISTS idx_movimentacoes_codigo ON movimentacoes(codigo)",
            "CREATE INDEX IF NOT EXISTS idx_equipamentos_status ON equipamentos_eletricos(status)",
            "CREATE INDEX IF NOT EXISTS idx_equipamentos_manuais_status ON equipamentos_manuais(status)",
            "CREATE INDEX IF NOT EXISTS idx_insumos_categoria ON insumos(categoria)",
        ]
        
        success_count = 0
        for index_sql in indexes:
            try:
                self.db.execute_query(index_sql)
                success_count += 1
            except Exception as e:
                print(f"AVISO - Erro ao criar indice: {e}")
        
        logger.log_action("DATABASE", f"{success_count} índices criados/verificados")
        print(f"OK - {success_count}/{len(indexes)} indices criados/verificados")
        return success_count == len(indexes)
    
    def create_validation_triggers(self):
        """Criar triggers para validação de dados"""
        triggers = [
            # Trigger para validar status de equipamentos elétricos
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_eletricos_status
            BEFORE INSERT ON equipamentos_eletricos
            WHEN NEW.status NOT IN ('disponivel', 'em_uso', 'manutencao', 'inativo')
            BEGIN
                SELECT RAISE(ABORT, 'Status inválido para equipamento elétrico');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_eletricos_status_update
            BEFORE UPDATE ON equipamentos_eletricos
            WHEN NEW.status NOT IN ('disponivel', 'em_uso', 'manutencao', 'inativo')
            BEGIN
                SELECT RAISE(ABORT, 'Status inválido para equipamento elétrico');
            END
            """,
            
            # Trigger para validar status de equipamentos manuais
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_manuais_status
            BEFORE INSERT ON equipamentos_manuais
            WHEN NEW.status NOT IN ('Disponível', 'Em Uso', 'Manutenção', 'Inativo', 'Emprestado')
            BEGIN
                SELECT RAISE(ABORT, 'Status inválido para equipamento manual');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_manuais_status_update
            BEFORE UPDATE ON equipamentos_manuais
            WHEN NEW.status NOT IN ('Disponível', 'Em Uso', 'Manutenção', 'Inativo', 'Emprestado')
            BEGIN
                SELECT RAISE(ABORT, 'Status inválido para equipamento manual');
            END
            """,
            
            # Trigger para validar quantidades não negativas
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_manuais_quantidade
            BEFORE INSERT ON equipamentos_manuais
            WHEN NEW.quantitativo < 0
            BEGIN
                SELECT RAISE(ABORT, 'Quantidade não pode ser negativa');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_manuais_quantidade_update
            BEFORE UPDATE ON equipamentos_manuais
            WHEN NEW.quantitativo < 0
            BEGIN
                SELECT RAISE(ABORT, 'Quantidade não pode ser negativa');
            END
            """,
            
            # Trigger para validar quantidades de insumos
            """
            CREATE TRIGGER IF NOT EXISTS validate_insumos_quantidade
            BEFORE INSERT ON insumos
            WHEN NEW.quantidade < 0
            BEGIN
                SELECT RAISE(ABORT, 'Quantidade de insumo não pode ser negativa');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS validate_insumos_quantidade_update
            BEFORE UPDATE ON insumos
            WHEN NEW.quantidade < 0
            BEGIN
                SELECT RAISE(ABORT, 'Quantidade de insumo não pode ser negativa');
            END
            """,
            
            # Trigger para validar códigos não vazios
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_codigo
            BEFORE INSERT ON equipamentos_eletricos
            WHEN NEW.codigo IS NULL OR TRIM(NEW.codigo) = ''
            BEGIN
                SELECT RAISE(ABORT, 'Código do equipamento elétrico não pode estar vazio');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS validate_equipamentos_manuais_codigo
            BEFORE INSERT ON equipamentos_manuais
            WHEN NEW.codigo IS NULL OR TRIM(NEW.codigo) = ''
            BEGIN
                SELECT RAISE(ABORT, 'Código do equipamento manual não pode estar vazio');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS validate_insumos_codigo
            BEFORE INSERT ON insumos
            WHEN NEW.codigo IS NULL OR TRIM(NEW.codigo) = ''
            BEGIN
                SELECT RAISE(ABORT, 'Código do insumo não pode estar vazio');
            END
            """,
            
            # Trigger para logging automático de alterações
            """
            CREATE TRIGGER IF NOT EXISTS log_equipamentos_eletricos_changes
            AFTER UPDATE ON equipamentos_eletricos
            BEGIN
                INSERT INTO logs_sistema (timestamp, nivel, usuario, acao, detalhes)
                VALUES (datetime('now'), 'INFO', 'SYSTEM', 'UPDATE', 
                       'Equipamento elétrico ' || NEW.codigo || ' atualizado');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS log_equipamentos_manuais_changes
            AFTER UPDATE ON equipamentos_manuais
            BEGIN
                INSERT INTO logs_sistema (timestamp, nivel, usuario, acao, detalhes)
                VALUES (datetime('now'), 'INFO', 'SYSTEM', 'UPDATE', 
                       'Equipamento manual ' || NEW.codigo || ' atualizado');
            END
            """,
            
            """
            CREATE TRIGGER IF NOT EXISTS log_insumos_changes
            AFTER UPDATE ON insumos
            BEGIN
                INSERT INTO logs_sistema (timestamp, nivel, usuario, acao, detalhes)
                VALUES (datetime('now'), 'INFO', 'SYSTEM', 'UPDATE', 
                       'Insumo ' || NEW.codigo || ' atualizado');
            END
            """
        ]
        
        success_count = 0
        for trigger_sql in triggers:
            try:
                self.db.execute_query(trigger_sql)
                success_count += 1
            except Exception as e:
                print(f"AVISO - Erro ao criar trigger: {e}")
        
        logger.log_action("DATABASE", f"{success_count} triggers criados")
        print(f"OK - {success_count}/{len(triggers)} triggers criados")
        return success_count == len(triggers)
    
    def add_constraints(self):
        """Adicionar constraints de integridade"""
        constraints = []
        
        try:
            # Verificar se é necessário adicionar constraints
            # No SQLite, constraints são adicionadas durante a criação da tabela
            # ou através de ALTER TABLE (limitado)
            
            # Criar tabela de verificações para garantir integridade referencial
            constraint_table = """
            CREATE TABLE IF NOT EXISTS integrity_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                check_type TEXT NOT NULL,
                check_sql TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            self.db.execute_query(constraint_table)
            
            # Inserir verificações de integridade
            integrity_checks = [
                ("movimentacoes", "FOREIGN_KEY", 
                 "SELECT COUNT(*) FROM movimentacoes m WHERE m.codigo NOT IN (SELECT codigo FROM equipamentos_eletricos UNION SELECT codigo FROM equipamentos_manuais UNION SELECT codigo FROM insumos)",
                 "Verificar se todos os códigos em movimentações existem nas tabelas de origem"),
                
                ("equipamentos_eletricos", "UNIQUE", 
                 "SELECT codigo, COUNT(*) FROM equipamentos_eletricos GROUP BY codigo HAVING COUNT(*) > 1",
                 "Verificar códigos duplicados em equipamentos elétricos"),
                
                ("equipamentos_manuais", "UNIQUE", 
                 "SELECT codigo, COUNT(*) FROM equipamentos_manuais GROUP BY codigo HAVING COUNT(*) > 1",
                 "Verificar códigos duplicados em equipamentos manuais"),
                
                ("insumos", "UNIQUE", 
                 "SELECT codigo, COUNT(*) FROM insumos GROUP BY codigo HAVING COUNT(*) > 1",
                 "Verificar códigos duplicados em insumos"),
                
                ("usuarios", "UNIQUE", 
                 "SELECT email, COUNT(*) FROM usuarios GROUP BY email HAVING COUNT(*) > 1",
                 "Verificar emails duplicados de usuários")
            ]
            
            for table_name, check_type, check_sql, description in integrity_checks:
                insert_sql = """
                INSERT OR REPLACE INTO integrity_checks (table_name, check_type, check_sql, description)
                VALUES (?, ?, ?, ?)
                """
                self.db.execute_query(insert_sql, (table_name, check_type, check_sql, description))
            
            logger.log_action("DATABASE", "Constraints de integridade configurados")
            print("OK - Constraints de integridade configurados")
            return True
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao configurar constraints: {e}")
            print(f"ERRO - Erro ao configurar constraints: {e}")
            return False
    
    def create_audit_table(self):
        """Criar tabela de auditoria para mudanças"""
        try:
            audit_table_sql = """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                table_name TEXT NOT NULL,
                operation TEXT NOT NULL,
                record_id TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                user_id TEXT,
                ip_address TEXT
            )
            """
            
            self.db.execute_query(audit_table_sql)
            
            # Criar índices para a tabela de auditoria
            audit_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_audit_table_name ON audit_log(table_name)",
                "CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_log(operation)",
                "CREATE INDEX IF NOT EXISTS idx_audit_record_id ON audit_log(record_id)"
            ]
            
            for index_sql in audit_indexes:
                self.db.execute_query(index_sql)
            
            logger.log_action("DATABASE", "Tabela de auditoria criada")
            print("OK - Tabela de auditoria criada")
            return True
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao criar tabela de auditoria: {e}")
            print(f"ERRO - Erro ao criar tabela de auditoria: {e}")
            return False
    
    def run_integrity_checks(self):
        """Executar verificações de integridade"""
        try:
            checks_result = self.db.execute_query("SELECT * FROM integrity_checks")
            
            if not checks_result:
                print("INFO - Nenhuma verificacao de integridade configurada")
                return True
            
            issues_found = 0
            for check in checks_result:
                try:
                    result = self.db.execute_query(check['check_sql'])
                    
                    if result and len(result) > 0:
                        if check['check_type'] == 'UNIQUE':
                            # Para verificações de unicidade, resultado indica duplicatas
                            if result:
                                issues_found += len(result)
                                print(f"AVISO - {check['description']}: {len(result)} problema(s) encontrado(s)")
                                for issue in result:
                                    print(f"   - {issue}")
                        else:
                            # Para outras verificações, resultado > 0 indica problema
                            count = list(result[0].values())[0] if result[0] else 0
                            if count > 0:
                                issues_found += count
                                print(f"AVISO - {check['description']}: {count} problema(s) encontrado(s)")
                    
                except Exception as e:
                    print(f"ERRO - Erro ao executar verificacao {check['description']}: {e}")
            
            if issues_found == 0:
                print("SUCESSO - Todas as verificacoes de integridade passaram!")
                logger.log_action("DATABASE", "Verificações de integridade OK")
            else:
                print(f"AVISO - {issues_found} problema(s) de integridade encontrado(s)")
                logger.log_security_event("WARNING", f"{issues_found} problemas de integridade encontrados")
            
            return issues_found == 0
            
        except Exception as e:
            logger.log_security_event("ERROR", f"Erro ao executar verificações: {e}")
            print(f"ERRO - Erro ao executar verificacoes: {e}")
            return False
    
    def apply_all_validations(self):
        """Aplicar todas as validações de integridade"""
        print("*** Iniciando aplicacao de validacoes de integridade...")
        
        steps = [
            ("Habilitando foreign keys", self.enable_foreign_keys),
            ("Criando indices", self.create_indexes),
            ("Criando triggers de validacao", self.create_validation_triggers),
            ("Configurando constraints", self.add_constraints),
            ("Criando tabela de auditoria", self.create_audit_table),
            ("Executando verificacoes", self.run_integrity_checks)
        ]
        
        success_count = 0
        for step_name, step_function in steps:
            print(f"\n>>> {step_name}...")
            if step_function():
                success_count += 1
            else:
                print(f"ERRO - Falha em: {step_name}")
        
        print(f"\n*** Resultado: {success_count}/{len(steps)} etapas concluidas com sucesso")
        
        if success_count == len(steps):
            logger.log_action("DATABASE", "Todas as validações de integridade aplicadas com sucesso")
            print("SUCESSO - Todas as validacoes de integridade foram aplicadas!")
            return True
        else:
            logger.log_security_event("WARNING", f"Apenas {success_count}/{len(steps)} validações aplicadas")
            print("AVISO - Algumas validacoes nao foram aplicadas completamente")
            return False

def main():
    """Função principal para executar as validações"""
    print("=" * 60)
    print("🛡️  SISTEMA DE VALIDAÇÕES DE INTEGRIDADE DO BANCO DE DADOS")
    print("=" * 60)
    
    integrity_manager = DatabaseIntegrityManager()
    success = integrity_manager.apply_all_validations()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 VALIDAÇÕES DE INTEGRIDADE APLICADAS COM SUCESSO!")
    else:
        print("⚠️  VALIDAÇÕES APLICADAS COM ALGUMAS LIMITAÇÕES")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()