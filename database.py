import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'interviews.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            overall_score INTEGER,
            transcript TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_interview(data):
    conn = get_connection()
    cur = conn.cursor()
    transcript_json = json.dumps(data.get('transcript', []))
    
    cur.execute('''
        INSERT INTO interviews (name, role, overall_score, transcript)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['role'], data['overall_score'], transcript_json))
    
    interview_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return interview_id

def get_interview(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM interviews WHERE id = ?', (id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_all_interviews():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM interviews ORDER BY timestamp DESC')
    rows = cur.fetchall()
    conn.close()
    return rows