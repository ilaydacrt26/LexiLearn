import streamlit as st
from data.vocabulary_data import VOCABULARY_BY_LEVEL
from utils.level_calculator import LevelCalculator
from utils.llm_handler import LLMHandler
from database.models import DatabaseManager
import random
import json
from datetime import datetime, date

def daily_tasks_page():
    st.title("📝 Günlük Kelime Görevleri")

    # İlk kurulum
    if 'daily_words' not in st.session_state:
        st.session_state.daily_words = get_daily_words()
        st.session_state.completed_tasks = []
        st.session_state.llm_handler = LLMHandler()

    # Günlük streak kontrolü
    show_daily_streak()

    # Ana içerik
    tab1, tab2, tab3 = st.tabs(["🎯 Bugünkü Görevler", "📚 Kelime Defteri", "🏆 Başarılar"])

    with tab1:
        daily_words_tasks()

    with tab2:
        vocabulary_notebook()

    with tab3:
        achievements()

def show_daily_streak():
    # Günlük seri gönderimi

    col1, col2, col3, col4 = st.columns(4)

    db = DatabaseManager()
    streak_data = db.get_user_streak(st.session_state.user_id)

    with col1:
        st.metric("🔥 Günlük Seri", f"{streak_data.get('current_streak', 0)} gün")

    with col2:
        st.metric("📈 En Uzun Seri", f"{streak_data.get('longest_streak', 0)} gün")

    with col3:
        today_completed = db.check_today_tasks_completed(st.session_state.user_id)
        st.metric("✅ Bugün", "Tamamlandı" if today_completed else "Devam Ediyor")

    with col4:
        st.metric("🎯 Haftalık Hedef", "5/7 gün")

def get_daily_words():
    # Günlük kelimeleri seç
    user_level = st.session_state.current_level
    level_words = VOCABULARY_BY_LEVEL.get(user_level, VOCABULARY_BY_LEVEL["A1"])

    # Tüm kategorilerden karışık 5 kelime seç
    all_words = []
    for category_words in level_words.values():
        all_words.extend(category_words)

    return random.sample(all_words, min(5, len(all_words)))

