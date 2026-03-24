<div align="center">

# GenAI RAG Discord Bot

**A production-ready Discord bot powered by Retrieval-Augmented Generation**

Query your own documents through Discord — grounded answers, source citations,  
per-user conversation memory, and interaction-scoped caching. Fully local. No paid APIs.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.x-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black)](https://ollama.com/)
[![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
- [How the Features Work](#how-the-features-work)
- [Troubleshooting](#troubleshooting)
- [Tech Stack](#tech-stack)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

GenAI RAG Discord Bot lets you drop documents into a folder and query them instantly through Discord. Built on a modular RAG pipeline — embed, retrieve, generate — every response is grounded in *your* data using local embeddings and a local LLM via Ollama. No OpenAI key. No data leaving your machine.

**What is RAG?** Retrieval-Augmented Generation first searches your documents for the most relevant passages, then feeds them as context to the language model. The bot answers from your actual content instead of hallucinating from general training data.

**This release adds four capabilities:**

- **Conversation memory** — retains the last 3 interactions per user and passes them as context to every new query
- **Interaction-scoped cache** — cache key includes the user's last 3 interactions, so the same question in a different conversation state is treated as a separate entry
- **Source citations** — every answer shows exactly which document chunks were used
- **`!summarize` command** — summarizes the user's own last 3 interactions from the current session

---

## Features

| Feature | Detail |
|---|---|
| `!ask <question>` | Query your documents with a natural language question |
| `!summarize` | Summarize your last 3 interactions in the current session |
| `!help` | List all available commands |
| Source citations | Every answer cites the document filename and chunk used |
| Conversation memory | Last 3 Q&A pairs per user prepended as context on every query |
| Interaction-scoped cache | Cache key = `hash(query + last 3 interactions)` per user |
| Semantic retrieval | Local embeddings via Sentence Transformers |
| Local LLM | Powered by Ollama — `gemma:2b`, `mistral`, or any compatible model |
| Fully offline | No external API calls, no data leaving your machine |

---

## 🏗️ Architecture

```
User Input (!ask / !summarize)
           │
           ▼
    Command Handler
           │
           ▼
   Conversation Memory (last 3)
           │
           ▼
      Cache Layer
     (query + history)
           │
     ┌─────┴─────┐
     │           │
   HIT         MISS
     │           ▼
     │     Retriever (SQLite)
     │           ▼
     │     Top-K Chunks
     │           ▼
     │     Generator (Ollama)
     │           ▼
     └────► Response + Sources
```

---

## 📁 Project Structure

```
genai-bot/
├── app.py                   # Entry point — starts the bot
├── config.py                # Centralised configuration
├── .env                     # Environment variables (not committed)
│
├── bot/
│   ├── handlers.py          # Memory store, cache logic, command registration
│   └── commands.py          # ask_command, summarize_command, help_command
│
├── rag/
│   ├── embedder.py          # Document ingestion and embedding (offline step)
│   ├── retriever.py         # Semantic chunk retrieval with source metadata
│   └── generator.py         # LLM prompt construction and answer generation
│
├── data/
│   └── docs/                # Place your .txt and .md documents here
│
├── db/
│   └── embeddings.db        # SQLite vector store (auto-created on first embed)
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com/) installed and running locally
- A Discord bot token — [create one here](https://discordpy.readthedocs.io/en/stable/discord.html)

---

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd genai-bot
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Discord
DISCORD_TOKEN=your_discord_bot_token_here

# Ollama
OLLAMA_URL=http://localhost:11434/api/generate
LLM_MODEL=gemma:2b

# RAG settings
MODEL_NAME=all-MiniLM-L6-v2
CHUNK_SIZE=500
TOP_K=3
```

> **Important:** In the [Discord Developer Portal](https://discord.com/developers/applications), open your bot's settings and enable **Message Content Intent** under Bot → Privileged Gateway Intents. Without this the bot cannot read message content.

### 5. Add your documents

Drop `.txt` or `.md` files into `data/docs/`:

```
data/docs/
├── ai_overview.txt
├── machine_learning.md
└── company_faq.txt
```

### 6. Generate embeddings

Run this once — and again whenever you add or update documents:

```bash
python -m rag.embedder
```

This creates `db/embeddings.db`, builds the `document_chunks` table, and stores all chunk embeddings locally.

### 7. Start the bot

```bash
python app.py
```

You should see:

```
🤖 Logged in as YourBotName
```

---

## Usage

### `!ask <question>`

Ask any question that can be answered from your documents. The bot automatically uses your last 3 interactions as context so follow-up questions work naturally.

```
You:  !ask What is machine learning?

Bot:  Machine learning is a branch of artificial intelligence that enables
      systems to learn and improve from experience without being explicitly
      programmed...

      📚 Sources:
      - machine_learning.md
      - ai_overview.txt
```

Follow-up questions resolve correctly using conversation history:

```
You:  !ask What are its main limitations?

Bot:  Building on the previous answer, the main limitations include
      data dependency, lack of interpretability, and high computational
      cost for training...

      📚 Sources:
      - machine_learning.md
```

---

### `!summarize`

Summarizes your own last 3 interactions from the current session. Scoped entirely to your personal history — not the general channel.

```
You:  !summarize

Bot:  Summary:
      You asked about machine learning and its limitations. The conversation
      covered the definition of ML, its core paradigms, and three key
      limitations: data dependency, interpretability, and compute cost.
```

> **Note:** `!summarize` requires at least one prior `!ask` in the current session. It reads from the same `deque(maxlen=3)` that `!ask` writes to, so it always reflects exactly the last 3 interactions.

---

### `!help`

Lists all available commands with a brief description of each.

---

## How the Features Work

### Conversation memory

Each user has a rolling window of their last 3 Q&A pairs stored in a `collections.deque(maxlen=3)`. On every `!ask` call, the formatted history is prepended to the LLM prompt so the model can resolve follow-up questions with full context. When a fourth interaction arrives, the oldest is automatically evicted.

Memory is **in-process and per-user** — it resets when the bot restarts. To persist memory across restarts, the history store can be extended to write to SQLite.

### Interaction-scoped cache

The cache key is an MD5 hash of the **normalized query combined with the user's current last 3 interactions and their user ID**. This design ensures:

- The same question asked fresh (empty history) and mid-conversation (with 3 prior turns) produce **different cache entries** with **different responses**
- A stale cached response from a previous conversation state is never incorrectly served
- Two users with identical histories asking the same question will correctly share a cache hit

### Source citations

The retriever returns chunk metadata — document filename and position — alongside the retrieved text. The generator passes this through to the bot handler, which appends a `📚 Sources:` footer to every response. Cached responses preserve their original source list unchanged.

### `!summarize` scoping

`!summarize` reads directly from the same `deque(maxlen=3)` that `!ask` writes to. It formats the stored Q&A pairs into a plain text block and sends it to Ollama with a summarization prompt. The output is a concise recap of the user's own recent session — deliberately limited to the same 3-interaction window used everywhere else in the bot.

---

## Troubleshooting

<details>
<summary><strong>Error: <code>no such table: document_chunks</code></strong></summary>

Embeddings have not been generated yet. Run:

```bash
python -m rag.embedder
```

</details>

<details>
<summary><strong>Bot is online but not responding to commands</strong></summary>

- Confirm `DISCORD_TOKEN` is correct in `.env`
- Enable **Message Content Intent** in the Discord Developer Portal under Bot → Privileged Gateway Intents

</details>

<details>
<summary><strong>Import errors when running scripts</strong></summary>

Always run from the project root using the `-m` flag:

```bash
python -m rag.embedder   # ✅ correct
python rag/embedder.py   # ❌ may cause import errors
```

</details>

<details>
<summary><strong>Ollama not responding</strong></summary>

Make sure Ollama is running and the model is pulled:

```bash
ollama serve
ollama pull gemma:2b
```

</details>

<details>
<summary><strong><code>!summarize</code> returns "Nothing to summarize yet"</strong></summary>

This triggers when you have no interaction history in the current session. Use `!ask` at least once before calling `!summarize`.

</details>

---

## Tech Stack

| Layer | Technology |
|---|---|
| Bot interface | [Discord.py 2.x](https://discordpy.readthedocs.io/) |
| Embeddings | [Sentence Transformers](https://www.sbert.net/) — `all-MiniLM-L6-v2` |
| Vector store | [SQLite](https://www.sqlite.org/) |
| LLM backend | [Ollama](https://ollama.com/) — `gemma:2b`, `mistral`, etc. |
| Conversation memory | Python `collections.deque(maxlen=3)` — in-process, per-user |
| Response cache | In-process dict keyed by `hash(query + last 3 interactions + user_id)` |
| Language | Python 3.10+ |

---

## Roadmap

- [ ] Persist conversation memory to SQLite across restarts
- [ ] FAISS or ChromaDB for faster vector retrieval
- [ ] Slash command support (`/ask`, `/summarize`, `/help`)
- [ ] Support for `.pdf` and `.docx` document ingestion
- [ ] Configurable memory window size via `.env`
- [ ] Per-guild document isolation for multi-server deployments
- [ ] Web UI for document management
- [ ] Cloud deployment guide (Railway / Fly.io)

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a pull request

Please follow the existing module structure and include appropriate logging for any new command handlers.

---

## License

```
GenAI RAG Discord Bot
Copyright (C) 2024  <your name or organisation>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

The full license text is available in the [LICENSE](LICENSE) file.

---

## Acknowledgements

- [Hugging Face](https://huggingface.co/) — Sentence Transformers and model hub
- [Ollama](https://ollama.com/) — local LLM inference engine
- [Discord.py](https://discordpy.readthedocs.io/) — Discord bot framework

---

<div align="center">
If this project helped you, consider giving it a star ⭐
</div>