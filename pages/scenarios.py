import streamlit as st
from data.scenarios_data import SCENARIOS
from utils.llm_handler import LLMHandler
from database.models import DatabaseManager
import json
import random

def scenarios_page():
    st.title("🎭 Gerçek Hayat Senaryoları")

    # ilk kurulum
    if 'scenario_handler' not in st.session_state:
        st.session_state.scenario_handler = ScenarioHandler()

    tab1, tab2, tab3 = st.tabs(["🎬 Senaryo Seç", "🎭 Rol Yapma", "📊 Sonuçlar"])

    with tab1:
        select_scenario()
    
    with tab2:
        if 'current_scenario' in st.session_state:
            role_play_scenario()
        else:
            st.info("Önce bir senaryo seçin!")

    with tab3:
        show_scenario_results()

class ScenarioHandler:
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.current_dialogue = []
        self.dialogue_step = 0

    def start_scenarios(self, scenario_data):
        # Senaryoyu başlat
        self.current_dialogue = []
        self.dialogue_step = 0
        self.scenarios_data = scenario_data
        return scenario_data["dialogue_flow"][0]
    
    def process_user_response(self, user_response, expected_response):
        # Kullanıcı yanıtını işle
        prompt = f"""
        Evaluate the user's response in this scenario context:
        Expected response type: {expected_response}
        User's actual response: "{user_response}"
        User level: {st.session_state.current_level}

        Rate the response (1-10) based on:
        1. Appropriateness to the situation
        2. Grammar correctness for the level
        3. Use of relevant vocabulary
        4. Natural flow of conversation

        Provide feedback and a score. Format at JSON.
        """

        evaluation = self.llm_handler.model.generate_content(prompt)
        return evaluation.text
    
    def get_next_dialogue_step(self):
        # Sonraki diyalog adımını al
        self.dialogue_step += 1
        if self.dialogue_step < len(self.scenarios_data['dialogue_flow']):
            return self.scenarios_data["dialogue_flow"][self.dialogue_step]
        return None
    
    def select_scenario():
        st.write("### 🎬 Senaryo Seçin")

        user_level = st.session_state.current_level
        available_scenarios = SCENARIOS.get(user_level, SCENARIOS["A1"])

        for scenario_key, scenario_data in available_scenarios.items():
            with st.expander(f"🚩 {scenario_data['title']}"):
                st.write(scenario_data['description'])

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**🎯 Öğreneceğiniz Kelimeler:**")
                    st.write(", ".join(scenario_data["vocabulary"]))

                with col2:
                    st.write("**💬 Yararlı İfadeler:**")
                    for phrase in scenario_data["phrases"][:3]:
                        st.write(f"• {phrase}")

                if st.button(f"Bu Senaryoyu Seç", key=f"select_{scenario_key}"):
                    st.session_state.current_scenario = scenario_data
                    st.session_state.scenario_key = scenario_key
                    st.session_state.scenario_started = False
                    st.success("Senaryo seçildi! 'Rol Yapma' sekmesine geçin.")

    ### Burada kalındı
    def role_play_scenario():
        pass
