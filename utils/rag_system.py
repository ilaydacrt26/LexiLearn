import os
import sys
import duckdb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GooglePalmEmbeddings
import numpy as np

class RAGSystem:
    def __init__(self, db_path='lexilearn_rag.duckdb'):
        self.db_path = db_path
        self.con = duckdb.connect(database=self.db_path, read_only=False)
        self.embeddings_model = GooglePalmEmbeddings(google_api_key=os.getenv("GEMINI_API_KEY"))

        self.con.execute("""
            CREATE TABLE IF NOT EXISTS rag_content (
                id VARCHAR PRIMARY KEY,
                content VARCHAR,
                embedding BLOB,
                level VARCHAR,
                type VARCHAR,
                chunk_id INTEGER
            )
        """)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

    def add_content(self, content, level, content_type):
        chunks = self.text_splitter.split_text(content)
        for i, chunk in enumerate(chunks):
            embedding = self.embeddings_model.embed_query(chunk)
            # DuckDB stores BLOBs as bytes, so convert numpy array to bytes
            embedding_bytes = embedding.tobytes()
            chunk_id = f"{level}_{content_type}_{i}_{hash(chunk)}"
            self.con.execute("INSERT INTO rag_content VALUES (?, ?, ?, ?, ?, ?)",
                             (chunk_id, chunk, embedding_bytes, level, content_type, i))

    def search_content(self, query, level, content_type=None, n_results=3):
        query_embedding = self.embeddings_model.embed_query(query)
        # Convert query embedding to bytes for DuckDB comparison (if needed, or handle in Python)
        query_embedding_bytes = np.array(query_embedding).tobytes()

        # Retrieve all relevant data from DuckDB for filtering and similarity calculation in Python
        # For large datasets, this might need optimization or external vector index
        where_clauses = [f"level = '{level}'"]
        if content_type:
            where_clauses.append(f"type = '{content_type}'")
        
        where_sql = " AND ".join(where_clauses)

        # Fetch all data that matches the metadata filters
        # We need the embeddings as numpy arrays for calculation
        results = self.con.execute(f"SELECT content, embedding, level, type FROM rag_content WHERE {where_sql}").fetchall()

        if not results:
            return []

        # Calculate cosine similarity in Python
        def cosine_similarity(vec1, vec2):
            vec1_np = np.frombuffer(vec1, dtype=np.float32) # Assuming embeddings are float32
            vec2_np = np.array(vec2)
            dot_product = np.dot(vec1_np, vec2_np)
            norm_vec1 = np.linalg.norm(vec1_np)
            norm_vec2 = np.linalg.norm(vec2_np)
            if norm_vec1 == 0 or norm_vec2 == 0:
                return 0.0
            return dot_product / (norm_vec1 * norm_vec2)

        scored_results = []
        for content, embedding_blob, level, content_type in results:
            similarity = cosine_similarity(embedding_blob, query_embedding)
            scored_results.append((content, similarity))

        # Sort by similarity and return top results
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return [content for content, _ in scored_results[:n_results]]

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
