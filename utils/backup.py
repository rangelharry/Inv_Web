#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventário Web - Sistema de Backup
Backup automático e manual do banco de dados
"""

import os
import shutil
import gzip
from datetime import datetime, timedelta
from typing import List, Dict, Any
import streamlit as st
from database.connection import get_database


class BackupManager:
    """Gerenciador de backup do banco de dados"""
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Inicializar gerenciador de backup
        
        Args:
            backup_dir: Diretório para armazenar backups
        """
        self.backup_dir = backup_dir
        self.db_path = "database/inventario.db"
        
        # Criar diretório de backup se não existir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, compress: bool = True) -> tuple[bool, str]:
        """
        Criar backup do banco de dados
        
        Args:
            compress: Se True, comprime o backup com gzip
            
        Returns:
            Tupla (sucesso, mensagem_ou_caminho)
        """
        try:
            if not os.path.exists(self.db_path):
                return False, "Banco de dados não encontrado"
            
            # Nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"inventario_backup_{timestamp}.db"
            
            if compress:
                backup_filename += ".gz"
            
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Criar backup
            if compress:
                with open(self.db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(self.db_path, backup_path)
            
            # Registrar backup na auditoria
            self._log_backup(backup_path, os.path.getsize(backup_path))
            
            return True, backup_path
            
        except Exception as e:
            return False, f"Erro ao criar backup: {str(e)}"
    
    def restore_backup(self, backup_path: str) -> tuple[bool, str]:
        """
        Restaurar backup do banco de dados
        
        Args:
            backup_path: Caminho para o arquivo de backup
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "Arquivo de backup não encontrado"
            
            # Criar backup do banco atual antes de restaurar
            current_backup = f"{self.db_path}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.db_path, current_backup)
            
            # Restaurar backup
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(self.db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            # Registrar restauração na auditoria
            self._log_restore(backup_path)
            
            return True, f"Backup restaurado com sucesso. Backup anterior salvo em: {current_backup}"
            
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}"
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Listar todos os backups disponíveis
        
        Returns:
            Lista de dicionários com informações dos backups
        """
        backups = []
        
        try:
            if not os.path.exists(self.backup_dir):
                return backups
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("inventario_backup_") and (filename.endswith(".db") or filename.endswith(".db.gz")):
                    filepath = os.path.join(self.backup_dir, filename)
                    stat = os.stat(filepath)
                    
                    # Extrair timestamp do nome do arquivo
                    try:
                        timestamp_str = filename.replace("inventario_backup_", "").replace(".db.gz", "").replace(".db", "")
                        backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    except:
                        backup_date = datetime.fromtimestamp(stat.st_mtime)
                    
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'date': backup_date,
                        'compressed': filename.endswith('.gz')
                    })
            
            # Ordenar por data (mais recente primeiro)
            backups.sort(key=lambda x: x['date'], reverse=True)
            
        except Exception as e:
            st.error(f"Erro ao listar backups: {e}")
        
        return backups
    
    def clean_old_backups(self, keep_days: int = 30, keep_count: int = 10) -> tuple[int, List[str]]:
        """
        Limpar backups antigos
        
        Args:
            keep_days: Manter backups dos últimos N dias
            keep_count: Manter pelo menos N backups mais recentes
            
        Returns:
            Tupla (quantidade_removida, lista_arquivos_removidos)
        """
        removed_count = 0
        removed_files = []
        
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return 0, []
            
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            # Manter pelo menos keep_count backups mais recentes
            backups_to_check = backups[keep_count:]
            
            for backup in backups_to_check:
                if backup['date'] < cutoff_date:
                    try:
                        os.remove(backup['filepath'])
                        removed_files.append(backup['filename'])
                        removed_count += 1
                    except Exception as e:
                        st.warning(f"Erro ao remover backup {backup['filename']}: {e}")
        
        except Exception as e:
            st.error(f"Erro ao limpar backups: {e}")
        
        return removed_count, removed_files
    
    def auto_backup(self) -> bool:
        """
        Executar backup automático se necessário
        
        Returns:
            True se backup foi criado, False caso contrário
        """
        try:
            # Verificar se já existe backup de hoje
            today = datetime.now().strftime("%Y%m%d")
            backups = self.list_backups()
            
            # Verificar se já há backup de hoje
            for backup in backups:
                if backup['date'].strftime("%Y%m%d") == today:
                    return False  # Já existe backup de hoje
            
            # Criar backup automático
            success, result = self.create_backup(compress=True)
            
            if success:
                # Limpar backups antigos
                self.clean_old_backups(keep_days=30, keep_count=10)
                return True
            
        except Exception as e:
            st.error(f"Erro no backup automático: {e}")
        
        return False
    
    def _log_backup(self, backup_path: str, size: int):
        """Registrar backup na auditoria"""
        try:
            db = get_database()
            db.execute_update("""
                INSERT INTO auditoria (usuario, acao, detalhes, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                "sistema",
                "Backup criado",
                f"Arquivo: {os.path.basename(backup_path)}, Tamanho: {size} bytes",
                datetime.now().isoformat()
            ))
        except Exception:
            pass  # Não falhar se não conseguir registrar auditoria
    
    def _log_restore(self, backup_path: str):
        """Registrar restauração na auditoria"""
        try:
            db = get_database()
            db.execute_update("""
                INSERT INTO auditoria (usuario, acao, detalhes, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                "sistema",
                "Backup restaurado",
                f"Arquivo: {os.path.basename(backup_path)}",
                datetime.now().isoformat()
            ))
        except Exception:
            pass  # Não falhar se não conseguir registrar auditoria
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas dos backups
        
        Returns:
            Dicionário com estatísticas
        """
        backups = self.list_backups()
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size': 0,
                'last_backup': None,
                'oldest_backup': None
            }
        
        total_size = sum(backup['size'] for backup in backups)
        
        return {
            'total_backups': len(backups),
            'total_size': total_size,
            'last_backup': backups[0]['date'] if backups else None,
            'oldest_backup': backups[-1]['date'] if backups else None
        }


# Instância global para cache
@st.cache_resource
def get_backup_manager() -> BackupManager:
    """
    Obter instância do gerenciador de backup (cached)
    
    Returns:
        Instância de BackupManager
    """
    return BackupManager()