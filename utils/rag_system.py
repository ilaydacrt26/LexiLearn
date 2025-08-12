import os
import sys

import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GooglePalmEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS

class RAGSystem:
    def __init__(self):
        self.embeddings = GooglePalmEmbeddings()
        self.vector_store = None  # Initialize as None, will be loaded or created

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        # Try to load existing FAISS index or create a new one
        if os.path.exists("faiss_index"):
            self.vector_store = FAISS.load_local("faiss_index", self.embeddings, allow_dangerous_deserialization=True)
        else:
            # Create an empty FAISS index initially if no existing one
            self.vector_store = FAISS.from_texts(["initial_text"], self.embeddings) # Dummy entry to initialize
            self.vector_store.save_local("faiss_index")

    def add_content(self, content, level, content_type):
        # İçeriği vektör veritabanına ekle
        chunks = self.text_splitter.split_text(content)
        metadatas = [{
            "level": level,
            "type": content_type,
            "chunk_id": i
        } for i, chunk in enumerate(chunks)]

        # Add chunks to FAISS index
        if self.vector_store:
            self.vector_store.add_texts(chunks, metadatas=metadatas)
        else:
            # This case should ideally not be hit if initialization is correct
            self.vector_store = FAISS.from_texts(chunks, self.embeddings, metadatas=metadatas)
        self.vector_store.save_local("faiss_index") # Persist changes

    def search_content(self, query, level, content_type=None, n_results=3):
        # Seviye ve türe göre içerik ara
        if not self.vector_store:
            return [] # No vector store, no results

        docs = self.vector_store.similarity_search(query, k=n_results)

        filtered_docs = []
        for doc in docs:
            if doc.metadata.get("level") == level:
                if content_type and doc.metadata.get("type") == content_type:
                    filtered_docs.append(doc.page_content)
                elif not content_type:
                    filtered_docs.append(doc.page_content)
        return filtered_docs

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
