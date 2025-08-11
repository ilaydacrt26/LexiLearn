import streamlit as st
from utils.llm_handler import LLMHandler
from data.level_test_questions import LEVEL_TEST_QUESTIONS

# Level test sayfası
def level_test_page():
    st.title("📚 İngilizce Seviye Testi")

    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.total_score = 0

    if not st.session_state.test_started:
        st.write("Bu test, İngilizce seviyenizi belirlemek için hazırlanmıştır. Lütfen her soruyu dikkatlice okuyun ve en uygun cevabı seçin.")
        if st.button("Testi Başlat"):
            st.session_state.test_started = True
            st.rerun()
    else:
        run_level_test()

# Level test fonksiyonu
def run_level_test():
    all_questions = []
    for level, questions in LEVEL_TEST_QUESTIONS.items():
        all_questions.extend(questions)
    
    if st.session_state.current_question < len(all_questions):
        question = all_questions[st.session_state.current_question]

        st.write(f"Soru {st.session_state.current_question + 1}/{len(all_questions)}")
        st.write(question['question'])

        answer = st.radio("Cevabınızı seçin:", question['options'], key=f"q_{st.session_state.current_question}")

        if st.button("Sonraki Soru"):
            if question["options"].index(answer) == question['correct']:
                st.session_state.total_score += question['points']

            st.session_state.answers.append(answer)
            st.session_state.current_question += 1
            st.rerun()
    else:
        calculate_level()

# Seviye hesaplama fonksiyonu
def calculate_level():
    total_possible = sum(q['points'] for questions in LEVEL_TEST_QUESTIONS.values() for q in questions)
    percentage = (st.session_state.total_score / total_possible) * 100

    if percentage < 25:
        level = "A1"
    elif percentage < 50:
        level = "A2"
    elif percentage < 75:
        level = "B1"
    else:
        level = "B2"

    st.success(f"Seviyeniz: {level}")
    st.write(f"Skor: {st.session_state.total_score}/{total_possible} ({percentage:.2f}%)")

    # Veritabanına kaydetme
    from database.models import DatabaseManager

    db = DatabaseManager()
    db.save_level_test_result(
        st.session_state.user_id,
        st.session_state.answers,
        level,
        st.session_state.total_score
    )

    db.update_user_level(st.session_state.user_id, level)
    st.session_state.current_level = level
