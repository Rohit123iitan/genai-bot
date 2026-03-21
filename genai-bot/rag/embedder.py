import os
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Configuration
# -----------------------------
DB_PATH = "db/embeddings.db"
DOCS_PATH = "data/docs/"
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500


# -----------------------------
# Load Embedding Model
# -----------------------------
model = SentenceTransformer(MODEL_NAME)


# -----------------------------
# Initialize Database
# -----------------------------
def init_db():
    """Create SQLite database and table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            content TEXT,
            embedding BLOB
        )
    """)

    conn.commit()
    return conn


# -----------------------------
# Text Chunking
# -----------------------------
def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into fixed-size chunks."""
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]


# -----------------------------
# Process Documents
# -----------------------------
def process_documents():
    """Read documents, create embeddings, and store in DB."""
    
    conn = init_db()
    cursor = conn.cursor()

    if not os.path.exists(DOCS_PATH):
        print(f"Folder not found: {DOCS_PATH}")
        return

    for filename in os.listdir(DOCS_PATH):

        if not filename.endswith((".txt", ".md")):
            continue

        file_path = os.path.join(DOCS_PATH, filename)

        print(f"Processing: {filename}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        chunks = chunk_text(text)

        for chunk in chunks:
            if not chunk.strip():
                continue

            # Generate embedding (normalized for cosine similarity)
            embedding = model.encode(
                chunk,
                normalize_embeddings=True
            )

            # Convert to float32 for compact storage
            embedding = np.array(embedding, dtype=np.float32)

            # Store as bytes
            embedding_bytes = embedding.tobytes()

            cursor.execute(
                """
                INSERT INTO document_chunks (filename, content, embedding)
                VALUES (?, ?, ?)
                """,
                (filename, chunk, embedding_bytes)
            )

    conn.commit()
    conn.close()

    print("Documents processed and stored successfully.")
