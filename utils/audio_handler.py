import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import io
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self, audio_bytes):
        try:
            # AudioSegment ile gelen sesi WAV formatına çevir
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)

            with sr.AudioFile(wav_io) as source:
                audio_data = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio_data)
                return transcript
        except sr.UnknownValueError:
            return "Google API sesi anlayamadı."
        except sr.RequestError as e:
            return f"Google API isteği başarısız oldu: {e}"
        except Exception as e:
            return f"Transkript hatası: {str(e)}"

    def analyze_pronunciation(self, original_text, spoken_text, user_level):
        from utils.llm_handler import LLMHandler

        llm = LLMHandler()

        prompt = f"""
        Analyze pronunciation accuracy for a {user_level} level student:

        Original text: "{original_text}"
        Spoken text: "{spoken_text}"

        Provide:
        1. Accuracy score (0-100)
        2. Mispronounced words
        3. Suggestions for improvement
        4. Phonetic tips

        Format as JSON.
        """

        analysis = llm.model.generate_content(prompt)
        return analysis.text 
    
    def generate_pronunciaton_feedback(self, level, topic="general"):
        exercises = {
            "A1": [
                "Hello, my name is Sarah",
                "I like to eat apples and bananas",
                "The cat is sleeping on the bed",
                "What time is it now?",
                "Thank you very much."
            ],
            "A2": [
                "I enjoy reading books in my free time",
                "Can you tell me about your favorite hobby?",
                "The weather is nice today, isn't it?",
                "I went to the market yesterday",
                "What do you like to do on weekends?"
            ],
            "B1": [
                "I have been learning English for two years",
                "Can you explain the rules of this game?",
                "I would like to travel to different countries",
                "What is your opinion on climate change?",
                "Let's discuss our plans for the summer vacation."
            ],
            "B2": [
                "I believe that education is the key to success",
                "Can you describe your ideal job?",
                "What are the advantages and disadvantages of technology?",
                "I think that art plays an important role in society",
                "Let's analyze the impact of social media on communication."
            ]
        }

        import random
        level_exercises = exercises.get(level, exercises["A1"])
        return random.choice(level_exercises)
