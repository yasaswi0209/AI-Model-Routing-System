import os, sqlite3
from pathlib import Path

DB_PATH=Path(os.getenv('SMARTROUTE_DB','data/smartroute.db'))
def connect():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row
    c.execute('''CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, question TEXT NOT NULL, answer TEXT NOT NULL, tier TEXT NOT NULL, model TEXT NOT NULL, reason TEXT NOT NULL, mode TEXT NOT NULL, latency_ms REAL NOT NULL, input_tokens INTEGER, output_tokens INTEGER, estimated_cost_usd REAL)''')
    return c

def save(record):
    fields=['question','answer','tier','model','reason','mode','latency_ms','input_tokens','output_tokens','estimated_cost_usd']
    with connect() as c:
        c.execute(f"INSERT INTO requests ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})",[record.get(f) for f in fields])

def history(limit=100):
    with connect() as c: return [dict(r) for r in c.execute('SELECT * FROM requests ORDER BY id DESC LIMIT ?', (limit,))]
