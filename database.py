from datetime import datetime
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
            wins INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            total_games_played INTEGER DEFAULT 0,
            time_finished TEXT DEFAULT NULL,
            last_played_date TEXT DEFAULT NULL
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


def getUserWins(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT wins FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return 0
    except:
        return 0
    

def getUserStreak(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT streak FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return 0
    except:
        return 0
    

def getTotalGamesPlayed(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT total_games_played FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return 0
    except:
        return 0


InitDB()