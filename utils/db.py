import os
from tinydb import TinyDB, Query
from pathlib import Path

DB_PATH = os.path.expanduser(os.getenv('DB_PATH', '~/.smartdesk_ai/smartdesk.json'))
Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)
db = TinyDB(DB_PATH)

def save_action_items(username, items):
    db.table('action_items').upsert({'username': username, 'items': items}, Query().username == username)

def load_action_items(username):
    res = db.table('action_items').get(Query().username == username)
    return res['items'] if res else []

def save_chat(username, chat):
    db.table('chat').upsert({'username': username, 'chat': chat}, Query().username == username)

def load_chat(username):
    res = db.table('chat').get(Query().username == username)
    return res['chat'] if res else []

def save_preferences(username, prefs):
    db.table('prefs').upsert({'username': username, 'prefs': prefs}, Query().username == username)

def load_preferences(username):
    res = db.table('prefs').get(Query().username == username)
    return res['prefs'] if res else {} 