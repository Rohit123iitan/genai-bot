import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from config import Config

# -----------------------------
# Load Embedding Model
# -----------------------------
model = SentenceTransformer(Config.MODEL_NAME)


# -----------------------------
# Load Embeddings from DB
# -----------------------------
def load_embeddings():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT content, embedding, source
        FROM document_chunks
    """)

    rows = cursor.fetchall()
    conn.close()

    contents = []
    vectors = []
    sources = []

    for content, emb_blob, source in rows:
        contents.append(content)
        vectors.append(np.frombuffer(emb_blob, dtype=np.float32))
        sources.append(source if source else "Unknown")

    if len(vectors) == 0:
        return [], np.array([]), []

    return contents, np.vstack(vectors), sources


# -----------------------------
# Retrieval Function (UPDATED)
# -----------------------------
def retrieve(query, top_k=None, return_scores=False):
    """
    Return top-k relevant chunks with content + source.
    """

    top_k = top_k or Config.TOP_K

    contents, embeddings, sources = load_embeddings()

    if embeddings.size == 0:
        return []

    # Encode query (normalized for cosine similarity)
    query_vec = model.encode(query, normalize_embeddings=True)

    # Compute similarity
    scores = np.dot(embeddings, query_vec)

    # Top-k indices
    top_indices = scores.argsort()[-top_k:][::-1]

    results = []
    
    for i in top_indices:
        item = {
            "content": contents[i],
            "source": sources[i],
        }

        if return_scores:
            item["score"] = float(scores[i])

        results.append(item)
    
    return results