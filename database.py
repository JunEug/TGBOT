import sqlite3

def get_db_connection():
    conn = sqlite3.connect('conversions.db')
    conn.row_factory = sqlite3.Row  
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            currency_from TEXT,
            currency_to TEXT,
            amount REAL,
            result_yahoo REAL,
            result_openapi REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_conversion(user_id, currency_from, currency_to, amount, result_yahoo, result_openapi):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversions (user_id, currency_from, currency_to, amount, result_yahoo, result_openapi)
        VALUES (?, ?, ?, ?, ?, ?)''', (user_id, currency_from, currency_to, amount, result_yahoo, result_openapi))
    conn.commit()
    conn.close()

def get_previous_requests(user_id, period):
    conn = get_db_connection()
    cursor = conn.cursor()

    period = period.strip()
    
    cursor.execute(''' 
        SELECT currency_from, currency_to, amount, result_yahoo, result_openapi, created_at 
        FROM conversions 
        WHERE user_id = ? AND created_at >= datetime('now', ?) 
        ORDER BY created_at DESC
    ''', (user_id, period))

    conversions = cursor.fetchall()
    conn.close()

    return [{
        'currency_from': row[0],
        'currency_to': row[1],
        'amount': row[2],
        'result_yahoo': row[3],
        'result_openapi': row[4],
        'created_at': row[5]
    } for row in conversions]