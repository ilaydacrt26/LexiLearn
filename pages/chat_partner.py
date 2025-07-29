import streamlit as st
from utils.llm_handler import LLMHandler
from utils.rag_system import RAGSystem
from database.models import DatabaseManager

def chat_partner_page():
    st.title("💬 AI Konuşma Partneri")

    # ilk kurulum
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.llm_handler = LLMHandler()
        st.session_state.rag_system = RAGSystem()

    # Konu seçimi
    col1, col2 = st.columns([3, 1])

    with col2:
        st.write("### 🎯 Konu seçin")
        topics = [
            "Serbest sohbet",
            "Günlük rutinler",
            "Hobiler",
            "Seyahat",
            "Hava durumu",
            "Yemek",
            "İş ve kariyer",
            "Eğitim",
            "Teknoloji"
        ]
        selected_topic = st.selectbox("Konu", topics)

        st.write("### 📊 Seviyeniz")
        st.info(st.session_state.current_level)

        if st.button("Konuşmayı Temizle"):
            st.session_state.chat_history = []
            st.rerun()

    with col1:
        # Sohbet geçmişi
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'])
                        if 'analysis' in message:
                            with st.expander("📝 Analiz"):
                                st.write(message['analysis'])
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])

        # Kullanıcı girişi
        user_input = st.text_input("Mesajınızı yazın...")

        if user_input:
            # Kullanıcı mesajını ekle
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })

            # RAG sistemi ile içerik arama
            relevant_content = st.session_state.rag_system.search_content(
                query=f'{selected_topic} {user_input}',
                level=st.session_state.current_level,
                content_type='dialogues'
            )

            context = " ".join(relevant_content) if relevant_content else ""

            # LLM ile yanıt oluştur
            response = st.session_state.llm_handler.generate_response(
                prompt=user_input,
                user_level=st.session_state.current_level,
                context=f"Topic: {selected_topic}. Context: {context}"
            )

            # Kullanıcı girişini analiz et
            analysis = st.session_state.llm_handler.analyze_user_input(
                user_input,
                st.session_state.current_level
            )

            # Mesajları güncelle
            st.session_state.chat_history[-1]['analysis'] = analysis
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })

            # XP kazanımı
            xp_gained = 10
            db = DatabaseManager()
            db.add_user_activity(
                st.session_state.user_id,
                "chat",
                score=5,
                xp_gained=xp_gained,
                details=f"Topic: {selected_topic}"
            )

            st.rerun()

# Görsel geri bildirim
def show_conwersation_stats():
    st.sidebar.write("### 📈 Sohbet İstatistikleri")
    total_messages = len(m for m in st.session_state.chat_history if m['role'] == 'user')
    st.sidebar.metric("Toplam Mesaj", total_messages)
    st.sidebar.metric("Kazanılan XP", total_messages * 10)