def daily_word_tasks():
    st.write("### 🎯 Bugünün Kelimeleri")

    for i, word_data in enumerate(st.session_state.daily_words):
        with st.expander(f"Kelime {i + 1}: **{word_data['word']}** ({word_data['pronunciation']})"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Anlam:** {word_data['meaning']}")
                st.write(f"**Örnek:** {word_data['example']}")

                # Kelime ile cümle kurma görevi
                st.write("### 📝 Görev: Bu kelimeyle bir cümle kurun")
                user_sentence = st.text_area(
                    f"'{word_data['word']}' kelimesini kullanarak cümle yazın.",
                    key=f'sentence_{i}',
                    height=100
                )

                if st.button(f"Cümleyi Kontrol Et", key=f"check_{i}"):
                    if user_sentence.strip():
                        check_sentence_task(word_data, user_sentence, i)
                    else:
                        st.warning("Lütfen bir cümle yazın!")

            with col2:
                st.write("### 🎯 Puan")

                if f"task_{i}" in st.session_state.completed_tasks:
                    task_result = next(t for t in st.session_state.completed_tasks if t["task_id"] == f"task_{i}")
                    st.success(f"Tamamlandı! 🎉")
                    st.write(f"Skor: {task_result['score']}/10")
                    st.write(f"XP: +{task_result['xp']}")
                else:
                    st.info("Görevi tamamlayın")

def check_sentence_task(word_data, user_sentence, task_index):
    # Cümle görevini kontrol et

    # LLM ile cümleyi değerlendir
    prompt = f"""
    Evaluate this English sentence created by a {st.session_state.current_level} level student:

    Target word: "{word_data['word']}"
    Student's sentence: "{user_sentence}"

    Check:
    1. Does the sentence use the target word correctly?
    2. Is the grammar correct for this level?
    3. Is the meaning clear?
    4. Rate the sentence (1 - 10)
    5. Provide constructive feedback

    Format as JSON with keys: uses_word, grammar_correct, meaning_clear, score, feedback
    """

    with st.spinner("Cümleniz değerlendiriliyor..."):
        evaluation = st.session_state.llm_handler.model.generate_content(prompt)

        try:
            eval_data = json.loads(evaluation.text)
            score = eval_data.get("score", 5)

            # Sonuçları göster
            if eval_data.get('uses_word', False) and eval_data.get('grammar_correct', False):
                st.success("Harika! Cümleniz doğru! 🎉")
            else:
                st.warning("Cümlenizde bazı sorunlar var:")
            
            st.write("**Geri Bildirim:**", eval_data.get("feedback", ""))
            st.write(f"**Skor:** {score}/10")

            # XP hesapla
            level_calc = LevelCalculator()
            base_xp = level_calc.get_xp_for_activity("sentence_creation")
            bonus = score / 10
            final_xp = int(base_xp * bonus)

            # Veritabanına kaydet
            db = DatabaseManager()
            db.add_user_activity(
                st.session_state.user_id,
                "word_task",
                score=score,
                xp_gained=final_xp,
                details=json.dumps({
                    "word": word_data["word"],
                    "sentence": user_sentence,
                    "evaluation": eval_data
                })
            )

            # XP güncelle
            new_xp, level_up, new_level = db.update_user_xp(
                st.session_state.user_id,
                final_xp,
                "word_task"
            )

            # Görev tamamlandı işaretle
            task_result = {
                "task_id":f"task_{task_index}",
                "score":score,
                "xp":final_xp
            }
            st.session_state.completed_tasks.append(task_result)

            if level_up:
                st.ballons()
                st.success(f"🎉 Tebrikler! {new_level} seviyesine yükseldiniz!")
                st.session_state.current_level = new_level
            
            st.write(f"**Kazanılan XP:** +{final_xp}")

        except:
            st.error("Değerlendirme sonuçları işlenirken hata oluştu.")

def vocabulary_notebook():
    # Öğrenilen kelimeler defteri
    st.write("### 📚 Kelime Defterim")

    db = DatabaseManager()

    learned_words = db.get_user_learned_words(st.session_state.user_id)

    if learned_words:
        # Filtreleme seçenekleri
        col1, col2 = st.columns(2)
        with col1:
            filter_level = st.selectbox("Seviye:", ["Tümü", "A1", "A2", "B1", "B2"])
        with col2:
            sort_by = st.selectbox("Sırala:", ["Tarih", "Skor", "Kelime"])

        # Kelimeleri listele
        for word_entry in learned_words:
            with st.expander(f"{word_entry['word']} = Skor: {word_entry['score']/10}"):
                st.write(f"**Oluşturduğunuz cümle:** {word_entry["sentence"]}")
                st.write(f"**Tarih:** {word_entry["date"]}")
                st.write(f"**Kazanılan XP:** {word_entry["xp"]}")

                # Tekrar çalış butonu
                if st.button(f"Tekrar Çalış", key=f"review_{word_entry["id"]}"):
                    st.info("Bu kelimeyi tekrar çalışmak için günlük görevlere eklendi!")
    else:
        st.info("Henüz kelime öğrenmediniz. Günlük görevleri tamamlayın!")

def achievements():
    # Başarılar ve rozetler
    st.write("### 🏆 Başarılarınız")

    db = DatabaseManager()
    user_stats = db.get_user_statistics(st.session_state.user_id)

    # Rozet sistemi
    badges = [
        {"name":"İlk Adım","desc":"İlk kelime görevini tamamla", "icon":"🎯", "condition":user_stats.get("completed_tasks", 0) >= 1},
        {"name":"Sebatkar","desc":"7 gün üst üste görev tamamla.", "icon":"🔥", "condition":user_stats.get("max_streak", 0) >= 7 },
        {"name":"Kelime Uzmanı","desc":"100 kelime öğren", "icon":"📚", "condition":user_stats.get("learned_words", 0) >= 100},
        {"name":"Mükemmelliyetçi","desc":"10 görevi 10/10 skorla tamamla.", "icon":"⭐", "condition":user_stats.get("perfect_scores", 0) >= 10},
        {"name":"Seviye Atlayıcı","desc":"Bir seviye atla", "icon":"🚀", "condition":user_stats.get("level_ups", 0) >= 1}
    ]

    col1, col2, col3 = st.columns(3)

    for i, badge in enumerate(badges):
        with [col1, col2, col3][i%3]:
            if badge["condition"]:
                st.success(f"{badge["icon"]} **{badge["name"]}**")
                st.write(badge["desc"])
            else:
                st.info(f"🔐 **{badge['name']}**")
                st.write(badge["desc"])
