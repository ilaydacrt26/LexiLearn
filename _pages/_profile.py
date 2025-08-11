import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from database.models import DatabaseManager
import pandas as pd
from datetime import datetime, timedelta

def profile_page():
    st.title("👤 Profil ve İlerleme")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 İlerleme", "🏆 Başarılar", "⚙️ Ayarlar"])

    with tab1:
        show_dashboard()

    with tab2:
        show_progress_charts()

    with tab3:
        show_achievements()

    with tab4:
        show_settings()

def show_dashboard():
    st.write("### 📊 Genel Bakış")

    db = DatabaseManager()
    user_stats = db.get_comprehensive_user_stats(st.session_state.user_id)

    # Ana metrikler
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Mevcut Seviye",
            st.session_state.current_level,
            delta=f"XP: {user_stats.get('total_xp', 0)}"
        )

    with col2:
        streak = user_stats.get('current_streak', 0)
        st.metric(
            "Günlük Seri",
            f"{streak} gün",
            delta = f"en uzun: {user_stats.get('longest_streak'), 0}"
        )

    with col3:
        st.metric(
            "Tamamlanan Görev",
            user_stats.get('total_activities', 0),
            delta = f"Bu hafta: {user_stats.get('week_activities', 0)}"
        )

    with col4:
        avg_score = user_stats.get('average_score', 0)
        st.metric(
            "Ortalama Skor",
            f"{avg_score:.1f}",
            delta = "📈"if avg_score > 7 else "📉"
        )

    # Haftalık aktivite grafiği
    st.write("### 📅 Haftalık Aktivite")
    weekly_data = db.get_weekly_activity(st.session_state.user_id)

    if weekly_data:
        df = pd.DataFrame(weekly_data, columns=['date', 'activity_count', 'xp_gained'])
        df['date'] = pd.to_datetime(df['date'])  # Convert date to datetime objects
        df = df.sort_values(by='date')  # Sort by date
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['activity_count'],
            name='Aktivite Sayısı',
            marker_color = 'lightblue'
        ))

        fig.update_layout(
            title="Son 7 Günlük Aktivite",
            xaxis_title="Tarih",
            yaxis_title="Aktivite Sayısı",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    # Modül bazında performans
    st.write("### 🎯 Modül Performansı")
    module_stats = db.get_module_performance(st.session_state.user_id)

    if module_stats:
        col1, col2 = st.columns(2)

        with col1:
            # Modül skorları
            modules = list(module_stats.keys())
            scores = [module_stats[m]['avg_score'] for m in modules]

            fig = go.Figure(data=go.Bar(x=modules, y=scores,
            name='Ortalama Skor',  # Add a name for the trace
            marker_color='lightcoral' # Example color
            ))
            fig.update_layout(
                title="Modül Ortalama Skorları",
                yaxis=dict(range=[0, 10]),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Aktivite dağılımı
            modules = list(module_stats.keys())
            counts = [module_stats[m]['count'] for m in modules]

            fig = go.Figure(data=go.Pie(labels=modules, values=counts))
            fig.update_layout(title="Aktivite Dağılımı", height=300)
            st.plotly_chart(fig, use_container_width=True)

def show_progress_charts():
    st.write("### 📈 İlerleme Grafikleri")

    db = DatabaseManager()

    # Zaman araığı seçimi
    time_range = st.selectbox("Zaman Aralığı:", ["Son 7 gün", "Son 30 gün", "Son 3 ay", "Tüm zamanlar"])

    if time_range == "Son 7 gün":
        days = 7
    elif time_range == "Son 30 gün":
        days = 30
    elif time_range == "Son 3 ay":
        days = 90
    else:
        days = None

    # Skor gelişimi
    st.write("###  📊Skor Gelişimi")
    score_progress = db.get_score_progress(st.session_state.user_id, days)

    if score_progress:
        df = pd.DataFrame(score_progress, columns=['date', 'score', 'activity_type'])

        fig = px.line(
            df,
            x='date',
            y='score',
            color='activity_type',
            title='Zaman İçinde Skor Gelişimi'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # XP birikimi
    st.write("### 💎 XP Birikimi")
    xp_progress = db.get_xp_progress(st.session_state.user_id, days)

    if xp_progress:
        df = pd.DataFrame(xp_progress, columns=['date', 'cumulative_xp'])

        fig = go.Figure(data=go.Scatter(
            x=df['date'],
            y=df['cumulative_xp'],
            mode='lines+markers',
            fill='tonexty',
            name='Toplam XP'
        ))

        fig.update_layout(
            title='XP Birikimi',
            xaxis_title='Tarih',
            yaxis_title='Toplam XP',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # Kelime Öğrenme Grafiği
    st.write("### 📚 Kelime Öğrenme")
    word_progress = db.get_vocabulary_progress(st.session_state.user_id, days)

    if word_progress:
        df = pd.DataFrame(word_progress, columns=['date', 'new_words', 'cumulative'])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['new_words'],
            name='Günlük Yeni Kelime',
            marker_color='lightgreen'
        ))

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['cumulative'],
            mode='lines+markers',
            name='Toplam Kelime',
            yaxis='y2',
            line=dict(color='red')
        ))

        fig.update_layout(
            title='Kelime Öğrenme İlerlemesi',
            xaxis_title='Tarih',
            yaxis_title='Günlük Yeni Kelime',
            yaxis2=dict(title='Toplam Kelime', overlaying='y', side='right'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

def show_achievements():
    st.write("### 🏆 Başarılar ve Rozetler")

    db = DatabaseManager()
    user_stats = db.get_comprehensive_user_stats(st.session_state.user_id)

    # Rozet sistemini tanımla
    achievements = [
        {
            "name":"İlk Adım",
            "description":"İlk aktiviteyi tamamladın",
            "icon":"🎯",
            "condition":user_stats.get('total_activities', 0) >= 1,
            "progress": min(user_stats.get('total_activities', 0), 1),
            "target":1
        },
        {
            "name":"Sabetkar",
            "description":"7 gün üst üste aktif oldun",
            "icon":"🔥",
            "condition":user_stats.get('longest_streak', 0) >= 7,
            "progress": min(user_stats.get('longest_streak', 0), 7),
            "target":7
        },
        {
            "name":"Konuşkan",
            "description":"50 sohbet mesajı gönderdin",
            "icon":"💬",
            "condition":user_stats.get('chat_messages', 0) >= 50,
            "progress": min(user_stats.get('chat_messages', 0), 50),
            "target":50
        },
        {
            "name":"Kelime Uzmanı",
            "description":"100 kelime öğrendin",
            "icon":"📚",
            "condition":user_stats.get('learned_words', 0) >= 100,
            "progress": min(user_stats.get('learned_words', 0), 100),
            "target":100
        },
        {
            "name":"Mükemmeliyetçi",
            "description":"10 aktiviteyi 10/10 skorla tamamladın",
            "icon":"⭐",
            "condition":user_stats.get('perfect_scores', 0) >= 10,
            "progress": min(user_stats.get('perfect_scores', 0), 10),
            "target":10
        },
        {
            "name":"İSeviye Atlayıcı",
            "description":"Bir seviye atladın",
            "icon":"🚀",
            "condition":user_stats.get('level_ups', 0) >= 1,
            "progress": min(user_stats.get('level_ups', 0), 1),
            "target":1
        },
        {
            "name":"Telaffuz Ustası",
            "description":"25 telaffuz egzersizi tamamladın",
            "icon":"🎤",
            "condition":user_stats.get('pronunciation_exercises', 0) >= 25,
            "progress": min(user_stats.get('pronunciation_exercises', 0), 25),
            "target":25
        },
        {
            "name":"Dinleme Şampiyonu",
            "description":"20 dinleme testini tamamladın",
            "icon":"🎧",
            "condition":user_stats.get('listening_test', 0) >= 20,
            "progress": min(user_stats.get('listening_test', 0), 20),
            "target":20
        }
    ]

    # Rozetleri göster
    cols=st.columns(3)
    for i, achievement in enumerate(achievements):
        with cols[i%3]:
            if achievement["condition"]:
                st.success(f"{achievement['icon']} **{achievement['name']}")
                st.write(achievement['description'])
                st.write("✅ **Tamamlandı!**")
            else:
                st.info(f"🔒 **{achievement['name']}**")
                st.write(achievement["description"])
                progress_percent = (achievement["progress"]/achievement["target"])*100
                st.progress(progress_percent/100)
                st.write(f"İlerleme: {achievement['progress']}/{achievement['target']}")

def show_settings():
    st.write("### ⚙️ Hesap Ayarları")

    # Kullanıcı bilgileri
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 👤 Profil Bilgileri")
        new_username = st.text_input("Kullanıcı Adı:", value=st.session_state.username)

        # Öğrenme hedefleri
        st.write("### 🎯 Öğrenme Hedefleri")
        daily_goal = st.slider("Günlük Hedef {dakika}:", 10, 120, 30)
        weekly_goal = st.slider("Haftalık Hedef {gün}:", 3, 7, 5)

        # Bildirim ayarları
        st.write("### 🔔 Bildirimler")
        daily_reminder = st.checkbox("Günlük hatırlatma", value=True)
        streak_reminder = st.checkbox("Seri hatırlatması", value=True)

    with col2:
        st.write("### 📊 İstatistikler")

        db = DatabaseManager()
        user_data = db.get_user_data(st.session_state.user_id)

        st.write(f"**Katılım Tarihi:** {user_data.get('created_at', 'Bilinmiyor')}")
        st.write(f"**Toplam Giriş:** {user_data.get('login_count', 0)}")
        st.write(f"**Son Giriş:** {user_data.get('last_login', 'Bugün')}")

        # Veri indirme
        st.write("### 📩 Veri Yönetimi")
        if st.button("İlerleme Raporunu İndir"):
            generate_progress_report()

        # Veri sıfırlama onay kutucuğu ve butonu
        confirm_reset = st.checkbox("Verilerimi sıfırlamak istediğimi onaylıyorum", key="confirm_data_reset")
        if st.button("Verileri Sıfırla", type="secondary", disabled=not confirm_reset, key="reset_data_button"):
            reset_user_data()

def generate_progress_report():
    # Kullanıcı ilerleme raporu oluştur
    db = DatabaseManager()

    # Tüm aktiviteleri al
    all_activities = db.get_all_user_activities(st.session_state.user_id)

    # CSV formatında rapor oluştur
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Başlıklar
    writer.writerow(['Tarih', 'Aktivite Türü', 'Skor', 'XP', 'Detaylar'])

    # Veriler
    for activity in all_activities:
        writer.writerow([
            activity[4], # Tarih
            activity[0], # Tür
            activity[1], # Skor
            activity[2], # XP
            activity[3] # Detaylar
        ])

    # İndirme
    st.download_button(
        label="📊 İlerleme Raporu (CSV)",
        data=output.getvalue(),
        file_name=f"lexilearn_progress_{st.session_state.username}.csv",
        mime="text/csv"
    )

    st.success("Rapor hazırlandı!")

def reset_user_data():
    # Kullanıcı verilerini sıfırla
    db = DatabaseManager()
    user_id = st.session_state.user_id
    db.reset_user_progress(user_id)

    # Session state'i temizle, ancak önemli bilgileri koru
    st.session_state.current_level = "A1"
    st.session_state.test_started = False # Reset level test state
    st.session_state.current_question = 0 # Reset current question
    st.session_state.answers = [] # Reset answers
    st.session_state.total_score = 0 # Reset total score

    st.success("Verileriniz sıfırlandı. Yeni bir başlangıç yapabilirsiniz!")
    st.rerun()
