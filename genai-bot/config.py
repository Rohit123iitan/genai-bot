import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # -----------------------------
    # Paths
    # -----------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DB_PATH = os.getenv(
        "DB_PATH",
        os.path.join(BASE_DIR, "db", "embeddings.db")
    )

    DOCS_PATH = os.getenv(
        "DOCS_PATH",
        os.path.join(BASE_DIR, "data", "docs")
    )

    # -----------------------------
    # Embedding Model
    # -----------------------------
    MODEL_NAME = os.getenv(
        "MODEL_NAME",
        "all-MiniLM-L6-v2"
    )

    # -----------------------------
    # RAG Parameters
    # -----------------------------
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    TOP_K = int(os.getenv("TOP_K", 3))

    # -----------------------------
    # LLM (Ollama)
    # -----------------------------
    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )

    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "mistral"
    )

    # -----------------------------
    # Discord Bot
    # -----------------------------
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

    # -----------------------------
    # Logging
    # -----------------------------
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")