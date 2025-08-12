import os
import sys

import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GooglePalmEmbeddings
from langchain_community.vectorstores import Chroma

class RAGSystem:
    def __init__(self):
        self.persist_directory = "chroma_db"
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.create_collection(
            name="lexilearn_content",
            get_or_create=True
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

    def add_content(self, content, level, content_type):
        # İçeriği vektör veritabanına ekle
        chunks = self.text_splitter.split_text(content)

        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                metadatas=[{"level": level, "type": content_type, "chunk_id": i}],
                ids=[f"{level}_{content_type}_{i}_{hash(chunk)}"]
            )

    def search_content(self, query, level, content_type=None, n_results=3):
        # Seviye ve türe göre içerik ara
        if content_type:
            where_clause = {
                "$and": [
                    {"level": {"$eq": level}},
                    {"type": {"$eq": content_type}}
                ]
            }
        else:
            where_clause = {"level": {"$eq": level}}

        results = self.collection.query(
            query_texts=[query],
            where=where_clause,
            n_results=n_results
        )

        return results['documents'][0] if results['documents'] else []
    
    def populate_initial_data(self):
        # Başlangıç verilerini ekle
        content_data = {
            "A1": {
                "vocabulary": ["Hello, goodbye, please, thank you, yes, no, family, food, colors, numbers",
                               "I am, you are, he is, she is, it is, we are, they are, present simple, basic questions"],
                "dialogues": ["A: Hello! What is your name?, B: Hi my name is John. Nice to meet you!",
                              "A: How are you today?, B: I am fine, thank you! How about you?"],
                "scenarios": ["At a restaurant: ordering food, asking for the menu, paying the bill",
                              "At a hotel: checking in, asking for room service, checkout"]
            },
            "A2": {
                "vocabulary": ["Daily routines, hobbies, travel, weather, food preferences",
                               "Present continuous, past simple, basic adjectives"],
                "dialogues": ["A: What do you like to do in your free time?, B: I like reading books and watching movies.",
                              "A: Where did you go on vacation?, B: I went to the beach last summer."],
                "scenarios": ["At a supermarket: shopping for groceries, asking for prices",
                              "At a doctor's office: making an appointment, describing symptoms"]
            },
            "B1": {
                "vocabulary": ["Work, education, health, environment, technology",
                               "Present perfect, future tenses, comparative and superlative adjectives"],
                "dialogues": ["A: What do you do for a living?, B: I work as a software engineer.",
                              "A: Have you ever traveled abroad?, B: Yes, I have been to France and Spain."],
                "scenarios": ["At a job interview: answering questions about experience",
                              "At a university: discussing courses and assignments"]
            },
            "B2": {
                "vocabulary": ["Politics, culture, society, global issues, advanced idioms",
                               "Complex sentences, passive voice, conditionals"],
                "dialogues": ["A: What are your thoughts on climate change?, B: I believe it is a critical issue that needs immediate action.",
                               "A: How do you think technology will change our lives in the next decade?, B: I think it will revolutionize communication and education."],
                "scenarios": ["At a conference: presenting ideas, networking with professionals",
                              "At a cultural event: discussing art, music, and literature"]
            }
        }

        for level, categories in content_data.items():
            for category, contents in categories.items():
                for content in contents:
                    self.add_content(content, level, category)

#!!! İlk kurulumda çalıştırılacak fonksiyon
def initialize_rag():
    rag = RAGSystem()
    rag.populate_initial_data()
    return rag

# initialize_rag()
