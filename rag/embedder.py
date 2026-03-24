import os
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from config import Config

DB_PATH = Config.DB_PATH
DOCS_PATH = Config.DOCS_PATH
MODEL_NAME = Config.MODEL_NAME
CHUNK_SIZE = Config.CHUNK_SIZE
model = SentenceTransformer(MODEL_NAME)
# ----------------------------------------------------------------------------------------------
# Initialize Database and Table -> Create SQLite database and table if not exists.
# ----------------------------------------------------------------------------------------------
def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,         
                content TEXT,
                embedding BLOB
            )
        """)

        conn.commit()
        return conn

    except Exception as e:
        print(f"Database initialization failed: {e}")
        return None
# -----------------------------------------------------------------------------
# Text Chunking -> Split documents into fixed-size chunks.
# -----------------------------------------------------------------------------
def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]
# -----------------------------------------------------------------------------
# Process Documents -> Read documents, create embeddings, and store in DB.
# ------------------------------------------------------------------------------
def process_documents():
    conn = init_db()
    if not conn:
        return

    cursor = conn.cursor()

    if not os.path.exists(DOCS_PATH):
        print(f"Folder not found: {DOCS_PATH}")
        return

    for filename in os.listdir(DOCS_PATH):

        if not filename.endswith((".txt", ".md")):
            continue

        file_path = os.path.join(DOCS_PATH, filename)

        try:
            with open(file_path, "r", encoding="latin-1") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        chunks = chunk_text(text)

        if chunks:
            print(f"Processing {filename} with {len(chunks)} chunks")

        for chunk in chunks:
            if not chunk.strip():
                continue
            embedding = model.encode(
                chunk,
                normalize_embeddings=True
            )

            embedding = np.array(embedding, dtype=np.float32)
            embedding_bytes = embedding.tobytes()

            cursor.execute(
                """
                INSERT INTO document_chunks (source, content, embedding)
                VALUES (?, ?, ?)
                """,
                (filename, chunk, embedding_bytes)
            )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    process_documents()
