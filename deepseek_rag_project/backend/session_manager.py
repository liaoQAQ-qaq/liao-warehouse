import sqlite3
import uuid
import json
import time
import threading
from datetime import datetime
from config import Config

class SessionManager:
    def __init__(self):
        # check_same_thread=False 允许在不同线程使用连接，但需要应用层加锁
        self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        self.lock = threading.Lock() # 🔒 核心优化：添加线程锁
        self.create_tables()

    def create_tables(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TIMESTAMP,
                    context TEXT  
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            self.conn.commit()

    def create_session(self, title="新会话"):
        session_id = str(uuid.uuid4())
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO sessions (id, title, created_at, context) VALUES (?, ?, ?, ?)',
                (session_id, title, datetime.now(), "")
            )
            self.conn.commit()
        return session_id

    def update_session_context(self, session_id, context_text):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE sessions SET context = ? WHERE id = ?',
                (context_text, session_id)
            )
            self.conn.commit()

    def get_session_context(self, session_id):
        # 读操作通常不需要加锁，但为了保险起见避免争用，也可以加
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT context FROM sessions WHERE id = ?', (session_id,))
            result = cursor.fetchone()
        return result[0] if result else ""

    def add_message(self, session_id, role, content):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)',
                (session_id, role, content, datetime.now())
            )
            self.conn.commit()

    def get_messages(self, session_id):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
            rows = cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]

    def get_sessions(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, title, created_at FROM sessions ORDER BY created_at DESC')
            rows = cursor.fetchall()
        return [{"id": row[0], "title": row[1], "created_at": row[2]} for row in rows]

    def delete_session(self, session_id):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
            self.conn.commit()

session_manager = SessionManager()