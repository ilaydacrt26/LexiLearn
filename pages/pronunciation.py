import streamlit as st
from utils.audio_handler import AudioHandler
from database.models import DatabaseManager
import json

def pronunciation_page():
    st.title("🎤 Telaffuz Kontrolü")

    # İlk kurulum
    if 'audio_handler' not in st.session_state:
        st.session_state.audio_handler = AudioHandler()
        st.session_state.current_exercise = None
        st.session_state.exercise_completed = False

    tab1, tab2, tab3 = st.tabs(["🎯 Egzersiz", "📊 Sonuçlar", "📈 İlerleme"])

    with tab1:
        pronunciation_exercise()

    with tab2:
        show_pronunciation_results()

    with tab3:
        show_pronunciation_progress()

def pronunciation_exercise():
    st.subheader("🎯 Telaffuz Egzersizi")

    col1, col2 = st.columns([2, 1])

    with col2:
        difficulty = st.selectbox("Zorluk Seviyesi", ["Kolay", "Orta", "Zor"])
        topic = st.selectbox("Konu", ["Genel", "Günlük Konuşma", "İş İngilizcesi", "Akademik"])

        if st.button("Yeni Egzersiz"):
            exercise_text = st.session_state.audio_handler.generate_pronunciaton_exercise(
                st.session_state.current_level,
                topic.lower()
            )

            st.session_state.current_exercise = exercise_text
            st.session_state.exercise_completed = False

    with col1:
        if st.session_state.current_exercise:
            st.write("### 📝 Metni Okuyun: ")
            st.info(st.session_state.current_exercise)

            # Ses Kaydı Butonu
            st.write("### 🎙️ Kaydınız: ")

            # Streamlit ses kaydı bileşeni
            audio_bytes = st.experimental_audio_input("Metni okuyun...")

            if audio_bytes and not st.session_state.exercise_completed:
                with st.spinner("Ses analiz ediliyor..."):
                    # Ses tanıma
                    transcribed_text = st.session_state.audio_handler.transcribe_audio(audio_bytes)

                    # Telaffuz analizi
                    analysis = st.session_state.audio_handler.analyze_pronunciation(
                        st.session_state.current_exercise,
                        transcribed_text,
                        st.session_state.current_level
                    )

                    # Sonuçları göster
                    try:
                        analysis_data = json.loads(analysis)
                        score = analysis_data.get("accuracy_score", 0)

                        st.write("### 📊 Sonuçlar")

                        col_score, col_accuracy = st.columns(2)
                        with col_score:
                            st.metric("Skor", f"{score}/100")
                        with col_accuracy:
                            if score >= 80:
                                st.success("Mükemmel Telaffuz! 🎉")
                            elif score >= 60:
                                st.warning("İyi, ama daha iyi olabilirsin! 💪")
                            else:
                                st.error("Daha fazla pratik yapmalısın! 😓")

                        st.write("**Söylediğiniz:**", transcribed_text)
                        st.write("**Öneriler:**", analysis_data.get("suggestions", ""))

                        # XP kazanımı
                        xp_gained = max(10, score // 10)
                        db = DatabaseManager()
                        db.add_user_activity(
                            st.session_state.user_id,
                            "pronunciation",
                            score=score,
                            xp_gained=xp_gained,
                            details=json.dumps({
                                "original": st.session_state.current_exercise,
                                "transcribed": transcribed_text,
                                "analysis": analysis_data
                            })
                        )

                        st.session_state.exercise_completed = True
                    except json.JSONDecodeError:
                        st.error("Telaffuz analizi başarısız oldu. Lütfen tekrar deneyin.")
            else:
                st.info("👆 Yukarıdan 'Yeni Egzersiz' butonuna tıklayark başlayın!")

def show_pronunciation_results():
    st.write("### 📊 Son Sonuçlarınız")

    db = DatabaseManager()
    recent_activities = db.get_user_activities(
        st.session_state.user_id, 
        activity_type="pronunciation", 
        limit=10
    )

    if recent_activities:
        for activity in recent_activities:
            with st.expander(f"Skor: {activity[2]} - {activity[5]}"):
                details = json.loads(activity[4])
                st.write(f"**Metin:**", details["original"])
                st.write(f"**Söylediğiniz:**", details["transcribed"])
                st.write(f"**XP Kazanımı:** {activity[3]}")
    else:
        st.info("Henüz telaffuz egzersizi yapmadınız.")

def show_pronunciation_progress():
    st.write("### 📈 Telaffuz İlerlemeniz")

    import plotly.graph_objects as go

    # Veri tabanından son 30 günlük aktiviteleri çek
    db = DatabaseManager()
    progress_data = db.get_pronunciation_progress(st.session_state.user_id)

    if progress_data:
        dates = [item[0] for item in progress_data]
        scores = [item[1] for item in progress_data]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Telaffuz Skoru',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.update_layout(
            title="Telaffuz İlerleme Grafiği (Son 30 Gün)",
            xaxis_title="Tarih",
            yaxis_title="Skor",
            yaxis=dict(range=[0, 100]),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Henüz telaffuz egzersizi yapmadınız veya veri bulunamadı.")
