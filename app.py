import streamlit as st
from _pages import _login as login, \
                  _level_test as level_test, \
                  _chat_partner as chat_partner, \
                  _daily_tasks as daily_tasks, \
                  _pronunciation as pronunciation, \
                  _scenarios as scenarios, \
                  _listening as listening, \
                  _profile as profile
from database.models import DatabaseManager

def main():
    st.set_page_config(
        page_title="LexiLearn",
        page_icon="🎓",
        layout="wide"
    )

    # 'page' session state değişkenini başlat
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 Ana Sayfa"

    # Kullanıcı girişi kontrolü
    if 'user_id' not in st.session_state:
        login.login_page()
        return # Stop execution if not logged in yet

    # Kullanıcı başarıyla giriş yaptıysa veya zaten girişliyse, weekly_target'ı session_state'e ekle/güncelle
    db = DatabaseManager()
    user_data = db.get_user_data(st.session_state.user_id)
    st.session_state.weekly_target = user_data.get('weekly_target', 5) # Default 5 gün

    # Sidebar içeriği
    st.sidebar.title(f"Merhaba, {st.session_state.username}!")

    page_options = [
        "🏠 Ana Sayfa",
        "📚 Seviye Belirleme Sınavı",
        "💬 Konuşma Partneri",
        "📝 Günlük Görevler",
        "🎤 Telaffuz Kontrolü",
        "🎭 Senaryolar",
        "🎧 Dinleme",
        "👤 Profil"
    ]
    selected_page_index = page_options.index(st.session_state.page) if st.session_state.page in page_options else 0
    page = st.sidebar.selectbox("Modül Seçin:", page_options, index=selected_page_index)

    if st.sidebar.button("Çıkış Yap"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Corrected page routing based on the 'page' variable from sidebar
    if page == "🏠 Ana Sayfa":
        show_dashboard()
    elif page == "📚 Seviye Belirleme Sınavı":
        level_test.level_test_page()
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

    db = DatabaseManager()
    user_stats = db.get_comprehensive_user_stats(st.session_state.user_id)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Mevcut Seviye", st.session_state.current_level)

    with col2:
        st.metric("Toplam XP", user_stats.get('total_xp', 0))

    with col3:
        st.metric("Günlük Streak", f"{user_stats.get('current_streak', 0)} gün")

    # Seviye Belirleme Sınavı Kartı
    if st.session_state.get('current_level') == "A1" or st.session_state.get('current_level') is None:
        st.markdown("""
        <div style="background-color:#262B33; padding:20px; border-radius:10px; border: 1px solid #3E4451; color: white;">
        <h4>🌟 Seviyenizi Belirleyin!</h4>
        <p>Henüz bir seviye belirleme sınavı yapmadınız veya seviyeniz A1 olarak görünüyor. Dil öğrenme yolculuğunuza doğru seviyeden başlamak için şimdi seviye belirleme sınavını tamamlayın!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Seviye Belirleme Sınavına Git", key="go_to_level_test"):
            st.session_state.page = "📚 Seviye Belirleme Sınavı"
            st.rerun()

    st.write("### 🚀 Modüller")

    modules = [
        {"name": "Konuşma Partneri", "icon": "💬", "description": "Yapay zeka ile interaktif konuşma pratiği yap.", "page": "💬 Konuşma Partneri"},
        {"name": "Günlük Görevler", "icon": "📝", "description": "Günlük kelime ve cümle görevlerini tamamla.", "page": "📝 Günlük Görevler"},
        {"name": "Telaffuz Kontrolü", "icon": "🎤", "description": "Konuşma becerilerini geliştir, telaffuzunu kontrol et.", "page": "🎤 Telaffuz Kontrolü"},
        {"name": "Senaryolar", "icon": "🎭", "description": "Farklı günlük yaşam senaryolarında pratik yap.", "page": "🎭 Senaryolar"},
        {"name": "Dinleme", "icon": "🎧", "description": "Dinleme becerilerini geliştirmek için çeşitli içerikler dinle.", "page": "🎧 Dinleme"},
        {"name": "Profil", "icon": "👤", "description": "Profilini ve ilerlemeni takip et, başarılarını gör.", "page": "👤 Profil"},
    ]

    cols = st.columns(3)
    for i, module in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background-color:##262730; padding:15px; border-radius:10px; border:1px solid #333333; margin-bottom:10px; color: white;">
                <h4>{module['icon']} {module['name']}</h4>
                <p style="font-size:0.9em; color:lightgray;">{module['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Git →", key=f"go_to_{module['name']}"):
                st.session_state.page = module['page']
                st.rerun()

if __name__ == "__main__":
    main()
