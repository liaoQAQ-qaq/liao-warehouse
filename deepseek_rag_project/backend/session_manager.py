import sqlite3
import uuid
import os
from datetime import datetime

# 数据库存储路径
DB_PATH = "../data/sessions.db"

class SessionManager:
    def __init__(self):
        # 确保目录存在
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化 SQLite 表结构"""
        with sqlite3.connect(DB_PATH) as conn:
            # 会话表
            conn.execute('''CREATE TABLE IF NOT EXISTS sessions 
                          (id TEXT PRIMARY KEY, title TEXT, updated_at TEXT)''')
            # 消息表
            conn.execute('''CREATE TABLE IF NOT EXISTS messages 
                          (id TEXT PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)''')

    def create_session(self, title="新会话"):
        """创建新会话"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", (session_id, title, now))
        return session_id

    def add_message(self, session_id, role, content):
        """添加消息"""
        msg_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", 
                        (msg_id, session_id, role, content, now))
            # 更新会话时间
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
    def delete_session(self, session_id):
        with sqlite3.connect(DB_PATH) as conn:
            # 级联删除：删除会话记录 + 该会话下的所有消息
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return True
    def get_messages(self, session_id):
        """获取某会话的所有消息"""
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp", (session_id,))
            return [{"role": row[0], "content": row[1]} for row in cur.fetchall()]

    def get_sessions(self):
        """获取所有会话列表"""
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute("SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC")
            return [{"id": r[0], "title": r[1], "date": r[2]} for r in cur.fetchall()]

# 全局实例
session_manager = SessionManager()