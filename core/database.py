import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
import json


class LogDatabase:
    def __init__(self, db_path: str = "captains_log.db"):
        self.db_path = db_path
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        self.init_database()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for classified logs"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stardate TEXT NOT NULL,
                earth_date TEXT NOT NULL,
                log_type TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                classification TEXT DEFAULT 'UNCLASSIFIED',
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                is_encrypted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create log types table for predefined categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#00FF00'
            )
        ''')
        
        # Insert default log types
        default_types = [
            ('MISSION_REPORT', 'Mission status and objectives', '#00FF00'),
            ('PERSONAL_LOG', 'Personal observations and thoughts', '#0080FF'),
            ('SYSTEM_STATUS', 'Ship systems and technical reports', '#FFD700'),
            ('DIPLOMATIC_LOG', 'First contact and diplomatic encounters', '#FF8000'),
            ('SCIENTIFIC_LOG', 'Research findings and discoveries', '#FF00FF'),
            ('SECURITY_ALERT', 'Security concerns and incidents', '#FF0000'),
            ('MEDICAL_LOG', 'Medical reports and crew health', '#00FFFF')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO log_types (name, description, color) 
            VALUES (?, ?, ?)
        ''', default_types)
        
        conn.commit()
        conn.close()
    
    def create_log_entry(self, stardate: str, earth_date: str, log_type: str, 
                        title: str, content: str, priority: int = 1, 
                        classification: str = 'UNCLASSIFIED') -> int:
        """Create a new log entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Encrypt content if classified
        is_encrypted = 0
        if classification in ['CLASSIFIED', 'TOP_SECRET']:
            content = self.cipher.encrypt(content.encode()).decode()
            is_encrypted = 1
        
        cursor.execute('''
            INSERT INTO logs (stardate, earth_date, log_type, priority, 
                            classification, title, content, is_encrypted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (stardate, earth_date, log_type, priority, classification, 
              title, content, is_encrypted))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id or 0
    
    def get_logs(self, limit: int = 50, offset: int = 0, 
                filter_type: Optional[str] = None) -> List[Dict]:
        """Retrieve log entries with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, stardate, earth_date, log_type, priority, classification,
                   title, content, is_encrypted, created_at, modified_at
            FROM logs
        '''
        params = []
        
        if filter_type:
            query += ' WHERE log_type = ?'
            params.append(filter_type)
        
        query += ' ORDER BY stardate DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            log = {
                'id': row[0],
                'stardate': row[1],
                'earth_date': row[2],
                'log_type': row[3],
                'priority': row[4],
                'classification': row[5],
                'title': row[6],
                'content': row[7],
                'is_encrypted': row[8],
                'created_at': row[9],
                'modified_at': row[10]
            }
            
            # Decrypt content if encrypted
            if log['is_encrypted']:
                try:
                    log['content'] = self.cipher.decrypt(log['content'].encode()).decode()
                except:
                    log['content'] = '[CLASSIFIED - DECRYPTION FAILED]'
            
            logs.append(log)
        
        conn.close()
        return logs
    
    def search_logs(self, search_term: str) -> List[Dict]:
        """Search logs by title or content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, stardate, earth_date, log_type, priority, classification,
                   title, content, is_encrypted, created_at, modified_at
            FROM logs
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY stardate DESC
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        logs = []
        
        for row in rows:
            log = {
                'id': row[0],
                'stardate': row[1],
                'earth_date': row[2],
                'log_type': row[3],
                'priority': row[4],
                'classification': row[5],
                'title': row[6],
                'content': row[7],
                'is_encrypted': row[8],
                'created_at': row[9],
                'modified_at': row[10]
            }
            
            # Decrypt content if encrypted
            if log['is_encrypted']:
                try:
                    log['content'] = self.cipher.decrypt(log['content'].encode()).decode()
                except:
                    log['content'] = '[CLASSIFIED - DECRYPTION FAILED]'
            
            logs.append(log)
        
        conn.close()
        return logs
    
    def get_log_types(self) -> List[Dict]:
        """Get all available log types"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, description, color FROM log_types ORDER BY name')
        rows = cursor.fetchall()
        
        types = [{'name': row[0], 'description': row[1], 'color': row[2]} for row in rows]
        
        conn.close()
        return types
    
    def delete_log(self, log_id: int) -> bool:
        """Delete a log entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM logs WHERE id = ?', (log_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success
