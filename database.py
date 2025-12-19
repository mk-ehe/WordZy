from datetime import datetime
import sqlite3
import bcrypt

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
            total_games_played INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            time_finished TEXT DEFAULT NULL,
            last_played_date TEXT DEFAULT NULL
        )
    ''')

    connection.commit()
    connection.close()

def register(username, password):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    bytes = password.encode('utf-8')
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(bytes, salt)

    hashed_password_str = hashed_password.decode('utf-8')

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password_str))

        connection.commit()
        connection.close()
        return True
    
    except sqlite3.IntegrityError:
        connection.close()
        return False


def login(username, password_input):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        stored_password_hash = result[0]
        
        input_bytes = password_input.encode('utf-8')
        stored_bytes = stored_password_hash.encode('utf-8')

        if bcrypt.checkpw(input_bytes, stored_bytes):
            return True
        else:
            return False
    else:
        return False
    

def finalizeGame(username, won, time_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT wins, streak, total_games_played FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            curr_wins, curr_streak, curr_total = row
            
            new_total = curr_total + 1
            new_wins = curr_wins + 1 if won else curr_wins
            
            if won:
                new_streak = curr_streak + 1
            else:
                new_streak = 0

            cursor.execute("""
                UPDATE users 
                SET wins=?, streak=?, total_games_played=?, time_finished=? 
                WHERE username=?
            """, (new_wins, new_streak, new_total, time_str, username))

            conn.commit()
            return True
    except Exception as e:
        print(e)
        return False
    finally:
        conn.close()


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


def setStreakToZero(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    sql_query = "UPDATE users SET streak = 0 WHERE username = ?"

    try:
        cursor.execute(sql_query, (username,))
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close() 


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


def getTime(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT time_finished FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return "00:00"
    except:
        return "00:00"


def sendWord(username, word_int, word):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    column_name = f"word{word_int}"
    sql_query = f"UPDATE users SET {column_name} = ? WHERE username = ?"

    try:
        cursor.execute(sql_query, (word, username))

        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def sendTime(username, time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    sql_query = f"UPDATE users SET time_finished = ? WHERE username = ?"

    try:
        cursor.execute(sql_query, (time, username))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()


def checkAndResetDaily(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today_date_obj = datetime.now().date()
    today_str = today_date_obj.strftime("%Y-%m-%d")
    
    try:
        cursor.execute("SELECT last_played_date FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        last_played_str = result[0] if result else None

        if last_played_str:
            try:
                last_played_obj = datetime.strptime(last_played_str, "%Y-%m-%d").date()
                
                delta = today_date_obj - last_played_obj
                
                if delta.days > 1:
                    cursor.execute("UPDATE users SET streak = 0 WHERE username = ?", (username,))
                    conn.commit()
            except ValueError:
                pass

        if last_played_str != today_str:
            cursor.execute("""
                UPDATE users 
                SET word1=NULL, word2=NULL, word3=NULL, word4=NULL, word5=NULL, word6=NULL, 
                    time_finished="00:00", last_played_date=?
                WHERE username=?
            """, (today_str, username))
            conn.commit()
            return False
        
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        conn.close()


def getPlayedWords(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    words = []
    
    try:
        cursor.execute("SELECT word1, word2, word3, word4, word5, word6 FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            words = [w for w in row if w is not None]
            
        return words
    except:
        return []
    finally:
        conn.close()


InitDB()
