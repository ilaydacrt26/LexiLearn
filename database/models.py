import sqlite3
from datetime import datetime
from utils.level_calculator import LevelCalculator

class DatabaseManager:
    def __init__(self, db_path='lexilearn.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                current_level TEXT DEFAULT 'A1',
                xp_points INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                test_answers TEXT,
                calculated_level TEXT,
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                score INTEGER,
                xp_gained INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def authenticate_user(self, username, hashed_password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, password, current_level
            FROM users
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def create_user(self, username, hashed_password):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, hashed_password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Kullanıcı adı zaten mevcut
            return False

    def update_user_xp(self, user_id, xp_to_add, activity_type="general"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Mevcut XP yi alma
        cursor.execute("SELECT xp_points FROM users WHERE id = ?", (user_id,))
        current_xp = cursor.fetchone()[0] or 0

        # Yeni XP yi hesaplama
        new_xp = current_xp + xp_to_add

        # XP yi güncelle
        cursor.execute("UPDATE users SET xp_points = ? WHERE id = ?", (new_xp, user_id))

        # Seviye kontrolü
        level_calc = LevelCalculator()
        level_changed, new_level = level_calc.check_level_up(current_xp, new_xp)

        if level_changed:
            cursor.execute("UPDATE users SET current_level = ? WHERE id = ?", (new_level, user_id))

            # Seviye atlama aktivitesi kaydet
            cursor.execute('''
                INSERT INTO user_activities (user_id, activity_type, score, xp_gained, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "level_up", 100, 100, f"Level up to {new_level}"))

        conn.commit()
        conn.close()

        return new_xp, level_changed, new_level if level_changed else None
