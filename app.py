import streamlit as st
from pages import login, level_test, chat_partner, daily_tasks, pronunciation, scenarios, listening, profile

def main():
    st.set_page_config(
        page_title="LexiLearn",
        page_icon="🎓",
        layout="wide"
    )

    # Kullanıcı girişi kontrolü
    if 'user_id' not in st.session_state:
        login.login_page()
        return
    
    # Seviye testi kontrolü
    if st.session_state.get('current_level') is None:
        level_test.level_test_page()
        return
    
    # Ana sayfa içeriği
    page = st.selectbox("Modül Seçin:", [
        "🏠 Ana Sayfa",
        "💬 Konuşma Partneri",
        "📝 Günlük Görevler",
        "🎤 Telaffuz Kontrolü",
        "🎭 Senaryolar",
        "🎧 Dinleme",
        "👤 Profil"
    ])

    if st.button("Çıkış Yap"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Sayfa yönlendirme
    if page == "🏠 Ana Sayfa":
        show_dashboard()
    elif page == "💬 Konuşma Partneri":
        chat_partner.chat_partner_page()
    elif page == "📝 Günlük Görevler":
        daily_tasks.daily_tasks_page()
    elif page == "🎤 Telaffuz Kontrolü":
        pronunciation.pronunciation_page()
    elif page == "🎭 Senaryolar":
        scenarios.scenarios_page()
    elif page == "🎧 Dinleme":
        listening.listening_page()
    elif page == "👤 Profil":
        profile.profile_page()

def show_dashboard():
    st.title("🎓 LexiLearn Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Mevcut Seviye", st.session_state.current_level)

    with col2:
        st.metric("Toplam XP", st.session_state.get('xp_points', 0))

    with col3:
        st.metric("Günlük Streak", "5 gün") ## İleride veri tabanından çekilecek

    st.write("### 📈 Haftalık İlerleme")

    ### Burada haftalık ilerleme grafiği gösterilecek

    st.write("### 📚 Günlük Hedefler")
    st.checkbox("Günlük kelime görevi tamamla")
    st.checkbox("10 dakika konuşma pratiği yap")
    st.checkbox("Telaffuz egzersizi yap")

if __name__ == "__main__":
    main()
