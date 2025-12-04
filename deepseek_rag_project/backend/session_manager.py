import sqlite3
import uuid
import json
import time
from datetime import datetime
from config import Config

class SessionManager:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # 增加 context 字段，用于存储临时文件内容（如视频分析报告）
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
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO sessions (id, title, created_at, context) VALUES (?, ?, ?, ?)',
            (session_id, title, datetime.now(), "")
        )
        self.conn.commit()
        return session_id

    # 🚀 新增：更新会话的临时上下文 (用于存放视频报告)
    def update_session_context(self, session_id, context_text):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE sessions SET context = ? WHERE id = ?',
            (context_text, session_id)
        )
        self.conn.commit()

    # 🚀 新增：获取会话的临时上下文
    def get_session_context(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT context FROM sessions WHERE id = ?', (session_id,))
        result = cursor.fetchone()
        return result[0] if result else ""

    def add_message(self, session_id, role, content):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)',
            (session_id, role, content, datetime.now())
        )
        self.conn.commit()

    def get_messages(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
        return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

    def get_sessions(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title, created_at FROM sessions ORDER BY created_at DESC')
        return [{"id": row[0], "title": row[1], "created_at": row[2]} for row in cursor.fetchall()]

    def delete_session(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        self.conn.commit()

session_manager = SessionManager()