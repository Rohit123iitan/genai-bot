import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from config import Config

# -----------------------------
# Loading Model
# -----------------------------
model = SentenceTransformer(Config.MODEL_NAME)

# -----------------------------
# Database Connection and embeddings Loading
# -----------------------------

def load_embeddings():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor= conn.cursor()
    
    cursor.execute("""
        SELECT content, embedding
        FROM document_chunks"""
    )
    rows = cursor.fetchall()
    content = []
    vectors = []
    for content,emb_blob in rows:
        content.append(content)
        vectors.append(np.frombuffer(emb_blob, dtype=np.float32))
    
    if len(vectors)==0:
        return [],np.array([])
    return content,np.vstack(vectors)

# -----------------------------
# Retrieval Function
# -----------------------------

def retrieve(query, top_k=None, return_scores=False):
    top_k = top_k or Config.TOP_K
    contents, embeddings = load_embeddings()

    if embeddings.size == 0:
        return []

    # Encode query (normalized for cosine similarity)
    query_vec = model.encode(query, normalize_embeddings=True)

    # Compute similarity
    scores = np.dot(embeddings, query_vec)

    # Top-k indices
    top_indices = scores.argsort()[-top_k:][::-1]

    if return_scores:
        return [(contents[i], float(scores[i])) for i in top_indices]

    return [contents[i] for i in top_indices]