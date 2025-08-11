import streamlit as st
import hashlib
from database.models import DatabaseManager

# Şifreyi hashleme fonksiyonu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_page():
    st.title(" 🎓 LexiLearn'e Hoş Geldiniz!")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Giriş Yap")

            if submit:
                db = DatabaseManager()
                user = db.authenticate_user(username, hash_password(password))
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.current_level = user[3]
                    st.success(f"Giriş başarılı! Hoş geldin, {st.session_state.username}!")
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre yanlış!")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Yeni Kullanıcı Adı")
            new_password = st.text_input("Yeni Şifre", type="password")
            confirm_password = st.text_input("Şifreyi Onayla", type="password")
            register = st.form_submit_button("Kayıt Ol")

            if register:
                if new_password == confirm_password:
                    db = DatabaseManager()
                    if db.create_user(new_username, hash_password(new_password)):
                        st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
                    else:
                        st.error("Kullanıcı adı zaten mevcut!")
                else:
                    st.error("Şifreler eşleşmiyor!")
