import sqlite3
import json
from datetime import datetime, date, timedelta
from utils.level_calculator import LevelCalculator

class DatabaseManager:
    def __init__(self, db_path='lexilearn.db'):
        self.db_path = db_path
        self.init_database()

    def connect(self):
        """Return a new SQLite connection to the configured database path."""
        return sqlite3.connect(self.db_path)

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
            return False

    def update_user_xp(self, user_id, xp_to_add, activity_type="general"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT xp_points FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        current_xp = (row[0] if row and row[0] is not None else 0)
        new_xp = current_xp + xp_to_add

        cursor.execute("UPDATE users SET xp_points = ? WHERE id = ?", (new_xp, user_id))

        level_calc = LevelCalculator()
        level_changed, new_level = level_calc.check_level_up(current_xp, new_xp)

        if level_changed:
            cursor.execute("UPDATE users SET current_level = ? WHERE id = ?", (new_level, user_id))
            cursor.execute('''
                INSERT INTO user_activities (user_id, activity_type, score, xp_gained, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "level_up", 100, 100, f"Level up to {new_level}"))

        conn.commit()
        conn.close()

        return new_xp, level_changed, (new_level if level_changed else None)

    # === EKLENEN FONKSİYONLAR ===

    def add_user_activity(self, user_id, activity_type, score, xp_gained, details):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_activities (user_id, activity_type, score, xp_gained, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, activity_type, score, xp_gained, details))
        conn.commit()
        conn.close()

    def get_user_learned_words(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, details, score, xp_gained, created_at
            FROM user_activities
            WHERE user_id = ? AND activity_type = 'word_task'
            ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()

        learned_words = []
        for row in rows:
            try:
                details = json.loads(row[1])
                learned_words.append({
                    "id": row[0],
                    "word": details.get("word", ""),
                    "sentence": details.get("sentence", ""),
                    "score": row[2],
                    "xp": row[3],
                    "date": row[4]
                })
            except:
                continue
        return learned_words

    def get_user_statistics(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND activity_type = "word_task"', (user_id,))
        completed_tasks = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND activity_type = "level_up"', (user_id,))
        level_ups = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND activity_type = "word_task" AND score = 10', (user_id,))
        perfect_scores = cursor.fetchone()[0]

        learned_words = completed_tasks  # her word_task = 1 kelime öğrenildi varsayımı
        streak_data = self.get_user_streak(user_id)

        conn.close()

        return {
            "completed_tasks": completed_tasks,
            "learned_words": learned_words,
            "perfect_scores": perfect_scores,
            "level_ups": level_ups,
            "max_streak": streak_data.get("longest_streak", 0)
        }

    def get_user_streak(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE(created_at)
            FROM user_activities
            WHERE user_id = ? AND activity_type = 'word_task'
            ORDER BY DATE(created_at) DESC
        ''', (user_id,))
        dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in cursor.fetchall()]
        conn.close()

        if not dates:
            return {"current_streak": 0, "longest_streak": 0}

        longest_streak = 1
        current_streak = 1
        today = date.today()

        if dates[0] == today:
            for i in range(1, len(dates)):
                if dates[i] == dates[i-1] - timedelta(days=1):
                    current_streak += 1
                    longest_streak = max(longest_streak, current_streak)
                else:
                    break
        else:
            current_streak = 0

        # longest streak hesaplama
        temp_streak = 1
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] - timedelta(days=1):
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

        return {"current_streak": current_streak, "longest_streak": longest_streak}

    def check_today_tasks_completed(self, user_id):
        today_str = date.today().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM user_activities
            WHERE user_id = ? AND activity_type = 'word_task' AND DATE(created_at) = ?
        ''', (user_id, today_str))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def save_level_test_result(self, user_id, answers, calculated_level, score):
        """
        Seviye test sonucunu veritabanına kaydeder.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO level_tests (user_id, test_answers, calculated_level, score)
            VALUES (?, ?, ?, ?)
        ''', (user_id, json.dumps(answers), calculated_level, score))
        conn.commit()
        conn.close()

    def update_user_level(self, user_id, new_level):
        """
        Kullanıcının mevcut seviyesini günceller.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET current_level = ?
            WHERE id = ?
        ''', (new_level, user_id))
        conn.commit()
        conn.close()

    def get_user_activity(self, user_id, activity_type=None, limit=10):
        """
        Kullanıcının yaptığı aktiviteleri veritabanından çeker.
        
        :param user_id: Kullanıcının ID'si
        :param activity_type: (Opsiyonel) Sadece belirli bir aktivite türünü filtrelemek için ("listening", "reading", vb.)
        :param limit: Kaç adet kayıt döndürüleceği
        :return: [(id, user_id, score, xp_gained, details, created_at), ...]
        """
        conn = self.connect()
        cursor = conn.cursor()

        if activity_type:
            cursor.execute("""
                SELECT id, user_id, score, xp_gained, details, created_at
                FROM user_activities
                WHERE user_id = ? AND activity_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, activity_type, limit))
        else:
            cursor.execute("""
                SELECT id, user_id, score, xp_gained, details, created_at
                FROM user_activities
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))

        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_comprehensive_user_stats(self, user_id):
        """
        Kullanıcının genel istatistiklerini döndürür.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Toplam XP
        cursor.execute("SELECT xp_points FROM users WHERE id = ?", (user_id,))
        total_xp = cursor.fetchone()[0] or 0

        # Aktivite sayısı
        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE user_id = ?", (user_id,))
        total_activities = cursor.fetchone()[0]

        # Haftalık aktivite
        cursor.execute("""
            SELECT COUNT(*) FROM user_activities
            WHERE user_id = ? AND DATE(created_at) >= DATE('now', '-7 day')
        """, (user_id,))
        week_activities = cursor.fetchone()[0]

        # Ortalama skor
        cursor.execute("SELECT AVG(score) FROM user_activities WHERE user_id = ?", (user_id,))
        avg_score = cursor.fetchone()[0] or 0

        # Günlük streak
        streak_data = self.get_user_streak(user_id)

        # Diğer detaylar
        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND activity_type = 'word_task'", (user_id,))
        learned_words = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND score = 10", (user_id,))
        perfect_scores = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND activity_type = 'level_up'", (user_id,))
        level_ups = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND activity_type = 'pronunciation'", (user_id,))
        pronunciation_exercises = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_activities WHERE user_id = ? AND activity_type = 'listening'", (user_id,))
        listening_test = cursor.fetchone()[0]

        conn.close()

        return {
            "total_xp": total_xp,
            "total_activities": total_activities,
            "week_activities": week_activities,
            "average_score": avg_score,
            "current_streak": streak_data.get("current_streak", 0),
            "longest_streak": streak_data.get("longest_streak", 0),
            "learned_words": learned_words,
            "perfect_scores": perfect_scores,
            "level_ups": level_ups,
            "pronunciation_exercises": pronunciation_exercises,
            "listening_test": listening_test,
            "chat_messages": 0  # Eğer chat log tablon yoksa 0 bırakılır
        }

    def get_weekly_activity(self, user_id):
        """
        Son 7 günün günlük aktivite sayısını ve kazanılan XP'yi döndürür.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DATE(created_at), COUNT(*), SUM(xp_gained)
            FROM user_activities
            WHERE user_id = ? AND DATE(created_at) >= DATE('now', '-7 day')
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """, (user_id,))
        data = cursor.fetchall()
        conn.close()
        return data

    def get_module_performance(self, user_id):
        """
        Modül bazında ortalama skor ve aktivite sayısını döndürür.
        details kolonundan 'module' alanını bekler.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT details, AVG(score), COUNT(*)
            FROM user_activities
            WHERE user_id = ?
            GROUP BY details
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        module_stats = {}
        for details, avg_score, count in rows:
            try:
                det_json = json.loads(details)
                module_name = det_json.get("module", "Bilinmiyor")
            except:
                module_name = "Bilinmiyor"

            module_stats[module_name] = {
                "avg_score": round(avg_score or 0, 2),
                "count": count
            }
        return module_stats

    def get_score_progress(self, user_id, days=None):
        """
        Belirtilen süre boyunca skor gelişimi.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT DATE(created_at), score, activity_type
            FROM user_activities
            WHERE user_id = ?
        """
        params = [user_id]

        if days:
            query += " AND DATE(created_at) >= DATE('now', ?)"
            params.append(f"-{days} day")

        query += " ORDER BY DATE(created_at)"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_xp_progress(self, user_id, days=None):
        """
        Belirtilen süre boyunca kümülatif XP gelişimi.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT DATE(created_at), SUM(xp_gained)
            FROM user_activities
            WHERE user_id = ?
        """
        params = [user_id]
        if days:
            query += " AND DATE(created_at) >= DATE('now', ?)"
            params.append(f"-{days} day")
        query += " GROUP BY DATE(created_at) ORDER BY DATE(created_at)"

        cursor.execute(query, tuple(params))
        daily_xp = cursor.fetchall()
        conn.close()

        cumulative = 0
        result = []
        for date_str, xp in daily_xp:
            cumulative += xp or 0
            result.append((date_str, cumulative))
        return result

    def get_vocabulary_progress(self, user_id, days=None):
        """
        Belirtilen süre boyunca öğrenilen kelimeler.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT DATE(created_at), COUNT(*)
            FROM user_activities
            WHERE user_id = ? AND activity_type = 'word_task'
        """
        params = [user_id]
        if days:
            query += " AND DATE(created_at) >= DATE('now', ?)"
            params.append(f"-{days} day")
        query += " GROUP BY DATE(created_at) ORDER BY DATE(created_at)"

        cursor.execute(query, tuple(params))
        daily_words = cursor.fetchall()
        conn.close()

        cumulative = 0
        result = []
        for date_str, count in daily_words:
            cumulative += count or 0
            result.append((date_str, count, cumulative))
        return result

    def get_pronunciation_progress(self, user_id):
        """
        Kullanıcının son 30 gündeki telaffuz skorlarının günlük ortalamasını döndürür.
        :param user_id: Kullanıcı ID'si
        :return: [(tarih, ortalama_skor), ...]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
                SELECT DATE(created_at) as date, AVG(score) as avg_score
                FROM user_activities
                WHERE user_id = ?
                  AND activity_type = 'pronunciation'
                  AND DATE(created_at) >= DATE('now', '-30 day')
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_user_data(self, user_id):
        """
        Kullanıcının temel bilgilerini döndürür.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, current_level, xp_points, created_at
            FROM users
            WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "username": row[0],
                "current_level": row[1],
                "xp_points": row[2],
                "created_at": row[3],
                "login_count": 0,  # giriş kayıt tablon yoksa sıfır
                "last_login": "Bilinmiyor"
            }
        return {}

    def get_all_user_activities(self, user_id):
        """
        Kullanıcının tüm aktivitelerini döndürür.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT activity_type, score, xp_gained, details, created_at
            FROM user_activities
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def reset_user_progress(self, user_id):
        """
        Kullanıcının tüm aktivitelerini siler ve XP ile seviyesini sıfırlar.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_activities WHERE user_id = ?", (user_id,))
        cursor.execute("""
            UPDATE users
            SET xp_points = 0, current_level = 'A1'
            WHERE id = ?
        """, (user_id,))

        conn.commit()
        conn.close()

 
