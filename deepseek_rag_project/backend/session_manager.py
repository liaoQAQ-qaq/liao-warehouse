import sqlite3
import uuid
from datetime import datetime
from config import Config

class SessionManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(Config.DB_PATH) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS sessions 
                          (id TEXT PRIMARY KEY, title TEXT, updated_at TEXT)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS messages 
                          (id TEXT PRIMARY KEY, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)''')

    def create_session(self, title="新会话"):
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with sqlite3.connect(Config.DB_PATH) as conn:
            conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", (session_id, title, now))
        return session_id

    def add_message(self, session_id, role, content):
        msg_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        with sqlite3.connect(Config.DB_PATH) as conn:
            conn.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", 
                        (msg_id, session_id, role, content, now))
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))

    def delete_session(self, session_id):
        with sqlite3.connect(Config.DB_PATH) as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return True

    def get_messages(self, session_id):
        with sqlite3.connect(Config.DB_PATH) as conn:
            cur = conn.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp", (session_id,))
            # 处理旧数据中 content 为 None 的情况
            results = []
            for row in cur.fetchall():
                role = row[0]
                content = row[1] if row[1] is not None else ""
                results.append({"role": role, "content": content})
            return results

    def get_sessions(self):
        with sqlite3.connect(Config.DB_PATH) as conn:
            cur = conn.execute("SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC")
            return [{"id": r[0], "title": r[1], "date": r[2]} for r in cur.fetchall()]

session_manager = SessionManager()