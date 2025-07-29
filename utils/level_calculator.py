class LevelCalculator:
    def __init__(self):
        self.level_thresholds = {
            "A1": 0,
            "A2": 500,
            "B1": 1500,
            "B2": 3000,
            "C1": 5000,
            "C2": 8000
        }

        self.activitiy_xp = {
            "word_task":20,
            "sentence_creation": 15,
            "chat_message":10,
            "pronunciation": 25,
            "scenario": 30,
            "listening": 20,
            "daily_streak": 50
        }

    def calculate_level_from_xp(self, current_xp, current_level):
        # Bir sonraki seviye için gereken XP
        levels = list(self.level_thresholds.keys())
        current_index = levels.index(current_level)

        if current_index < len(levels) - 1:
            next_level = levels[current_index + 1]
            return self.level_thresholds[next_level] - current_xp
        return 0
    
    def get_xp_for_activity(self, activity_type, bonus_multiplier=1.0):
        # Aktivite için XP hesapla
        base_xp = self.activitiy_xp.get(activity_type, 10)
        return int(base_xp * bonus_multiplier)
    
    def check_level_up(self, old_xp, new_xp):
        # Seviye atlama kontrolü
        old_level = self.calculate_level_from_xp(old_xp)
        new_level = self.calculate_level_from_xp(new_xp)
        return old_level != new_level, new_level
    
