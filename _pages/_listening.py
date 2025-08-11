import streamlit as st
from data.listening_data import LISTENING_CONTENT
from database.models import DatabaseManager
import random
import json
import os # Added for file handling
from utils.audio_handler import AudioHandler # Added for Text-to-Speech

def listening_page():
    st.title("🎧 Dinleme Egzersizleri")

    tab1, tab2, tab3 = st.tabs(["🎵 Dinleme", "📝 Test", "📊 Sonuçlar"])

    with tab1:
        listening_exercise()

    with tab2:
        if "current_listening" in st.session_state:
            listening_test()
        else:
            st.info("Önce ses dosyasını dinleyin!")

    with tab3:
        listening_results()

def listening_exercise():
    st.write("### 🎵 Dinleme Egzersizi Seçin")

    user_level = st.session_state.current_level
    available_content = LISTENING_CONTENT.get(user_level, LISTENING_CONTENT["A1"])

    for i, content in enumerate(available_content):
        with st.expander(f" 🎧 {content["title"]}"):
            st.write("**Seviye:**" + user_level)

            # Ses oynatıcı
            if st.button(f"🎵 Dinle", key=f"play_{i}"):
                # Gerçek uygulamada ses dosyası oynatılacak 
                # Şimdilik transkript gösteriyoruz
                # st.audio("data/audio_files/sample.mp3")
                
                # Use Text-to-Speech
                audio_handler = AudioHandler()
                transcript_text = content["transcript"]
                audio_file = audio_handler.text_to_speech(transcript_text)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    # Clean up the temporary file after playback
                    os.unlink(audio_file)

                # Clear previous test state
                if "listening_answers" in st.session_state:
                    del st.session_state.listening_answers
                if "test_completed" in st.session_state:
                    del st.session_state.test_completed
                if "test_score" in st.session_state:
                    del st.session_state.test_score
                if "correct_count" in st.session_state:
                    del st.session_state.correct_count
                if "total_count" in st.session_state:
                    del st.session_state.total_count

                st.session_state.current_listening=content
                st.session_state.listening_index=i
                st.success("Ses dinlendi! Test sekmesine geçebilirsiniz.")


def listening_test():
    st.write(f"### 📝 Test: {st.session_state.current_listening['title']}")

    if 'listening_answers' not in st.session_state:
        st.session_state.listening_answers={}
        st.session_state.test_completed=False

    # Ses dosyasını tekrar dinleme seçeneği
    col1, col2 = st.columns([3,1])

    with col1:
        if not st.session_state.test_completed:
            # Soruları göster
            questions = st.session_state.current_listening["questions"]

            for i, question in enumerate(questions):
                st.write(f"**Soru {i+1}:** {question["question"]}")

                answer = st.radio(
                    "Cevabınızı seçin:",
                    question["options"],
                    key=f"q_{i}"
                )

            if st.button("Testi Tamamla"):
                # Collect answers before evaluating
                questions = st.session_state.current_listening["questions"]
                for i, question in enumerate(questions):
                    # Get the selected option's index (assuming st.radio returns the option string)
                    # We need to find the index of the selected option from the original options list
                    selected_option = st.session_state[f"q_{i}"]
                    st.session_state.listening_answers[i] = question["options"].index(selected_option)
                
                evaluate_listening_test()
        else:
            show_test_results()

def evaluate_listening_test():
    ## Dinleme testini değerlendir
    questions = st.session_state.current_listening["questions"]
    correct_answers=0
    total_questions=len(questions)

    # Cevapları kontrol et
    for i, question in enumerate(questions):
        if st.session_state.listening_answers[i]==question["correct"]:
            correct_answers+=1

    # Skor hesapla
    score = (correct_answers / total_questions) * 100
    st.session_state.test_score = score # Changed from text_score to test_score
    st.session_state.correct_count = correct_answers
    st.session_state.total_count = total_questions
    st.session_state.test_completed = True

    # XP hesapla
    base_xp = 20
    xp_gained = int(base_xp * (score/100))

    # Veritabanına kaydet
    db=DatabaseManager()
    db.add_user_activity(
        st.session_state.user_id,
        "listening",
        score=int(score),
        xp_gained=xp_gained,
        details=json.dumps({
            "title":st.session_state.current_listening["title"],
            "correct_answers":correct_answers,
            "total_questions":total_questions,
            "answers":st.session_state.listening_answers
        })
    )

    # XP güncelle
    new_xp, level_up, new_level = db.update_user_xp(
        st.session_state.user_id,
        xp_gained,
        "listening"
    )

    if level_up:
        st.balloons()
        st.success(f"🎉 Tebrikler! {new_level} seviyesine yükseldiniz!")
        st.session_state.current_level=new_level
    st.rerun()

def show_test_results():
    # Test sonuçlarını göster
    score = st.session_state.test_score
    correct = st.session_state.correct_count
    total = st.session_state.total_count

    st.write("### 📊 Test Sonuçlarınız")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Skor", f"{score:.0f}%")

    with col2:
        st.metric("Doğru Cevap", f"{correct}/{total}")

    with col3:
        if score >= 80:
            performance = "Mükemmel! ⭐"
        elif score >=60:
            performance = "İyi! 👌"
        else:
            performance = "Pratik Gerekli 💪"
        st.metric("Performans", performance)

    # Detaylı sonuçlar
    st.write("### 📝 Cevap Analizi")
    questions = st.session_state.current_listening["questions"]

    for i, question in enumerate(questions):
        user_answer = st.session_state.listening_answers[i]
        correct_answer = question["correct"]

        if user_answer == correct_answer:
            st.success(f"✅ Soru {i+1}: Doğru!")
        else:
            st.error(f"❌ Soru {i+1}: Yanlış")
            st.write(f"Doğru cevap: {question["options"][correct_answer]}")

    # Transkript gösterme seçeneği
    if st.button("🗒️ Metni Göster"):
        st.write("### 🗒️ Dinlediğiniz Metin:")
        st.info(st.session_state.current_listening["transcript"])

    # Yeni test butonu
    if st.button("🎧 Yeni Dinleme Egzersizi"):
        # Dinleme state'ini temizle
        for key in list(st.session_state.keys()):
            if key.startswith("listening_") or key.startswith("current_listening") or key.startswith("test_"):
                del st.session_state[key]
        st.rerun()

def listening_results():
    # Dinleme geçmişi
    st.write("### 📊 Dinleme Geçmişiniz")

    db = DatabaseManager()
    listening_history = db.get_user_activity(
        st.session_state.user_id,
        activity_type="listening",
        limit=10
    )

    if listening_history:
        # İstatistikler
        scores = [activity[2] for activity in listening_history]
        avg_score = sum(scores) / len(scores)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ortalama Skor", f"{avg_score:.1f}%")
        with col2:
            st.metric("Toplam Test", len(listening_history))
        with col3:
            high_scores = len([s for s in scores if s >= 80])
            st.metric("Yüksek Skor", f"{high_scores}/{len(scores)}")

        # Geçmiş testler
        st.write("### 🗒️ Test Geçmişi")
        for activity in listening_history:
            details = json.loads(activity[4])
            with st.expander(f"{details["title"]} - Skor: {activity[2]}%"):
                st.write(f"**Tarih:** {activity[5]}")
                st.write(f"**Doğru Cevap:** {details["correct_answers"]}/{details["total_questions"]}")
                st.write(f"**Kazanılan XP:** {activity[3]}")
    else:
        st.info("Henüz dinleme egzersizi yapmadınız.")

    