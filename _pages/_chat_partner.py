import streamlit as st
import json
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
                                analysis_data = message.get('analysis')

                                # Parse JSON string if necessary
                                if isinstance(analysis_data, str):
                                    try:
                                        analysis_data = json.loads(analysis_data)
                                    except Exception:
                                        # Fallback: show raw text if not JSON
                                        st.write(analysis_data)
                                        analysis_data = None

                                # Unwrap if returned as { "analysis": { ... } }
                                if isinstance(analysis_data, dict) and 'analysis' in analysis_data and isinstance(analysis_data['analysis'], dict):
                                    analysis_data = analysis_data['analysis']

                                if isinstance(analysis_data, dict):
                                    grammar_mistakes = analysis_data.get('grammar_mistakes') or []
                                    vocabulary_suggestions = analysis_data.get('vocabulary_suggestions') or []
                                    overall_assessment = analysis_data.get('overall_assessment')
                                    encouragement_feedback = analysis_data.get('encouragement_feedback')

                                    # Title line with stars if available
                                    if overall_assessment is not None:
                                        try:
                                            rating = int(str(overall_assessment).strip().split()[0])
                                            stars = '⭐' * max(0, min(5, rating))
                                            st.markdown(f"**Genel Değerlendirme:** {stars} ({rating}/5)")
                                        except Exception:
                                            st.markdown(f"**Genel Değerlendirme:** {overall_assessment}")

                                    if grammar_mistakes:
                                        st.markdown("**🧩 Dilbilgisi Notları:**")
                                        for item in grammar_mistakes:
                                            st.markdown(f"- {item}")

                                    if vocabulary_suggestions:
                                        st.markdown("**🗂️ Kelime Önerileri:**")
                                        for item in vocabulary_suggestions:
                                            st.markdown(f"- {item}")

                                    if encouragement_feedback:
                                        st.markdown("**💡 Geri Bildirim:**")
                                        st.write(encouragement_feedback)
                                
                                elif analysis_data is None:
                                    pass
                                else:
                                    # Unknown structure; show safely
                                    st.write(analysis_data)
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])

        # Kullanıcı girişi - chat_input kullanarak
        user_input = st.chat_input("Mesajınızı yazın...")

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
            username = st.session_state.get('username', None)
            # # Debug için kullanıcı adını göster
            # if username:
            #     st.write(f"Debug: Kullanıcı adı '{username}' olarak AI'ya gönderiliyor")
            
            response = st.session_state.llm_handler.generate_response(
                prompt=user_input,
                user_level=st.session_state.current_level,
                context=f"Topic: {selected_topic}. Context: {context}",
                username=username
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
