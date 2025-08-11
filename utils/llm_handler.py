import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

class LLMHandler:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(self, prompt, user_level='A1', context="", username=None):
        level_prompts = {
            "A1": "Use simple present tense, basic vocabulary (500 - 1000 words), and short sentences.",
            "A2": "Use present and past tenses, common vocabulary (1000 - 2000 words), and simple compound sentences.",
            "B1": "Use various tenses, intermediate vocabulary (2000 - 3000 words), and complex sentences.",
            "B2": "Use advanced grammar, wide vocabulary (3000+), and sophisticated expressions.",
        }   

        user_name_instruction = f"IMPORTANT: The user's name is {username}. Always use '{username}' when addressing them. NEVER use generic names like 'John', 'Sarah', or any other name." if username else ""

        system_prompt = f"""
        You are an English learning assistant. The user is at level {user_level}.
        {level_prompts.get(user_level, level_prompts['A1'])}
        
        {user_name_instruction}

        Guidelines:
        - Always respond in English.
        - Correct user's mistakes gently.
        - Provide alternative expressions.
        - Ask follow-up questions to continue the conversation.
        - Be encouraging and supportive.
        - CRITICAL: When addressing the user, use their actual name '{username}' only. Do not use any other names.

        Context: {context}
        """

        full_prompt = f"{system_prompt}\nUser: {prompt}\nAssistant:"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except:
            return "Sorry, I couldn't process your request at the moment. Please try again later."
        
    def analyze_user_input(self, user_input, user_level):
        prompt = f"""
        Analyze this English text from a {user_level} level student:
        {user_input}

        Provide:
        1. Grammar mistakes (if any)
        2. Vocabulary suggestions
        3. Overall assessment (1 - 5 stars)
        4. Encouragement feedback

        Format as JSON.
       """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e)})

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
