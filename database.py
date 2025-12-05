import sqlite3

DB_NAME = "users.db"

def InitDB():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            word1 TEXT DEFAULT NULL,
            word2 TEXT DEFAULT NULL,
            word3 TEXT DEFAULT NULL,
            word4 TEXT DEFAULT NULL,
            word5 TEXT DEFAULT NULL,
            word6 TEXT DEFAULT NULL,
            wins INTEGER DEFAULT 0
        )
    ''')

    connection.commit()
    connection.close()

def register(username, password):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

        connection.commit()
        connection.close()
        return True
    
    except sqlite3.IntegrityError:
        connection.close()
        return False


def login(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    
    conn.close()
    
    return result is not None


InitDB()