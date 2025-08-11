import streamlit as st
import speech_recognition as sr
import io
import tempfile
import os
import re
import json
import wave
import audioop
from gtts import gTTS # Added for Text-to-Speech
from dotenv import load_dotenv

load_dotenv()

class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def text_to_speech(self, text, lang='en'):
        """Converts text to speech and saves it to a temporary WAV file."""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            temp_mp3_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            tts.save(temp_mp3_path)

            return temp_mp3_path
        except Exception as e:
            st.error(f"Text-to-speech error: {e}")
            return None

    def transcribe_audio(self, audio_bytes):
        """Transcribe audio bytes robustly without external tools.

        Strategy:
        1) If bytes look like WAV (RIFF/WAVE), parse with wave + audioop, convert to mono 16-bit 16kHz, feed to Google ASR.
        2) Else, try SpeechRecognition's AudioFile directly.
        3) Else, return a friendly error.
        """
        # Accept dict from mic_recorder (contains raw WAV bytes)
        if isinstance(audio_bytes, dict):
            audio_bytes = audio_bytes.get("bytes")
        # Accept memoryview/bytearray
        if isinstance(audio_bytes, memoryview):
            audio_bytes = bytes(audio_bytes)
        # Accept file-like objects
        if hasattr(audio_bytes, "read") and not isinstance(audio_bytes, (bytes, bytearray)):
            try:
                audio_bytes = audio_bytes.read()
            except Exception:
                return "Transkript hatası: Ses verisi okunamadı."
        if not isinstance(audio_bytes, (bytes, bytearray)):
            return "Transkript hatası: Ses verisi geçersiz."
        # Quick check for WAV header
        try:
            header = audio_bytes[:12]
        except Exception:
            return "Transkript hatası: Ses verisi okunamadı."
        is_wav = len(header) >= 12 and header[0:4] == b"RIFF" and header[8:12] == b"WAVE"

        if is_wav:
            try:
                wav_buffer = io.BytesIO(audio_bytes)
                with wave.open(wav_buffer, 'rb') as wav_reader:
                    sample_rate = wav_reader.getframerate()
                    sample_width = wav_reader.getsampwidth()
                    num_channels = wav_reader.getnchannels()
                    n_frames = wav_reader.getnframes()
                    raw_frames = wav_reader.readframes(n_frames)

                # Convert to mono
                pcm = raw_frames
                if num_channels > 1:
                    pcm = audioop.tomono(pcm, sample_width, 1, 1)
                # Convert sample width to 16-bit
                if sample_width != 2:
                    pcm = audioop.lin2lin(pcm, sample_width, 2)
                    sample_width = 2
                # Resample to 16kHz
                target_rate = 16000
                if sample_rate != target_rate:
                    pcm, _ = audioop.ratecv(pcm, 2, 1, sample_rate, target_rate, None)
                    sample_rate = target_rate

                audio_data = sr.AudioData(pcm, sample_rate, sample_width)
                transcript = self.recognizer.recognize_google(audio_data, language="en-US")
                return transcript
            except sr.UnknownValueError:
                return "Google API sesi anlayamadı."
            except sr.RequestError as e:
                return f"Google API isteği başarısız oldu: {e}"
            except Exception:
                # Fallthrough to try AudioFile generic path
                pass

        # Try generic path
        try:
            wav_buffer = io.BytesIO(audio_bytes)
            with sr.AudioFile(wav_buffer) as source:
                audio_data = self.recognizer.record(source)
                transcript = self.recognizer.recognize_google(audio_data, language="en-US")
                return transcript
        except sr.UnknownValueError:
            return "Google API sesi anlayamadı."
        except sr.RequestError as e:
            return f"Google API isteği başarısız oldu: {e}"
        except Exception:
            return "Transkript hatası: Ses formatı desteklenmiyor. Lütfen tekrar kaydedin."

    def audiosegment_to_wav_bytes(self, segment):
        """Convert a pydub.AudioSegment to WAV bytes without requiring FFmpeg.

        Uses Python's wave module and the segment's raw PCM data.
        """
        try:
            import wave
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wav_writer:
                wav_writer.setnchannels(segment.channels)
                # pydub: sample_width is bytes per sample
                wav_writer.setsampwidth(segment.sample_width)
                wav_writer.setframerate(segment.frame_rate)
                wav_writer.writeframes(segment.raw_data)
            buf.seek(0)
            return buf.read()
        except Exception:
            return b""

    def extract_json(self, text: str) -> str | None:
        fenced = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
        if fenced:
            return fenced.group(1)
        start = text.find("{")
        if start == -1:
            return None
        depth = 0
        for idx in range(start, len(text)):
            ch = text[idx]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[start:idx+1]
        return None

    def analyze_pronunciation(self, original_text, spoken_text, user_level):
        """Analyze pronunciation via LLM and always return a strict JSON string.

        Keys: accuracy_score (0-100 int), mispronounced_words (list of strings),
        suggestions (string), phonetic_tips (string)
        """
        # Hatalı veya boş transkript için hızlı dönüş
        if not spoken_text or spoken_text.lower().startswith("google api") or spoken_text.lower().startswith("transkript hatası"):
            fallback = {
                "accuracy_score": 0,
                "mispronounced_words": [],
                "suggestions": "We couldn't process your audio. Please try recording again in a quiet environment.",
                "phonetic_tips": "Speak clearly and keep the microphone close to your mouth."
            }
            return json.dumps(fallback)

        from utils.llm_handler import LLMHandler

        llm = LLMHandler()

        prompt = (
            "You are a pronunciation assessment assistant. "
            f"The learner's level is {user_level}.\n\n"
            f"Original text: " + json.dumps(original_text) + "\n"
            f"Spoken text: " + json.dumps(spoken_text) + "\n\n"
            "Return ONLY valid JSON with the following keys: \n"
            "- accuracy_score (integer 0-100)\n"
            "- mispronounced_words (array of strings)\n"
            "- suggestions (string)\n"
            "- phonetic_tips (string)\n"
            "Do not include any extra commentary or code fences."
        )

        try:
            analysis = llm.model.generate_content(prompt)
            raw_text = analysis.text or ""
        except Exception as e:
            raw_text = ""

        json_str = self.extract_json(raw_text)
        result: dict
        if json_str:
            try:
                result = json.loads(json_str)
            except Exception:
                result = {}
        else:
            result = {}

        # LLM başarısızsa kaba benzerlik tabanlı skor hesapla
        def basic_similarity_assessment(original: str, spoken: str) -> dict:
            def normalize(s: str) -> list[str]:
                s = s.lower()
                s = re.sub(r"[^a-z\s]", " ", s)
                tokens = [t for t in s.split() if t]
                return tokens
            orig_tokens = normalize(original)
            spok_tokens = normalize(spoken)
            if not orig_tokens or not spok_tokens:
                return {
                    "accuracy_score": 0,
                    "mispronounced_words": [],
                    "suggestions": "Read the whole sentence clearly and try again.",
                    "phonetic_tips": "Open your mouth a bit more and articulate vowels."
                }
            orig_set = set(orig_tokens)
            spok_set = set(spok_tokens)
            intersection = len(orig_set & spok_set)
            ratio = intersection / max(1, len(orig_set))
            score = int(max(0, min(100, round(ratio * 100))))
            missed = [w for w in orig_tokens if w not in spok_set]
            if score >= 80:
                sug = "Great job! Focus on stress and intonation to sound even more natural."
            elif score >= 60:
                sug = "Good effort. Practice the missed words and keep a steady rhythm."
            else:
                sug = "Slow down and pronounce each word clearly, matching the original text."
            tips = "Pay attention to word stress and long vs. short vowels (e.g., ship/sheep)."
            return {
                "accuracy_score": score,
                "mispronounced_words": list(dict.fromkeys(missed))[:10],
                "suggestions": sug,
                "phonetic_tips": tips,
            }

        # Zorunlu alanları normalize et; eksikse benzerlik tabanlı fallback kullan
        if not isinstance(result, dict):
            result = {}
        if not result or "accuracy_score" not in result:
            result = basic_similarity_assessment(original_text, spoken_text)

        accuracy = result.get("accuracy_score", 0)
        try:
            accuracy_int = int(float(accuracy))
        except Exception:
            accuracy_int = 0
        accuracy_int = max(0, min(100, accuracy_int))

        mis_words = result.get("mispronounced_words")
        if not isinstance(mis_words, list):
            mis_words = []

        suggestions = result.get("suggestions")
        if not isinstance(suggestions, str):
            # Fallback öneri
            sim_fallback = basic_similarity_assessment(original_text, spoken_text)
            suggestions = sim_fallback["suggestions"]

        tips = result.get("phonetic_tips")
        if not isinstance(tips, str):
            sim_fallback = basic_similarity_assessment(original_text, spoken_text)
            tips = sim_fallback["phonetic_tips"]

        cleaned = {
            "accuracy_score": accuracy_int,
            "mispronounced_words": mis_words,
            "suggestions": suggestions,
            "phonetic_tips": tips,
        }

        return json.dumps(cleaned)
    
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

    def generate_pronunciation_exercise(self, level, topic="general"):
        """Return a pronunciation exercise sentence for the given level and optional topic.

        This is the correctly spelled method and should be preferred.
        """
        return self.generate_pronunciaton_feedback(level, topic)

    def generate_pronunciaton_exercise(self, level, topic="general"):
        """Backward-compatible alias matching the misspelled call site in pages/pronunciation.py."""
        return self.generate_pronunciation_exercise(level, topic)