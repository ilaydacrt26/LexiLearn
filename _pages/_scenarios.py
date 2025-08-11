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
        st.session_state.scenario_handler.select_scenario()
    
    with tab2:
        if 'current_scenario' in st.session_state:
            st.session_state.scenario_handler.role_play_scenario()
        else:
            st.info("Önce bir senaryo seçin!")

    with tab3:
        show_scenario_results()

class ScenarioHandler:
    def __init__(self):
        self.llm_handler = LLMHandler()

    def start_scenarios(self, scenario_data):
        self.scenarios_data = scenario_data

    def process_user_response(self, user_response, expected_response):
        prompt = f'''
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
        '''

        evaluation = self.llm_handler.model.generate_content(prompt)
        raw_text = evaluation.text or ""
        json_str = self.llm_handler.extract_json(raw_text)

        if json_str:
            try:
                eval_data = json.loads(json_str)
                score = eval_data.get("score", 5)

                user_dialogue = {
                    "speaker": "user",
                    "text": user_response,
                    "score": score,
                    "feedback": eval_data.get("feedback","")
                }
                st.session_state.scenario_dialogue.append(user_dialogue)
                st.session_state.scenario_scores.append(score)
                st.session_state.scenario_step += 1 # Advance to next step (NPC)
                st.rerun()
            except json.JSONDecodeError:
                st.error("Yanıt değerlendirilemedi: LLM yanıtı geçerli JSON değil.")
        else:
            st.error("Yanıt değerlendirilemedi: LLM yanıtında JSON bulunamadı.")

    def select_scenario(self):
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

    def role_play_scenario(self):
        st.write(f"### 🎭 {st.session_state.current_scenario['title']}")
        st.write(st.session_state.current_scenario['description'])

        # Initialize scenario state if not started
        if not st.session_state.get('scenario_started', False):
            if st.button("🎬 Senaryoyu başlat"):
                st.session_state.scenario_handler.start_scenarios(st.session_state.current_scenario)
                st.session_state.scenario_dialogue = [] # Empty list for dialogue history
                st.session_state.scenario_started = True
                st.session_state.scenario_step = 0 # Start at index 0 of dialogue_flow
                st.session_state.scenario_scores = []
                st.rerun() # Rerun to display first NPC message

        if st.session_state.get("scenario_started", False):
            st.write("### 💬 Konuşma")

            dialogue_flow = st.session_state.current_scenario["dialogue_flow"]
            current_step_idx = st.session_state.scenario_step

            # Display all dialogues already in history
            for dialogue in st.session_state.scenario_dialogue:
                if dialogue["speaker"] != "user":
                    with st.chat_message("assistant"):
                        st.write(f"**{dialogue['speaker'].title()}:** {dialogue['text']}")
                else:
                    with st.chat_message("user"):
                        st.write(f"**Siz:** {dialogue['text']}")
                        if 'score' in dialogue:
                            st.write(f"**Skor: {dialogue['score']}/10")

            # Logic to handle the current step in dialogue_flow
            if current_step_idx < len(dialogue_flow):
                current_dialogue_item = dialogue_flow[current_step_idx]

                if current_dialogue_item["speaker"] != "user": # It's an NPC's turn to speak
                    # Append NPC dialogue to history if it's not already there
                    if not st.session_state.scenario_dialogue or \
                       (st.session_state.scenario_dialogue[-1] != current_dialogue_item):
                        st.session_state.scenario_dialogue.append(current_dialogue_item)
                        st.session_state.scenario_step += 1 # Advance to next step (should be user's turn)
                        st.rerun() # Rerun to display the NPC message and potentially the user input for the next turn
                else: # It's the user's turn to respond
                    expected_response_type = current_dialogue_item["expected"]
                    st.write(f"**🎯 Beklenen:** {expected_response_type}")

                    user_response = st.text_input(
                        "Yanıtınızı yazın:",
                        key=f"response_{current_step_idx}"
                    )

                    if st.button("Yanıtı Gönder") and user_response:
                        evaluation = self.process_user_response(
                            user_response, expected_response_type
                        )

                        try:
                            eval_data = json.loads(evaluation)
                            score = eval_data.get("score", 5)

                            user_dialogue = {
                                "speaker": "user",
                                "text": user_response,
                                "score": score,
                                "feedback": eval_data.get("feedback","")
                            }
                            st.session_state.scenario_dialogue.append(user_dialogue)
                            st.session_state.scenario_scores.append(score)
                            st.session_state.scenario_step += 1 # Advance to next step (NPC)
                            st.rerun()
                        except json.JSONDecodeError:
                            st.error("Yanıt değerlendirilemedi.")
            else:
                # Scenario completed
                complete_scenario()

def complete_scenario():
    st.success("🎉 Senaryo Tamamlandı!")

    total_score = sum(st.session_state.scenario_scores)
    avg_score = total_score/len(st.session_state.scenario_scores) if st.session_state.scenario_scores else 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Ortalama Skor", f"{avg_score:.1f}/10")

    with col2:
        if avg_score >= 8:
            preformance = "Mükemmel! ⭐"
        elif avg_score >= 6:
            preformance = "İyi! 👌"
        else:
            preformance = "Pratik gerekli 💪"
        st.metric("Performans", preformance)

    with col3:
        xp_gained = int(30 * (avg_score / 10))
        st.metric("Kazanılan XP", f"+{xp_gained}")

    db = DatabaseManager()
    db.add_user_activity(
        st.session_state.user_id,
        "scenario",
        score=int(avg_score),
        xp_gained=xp_gained,
        details=json.dumps({
            "scenario":st.session_state.scenario_key,
            "dialogue":st.session_state.scenario_dialogue,
            "scores":st.session_state.scenario_scores
        })
    )

    new_xp, level_up, new_level = db.update_user_xp(
        st.session_state.user_id,
        xp_gained,
        "scenario"
    )

    if level_up:
        st.balloons()
        st.success(f"🎉 Tebrikler! {new_level} seviyesine yükseldiniz!")
        st.session_state.current_level = new_level

    if st.button("Yeni Senaryo"):
        for key in list(st.session_state.keys()):
            if key.startswith("scenario_"):
                del st.session_state[key]
        if "current_scenario" in st.session_state:
            del st.session_state["current_scenario"]
        st.rerun()

def show_scenario_results():
    st.write("### 📊 Senaryo Geçmişiniz")

    db=DatabaseManager()
    scenario_history=db.get_user_activity(
        st.session_state.user_id,
        activity_type="scenario",
        limit=10
    )

    if scenario_history:
        for activity in scenario_history:
            details=json.loads(activity[4])
            with st.expander(f"Senaryo: {details["scenario"]} - Skor {activity[2]}/10"):
                st.write(f"**Tarih:** {activity[5]}")
                st.write(f"**Ortalama Skor:** {activity[2]}/10")
                st.write(f"**Kazanılan XP:** {activity[3]}")

                dialogue_count = len([d for d in details["dialogue"] if d["speaker"] == "user"])
                st.write(f"**Toplam Yanıt:** {dialogue_count}")
    else:
        st.info("Henüz senaryo tamamlamadınız.")
