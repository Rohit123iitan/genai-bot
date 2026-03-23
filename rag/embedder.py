import os
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from config import Config

# Load configuration
DB_PATH = Config.DB_PATH
DOCS_PATH = Config.DOCS_PATH
MODEL_NAME = Config.MODEL_NAME
CHUNK_SIZE = Config.CHUNK_SIZE

# Load Embedding Model
model = SentenceTransformer(MODEL_NAME)


# -----------------------------
# Initialize Database (UPDATED)
# -----------------------------
def init_db():
    """Create SQLite database and table if not exists."""

    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("✅ Connected to SQLite database")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,          -- 🔥 unified field for retriever
                content TEXT,
                embedding BLOB
            )
        """)

        conn.commit()
        return conn

    except Exception as e:
        print(f"Database initialization failed: {e}")
        return None


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
# Process Documents (UPDATED)
# -----------------------------
def process_documents():
    """Read documents, create embeddings, and store in DB."""

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

            # -----------------------------
            # Generate embedding
            # -----------------------------
            embedding = model.encode(
                chunk,
                normalize_embeddings=True
            )

            embedding = np.array(embedding, dtype=np.float32)
            embedding_bytes = embedding.tobytes()

            # -----------------------------
            # Store in DB (UPDATED)
            # -----------------------------
            cursor.execute(
                """
                INSERT INTO document_chunks (source, content, embedding)
                VALUES (?, ?, ?)
                """,
                (filename, chunk, embedding_bytes)
            )

    conn.commit()
    conn.close()

    print("✅ Documents processed and stored successfully.")


if __name__ == "__main__":
    process_documents()