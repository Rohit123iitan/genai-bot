import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # -----------------------------
    # Validation -> Validate critical configuration values and provide user-friendly error messages.
    # -----------------------------
    @staticmethod
    def validate():
        if not Config.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is missing in .env file")
        
        db_dir = os.path.dirname(Config.DB_PATH)
        os.makedirs(db_dir, exist_ok=True)
        if not os.path.exists(Config.DOCS_PATH):
            print(f"Warning: Docs folder not found → {Config.DOCS_PATH}")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.getenv(
        "DB_PATH",
        os.path.join(BASE_DIR, "db", "embeddings.db")
    )

    DOCS_PATH = os.getenv(
        "DOCS_PATH",
        os.path.join(BASE_DIR, "data", "docs")
    )

    MODEL_NAME = os.getenv(
        "MODEL_NAME",
        "all-MiniLM-L6-v2"
    )

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    TOP_K = int(os.getenv("TOP_K", 3))

    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )

    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "mistral"
    )

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    