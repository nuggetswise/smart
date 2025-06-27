"""
Persistent chat memory with TTL/pruning.
"""
import os
from tinydb import TinyDB, Query
import json
from pathlib import Path

DB_PATH = os.path.expanduser(os.getenv('DB_PATH', '~/.smartdesk_ai/smartdesk.json'))
Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)
db = TinyDB(DB_PATH)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'persona_config.json')
with open(CONFIG_PATH) as f:
    config = json.load(f)
MEMORY_LIMIT = config.get('memory_limit', 100)

class LongTermMemory:
    """
    Persistent chat memory with TTL/pruning, using TinyDB.
    """
    def __init__(self, user_id: str = 'default'):
        self.user_id = user_id
        self.memory_limit = MEMORY_LIMIT
        self.table = db.table('chat')
    
    def add_message(self, role: str, content: str):
        history = self.load_history()
        history.append({'role': role, 'content': content})
        if len(history) > self.memory_limit:
            history = history[-self.memory_limit:]
        self.table.upsert({'user_id': self.user_id, 'history': history}, Query().user_id == self.user_id)
    
    def get_recent_messages(self, n: int = 10):
        history = self.load_history()
        return history[-n:] if n else history
    
    def get_all_messages(self):
        return self.load_history()
    
    def clear_memory(self):
        self.table.upsert({'user_id': self.user_id, 'history': []}, Query().user_id == self.user_id)
    
    def load_history(self):
        res = self.table.get(Query().user_id == self.user_id)
        return res['history'] if res else []

def save_message(user_id, message):
    history = load_history(user_id)
    history.append(message)
    if len(history) > MEMORY_LIMIT:
        history = history[-MEMORY_LIMIT:]
    db.table('chat').upsert({'user_id': user_id, 'history': history}, Query().user_id == user_id)

def load_history(user_id):
    res = db.table('chat').get(Query().user_id == user_id)
    return res['history'] if res else []

def prune_history(user_id, limit=None):
    limit = limit or MEMORY_LIMIT
    history = load_history(user_id)
    if len(history) > limit:
        history = history[-limit:]
        db.table('chat').upsert({'user_id': user_id, 'history': history}, Query().user_id == user_id) 